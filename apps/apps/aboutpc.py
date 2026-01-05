import sys
import platform
import psutil
import socket
import os
import time
from datetime import datetime, timedelta
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
# ======= OS CONFIGURATION/BRANDING =======
Os = "OpenDesktop"
# =========================================
class OpenAbout(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Properties")
        self.setFixedSize(560,723)
        
        # Window icon
        self.setWindowIcon(QIcon.fromTheme("computer", 
                          QApplication.style().standardIcon(QStyle.SP_ComputerIcon)))
        
        # Apply XP styling
        self.apply_xp_style()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tabs
        self.create_tabs(main_layout)
        
        # Create buttons
        self.create_buttons(main_layout)
        
        # Timer for dynamic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dynamic_info)
        self.update_timer.start(2000)  # Update every 2 seconds
        
        # Initial data load
        self.update_all_info()
        
    def apply_xp_style(self):
        """Apply Windows XP visual style"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ECE9D8;
            }
            QTabWidget::pane {
                border: 1px solid #8A8A8A;
                background-color: #FFFFFF;
                top: -1px;
            }
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #F1F1F1, stop: 0.4 #E4E4E4,
                    stop: 0.5 #DEDEDE, stop: 1.0 #D8D8D8);
                border: 1px solid #8A8A8A;
                border-bottom-color: #8A8A8A;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                padding: 6px 12px;
                margin-right: 2px;
                font-family: "Tahoma";
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #FFFFFF, stop: 0.4 #F8F8F8,
                    stop: 0.5 #F1F1F1, stop: 1.0 #EAEAEA);
                border-bottom-color: #FFFFFF;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #F6F6F6, stop: 0.4 #E6E6E6,
                    stop: 0.5 #DEDEDE, stop: 1.0 #D6D6D6);
                border: 1px solid #8A8A8A;
                border-radius: 3px;
                padding: 4px 12px;
                font-family: "Tahoma";
                font-size: 11px;
                min-width: 75px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #FFFFFF, stop: 0.4 #F0F0F0,
                    stop: 0.5 #EBEBEB, stop: 1.0 #E6E6E6);
                border: 1px solid #316AC5;
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #D6D6D6, stop: 0.4 #DEDEDE,
                    stop: 0.5 #E6E6E6, stop: 1.0 #F6F6F6);
                padding: 5px 11px 3px 13px;
            }
            QGroupBox {
                font-family: "Tahoma";
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #8A8A8A;
                border-radius: 3px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0px 5px 0px 5px;
            }
            QLabel {
                font-family: "Tahoma";
                font-size: 11px;
            }
            QProgressBar {
                border: 1px solid #8A8A8A;
                border-radius: 3px;
                background-color: #FFFFFF;
                text-align: center;
                font-family: "Tahoma";
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #316AC5;
                border-radius: 2px;
            }
            QLineEdit {
                border: 1px solid #8A8A8A;
                padding: 3px;
                font-family: "Tahoma";
                font-size: 11px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #316AC5;
            }
        """)
        
    def create_tabs(self, layout):
        """Create the XP-style tabs"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont("Tahoma", 10))
        
        # Create tabs
        self.tab_widget.addTab(self.create_general_tab(), "General")
        self.tab_widget.addTab(self.create_computer_tab(), "Computer Name")
        
        layout.addWidget(self.tab_widget)
        
    def create_general_tab(self):
        """Create the General tab with dynamic system info"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with Windows logo
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        # Windows logo
        logo_label = QLabel()
        logo_pixmap = QApplication.style().standardIcon(QStyle.SP_ComputerIcon).pixmap(48, 48)
        logo_label.setPixmap(logo_pixmap)
        header_layout.addWidget(logo_label)
        
        # System info
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        self.system_title = QLabel()
        self.system_title.setFont(QFont("Tahoma", 12, QFont.Bold))
        info_layout.addWidget(self.system_title)
        
        self.version_label = QLabel()
        self.version_label.setFont(QFont("Tahoma", 10))
        info_layout.addWidget(self.version_label)
        
        # Registered to (simulated)
        reg_label = QLabel("Registered to: User")
        reg_label.setFont(QFont("Tahoma", 9))
        info_layout.addWidget(reg_label)
        
        reg_number = QLabel("55274-640-1234567-23149")
        reg_number.setFont(QFont("Tahoma", 9))
        info_layout.addWidget(reg_number)
        
        header_layout.addWidget(info_widget, 1)
        layout.addWidget(header)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #8A8A8A;")
        layout.addWidget(separator)
        
        # Scroll area for dynamic content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content = QWidget()
        scroll.setWidget(content)
        content_layout = QVBoxLayout(content)
        
        # Computer information group
        comp_group = QGroupBox("Computer Information")
        comp_layout = QGridLayout()
        
        comp_layout.addWidget(QLabel("Operating system or desktop: "), 0, 0)
        self.manufacturer_label = QLabel(f"{Os}")
        comp_layout.addWidget(self.manufacturer_label, 0, 1)
        
        comp_layout.addWidget(QLabel("Model:"), 1, 0)
        self.model_label = QLabel("Loading...")
        comp_layout.addWidget(self.model_label, 1, 1)
        
        # comp_layout.addWidget(QLabel("BIOS/UEFI:"), 2, 0)
        # self.bios_label = QLabel("Loading...")
        # comp_layout.addWidget(self.bios_label, 2, 1)
        
        comp_group.setLayout(comp_layout)
        content_layout.addWidget(comp_group)
        
        # Processor information group
        cpu_group = QGroupBox("Processor")
        cpu_layout = QVBoxLayout()
        
        self.cpu_label = QLabel("Loading...")
        cpu_layout.addWidget(self.cpu_label)
        
        # CPU usage progress bar
        cpu_usage_widget = QWidget()
        cpu_usage_layout = QHBoxLayout(cpu_usage_widget)
        cpu_usage_layout.setContentsMargins(5, 5, 5, 5)
        
        cpu_usage_layout.addWidget(QLabel("CPU Usage:"))
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setTextVisible(True)
        cpu_usage_layout.addWidget(self.cpu_progress, 1)
        
        cpu_layout.addWidget(cpu_usage_widget)
        
        # CPU frequency
        cpu_freq_widget = QWidget()
        cpu_freq_layout = QHBoxLayout(cpu_freq_widget)
        cpu_freq_layout.setContentsMargins(5, 5, 5, 5)
        
        cpu_freq_layout.addWidget(QLabel("Frequency:"))
        self.cpu_freq_label = QLabel("Loading...")
        cpu_freq_layout.addWidget(self.cpu_freq_label, 1)
        
        cpu_layout.addWidget(cpu_freq_widget)
        
        # CPU cores
        cpu_cores_widget = QWidget()
        cpu_cores_layout = QHBoxLayout(cpu_cores_widget)
        cpu_cores_layout.setContentsMargins(5, 5, 5, 5)
        
        cpu_cores_layout.addWidget(QLabel("Cores:"))
        self.cpu_cores_label = QLabel("Loading...")
        cpu_cores_layout.addWidget(self.cpu_cores_label, 1)
        
        cpu_layout.addWidget(cpu_cores_widget)
        
        cpu_group.setLayout(cpu_layout)
        content_layout.addWidget(cpu_group)
        
        # Memory information group
        mem_group = QGroupBox("Memory (RAM)")
        mem_layout = QVBoxLayout()
        
        self.memory_label = QLabel("Loading...")
        mem_layout.addWidget(self.memory_label)
        
        # Memory usage progress bar
        mem_usage_widget = QWidget()
        mem_usage_layout = QHBoxLayout(mem_usage_widget)
        mem_usage_layout.setContentsMargins(5, 5, 5, 5)
        
        mem_usage_layout.addWidget(QLabel("Memory Usage:"))
        self.mem_progress = QProgressBar()
        self.mem_progress.setTextVisible(True)
        mem_usage_layout.addWidget(self.mem_progress, 1)
        
        mem_layout.addWidget(mem_usage_widget)
        
        # Memory details
        mem_details_widget = QWidget()
        mem_details_layout = QGridLayout(mem_details_widget)
        mem_details_layout.setContentsMargins(5, 5, 5, 5)
        
        mem_details_layout.addWidget(QLabel("Available:"), 0, 0)
        self.mem_available_label = QLabel("Loading...")
        mem_details_layout.addWidget(self.mem_available_label, 0, 1)
        
        mem_details_layout.addWidget(QLabel("Cached:"), 1, 0)
        self.mem_cached_label = QLabel("Loading...")
        mem_details_layout.addWidget(self.mem_cached_label, 1, 1)
        
        mem_details_layout.addWidget(QLabel("Swap Total:"), 2, 0)
        self.swap_total_label = QLabel("Loading...")
        mem_details_layout.addWidget(self.swap_total_label, 2, 1)
        
        mem_layout.addWidget(mem_details_widget)
        
        mem_group.setLayout(mem_layout)
        content_layout.addWidget(mem_group)
        
        # Storage information group
        storage_group = QGroupBox("Storage")
        storage_layout = QVBoxLayout()
        
        # Primary disk info
        disk_widget = QWidget()
        disk_layout = QVBoxLayout(disk_widget)
        disk_layout.setContentsMargins(5, 5, 5, 5)
        
        self.disk_label = QLabel("Loading...")
        disk_layout.addWidget(self.disk_label)
        
        # Disk usage progress bar
        disk_usage_widget = QWidget()
        disk_usage_layout = QHBoxLayout(disk_usage_widget)
        
        disk_usage_layout.addWidget(QLabel("Disk Usage:"))
        self.disk_progress = QProgressBar()
        self.disk_progress.setTextVisible(True)
        disk_usage_layout.addWidget(self.disk_progress, 1)
        
        disk_layout.addWidget(disk_usage_widget)
        
        # Disk details
        disk_details_widget = QWidget()
        disk_details_layout = QGridLayout(disk_details_widget)
        
        disk_details_layout.addWidget(QLabel("Free:"), 0, 0)
        self.disk_free_label = QLabel("Loading...")
        disk_details_layout.addWidget(self.disk_free_label, 0, 1)
        
        disk_details_layout.addWidget(QLabel("File System:"), 1, 0)
        self.fs_label = QLabel("Loading...")
        disk_details_layout.addWidget(self.fs_label, 1, 1)
        
        disk_layout.addWidget(disk_details_widget)
        
        storage_layout.addWidget(disk_widget)
        
        # All disks button
        disks_button = QPushButton("View All Disks...")
        disks_button.clicked.connect(self.show_all_disks)
        storage_layout.addWidget(disks_button, 0, Qt.AlignRight)
        
        storage_group.setLayout(storage_layout)
        content_layout.addWidget(storage_group)
        
        # System uptime
        uptime_group = QGroupBox("System Uptime")
        uptime_layout = QVBoxLayout()
        
        self.uptime_label = QLabel("Loading...")
        uptime_layout.addWidget(self.uptime_label)
        
        boot_widget = QWidget()
        boot_layout = QHBoxLayout(boot_widget)
        
        boot_layout.addWidget(QLabel("Boot Time:"))
        self.boot_time_label = QLabel("Loading...")
        boot_layout.addWidget(self.boot_time_label, 1)
        
        uptime_layout.addWidget(boot_widget)
        
        uptime_group.setLayout(uptime_layout)
        content_layout.addWidget(uptime_group)
        
        content_layout.addStretch()
        layout.addWidget(scroll, 1)
        
        return tab
        
    def create_computer_tab(self):
        """Create the Computer Name tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Computer description
        desc_group = QGroupBox("Computer Description")
        desc_layout = QVBoxLayout()
        
        desc_label = QLabel("Provide a description of this computer:")
        desc_layout.addWidget(desc_label)
        
        self.desc_text = QTextEdit()
        self.desc_text.setMaximumHeight(60)
        self.desc_text.setPlainText("Primary workstation")
        desc_layout.addWidget(self.desc_text)
        
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # Computer name
        name_group = QGroupBox("Computer Name")
        name_layout = QGridLayout()
        
        name_layout.addWidget(QLabel("Full computer name:"), 0, 0)
        self.full_name_label = QLabel()
        name_layout.addWidget(self.full_name_label, 0, 1)
        
        name_layout.addWidget(QLabel("Workgroup/Domain:"), 1, 0)
        self.workgroup_label = QLabel()
        name_layout.addWidget(self.workgroup_label, 1, 1)
        
        # Network identification button
        network_btn = QPushButton("Network ID...")
        network_btn.clicked.connect(self.show_network_id)
        name_layout.addWidget(network_btn, 2, 0, 1, 2)
        
        name_group.setLayout(name_layout)
        layout.addWidget(name_group)
        
        # Network information
        net_group = QGroupBox("Network Information")
        net_layout = QGridLayout()
        
        net_layout.addWidget(QLabel("Hostname:"), 0, 0)
        self.hostname_label = QLabel()
        net_layout.addWidget(self.hostname_label, 0, 1)
        
        net_layout.addWidget(QLabel("IP Address:"), 1, 0)
        self.ip_label = QLabel()
        net_layout.addWidget(self.ip_label, 1, 1)
        
        net_layout.addWidget(QLabel("MAC Address:"), 2, 0)
        self.mac_label = QLabel()
        net_layout.addWidget(self.mac_label, 2, 1)
        
        # Network interfaces count
        net_layout.addWidget(QLabel("Network Interfaces:"), 3, 0)
        self.net_count_label = QLabel()
        net_layout.addWidget(self.net_count_label, 3, 1)
        
        # Refresh network button
        refresh_net_btn = QPushButton("Refresh Network")
        refresh_net_btn.clicked.connect(self.refresh_network_info)
        net_layout.addWidget(refresh_net_btn, 4, 0, 1, 2)
        
        net_group.setLayout(net_layout)
        layout.addWidget(net_group)
        
        layout.addStretch()
        
        return tab
        
    def create_buttons(self, layout):
        """Create the XP-style buttons"""
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(15, 10, 15, 15)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(QApplication.style().standardIcon(QStyle.SP_BrowserReload))
        refresh_btn.clicked.connect(self.update_all_info)
        refresh_btn.setFixedWidth(100)
        
        # OK button
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.close)
        ok_btn.setDefault(True)
        ok_btn.setFixedWidth(75)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        cancel_btn.setFixedWidth(75)
        
        button_layout.addWidget(refresh_btn)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addWidget(button_widget)
        
    def update_all_info(self):
        """Update all system information"""
        self.update_static_info()
        self.update_dynamic_info()
        
    def update_static_info(self):
        """Update static system information"""
        # System info
        system = platform.system()
        release = platform.release()
        version = platform.version()
        
        if system == "Windows":
            self.system_title.setText(f"Microsoft Windows {release}")
            self.version_label.setText(f"Version {version}")
        elif system == "Linux":
            self.system_title.setText("Linux")
            self.version_label.setText(f"{release} ({version})")
        else:
            self.system_title.setText(f"{system} {release}")
            self.version_label.setText(version)
        
        # Manufacturer and model
        self.get_system_manufacturer()
        
        # CPU info
        self.get_cpu_info()
        
        # Memory info
        self.get_memory_info()
        
        # Network info
        self.get_network_info()
        
    def update_dynamic_info(self):
        """Update dynamic system information"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.cpu_progress.setValue(int(cpu_percent))
        
        # CPU frequency (dynamic)
        try:
            freq = psutil.cpu_freq()
            if freq:
                self.cpu_freq_label.setText(f"{freq.current:.0f} MHz")
        except:
            pass
        
        # Memory usage
        mem = psutil.virtual_memory()
        self.mem_progress.setValue(int(mem.percent))
        self.mem_available_label.setText(self.format_bytes(mem.available))
        self.mem_cached_label.setText(self.format_bytes(mem.cached if hasattr(mem, 'cached') else 0))
        
        # Swap memory
        swap = psutil.swap_memory()
        self.swap_total_label.setText(self.format_bytes(swap.total))
        
        # Disk usage
        self.get_disk_info()
        
        # System uptime
        self.get_uptime()
        
        # Network info updates
        self.update_network_dynamic()
        
    def get_system_manufacturer(self):
        """Get system manufacturer information"""
        system = platform.system()
        
        try:
            if system == "Windows":
                try:
                    import wmi
                    c = wmi.WMI()
                    for computer in c.Win32_ComputerSystem():
                        self.model_label.setText("unknown")
                    for bios in c.Win32_BIOS():
                        # self.bios_label.setText(bios.Caption or "Unknown")
                        pass
                except:
                    self.model_label.setText("Unknown")
                    # self.bios_label.setText("BIOS")
                    
            elif system == "Linux":
                # Try to read from DMI/sysfs
                try:
                    with open('/sys/class/dmi/id/sys_vendor', 'r') as f:
                        pass
                except:
                    pass
                try:
                    with open('/sys/class/dmi/id/product_name', 'r') as f:
                        self.model_label.setText(f.read().strip() or "Unknown")
                except:
                    self.model_label.setText("Unknown")
                    
                try:
                    with open('/sys/class/dmi/id/bios_version', 'r') as f:
                        self.bios_label.setText(f.read().strip() or "BIOS")
                except:
                    self.bios_label.setText("BIOS")
                    
            else:  # macOS
                # self.manufacturer_label.setText("Apple")
                self.model_label.setText("Mac")
                # self.bios_label.setText("EFI")
                
        except Exception as e:
            # self.manufacturer_label.setText("Unknown")
            self.model_label.setText("Unknown")
            # self.bios_label.setText("Unknown")
            
    def get_cpu_info(self):
        """Get CPU information"""
        try:
            # Try to get detailed CPU info
            cpu_data = cpuinfo.get_cpu_info()
            brand = cpu_data.get('brand_raw', 'Unknown CPU')
            self.cpu_label.setText(brand)
            
            # CPU cores
            physical_cores = psutil.cpu_count(logical=False)
            logical_cores = psutil.cpu_count(logical=True)
            self.cpu_cores_label.setText(f"{physical_cores} physical, {logical_cores} logical")
            
            # Initial CPU frequency
            freq = psutil.cpu_freq()
            if freq:
                self.cpu_freq_label.setText(f"{freq.current:.0f} MHz")
            else:
                self.cpu_freq_label.setText("Unknown")
                
        except Exception as e:
            self.cpu_label.setText(platform.processor() or "Unknown CPU")
            self.cpu_cores_label.setText(f"{psutil.cpu_count()} cores")
            
    def get_memory_info(self):
        """Get memory information"""
        try:
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024**3)
            self.memory_label.setText(f"Total Physical Memory: {total_gb:.1f} GB")
        except:
            self.memory_label.setText("Memory: Unknown")
            
    def get_disk_info(self):
        """Get disk information"""
        try:
            # Get primary disk (usually C:\ on Windows, / on Linux)
            partitions = psutil.disk_partitions()
            primary_partition = None
            
            for partition in partitions:
                if platform.system() == "Windows":
                    if partition.mountpoint == "C:\\":
                        primary_partition = partition
                        break
                else:
                    if partition.mountpoint == "/":
                        primary_partition = partition
                        break
            
            if not primary_partition and partitions:
                primary_partition = partitions[0]
            
            if primary_partition:
                usage = psutil.disk_usage(primary_partition.mountpoint)
                
                total_gb = usage.total / (1024**3)
                free_gb = usage.free / (1024**3)
                
                self.disk_label.setText(f"{primary_partition.device} ({primary_partition.mountpoint}) - {total_gb:.1f} GB")
                self.disk_progress.setValue(int(usage.percent))
                self.disk_free_label.setText(f"{free_gb:.1f} GB")
                self.fs_label.setText(primary_partition.fstype)
                
        except Exception as e:
            self.disk_label.setText("Disk: Unknown")
            self.disk_progress.setValue(0)
            self.disk_free_label.setText("Unknown")
            self.fs_label.setText("Unknown")
            
    def get_uptime(self):
        """Get system uptime"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_str = str(timedelta(seconds=int(uptime_seconds)))
            
            self.uptime_label.setText(f"System has been running for {uptime_str}")
            
            boot_time_str = datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")
            self.boot_time_label.setText(boot_time_str)
            
        except:
            self.uptime_label.setText("Uptime: Unknown")
            self.boot_time_label.setText("Unknown")
            
    def get_network_info(self):
        """Get network information"""
        try:
            # Hostname
            hostname = socket.gethostname()
            self.hostname_label.setText(hostname)
            self.full_name_label.setText(hostname)
            
            # Workgroup/Domain
            if platform.system() == "Windows":
                try:
                    import wmi
                    c = wmi.WMI()
                    for computer in c.Win32_ComputerSystem():
                        domain = computer.Domain or "WORKGROUP"
                        self.workgroup_label.setText(domain)
                except:
                    self.workgroup_label.setText("WORKGROUP")
            else:
                self.workgroup_label.setText("WORKGROUP")
                
            # IP and MAC address
            self.update_network_dynamic()
            
            # Network interface count
            net_if_addrs = psutil.net_if_addrs()
            self.net_count_label.setText(str(len(net_if_addrs)))
            
        except:
            self.hostname_label.setText("Unknown")
            self.full_name_label.setText("Unknown")
            self.workgroup_label.setText("Unknown")
            self.net_count_label.setText("0")
            
    def update_network_dynamic(self):
        """Update dynamic network information"""
        try:
            # Get primary IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            self.ip_label.setText(ip_address)
            
            # Get MAC address of primary interface
            net_if_addrs = psutil.net_if_addrs()
            mac_address = "Unknown"
            
            for interface, addrs in net_if_addrs.items():
                for addr in addrs:
                    if addr.family == psutil.AF_LINK and addr.address:
                        mac_address = addr.address
                        break
                if mac_address != "Unknown":
                    break
            
            self.mac_label.setText(mac_address)
            
        except Exception as e:
            self.ip_label.setText("Unknown")
            self.mac_label.setText("Unknown")
            
    def show_all_disks(self):
        """Show all disks in a dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("All Disks")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        try:
            partitions = psutil.disk_partitions()
            disk_info = "Disk Partitions:\n\n"
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info += f"Device: {partition.device}\n"
                    disk_info += f"Mountpoint: {partition.mountpoint}\n"
                    disk_info += f"File System: {partition.fstype}\n"
                    disk_info += f"Total: {self.format_bytes(usage.total)}\n"
                    disk_info += f"Used: {self.format_bytes(usage.used)} ({usage.percent}%)\n"
                    disk_info += f"Free: {self.format_bytes(usage.free)}\n"
                    disk_info += "-" * 40 + "\n"
                except:
                    continue
                    
            text_edit.setText(disk_info)
        except:
            text_edit.setText("Unable to retrieve disk information")
        
        layout.addWidget(text_edit)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn, 0, Qt.AlignRight)
        
        dialog.exec()
        
    def show_network_id(self):
        """Show network identification information"""
        QMessageBox.information(self, "Network ID", 
                              "This feature would normally launch the Network Identification Wizard.\n\n"
                              f"Computer: {socket.gethostname()}\n"
                              f"Workgroup: {self.workgroup_label.text()}")
        
    def refresh_network_info(self):
        """Refresh network information"""
        self.get_network_info()
        QMessageBox.information(self, "Network Info", "Network information refreshed!")
        
    def format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"

def main():
    app = QApplication(sys.argv)
    
    # Set XP-like font
    font = QFont("Tahoma", 9)
    app.setFont(font)
    
    # Create and show window
    window = OpenAbout()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    # Check dependencies
    try:
        import psutil
    except ImportError:
        print("Please install psutil: pip install psutil")
        sys.exit(1)
    
    try:
        import cpuinfo
    except ImportError:
        print("Note: For detailed CPU info, install py-cpuinfo: pip install py-cpuinfo")
    
    main()