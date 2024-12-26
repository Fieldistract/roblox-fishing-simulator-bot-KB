# Approach 1: Using win32api (your current approach, but simplified)
import win32api
import win32con
import pyautogui

def get_resolution_pyautogui():
    width, height = pyautogui.size()
    return width, height

def get_positions():
    try:
        print("\nPyautogui resolution:")
        width, height = get_resolution_pyautogui()
        print(f"{width}x{height}")
    except:
        print("PyAutoGUI not installed")

get_positions()
