# ! THIS EXERCISE DOESN'T WORK IN FIREBASE !

# 01 Create a program that jiggles the mouse so that the computer doesn't go to sleep
""" 
    Make a program that:
        1. Jiggles the mouse so that the computer doesn't go to sleep
"""

import time
import pyautogui

def main():
    print("Mouse jiggler started. Press Ctrl+C to stop.")
    try:
        while True:
            # Get current mouse position
            current_x, current_y = pyautogui.position()
            
            # Move mouse slightly to the right and back
            pyautogui.moveTo(current_x + 5, current_y, duration=0.1)
            pyautogui.moveTo(current_x, current_y, duration=0.1)
            
            # Wait for 30 seconds before the next jiggle
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\nMouse jiggler stopped.")

if __name__ == "__main__":
    main()
