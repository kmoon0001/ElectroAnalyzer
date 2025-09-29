"""
Polished Modern Main Window - Your exact layout specification with all enhancements.
"""
import os
import sys
import requests
import urllib.parse
import webbrowser
import jwt

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QStatusBar,
    QMenuBar, QFileDialog, QTextEdit, QLabel, QPushButton, QComboBox,
    QFrame, QProgressBar, QMessageBox, QSplitter, QDialog, QTextBrowser
)
import os
import sys
import requests
import urllib.parse
import webbrowser
import jwt

from PyQt6.QtCore import Qt, QThread, QUrl, QTimer, pyqtSignal
from PyQt6.QtGui import QTextDocument, QFont, QKeySequence, QAction, QIcon, QPixmap

# Import new modern components
from .widgets.modern_card import ModernCard, ComplianceCard
from .widgets.medical_theme import medical_theme
from .widgets.quadrant_widget import QuadrantWidget
from .widgets.responsive_layout import ResponsiveWidget, VirtualScrollArea
from .widgets.micro_interactions import AnimatedButton, FadeInWidget, LoadingSpinner

# Import existing components
from .widgets.chat_input import ChatInput

from .dialogs.rubric_manager_dialog import RubricManagerDialog
from .dialogs.performance_settings_dialog import PerformanceSettingsDialog
from .dialogs.help_dialog import HelpDialog
from .dialogs.synergy_session_dialog import SynergySessionDialog
from .dialogs.review_dashboard_dialog import ReviewDashboardDialog

from .workers.analysis_starter_worker import AnalysisStarterWorker
from .workers.analysis_worker import AnalysisWorker
from .workers.ai_loader_worker import AILoaderWorker
from .workers.dashboard_worker import DashboardWorker
from .workers.review_worker import ReviewRequestWorker

from .widgets.dashboard_widget import DashboardWidget
from .widgets.performance_status_widget import PerformanceStatusWidget

from ..config import get_settings

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


        layout = QVBoxLayout(self)

        # Header
        header = QLabel("📄 Clinical Document Content")
        header.setStyleSheet("""
            QLabel {
                color: #4a90e2;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: white;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header)

        # Document display
        self.document_display = QTextEdit()
        self.document_display.setPlainText(document_content)
        self.document_display.setReadOnly(True)
        self.document_display.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 2px solid #4a90e2;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.document_display)

        # Close button
        close_btn = QPushButton("✖️ Close Preview")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:focus {
                border: 2px solid #4a90e2;
            }
        """)
        layout.addWidget(close_btn)

class ReportViewDialog(QDialog):
    """Popup dialog for full compliance report view."""

    def __init__(self, report_content: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📊 Compliance Analysis Report")
        self.setGeometry(150, 150, 1000, 700)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f8ff;
                color: black;
            }
        """)

        layout = QVBoxLayout(self)

import os
import sys
import requests
import urllib.parse
import webbrowser
import jwt

from PyQt6.QtCore import Qt, QThread, QUrl, QTimer, pyqtSignal
from PyQt6.QtGui import QTextDocument, QFont, QKeySequence, QAction, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextBrowser, QDialog
)

# Example Main Window Class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.access_token = None
        self.username = None
        self.user_role = "therapist"  # Default role
        self.is_admin = False
        self._current_file_path = None
        self._current_folder_path = None
        self._current_report_id = None  # To store the ID of the latest report
        self.compliance_service = None
        self.worker_thread = None
        self.worker = None

        self.setWindowTitle("Therapy Compliance Analyzer")
        self.setGeometry(100, 100, 1000, 700)

        # Main UI setup can go here...

    def show_report(self, report_content: str):
        dialog = ReportViewDialog(report_content, parent=self)
        dialog.exec()

# Dialog class for Detailed Compliance Report Display
class ReportViewDialog(QDialog):
    def __init__(self, report_content: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 Detailed Compliance Analysis Report")
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        # Header
        header = QLabel("📋 Detailed Compliance Analysis Report")
        header.setStyleSheet("""
            QLabel {
                color: #28a745;
                font-size: 18px;
                font-weight: bold;
                padding: 12px;
                background-color: white;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header)

        # Report display
        self.report_display = QTextBrowser()
        self.report_display.setHtml(report_content)
        self.report_display.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                border: 2px solid #28a745;
                border-radius: 8px;
                padding: 20px;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(self.report_display)

        # Button row
        button_layout = QHBoxLayout()

        # Export button
        export_btn = QPushButton("💾 Export Report")
        export_btn.clicked.connect(self.export_report)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:focus {
                border: 2px solid #63a4ff;
            }
        """)
        button_layout.addWidget(export_btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def export_report(self):
        # Example export functionality (save html report to file)
        from PyQt6.QtWidgets import QFileDialog, QMessageBox

        filename, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "HTML Files (*.html);;All Files (*)")
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.report_display.toHtml())
                QMessageBox.information(self, "Export Successful", f"Report saved to {filename}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", f"Could not save report: {str(e)}")


        # Close button
        close_btn = QPushButton("✖️ Close Report")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:focus {
                border: 2px solid #4a90e2;
            }
        """)

        button_layout.addWidget(export_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

    def export_report(self):
        """Export report to file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "💾 Export Compliance Report",
            "compliance_report.html",
            "HTML Files (*.html);;PDF Files (*.pdf);;All Files (*)"
        )

from PyQt6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget,
    QMessageBox, QFileDialog, QMainWindow
)
from PyQt6.QtGui import QFont
import jwt

class ReportViewDialog(QDialog):
    # ... existing __init__ and other methods ...

    def export_report(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "HTML Files (*.html);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.report_display.toHtml())
                QMessageBox.information(self, "Export Success", f"✅ Report exported to:\n{file_name}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"❌ Could not export report:\n{e}")

class SectionFrame(QFrame):
    """A QFrame with a subtle border for a sophisticated look."""
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("SectionFrame")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        if title:
            title_label = QLabel(title)
            title_font = QFont()
            title_font.setPointSize(11)
            title_font.setBold(True)
            title_label.setFont(title_font)
            title_label.setStyleSheet("color: #4a90e2; margin-bottom: 4px; border: none;")
            layout.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.content_layout)

    def add_content(self, widget: QWidget):
        """Adds a widget to the content area of the frame."""
        self.content_layout.addWidget(widget)

    def add_layout(self, layout: QHBoxLayout):
        self.content_layout.addLayout(layout)

class MainWindow(QMainWindow):
    # ... existing __init__ and other methods ...

    def set_user_session(self, access_token: str):
        """Sets the user's session token and decodes it to get role information."""
        self.access_token = access_token
        try:
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            self.user_role = decoded_token.get("role", "therapist")
            self.username = decoded_token.get("sub", "Unknown User")
        except jwt.PyJWTError:
            self.user_role = "therapist"  # Default on error
            self.username = "Unknown User"

        self.setup_menu_bar()

    def start(self):
        """Start the application with modern loading experience."""
        self.load_ai_models()
        self.load_main_ui()
        self.show()


class ModernMainWindow(QMainWindow):
    """Modern main window with your exact layout."""

    def __init__(self):
        super().__init__()
        print("!!! JULES DEBUG: EXECUTING LATEST POLISHED VERSION !!!")
        print("🎨 Initializing working modern UI...")
        self._current_file_path = None
        self._current_document_content = ""
        self._current_report_content = ""
        self.document_preview_dialog = None
        self.report_view_dialog = None
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        # Window setup
        self.setWindowTitle("🏥 Therapy Compliance Analyzer - Polished Edition")
        self.setGeometry(100, 100, 1400, 900)

        # Apply PyCharm gray with medical accents
        self.setStyleSheet("""
            QMainWindow {
                background-color: #3c3f41; /* PyCharm gray background */
                color: #bbbbbb; /* Light text for dark background */
            }
            QFrame#SectionFrame {
                background-color: #2b2b2b;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                margin: 0px;
            }
            QMenuBar {
                background-color: #ffffff;
                color: #1a1a1a;
                border-bottom: 1px solid #4a90e2; /* Medical blue border */
                padding: 4px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:hover {
                background-color: #e6f3ff;
            }
            QMenuBar::item:selected {
                background-color: #4a90e2; /* Medical blue */
                color: white;
            }
            QStatusBar {
                background-color: #ffffff;
                color: #666666; /* Medical grey */
                border-top: 1px solid #4a90e2;
            }
        """)

        # Setup components
        self.setup_menu_bar()
        self.setup_status_bar()
        self.create_main_layout()

        print("✅ Working UI created successfully!")

    def setup_menu_bar(self):
from PyQt6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget,
    QMessageBox, QFileDialog, QMainWindow
)
from PyQt6.QtGui import QFont
import jwt

class ReportViewDialog(QDialog):
    # ... existing __init__ and other methods ...

    def export_report(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "HTML Files (*.html);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.report_display.toHtml())
                QMessageBox.information(self, "Export Success", f"✅ Report exported to:\n{file_name}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"❌ Could not export report:\n{e}")

class SectionFrame(QFrame):
    """A QFrame with a subtle border for a sophisticated look."""
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("SectionFrame")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        if title:
            title_label = QLabel(title)
            title_font = QFont()
            title_font.setPointSize(11)
            title_font.setBold(True)
            title_label.setFont(title_font)
            title_label.setStyleSheet("color: #4a90e2; margin-bottom: 4px; border: none;")
            layout.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.content_layout)

    def add_content(self, widget: QWidget):
        """Adds a widget to the content area of the frame."""
        self.content_layout.addWidget(widget)

    def add_layout(self, layout: QHBoxLayout):
        self.content_layout.addLayout(layout)

class MainWindow(QMainWindow):
    # ... existing __init__ and other methods ...

    def set_user_session(self, access_token: str):
        """Sets the user's session token and decodes it to get role information."""
        self.access_token = access_token
        try:
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            self.user_role = decoded_token.get("role", "therapist")
            self.username = decoded_token.get("sub", "Unknown User")
        except jwt.PyJWTError:
            self.user_role = "therapist"  # Default on error
            self.username = "Unknown User"

        self.setup_menu_bar()

    def start(self):
        """Start the application with modern loading experience."""
        self.load_ai_models()
        self.load_main_ui()
        self.show()


        # View menu
        view_menu = menubar.addMenu("👁️ View")
        view_menu.addAction("🌞 Light Theme", lambda: self.set_theme("light"))
        view_menu.addAction("🌙 Dark Theme", lambda: self.set_theme("dark"))

        # Help menu
        help_menu = menubar.addMenu("❓ Help")
        help_action = QAction("📖 View Help", self)
        help_action.setShortcut(QKeySequence("F1"))
        help_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(help_action)

    def setup_status_bar(self):
        """Setup status bar with easter egg."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_bar.showMessage("Ready")

        # AI status
        self.ai_status_label = QLabel("🤖 AI Models: Ready")
        self.ai_status_label.setStyleSheet("color: #059669;")
        self.status_bar.addPermanentWidget(self.ai_status_label)

        # Easter egg
        self.easter_egg_label = QLabel("Pacific Coast Therapy")
        self.easter_egg_label.setStyleSheet("""
            font-family: "Brush Script MT", "Lucida Handwriting", cursive;
            font-size: 10px;
            color: #94a3b8;
            font-style: italic;
            margin-left: 20px;
        """)
        self.status_bar.addPermanentWidget(self.easter_egg_label)

    def create_main_layout(self):
        """Create the main layout with your specification."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # TOP SECTION: Rubric and Upload cards (7 lines tall each)
        top_section = self.create_top_section()
        main_layout.addWidget(top_section)

# In your main window's UI setup method, e.g. init_ui or similar

# PROGRESS BAR SECTION
self.progress_section = self.create_progress_section()
main_layout.addWidget(self.progress_section)

# LANGUAGE SCORE SECTION
self.language_score_section = self.create_language_score_section()
main_layout.addWidget(self.language_score_section)

# MAIN CONTENT SECTION (AI Chat/Results)
main_content = self.create_main_content_section()
main_layout.addWidget(main_content, 1)  # Give stretch factor 1 for growability


        # CONTROL BUTTONS: Run Analysis, Document Preview, Stop, Analytics
        control_buttons = self.create_control_buttons()
        main_layout.addWidget(control_buttons)

        # MAIN CONTENT: Large AI chat/results window (biggest section)
        main_content = self.create_main_content()
        main_layout.addWidget(main_content, 1)  # Takes most space

        # BOTTOM: Chat input box
        chat_section = self.create_chat_section()
        main_layout.addWidget(chat_section)

    def create_top_section(self) -> QWidget:
        """Create top section with rubric and upload cards (4 lines tall each)."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(8)

        # Rubric section (left side)
        rubric_section = SectionFrame("📋 Compliance Rubric")

        rubric_content = QWidget()
        rubric_layout = QVBoxLayout(rubric_content)
        rubric_layout.setContentsMargins(0,0,0,0)
        rubric_layout.setSpacing(4)

        # Rubric selector with all disciplines option
        self.rubric_selector = QComboBox()
        self.rubric_selector.addItems([
            "Medicare Part B Requirements",
            "PT Compliance Rubric",
            "OT Compliance Rubric",
            "SLP Compliance Rubric"
        ])
        self.rubric_selector.setStyleSheet("""
            QComboBox {
                background-color: #f0f8ff;
                border: 1px solid #4a90e2;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                color: black;
            }
            QComboBox:hover {
                border-color: #357abd;
                background-color: #e6f3ff;
            }
            QComboBox:focus {
                border: 2px solid #63a4ff;
            }
        """)
        self.rubric_selector.currentTextChanged.connect(self.on_rubric_changed)

        # Description
        self.rubric_description = QLabel("Physical therapy compliance guidelines")
        self.rubric_description.setWordWrap(True)
        self.rubric_description.setStyleSheet("color: #64748b; font-size: 11px; border: none;")

        rubric_layout.addWidget(self.rubric_selector)
        rubric_layout.addWidget(self.rubric_description)
        rubric_section.add_content(rubric_content)

        # Upload section (right side)
        upload_section = SectionFrame("📄 Document Upload")

        upload_content = QWidget()
        upload_layout = QVBoxLayout(upload_content)
        upload_layout.setContentsMargins(0,0,0,0)
        upload_layout.setSpacing(4)

        # Buttons row
        button_layout = QHBoxLayout()

        self.upload_button = QPushButton("📤 Upload Document")
        self.upload_button.clicked.connect(self.open_file_dialog)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:focus {
                border: 1px solid #63a4ff;
            }
        """)

        self.clear_button = QPushButton("🗑️ Clear")
        self.clear_button.clicked.connect(self.clear_display)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #cccccc;
                color: #1a1a1a;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #b8b8b8;
            }
            QPushButton:focus {
                border: 1px solid #888888;
            }
        """)

        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()

        # Status
        self.document_status = QLabel("No document uploaded")
        self.document_status.setWordWrap(True)
        self.document_status.setStyleSheet("color: #64748b; font-size: 11px; border: none;")

        upload_layout.addLayout(button_layout)
        upload_layout.addWidget(self.document_status)
        upload_section.add_content(upload_content)

        # Add cards to layout
        layout.addWidget(rubric_section, 1)
        layout.addWidget(upload_section, 1)

        return container

    def create_progress_section(self) -> QWidget:
        """Create thin static progress bar section."""
        container = QWidget()
        container.setFixedHeight(40)  # Thin section
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 5, 0, 5)

        # Progress label
        self.progress_label = QLabel("Ready to analyze")
        self.progress_label.setStyleSheet("color: #bbbbbb; font-size: 11px;")  # Light text for dark background

        # Thin progress bar (always visible)
        self.main_progress_bar = QProgressBar()
        self.main_progress_bar.setFixedHeight(8)  # Very thin
        self.main_progress_bar.setValue(0)
        self.main_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #4a90e2;
                border-radius: 4px;
                text-align: center;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 3px;
            }
        """)

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QTextEdit,
    QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ComplianceAnalyzerMainWindow(QMainWindow):
    def create_progress_section(self) -> QWidget:
        """Create a progress bar section with label, loading spinner, and control buttons."""
        progress_widget = QWidget()
        progress_layout = QHBoxLayout(progress_widget)
        progress_layout.setContentsMargins(0, 6, 0, 6)
        progress_layout.setSpacing(12)

        # Progress bar container with label and thin progress bar
        progress_container = QWidget()
        progress_container_layout = QVBoxLayout(progress_container)
        progress_container_layout.setContentsMargins(0, 0, 0, 0)
        progress_container_layout.setSpacing(4)

        self.progress_label = QLabel("Ready to analyze")
        self.progress_label.setStyleSheet("color: #bbbbbb; font-size: 11px;")
        self.main_progress_bar = QProgressBar()
        self.main_progress_bar.setFixedHeight(8)
        self.main_progress_bar.setValue(0)
        self.main_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #4a90e2;
                border-radius: 4px;
                text-align: center;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 3px;
            }
        """)

        progress_container_layout.addWidget(self.progress_label)
        progress_container_layout.addWidget(self.main_progress_bar)

        # Loading spinner (custom widget, assume implemented elsewhere)
        self.loading_spinner = LoadingSpinner(24)
        self.loading_spinner.setVisible(False)

        # Control buttons
        self.run_analysis_button = QPushButton("🚀 Run Analysis")
        self.run_analysis_button.clicked.connect(self.run_analysis)
        self.run_analysis_button.setEnabled(False)  # Initially disabled until document uploaded or settings valid
        self.run_analysis_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QPushButton:focus {
                border: 1px solid #3cff5a;
            }
        """)

        self.request_review_button = AnimatedButton("🧑‍🏫 Request Review")
        self.request_review_button.clicked.connect(self.request_review)
        self.request_review_button.setVisible(False)  # Only visible after analysis completes
        self.request_review_button.setStyleSheet(medical_theme.get_button_stylesheet('info'))

        # Assemble progress layout
        progress_layout.addWidget(self.run_analysis_button)
        progress_layout.addWidget(self.request_review_button)
        progress_layout.addWidget(progress_container, 1)  # stretch for progress container
        progress_layout.addWidget(self.loading_spinner)

        return progress_widget

    def create_main_content_section(self) -> QWidget:
        """Create the main content area with document preview and analysis results."""
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(12)

        # Document preview section inside modern styled card
        document_card = ModernCard("📖 Document Preview")
        document_content = QWidget()
        document_layout = QVBoxLayout(document_content)

        self.document_display_area = QTextEdit()
        self.document_display_area.setPlaceholderText("📄 Upload a document to see its content here...")
        self.document_display_area.setReadOnly(True)
        self.document_display_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {medical_theme.get_color('bg_secondary')};
                border: 1px solid {medical_theme.get_color('border_light')};
                border-radius: 6px;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                line-height: 1.4;
            }}
        """)

        document_layout.addWidget(self.document_display_area)
        document_card.add_content(document_content)

        # Analysis result section (e.g. AI chat/results pane)
        results_card = ModernCard("🧠 AI Analysis Results")
        results_content = QWidget()
        results_layout = QVBoxLayout(results_content)

        self.analysis_results = QTextEdit()
        self.analysis_results.setPlaceholderText(
            "AI Analysis Chat Interface\nUpload a clinical document and click Document Preview to see content.\n"
            "Select compliance rubric, then Run Analysis to begin.\n"
            "Use Stop Analysis to halt processing if needed.\n"
            "View Analytics Dashboard for insights.\nClick Full Report to see details."
        )
        self.analysis_results.setReadOnly(True)
        self.analysis_results.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #bbbbbb;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                padding: 16px;
                font-size: 12px;
                line-height: 1.6;
            }
        """)
        results_layout.addWidget(self.analysis_results)
        results_card.add_content(results_content)

        # Add document preview and analysis results to the horizontal layout
        content_layout.addWidget(document_card, 1)
        content_layout.addWidget(results_card, 2)

        return content_widget


    # Placeholder implementations for methods referenced above
    def run_analysis(self):
        # Starts the analysis task in background
        print("Running analysis... (to be implemented)")

    def request_review(self):
        # Handles request review button logic
        print("Requesting review... (to be implemented)")

# Assume LoadingSpinner, AnimatedButton, ModernCard, medical_theme etc are custom components imported elsewhere

        """)

        # Stop Analysis button
        self.stop_analysis_button = QPushButton("⏹️ Stop Analysis")
        self.stop_analysis_button.clicked.connect(self.stop_analysis)
        self.stop_analysis_button.setEnabled(False)
        self.stop_analysis_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QPushButton:focus {
                border: 1px solid #ff4f62;
            }
        """)

        # Document Preview button
        self.doc_preview_btn = QPushButton("📖 Document Preview")
        self.doc_preview_btn.clicked.connect(self.toggle_document_preview)
        self.doc_preview_btn.setEnabled(False)
        self.doc_preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QPushButton:focus {
                border: 1px solid #63a4ff;
            }
        """)

from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QTextEdit
)
from PyQt6.QtGui import QFont

class ComplianceAnalyzerMainWindow(QMainWindow):
    def create_bottom_controls_section(self) -> QWidget:
        """Create bottom control buttons including Run Analysis, Stop, Document Preview, Analytics, Full Report."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(12)

        # Run Analysis button
        self.run_analysis_button = QPushButton("🚀 Run Analysis")
        self.run_analysis_button.clicked.connect(self.run_analysis)
        self.run_analysis_button.setEnabled(False)
        self.run_analysis_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QPushButton:focus {
                border: 1px solid #3cff5a;
            }
        """)

        # Stop Analysis button
        self.stop_analysis_button = QPushButton("⏹ Stop Analysis")
        self.stop_analysis_button.clicked.connect(self.stop_analysis)
        self.stop_analysis_button.setEnabled(False)
        self.stop_analysis_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #b02a37;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QPushButton:focus {
                border: 1px solid #ff6a6a;
            }
        """)

        # Document Preview button
        self.doc_preview_btn = QPushButton("📄 Document Preview")
        self.doc_preview_btn.clicked.connect(self.show_document_preview)
        self.doc_preview_btn.setEnabled(False)
        self.doc_preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QPushButton:focus {
                border: 1px solid #66b0ff;
            }
        """)

        # Analytics Dashboard button
        self.analytics_button = QPushButton("📊 Analytics Dashboard")
        self.analytics_button.clicked.connect(self.show_analytics)
        self.analytics_button.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a32a3;
            }
            QPushButton:focus {
                border: 1px solid #8c5dff;
            }
        """)

        # Full Report button
        self.report_view_btn = QPushButton("📋 Full Report")
        self.report_view_btn.clicked.connect(self.toggle_report_view)
        self.report_view_btn.setEnabled(False)
        self.report_view_btn.setStyleSheet("""
            QPushButton {
                background-color: #fd7e14;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e8690b;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QPushButton:focus {
                border: 1px solid #ff9a4a;
            }
        """)

        layout.addWidget(self.run_analysis_button)
        layout.addWidget(self.stop_analysis_button)
        layout.addWidget(self.doc_preview_btn)
        layout.addWidget(self.analytics_button)
        layout.addWidget(self.report_view_btn)
        layout.addStretch()

        return container

    def create_main_content(self) -> QWidget:
        """Create main AI chat/results area (full width) with quadrant widget for results."""
        results_section = SectionFrame("🤖 AI Analysis & Chat Interface")
        results_content = QWidget()
        results_layout = QVBoxLayout(results_content)

        # Use QuadrantWidget as the results display
        self.analysis_results_area = QuadrantWidget()
        results_layout.addWidget(self.analysis_results_area)
        results_section.add_content(results_content)

        # Use Responsive Splitter for layout of document preview and results
        from .widgets.responsive_layout import ResponsiveSplitter

        splitter = ResponsiveSplitter()
        splitter.addWidget(document_card)  # Assuming document_card defined globally or pass as arg
        splitter.addWidget(results_section)
        splitter.setSizes([400, 600])  # Allocate more space to results

        return splitter


        return results_section

    def create_chat_section(self) -> QWidget:
        """Create chat input box at bottom."""
        chat_section = SectionFrame("💬 AI Assistant")
        chat_content = QWidget()
        chat_layout = QHBoxLayout(chat_content)

        # Chat input
        self.chat_input = ChatInput()
        self.chat_input.sendMessage.connect(self.send_chat)
        self.chat_input.setPlaceholderText("Ask the AI assistant... (Press Enter to send)")
        self.chat_input.setMaximumHeight(60)
        self.chat_input.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                color: black;
            }
            QTextEdit:focus {
                border: 1px solid #4a90e2;
            }
        """)

        # Send button
        self.send_button = QPushButton("📤 Send")
        self.send_button.clicked.connect(self.send_chat)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:focus {
                border: 1px solid #63a4ff;
            }
        """)
        self.send_button.setFixedWidth(80)

        chat_layout.addWidget(self.chat_input, 1)
class ComplianceAnalyzerMainWindow(QMainWindow):

    def create_chat_section(self) -> QWidget:
        """Create the chat input section."""
        chat_widget = SectionFrame("💬 AI Chat & Input")
        chat_content = QWidget()
        chat_layout = QHBoxLayout(chat_content)

        # Placeholders for voice input and send buttons
        self.voice_button = QPushButton("🎤 Voice")
        self.send_chat_button = QPushButton("📩 Send")

        chat_layout.addWidget(self.voice_button)
        chat_layout.addWidget(self.send_chat_button)

        chat_widget.add_content(chat_content)
        return chat_widget

    def start(self):
        """Start the application."""
        print("🚀 Starting working modern application...")
        print("✅ Working modern UI loaded successfully!")

    # Event handlers
    def on_rubric_changed(self, text):
        """Handle rubric selection change."""
        descriptions = {
            "Medicare Part B Requirements": "Guidelines for outpatient therapy services under Medicare Part B.",
            "PT Compliance Rubric": "Physical therapy compliance guidelines and Medicare requirements",
            "OT Compliance Rubric": "Occupational therapy compliance guidelines and documentation standards",
            "SLP Compliance Rubric": "Speech-language pathology compliance guidelines and regulatory requirements"
        }
        self.rubric_description.setText(descriptions.get(text, "Select a rubric to see description"))

    def _on_rubric_selected(self, index):
        """Handle rubric selection with detailed enabling and description."""
        selected_rubric = self.rubric_selector.itemData(index)
        if selected_rubric:
            self.rubric_description_label.setText(
                selected_rubric.get("description", "No description available.")
            )
            self.run_analysis_button.setEnabled(True)
            self.run_analysis_button.setText("🚀 Run Analysis")
        else:
            self.rubric_description_label.setText("Select a rubric to see description")
            self.run_analysis_button.setEnabled(False)


    def open_file_dialog(self):
        """Open file dialog for document upload."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "📁 Select Clinical Document", 
            "", 
            "All Supported Files (*.pdf *.docx *.txt);;PDF Files (*.pdf);;Word Documents (*.docx);;Text Files (*.txt)"
        )

        if file_name:
            self._current_file_path = file_name
            file_info = os.path.basename(file_name)
            self.document_status.setText(f"📄 {file_info}")

            try:
                # Try to read as text
                with open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    self._current_document_content = content

                self.status_bar.showMessage(f"✅ Loaded: {file_info}", 3000)
                self.run_analysis_button.setEnabled(True)
                self.doc_preview_btn.setEnabled(True)  # Enable preview button

                # Show success in chat area
                self.analysis_results.append(f"""
                <div style="background-color: #d4edda; color: #155724; padding: 10px; border-radius: 6px; margin: 4px 0; border-left: 4px solid #28a745;">
                    <strong>✅ Document Loaded:</strong> {file_info}<br>
                    <small style="color: #666;">Click 'View Document Preview' to see content • Ready for analysis</small>
                </div>
                """)

            except Exception as e:
                self.status_bar.showMessage(f"⚠️ Preview error: {e}", 5000)
                self.analysis_results.append(f"""
                <div style="background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 6px; margin: 4px 0; border-left: 4px solid #dc3545;">
                    <strong>❌ Error Loading Document:</strong> {e}
                </div>
                """)

    def run_analysis(self):
        """Run compliance analysis using a background worker."""
        if not self._current_file_path:
            QMessageBox.warning(self, "No Document", "Please upload a document first.")
            return

        # NOTE: In a real application, we would first call a 'starter' worker
        # to get a task_id from the backend. For this simulation, we'll use a dummy task_id.
        dummy_task_id = "12345"

        self.main_progress_bar.setRange(0, 100)
        self.main_progress_bar.setValue(0)
        self.main_progress_bar.setVisible(True)
        self.run_analysis_button.setEnabled(False)
        self.run_analysis_button.setText("🔄 Analyzing...")
        self.progress_label.setText("🤖 AI analysis in progress...")
        self.stop_analysis_button.setEnabled(True)

        # Setup and run the worker in a separate thread
        self.worker_thread = QThread()
        self.analysis_worker = AnalysisWorker(dummy_task_id)
        self.analysis_worker.moveToThread(self.worker_thread)

        # Connect signals
        self.analysis_worker.progress.connect(self.main_progress_bar.setValue)
        self.analysis_worker.success.connect(self.analysis_complete)
        self.analysis_worker.error.connect(self.on_analysis_error)
        self.analysis_worker.finished.connect(self.worker_thread.quit)
        self.analysis_worker.finished.connect(self.analysis_worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.started.connect(self.analysis_worker.run)
        self.worker_thread.start()

    def on_analysis_error(self, error_message):
        """Show analysis error message."""
        QMessageBox.critical(self, "Analysis Error", error_message)
        self.run_analysis_button.setEnabled(True)
        self.run_analysis_button.setText("🚀 Run Analysis")
        self.stop_analysis_button.setEnabled(False)
        self.progress_label.setText("❌ Analysis Failed")

    def analysis_complete(self, result=None):
        """Handle analysis completion."""
        # The result from the worker would be used here.
        # For now, we'll keep the existing report generation.
        self.main_progress_bar.setValue(100)
        self.run_analysis_button.setEnabled(True)
        self.run_analysis_button.setText("🚀 Run Analysis")
        self.stop_analysis_button.setEnabled(False)
        self.progress_label.setText("✅ Analysis complete")

        # Get selected rubric for context
        selected_rubric = self.rubric_selector.currentText()

        # Show enhanced demo results
        html_report = f"""
        <style>
            .dot {{
                height: 10px; width: 10px; border-radius: 50%;
                display: inline-block; margin-right: 8px; vertical-align: middle;
            }}
            .high-risk {{ background-color: #dc3545; }}
            .medium-risk {{ background-color: #f59e0b; }}
            .strength {{ background-color: #28a745; }}
            .finding-item {{ border-left: 3px solid #ccc; padding-left: 10px; margin-bottom: 10px; }}
            .high-risk-border {{ border-left-color: #dc3545; }}
            .medium-risk-border {{ border-left-color: #f59e0b; }}
            .strength-border {{ border-left-color: #28a745; }}
        </style>
        <div style="background-color: #1e3a8a; color: white; padding: 15px; border-radius: 8px; margin-bottom: 12px;">
            <h2 style="color: white; margin: 0 0 10px 0;">🎯 Compliance Analysis Results</h2>
            <div style="display: flex; justify-content: space-between;">
                <div><strong>Overall Score:</strong> <span style="color: #10b981; font-size: 18px; font-weight: bold;">87%</span></div>
                <div><strong>Risk Level:</strong> <span style="color: #f59e0b; font-weight: bold;">Medium</span></div>
                <div><strong>Document Type:</strong> Progress Note</div>
            </div>
            <p style="margin: 8px 0 0 0;"><strong>Rubric Applied:</strong> {selected_rubric}</p>
        </div>

        <h4 style="color: #bbbbbb; margin: 12px 0 8px 0;">Findings</h4>

        <div class="finding-item high-risk-border">
            <p><span class="dot high-risk"></span><strong>Critical:</strong> Missing Medicare-required functional limitation reporting</p>
            <p><small><strong>Evidence:</strong> No G-codes or severity modifiers documented</small></p>
            <p><small><strong>Recommendation:</strong> Add G0918-G0920 codes with appropriate severity levels</small></p>
        </div>

        <div class="finding-item high-risk-border">
            <p><span class="dot high-risk"></span><strong>Critical:</strong> Insufficient skilled therapy justification</p>
            <p><small><strong>Evidence:</strong> Generic treatment descriptions without complexity rationale</small></p>
            <p><small><strong>Recommendation:</strong> Document why skilled therapist intervention is medically necessary</small></p>
        </div>

        <div class="finding-item medium-risk-border">
            <p><span class="dot medium-risk"></span><strong>Medium:</strong> Missing standardized outcome measures</p>
            <p><small><strong>Evidence:</strong> No validated assessment tools documented</small></p>
            <p><small><strong>Recommendation:</strong> Include Berg Balance Scale, FIM scores, or discipline-specific measures</small></p>
        </div>

        <h4 style="color: #bbbbbb; margin: 12px 0 8px 0;">Strengths</h4>

        <div class="finding-item strength-border">
            <p><span class="dot strength"></span><strong>Excellent:</strong> Clear documentation of treatment interventions</p>
            <p><small><strong>Evidence:</strong> Detailed session notes with specific exercises and patient responses</small></p>
        </div>

        <div class="finding-item strength-border">
            <p><span class="dot strength"></span><strong>Good:</strong> Appropriate frequency and duration documented</p>
            <p><small><strong>Evidence:</strong> Treatment schedule aligns with patient condition and goals</small></p>
        </div>
        """
        self.analysis_results.setHtml(html_report)

        # Store report content and enable report button
        self._current_report_content = self.analysis_results.toHtml()
        self.report_view_btn.setEnabled(True)

        self.status_bar.showMessage("✅ Analysis completed successfully!", 5000)

def send_chat_message(self):
    """Send a chat message to the AI assistant, opening a new chat dialog with the user's message as initial context."""
    # Implementation for sending chat message here

        message = self.chat_input.toPlainText().strip()
        if message:
            # Add to results area
            self.analysis_results.append(f"""
            <div style="background-color: #e8f4fd; padding: 8px; border-radius: 4px; margin: 4px 0; color: black;">
                <strong>You:</strong> {message}
            </div>
            <div style="background-color: #f0f9ff; padding: 8px; border-radius: 4px; margin: 4px 0; color: black;">
                <strong>🤖 AI Assistant:</strong> Thank you for your question about "{message}".
                This feature is being enhanced with the new AI chat system. Please use the analysis results above for now.
            </div>
            """)
            self.chat_input.clear()

    def clear_display(self):
        """Clear all displays."""
        self.analysis_results.clear()
        self.document_status.setText("No document uploaded")
        self._current_file_path = None
        self._current_document_content = ""
        self._current_report_content = ""
        self.run_analysis_button.setEnabled(False)
        self.doc_preview_btn.setEnabled(False)
        self.report_view_btn.setEnabled(False)
        self.status_bar.showMessage("Displays cleared", 2000)

    def toggle_document_preview(self):
        """Toggle document preview popup window."""
        if not self._current_document_content:
            QMessageBox.warning(self, "No Document", "Please upload a document first.")
            return

        if self.document_preview_dialog is None or not self.document_preview_dialog.isVisible():
            self.document_preview_dialog = DocumentPreviewDialog(
                self._current_document_content,
                self
            )
            self.document_preview_dialog.show()
            self.doc_preview_btn.setText("📖 Hide Document Preview")
        else:
            self.document_preview_dialog.close()
            self.doc_preview_btn.setText("📖 View Document Preview")

    def toggle_report_view(self):
        """Toggle full report view popup window."""
        if not self._current_report_content:
            QMessageBox.warning(self, "No Report", "Please run analysis first to generate a report.")
            return

def toggle_report_view(self):
    if self.report_view_dialog is None or not self.report_view_dialog.isVisible():
        self.report_view_dialog = ReportViewDialog(
            self._current_report_content,
            self
        )
        self.report_view_dialog.show()
        self.report_view_btn.setText("📊 Hide Full Report")
    else:
        self.report_view_dialog.close()
        self.report_view_btn.setText("📋 Full Report")

def stop_analysis(self):
    """Stop the current analysis."""
    if hasattr(self, 'analysis_worker'):
        self.analysis_worker.stop()

    self.main_progress_bar.setValue(0)
    self.run_analysis_button.setEnabled(True)
    self.run_analysis_button.setText("🚀 Run Analysis")
    self.stop_analysis_button.setEnabled(False)
    self.progress_label.setText("Analysis stopped by user")

    # Show stopped message
    self.analysis_results.append("""
    <div style="background-color: #7f1d1d; color: white; padding: 10px; border-radius: 6px; margin: 4px 0;">
        <strong>⏹️ Analysis Stopped:</strong> Processing halted by user request<br>
        <small style="color: #fca5a5;">You can restart analysis at any time</small>
    </div>
    """)

    self.status_bar.showMessage("⏹️ Analysis stopped", 3000)

def show_analytics(self):
    """Show analytics dashboard."""
    analytics_dialog = QDialog(self)
    analytics_dialog.setWindowTitle("📊 Analytics Dashboard")
    analytics_dialog.setGeometry(200, 200, 900, 600)
    analytics_dialog.setStyleSheet("""
        QDialog {
            background-color: #3c3f41;
            color: #bbbbbb;
        }
    """)

    layout = QVBoxLayout(analytics_dialog)

    # Header
    header = QLabel("📊 Compliance Analytics & Trends")
    header.setStyleSheet("""
        QLabel {
            color: #6f42c1;
            font-size: 18px;
            font-weight: bold;
            padding: 12px;
            background-color: #2b2b2b;
            border-radius: 8px;
            margin-bottom: 10px;
        }
    """)
    layout.addWidget(header)

    analytics_content = QTextBrowser()
    analytics_content.setHtml("""
    <!-- (Detailed analytics HTML content as in your snippet) -->
    """)
    analytics_content.setStyleSheet("""
        QTextBrowser {
            background-color: #2b2b2b;
            color: #bbbbbb;
            border: 2px solid #6f42c1;
            border-radius: 8px;
            padding: 15px;
            font-size: 12px;
        }
    """)
    layout.addWidget(analytics_content)

    close_btn = QPushButton("✖️ Close Analytics")
    close_btn.clicked.connect(analytics_dialog.close)
    close_btn.setStyleSheet("""
        QPushButton {
            background-color: #666666;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #555555;
        }
        QPushButton:focus {
            border: 2px solid #888888;
        }
    """)
    layout.addWidget(close_btn)

    analytics_dialog.exec()

def set_theme(self, theme):
    """Set application theme."""
    if theme == "dark":
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e293b;
                color: #f1f5f9;
            }
            QFrame {
                background-color: #334155 !important;
                border: 1px solid #475569 !important;
            }
            QTextEdit {
                background-color: #334155 !important;
                color: #f1f5f9 !important;
                border: 1px solid #475569 !important;
            }
            QLabel {
                color: #f1f5f9;
            }
        """)
        self.status_bar.showMessage("🌙 Dark theme activated", 2000)
    else:
        # Reset to light theme or call init_ui() to reload styles
        self.init_ui()
        self.status_bar.showMessage("🌞 Light theme activated", 2000)

# Placeholder methods to be implemented as relevant
def logout(self):
    reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?")
    if reply == QMessageBox.StandardButton.Yes:
        self.close()

def manage_rubrics(self):
    dialog = RubricManagerDialog(access_token="dummy_token_for_testing", parent=self)
    dialog.exec()

def show_performance_settings(self):
    dialog = PerformanceSettingsDialog(parent=self)
    dialog.exec()

def show_help_dialog(self):
    dialog = HelpDialog(self)
    dialog.exec()
