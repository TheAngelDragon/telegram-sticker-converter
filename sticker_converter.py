import sys
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
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

        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["5", "10", "15", "20", "25", "30"])
        self.fps_combo.setCurrentText("30")

        self.time_spin = QDoubleSpinBox()
        self.time_spin.setRange(0.1, 3.0)
        self.time_spin.setDecimals(2)
        self.time_spin.setSingleStep(0.1)
        self.time_spin.setValue(3.0)

        settings_layout.addRow("Frame Rate (FPS)", self.fps_combo)
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

        # Dark theme with light blue buttons
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
            QComboBox,
            QDoubleSpinBox {
                background: #3a3d41;
                color: white;
                border: 1px solid #5a5a5a;
                border-radius: 5px;
                padding: 6px;
            }

            QComboBox QAbstractItemView {
                background: #3a3d41;
                color: white;
            }

            QPushButton {
                background: #60a5fa;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #93c5fd;
            }

            QPushButton:pressed {
                background: #3b82f6;
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
            "-r", self.fps_combo.currentText(),
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