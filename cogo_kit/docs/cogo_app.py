import sys
import numpy as np
from cogo_core import calculate_inverse, calculate_traverse
from signal_interpreter import interpret_signal_to_image

def main():
    print("=== Cogo (Coordinate Geometry) Utility ===")
    print("Mode: 1=Inverse, 2=Traverse, 3=Signal2Image, 4=Exit")
    
    while True:
        try:
            choice = input("\nSelect mode > ")
            if choice == '1':
                x1 = float(input("P1 X: "))
                y1 = float(input("P1 Y: "))
                x2 = float(input("P2 X: "))
                y2 = float(input("P2 Y: "))
                d, b = calculate_inverse(x1, y1, x2, y2)
                print(f"Result: Distance={d:.4f}, Bearing={b:.4f}")
            elif choice == '2':
                x = float(input("Start X: "))
                y = float(input("Start Y: "))
                d = float(input("Distance: "))
                b = float(input("Bearing: "))
                nx, ny = calculate_traverse(x, y, d, b)
                print(f"Result: New X={nx:.4f}, New Y={ny:.4f}")
            elif choice == '3':
                print("Generating mock GHz signal translation...")
                # Mock signal: 5000 points of synthetic data
                mock_signal = np.random.rand(5000) * 0.8
                filename = interpret_signal_to_image(mock_signal)
                print(f"Success! View result at {filename}")
            elif choice == '4' or choice.lower() == 'exit':
                break
            else:
                print("Invalid choice.")
        except ValueError:
            print("Error: Please enter numeric values.")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
