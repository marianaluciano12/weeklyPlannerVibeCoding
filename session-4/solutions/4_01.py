# 1. Mouse Jiggler
# ⚠️  This exercise doesn't work in cloud/browser-based environments

# 🔎  Create a program that:
#     1. Jiggles the mouse so that the computer doesn't go to sleep

import time
import pyautogui

def main():
    print("Mouse jiggler started. Press Ctrl+C to stop.")
    try:
        while True:
            current_x, current_y = pyautogui.position()
            pyautogui.moveTo(current_x + 5, current_y, duration=0.1)
            pyautogui.moveTo(current_x, current_y, duration=0.1)
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nMouse jiggler stopped.")

if __name__ == "__main__":
    main()
