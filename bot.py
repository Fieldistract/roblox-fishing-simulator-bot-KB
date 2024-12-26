# Import necessary libraries
import time
import keyboard
import random
import pydirectinput
import mouse
import win32gui
import win32ui
import win32con
from ctypes import windll
import struct
import win32api

kianCords, krisCords, kianCords2 = (1283, 1057), (1374, 1306), (965, 785)
barCords = kianCords2

def get_pixel_color(x, y, retries=3):
    """Get pixel color with retries"""
    for _ in range(retries):
        try:
            hwin = win32gui.GetDesktopWindow()
            hwindc = win32gui.GetWindowDC(hwin)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, 1, 1)
            memdc.SelectObject(bmp)
            memdc.BitBlt((0, 0), (1, 1), srcdc, (x, y), win32con.SRCCOPY)
            bits = bmp.GetBitmapBits(True)
            b, g, r = struct.unpack('BBB', bits[:3])

            # Clean up
            memdc.DeleteDC()
            srcdc.DeleteDC()
            win32gui.ReleaseDC(hwin, hwindc)
            win32gui.DeleteObject(bmp.GetHandle())

            return (r, g, b)
        except Exception as e:
            print(f"Retry {_ + 1} - Error getting pixel color: {e}")
            time.sleep(0.1)  # Wait before retry
    return (0, 0, 0)

def is_fish_detected():
    """Check for green or white color at specific coordinates"""
    color = get_pixel_color(*barCords)
    # Check if the color is either green (83, 250, 83) or white (250, 250, 250)
    return color in [(83, 250, 83), (255, 255, 255)]

def verify_fish_caught(retries=5):
    """Verify if fishing process is complete by checking if green/white colors are gone"""
    # Wait a bit before starting verification
    consecutive_non_fish = 0
    for _ in range(retries):
        color = get_pixel_color(*barCords)
        if color not in [(83, 250, 83), (255, 255, 255)]:
            consecutive_non_fish += 1
            if consecutive_non_fish >= 3:  # Need 3 consecutive non-fish readings
                return True
        else:
            consecutive_non_fish = 0
        time.sleep(0.1)
    return False

# Hlvl speed everything between (0.01, 0.02 and 0.02, 0.04)
# Nolvl speed everything between (0.0001, 0.0005)
def click_random_throw():
    """Random throw click implementation with medium speed"""
    x, y = random.randint(940, 950), random.randint(330, 340)
    mouse.move(x, y, duration=random.uniform(0.0001, 0.0005))
    time.sleep(random.uniform(0.0001, 0.0005))
    mouse.click()
def capture_screen():
    screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    hwin = win32gui.GetDesktopWindow()
    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()

    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, screen_width, screen_height)
    memdc.SelectObject(bmp)

    memdc.BitBlt((0, 0), (screen_width, screen_height), srcdc, (0, 0), win32con.SRCCOPY)
    bits = bmp.GetBitmapBits(True)

    # Clean up resources
    memdc.DeleteDC()
    srcdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())
    return bits, screen_width, screen_height

def get_resolution_pyautogui():
    cur_width, cur_height = pyautogui.size()
    return cur_width, cur_height
class BubbleDetector:
    def __init__(self):
        self.last_detection_time = 0
        self.detection_cooldown = 2.0  # Cooldown in seconds

    def check_air_bubbles_on_screen(self):
        """Check for air bubbles with cooldown to prevent multiple detections"""
        current_time = time.time()
        if current_time - self.last_detection_time < self.detection_cooldown:
            return False

        try:
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

            hwin = win32gui.GetDesktopWindow()
            hwindc = win32gui.GetWindowDC(hwin)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()

            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, screen_width, screen_height)
            memdc.SelectObject(bmp)

            memdc.BitBlt((0, 0), (screen_width, screen_height), srcdc, (0, 0), win32con.SRCCOPY)
            bits = bmp.GetBitmapBits(True)

            # Clean up resources
            memdc.DeleteDC()
            srcdc.DeleteDC()
            win32gui.ReleaseDC(hwin, hwindc)
            win32gui.DeleteObject(bmp.GetHandle())

            chunk_size = 50
            matches_found = False

            for y in range(0, screen_height - chunk_size, chunk_size):
                if matches_found:
                    break
                for x in range(0, screen_width - chunk_size, chunk_size):
                    matches = 0
                    for sample_y in range(y, y + chunk_size, 2):
                        for sample_x in range(x, x + chunk_size, 2):
                            pixel_offset = ((sample_y * screen_width + sample_x) * 4)
                            if pixel_offset + 2 >= len(bits):
                                continue

                            b = bits[pixel_offset]
                            g = bits[pixel_offset + 1]
                            r = bits[pixel_offset + 2]

                            if (abs(r - 68) < 2 and
                                abs(g - 252) < 2 and
                                abs(b - 234) < 2):
                                matches += 1

                            if matches >= 3:
                                self.last_detection_time = current_time
                                return True

            return False

        except Exception as e:
            print(f"Error checking bubbles: {e}")
            return False

def main():
    """Main function to run the fishing bot"""
    counter = 0
    fish_counter = 0
    fish_found = False
    bubble_detector = BubbleDetector()

    print("Fishing bot started. Press 'q' to quit.")
    print("Please wait 3 seconds before starting...")
    time.sleep(3)

    # Initial cast
    print("Making initial cast...")
    click_random_throw()
    time.sleep(1)

    while not keyboard.is_pressed('q'):
        try:
            # Check if fish is found
            if is_fish_detected():
                print("Fish detected!")
                click_random_throw()
                fish_found = True
                time.sleep(0.01)

            # Increase fish counter if found
            if fish_found:
                if verify_fish_caught():
                    fish_counter += 1
                    print(f'Fish caught: {fish_counter}')
                    fish_found = False
                    time.sleep(0.5)  # Increased wait time after catching
                    click_random_throw()

            # If fish not found, check for air bubbles
            if not fish_found:
                if bubble_detector.check_air_bubbles_on_screen():
                    print("Bubbles detected!")
                    click_random_throw()
                    time.sleep(0.2)

            # If inventory is full, exit
            if fish_counter == 2000:
                print('Inventory full, selling...')
                return

            time.sleep(0.01)

        except KeyboardInterrupt:
            print("\nBot stopped by user")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    main()
