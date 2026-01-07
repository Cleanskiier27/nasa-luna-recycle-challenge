import numpy as np
from PIL import Image
from cogo_core import calculate_traverse

def interpret_signal_to_image(signal_data, width=512, height=512, filename="translated_signal.png"):
    """
    Translates Ghz signal data into a spatial 2D image using COGO mapping.
    
    Args:
        signal_data (np.array): Raw 1D signal data (GHz range).
        width (int): Output image width.
        height (int): Output image height.
        filename (str): Name of the output image file.
    """
    print(f"Interpreting {len(signal_data)} signal points...")
    
    # Create an empty grayscale image array
    image_array = np.zeros((height, width), dtype=np.uint8)
    
    # Center of the "SatGPU" map
    cx, cy = width // 2, height // 2
    
    # Process signal into the spatial map
    # We use COGO Traverse to map signal magnitude to a distance from the center
    # and signal index to an angle (bearing).
    for i, magnitude in enumerate(signal_data):
        # Map signal index to 0-360 degrees
        bearing = (i / len(signal_data)) * 360.0
        
        # Map magnitude to distance (scaled to fit image)
        distance = magnitude * (min(width, height) // 2.5)
        
        # COGO Translation
        nx, ny = calculate_traverse(cx, cy, distance, bearing)
        
        # Convert to pixel coordinates
        px = int(nx)
        py = int(ny)
        
        if 0 <= px < width and 0 <= py < height:
            # Additive signal strength
            intensity = int(magnitude * 255)
            image_array[py, px] = min(255, int(image_array[py, px]) + intensity)

    # Save the resulting image
    img = Image.fromarray(image_array, mode='L')
    img.save(filename)
    print(f"Signal translation saved to {filename}")
    return filename

if __name__ == "__main__":
    # Simulate a GHz signal (random data with some structure)
    t = np.linspace(0, 1, 10000)
    signal = 0.5 * (1 + np.sin(2 * np.pi * 50 * t)) * (0.5 + 0.5 * np.random.rand(10000))
    
    interpret_signal_to_image(signal)
