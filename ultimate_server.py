#!/usr/bin/env python3
"""
Ultimate Server Python Script
A comprehensive server that proxies Maven Central, handles Git operations,
manages app configurations, and provides CI/CD integration capabilities.

Features:
- Maven Central proxy with caching
- Git operations (clone, pull, push, status)
- App configuration management
- Proxy for configured applications
- Google Cloud CI integration hooks
- RESTful API endpoints

Requirements:
    pip install flask requests gitpython google-cloud-build

Environment Variables:
    MAVEN_CENTRAL_CACHE_DIR: Directory for caching Maven artifacts
    GIT_REPOS_DIR: Directory for Git repositories
    APPS_CONFIG_FILE: JSON file with app configurations
    GOOGLE_CLOUD_PROJECT: GCP project ID
    GOOGLE_CLOUD_BUILD_TRIGGER: Cloud Build trigger ID
"""

import os
import json
import logging
import tempfile
import shutil
from pathlib import Path
from flask import Flask, request, Response, jsonify, send_file
import requests
from git import Repo, GitCommandError
from google.cloud.devtools import cloudbuild_v1
from google.oauth2 import service_account

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
MAVEN_CENTRAL_URL = 'https://repo1.maven.org/maven2'
CACHE_DIR = Path(os.getenv('MAVEN_CENTRAL_CACHE_DIR', './maven_cache'))
GIT_REPOS_DIR = Path(os.getenv('GIT_REPOS_DIR', './git_repos'))
APPS_CONFIG_FILE = os.getenv('APPS_CONFIG_FILE', 'apps_config.json')
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
GOOGLE_CLOUD_BUILD_TRIGGER = os.getenv('GOOGLE_CLOUD_BUILD_TRIGGER')

# Ensure directories exist
CACHE_DIR.mkdir(exist_ok=True)
GIT_REPOS_DIR.mkdir(exist_ok=True)

# Load app configurations
def load_apps_config():
    if os.path.exists(APPS_CONFIG_FILE):
        with open(APPS_CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

apps_config = load_apps_config()

# Google Cloud Build client
build_client = None
if GOOGLE_CLOUD_PROJECT and os.path.exists('service_account.json'):
    credentials = service_account.Credentials.from_service_account_file('service_account.json')
    build_client = cloudbuild_v1.CloudBuildClient(credentials=credentials)

@app.route('/maven/<path:path>', methods=['GET'])
def maven_proxy(path):
    """Proxy requests to Maven Central with caching."""
    cache_path = CACHE_DIR / path
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    # Check cache first
    if cache_path.exists():
        logger.info(f"Serving from cache: {path}")
        return send_file(cache_path, mimetype='application/octet-stream')

    # Proxy to Maven Central
    url = f"{MAVEN_CENTRAL_URL}/{path}"
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # Cache the file
            with open(cache_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            logger.info(f"Cached and serving: {path}")
            return Response(response.content, content_type=response.headers.get('content-type', 'application/octet-stream'))
        else:
            return Response(response.content, status=response.status_code)
    except Exception as e:
        logger.error(f"Error proxying Maven artifact: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/git/<repo_name>', methods=['POST'])
def git_operation(repo_name):
    """Handle Git operations for repositories."""
    data = request.get_json()
    operation = data.get('operation')
    repo_path = GIT_REPOS_DIR / repo_name

    try:
        if operation == 'clone':
            url = data.get('url')
            if not url:
                return jsonify({'error': 'URL required for clone'}), 400
            if repo_path.exists():
                shutil.rmtree(repo_path)
            Repo.clone_from(url, repo_path)
            return jsonify({'status': 'cloned', 'path': str(repo_path)})

        elif operation == 'pull':
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            origin.pull()
            return jsonify({'status': 'pulled'})

        elif operation == 'push':
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            origin.push()
            return jsonify({'status': 'pushed'})

        elif operation == 'status':
            repo = Repo(repo_path)
            status = {
                'branch': repo.active_branch.name,
                'is_dirty': repo.is_dirty(),
                'untracked_files': repo.untracked_files,
                'ahead': len(list(repo.iter_commits('HEAD..origin/main'))) if 'origin/main' in [r.name for r in repo.remotes.origin.refs] else 0,
                'behind': len(list(repo.iter_commits('origin/main..HEAD'))) if 'origin/main' in [r.name for r in repo.remotes.origin.refs] else 0
            }
            return jsonify(status)

        else:
            return jsonify({'error': 'Unknown operation'}), 400

    except GitCommandError as e:
        logger.error(f"Git error: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Error in git operation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/apps/<app_name>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def app_proxy(app_name):
    """Proxy requests to configured applications."""
    if app_name not in apps_config:
        return jsonify({'error': 'App not configured'}), 404

    app_config = apps_config[app_name]
    base_url = app_config.get('base_url')
    if not base_url:
        return jsonify({'error': 'App base URL not configured'}), 500

    # Construct target URL
    path = request.args.get('path', '')
    target_url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    # Forward the request
    try:
        headers = {k: v for k, v in request.headers if k.lower() not in ['host', 'content-length']}
        if request.method == 'GET':
            response = requests.get(target_url, headers=headers, params=request.args)
        elif request.method == 'POST':
            response = requests.post(target_url, headers=headers, json=request.get_json(), params=request.args)
        elif request.method == 'PUT':
            response = requests.put(target_url, headers=headers, json=request.get_json(), params=request.args)
        elif request.method == 'DELETE':
            response = requests.delete(target_url, headers=headers, params=request.args)
        else:
            return jsonify({'error': 'Method not supported'}), 405

        return Response(response.content, status=response.status_code,
                        content_type=response.headers.get('content-type'))

    except Exception as e:
        logger.error(f"Error proxying to app {app_name}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/ci/build', methods=['POST'])
def trigger_ci_build():
    """Trigger Google Cloud Build."""
    if not build_client or not GOOGLE_CLOUD_PROJECT or not GOOGLE_CLOUD_BUILD_TRIGGER:
        return jsonify({'error': 'Google Cloud Build not configured'}), 500

    try:
        # Create build request
        build = cloudbuild_v1.Build()
        build.source = cloudbuild_v1.Source()
        build.source.storage_source = cloudbuild_v1.StorageSource(
            bucket='your-source-bucket',  # Configure this
            object_='source.zip'  # Configure this
        )

        # Trigger the build
        operation = build_client.run_build(
            project_id=GOOGLE_CLOUD_PROJECT,
            build=build
        )

        return jsonify({'build_id': operation.metadata.build.id, 'status': 'triggered'})

    except Exception as e:
        logger.error(f"Error triggering CI build: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/config', methods=['GET', 'POST'])
def manage_config():
    """Manage server configuration."""
    global apps_config
    if request.method == 'GET':
        return jsonify({
            'maven_cache_dir': str(CACHE_DIR),
            'git_repos_dir': str(GIT_REPOS_DIR),
            'apps_config': apps_config,
            'google_cloud_project': GOOGLE_CLOUD_PROJECT,
            'google_cloud_build_trigger': GOOGLE_CLOUD_BUILD_TRIGGER
        })

    elif request.method == 'POST':
        data = request.get_json()
        if 'apps' in data:
            apps_config.update(data['apps'])
            with open(APPS_CONFIG_FILE, 'w') as f:
                json.dump(apps_config, f, indent=2)
        return jsonify({'status': 'updated'})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)