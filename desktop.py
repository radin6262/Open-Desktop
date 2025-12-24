#!/usr/bin/env python3
import gi
import json
import os
import subprocess
import configparser
gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.1")
gi.require_version("Gdk", "3.0")
gi.require_version("Wnck", "3.0")

from gi.repository import Gtk, WebKit2, Gdk, Wnck, GLib

class DesktopService(Gtk.Window):
    def __init__(self):
        super().__init__(title="GoldenMoon Desktop env")
        self.set_decorated(False)
        self.fullscreen()

        # Get absolute path to the directory where this script lives
        self.base_dir = os.path.dirname(os.path.realpath(__file__))

        # WebKit Settings for Local File Access and Security
        settings = WebKit2.Settings()
        settings.set_allow_universal_access_from_file_urls(True)
        settings.set_allow_file_access_from_file_urls(True)

        # JS-Python Bridge Setup
        self.content_manager = WebKit2.UserContentManager()
        self.content_manager.register_script_message_handler("bridge")
        self.content_manager.connect("script-message-received::bridge", self.on_js_message)

        # WebView Initialization
        self.webview = WebKit2.WebView.new_with_user_content_manager(self.content_manager)
        self.webview.set_settings(settings)
        
        # Load local HTML
        html_path = "file://" + os.path.join(self.base_dir, "desktop.html")
        self.webview.load_uri(html_path)

        self.add(self.webview)
        self.connect("destroy", Gtk.main_quit)

        # Initialize Wnck for Window Tracking
        self.screen = Wnck.Screen.get_default()
        # Update running apps status every 2 seconds
        GLib.timeout_add_seconds(2, self.update_running_apps)

        self.show_all()

    def get_system_icon_path(self, icon_name):
        """Resolves system icon names to absolute file:// paths."""
        icon_theme = Gtk.IconTheme.get_default()
        icon_info = icon_theme.lookup_icon(icon_name, 48, 0)
        return "file://" + icon_info.get_filename() if icon_info else ""

    def update_running_apps(self):
        """Checks for open windows and tells JS which apps are running."""
        self.screen.force_update()
        running_windows = [w.get_class_group_name().lower() for w in self.screen.get_windows()]
        self.webview.run_javascript(f"updateRunningIndicators({json.dumps(running_windows)})")
        return True

    def on_js_message(self, manager, result):
        """Primary handler for JS bridge calls."""
        message = result.get_js_value().to_string()
        data = json.loads(message)
        action = data.get("action")

        if action == "get_dock_apps":
            self.handle_get_dock_apps()
        elif action == "launch_app":
            # Passing the FilePathBased flag from JS
            self.handle_launch_app(data.get("command"), data.get("file_path_based", False))
        elif action == "focus_app":
            self.handle_focus_app(data.get("command"))
        elif action == "power_command":
            cmd = data.get("command")
            if cmd == "shutdown": subprocess.Popen(["systemctl", "poweroff"])
            elif cmd == "restart": subprocess.Popen(["systemctl", "reboot"])
            elif cmd == "sleep": subprocess.Popen(["systemctl", "suspend"])
        elif action == "get_power_icons":
            self.handle_get_power_icons()
        elif action == "open_bg_picker":
            self.handle_open_bg_picker()
        elif action == "get_saved_background":
            self.handle_get_saved_background()
        elif action == "get_start_apps":
            self.handle_get_start_apps()

    def handle_get_dock_apps(self):
        """Reads dock.json and resolves icons locally or from system."""
        try:
            dock_path = os.path.join(self.base_dir, "dock.json")
            with open(dock_path, "r") as f:
                apps = json.load(f)
            
            for app in apps:
                if app.get("FilePathBased"):
                    # Load icon from local folder
                    local_icon = os.path.join(self.base_dir, app['icon'])
                    app['icon_path'] = "file://" + local_icon
                else:
                    # Load icon from gnome theme
                    app['icon_path'] = self.get_system_icon_path(app['icon'])
            
            self.webview.run_javascript(f"receiveDockData({json.dumps(apps)})")
        except Exception as e:
            print(f"Error loading dock.json: {e}")

    def handle_launch_app(self, command, is_python_script):
        """Executes the app. If is_python_script is true, runs with python3."""
        try:
            if is_python_script:
                # Resolve script relative to this folder
                script_path = os.path.join(self.base_dir, command)
                subprocess.Popen(["python3", script_path], cwd=self.base_dir)
            else:
                # Normal command execution
                subprocess.Popen(command.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.webview.run_javascript("onLaunchResult(true, '')")
        except Exception as e:
            self.webview.run_javascript(f"onLaunchResult(false, '{str(e)}')")

    def handle_get_power_icons(self):
        icons = {
            "shutdown": self.get_system_icon_path("system-shutdown"),
            "restart": self.get_system_icon_path("system-reboot"),
            "sleep": self.get_system_icon_path("system-suspend")
        }
        self.webview.run_javascript(f"receivePowerIcons({json.dumps(icons)})")

    def handle_open_bg_picker(self):
        """Native GTK file picker for background image."""
        dialog = Gtk.FileChooserDialog(
            title="Select Wallpaper", parent=self, action=Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            # Save choice to config.json
            config_path = os.path.join(self.base_dir, "config.json")
            with open(config_path, "w") as f:
                json.dump({"wallpaper": file_path}, f)
            # Update JS
            self.webview.run_javascript(f"applyBackground('file://{file_path}')")
        dialog.destroy()

    def handle_get_saved_background(self):
        """Loads wallpaper from config.json or sends null for default."""
        saved_path = None
        config_path = os.path.join(self.base_dir, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    path = data.get("wallpaper")
                    if path and os.path.exists(path):
                        saved_path = "file://" + path
            except: pass
        self.webview.run_javascript(f"receiveSavedBackground({json.dumps(saved_path)})")

    def handle_focus_app(self, command):
        """Brings an already running window to the front."""
        self.screen.force_update()
        target = command.lower()
        for window in self.screen.get_windows():
            if target in window.get_class_group_name().lower():
                window.activate(Gdk.CURRENT_TIME)
                break
    import configparser

# ... inside DesktopService class ...

    def handle_get_start_apps(self):
        """Scans Linux standard paths for .desktop files and parses them."""
        app_dirs = [
            "/usr/share/applications",
            os.path.expanduser("~/.local/share/applications")
        ]
        
        apps_list = []
        seen_names = set()

        for adir in app_dirs:
            if not os.path.exists(adir): continue
            for file in os.listdir(adir):
                if file.endswith(".desktop"):
                    path = os.path.join(adir, file)
                    try:
                        # Use ConfigParser to read .desktop (INI format)
                        config = configparser.ConfigParser(interpolation=None)
                        config.read(path)
                        
                        if "Desktop Entry" in config:
                            entry = config["Desktop Entry"]
                            # Skip hidden apps or non-apps
                            if entry.get("NoDisplay") == "true" or entry.get("Type") != "Application":
                                continue
                                
                            name = entry.get("Name", "Unknown")
                            exec_cmd = entry.get("Exec", "").split(" %")[0] # Strip %u, %f etc
                            icon = entry.get("Icon", "system-run")
                            
                            # Avoid duplicates (user local overrides system)
                            if name not in seen_names:
                                apps_list.append({
                                    "name": name,
                                    "exec": exec_cmd,
                                    "icon": self.get_system_icon_path(icon)
                                })
                                seen_names.add(name)
                    except Exception as e:
                        print(f"Error parsing {file}: {e}")

        # Sort alphabetically
        apps_list.sort(key=lambda x: x["name"].lower())
        self.webview.run_javascript(f"receiveStartMenuApps({json.dumps(apps_list)})")

# Update your on_js_message to include:
# elif action == "get_start_apps": self.handle_get_start_apps()

if __name__ == "__main__":
    DesktopService()
    Gtk.main()