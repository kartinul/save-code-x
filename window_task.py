import subprocess
import time
import pyautogui
import pygetwindow as gw
import os
from threading import Thread
from pynput import keyboard

stop_flag = False
input_mode = False


def on_press(key):
    global stop_flag, input_mode
    try:
        if key.char and key.char.lower() == "x" and not input_mode:
            print("\n[X] Stop key pressed — terminating execution...")
            stop_flag = True
            closeAllCMD()
    except:
        pass


def keyboard_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def closeAllCMD():
    for w in gw.getWindowsWithTitle("cmd"):
        try:
            w.close()
        except:
            pass


def runTypeAndSS(runArgsStr, input_str, file_name):
    global stop_flag, input_mode
    stop_flag = False
    os.makedirs("screenshots", exist_ok=True)

    subprocess.Popen(
        f'start "" cmd /c "{runArgsStr} && echo. && echo. && pause"', shell=True
    )

    win = None
    start_time = time.time()

    while time.time() - start_time < 5:
        if stop_flag:
            stop_flag = False
            print("returning -1 when searching for cmd")
            return -1
        for w in gw.getWindowsWithTitle("cmd"):
            try:
                if w.width > 100 and w.height > 100:
                    win = w
                    win.activate()
                    break
            except:
                pass
        if win:
            break
        time.sleep(0.05)

    if not win:
        print("no CMD window found")

    if gw.getActiveWindow() is None or gw.getActiveWindow().title != "cmd":
        print("The current window not CMD")

    for inp in input_str.splitlines():
        if stop_flag:
            stop_flag = False
            print("returning -1 while typing")
            return -1
        print(f"inp: {inp}")
        input_mode = True
        pyautogui.write(inp)
        input_mode = False
        pyautogui.press("enter")

    if stop_flag:
        stop_flag = False
        print("returning -1 after typing")
        return -1
    time.sleep(0.8)

    try:
        ss_path = os.path.join("screenshots", f"{file_name}.png")
        pyautogui.screenshot(ss_path, region=(win.left, win.top, win.width, win.height))
        print(f"Screenshot saved: {ss_path}")
    except Exception as e:
        print(f"Screenshot failed for {file_name}: {e}")

    pyautogui.press("enter")


# Start the key listener in a separate thread
Thread(target=keyboard_listener, daemon=True).start()
