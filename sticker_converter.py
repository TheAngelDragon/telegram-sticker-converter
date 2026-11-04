import sys
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

TITLE = "Telegram Sticker Converter"


def get_ffmpeg_path():
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent

    return base / "ffmpeg" / "ffmpeg.exe"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(TITLE)
        self.resize(400, 300)

        self.input_file = None

        self.build_ui()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # File Selection
        file_group = QGroupBox("Video")
        file_layout = QHBoxLayout(file_group)

        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.select_file)

        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(browse_button)

        layout.addWidget(file_group)

        # Settings
        settings_group = QGroupBox("Settings")
        settings_layout = QFormLayout(settings_group)

        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 120)
        self.fps_spin.setValue(30)

        self.time_spin = QSpinBox()
        self.time_spin.setRange(1, 60)
        self.time_spin.setValue(3)

        settings_layout.addRow("Frame Rate (FPS)", self.fps_spin)
        settings_layout.addRow("Duration (seconds)", self.time_spin)

        layout.addWidget(settings_group)

        # Convert Button
        self.convert_button = QPushButton("Convert to WebM")
        self.convert_button.setMinimumHeight(42)
        self.convert_button.clicked.connect(self.convert)

        layout.addWidget(self.convert_button)

        # Status Area
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        layout.addWidget(self.status_label)

        layout.addStretch()

        # Dark theme with purple buttons
        self.setStyleSheet("""
            QMainWindow {
                background: #1e1f22;
            }

            QLabel,
            QGroupBox {
                color: #e8eaed;
            }

            QGroupBox {
                font-weight: bold;
                border: 1px solid #4b4b4b;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 12px;
                background: #2b2d31;
            }

            QLineEdit,
            QSpinBox {
                background: #3a3d41;
                color: white;
                border: 1px solid #5a5a5a;
                border-radius: 5px;
                padding: 6px;
            }

            QPushButton {
                background: #7c3aed;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #8b5cf6;
            }

            QPushButton:pressed {
                background: #6d28d9;
            }
        """)

    def set_status(self, message, success):
        if success:
            self.status_label.setStyleSheet("""
                color: #4ade80;
                font-weight: bold;
            """)
            self.status_label.setText(f"✅ {message}")
        else:
            self.status_label.setStyleSheet("""
                color: #f87171;
                font-weight: bold;
            """)
            self.status_label.setText(f"❌ {message}")

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video",
            "",
            (
                "Video Files (*.mov *.mp4 *.m4v *.mkv *.avi *.webm);;"
                "All Files (*.*)"
            )
        )

        if not file_path:
            return

        self.input_file = Path(file_path)

        self.file_edit.setText(str(self.input_file))

        self.set_status(
            f"Selected {self.input_file.name}",
            True
        )

    def convert(self):
        if not self.input_file:
            self.set_status(
                "Please select a video file first.",
                False
            )
            return

        ffmpeg = get_ffmpeg_path()

        if not ffmpeg.exists():
            self.set_status(
                f"FFmpeg not found: {ffmpeg}",
                False
            )
            return

        output_file = self.input_file.with_suffix(".webm")

        cmd = [
            str(ffmpeg),
            "-y",
            "-i", str(self.input_file),
            "-r", str(self.fps_spin.value()),
            "-t", str(self.time_spin.value()),
            "-an",
            "-c:v", "libvpx-vp9",
            "-pix_fmt", "yuva420p",
            "-s", "512x512",
            "-b:v", "300K",
            str(output_file)
        ]

        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                error_text = result.stderr.strip()

                if error_text:
                    error_text = error_text.splitlines()[-1]

                self.set_status(
                    error_text or "FFmpeg conversion failed.",
                    False
                )
                return

            self.set_status(
                f"Sticker created successfully.\nLocation: {output_file}",
                True
            )

        except Exception as e:
            self.set_status(
                str(e),
                False
            )

        finally:
            QApplication.restoreOverrideCursor()


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()