import subprocess
import time
import pyautogui
import pygetwindow as gw
import os

os.makedirs("screenshots", exist_ok=True)


def run_and_type_in_exe(runArgsStr, input_str, file_name):
    subprocess.Popen(
        f'start cmd /c "{runArgsStr} && echo. && echo. && pause"', shell=True
    )
    win = None
    start_time = time.time()
    while time.time() - start_time < 5:
        windows = [
            w for w in gw.getWindowsWithTitle("cmd") if w.isActive or w.isVisible
        ]
        if windows:
            win = windows[0]
            win.activate()
            break
        time.sleep(0.1)

    for inp in input_str.split("\n"):
        pyautogui.typewrite(inp, interval=0.02)
        pyautogui.press("enter")

    time.sleep(1.8)

    if win:
        left, top, width, height = win.left, win.top, win.width, win.height
        screenshot_path = os.path.join("screenshots", file_name + ".png")
        pyautogui.screenshot(screenshot_path, region=(left, top, width, height))

    pyautogui.press("enter")
