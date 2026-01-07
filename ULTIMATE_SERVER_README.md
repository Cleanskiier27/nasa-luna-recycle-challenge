# Ultimate Server Python Script

A comprehensive server that provides Maven Central proxy, Git operations, app proxying, and Google Cloud CI integration.

## Features

- **Maven Central Proxy**: Caches and proxies Maven artifacts from Maven Central
- **Git Operations**: Clone, pull, push, and status operations for Git repositories
- **App Proxying**: Proxy requests to configured applications
- **Google Cloud CI**: Integration with Google Cloud Build for CI/CD
- **Configuration Management**: RESTful API for managing server configuration

## Setup

1. Install dependencies:
   ```bash
   pip install flask requests gitpython google-cloud-build
   ```

2. Configure environment variables:
   ```bash
   export MAVEN_CENTRAL_CACHE_DIR=./maven_cache
   export GIT_REPOS_DIR=./git_repos
   export APPS_CONFIG_FILE=apps_config.json
   export GOOGLE_CLOUD_PROJECT=your-project-id
   export GOOGLE_CLOUD_BUILD_TRIGGER=your-trigger-id
   ```

3. For Google Cloud integration, create a service account key file `service_account.json`

4. Configure apps in `apps_config.json`:
   ```json
   {
     "my-app": {
       "base_url": "http://localhost:8080",
       "description": "My application"
     }
   }
   ```

## Running the Server

```bash
python ultimate_server.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Maven Proxy
- `GET /maven/<path>` - Proxy Maven Central artifacts

### Git Operations
- `POST /git/<repo_name>` - Perform Git operations
  ```json
  {
    "operation": "clone",
    "url": "https://github.com/user/repo.git"
  }
  ```

### App Proxying
- `GET|POST|PUT|DELETE /apps/<app_name>?path=<endpoint>` - Proxy to configured apps

### CI/CD
- `POST /ci/build` - Trigger Google Cloud Build

### Configuration
- `GET /config` - Get current configuration
- `POST /config` - Update configuration

### Health Check
- `GET /health` - Server health status

## Usage Examples

### Proxy Maven Artifact
```bash
curl http://localhost:5000/maven/org/springframework/spring-core/5.3.9/spring-core-5.3.9.jar -o spring-core.jar
```

### Clone Git Repository
```bash
curl -X POST http://localhost:5000/git/myrepo \
  -H "Content-Type: application/json" \
  -d '{"operation": "clone", "url": "https://github.com/user/repo.git"}'
```

### Proxy to App
```bash
curl http://localhost:5000/apps/my-app?path=/api/status
```

## Google Cloud CI Integration

To enable CI integration:
1. Set up Google Cloud Build trigger
2. Configure environment variables
3. Use the `/ci/build` endpoint to trigger builds

## Security Notes

- This server is for development/testing purposes
- Implement proper authentication and authorization for production use
- Configure firewall rules appropriately
- Use HTTPS in production