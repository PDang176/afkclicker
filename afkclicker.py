import time
import threading
import pyautogui
import pywinctl as pwc
import numpy as np
import cv2

from pynput import keyboard
from rapidocr_onnxruntime import RapidOCR

class AFKClicker:
    def __init__(self):
        self.program_running = True
        self.running = False
        self.listener = keyboard.GlobalHotKeys({
            '<ctrl>+`': self.quit_program,
            '<ctrl>+[': self.afk_fishing,
            # '<ctrl>+x': self.afk_xp_farm_skeletons,
            '<ctrl>+]': self.stop_afk
        })
        self.minecraft_bounds = None
        self.target_text = None
        self.button = None

        self.retry_interval = 0.1
        self.click_interval = 2

        self.ocr = RapidOCR()
        self.thread = threading.Thread(target=self.run, daemon=True)


    def get_minecraft_window_bounds(self):
        windows = pwc.getWindowsWithTitle('minecraft', condition=pwc.Re.CONTAINS, flags=pwc.Re.IGNORECASE)
        windows = [w for w in windows if "launcher" not in w.title.lower()]
        if windows and windows[0].isVisible:
            left, top, width, height = windows[0].box
            
            new_left = left + (width // 2)
            new_top = top + (height // 2)
            new_width = width // 2
            new_height = height // 2

            self.minecraft_bounds = (new_left, new_top, new_width, new_height)
        else:
            print("Minecraft window not found. Please make sure Minecraft is running.")

    def quit_program(self):
        print("Exiting AFK Clicker...")
        self.running = False
        self.program_running = False
        self.listener.stop()

    def run(self):
        while self.program_running:
            if not self.running or not self.target_text:
                time.sleep(self.retry_interval)
                continue

            self.get_minecraft_window_bounds()
            if not self.minecraft_bounds:
                print("Minecraft window bounds not set. Retrying...")
                time.sleep(self.retry_interval)
                continue

            screenshot = pyautogui.screenshot(region=self.minecraft_bounds)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            frame = cv2.resize(frame, None, fx=2, fy=2)

            # screenshot.save("debug_screenshot.png")
            # continue

            results, _ = self.ocr(frame)
            if not results:
                continue

            text = " ".join([line[1] for line in result])

            if self.target_text.lower() in text.lower():
                print(f"Text '{self.target_text}' detected → clicking")
                pyautogui.click(button=self.button)
                time.sleep(self.click_interval)
                pyautogui.click(button=self.button)
            
            time.sleep(self.retry_interval)

    def stop_afk(self):
        print("Ending AFK Session...")
        self.running = False
        self.button = None
        self.target_text = None

    def afk_fishing(self):
        if self.running:
            print("Already running an AFK session. Please stop it first.")
            return

        print("Starting AFK Fishing...")
        self.target_text = "fishing bobber splashes"
        self.button = "right"
        self.running = True

    def afk_xp_farm_skeletons(self):
        if self.running:
            print("Already running an AFK session. Please stop it first.")
            return
        print("Starting AFK XP Farm for Skeletons...")
        self.target_text = "skeleton rattles"
        self.button = "left"
        self.running = True

    def start(self):
        print("Starting AFK Clicker...")
        self.thread.start()
        with self.listener:
            self.listener.join()

if __name__ == "__main__":
    app = AFKClicker()
    app.start()