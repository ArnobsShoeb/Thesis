import psutil
import time
import threading
import tkinter as tk
from tkinter import messagebox
import queue
import signal
import sys

popup_queue = queue.Queue()
running = True  # Global flag to stop the loop gracefully

def check_usb():
    usb_drives = []
    partitions = psutil.disk_partitions(all=False)
    for partition in partitions:
        if 'removable' in partition.opts.lower():
            usb_drives.append(partition.device)
    return usb_drives

def monitor_usb():
    connected_devices = set(check_usb())
    print("Monitoring USB devices on Windows... (Press Ctrl+C to stop)\n")

    while running:
        current_devices = set(check_usb())

        # Detect newly connected devices
        new_devices = current_devices - connected_devices
        for dev in new_devices:
            msg = f"New USB device connected: {dev}"
            print(msg)
            popup_queue.put(msg)

        # Detect disconnected devices
        removed_devices = connected_devices - current_devices
        for dev in removed_devices:
            msg = f"USB device removed: {dev}"
            print(msg)
            popup_queue.put(msg)

        connected_devices = current_devices
        time.sleep(1)

def process_popups(root):
    if not running:
        root.quit()  # Exit the GUI loop if Ctrl+C was pressed
        return

    try:
        if not popup_queue.empty():
            msg = popup_queue.get()
            messagebox.showinfo("USB Notification", msg)
    except tk.TclError:
        return  # If GUI is closed unexpectedly

    root.after(200, lambda: process_popups(root))  # Check again after 200ms

def signal_handler(sig, frame):
    global running
    print("\nStopping monitoring and closing the program...")
    running = False

def start_monitoring():
    root = tk.Tk()
    root.withdraw()

    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal_handler)

    # Start USB monitoring in background
    t = threading.Thread(target=monitor_usb, daemon=True)
    t.start()

    # Start checking for popup messages
    process_popups(root)

    # Run the GUI loop
    root.mainloop()

if __name__ == "__main__":
    if not psutil.WINDOWS:
        print("This script is intended to run on Windows only.")
    else:
        start_monitoring()
