import gi
import subprocess
import sys
import os
import logging
from datetime import datetime, timedelta
from gi.repository import GLib

gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3, Gtk

APP_ID = 'gpu_tray_icon'

def setup_logging():
    """Setup logging configuration before any other operations"""
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(script_dir, 'logs')
        
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate today's log filename
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(log_dir, f'{today}.log')
        
        # Configure logging with force=True to override any existing configuration
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s',
            force=True  # This ensures reconfiguration if already configured
        )
        
        # Test logging to ensure it's working
        logging.info("="*50)
        logging.info("Logging system initialized successfully")
        logging.info(f"Log file: {log_file}")
        logging.info(f"Script directory: {script_dir}")
        logging.info(f"Process ID: {os.getpid()}")
        
        # Clean up previous day's log file
        prev_day = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        prev_log = os.path.join(log_dir, f'{prev_day}.log')
        if os.path.exists(prev_log):
            try:
                os.remove(prev_log)
                logging.info(f"Deleted previous day's log file: {prev_log}")
            except Exception as e:
                logging.warning(f"Failed to delete previous day's log file: {e}")
        
        return True
        
    except Exception as e:
        # If file logging fails, fall back to console logging
        print(f"Failed to setup file logging: {e}")
        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s %(levelname)s: %(message)s',
                force=True
            )
            logging.error(f"File logging failed, using console logging: {e}")
            return False
        except Exception as console_error:
            print(f"Complete logging failure: {console_error}")
            return False

class GPUTrayIcon:
    def __init__(self):
        logging.info("GPU Tray Icon application starting up")
        
        # Get initial GPU status
        initial_gpu = self.get_current_gpu()
        logging.info(f"Initial GPU detected: {initial_gpu}")
        
        self.indicator = AppIndicator3.Indicator.new(
            APP_ID,
            self.get_icon_path(),
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        logging.info("System tray indicator created and activated")
        
        self.menu = Gtk.Menu()
        self.update_gpu()
        self.build_menu()
        self.indicator.set_menu(self.menu)
        logging.info("GPU Tray Icon application initialized successfully")

    def get_current_gpu(self):
        logging.info("Querying current GPU status using prime-select")
        try:
            result = subprocess.check_output(['prime-select', 'query'], text=True).strip()
            gpu_name = result.capitalize()
            logging.info(f"GPU detection successful: {gpu_name}")
            return gpu_name
        except Exception as e:
            logging.error(f"GPU detection failed: {e}")
            return "Unknown"

    def get_icon_path(self):
        gpu = self.get_current_gpu().lower()
        base_path = "/mnt/Work/Python_Projects/GPU_DETECTION_TOOL/icons/"
        
        if "nvidia" in gpu:
            icon_path = base_path + "nvidia.ico"
        elif "intel" in gpu:
            icon_path = base_path + "intel.ico"
        elif "amd" in gpu:
            icon_path = base_path + "amd.ico"
        else:
            icon_path = base_path + "intel.ico"  # fallback
        
        logging.info(f"Selected icon path: {icon_path} for GPU: {gpu}")
        return icon_path

    def switch_gpu(self):
        import threading
        logging.info("GPU switch initiated by user")
        
        current = self.get_current_gpu().lower()
        target = 'nvidia' if current == 'intel' else 'intel'
        logging.info(f"Switching from {current} to {target}")
        
        # Update UI to show switching state
        self.indicator.set_label("Switching...", "")
        self.indicator.set_icon_full(self.get_loading_icon_path(), "Loading Icon")
        logging.info("Updated tray icon to show switching state")
        
        while Gtk.events_pending():
            Gtk.main_iteration()

        def do_switch():
            switch_success = False
            try:
                logging.info(f"Executing prime-select command to switch to {target}")
                result = subprocess.run(['sudo', '/usr/bin/prime-select', target], check=True)
                switch_success = (result.returncode == 0)
                logging.info(f"Switched GPU to {target}. Success: {switch_success}")
            except Exception as e:
                logging.error(f"Failed to switch GPU to {target}: {e}")
            
            GLib.idle_add(self.update_gpu)
            if switch_success:
                GLib.idle_add(self.show_logout_notification)

        threading.Thread(target=do_switch, daemon=True).start()

    def get_loading_icon_path(self):
        loading_path = "/mnt/Work/Python_Projects/GPU_DETECTION_TOOL/icons/loading.ico"
        logging.info(f"Using loading icon: {loading_path}")
        return loading_path

    def show_logout_notification(self):
        logging.info("Displaying logout notification dialog to user")
        dialog = Gtk.MessageDialog(
            parent=None,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="GPU switched! Please logout and login again for changes to take effect."
        )
        dialog.format_secondary_text(
            "Click 'OK' to logout now, or 'Cancel' to logout later."
        )
        
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            logging.info("User chose to logout immediately")
            try:
                subprocess.run(['gnome-session-quit', '--logout', '--no-prompt'])
                logging.info("Logout command executed successfully")
            except Exception as e:
                logging.error(f"Failed to execute logout command: {e}")
        else:
            logging.info("User chose to logout later")
        
        dialog.destroy()
        logging.info("Logout notification dialog closed")

    def update_gpu(self):
        logging.info("Updating GPU status and tray icon")
        gpu = self.get_current_gpu()
        
        # Update label
        self.indicator.set_label(f"GPU: {gpu}", "")
        logging.info(f"Updated tray label to: GPU: {gpu}")
        
        # Update icon
        icon_path = self.get_icon_path()
        self.indicator.set_icon_full(icon_path, "GPU Icon")
        logging.info(f"Updated tray icon to: {icon_path}")

    def build_menu(self):
        logging.info("Building context menu for tray icon")
        
        # Create Switch GPU menu item
        switch_item = Gtk.MenuItem(label="Switch GPU")
        switch_item.connect("activate", self.on_switch)
        self.menu.append(switch_item)
        logging.info("Added 'Switch GPU' menu item")
        
        # Create Quit menu item
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.on_quit)
        self.menu.append(quit_item)
        logging.info("Added 'Quit' menu item")
        
        self.menu.show_all()
        logging.info("Context menu built and displayed")

    def on_switch(self, _):
        logging.info("User clicked 'Switch GPU' menu item")
        self.switch_gpu()

    def on_quit(self, _):
        logging.info("User clicked 'Quit' menu item")
        logging.info("GPU Tray Icon application shutting down")
        Gtk.main_quit()

def main():
    # Setup logging first, before any other operations
    logging_success = setup_logging()
    
    if logging_success:
        logging.info("Starting GPU Tray Icon main function")
    else:
        print("Warning: Logging setup failed, continuing with console logging")
        logging.warning("Starting GPU Tray Icon main function with degraded logging")
    
    try:
        app = GPUTrayIcon()
        logging.info("Entering GTK main event loop")
        Gtk.main()
        logging.info("GTK main event loop ended - application terminated")
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
