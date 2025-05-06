import time
from pynput import keyboard
import tkinter as tk
from threading import Thread


# Parameters
DELAY_THRESHOLD = 0.1  # Minimum delay (in seconds) to be considered human
CONSISTENT_COUNT = 10  # How many consistent fast keypresses trigger a warning


last_time = None
fast_count = 0


def show_alert():
    root = tk.Tk()
    root.withdraw()
    tk.messagebox.showwarning("Threat Detected", "Auto typing device detected!")
    root.destroy()


def on_press(key):
    global last_time, fast_count


    current_time = time.time()
    if last_time is not None:
        delay = current_time - last_time
        if delay < DELAY_THRESHOLD:
            fast_count += 1
        else:
            fast_count = 0


        if fast_count >= CONSISTENT_COUNT:
            print("Threat detected")
            Thread(target=show_alert).start()
            fast_count = 0
    last_time = current_time


# Start listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()


