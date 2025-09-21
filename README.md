<img width="100%" height="146" alt="Screenshot from 2025-09-21 06-19-31" src="https://github.com/user-attachments/assets/1d0c9c09-efd6-49d3-8dfe-5ca4a2367003" />


# GPU Detection Tray Icon for Zorin OS

This Python app creates a tray icon that displays the currently selected GPU and allows switching between GPUs (NVIDIA/Intel) with a click. It is designed to run as a background service and start automatically at login.

## Features
- Tray icon shows current GPU
- Click to switch GPU (uses `prime-select`)
- Runs as a service at login

## Requirements
- Python 3
- PyGObject (`python3-gi`)
- AppIndicator3 (`gir1.2-appindicator3-0.1`)
- Zorin OS/Ubuntu with NVIDIA/Intel GPUs and `prime-select`
- User must have passwordless sudo access for `prime-select`:
   - Add this line to `/etc/sudoers` using `sudo visudo`:
      ```
      yourusername ALL=(root) NOPASSWD: /usr/bin/prime-select *
      ```
   - Replace `yourusername` with your actual username.


## Installation Steps

1. Clone or copy the project folder to your system.
2. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-gi gir1.2-appindicator3-0.1 prime-select
   ```
3. Set up passwordless sudo for `prime-select` (see Requirements above).
4. Make sure all icon files are present in the `icons/` folder.
5. (Optional) Make the script executable:
   ```bash
   chmod +x /mnt/Work/Python_Projects/GPU_DETECTION_TOOL/tray_gpu.py
   ```
6. (Optional) Test by running:
   ```bash
   python3 /mnt/Work/Python_Projects/GPU_DETECTION_TOOL/tray_gpu.py
   ```

## Autostart

To start the app automatically at login:

1. Create a file named `gpu_tray.desktop` in your autostart folder:
   ```bash
   nano ~/.config/autostart/gpu_tray.desktop
   ```
2. Paste the following content:
   ```ini
   [Desktop Entry]
   Type=Application
   Exec=python3 /mnt/Work/Python_Projects/GPU_DETECTION_TOOL/tray_gpu.py
   Hidden=false
   NoDisplay=false
   X-GNOME-Autostart-enabled=true
   Name=GPU Tray
   Comment=Show and switch current GPU
   ```
3. Save and exit. The app will now start automatically at login.

---

## Icons and Assets

The following icon files must be present in the `icons/` folder:

- `intel.ico` — Icon for Intel GPU
- `nvidia.ico` — Icon for NVIDIA GPU
- `amd.ico` — Icon for AMD GPU (optional)
- `loading.ico` — Icon shown while switching GPUs

You can replace these icons with your own, but keep the filenames and update the code if needed.
