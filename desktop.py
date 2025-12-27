# Visit our github repo for more info on license

# You are prohibited of coping/rewriting/integrating this code with your personal app
# Usage of this app is only permitted to personal or commercial use but you can't use it as "tradiing/buy/sell/rent/redist"
# Copyright 2025 (C) Radin6262, All rights reserved

#!/usr/bin/env python3
import gi
import json
import os
import subprocess
import configparser

# Core dependencies for GUI, Web Rendering, and Window Management
gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.1")
gi.require_version("Gdk", "3.0")
gi.require_version("Wnck", "3.0")

from gi.repository import Gtk, WebKit2, Gdk, Wnck, GLib

class OpenDesktop(Gtk.Window):
    def __init__(self):
        super().__init__(title="OpenDesktop Environment")
        self.set_decorated(False)
        self.fullscreen()

        # Absolute path tracking for assets and scripts
        self.base_dir = os.path.dirname(os.path.realpath(__file__))

        # WebKit Configuration: Enable local file access
        settings = WebKit2.Settings()
        settings.set_allow_universal_access_from_file_urls(True)
        settings.set_allow_file_access_from_file_urls(True)
        settings.set_enable_developer_extras(True)

        # Content Manager for Javascript <-> Python Bridge
        self.content_manager = WebKit2.UserContentManager()
        self.content_manager.register_script_message_handler("bridge")
        self.content_manager.connect("script-message-received::bridge", self.on_js_message)

        # Initialize the webview
        self.webview = WebKit2.WebView.new_with_user_content_manager(self.content_manager)
        self.webview.set_settings(settings)
        
        # Load the HTML interface
        html_path = "file://" + os.path.join(self.base_dir, "desktop.html")
        self.webview.load_uri(html_path)

        self.add(self.webview)
        self.connect("destroy", Gtk.main_quit)

        # Window Tracking Setup via libwnck
        self.screen = Wnck.Screen.get_default()
        # Poll for running apps every 2 seconds to update the dock/taskbar
        GLib.timeout_add_seconds(2, self.update_running_apps)

        self.show_all()

    def get_system_icon_path(self, icon_name):
        """Resolves system icon names to full local paths, with a fallback."""
        # Define the default fallback icon name
        DEFAULT_ICON = "preferences-system" 
        
        icon_theme = Gtk.IconTheme.get_default()
        
        # 1. Try to find the requested icon
        if icon_name:
            icon_info = icon_theme.lookup_icon(icon_name, 48, 0)
            if icon_info:
                return "file://" + icon_info.get_filename()
        
        # 2. Fallback: Try to find the default settings icon
        fallback_info = icon_theme.lookup_icon(DEFAULT_ICON, 48, 0)
        if fallback_info:
            return "file://" + fallback_info.get_filename()
            
        # 3. Ultimate safety: return empty string if even the fallback is missing
        return ""

    def update_running_apps(self):
        """Scans the window list and sends details to the frontend."""
        self.screen.force_update()
        running_data = []
        for w in self.screen.get_windows():
            # Filter for normal application windows only
            if w.get_window_type() == Wnck.WindowType.NORMAL:
                class_group = w.get_class_group_name().lower()
                running_data.append({
                    "class": class_group,
                    "xid": w.get_xid(),
                    "name": w.get_name(),
                    "icon": self.get_system_icon_path(class_group)
                })
        
        # Inject the window list into the JS environment
        js_call = f"updateRunningIndicators({json.dumps(running_data)})"
        self.webview.run_javascript(js_call)
        return True

    def on_js_message(self, manager, result):
        """Dispatches messages from the UI to Python handlers."""
        try:
            message = result.get_js_value().to_string()
            data = json.loads(message)
            action = data.get("action")

            if action == "get_dock_apps":
                self.handle_get_dock_apps()
            elif action == "launch_app":
                self.handle_launch_app(data.get("command"), data.get("file_path_based", False))
            elif action == "focus_app":
                self.handle_focus_app_by_xid(data.get("xid"))
            elif action == "focus_app_by_command":
                self.handle_focus_app_by_command(data.get("command"))
            elif action == "close_app":
                self.handle_close_app(data.get("xid"))
            elif action == "get_start_apps":
                self.handle_get_start_apps()
            elif action == "get_power_icons":
                self.handle_get_power_icons()
            elif action == "power_command":
                self.handle_power_command(data.get("command"))
            elif action == "open_bg_picker":
                self.handle_open_bg_picker()
            elif action == "get_saved_background":
                self.handle_get_saved_background()
        except Exception as e:
            print(f"Bridge error: {e}")

    def handle_get_dock_apps(self):
        """Loads pinned apps from dock.json."""
        try:
            dock_path = os.path.join(self.base_dir, "dock.json")
            if not os.path.exists(dock_path):
                self.webview.run_javascript("receiveDockData([])")
                return

            with open(dock_path, "r") as f:
                apps = json.load(f)
            
            for app in apps:
                if app.get("FilePathBased"):
                    app['icon_path'] = "file://" + os.path.join(self.base_dir, app['icon'])
                else:
                    app['icon_path'] = self.get_system_icon_path(app['icon'])
            
            self.webview.run_javascript(f"receiveDockData({json.dumps(apps)})")
        except Exception as e:
            print(f"Error in handle_get_dock_apps: {e}")

    def handle_launch_app(self, command, is_python_script):
        """Launches an application or script."""
        try:
            if is_python_script:
                script_path = os.path.join(self.base_dir, command)
                subprocess.Popen(["python3", script_path], cwd=self.base_dir)
            else:
                subprocess.Popen(command.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.webview.run_javascript("onLaunchResult(true, '')")
        except Exception as e:
            self.webview.run_javascript(f"onLaunchResult(false, '{str(e)}')")

    def handle_close_app(self, xid):
        """Closes a specific window using its XID."""
        self.screen.force_update()
        for window in self.screen.get_windows():
            if window.get_xid() == xid:
                window.close(Gdk.CURRENT_TIME)
                break

    def handle_focus_app_by_xid(self, xid):
        """Focuses/Pops up an existing window by its XID."""
        self.screen.force_update()
        for window in self.screen.get_windows():
            if window.get_xid() == xid:
                window.activate(Gdk.CURRENT_TIME)
                break

    def handle_focus_app_by_command(self, command):
        """Focuses an existing window by matching class name."""
        self.screen.force_update()
        target = command.lower()
        for window in self.screen.get_windows():
            if target in window.get_class_group_name().lower():
                window.activate(Gdk.CURRENT_TIME)
                break

    def handle_get_start_apps(self):
        """Parses system .desktop files for the Start Menu."""
        app_dirs = ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]
        apps_list = []
        seen_names = set()

        for adir in app_dirs:
            if not os.path.exists(adir): continue
            for file in os.listdir(adir):
                if file.endswith(".desktop"):
                    try:
                        config = configparser.ConfigParser(interpolation=None)
                        config.read(os.path.join(adir, file))
                        if "Desktop Entry" in config:
                            entry = config["Desktop Entry"]
                            if entry.get("NoDisplay") == "true" or entry.get("Type") != "Application":
                                continue
                            
                            name = entry.get("Name", "Unknown")
                            if name not in seen_names:
                                apps_list.append({
                                    "name": name,
                                    "exec": entry.get("Exec", "").split(" %")[0].replace('"', ''),
                                    "icon": self.get_system_icon_path(entry.get("Icon", "system-run"))
                                })
                                seen_names.add(name)
                    except:
                        pass
        
        apps_list.sort(key=lambda x: x["name"].lower())
        self.webview.run_javascript(f"receiveStartMenuApps({json.dumps(apps_list)})")

    def handle_get_power_icons(self):
        """Fetches system icons for power actions."""
        icons = {
            "shutdown": self.get_system_icon_path("system-shutdown"),
            "restart": self.get_system_icon_path("system-reboot"),
            "sleep": self.get_system_icon_path("system-suspend")
        }
        self.webview.run_javascript(f"receivePowerIcons({json.dumps(icons)})")

    def handle_power_command(self, cmd):
        """Executes systemctl power commands."""
        if cmd == "shutdown": subprocess.Popen(["systemctl", "poweroff"])
        elif cmd == "restart": subprocess.Popen(["systemctl", "reboot"])
        elif cmd == "sleep": subprocess.Popen(["systemctl", "suspend"])

    def handle_open_bg_picker(self):
        """Opens a GTK File Chooser for wallpaper selection."""
        dialog = Gtk.FileChooserDialog(
            title="Select Wallpaper", 
            parent=self, 
            action=Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        
        filter_img = Gtk.FileFilter()
        filter_img.set_name("Images")
        filter_img.add_mime_type("image/png")
        filter_img.add_mime_type("image/jpeg")
        dialog.add_filter(filter_img)

        if dialog.run() == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            config_path = os.path.join(self.base_dir, "config.json")
            with open(config_path, "w") as f:
                json.dump({"wallpaper": path}, f)
            self.webview.run_javascript(f"applyBackground('file://{path}')")
        
        dialog.destroy()

    def handle_get_saved_background(self):
        """Restores the wallpaper from config.json."""
        config_path = os.path.join(self.base_dir, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    path = data.get("wallpaper")
                    if path and os.path.exists(path):
                        self.webview.run_javascript(f"receiveSavedBackground('file://{path}')")
            except:
                pass

if __name__ == "__main__":
    GLib.idle_add(lambda: Wnck.Screen.get_default().force_update())
    OpenDesktop()
    Gtk.main()