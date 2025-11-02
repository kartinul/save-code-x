import subprocess
import time
import pyautogui
import pygetwindow as gw
import os

def closeAllCMD():
    for w in gw.getWindowsWithTitle("cmd"):
        w.close()

    

def runTypeAndSS(runArgsStr, input_str, file_name):
    os.makedirs("screenshots", exist_ok=True)
    subprocess.Popen(
        f'start "" cmd /c "{runArgsStr} && echo. && echo. && pause"', shell=True
    )

    win = None
    start_time = time.time()

    while time.time() - start_time < 5:
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
        print("No CMD Window Fount")
        return

    if gw.getActiveWindow() is None or gw.getActiveWindow().title != "cmd":
        print("NOT CMD")

        closeAllCMD()
        return -1

    for inp in input_str.splitlines():
        if inp.strip():
            pyautogui.typewrite(inp, interval=0.01)
            pyautogui.press("enter")

    time.sleep(0.8)

    try:
        ss_path = os.path.join("screenshots", f"{file_name}.png")
        pyautogui.screenshot(ss_path, region=(win.left, win.top, win.width, win.height))
        print(f"Screenshot saved: {ss_path}")
    except Exception as e:
        print(f"Screenshot failed for {file_name}: {e}")

    pyautogui.press("enter")
