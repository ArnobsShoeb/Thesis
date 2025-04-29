import wmi
import time


def get_usb_info():
    c = wmi.WMI()
    usb_info_list = []
   
    for disk in c.Win32_DiskDrive():
        if 'USB' in disk.InterfaceType:  # Ensure it's a USB device
            partitions = [p for p in c.Win32_DiskPartition() if p.DeviceID in disk.DeviceID]
            logical_disks = [
                ld for p in partitions for ld in c.Win32_LogicalDisk() if ld.DeviceID in p.DeviceID
            ]
           
            usb_info = {
                "Model": disk.Model,
                "Size (GB)": round(int(disk.Size) / (1024**3), 2) if disk.Size else "Unknown",
                "Serial Number": disk.SerialNumber.strip() if disk.SerialNumber else "Unknown",
                "Partitions": len(partitions),
                "File System": logical_disks[0].FileSystem if logical_disks else "Unknown",
                "Drive Letter": logical_disks[0].DeviceID if logical_disks else "Unknown"
            }
            usb_info_list.append(usb_info)
   
    return usb_info_list


def monitor_usb():
    print("Listening for USB insert/removal events...\n")
    previous_drives = set(d["Drive Letter"] for d in get_usb_info())


    while True:
        time.sleep(2)  # Check every 2 seconds
        current_drives = set(d["Drive Letter"] for d in get_usb_info())
       
        added = current_drives - previous_drives
        removed = previous_drives - current_drives
       
        if added:
            for drive in added:
                print(f"USB Inserted: {drive}")
                for usb in get_usb_info():
                    if usb["Drive Letter"] == drive:
                        print(f"  📌 Model: {usb['Model']}")
                        print(f"  🔢 Serial Number: {usb['Serial Number']}")
                        print(f"  💾 Size: {usb['Size (GB)']} GB")
                        print(f"  🗂️ File System: {usb['File System']}")
                        print(f"  📂 Drive Letter: {usb['Drive Letter']}\n")
       
        if removed:
            for drive in removed:
                print(f"USB Removed: {drive}\n")


        previous_drives = current_drives


# Run the monitor function
monitor_usb()