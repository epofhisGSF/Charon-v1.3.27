#!/usr/bin/env python3
"""
Drifter Wormhole Tracker for EVE Online
A desktop application for tracking Jove Observatory drifter wormholes
"""

import sys
import json
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QTextEdit, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QDialog, QDialogButtonBox, QGroupBox, QLineEdit, QFrame,
    QScrollArea, QGridLayout, QTabWidget, QMenu, QCompleter, QSizePolicy
)
from PyQt6.QtCore import Qt, QSettings, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QPalette

from jove_systems import JOVE_SYSTEMS


class DrifterTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('DrifterTracker', 'EVEWormholeScanner')
        self.scans = self.load_scans()
        self.default_role_id = self.settings.value('default_role_id', '')
        
        # Auto-cleanup setting (default: False for safety)
        auto_cleanup = self.settings.value('auto_cleanup_on_start', False, type=bool)
        
        # Clean up expired wormholes only if enabled
        if auto_cleanup:
            self.cleanup_expired_wormholes()
        
        # Load EVE SDE data for advanced routing
        self.sde_loader = None
        self.load_sde_data()
        
        self.init_ui()
    
    def load_sde_data(self):
        """Load EVE SDE data for advanced routing features"""
        try:
            from eve_sde_loader import EVESDELoader
            self.sde_loader = EVESDELoader()
            
            if self.sde_loader.load_processed_data():
                print(f"✓ Loaded SDE data: {len(self.sde_loader.systems):,} systems")
            else:
                print("⚠ SDE data not found. Running automatic setup...")
                # Auto-run SDE setup with visual feedback
                self.run_sde_setup_with_dialog()
        except ImportError:
            print("⚠ eve_sde_loader.py not found.")
            print("   Advanced routing disabled. Basic routing still available.")
            self.sde_loader = None
        except Exception as e:
            print(f"⚠ Failed to load SDE data: {e}")
            self.sde_loader = None
    
    def run_sde_setup_with_dialog(self):
        """Download SDE data with visual progress dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
        from PyQt6.QtCore import Qt, QTimer
        from PyQt6.QtGui import QFont
        
        # Create progress dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("CHARON - First Time Setup")
        dialog.setModal(True)
        dialog.setFixedSize(500, 250)
        dialog.setStyleSheet("""
            QDialog {
                background: #0a0a0f;
                border: 2px solid #2a2a35;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("⦰ FIRST TIME SETUP")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #e8e8e8;
            letter-spacing: 3px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Status message
        status = QLabel("Downloading EVE Online universe data...\nThis will take about 1 minute.")
        status.setStyleSheet("""
            font-size: 12px;
            color: #b8b8b8;
            padding: 10px;
        """)
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setWordWrap(True)
        layout.addWidget(status)
        
        # Progress bar (indeterminate)
        progress = QProgressBar()
        progress.setRange(0, 0)  # Indeterminate progress
        progress.setStyleSheet("""
            QProgressBar {
                background: #16161d;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                text-align: center;
                height: 25px;
                color: #e8e8e8;
            }
            QProgressBar::chunk {
                background: #4a4a55;
            }
        """)
        layout.addWidget(progress)
        
        # Detail label
        detail = QLabel("Initializing download...")
        detail.setStyleSheet("""
            font-size: 10px;
            color: #8a8a8a;
            padding: 5px;
        """)
        detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(detail)
        
        # Show dialog
        dialog.show()
        
        # Process events to show dialog
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
        
        # Run setup in background
        def update_status(msg):
            detail.setText(msg)
            QApplication.processEvents()
        
        try:
            update_status("Downloading system data...")
            
            import setup_sde
            
            # Monkey-patch print to update UI
            original_print = print
            def print_to_ui(*args, **kwargs):
                msg = ' '.join(str(arg) for arg in args)
                if 'Downloading' in msg or 'Processing' in msg or '✓' in msg:
                    update_status(msg.replace('✓', '').strip())
                original_print(*args, **kwargs)
            
            # Temporarily replace print
            import builtins
            builtins.print = print_to_ui
            
            # Run the setup in silent mode
            setup_sde.main(silent=True)
            
            # Restore original print
            builtins.print = original_print
            
            update_status("Loading processed data...")
            QApplication.processEvents()
            
            # Try loading again
            from eve_sde_loader import EVESDELoader
            self.sde_loader = EVESDELoader()
            
            if self.sde_loader.load_processed_data():
                update_status(f"✓ Loaded {len(self.sde_loader.systems):,} systems successfully!")
                QApplication.processEvents()
                
                # Close dialog after brief delay
                QTimer.singleShot(1500, dialog.close)
            else:
                dialog.close()
                self.show_error_dialog(
                    "Setup Complete - Restart Required",
                    "SDE data was downloaded but needs a restart to load.\n\n"
                    "Please close and reopen CHARON."
                )
                self.sde_loader = None
                
        except Exception as e:
            builtins.print = original_print
            dialog.close()
            self.show_error_dialog(
                "Setup Failed",
                f"Failed to download SDE data:\n{str(e)}\n\n"
                f"Advanced routing will be disabled.\n"
                f"Basic wormhole tracking still available."
            )
            self.sde_loader = None
    
    def show_error_dialog(self, title, message):
        """Show error dialog"""
        from PyQt6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStyleSheet("""
            QMessageBox {
                background: #0a0a0f;
            }
            QLabel {
                color: #e8e8e8;
                font-size: 12px;
            }
            QPushButton {
                background: #16161d;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 8px 20px;
                color: #e8e8e8;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #1e1e28;
                border: 1px solid #4a4a55;
            }
        """)
        msg.exec()
    
    def run_sde_setup(self):
        """Automatically download and setup SDE data (legacy console version)"""
        try:
            print("\n" + "="*60)
            print("CHARON - First Time Setup")
            print("="*60)
            print("Downloading EVE Online universe data...")
            print("This may take a minute...\n")
            
            import setup_sde
            
            # Run the setup in silent mode (no prompts)
            setup_sde.main(silent=True)
            
            print("\n✓ Setup complete! Loading data...")
            
            # Try loading again
            from eve_sde_loader import EVESDELoader
            self.sde_loader = EVESDELoader()
            
            if self.sde_loader.load_processed_data():
                print(f"✓ Successfully loaded {len(self.sde_loader.systems):,} systems")
                print("="*60 + "\n")
            else:
                print("⚠ Setup completed but data failed to load.")
                print("   You may need to restart CHARON.")
                self.sde_loader = None
                
        except Exception as e:
            print(f"\n⚠ Auto-setup failed: {e}")
            print("   Advanced routing will be disabled.")
            print("   Basic wormhole tracking still available.\n")
            self.sde_loader = None

    def init_ui(self):
        self.setWindowTitle('CHARON - Wormhole Intelligence System')
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 600)
        
        # Set dark theme
        self.set_dark_theme()
        
        # Create central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #0a0a0f;
            }
            QTabBar::tab {
                background: #0e0e14;
                color: #8a8a8a;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: #0a0a0f;
                color: #e8e8e8;
            }
            QTabBar::tab:hover {
                background: #16161d;
                color: #e8e8e8;
            }
        """)
        
        # Create Scanner Tab (existing functionality)
        scanner_tab = QWidget()
        scanner_layout = QVBoxLayout(scanner_tab)
        scanner_layout.setSpacing(20)
        scanner_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = self.create_header()
        scanner_layout.addWidget(header)
        
        # Stats
        self.stats_widget = self.create_stats()
        scanner_layout.addWidget(self.stats_widget)
        
        # Input section
        input_section = self.create_input_section()
        scanner_layout.addWidget(input_section)
        
        # Scans list
        self.scans_list = QListWidget()
        self.scans_list.setStyleSheet("""
            QListWidget {
                background: #0e0e14;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 10px;
                font-size: 14px;
            }
            QListWidget::item {
                background: #16161d;
                border: 1px solid #2a2a35;
                border-left: 4px solid #e8e8e8;
                border-radius: 2px;
                padding: 15px;
                margin: 5px;
            }
            QListWidget::item:hover {
                border-color: #e8e8e8;
            }
        """)
        scanner_layout.addWidget(self.scans_list, 1)
        
        # Create Routing Tab
        routing_tab = self.create_routing_tab()
        
        # Create Mass Calculator Tab
        mass_tab = self.create_mass_tab()
        
        # Add tabs
        self.tab_widget.addTab(scanner_tab, "SCANNER")
        self.tab_widget.addTab(routing_tab, "ROUTING")
        self.tab_widget.addTab(mass_tab, "MASS")
        
        main_layout.addWidget(self.tab_widget)
        
        # Footer with Charon branding
        footer = QLabel('STAND BY FOR CONTINUITY')
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("""
            font-size: 8px;
            color: #3a3a45;
            letter-spacing: 3px;
            padding: 10px;
            background: #0a0a0f;
            border-top: 1px solid #1a1a20;
        """)
        main_layout.addWidget(footer)
        
        self.update_scans_list()
        
        # Populate regions after all UI elements are created
        self.populate_regions()

    def set_dark_theme(self):
        """Charon - Professional militaristic space theme"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0f, stop:1 #14141c);
                color: #e8e8e8;
            }
            QLabel {
                color: #e8e8e8;
                background: transparent;
            }
            QComboBox {
                background: #16161d;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 8px 12px;
                color: #e8e8e8;
                font-size: 12px;
                min-height: 28px;
            }
            QComboBox:hover {
                border: 1px solid #4a4a55;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #e8e8e8;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background: #16161d;
                border: 1px solid #2a2a35;
                selection-background-color: #2a2a35;
                color: #e8e8e8;
            }
            QTextEdit, QLineEdit {
                background: #16161d;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 8px 12px;
                color: #e8e8e8;
                font-size: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QTextEdit:focus, QLineEdit:focus {
                border: 1px solid #4a4a55;
            }
            QPushButton {
                background: #16161d;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 10px 20px;
                color: #e8e8e8;
                font-size: 12px;
                font-weight: bold;
                min-height: 32px;
            }
            QPushButton:hover {
                background: #1e1e28;
                border: 1px solid #4a4a55;
            }
            QPushButton:pressed {
                background: #0e0e14;
            }
            QPushButton#secondaryBtn {
                background: #0e0e14;
                border: 1px solid #2a2a35;
            }
            QPushButton#secondaryBtn:hover {
                background: #16161d;
                border: 1px solid #4a4a55;
            }
            QListWidget {
                background: #0e0e14;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 5px;
                color: #e8e8e8;
            }
            QListWidget::item {
                background: transparent;
                border: none;
                padding: 8px;
            }
            QListWidget::item:hover {
                background: #16161d;
            }
            QGroupBox {
                background: #0e0e14;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                margin-top: 12px;
                padding: 15px 10px 10px 10px;
                font-weight: bold;
                font-size: 11px;
                color: #b8b8b8;
                letter-spacing: 1px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
                background: #0e0e14;
                color: #b8b8b8;
            }
            QTabWidget::pane {
                border: 1px solid #2a2a35;
                background: #0a0a0f;
                border-radius: 2px;
            }
            QTabBar::tab {
                background: #16161d;
                border: 1px solid #2a2a35;
                padding: 10px 20px;
                color: #6a6a6a;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
                border-bottom: none;
                border-top-left-radius: 2px;
                border-top-right-radius: 2px;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background: #0a0a0f;
                color: #e8e8e8;
                border-bottom: 2px solid #e8e8e8;
            }
            QTabBar::tab:hover:!selected {
                background: #1e1e28;
                color: #b8b8b8;
            }
            QScrollBar:vertical {
                background: #0e0e14;
                width: 10px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #2a2a35;
                min-height: 20px;
                border-radius: 0px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3a3a45;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background: #0e0e14;
                height: 10px;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background: #2a2a35;
                min-width: 20px;
                border-radius: 0px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #3a3a45;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)

    def create_header(self):
        """Create Charon header with logo"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(0)
        
        # Charon logo (circle with vertical line)
        logo = QLabel('⦰')
        logo.setStyleSheet("""
            font-size: 42px;
            color: #e8e8e8;
            font-weight: 100;
        """)
        logo.setFixedWidth(60)
        
        # Charon text
        title = QLabel('CHARON')
        title.setStyleSheet("""
            font-family: sans-serif;
            font-size: 26px;
            font-weight: 300;
            color: #e8e8e8;
            letter-spacing: 8px;
            padding-left: 10px;
        """)
        
        header_layout.addWidget(logo)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Subtitle
        subtitle = QLabel('WORMHOLE INTELLIGENCE SYSTEM')
        subtitle.setStyleSheet("""
            font-size: 9px;
            color: #6a6a6a;
            letter-spacing: 3px;
            padding-right: 10px;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(subtitle)
        
        return header_widget

    def create_stats(self):
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setSpacing(15)
        
        self.stat_total = self.create_stat_card('Systems Scanned', '0')
        self.stat_holes = self.create_stat_card('Holes Found', '0')
        self.stat_regions = self.create_stat_card('Regions', '0')
        
        stats_layout.addWidget(self.stat_total)
        stats_layout.addWidget(self.stat_holes)
        stats_layout.addWidget(self.stat_regions)
        
        return stats_widget

    def create_stat_card(self, label, value):
        card = QGroupBox()
        card.setStyleSheet("""
            QGroupBox {
                background: #0e0e14;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(card)
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("""
            font-size: 32px;
            font-weight: 300;
            color: #e8e8e8;
        """)
        
        text_label = QLabel(label)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("""
            font-size: 10px;
            color: #6a6a6a;
            text-transform: uppercase;
            letter-spacing: 2px;
        """)
        
        layout.addWidget(value_label)
        layout.addWidget(text_label)
        
        return card

    def create_input_section(self):
        group = QGroupBox('Scan Input')
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        # Region selector
        region_layout = QVBoxLayout()
        region_label = QLabel('Region')
        region_label.setStyleSheet('font-weight: bold; color: #e8e8e8;')
        self.region_combo = QComboBox()
        self.region_combo.addItem('Select Region')
        self.region_combo.currentIndexChanged.connect(self.on_region_changed)
        region_layout.addWidget(region_label)
        region_layout.addWidget(self.region_combo)
        layout.addLayout(region_layout)
        
        # Note: populate_regions() will be called after full UI initialization
        
        # System buttons (hidden initially)
        self.system_buttons_widget = QWidget()
        system_buttons_layout = QVBoxLayout(self.system_buttons_widget)
        system_buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        system_label = QLabel('System')
        system_label.setStyleSheet('font-weight: bold; color: #e8e8e8;')
        system_buttons_layout.addWidget(system_label)
        
        # Scrollable container for system buttons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(150)
        scroll_area.setMaximumHeight(300)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: #0e0e14;
                border: 1px solid #2a2a35;
                border-radius: 2px;
            }
            QScrollBar:vertical {
                background: #16161d;
                width: 12px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: #e8e8e8;
                border-radius: 2px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #b8b8b8;
            }
        """)
        
        # Container widget for buttons
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.system_grid_layout = QGridLayout(scroll_content)
        self.system_grid_layout.setSpacing(5)
        self.system_grid_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll_area.setWidget(scroll_content)
        system_buttons_layout.addWidget(scroll_area)
        self.system_buttons_widget.setVisible(False)
        layout.addWidget(self.system_buttons_widget)
        
        # Selected system indicator
        self.selected_system_label = QLabel('')
        self.selected_system_label.setStyleSheet("""
            font-weight: bold; 
            color: #e8e8e8; 
            background: #16161d;
            padding: 8px;
            border-radius: 2px;
            border-left: 4px solid #b8b8b8;
            font-size: 14px;
        """)
        self.selected_system_label.setVisible(False)
        layout.addWidget(self.selected_system_label)
        
        # Wormhole type buttons (hidden initially)
        self.type_buttons_widget = QWidget()
        type_buttons_layout = QVBoxLayout(self.type_buttons_widget)
        type_buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        type_label = QLabel('Wormhole Type')
        type_label.setStyleSheet('font-weight: bold; color: #e8e8e8;')
        type_buttons_layout.addWidget(type_label)
        
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(10)
        
        self.type_buttons = {}
        hole_types = ['Vidette', 'Redoubt', 'Sentinel', 'Barbican', 'Conflux']
        
        for hole_type in hole_types:
            btn = QPushButton(hole_type)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background: #16161d;
                    border: 2px solid #2a2a35;
                    border-radius: 2px;
                    padding: 10px 20px;
                    color: #e8e8e8;
                    font-weight: bold;
                    min-width: 100px;
                }
                QPushButton:hover {
                    border-color: #e8e8e8;
                    background: #0e0e14;
                }
                QPushButton:checked {
                    background: #e8e8e8;
                    border-color: #e8e8e8;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, t=hole_type: self.on_type_button_clicked(t))
            self.type_buttons[hole_type] = btn
            buttons_row.addWidget(btn)
        
        type_buttons_layout.addLayout(buttons_row)
        self.type_buttons_widget.setVisible(False)
        layout.addWidget(self.type_buttons_widget)
        
        # Paste area (hidden initially)
        self.paste_widget = QWidget()
        paste_layout = QVBoxLayout(self.paste_widget)
        
        paste_label = QLabel('Paste Wormhole Info from EVE (Right-click > Show Info)')
        paste_label.setStyleSheet('font-weight: bold; color: #e8e8e8; margin-top: 10px;')
        self.wh_text = QTextEdit()
        self.wh_text.setPlaceholderText('Paste the full wormhole information text here...\n\nExample:\nUnidentified Wormhole\nThis wormhole seems to lead into unknown parts of space.\nType: Sentinel\nThis wormhole has not yet had its stability significantly disrupted...')
        self.wh_text.setMaximumHeight(150)
        
        role_label = QLabel('Discord Role ID (optional)')
        role_label.setStyleSheet('font-weight: bold; color: #e8e8e8;')
        self.role_input = QLineEdit()
        self.role_input.setPlaceholderText('1326789530983858256')
        self.role_input.setText(self.default_role_id)
        
        paste_layout.addWidget(paste_label)
        paste_layout.addWidget(self.wh_text)
        paste_layout.addWidget(role_label)
        paste_layout.addWidget(self.role_input)
        
        self.paste_widget.setVisible(False)
        layout.addWidget(self.paste_widget)
        
        # Selected type indicator
        self.selected_type_label = QLabel('')
        self.selected_type_label.setStyleSheet("""
            font-weight: bold; 
            color: #e8e8e8; 
            background: #16161d;
            padding: 8px;
            border-radius: 2px;
            border-left: 4px solid #e8e8e8;
        """)
        self.selected_type_label.setVisible(False)
        layout.addWidget(self.selected_type_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.back_btn = QPushButton('← Back')
        self.back_btn.setObjectName('secondaryBtn')
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setVisible(False)
        
        self.no_hole_btn = QPushButton('No Hole Found')
        self.no_hole_btn.setObjectName('secondaryBtn')
        self.no_hole_btn.clicked.connect(self.add_no_hole_scan)
        self.no_hole_btn.setVisible(False)
        
        self.parse_btn = QPushButton('Parse & Add Scan')
        self.parse_btn.clicked.connect(self.add_scan_from_paste)
        self.parse_btn.setVisible(False)
        
        bulk_import_btn = QPushButton('📋 Bulk Import')
        bulk_import_btn.setObjectName('secondaryBtn')
        bulk_import_btn.clicked.connect(self.show_bulk_import)
        bulk_import_btn.setToolTip('Import multiple scans from text (Discord format)')
        
        cleanup_btn = QPushButton('🕐 Clean Expired')
        cleanup_btn.setObjectName('secondaryBtn')
        cleanup_btn.clicked.connect(self.manual_cleanup_expired)
        cleanup_btn.setToolTip('Remove wormholes that have exceeded their lifetime')
        
        clear_btn = QPushButton('Clear All Data')
        clear_btn.setObjectName('secondaryBtn')
        clear_btn.clicked.connect(self.clear_all_data)
        
        export_btn = QPushButton('Export to Discord')
        export_btn.clicked.connect(self.show_discord_export)
        
        buttons_layout.addWidget(self.back_btn)
        buttons_layout.addWidget(bulk_import_btn)
        buttons_layout.addWidget(cleanup_btn)
        buttons_layout.addWidget(clear_btn)
        buttons_layout.addWidget(export_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.no_hole_btn)
        buttons_layout.addWidget(self.parse_btn)
        
        layout.addLayout(buttons_layout)
        
        # Store current state
        self.current_region = None
        self.current_system = None
        self.current_hole_type = None
        
        return group

    def cleanup_expired_wormholes(self):
        """Remove wormholes that have exceeded their expected lifetime"""
        from datetime import datetime, timedelta
        
        # Wormhole lifetime based on life status (in hours)
        LIFETIME_HOURS = {
            'Fresh': 24,           # Fresh: 24 hours
            'Destabilizing': 4,    # Destabilizing: 4 hours remaining
            'Critical': 0.25       # Critical: 15 minutes (0.25 hours)
        }
        
        now = datetime.now()
        original_count = len(self.scans)
        expired_wormholes = []
        
        # Filter out expired wormholes
        new_scans = []
        for scan in self.scans:
            # Skip "No Hole" entries - they don't expire
            if scan['holeType'] == 'None':
                new_scans.append(scan)
                continue
            
            try:
                scanned_time = datetime.fromisoformat(scan['scannedAt'])
                life_status = scan['lifeStatus']
                
                # Get expected lifetime for this wormhole
                lifetime_hours = LIFETIME_HOURS.get(life_status, 24)  # Default to 24 hours
                
                # Calculate age of the scan
                age = now - scanned_time
                max_age = timedelta(hours=lifetime_hours)
                
                # If wormhole is still within its lifetime, keep it
                if age <= max_age:
                    new_scans.append(scan)
                else:
                    # Wormhole has expired
                    expired_wormholes.append({
                        'system': scan['system'],
                        'region': scan['region'],
                        'type': scan['holeType'],
                        'age_hours': age.total_seconds() / 3600
                    })
            except (ValueError, KeyError):
                # If there's any error parsing, keep the scan to be safe
                new_scans.append(scan)
        
        # Update scans if any were removed
        if len(new_scans) < original_count:
            self.scans = new_scans
            self.save_scans()
            
            # Log cleanup for debugging (optional)
            removed_count = original_count - len(new_scans)
            print(f"Cleaned up {removed_count} expired wormhole(s)")
            for wh in expired_wormholes[:5]:  # Show first 5
                print(f"  - {wh['system']} ({wh['region']}) - {wh['type']} - {wh['age_hours']:.1f}h old")

    def manual_cleanup_expired(self):
        """Manually trigger cleanup of expired wormholes with user feedback"""
        from datetime import datetime, timedelta
        
        # Count how many will be removed
        LIFETIME_HOURS = {
            'Fresh': 24,
            'Destabilizing': 4,
            'Critical': 0.25
        }
        
        now = datetime.now()
        expired_count = 0
        expired_list = []
        
        for scan in self.scans:
            if scan['holeType'] == 'None':
                continue
            
            try:
                scanned_time = datetime.fromisoformat(scan['scannedAt'])
                life_status = scan['lifeStatus']
                lifetime_hours = LIFETIME_HOURS.get(life_status, 24)
                age = now - scanned_time
                max_age = timedelta(hours=lifetime_hours)
                
                if age > max_age:
                    expired_count += 1
                    age_hours = age.total_seconds() / 3600
                    expired_list.append(f"{scan['system']} ({scan['region']}) - {scan['holeType']} - {age_hours:.1f}h old")
            except:
                continue
        
        if expired_count == 0:
            QMessageBox.information(self, 'No Expired Wormholes', 'All wormholes are still within their expected lifetime.')
            return
        
        # Ask for confirmation
        message = f"Found {expired_count} expired wormhole(s):\n\n"
        message += "\n".join(expired_list[:10])
        if len(expired_list) > 10:
            message += f"\n... and {len(expired_list) - 10} more"
        message += "\n\nRemove expired wormholes?"
        
        reply = QMessageBox.question(
            self, 'Clean Expired Wormholes',
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.cleanup_expired_wormholes()
            self.update_scans_list()
            self.populate_regions()
            
            # Refresh current region view
            current_index = self.region_combo.currentIndex()
            if current_index > 0:
                self.on_region_changed(current_index)
            
            QMessageBox.information(self, 'Cleanup Complete', f'Removed {expired_count} expired wormhole(s).')

    def populate_regions(self):
        """Populate region dropdown with status indicators"""
        # Store current selection
        current_region = self.region_combo.currentData()
        
        # Clear and rebuild
        self.region_combo.clear()
        self.region_combo.addItem('Select Region')
        
        for region in sorted(JOVE_SYSTEMS.keys()):
            total_systems = len(JOVE_SYSTEMS[region])
            
            # Count systems with scans in this region
            systems_scanned = set()
            has_wormholes = False
            
            for scan in self.scans:
                if scan['region'] == region:
                    systems_scanned.add(scan['system'])
                    if scan['holeType'] != 'None':
                        has_wormholes = True
            
            # Build display text with status
            scanned_count = len(systems_scanned)
            status = ""
            if scanned_count > 0:
                status = f" [{scanned_count}/{total_systems}]"
                if has_wormholes:
                    status = f" ● {status}"
            
            display_text = f"{region}{status}"
            self.region_combo.addItem(display_text, region)
        
        # Restore selection if possible
        if current_region:
            for i in range(self.region_combo.count()):
                if self.region_combo.itemData(i) == current_region:
                    self.region_combo.setCurrentIndex(i)
                    break

    def show_bulk_import(self):
        """Show bulk import dialog"""
        dialog = BulkImportDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            import_text = dialog.get_import_text()
            if import_text:
                self.process_bulk_import(import_text)

    def process_bulk_import(self, import_text):
        """Process bulk import text and add scans"""
        import re
        from datetime import datetime, timedelta
        
        lines = import_text.strip().split('\n')
        
        # Also split by => if multiple entries are on same line
        expanded_lines = []
        for line in lines:
            # If a line has multiple => arrows, it likely has multiple entries
            if line.count('=>') > 1:
                # Split by system pattern: SYSTEM (optional region) =>
                # Look for pattern: word-boundary, system name, optional space/paren/region, =>
                parts = re.split(r'(?=\b[A-Z0-9]+-[A-Z0-9]+\s*(?:\([^)]+\))?\s*=>)', line, flags=re.IGNORECASE)
                for part in parts:
                    part = part.strip()
                    if part and '=>' in part:
                        expanded_lines.append(part)
            else:
                expanded_lines.append(line)
        
        lines = expanded_lines
        
        added_count = 0
        error_count = 0
        errors = []
        
        # Try to extract the scan completion time from header
        # Format: "Scan was completed 2 days ago" or specific timestamp
        scan_timestamp = None
        for line in lines[:5]:  # Check first 5 lines for timestamp
            if 'Scan was completed' in line:
                # Try to parse relative time
                if 'days ago' in line:
                    days_match = re.search(r'(\d+)\s+days?\s+ago', line)
                    if days_match:
                        days_ago = int(days_match.group(1))
                        scan_timestamp = datetime.now() - timedelta(days=days_ago)
                elif 'hours ago' in line:
                    hours_match = re.search(r'(\d+)\s+hours?\s+ago', line)
                    if hours_match:
                        hours_ago = int(hours_match.group(1))
                        scan_timestamp = datetime.now() - timedelta(hours=hours_ago)
                elif 'minutes ago' in line:
                    minutes_match = re.search(r'(\d+)\s+minutes?\s+ago', line)
                    if minutes_match:
                        minutes_ago = int(minutes_match.group(1))
                        scan_timestamp = datetime.now() - timedelta(minutes=minutes_ago)
                break
        
        # If no timestamp found, use current time
        if not scan_timestamp:
            scan_timestamp = datetime.now()
        
        # Track current region from section headers
        current_region = None
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line or line.startswith('#'):
                continue
            
            # Check for region header: "Region (Scanned: X/Y)" or just "Region"
            # This sets the context for systems without explicit region
            for potential_region in JOVE_SYSTEMS.keys():
                if potential_region in line and ('Scanned:' in line or 'Complete' in line or 'Incomplete' in line):
                    current_region = potential_region
                    break
            
            # Skip obvious header/info lines
            if any(skip in line for skip in ['Scan was completed', 'Systems Scanned:', 'Complete Scan', 'Incomplete Scan']):
                continue
            
            # Look for lines with arrow (wormhole data)
            if '=>' not in line:
                continue
            
            # Simple extraction: split by arrow
            parts = line.split('=>', 1)
            if len(parts) != 2:
                continue
            
            left = parts[0].strip()
            right = parts[1].strip()
            
            # Clean up any formatting characters
            left = re.sub(r'[*_`~]', '', left)  # Remove markdown
            right = re.sub(r'[*_`~]', '', right)  # Remove markdown
            
            # Extract SYSTEM from left side
            # System format: "SYSTEM" or "SYSTEM (Region)"
            system = None
            region = None
            
            # Try to find system code - nullsec format: any alphanumeric with dash
            # Examples: L-1SW8, 2PQU-5, EKPB-3, 92K-H2, 6F-H3W
            system_match = re.search(r'\b([A-Z0-9]+-[A-Z0-9]+)\b', left, re.IGNORECASE)
            if system_match:
                system = system_match.group(1).upper()
            
            # Try to find region in parentheses
            region_match = re.search(r'\(([^)]+)\)', left)
            if region_match:
                potential = region_match.group(1).strip()
                if potential in JOVE_SYSTEMS:
                    region = potential
            
            # If no region found in line, use current_region from header
            if not region:
                region = current_region
            
            # If still no region, search all regions for this system
            if not region and system:
                for reg, systems in JOVE_SYSTEMS.items():
                    if system in systems:
                        region = reg
                        break
            
            # Skip if we couldn't determine system or region
            if not system or not region:
                continue
            
            # Validate
            if region not in JOVE_SYSTEMS or system not in JOVE_SYSTEMS[region]:
                errors.append(f"Invalid: {system} in {region}")
                error_count += 1
                continue
            
            # Extract HOLE TYPE from right side
            # Look for: Barbican, Conflux, Vidette, Redoubt, Sentinel, or in parentheses
            hole_type = None
            
            # Check common types
            for wh_type in ['Barbican', 'Conflux', 'Vidette', 'Redoubt', 'Sentinel']:
                if wh_type.lower() in right.lower():
                    hole_type = wh_type
                    break
            
            # If not found, look in parentheses
            if not hole_type:
                paren_match = re.search(r'\(([^)]+)\)', right)
                if paren_match:
                    hole_type = paren_match.group(1).strip()
            
            # If still not found, take first word
            if not hole_type:
                first_word = right.split(',')[0].split()[0].strip('@').strip()
                if first_word:
                    hole_type = first_word
            
            if not hole_type:
                continue
            
            # Normalize hole type
            hole_type = hole_type.strip().title()
            
            # Extract LIFE status
            life_status = 'Fresh'
            # Look for "Life:" keyword - simpler, more robust regex
            life_match = re.search(r'Life(?:time)?[:\s]+([^,]+?)(?:,|\s+Mass:)', right, re.IGNORECASE)
            if life_match:
                life_text = life_match.group(1).strip().replace('@', '').strip()
                
                # Check for Critical indicators
                if any(keyword in life_text for keyword in ['EOL', 'Critical', 'Less than', '< 1 hour', 'hour remaining']):
                    life_status = 'Critical'
                # Check for Destabilizing indicators
                elif any(keyword in life_text for keyword in ['Destab', 'Reduced', 'Beginning']):
                    life_status = 'Destabilizing'
                else:
                    life_status = 'Fresh'
            
            # Extract MASS status
            mass_status = '100% > 50%'
            # Look for Mass or "Mass Stability:" followed by percentage/description
            mass_match = re.search(r'Mass(?:\s+Stability)?[:\s]+([@A-Za-z0-9%>\s<]+?)(?:\s+(?:remaining|Lifetime|Life|$))', right, re.IGNORECASE)
            if mass_match:
                mass_text = mass_match.group(1).strip().replace('@', '').strip()
                
                # Normalize common variations
                if any(keyword in mass_text for keyword in ['< 10%', 'less than 10', 'Verge of Collapse', 'Critically']):
                    mass_status = '< 10%'
                elif any(keyword in mass_text for keyword in ['50%', 'More than 50', 'Stable']):
                    mass_status = '100% > 50%'
                elif any(keyword in mass_text for keyword in ['Reduced', 'Destab', '10%']):
                    mass_status = '50% > 10%'
                else:
                    # Try to keep original if it matches expected format
                    if any(char in mass_text for char in ['%', '>']):
                        mass_status = mass_text
                    # Otherwise keep default
            
            # Extract role ID if present
            role_match = re.search(r'<@&(\d+)>', line)
            role_id = role_match.group(1) if role_match else ''
            
            # Calculate actual wormhole spawn time based on life status
            # The scan_timestamp is when the scan was performed, and we calculate
            # backwards from that based on the wormhole's life status
            spawn_time = self.calculate_spawn_time(life_status, scan_timestamp)
            
            # Success! Add the scan
            scan = {
                'id': int(datetime.now().timestamp() * 1000000) + added_count,
                'region': region,
                'system': system,
                'holeType': hole_type,
                'lifeStatus': life_status,
                'massStatus': mass_status,
                'roleId': role_id,
                'rawInfo': f'Bulk imported: {line}',
                'scannedAt': spawn_time.isoformat()  # Use calculated spawn time
            }
            
            self.scans.insert(0, scan)
            added_count += 1
        
        # Save and update
        self.save_scans()
        self.update_scans_list()
        self.populate_regions()
        
        # Refresh current region view if one is selected
        current_index = self.region_combo.currentIndex()
        if current_index > 0:
            self.on_region_changed(current_index)
        
        # Show results
        message = f"Successfully imported {added_count} scan(s)."
        if added_count == 0 and error_count == 0:
            message += "\n\nNo valid wormhole entries found in the pasted text."
            message += "\n\nExpected format:"
            message += "\nL-1SW8 => @Barbican, Life: Fresh, Mass: 100% > 50%"
            message += "\n\nOr with region header:"
            message += "\nFountain (Scanned: 3/26)"
            message += "\nL-1SW8 => @Barbican, Life: Fresh, Mass: 100% > 50%"
        if scan_timestamp:
            time_diff = datetime.now() - scan_timestamp
            if time_diff.days > 0:
                message += f"\n\nScans dated: {time_diff.days} day(s) ago"
            elif time_diff.seconds > 3600:
                message += f"\n\nScans dated: {time_diff.seconds // 3600} hour(s) ago"
            if added_count > 0:
                message += f"\n\nTip: Use 'Clean Expired' button to remove old wormholes."
        if error_count > 0:
            message += f"\n\n{error_count} error(s):\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                message += f"\n... and {len(errors) - 10} more"
        
        QMessageBox.information(self, 'Bulk Import Complete', message)

    def on_region_changed(self, index):
        if index == 0:
            # Clear system buttons
            while self.system_grid_layout.count():
                item = self.system_grid_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            self.system_buttons_widget.setVisible(False)
            self.type_buttons_widget.setVisible(False)
            self.paste_widget.setVisible(False)
            self.selected_system_label.setVisible(False)
            self.no_hole_btn.setVisible(False)
            self.back_btn.setVisible(False)
            self.current_region = None
            self.current_system = None
            return
        
        region = self.region_combo.itemData(index)
        
        # Safety check - if region is None, return
        if not region or region not in JOVE_SYSTEMS:
            return
        
        self.current_region = region
        
        # Clear existing system buttons
        while self.system_grid_layout.count():
            item = self.system_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get systems for this region
        all_systems = sorted(JOVE_SYSTEMS[region])
        
        # Filter out systems marked as "No Hole"
        systems_with_no_hole = set()
        systems_with_holes = {}  # system -> count of wormholes
        
        for scan in self.scans:
            if scan['region'] == region:
                if scan['holeType'] == 'None':
                    systems_with_no_hole.add(scan['system'])
                else:
                    if scan['system'] not in systems_with_holes:
                        systems_with_holes[scan['system']] = 0
                    systems_with_holes[scan['system']] += 1
        
        # Only show systems that haven't been marked as "No Hole"
        available_systems = [s for s in all_systems if s not in systems_with_no_hole]
        
        # Use fixed 4 columns for all regions - works well at all window sizes
        cols = 4
        
        # Create buttons in grid
        for i, system in enumerate(available_systems):
            row = i // cols
            col = i % cols
            
            # Check if this system has wormholes
            has_holes = system in systems_with_holes
            hole_count = systems_with_holes.get(system, 0)
            
            # Create button text with wormhole indicator
            if has_holes:
                btn_text = f"● {system}"
                if hole_count > 1:
                    btn_text += f" ({hole_count})"
                btn_style = """
                    QPushButton {
                        background: #16161d;
                        border: 2px solid #b8b8b8;
                        border-radius: 2px;
                        padding: 8px 12px;
                        color: #e8e8e8;
                        font-weight: bold;
                        font-size: 12px;
                        min-height: 30px;
                    }
                    QPushButton:hover {
                        border-color: #e8e8e8;
                        background: #1e1e28;
                        color: #e8e8e8;
                    }
                """
            else:
                btn_text = system
                btn_style = """
                    QPushButton {
                        background: #16161d;
                        border: 1px solid #2a2a35;
                        border-radius: 2px;
                        padding: 8px 12px;
                        color: #e8e8e8;
                        font-weight: normal;
                        font-size: 12px;
                        min-height: 30px;
                    }
                    QPushButton:hover {
                        border-color: #e8e8e8;
                        background: #0e0e14;
                        color: #e8e8e8;
                        font-weight: bold;
                    }
                """
            
            btn = QPushButton(btn_text)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(lambda checked, s=system: self.on_system_selected(s))
            self.system_grid_layout.addWidget(btn, row, col)
        
        self.system_buttons_widget.setVisible(True)
        self.type_buttons_widget.setVisible(False)
        self.paste_widget.setVisible(False)
        self.selected_system_label.setVisible(False)
        self.selected_type_label.setVisible(False)
        self.no_hole_btn.setVisible(False)
        self.parse_btn.setVisible(False)
        self.back_btn.setVisible(False)

    def on_system_selected(self, system):
        self.current_system = system
        
        # Hide system buttons and show type buttons
        self.system_buttons_widget.setVisible(False)
        self.selected_system_label.setText(f'Selected System: {system}')
        self.selected_system_label.setVisible(True)
        self.type_buttons_widget.setVisible(True)
        self.no_hole_btn.setVisible(True)
        self.back_btn.setVisible(True)
        
        # Uncheck all type buttons
        for btn in self.type_buttons.values():
            btn.setChecked(False)
        
        self.paste_widget.setVisible(False)
        self.parse_btn.setVisible(False)
        self.selected_type_label.setVisible(False)

    def on_type_button_clicked(self, hole_type):
        # Uncheck other buttons
        for type_name, btn in self.type_buttons.items():
            if type_name != hole_type:
                btn.setChecked(False)
        
        # Show paste area if this button is now checked
        if self.type_buttons[hole_type].isChecked():
            self.current_hole_type = hole_type
            self.paste_widget.setVisible(True)
            self.parse_btn.setVisible(True)
            self.selected_type_label.setText(f'Adding: {hole_type} Wormhole')
            self.selected_type_label.setVisible(True)
            self.wh_text.clear()
            self.wh_text.setFocus()
        else:
            self.current_hole_type = None
            self.paste_widget.setVisible(False)
            self.parse_btn.setVisible(False)
            self.selected_type_label.setVisible(False)
    
    def go_back(self):
        """Go back to previous state based on what's currently shown"""
        if self.paste_widget.isVisible():
            # Go back from paste to type selection
            self.paste_widget.setVisible(False)
            self.parse_btn.setVisible(False)
            self.selected_type_label.setVisible(False)
            self.wh_text.clear()
            for btn in self.type_buttons.values():
                btn.setChecked(False)
            self.current_hole_type = None
        elif self.type_buttons_widget.isVisible():
            # Go back from type selection to system selection
            self.type_buttons_widget.setVisible(False)
            self.selected_system_label.setVisible(False)
            self.system_buttons_widget.setVisible(True)
            self.no_hole_btn.setVisible(False)
            self.back_btn.setVisible(False)
            for btn in self.type_buttons.values():
                btn.setChecked(False)
            self.current_system = None
            self.current_hole_type = None

    def parse_wormhole_info(self, text):
        """Parse wormhole information from EVE client paste"""
        text_lower = text.lower()
        
        hole_type = 'Unknown'
        life_status = 'Fresh'
        mass_status = '100% > 50%'
        
        # Detect hole type
        if 'vidette' in text_lower:
            hole_type = 'Vidette'
        elif 'redoubt' in text_lower:
            hole_type = 'Redoubt'
        elif 'sentinel' in text_lower:
            hole_type = 'Sentinel'
        elif 'barbican' in text_lower:
            hole_type = 'Barbican'
        elif 'conflux' in text_lower:
            hole_type = 'Conflux'
        elif 'k162' in text_lower or 'unidentified' in text_lower:
            hole_type = 'Unidentified'
        
        # Detect life status
        if 'not yet' in text_lower and 'stability' in text_lower and 'disrupted' in text_lower:
            life_status = 'Fresh'
        elif 'beginning of' in text_lower and 'natural lifetime' in text_lower:
            life_status = 'Fresh'
        elif 'stability' in text_lower and 'reduced' in text_lower and 'not yet' in text_lower and 'critical' in text_lower:
            life_status = 'Destabilizing'
        elif 'verge of dissipating' in text_lower or ('reaching' in text_lower and 'end' in text_lower and 'natural lifetime' in text_lower):
            life_status = 'Critical'
        
        # Detect mass status
        if 'not yet' in text_lower and 'mass' in text_lower and 'significantly disrupted' in text_lower:
            mass_status = '100% > 50%'
        elif 'mass' in text_lower and 'reduced' in text_lower and 'not yet' in text_lower and 'critical' in text_lower:
            mass_status = '50% > 10%'
        elif 'verge of collapse' in text_lower or ('mass' in text_lower and 'critical' in text_lower):
            mass_status = '< 10%'
        
        return hole_type, life_status, mass_status

    def calculate_spawn_time(self, life_status, scan_time=None):
        """
        Calculate estimated spawn time based on wormhole life status.
        
        Wormhole lifecycle:
        - Fresh: 0-4 hours old
        - Destabilizing: 4-24 hours old  
        - Critical: 24+ hours old (we'll estimate 24h exactly)
        
        Args:
            life_status: The wormhole's current life status
            scan_time: When the wormhole was scanned (defaults to now)
        
        Returns a datetime representing when the wormhole likely spawned.
        """
        if scan_time is None:
            scan_time = datetime.now()
        
        if life_status == 'Fresh':
            # Fresh wormhole - assume it just spawned (could be 0-4h old)
            # Conservative: assume it spawned when scanned (safest assumption)
            return scan_time
        
        elif life_status == 'Destabilizing':
            # Destabilizing: 4-24 hours old
            # Conservative: assume it's been 4 hours (just turned destabilizing)
            # This gives maximum remaining lifetime
            return scan_time - timedelta(hours=4)
        
        elif life_status == 'Critical':
            # Critical: 24+ hours old
            # Conservative: assume it's been exactly 24 hours
            # This gives maximum remaining lifetime before it collapses
            return scan_time - timedelta(hours=24)
        
        else:
            # Unknown status - assume fresh
            return scan_time
    
    def add_scan_from_paste(self):
        if not self.current_region or not self.current_system:
            QMessageBox.warning(self, 'No System Selected', 'Please select a region and system first')
            return
        
        region = self.current_region
        system = self.current_system
        wh_info = self.wh_text.toPlainText().strip()
        role_id = self.role_input.text().strip()
        
        # Get selected hole type
        selected_type = self.current_hole_type
        
        if not selected_type:
            QMessageBox.warning(self, 'No Type Selected', 'Please select a wormhole type first')
            return
        
        if not wh_info:
            QMessageBox.warning(self, 'No Data', 'Please paste wormhole information from EVE client')
            return
        
        # Save role ID as default
        if role_id:
            self.default_role_id = role_id
            self.settings.setValue('default_role_id', role_id)
        
        # Parse the wormhole info (for life and mass)
        _, life_status, mass_status = self.parse_wormhole_info(wh_info)
        
        # Calculate actual spawn time based on life status
        # This ensures the wormhole shows the correct age and expiration
        spawn_time = self.calculate_spawn_time(life_status)
        
        # Add new scan (don't remove existing - allow multiple wormholes per system)
        scan = {
            'id': int(datetime.now().timestamp() * 1000000),  # More unique IDs for multiple holes
            'region': region,
            'system': system,
            'holeType': selected_type,
            'lifeStatus': life_status,
            'massStatus': mass_status,
            'roleId': role_id or self.default_role_id,
            'rawInfo': wh_info,
            'scannedAt': spawn_time.isoformat()  # Use calculated spawn time, not current time
        }
        
        self.scans.insert(0, scan)
        self.save_scans()
        self.update_scans_list()
        
        # Refresh region list to update status
        self.populate_regions()
        
        # Refresh the system grid to update the wormhole indicator
        current_index = self.region_combo.currentIndex()
        self.on_region_changed(current_index)
        
        # After refreshing, re-select the current system to continue adding holes
        self.on_system_selected(system)
        
        # Reset form partially - clear paste area but keep type selection visible
        self.wh_text.clear()
        for btn in self.type_buttons.values():
            btn.setChecked(False)
        self.paste_widget.setVisible(False)
        self.parse_btn.setVisible(False)
        self.selected_type_label.setVisible(False)
        self.current_hole_type = None
        
        # Show success message
        QMessageBox.information(
            self, 'Scan Added', 
            f'{selected_type} wormhole added to {system}.\n\nYou can add more wormholes to this system or go back to select a different system.'
        )

    def add_no_hole_scan(self):
        if not self.current_region or not self.current_system:
            QMessageBox.warning(self, 'No System Selected', 'Please select a region and system first')
            return
        
        region = self.current_region
        system = self.current_system
        role_id = self.role_input.text().strip()
        
        # Check if there are already wormholes logged for this system
        existing_holes = [s for s in self.scans if s['system'] == system and s['holeType'] != 'None']
        if existing_holes:
            reply = QMessageBox.question(
                self, 'Existing Wormholes',
                f'{system} already has {len(existing_holes)} wormhole(s) logged.\n\nDo you want to mark this system as having no holes?\nThis will remove all existing wormhole entries for this system.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Save role ID as default
        if role_id:
            self.default_role_id = role_id
            self.settings.setValue('default_role_id', role_id)
        
        # Remove all existing scans for this system (since we're marking it as no hole)
        self.scans = [s for s in self.scans if s['system'] != system]
        
        # Add new scan
        scan = {
            'id': int(datetime.now().timestamp() * 1000),
            'region': region,
            'system': system,
            'holeType': 'None',
            'lifeStatus': 'N/A',
            'massStatus': 'N/A',
            'roleId': role_id or self.default_role_id,
            'scannedAt': datetime.now().isoformat()
        }
        
        self.scans.insert(0, scan)
        self.save_scans()
        self.update_scans_list()
        
        # Refresh region list to update status
        self.populate_regions()
        
        # Refresh the system grid to hide the system that was just marked as "No Hole"
        # Re-trigger region changed to rebuild the grid
        current_index = self.region_combo.currentIndex()
        self.on_region_changed(current_index)
        
        # Reset form state
        self.type_buttons_widget.setVisible(False)
        self.selected_system_label.setVisible(False)
        self.no_hole_btn.setVisible(False)
        self.back_btn.setVisible(False)
        self.current_system = None

    def update_scans_list(self):
        self.scans_list.clear()
        
        if not self.scans:
            item = QListWidgetItem('🌌 No Systems Scanned\n\nBegin scanning Jove Observatory systems to track drifter wormholes')
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scans_list.addItem(item)
            self.update_stats(0, 0, 0)
            return
        
        # Group by region, then by system
        by_region = {}
        for scan in self.scans:
            region = scan['region']
            system = scan['system']
            if region not in by_region:
                by_region[region] = {}
            if system not in by_region[region]:
                by_region[region][system] = []
            by_region[region][system].append(scan)
        
        # Calculate stats
        total_systems = sum(len(systems) for systems in by_region.values())
        holes_found = len([s for s in self.scans if s['holeType'] != 'None'])
        regions_count = len(by_region)
        self.update_stats(total_systems, holes_found, regions_count)
        
        # Add region groups
        for region in sorted(by_region.keys()):
            systems_dict = by_region[region]
            total_in_region = len(JOVE_SYSTEMS[region])
            scanned_in_region = len(systems_dict)
            is_complete = scanned_in_region == total_in_region
            status = '[COMPLETE]' if is_complete else '[INCOMPLETE]'
            
            # Region header
            header_text = f'━━━ {region} ({scanned_in_region}/{total_in_region}) {status} ━━━'
            header_item = QListWidgetItem(header_text)
            header_item.setForeground(QColor('#e8e8e8'))
            header_item.setFont(QFont('Arial', 12, QFont.Weight.Bold))
            self.scans_list.addItem(header_item)
            
            # System scans (grouped by system)
            for system in sorted(systems_dict.keys()):
                scans = systems_dict[system]
                
                # System header
                system_header = f"  ► {system}"
                if len(scans) > 1:
                    system_header += f" ({len(scans)} wormholes)"
                system_item = QListWidgetItem(system_header)
                system_item.setForeground(QColor('#b8b8b8'))
                system_item.setFont(QFont('Arial', 11, QFont.Weight.Bold))
                self.scans_list.addItem(system_item)
                
                # Individual wormholes - each on its own row with a delete button
                for scan in sorted(scans, key=lambda s: s['scannedAt'], reverse=True):
                    hole_display = 'No Hole' if scan['holeType'] == 'None' else scan['holeType']
                    scanned_time = datetime.fromisoformat(scan['scannedAt']).strftime('%Y-%m-%d %H:%M')
                    
                    # Create a simple text item for the scan
                    scan_text = f"        {hole_display}"
                    if scan['holeType'] != 'None':
                        scan_text += f"  |  Life: {scan['lifeStatus']}  |  Mass: {scan['massStatus']}"
                    scan_text += f"\n        Scanned: {scanned_time}"
                    
                    # Add simple list item
                    item = QListWidgetItem(scan_text)
                    item.setData(Qt.ItemDataRole.UserRole, scan['id'])
                    if scan['holeType'] == 'None':
                        item.setForeground(QColor('#8a8a8a'))
                    else:
                        item.setForeground(QColor('#ffffff'))
                    self.scans_list.addItem(item)
        
        # Enable context menu for deletion (right-click to delete)
        self.scans_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.scans_list.customContextMenuRequested.connect(self.show_context_menu)

    def update_stats(self, total, holes, regions):
        # Update stat cards
        for i, widget in enumerate(self.stats_widget.findChildren(QGroupBox)):
            value_label = widget.findChild(QLabel)
            if i == 0:
                value_label.setText(str(total))
            elif i == 1:
                value_label.setText(str(holes))
            elif i == 2:
                value_label.setText(str(regions))

    def show_context_menu(self, position):
        item = self.scans_list.itemAt(position)
        if item and item.data(Qt.ItemDataRole.UserRole):
            from PyQt6.QtWidgets import QMenu
            from PyQt6.QtGui import QAction
            
            menu = QMenu()
            delete_action = QAction('Delete', self)
            delete_action.triggered.connect(lambda: self.delete_scan(item.data(Qt.ItemDataRole.UserRole)))
            menu.addAction(delete_action)
            menu.exec(self.scans_list.mapToGlobal(position))

    def delete_scan(self, scan_id):
        # Find the scan to show details in confirmation
        scan_to_delete = None
        for scan in self.scans:
            if scan['id'] == scan_id:
                scan_to_delete = scan
                break
        
        if not scan_to_delete:
            return
        
        # Confirmation dialog
        hole_name = scan_to_delete['holeType'] if scan_to_delete['holeType'] != 'None' else 'No Hole'
        system_name = scan_to_delete['system']
        region_name = scan_to_delete['region']
        
        reply = QMessageBox.question(
            self, 'Delete Scan',
            f"Delete this scan?\n\n"
            f"System: {system_name} ({region_name})\n"
            f"Wormhole: {hole_name}\n\n"
            f"This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.scans = [s for s in self.scans if s['id'] != scan_id]
            self.save_scans()
            self.update_scans_list()
            
            # Refresh region list to update status
            self.populate_regions()
            
            # Update routing dropdown if it exists
            if hasattr(self, 'dest_region_combo'):
                self.update_routing_dropdown()
            
            # Refresh the system grid to update indicators
            current_index = self.region_combo.currentIndex()
            if current_index > 0:
                self.on_region_changed(current_index)

    def clear_all_data(self):
        reply = QMessageBox.question(
            self, 'Clear All Data',
            'Are you sure you want to clear all scan data?\n\nThis action cannot be undone.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.scans = []
            self.save_scans()
            self.update_scans_list()
            
            # Refresh region list to remove all status indicators
            self.populate_regions()
            
            # Refresh the system grid to show all systems again
            current_index = self.region_combo.currentIndex()
            if current_index > 0:
                self.on_region_changed(current_index)

    def show_discord_export(self):
        if not self.scans:
            QMessageBox.information(self, 'No Data', 'No scan data available. Please scan systems first.')
            return
        
        dialog = ExportDialog(self.scans, self)
        dialog.exec()

    def load_scans(self):
        try:
            scans_json = self.settings.value('scans', '[]')
            return json.loads(scans_json)
        except:
            return []

    def save_scans(self):
        self.settings.setValue('scans', json.dumps(self.scans))




    def create_routing_tab(self):
        """Create the routing tab with pathfinding capabilities"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_label = QLabel('[ROUTING] Drifter Wormhole Routing')
        header_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 900;
            color: #e8e8e8;
            padding: 10px 0;
        """)
        layout.addWidget(header_label)
        
        # Check if SDE is loaded for advanced features
        sde_available = self.sde_loader is not None
        
        # Controls
        controls_group = QGroupBox()
        controls_group.setStyleSheet("""
            QGroupBox {
                background: #0e0e14;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 20px;
            }
        """)
        controls_layout = QVBoxLayout(controls_group)
        
        # Mode selector: Simple or Advanced
        mode_layout = QHBoxLayout()
        mode_label = QLabel('Routing Mode:')
        mode_label.setStyleSheet('font-weight: bold; color: #e8e8e8; font-size: 14px;')
        
        self.routing_mode_combo = QComboBox()
        self.routing_mode_combo.addItem('🏠 Home Regions → Destination', 'simple')
        if sde_available:
            self.routing_mode_combo.addItem('🌐 Any System → Any System (Hybrid)', 'hybrid')
        self.routing_mode_combo.currentIndexChanged.connect(self.on_routing_mode_changed)
        
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.routing_mode_combo, 1)
        controls_layout.addLayout(mode_layout)
        
        # Simple mode controls (home regions)
        self.simple_controls = QWidget()
        simple_layout = QHBoxLayout(self.simple_controls)
        simple_layout.setContentsMargins(0, 10, 0, 0)
        
        dest_label = QLabel('Destination Region:')
        dest_label.setStyleSheet('font-weight: bold; color: #e8e8e8; font-size: 14px;')
        self.dest_region_combo = QComboBox()
        self.dest_region_combo.addItem('Select Region')
        for region in sorted(JOVE_SYSTEMS.keys()):
            self.dest_region_combo.addItem(region, region)
        self.dest_region_combo.currentIndexChanged.connect(self.calculate_routes)
        
        simple_layout.addWidget(dest_label)
        simple_layout.addWidget(self.dest_region_combo, 1)
        controls_layout.addWidget(self.simple_controls)
        
        # Advanced mode controls (any system)
        self.advanced_controls = QWidget()
        advanced_layout = QHBoxLayout(self.advanced_controls)
        advanced_layout.setContentsMargins(0, 10, 0, 0)
        
        # Origin system
        origin_label = QLabel('From:')
        origin_label.setStyleSheet('font-weight: bold; color: #e8e8e8; font-size: 14px;')
        self.origin_system_input = QLineEdit()
        self.origin_system_input.setPlaceholderText('Enter system name (e.g., Jita)')
        self.origin_system_input.setStyleSheet("""
            QLineEdit {
                background: #16161d;
                border: 2px solid #2a2a35;
                border-radius: 2px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #e8e8e8;
            }
        """)
        
        # Add autocomplete for origin
        if self.sde_loader:
            from PyQt6.QtWidgets import QCompleter
            from PyQt6.QtCore import Qt as QtCore_Qt
            
            origin_completer = QCompleter(sorted(self.sde_loader.system_name_to_id.keys()))
            origin_completer.setCaseSensitivity(QtCore_Qt.CaseSensitivity.CaseInsensitive)
            origin_completer.setFilterMode(QtCore_Qt.MatchFlag.MatchContains)
            origin_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            self.origin_system_input.setCompleter(origin_completer)
        
        # Destination system
        dest_label2 = QLabel('To:')
        dest_label2.setStyleSheet('font-weight: bold; color: #e8e8e8; font-size: 14px;')
        self.dest_system_input = QLineEdit()
        self.dest_system_input.setPlaceholderText('Enter system name (e.g., Amarr)')
        self.dest_system_input.setStyleSheet("""
            QLineEdit {
                background: #16161d;
                border: 2px solid #2a2a35;
                border-radius: 2px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #e8e8e8;
            }
        """)
        
        # Add autocomplete for destination
        if self.sde_loader:
            dest_completer = QCompleter(sorted(self.sde_loader.system_name_to_id.keys()))
            dest_completer.setCaseSensitivity(QtCore_Qt.CaseSensitivity.CaseInsensitive)
            dest_completer.setFilterMode(QtCore_Qt.MatchFlag.MatchContains)
            dest_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            self.dest_system_input.setCompleter(dest_completer)
        
        # Enable Enter key to trigger route finding
        self.origin_system_input.returnPressed.connect(self.calculate_hybrid_routes)
        self.dest_system_input.returnPressed.connect(self.calculate_hybrid_routes)
        
        # Find route button
        find_route_btn = QPushButton('FIND ROUTES')
        find_route_btn.clicked.connect(self.calculate_hybrid_routes)
        find_route_btn.setStyleSheet("""
            QPushButton {
                background: #16161d;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 10px 20px;
                color: #e8e8e8;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1e1e28;
                border: 1px solid #4a4a55;
            }
            QPushButton:pressed {
                background: #0e0e14;
            }
        """)
        
        advanced_layout.addWidget(origin_label)
        advanced_layout.addWidget(self.origin_system_input, 1)
        advanced_layout.addWidget(dest_label2)
        advanced_layout.addWidget(self.dest_system_input, 1)
        advanced_layout.addWidget(find_route_btn)
        controls_layout.addWidget(self.advanced_controls)
        
        # Hide advanced controls initially
        self.advanced_controls.hide()
        
        # Bottom control row
        bottom_controls = QHBoxLayout()
        
        # Refresh button (multi-hop now always enabled)
        refresh_btn = QPushButton('REFRESH ROUTES')
        refresh_btn.clicked.connect(self.refresh_routes_with_feedback)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #16161d;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 10px 20px;
                color: #e8e8e8;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1e1e28;
                border: 1px solid #4a4a55;
            }
            QPushButton:pressed {
                background: #0e0e14;
            }
        """)
        
        bottom_controls.addWidget(refresh_btn)
        bottom_controls.addStretch()
        
        controls_layout.addLayout(bottom_controls)
        layout.addWidget(controls_group)
        
        # Routes display
        self.routes_list = QListWidget()
        self.routes_list.setStyleSheet("""
            QListWidget {
                background: #0e0e14;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 15px;
                font-size: 13px;
            }
            QListWidget::item {
                background: #16161d;
                border: 1px solid #2a2a35;
                border-left: 4px solid #e8e8e8;
                border-radius: 2px;
                padding: 20px;
                margin: 8px 0;
            }
            QListWidget::item:hover {
                border-color: #e8e8e8;
                background: #1f2742;
            }
        """)
        self.routes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.routes_list.customContextMenuRequested.connect(self.show_route_context_menu)
        
        layout.addWidget(self.routes_list, 1)
        
        # Initial load
        self.safest_mode = False
        if hasattr(self, 'dest_region_combo'):
            self.update_routing_dropdown()  # Initialize with wormhole symbols
        self.calculate_routes()
        
        return widget
    
    def on_routing_mode_changed(self, index):
        """Handle routing mode change"""
        mode = self.routing_mode_combo.currentData()
        
        if mode == 'simple':
            self.simple_controls.show()
            self.advanced_controls.hide()
            self.calculate_routes()
        else:  # hybrid
            self.simple_controls.hide()
            self.advanced_controls.show()
            self.routes_list.clear()
            item = QListWidgetItem("Enter origin and destination systems, then click 'Find Routes'")
            item.setForeground(QColor('#8a8a8a'))
            self.routes_list.addItem(item)
    
    def toggle_route_mode(self):
        """Toggle between dodgy and safest path mode"""
        self.safest_mode = self.route_mode_toggle.isChecked()
        if self.safest_mode:
            self.route_mode_toggle.setText('Mode: Safest Path')
        else:
            self.route_mode_toggle.setText('Mode: Dodgy Path')
        self.calculate_routes()
    
    def refresh_routes_with_feedback(self):
        """Refresh routes with visual feedback"""
        # Show loading state
        self.routes_list.clear()
        loading_item = QListWidgetItem("🔄 Refreshing routes...")
        loading_item.setForeground(QColor('#e8e8e8'))
        loading_item.setFont(QFont('', 12, QFont.Weight.Bold))
        self.routes_list.addItem(loading_item)
        
        # Process events to show the loading message
        QTimer.singleShot(100, lambda: self.calculate_hybrid_routes() if self.sde_loader else self.calculate_routes())
    
    def calculate_hybrid_routes(self):
        """Calculate hybrid routes using stargates + wormholes"""
        self.routes_list.clear()
        
        if not self.sde_loader:
            item = QListWidgetItem("⚠️ SDE data not loaded. Run 'python setup_sde.py' first.")
            item.setForeground(QColor('#ff6b6b'))
            self.routes_list.addItem(item)
            return
        
        # Get start and end systems
        from_system = self.from_system_combo.currentData()
        to_system = self.to_system_combo.currentData()
        
        if not from_system or not to_system:
            item = QListWidgetItem("Please select both starting and destination systems")
            item.setForeground(QColor('#8a8a8a'))
            self.routes_list.addItem(item)
            return
        
        # Get max gates setting
        try:
            max_gates = int(self.max_jumps_input.text())
        except:
            max_gates = 15
        
        # Build wormhole connection graph
        connections = self.build_connection_graph()
        
        if not connections:
            # No wormholes - just do direct stargate route
            self.show_stargate_only_route(from_system, to_system)
            return
        
        # Find hybrid routes: Stargates → Wormhole → Stargates
        routes = self.find_hybrid_routes(from_system, to_system, connections, max_gates)
        
        if not routes:
            # Fallback to direct stargate route
            self.show_stargate_only_route(from_system, to_system)
            return
        
        # Display routes
        for route_data in routes[:5]:  # Show top 5 routes
            self.display_hybrid_route(route_data)
    
    def find_hybrid_routes(self, from_system, to_system, connections, max_gates):
        """Find routes combining stargates and wormholes"""
        routes = []
        
        # Get all systems with wormholes
        wormhole_systems = list(connections.keys())
        
        # For each wormhole system, calculate:
        # 1. Gates from start to wormhole entry
        # 2. Wormhole jump
        # 3. Gates from wormhole exit to destination
        
        for entry_system in wormhole_systems:
            # Path from start to wormhole entry
            entry_path = self.sde_loader.find_path(from_system, entry_system, max_jumps=max_gates)
            
            if not entry_path:
                continue
            
            entry_gates = len(entry_path) - 1
            
            # For each system this wormhole connects to
            for exit_system, wh_data in connections[entry_system]:
                # Path from wormhole exit to destination
                exit_path = self.sde_loader.find_path(exit_system, to_system, max_jumps=max_gates)
                
                if not exit_path:
                    continue
                
                exit_gates = len(exit_path) - 1
                total_gates = entry_gates + exit_gates
                
                # Calculate route score
                score = self.calculate_route_score(
                    entry_gates, exit_gates, wh_data, total_gates
                )
                
                routes.append({
                    'entry_path': entry_path,
                    'entry_system': entry_system,
                    'exit_system': exit_system,
                    'exit_path': exit_path,
                    'wormhole': wh_data,
                    'entry_gates': entry_gates,
                    'exit_gates': exit_gates,
                    'total_gates': total_gates,
                    'score': score
                })
        
        # Sort by score (lower is better)
        routes.sort(key=lambda r: r['score'])
        
        return routes
    
    def calculate_route_score(self, entry_gates, exit_gates, wh_data, total_gates):
        """Calculate route score based on weighted criteria"""
        score = 0
        
        # Base score: total gates
        score += total_gates
        
        # Wormhole life penalties
        if wh_data['lifeStatus'] == 'Critical':
            score += 20  # Heavy penalty
        elif wh_data['lifeStatus'] == 'Destabilizing':
            score += 10  # Moderate penalty
        
        # Mass penalties
        if '< 10%' in wh_data['massStatus']:
            score += 15  # Critical mass
        elif '50% > 10%' in wh_data['massStatus']:
            score += 5  # Reduced mass
        
        # Gate distribution penalty (prefer balanced routes)
        gate_imbalance = abs(entry_gates - exit_gates)
        score += gate_imbalance * 0.5
        
        # Bonus for short routes
        if total_gates < 10:
            score -= 5
        
        # Bonus for fresh, full mass holes
        if wh_data['lifeStatus'] == 'Fresh' and '100% > 50%' in wh_data['massStatus']:
            score -= 3
        
        return score
    
    def count_jumpbridges_in_path(self, path):
        """Count how many jumpbridges are used in a path"""
        if not path or len(path) < 2 or not self.sde_loader:
            return 0
        
        jb_count = 0
        for i in range(len(path) - 1):
            current = path[i]
            next_sys = path[i + 1]
            
            # Get system IDs
            current_id = self.sde_loader.system_name_to_id.get(current)
            next_id = self.sde_loader.system_name_to_id.get(next_sys)
            
            if current_id and next_id:
                # Check if this hop is a jumpbridge
                if current_id in self.sde_loader.jumpbridges:
                    if next_id in self.sde_loader.jumpbridges[current_id]:
                        jb_count += 1
        
        return jb_count
    
    def display_hybrid_route(self, route_data):
        """Display a hybrid route with detailed information"""
        entry_gates = route_data['entry_gates']
        exit_gates = route_data['exit_gates']
        total_gates = route_data['total_gates']
        wh = route_data['wormhole']
        score = route_data['score']
        
        # Count jumpbridges in entry and exit paths
        entry_jbs = self.count_jumpbridges_in_path(route_data.get('entry_path', []))
        exit_jbs = self.count_jumpbridges_in_path(route_data.get('exit_path', []))
        total_jbs = entry_jbs + exit_jbs
        
        # Calculate actual gate jumps (excluding JBs)
        entry_gates_only = entry_gates - entry_jbs
        exit_gates_only = exit_gates - exit_jbs
        total_gates_only = entry_gates_only + exit_gates_only
        
        # Determine route quality
        if score < 10:
            quality = "[OPTIMAL]"
            color = "#51cf66"
        elif score < 20:
            quality = "[OK]"
            color = "#ffa500"
        elif score < 30:
            quality = "🟠 Acceptable"
            color = "#ff8800"
        else:
            quality = "[WARNING]"
            color = "#ff6b6b"
        
        # Build route description with JB info
        if total_jbs > 0:
            route_text = f"{quality} - {total_gates_only} gates + {total_jbs} JB{'s' if total_jbs > 1 else ''}\n"
        else:
            route_text = f"{quality} - {total_gates} total gates\n"
        
        # Entry leg
        if entry_jbs > 0:
            route_text += f"    {route_data['entry_path'][0]} → [{entry_gates_only} gates + {entry_jbs} JB] → "
        else:
            route_text += f"    {route_data['entry_path'][0]} → [{entry_gates} gates] → "
        route_text += f"{route_data['entry_system']}\n"
        route_text += f"    ↓ [{wh['holeType']} Wormhole"
        
        # Add warnings
        warnings = []
        if wh['lifeStatus'] in ['Critical', 'Destabilizing']:
            warnings.append(f"{wh['lifeStatus']}")
        if '< 10%' in wh['massStatus']:
            warnings.append("Low Mass")
        
        if warnings:
            route_text += f" - ⚠️ {', '.join(warnings)}"
        
        route_text += f"] ↓\n"
        
        # Exit leg  
        if exit_jbs > 0:
            route_text += f"    {route_data['exit_system']} → [{exit_gates_only} gates + {exit_jbs} JB] → "
        else:
            route_text += f"    {route_data['exit_system']} → [{exit_gates} gates] → "
        route_text += f"{route_data['exit_path'][-1]}"
        
        item = QListWidgetItem(route_text)
        item.setForeground(QColor(color))
        item.setData(Qt.ItemDataRole.UserRole, route_data)
        self.routes_list.addItem(item)
    
    def show_stargate_only_route(self, from_system, to_system):
        """Show direct stargate route when no wormholes available"""
        path = self.sde_loader.find_path(from_system, to_system, max_jumps=50)
        
        if not path:
            item = QListWidgetItem(f"No route found between {from_system} and {to_system}")
            item.setForeground(QColor('#ff6b6b'))
            self.routes_list.addItem(item)
            return
        
        gates = len(path) - 1
        
        route_text = f"⭐ Direct Stargate Route - {gates} jumps\n"
        route_text += f"    {from_system} → ... → {to_system}\n"
        route_text += f"    No drifter wormholes available for this route"
        
        item = QListWidgetItem(route_text)
        item.setForeground(QColor('#8a8a8a'))
        self.routes_list.addItem(item)
    
    def refresh_routes_with_feedback(self):
        """Refresh routes with visual feedback"""
        # Show loading state
        self.routes_list.clear()
        loading_item = QListWidgetItem("🔄 Refreshing routes...")
        loading_item.setForeground(QColor('#e8e8e8'))
        loading_item.setFont(QFont('', 12, QFont.Weight.Bold))
        self.routes_list.addItem(loading_item)
        
        # Determine which calculation to run
        mode = self.routing_mode_combo.currentData() if hasattr(self, 'routing_mode_combo') else 'simple'
        
        if mode == 'hybrid':
            QTimer.singleShot(100, self.calculate_hybrid_routes)
        else:
            QTimer.singleShot(100, self.calculate_routes)
    
    def calculate_hybrid_routes(self):
        """Calculate hybrid routes using stargates + wormholes"""
        self.routes_list.clear()
        
        # Show "Calculating..." indicator
        calculating_item = QListWidgetItem("🔄 Calculating routes...")
        calculating_item.setForeground(QColor('#51cf66'))
        self.routes_list.addItem(calculating_item)
        
        # Process events so indicator shows immediately
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
        
        if not self.sde_loader:
            self.routes_list.clear()  # Clear indicator
            item = QListWidgetItem("⚠️ SDE data not loaded. Run 'python setup_sde.py' for hybrid routing.")
            item.setForeground(QColor('#ff6b6b'))
            self.routes_list.addItem(item)
            return
        
        # Get origin and destination
        origin = self.origin_system_input.text().strip()
        destination = self.dest_system_input.text().strip()
        
        if not origin or not destination:
            self.routes_list.clear()  # Clear indicator
            item = QListWidgetItem("Please enter both origin and destination systems")
            item.setForeground(QColor('#8a8a8a'))
            self.routes_list.addItem(item)
            return
        
        # Try to find system names (case-insensitive, partial match)
        origin_matched = self.find_system_name(origin)
        destination_matched = self.find_system_name(destination)
        
        # Validate systems exist
        if not origin_matched:
            self.show_system_suggestions(origin, "origin")
            return
        
        if not destination_matched:
            self.show_system_suggestions(destination, "destination")
            return
        
        # Update input fields with matched names
        self.origin_system_input.setText(origin_matched)
        self.dest_system_input.setText(destination_matched)
        
        # Build wormhole connection graph
        connections = self.build_connection_graph()
        
        if not connections:
            # No wormholes available - show direct route
            self.show_direct_route(origin_matched, destination_matched)
            return
        
        # Find hybrid routes
        routes = self.find_hybrid_routes(origin_matched, destination_matched, connections)
        
        # Clear the "Calculating..." indicator
        self.routes_list.clear()
        
        if not routes:
            # No good hybrid routes - show direct route
            self.show_direct_route(origin_matched, destination_matched)
            return
        
        # Display top routes
        for i, route_data in enumerate(routes[:5]):
            # Filter by multi-hop setting
            allow_multihop = True  # Multi-hop always enabled
            wormhole_count = route_data.get('wormhole_count', 1)
            
            # Skip multi-hop routes if toggle is OFF
            if wormhole_count > 1 and not allow_multihop:
                continue
            
            self.display_hybrid_route(route_data, i + 1)
    
    def find_system_name(self, query):
        """Find exact or close match for system name"""
        if not self.sde_loader:
            return None
        
        # Exact match (case-insensitive)
        for system_name in self.sde_loader.system_name_to_id.keys():
            if system_name.lower() == query.lower():
                return system_name
        
        # Starts with match
        for system_name in self.sde_loader.system_name_to_id.keys():
            if system_name.lower().startswith(query.lower()):
                return system_name
        
        return None
    
    def show_system_suggestions(self, query, field_name):
        """Show suggestions for system name that wasn't found"""
        if not self.sde_loader:
            return
        
        # Find close matches
        matches = []
        query_lower = query.lower()
        
        for system_name in self.sde_loader.system_name_to_id.keys():
            if query_lower in system_name.lower():
                matches.append(system_name)
                if len(matches) >= 10:
                    break
        
        if matches:
            text = f"⚠️ System '{query}' not found\n\n"
            text += f"Did you mean one of these?\n"
            for match in matches[:10]:
                region = self.sde_loader.get_system_region(match)
                text += f"  • {match} ({region})\n"
            text += f"\nTip: Start typing and use autocomplete dropdown"
        else:
            text = f"⚠️ No systems found matching '{query}'\n\n"
            text += "Tips:\n"
            text += "  • Check spelling\n"
            text += "  • Use autocomplete (start typing)\n"
            text += "  • Try well-known systems: Jita, Amarr, Dodixie"
        
        item = QListWidgetItem(text)
        item.setForeground(QColor('#ff6b6b'))
        self.routes_list.addItem(item)
    
    def find_hybrid_routes(self, origin, destination, connections, max_gates_per_leg=15):
        """Find hybrid routes combining stargates and wormholes"""
        routes = []
        
        # Get all wormhole entry points
        wormhole_systems = list(connections.keys())
        
        print(f"Finding routes from {origin} to {destination}")
        print(f"Checking {len(wormhole_systems)} wormhole systems...")
        
        # Check if multi-hop is enabled
        allow_multihop = True  # Multi-hop always enabled
        
        # Single-hop routes (1 wormhole)
        for entry_system in wormhole_systems:
            # Calculate path from origin to wormhole entry
            entry_path = self.sde_loader.find_path(origin, entry_system, max_jumps=max_gates_per_leg)
            
            if not entry_path:
                continue
            
            entry_gates = len(entry_path) - 1
            
            # For each system this wormhole connects to
            for exit_system, wh_data in connections[entry_system]:
                # Calculate path from wormhole exit to destination
                exit_path = self.sde_loader.find_path(exit_system, destination, max_jumps=max_gates_per_leg)
                
                if not exit_path:
                    continue
                
                exit_gates = len(exit_path) - 1
                total_gates = entry_gates + exit_gates
                
                # Calculate score
                score = self.calculate_route_score_single(entry_gates, exit_gates, wh_data)
                
                routes.append({
                    'origin': origin,
                    'destination': destination,
                    'entry_path': entry_path,
                    'hops': [{
                        'entry_system': entry_system,
                        'exit_system': exit_system,
                        'wormhole': wh_data
                    }],
                    'exit_path': exit_path,
                    'entry_gates': entry_gates,
                    'exit_gates': exit_gates,
                    'total_gates': total_gates,
                    'wormhole_count': 1,
                    'score': score
                })
        
        # Multi-hop routes (2 wormholes) - only if enabled
        if allow_multihop:
            print("Calculating multi-hop routes...")
            for entry_system in wormhole_systems:
                # Path from origin to first wormhole
                entry_path = self.sde_loader.find_path(origin, entry_system, max_jumps=max_gates_per_leg)
                
                if not entry_path:
                    continue
                
                entry_gates = len(entry_path) - 1
                
                # First wormhole jump
                for mid_system, wh_data_1 in connections[entry_system]:
                    # Check if mid system has another wormhole
                    if mid_system not in connections:
                        continue
                    
                    # Calculate distance between first and second wormhole
                    mid_path = self.sde_loader.find_path(mid_system, mid_system, max_jumps=0)
                    
                    # Second wormhole jump
                    for exit_system, wh_data_2 in connections[mid_system]:
                        # Avoid going back to entry
                        if exit_system == entry_system:
                            continue
                        
                        # MULTI-HOP ONLY FOR DIFFERENT WORMHOLE TYPES
                        # Skip if same type - just use single wormhole instead
                        if wh_data_1['holeType'] == wh_data_2['holeType']:
                            continue
                        
                        # Path from second wormhole exit to destination
                        exit_path = self.sde_loader.find_path(exit_system, destination, max_jumps=max_gates_per_leg)
                        
                        if not exit_path:
                            continue
                        
                        exit_gates = len(exit_path) - 1
                        total_gates = entry_gates + exit_gates
                        
                        # Don't show multi-hop if it makes route significantly worse (10+ gates)
                        # Calculate best single-hop alternative
                        direct_route_1 = self.sde_loader.find_path(mid_system, destination, max_jumps=max_gates_per_leg)
                        direct_route_1_gates = entry_gates + (len(direct_route_1) - 1 if direct_route_1 else 999)
                        
                        # If multi-hop is 10+ gates worse than single-hop, skip it
                        if total_gates > direct_route_1_gates + 10:
                            continue
                        
                        # Score multi-hop (bonus for avoiding gates)
                        score = self.calculate_route_score_multihop(entry_gates, exit_gates, wh_data_1, wh_data_2)
                        
                        routes.append({
                            'origin': origin,
                            'destination': destination,
                            'entry_path': entry_path,
                            'hops': [
                                {
                                    'entry_system': entry_system,
                                    'exit_system': mid_system,
                                    'wormhole': wh_data_1
                                },
                                {
                                    'entry_system': mid_system,
                                    'exit_system': exit_system,
                                    'wormhole': wh_data_2
                                }
                            ],
                            'exit_path': exit_path,
                            'entry_gates': entry_gates,
                            'exit_gates': exit_gates,
                            'total_gates': total_gates,
                            'wormhole_count': 2,
                            'score': score
                        })
        
        # Sort by score (lower is better)
        routes.sort(key=lambda r: r['score'])
        
        print(f"Found {len(routes)} routes ({sum(1 for r in routes if r['wormhole_count'] == 2)} multi-hop)")
        return routes
    
    def calculate_route_score_single(self, entry_gates, exit_gates, wh_data):
        """
        Simple 3-band scoring: Good / Iffy / Risky
        
        Bands:
        < 20: Good (Safe to use)
        20-40: Iffy (Proceed with caution)  
        > 40: Risky (Avoid unless emergency)
        """
        score = 0
        
        # Base: total gates
        total_gates = entry_gates + exit_gates
        score += total_gates
        
        # CRITICAL CONDITIONS = INSTANT RISKY (40+)
        if wh_data['lifeStatus'] == 'Critical':
            score += 60  # Immediate risk
        
        if '< 10%' in wh_data['massStatus']:
            score += 50  # Could collapse anytime
        
        # MODERATE CONDITIONS = IFFY TERRITORY (20+)
        if wh_data['lifeStatus'] == 'Destabilizing':
            score += 25  # Time pressure
        
        if '50% > 10%' in wh_data['massStatus']:
            score += 20  # Limited capacity
        
        # Long routes push into Iffy
        if total_gates > 15:
            score += 10
        
        # Bonuses for ideal conditions
        if total_gates < 10 and wh_data['lifeStatus'] == 'Fresh' and '100% > 50%' in wh_data['massStatus']:
            score -= 5  # Perfect route bonus
        
        return score
    
    def calculate_route_score_multihop(self, entry_gates, exit_gates, wh_data_1, wh_data_2):
        """
        Multi-hop scoring with HEAVY penalties for operational reality
        
        Multi-hop wormholes require:
        - Burning to WH in each intermediate system (time + danger)
        - Dealing with NPCs in each system
        - Multiple hole transitions (more points of failure)
        
        This makes multi-hop much less attractive than single-hop + gates
        """
        score = 0
        
        # Base: total gates
        total_gates = entry_gates + exit_gates
        score += total_gates
        
        # HEAVY MULTI-HOP PENALTY (was -5, now +30)
        # Represents: burn time, NPC danger, multiple transitions
        # This makes multi-hop only worth it for HUGE gate savings
        BURN_TIME_PENALTY = 15  # Each WH system requires burn time
        NPC_DANGER_PENALTY = 10  # Risk of NPCs in each system
        COMPLEXITY_PENALTY = 5   # More moving parts = more failure points
        
        score += (BURN_TIME_PENALTY + NPC_DANGER_PENALTY + COMPLEXITY_PENALTY)
        
        # Check both holes for critical conditions
        for wh_data in [wh_data_1, wh_data_2]:
            if wh_data['lifeStatus'] == 'Critical':
                score += 50  # Very risky
            elif wh_data['lifeStatus'] == 'Destabilizing':
                score += 20
            
            if '< 10%' in wh_data['massStatus']:
                score += 45  # Dangerous
            elif '50% > 10%' in wh_data['massStatus']:
                score += 18
        
        # Perfect chain bonus (reduced, was -10, now -5)
        # Even perfect multi-hop is still worse than single-hop due to burn time
        if all(wh['lifeStatus'] == 'Fresh' and '100% > 50%' in wh['massStatus'] 
               for wh in [wh_data_1, wh_data_2]):
            score -= 5
        
        return score
    
    def display_hybrid_route(self, route_data, rank):
        """Display a hybrid route with detailed information"""
        score = route_data['score']
        total_gates = route_data['total_gates']
        entry_gates = route_data['entry_gates']
        exit_gates = route_data['exit_gates']
        wormhole_count = route_data.get('wormhole_count', 1)
        hops = route_data.get('hops', [])
        
        # Count jumpbridges in entry and exit paths
        entry_jbs = self.count_jumpbridges_in_path(route_data.get('entry_path', []))
        exit_jbs = self.count_jumpbridges_in_path(route_data.get('exit_path', []))
        total_jbs = entry_jbs + exit_jbs
        
        # Calculate actual gate jumps (excluding JBs)
        entry_gates_only = entry_gates - entry_jbs
        exit_gates_only = exit_gates - exit_jbs
        total_gates_only = entry_gates_only + exit_gates_only
        
        # Fallback for old single-hop format
        if not hops and 'wormhole' in route_data:
            hops = [{
                'entry_system': route_data.get('entry_system'),
                'exit_system': route_data.get('exit_system'),
                'wormhole': route_data['wormhole']
            }]
        
        # Simple 3-band quality system
        if score < 20:
            quality = "[OK]"
            color = "#51cf66"
        elif score < 40:
            quality = "[CAUTION]"
            color = "#ffd43b"
        else:
            quality = "[WARNING]"
            color = "#ff6b6b"
        
        # Build display text
        if wormhole_count == 1:
            text = f"#{rank} {quality} Route (Score: {score:.1f})\n"
        else:
            text = f"#{rank} {quality} Multi-Hop Route (Score: {score:.1f}) [MULTI-HOP]\n"
        
        text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        # Entry leg
        text += f"► {route_data['origin']}\n"
        if entry_gates > 0:
            if entry_jbs > 0:
                text += f"    ↓ {entry_gates_only} stargate{'s' if entry_gates_only != 1 else ''}"
                text += f" + {entry_jbs} JB{'s' if entry_jbs != 1 else ''}\n"
            else:
                text += f"    ↓ {entry_gates} stargate{'s' if entry_gates != 1 else ''}\n"
        
        # Wormhole hops
        for i, hop in enumerate(hops):
            wh = hop['wormhole']
            text += f"● {hop['entry_system']}\n"
            text += f"    ↓ [{wh['holeType']} Wormhole"
            
            # Add warnings
            warnings = []
            if wh['lifeStatus'] == 'Critical':
                warnings.append("⚠️ CRITICAL")
            elif wh['lifeStatus'] == 'Destabilizing':
                warnings.append("⚠️ Destabilizing")
            
            if '< 10%' in wh['massStatus']:
                warnings.append("⚠️ LOW MASS")
            
            if warnings:
                text += f" - {' '.join(warnings)}"
            text += f"] ↓\n"
        
        # Exit system (last hop exit)
        if hops:
            text += f"● {hops[-1]['exit_system']}\n"
        
        # Exit leg
        if exit_gates > 0:
            if exit_jbs > 0:
                text += f"    ↓ {exit_gates_only} stargate{'s' if exit_gates_only != 1 else ''}"
                text += f" + {exit_jbs} JB{'s' if exit_jbs != 1 else ''}\n"
            else:
                text += f"    ↓ {exit_gates} stargate{'s' if exit_gates != 1 else ''}\n"
        text += f"► {route_data['destination']}\n"
        
        text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        # Show total with JB breakdown if applicable
        if total_jbs > 0:
            text += f"Total: {total_gates_only} gates + {total_jbs} JB{'s' if total_jbs != 1 else ''} + {wormhole_count} wormhole{'s' if wormhole_count != 1 else ''}"
        else:
            text += f"Total: {total_gates} gates + {wormhole_count} wormhole{'s' if wormhole_count != 1 else ''}"
        
        # Compare to direct route
        direct_path = self.sde_loader.find_path(route_data['origin'], route_data['destination'], max_jumps=50)
        if direct_path:
            direct_gates = len(direct_path) - 1
            savings = direct_gates - total_gates
            if savings > 0:
                text += f"\n💡 Saves {savings} gates vs direct route ({direct_gates} gates)"
        
        item = QListWidgetItem(text)
        item.setForeground(QColor(color))
        item.setData(Qt.ItemDataRole.UserRole, route_data)
        self.routes_list.addItem(item)
    
    def show_direct_route(self, origin, destination):
        """Show direct stargate route when no wormholes available"""
        path = self.sde_loader.find_path(origin, destination, max_jumps=50)
        
        if not path:
            item = QListWidgetItem(f"⚠️ No route found between {origin} and {destination}")
            item.setForeground(QColor('#ff6b6b'))
            self.routes_list.addItem(item)
            return
        
        gates = len(path) - 1
        
        text = f"⭐ Direct Stargate Route\n"
        text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"► {origin} → {destination}\n"
        text += f"    {gates} stargate jumps\n"
        text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"ℹ️ No drifter wormholes available\n"
        text += f"   Scan more systems to find shortcuts!"
        
        item = QListWidgetItem(text)
        item.setForeground(QColor('#8a8a8a'))
        self.routes_list.addItem(item)
    
    def calculate_routes(self):
        """Calculate routes from home regions to selected destination"""
        self.routes_list.clear()
        
        # Show "Calculating..." indicator
        calculating_item = QListWidgetItem("🔄 Calculating routes...")
        calculating_item.setForeground(QColor('#51cf66'))
        self.routes_list.addItem(calculating_item)
        
        # Process events so the indicator shows immediately
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
        
        dest_region = self.dest_region_combo.currentData()
        if not dest_region:
            self.routes_list.clear()
            return
        
        # Home regions
        home_regions = ['Scalding Pass', 'Wicked Creek', 'Insmother']
        
        # Build connection graph from active wormholes
        connections = self.build_connection_graph()
        
        # Clear the "Calculating..." indicator
        self.routes_list.clear()
        
        if not connections:
            item = QListWidgetItem("No active wormhole connections found. Scan some systems first!")
            item.setForeground(QColor('#8a8a8a'))
            self.routes_list.addItem(item)
            return
        
        # Find routes from each home region
        routes_found = False
        for home_region in home_regions:
            routes = self.find_routes(home_region, dest_region, connections)
            
            if routes:
                routes_found = True
                
                # Separate single-hop and multi-hop routes
                single_hop = [r for r in routes if len(r) == 2]
                multi_hop_raw = [r for r in routes if len(r) > 2]
                
                # FILTER MULTI-HOP: Only show different wormhole types
                multi_hop = []
                for route in multi_hop_raw:
                    # Check if all hops use different types
                    hop_types = []
                    is_valid = True
                    
                    for i in range(len(route) - 1):
                        system = route[i]
                        next_system = route[i + 1]
                        
                        # Find wormhole type for this hop
                        if system in connections:
                            for neighbor, wh_data in connections[system]:
                                if neighbor == next_system:
                                    hop_types.append(wh_data['holeType'])
                                    break
                    
                    # Check if any consecutive hops use the same type
                    for i in range(len(hop_types) - 1):
                        if hop_types[i] == hop_types[i + 1]:
                            is_valid = False
                            break
                    
                    # Only include if all hops use different types
                    if is_valid:
                        multi_hop.append(route)
                
                # Add home region header
                header_item = QListWidgetItem(f"► From {home_region}:")
                header_item.setForeground(QColor('#e8e8e8'))
                header_item.setFont(QFont('', 14, QFont.Weight.Bold))
                self.routes_list.addItem(header_item)
                
                # Add single-hop routes (direct connections)
                if single_hop:
                    for route in single_hop[:3]:
                        route_text = self.format_route_with_safety(route, connections)
                        item = QListWidgetItem(route_text)
                        item.setData(Qt.ItemDataRole.UserRole, route)
                        self.routes_list.addItem(item)
                
                # Add multi-hop routes under separate header
                if multi_hop:
                    multi_header = QListWidgetItem("  [MULTI-HOP] Multi-Hop Routes:")
                    multi_header.setForeground(QColor('#8a8a8a'))
                    multi_header.setFont(QFont('', 12, QFont.Weight.Bold))
                    self.routes_list.addItem(multi_header)
                    
                    for route in multi_hop[:3]:
                        route_text = self.format_multihop_route(route, connections)
                        item = QListWidgetItem(route_text)
                        item.setData(Qt.ItemDataRole.UserRole, route)
                        self.routes_list.addItem(item)
                
                # Add spacer
                self.routes_list.addItem(QListWidgetItem(""))
        
        if not routes_found:
            item = QListWidgetItem(f"No routes found to {dest_region} from home regions.")
            item.setForeground(QColor('#8a8a8a'))
            self.routes_list.addItem(item)
        
        # Update dropdown to show which regions have active wormholes
        self.update_routing_dropdown()
    
    def build_connection_graph(self):
        """Build bidirectional connection graph from active wormholes"""
        from datetime import datetime, timedelta
        
        connections = {}  # {system: [(connected_system, wormhole_data), ...]}
        
        # Get non-expired wormholes
        LIFETIME_HOURS = {'Fresh': 24, 'Destabilizing': 4, 'Critical': 0.25}
        now = datetime.now()
        
        active_wormholes = []
        for scan in self.scans:
            if scan['holeType'] == 'None':
                continue
            
            # Check if expired
            try:
                scanned_time = datetime.fromisoformat(scan['scannedAt'])
                lifetime = LIFETIME_HOURS.get(scan['lifeStatus'], 24)
                age = now - scanned_time
                if age > timedelta(hours=lifetime):
                    continue  # Expired
            except:
                pass
            
            active_wormholes.append(scan)
        
        # Build connections: Drifter wormholes connect to other holes of the SAME TYPE
        # Barbican → Barbican, Conflux → Conflux, etc.
        for i, scan in enumerate(active_wormholes):
            system_a = scan['system']
            hole_type_a = scan['holeType']
            
            if system_a not in connections:
                connections[system_a] = []
            
            # Connect to other systems with the SAME wormhole type
            for j, other_scan in enumerate(active_wormholes):
                if i == j:
                    continue
                
                system_b = other_scan['system']
                hole_type_b = other_scan['holeType']
                
                # Only connect if same wormhole type
                if hole_type_a == hole_type_b:
                    # Store the DESTINATION wormhole data for proper penalty calculation
                    connections[system_a].append((system_b, other_scan))
        
        return connections
    
    def find_routes(self, start_region, end_region, connections):
        """Find routes using BFS/Dijkstra depending on mode"""
        from collections import deque
        
        # Get all systems in start and end regions
        start_systems = list(JOVE_SYSTEMS.get(start_region, []))
        end_systems = list(JOVE_SYSTEMS.get(end_region, []))
        
        if not start_systems or not end_systems:
            return []
        
        routes = []
        
        # Single-hop only - no multi-hop wormhole chains
        # Multi-hop requires too much burn time and NPC danger
        for start_sys in start_systems:
            if start_sys not in connections:
                continue
            
            # Check direct connections from this start system
            for neighbor, wh_data in connections[start_sys]:
                # Is the neighbor in the destination region?
                neighbor_region = None
                for reg, systems in JOVE_SYSTEMS.items():
                    if neighbor in systems:
                        neighbor_region = reg
                        break
                
                if neighbor_region == end_region:
                    # Found single-hop route!
                    routes.append([start_sys, neighbor])
        
        # Sort routes by safety or distance
        if self.safest_mode:
            # Safest: prefer Fresh wormholes, avoid Critical/Destabilizing
            routes.sort(key=lambda r: (len(r), self.count_risky_holes(r, connections)))
        else:
            # Dodgy: just shortest, doesn't care about hole condition
            routes.sort(key=lambda r: len(r))
        
        return routes
    
    def count_risky_holes(self, route, connections):
        """Count critical/destabilizing holes in route (for safest path calculation)"""
        count = 0
        for i in range(len(route) - 1):
            system = route[i]
            next_system = route[i + 1]
            if system in connections:
                for neighbor, wh_data in connections[system]:
                    if neighbor == next_system:
                        if wh_data['lifeStatus'] in ['Critical', 'Destabilizing']:
                            count += 1
        return count
    
    def format_route(self, route, connections):
        """Format route for display with wormhole types"""
        if len(route) < 2:
            return " → ".join(route)
        
        # Build route with wormhole types
        route_parts = []
        for i in range(len(route)):
            system = route[i]
            route_parts.append(system)
            
            # Add wormhole type for the connection to next system
            if i < len(route) - 1:
                next_system = route[i + 1]
                wh_type = self.get_wormhole_type_for_hop(system, next_system, connections)
                if wh_type:
                    route_parts.append(f"[{wh_type}]")
        
        # Format with proper display
        if len(route) <= 4:
            return " → ".join(route_parts)
        else:
            # Show first 3 hops and last destination
            first_part = " → ".join(route_parts[:7])  # First 3 systems + 3 wormhole labels
            return f"{first_part} ... → {route[-1]}"
    
    def format_route_with_safety(self, route, connections):
        """Format single-hop route with safety indicators"""
        if len(route) < 2:
            return route[0]
        
        from_sys = route[0]
        to_sys = route[1]
        
        # Get wormhole data
        wh_type = None
        wh_life = None
        wh_mass = None
        
        if from_sys in connections:
            for neighbor, wh_data in connections[from_sys]:
                if neighbor == to_sys:
                    wh_type = wh_data['holeType']
                    wh_life = wh_data['lifeStatus']
                    wh_mass = wh_data['massStatus']
                    break
        
        # Build route string with safety indicators
        route_str = f"{from_sys} → [{wh_type}] → {to_sys}"
        
        # Add warning indicators for unsafe holes
        warnings = []
        if wh_life == 'Critical':
            warnings.append("⚠️ CRITICAL")
        elif wh_life == 'Destabilizing':
            warnings.append("⚠️ Destabilizing")
        
        if wh_mass and '< 10%' in wh_mass:
            warnings.append("⚠️ Low Mass")
        
        if warnings:
            route_str += f"  {' '.join(warnings)}"
        
        return route_str
    
    def format_multihop_route(self, route, connections):
        """Format multi-hop route with full path details including regions"""
        if len(route) < 2:
            return route[0]
        
        # Build detailed path with systems, wormholes, and regions
        path_segments = []
        has_warnings = False
        
        for i in range(len(route)):
            system = route[i]
            region = self.get_region_for_system(system)
            
            # Add system with region
            path_segments.append(f"{system} ({region})")
            
            # Add wormhole connection to next system
            if i < len(route) - 1:
                next_system = route[i + 1]
                
                # Get wormhole details
                wh_type = None
                wh_life = None
                
                if system in connections:
                    for neighbor, wh_data in connections[system]:
                        if neighbor == next_system:
                            wh_type = wh_data['holeType']
                            wh_life = wh_data['lifeStatus']
                            break
                
                # Format wormhole with safety indicator
                wh_str = f"[{wh_type}]"
                if wh_life in ['Critical', 'Destabilizing']:
                    wh_str = f"[{wh_type} ⚠️]"
                    has_warnings = True
                
                path_segments.append(f"→ {wh_str} →")
        
        # Join all segments
        route_str = "    " + " ".join(path_segments)
        
        # Add overall warning if route contains unsafe holes
        if has_warnings:
            route_str += "\n    ⚠️ WARNING: Route contains Critical or Destabilizing wormholes"
        
        return route_str
    
    def get_region_for_system(self, system):
        """Get the region a system belongs to"""
        for region, systems in JOVE_SYSTEMS.items():
            if system in systems:
                return region
        return "Unknown"
    
    def get_wormhole_type_for_hop(self, from_system, to_system, connections):
        """Get the wormhole type used for a connection"""
        if from_system in connections:
            for neighbor, wh_data in connections[from_system]:
                if neighbor == to_system:
                    return wh_data['holeType']
        return None
    
    def show_route_context_menu(self, position):
        """Show context menu for route actions"""
        item = self.routes_list.itemAt(position)
        if not item:
            return
        
        route_data = item.data(Qt.ItemDataRole.UserRole)
        if not route_data:
            return
        
        menu = QMenu()
        mark_crit = menu.addAction("⚠️ Mark Connection as Critical")
        mark_dead = menu.addAction("❌ Mark Connection as Dead")
        
        action = menu.exec(self.routes_list.mapToGlobal(position))
        
        if action == mark_crit:
            self.mark_connection_status(route_data, 'Critical')
        elif action == mark_dead:
            self.mark_connection_status(route_data, 'Dead')
    
    def mark_connection_status(self, route, status):
        """Mark connections in route as critical or dead"""
        # Update wormhole status for connections in this route
        for i in range(len(route) - 1):
            system = route[i]
            # Find wormhole in this system and update its life status
            for scan in self.scans:
                if scan['system'] == system and scan['holeType'] != 'None':
                    if status == 'Dead':
                        # Remove the wormhole
                        self.scans.remove(scan)
                    else:
                        # Mark as Critical
                        scan['lifeStatus'] = status
                    break
        
        self.save_scans()
        self.update_scans_list()
        self.calculate_routes()  # Refresh routes
    
    def update_routing_dropdown(self):
        """Update destination dropdown to show wormhole symbols for regions with active holes"""
        from datetime import datetime, timedelta
        
        # Get current selection
        current_selection = self.dest_region_combo.currentData()
        
        # Find regions with active (non-expired) wormholes
        LIFETIME_HOURS = {'Fresh': 24, 'Destabilizing': 4, 'Critical': 0.25}
        now = datetime.now()
        regions_with_holes = set()
        
        for scan in self.scans:
            if scan['holeType'] == 'None':
                continue
            
            # Check if expired
            try:
                scanned_time = datetime.fromisoformat(scan['scannedAt'])
                lifetime = LIFETIME_HOURS.get(scan['lifeStatus'], 24)
                age = now - scanned_time
                if age <= timedelta(hours=lifetime):
                    regions_with_holes.add(scan['region'])
            except:
                regions_with_holes.add(scan['region'])
        
        # Rebuild dropdown
        self.dest_region_combo.blockSignals(True)  # Prevent triggering calculate_routes
        self.dest_region_combo.clear()
        self.dest_region_combo.addItem('Select Region')
        
        for region in sorted(JOVE_SYSTEMS.keys()):
            if region in regions_with_holes:
                display_text = f"● {region}"
            else:
                display_text = region
            self.dest_region_combo.addItem(display_text, region)
        
        # Restore selection
        if current_selection:
            for i in range(self.dest_region_combo.count()):
                if self.dest_region_combo.itemData(i) == current_selection:
                    self.dest_region_combo.setCurrentIndex(i)
                    break
        
        self.dest_region_combo.blockSignals(False)




    def create_mass_tab(self):
        """Create the mass calculator tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_label = QLabel('[MASS] Fleet Mass Calculator')
        header_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 900;
            color: #e8e8e8;
            padding: 10px 0;
        """)
        layout.addWidget(header_label)
        
        # Ship database info
        ship_count = len(self.sde_loader.ship_masses) if self.sde_loader and hasattr(self.sde_loader, 'ship_masses') else 0
        info_label = QLabel(f'📊 Ship Database: {ship_count:,} subcapital ships available')
        info_label.setStyleSheet("""
            font-size: 12px;
            color: #8a8a8a;
            padding: 0 0 10px 0;
        """)
        layout.addWidget(info_label)
        
        # Check if SDE data is loaded AND has ship masses
        if not self.sde_loader or not hasattr(self.sde_loader, 'ship_masses') or not self.sde_loader.ship_masses:
            warning_label = QLabel("⚠️ EVE SDE data not loaded\n\nRun 'python setup_sde.py' to enable mass calculations")
            warning_label.setStyleSheet("""
                font-size: 16px;
                color: #ff6b6b;
                padding: 40px;
                background: #16161d;
                border: 2px solid #ff6b6b;
                border-radius: 2px;
            """)
            warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(warning_label, 1)
            return widget
        
        # Fleet composition section
        fleet_group = QGroupBox("Fleet Composition")
        fleet_group.setStyleSheet("""
            QGroupBox {
                background: #0e0e14;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 20px;
                font-weight: bold;
                font-size: 14px;
                color: #e8e8e8;
            }
        """)
        fleet_layout = QVBoxLayout(fleet_group)
        
        # Ship type selector and quantity
        add_ship_layout = QHBoxLayout()
        
        # Bulk import button
        bulk_import_btn = QPushButton("BULK IMPORT FLEET")
        bulk_import_btn.clicked.connect(self.show_fleet_bulk_import)
        bulk_import_btn.setStyleSheet("""
            QPushButton {
                background: #16161d;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 10px 20px;
                color: #e8e8e8;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1e1e28;
                border: 1px solid #4a4a55;
            }
            QPushButton:pressed {
                background: #0e0e14;
            }
        """)
        add_ship_layout.addWidget(bulk_import_btn)
        add_ship_layout.addStretch()
        
        fleet_layout.addLayout(add_ship_layout)
        
        # Manual add section
        manual_add_layout = QHBoxLayout()
        
        self.ship_type_combo = QComboBox()
        self.ship_type_combo.addItem("Select Ship Type")
        
        # Add ALL subcapital ships from SDE (sorted alphabetically)
        all_ships = sorted(self.sde_loader.ship_masses.keys())
        for ship in all_ships:
            self.ship_type_combo.addItem(ship, ship)
        
        # Make searchable
        self.ship_type_combo.setEditable(True)
        self.ship_type_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        # Add completer for search
        from PyQt6.QtWidgets import QCompleter
        completer = QCompleter(all_ships)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.ship_type_combo.setCompleter(completer)
        
        self.ship_quantity_input = QLineEdit()
        self.ship_quantity_input.setPlaceholderText("Quantity")
        self.ship_quantity_input.setMaximumWidth(100)
        
        add_ship_btn = QPushButton("ADD SHIPS")
        add_ship_btn.clicked.connect(self.add_ships_to_fleet)
        add_ship_btn.setStyleSheet("""
            QPushButton {
                background: #16161d;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 10px 20px;
                color: #e8e8e8;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1e1e28;
                border: 1px solid #4a4a55;
            }
            QPushButton:pressed {
                background: #0e0e14;
            }
        """)
        
        manual_add_layout.addWidget(QLabel("Manual Add:"))
        manual_add_layout.addWidget(self.ship_type_combo, 1)
        manual_add_layout.addWidget(QLabel("Qty:"))
        manual_add_layout.addWidget(self.ship_quantity_input)
        manual_add_layout.addWidget(add_ship_btn)
        
        fleet_layout.addLayout(manual_add_layout)
        
        # Current fleet list
        self.fleet_list = QListWidget()
        self.fleet_list.setStyleSheet("""
            QListWidget {
                background: #0a0a0f;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 10px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #16161d;
            }
        """)
        self.fleet_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.fleet_list.customContextMenuRequested.connect(self.show_fleet_context_menu)
        fleet_layout.addWidget(self.fleet_list)
        
        # Clear fleet button
        clear_fleet_btn = QPushButton("🗑️ Clear Fleet")
        clear_fleet_btn.clicked.connect(self.clear_fleet)
        clear_fleet_btn.setStyleSheet("""
            QPushButton {
                background: #ff6b6b;
                border: none;
                border-radius: 2px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #ff5252;
            }
        """)
        fleet_layout.addWidget(clear_fleet_btn)
        
        layout.addWidget(fleet_group)
        
        # Mass analysis section
        analysis_group = QGroupBox("Mass Analysis")
        analysis_group.setStyleSheet("""
            QGroupBox {
                background: #0e0e14;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 20px;
                font-weight: bold;
                font-size: 14px;
                color: #e8e8e8;
            }
        """)
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.mass_analysis_label = QLabel("Add ships to see mass analysis")
        self.mass_analysis_label.setStyleSheet("""
            font-size: 14px;
            color: #8a8a8a;
            padding: 20px;
        """)
        self.mass_analysis_label.setWordWrap(True)
        analysis_layout.addWidget(self.mass_analysis_label)
        
        layout.addWidget(analysis_group)
        
        # Initialize fleet composition
        self.fleet_composition = {}  # {ship_type: quantity}
        
        return widget
    
    def add_ships_to_fleet(self):
        """Add ships to fleet composition"""
        ship_type = self.ship_type_combo.currentData()
        if not ship_type:
            return
        
        try:
            quantity = int(self.ship_quantity_input.text())
            if quantity <= 0:
                return
        except ValueError:
            return
        
        # Add to fleet composition
        if ship_type in self.fleet_composition:
            self.fleet_composition[ship_type] += quantity
        else:
            self.fleet_composition[ship_type] = quantity
        
        # Update display
        self.update_fleet_display()
        
        # Clear input
        self.ship_quantity_input.clear()
    
    def update_fleet_display(self):
        """Update fleet composition display and mass analysis"""
        self.fleet_list.clear()
        
        if not self.fleet_composition:
            self.mass_analysis_label.setText("Add ships to see mass analysis")
            return
        
        # Calculate total mass
        total_mass = 0
        total_ships = 0
        
        for ship_type, quantity in sorted(self.fleet_composition.items()):
            ship_mass = self.sde_loader.ship_masses.get(ship_type, 0)
            total_ship_mass = ship_mass * quantity
            total_mass += total_ship_mass
            total_ships += quantity
            
            item = QListWidgetItem(f"{quantity}x {ship_type} ({ship_mass:,} kg each) = {total_ship_mass:,} kg")
            self.fleet_list.addItem(item)
        
        # Add totals
        self.fleet_list.addItem(QListWidgetItem(""))
        total_item = QListWidgetItem(f"📊 Total: {total_ships} ships, {total_mass:,} kg")
        font = total_item.font()
        font.setBold(True)
        total_item.setFont(font)
        total_item.setForeground(QColor('#e8e8e8'))
        self.fleet_list.addItem(total_item)
        
        # Update mass analysis
        self.update_mass_analysis(total_mass)
    
    def update_mass_analysis(self, total_mass):
        """Update mass analysis with wormhole compatibility"""
        from eve_sde_loader import WORMHOLE_MASS_LIMITS
        
        analysis = f"<b style='color: #e8e8e8; font-size: 16px;'>Total Fleet Mass: {total_mass:,} kg</b><br><br>"
        
        # Check if any individual ship exceeds the individual jump limit
        individual_limit = 375_000_000  # 375M kg per ship
        heavy_ships = []
        for ship_type, quantity in self.fleet_composition.items():
            ship_mass = self.sde_loader.ship_masses.get(ship_type, 0)
            if ship_mass > individual_limit:
                heavy_ships.append(f"{ship_type} ({ship_mass/1_000_000:.1f}M kg)")
        
        if heavy_ships:
            analysis += "<b style='color: #ff6b6b;'>⚠️ WARNING: Ships too heavy for drifter holes:</b><br>"
            for ship in heavy_ships:
                analysis += f"  • {ship}<br>"
            analysis += "<br>"
        
        analysis += "<b>Wormhole Compatibility:</b><br><br>"
        
        # Check each wormhole life stage
        for stage in ['Fresh', 'Destabilizing', 'Critical']:
            limits = WORMHOLE_MASS_LIMITS[stage]
            total_capacity = limits['total_mass']
            
            # If any ships are too heavy individually, mark as incompatible
            if heavy_ships:
                status = "❌ SHIPS TOO HEAVY (individual limit: 375M kg)"
                color = "#ff6b6b"
            # Check if fleet exceeds total capacity
            elif total_mass > total_capacity:
                status = "❌ EXCEEDS TOTAL CAPACITY"
                color = "#ff6b6b"
            # Check if close to limit
            elif total_mass > total_capacity * 0.8:
                status = f"⚠️ RISKY ({total_mass / total_capacity * 100:.0f}% of capacity)"
                color = "#ffa500"
            else:
                jumps_possible = int(total_capacity / total_mass)
                status = f"✓ OK ({jumps_possible} full fleet jumps possible)"
                color = "#51cf66"
            
            analysis += f"<b style='color: {color};'>{stage}:</b> {status}<br>"
            analysis += f"  Capacity: {total_capacity/1_000_000:.0f}M kg total<br><br>"
        
        analysis += "<br><b>Notes:</b><br>"
        analysis += "• Individual ship limit: 375M kg (no battleships, no capitals)<br>"
        analysis += "• Total capacity: 750M kg fresh, decreases as destabilizes<br>"
        analysis += "• Multiple ships can jump together if under total capacity"
        
        self.mass_analysis_label.setText(analysis)
    
    def clear_fleet(self):
        """Clear fleet composition"""
        self.fleet_composition.clear()
        self.update_fleet_display()
    
    def show_fleet_bulk_import(self):
        """Show bulk import dialog for fleet composition"""
        try:
            dialog = FleetBulkImportDialog(self)
            result = dialog.exec()
            if result == QDialog.DialogCode.Accepted:
                import_text = dialog.get_import_text()
                if import_text:
                    self.process_fleet_bulk_import(import_text)
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def process_fleet_bulk_import(self, import_text):
        """Parse and import fleet composition from EVE fleet window"""
        import re
        from security_utils import SecurityValidator
        
        lines = import_text.strip().split('\n')
        ships_added = 0
        errors = []
        
        # Ship name extraction patterns
        for line in lines:
            try:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
            
                # Clean up common EVE fleet formatting
                line = re.sub(r'\s+', ' ', line)  # Normalize whitespace
            
                ship_type = None
                quantity = 1  # Default to 1 if no quantity found
            
                # Pattern 1: EVE Fleet format - ship name comes BETWEEN system and role
                # Format: "CharacterName SystemName ShipName ShipClass RoleKeyword..."
                # Example: "Ultra PUIG-F Manticore Stealth Bomber Fleet Commander"
                #                         ^^^^^^^^^ Extract this
            
                # Common ship class keywords (appear after ship name)
                ship_class_keywords = [
                    'Frigate', 'Destroyer', 'Cruiser', 'Battlecruiser', 'Battleship',
                    'Stealth Bomber', 'Force Recon', 'Heavy Assault', 'Heavy Interdictor',
                    'Logistics', 'Recon', 'Command', 'Covert Ops', 'Electronic Attack',
                    'Assault Frigate', 'Strategic Cruiser', 'Black Ops', 'Marauder',
                    'Carrier', 'Dreadnought', 'Force Auxiliary', 'Supercarrier', 'Titan',
                    'Interceptor', 'Combat Interceptor', 'Fleet Interceptor'
                ]
            
                # Common role keywords (appear after ship class)
                role_keywords = ['Squad', 'Wing', 'Fleet', 'Member', 'Commander', 'Leader', 'Boss']
            
                # SECURITY: Limit line length
                if len(line) > SecurityValidator.MAX_INPUT_TEXT_LENGTH:
                    continue
            
                # Strategy: Find ship class keyword, extract word before it
                for ship_class in ship_class_keywords:
                    idx = line.find(ship_class)
                    if idx > 0:
                        # Found ship class - ship name is the word immediately before it
                        before_class = line[:idx].strip()
                        words = before_class.split()
                    
                        if words:
                            # Last word before class is the ship name
                            ship_type = words[-1].strip()
                        
                            # SECURITY: Validate length
                            if len(ship_type) > 50 or len(ship_type) < 3:
                                ship_type = None
                                continue
                        
                            # SECURITY: Remove dangerous chars
                            ship_type = re.sub(r'[^\w\s\-]', '', ship_type).strip()
                        
                            # SECURITY: Validate format
                            if ship_type and re.match(r'^[A-Za-z][A-Za-z0-9\s\-]*$', ship_type):
                                break  # Found valid ship name
                            else:
                                ship_type = None
            
                # If no ship class found, try finding role keywords (less reliable)
                if not ship_type:
                    found_keyword_at = -1
                    for keyword in role_keywords:
                        idx = line.find(keyword)
                        if idx > 0 and idx < 200:  # SECURITY: Limit
                            if found_keyword_at == -1 or idx < found_keyword_at:
                                found_keyword_at = idx
                
                    if found_keyword_at > 0:
                        # Extract words before role keyword
                        before_role = line[:found_keyword_at].strip()
                        words = before_role.split()
                    
                        # Try last 1-2 words as ship name
                        if len(words) >= 2:
                            ship_type = words[-2] + ' ' + words[-1]
                        elif len(words) == 1:
                            ship_type = words[-1]
                    
                        if ship_type:
                            # SECURITY: Sanitize
                            ship_type = re.sub(r'[\d\s\-]+$', '', ship_type).strip()
                            ship_type = re.sub(r'[^\w\s\-]', '', ship_type).strip()
                        
                            # SECURITY: Validate
                            if not ship_type or len(ship_type) < 3 or len(ship_type) > 50:
                                ship_type = None
                            elif not re.match(r'^[A-Za-z][A-Za-z0-9\s\-]*$', ship_type):
                                ship_type = None
            
                # Pattern 2: "Hound	Stealth Bomber	9" (Fleet Composition tab with tabs)
                if not ship_type:
                    tab_match = re.search(r'^([A-Za-z\s-]+?)\t+([A-Za-z\s]+?)\t+(\d+)\s*$', line)
                    if tab_match:
                        ship_type = tab_match.group(1).strip()
                        quantity = int(tab_match.group(3))
            
                # Pattern 3: "Hound  Stealth Bomber  9" (with spaces)
                if not ship_type:
                    space_match = re.search(r'^([A-Za-z\s-]+?)\s{2,}([A-Za-z\s]+?)\s{2,}(\d+)\s*$', line)
                    if space_match:
                        ship_type = space_match.group(1).strip()
                        quantity = int(space_match.group(3))
            
                # Pattern 4: "Redeemer 10" (ship name and number)
                if not ship_type:
                    simple_match = re.search(r'^([A-Za-z\s-]+?)\s+(\d+)\s*$', line)
                    if simple_match:
                        ship_type = simple_match.group(1).strip()
                        quantity = int(simple_match.group(2))
            
                # Pattern 5: Just ship name "Redeemer" (quantity defaults to 1)
                if not ship_type:
                    name_only = re.match(r'^([A-Z][A-Za-z\s-]+?)$', line)
                    if name_only:
                        ship_type = name_only.group(1).strip()
                        quantity = 1
            
                if ship_type:
                    # Validate ship name with security utils
                    ship_type = SecurityValidator.truncate_string(ship_type, 100)
                
                    # Clean up ship name
                    ship_type = ship_type.strip()
                
                    # Look up ship mass
                    if ship_type in self.sde_loader.ship_masses:
                        if ship_type in self.fleet_composition:
                            self.fleet_composition[ship_type] += quantity
                        else:
                            self.fleet_composition[ship_type] = quantity
                        ships_added += quantity
                    else:
                        # Try case-insensitive match
                        matched = False
                        ship_lower = ship_type.lower()
                        for known_ship in self.sde_loader.ship_masses.keys():
                            if known_ship.lower() == ship_lower:
                                ship_type = known_ship  # Use correct case
                                if ship_type in self.fleet_composition:
                                    self.fleet_composition[ship_type] += quantity
                                else:
                                    self.fleet_composition[ship_type] = quantity
                                ships_added += quantity
                                matched = True
                                break
                    
                        if not matched:
                            errors.append(f"Unknown ship: {ship_type}")
            except Exception as e:
                # Skip problematic lines
                errors.append(f"Parse error: {str(e)[:50]}")
                print(f"DEBUG: Parse error on line: {e}")
                continue
        
        # Update display
        self.update_fleet_display()
        
        # Show result message
        if ships_added > 0:
            message = f"Successfully imported {ships_added} ship(s)"
            if errors:
                message += f"\n\nWarnings:\n" + "\n".join(errors[:10])
                if len(errors) > 10:
                    message += f"\n... and {len(errors) - 10} more"
            QMessageBox.information(self, 'Fleet Import Complete', message)
        else:
            message = "No ships were imported."
            if errors:
                message += f"\n\nErrors:\n" + "\n".join(errors[:10])
            QMessageBox.warning(self, 'Fleet Import Failed', message)
    
    def show_fleet_context_menu(self, position):
        """Show context menu for fleet list"""
        item = self.fleet_list.itemAt(position)
        if not item:
            return
        
        # Extract ship type from item text
        text = item.text()
        if 'x' not in text or '=' in text and 'Total' in text:
            return
        
        ship_type = text.split('x')[1].split('(')[0].strip()
        
        menu = QMenu()
        remove_action = menu.addAction(f"Remove {ship_type}")
        
        action = menu.exec(self.fleet_list.mapToGlobal(position))
        
        if action == remove_action:
            if ship_type in self.fleet_composition:
                del self.fleet_composition[ship_type]
                self.update_fleet_display()


class ExportDialog(QDialog):
    def __init__(self, scans, parent=None):
        super().__init__(parent)
        self.scans = scans
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Discord Export')
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout(self)
        
        label = QLabel('Discord Intel Report')
        label.setStyleSheet('font-size: 18px; font-weight: bold; color: #e8e8e8;')
        layout.addWidget(label)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background: #16161d;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 15px;
                color: #e8e8e8;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        
        report = self.generate_discord_report()
        self.text_edit.setPlainText(report)
        layout.addWidget(self.text_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.copy_and_close)
        layout.addWidget(button_box)

    def generate_discord_report(self):
        timestamp = int(datetime.now().timestamp())
        
        # Group by region, then by system
        by_region = {}
        for scan in self.scans:
            region = scan['region']
            system = scan['system']
            if region not in by_region:
                by_region[region] = {}
            if system not in by_region[region]:
                by_region[region][system] = []
            by_region[region][system].append(scan)
        
        # Count unique systems scanned
        total_systems = sum(len(systems) for systems in by_region.values())
        
        report = f'## Scan was completed <t:{timestamp}:R>\n'
        report += f'# Systems Scanned: {total_systems}\n'
        
        for region in sorted(by_region.keys()):
            systems_dict = by_region[region]
            total_in_region = len(JOVE_SYSTEMS[region])
            scanned_in_region = len(systems_dict)
            is_complete = scanned_in_region == total_in_region
            status = '[COMPLETE] Scan' if is_complete else '[INCOMPLETE] Scan'
            
            # Check if there are any actual holes in this region
            has_holes = False
            for system_scans in systems_dict.values():
                if any(s['holeType'] != 'None' for s in system_scans):
                    has_holes = True
                    break
            
            if has_holes:
                report += f'## {region} (Scanned: {scanned_in_region}/{total_in_region}) {status}\n'
                
                for system in sorted(systems_dict.keys()):
                    system_scans = systems_dict[system]
                    holes_in_system = [s for s in system_scans if s['holeType'] != 'None']
                    
                    if holes_in_system:
                        for scan in sorted(holes_in_system, key=lambda s: s['holeType']):
                            role_mention = f"***⁨<@&{scan['roleId']}>⁩***" if scan['roleId'] else '***Drifter Hole***'
                            report += f"**{system}** => {role_mention} ({scan['holeType']}), **Life:** *{scan['lifeStatus']}*, **Mass:** *{scan['massStatus']}*\n"
        
        return report

    def copy_and_close(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())
        QMessageBox.information(self, 'Copied', 'Discord report copied to clipboard!')
        self.accept()


class BulkImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Bulk Import Scans')
        self.setGeometry(200, 200, 900, 700)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            '<b>Bulk Import Formats:</b><br><br>'
            '<b>1. Discord Export Format:</b><br>'
            'Paste exported Discord text directly (including ** and role mentions)<br><br>'
            '<b>2. CSV Format:</b><br>'
            'REGION,SYSTEM,TYPE,LIFE,MASS,ROLE_ID<br>'
            'Example: Cache,M-CNUD,Vidette,Fresh,100% > 50%,1326789530983858256<br><br>'
            '<i>Lines starting with # are ignored. Empty lines are skipped.</i>'
        )
        instructions.setStyleSheet("""
            color: #e8e8e8;
            background: #0e0e14;
            padding: 15px;
            border-radius: 2px;
            border: 1px solid #2a2a35;
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Text area
        text_label = QLabel('Paste scan data below:')
        text_label.setStyleSheet('font-weight: bold; color: #e8e8e8; margin-top: 10px;')
        layout.addWidget(text_label)
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(
            'Paste Discord export or CSV data here...\n\n'
            'Examples:\n'
            '**M-CNUD** => ***⁨<@&1234567890>⁩*** (Vidette), **Life:** *Fresh*, **Mass:** *100% > 50%*\n'
            'Cache,I6-SYN,Sentinel,Destabilizing,50% > 10%,1234567890\n'
            '# This is a comment\n'
            'Branch,P7Z-R3,Conflux,Critical,< 10%'
        )
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background: #16161d;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 15px;
                color: #e8e8e8;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.text_edit)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_import_text(self):
        return self.text_edit.toPlainText()


class FleetBulkImportDialog(QDialog):
    """Dialog for bulk importing fleet composition from EVE"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Bulk Import Fleet Composition')
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            '<b>Import fleet composition from EVE Online:</b><br><br>'
            '1. Open Fleet window (Alt+F)<br>'
            '2. Click "Fleet composition" OR "Fleet Summary" tab<br>'
            '3. Select and copy the ship list (Ctrl+A, Ctrl+C)<br>'
            '4. Paste here and click Import'
        )
        instructions.setStyleSheet("""
            color: #e8e8e8;
            background: #16161d;
            padding: 15px;
            border-radius: 2px;
            border: 1px solid #2a2a35;
        """)
        layout.addWidget(instructions)
        
        # Text edit for pasting
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(
            'Paste fleet composition here...\n\n'
            'Supported formats:\n'
            '• Fleet Composition: "Hound  Stealth Bomber  9"\n'
            '• Fleet Summary with ship icons\n'
            '• Ship type followed by number'
        )
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background: #16161d;
                border: 1px solid #2a2a35;
                border-radius: 2px;
                padding: 15px;
                color: #e8e8e8;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.text_edit)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_import_text(self):
        return self.text_edit.toPlainText()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    tracker = DrifterTracker()
    tracker.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
