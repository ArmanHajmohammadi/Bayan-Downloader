import sys
import os
import subprocess
import requests
from bs4 import BeautifulSoup
import re
import certifi
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal


class VideoDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()

        self.url_label = QLabel("Video URL:")
        self.url_input = QLineEdit(self)
        self.download_path_label = QLabel("Download Path:")
        self.download_path_input = QLineEdit(self)
        self.browse_button = QPushButton("Browse", self)
        self.output_name_label = QLabel("Video Name:")
        self.output_name_input = QLineEdit(self)

        self.download_button = QPushButton("Download Video", self)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        layout.addWidget(self.download_path_label)
        layout.addWidget(self.download_path_input)
        layout.addWidget(self.browse_button)

        layout.addWidget(self.output_name_label)
        layout.addWidget(self.output_name_input)

        layout.addWidget(self.download_button)
        layout.addWidget(QLabel("by: Arman Hajmohammadi"))
        self.browse_button.clicked.connect(self.browse_path)
        self.download_button.clicked.connect(self.download_video)

        self.setLayout(layout)
        self.setWindowTitle('Bayan Downloader')
        # Replace 'icon.png' with your icon file
        self.setWindowIcon(QIcon('Download.ico'))
        self.setFixedSize(500, 300)  # Set fixed window size

    def browse_path(self):
        download_path = QFileDialog.getExistingDirectory(
            self, 'Select Download Path')
        if download_path:
            self.download_path_input.setText(download_path)

    def download_video(self):
        url = str(self.url_input.text()).replace(" ", "").replace("\n", "")
        download_path = self.download_path_input.text()
        output_name = self.output_name_input.text()

        if not url or not download_path or not output_name:
            QMessageBox.warning(self, 'Warning', 'Please fill in all fields.')
            return

        try:
            print("log 1 => url = " + url)
            video_url = get_video_url(url)
            print("log 2 => video_url = " + video_url)
            if video_url:
                output_file = os.path.join(download_path, output_name + ".mp4")

                # Disable the download button during the download process
                self.download_button.setEnabled(False)
                self.download_button.setText("Please wait...")

                # Create a downloader object
                downloader = Downloader(video_url, output_file, self)

                # Connect signals
                downloader.download_finished.connect(self.download_finished)

                # Start the download process
                downloader.start()

            else:
                QMessageBox.warning(
                    self, 'Warning', 'Failed to get video URL.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f"An error occurred: {str(e)}")

    def download_finished(self):
        # Enable the download button after the download process finishes
        self.download_button.setEnabled(True)
        self.download_button.setText("Download Video")
        QMessageBox.information(
            self, 'Success', 'Video downloaded successfully.')


class Downloader(QThread):
    download_finished = pyqtSignal()

    def __init__(self, video_url, output_file, parent=None):
        super().__init__(parent)
        self.video_url = video_url
        self.output_file = output_file

    def run(self):
        try:
            # Use subprocess to run ffmpeg command for downloading the video
            subprocess.run(["ffmpeg", "-i", self.video_url,
                           self.output_file], check=True)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(
                None, 'Error', f"Error occurred while downloading the video: {e}")
        finally:
            self.download_finished.emit()


def get_video_url(url):
    try:

        response = requests.get(url, verify=False)

        if response.status_code == 200:

            soup = BeautifulSoup(response.text, 'html.parser')

            # Use a regular expression to find the specific part in the HTML
            pattern = re.compile(
                r'\{.*type: "video/mp4".*src: "([^"]*)".*\}', re.DOTALL)
            match = pattern.search(str(soup))

            # Check if the pattern is found
            if match:
                # Extract and return the 'src' part of the match
                return match.group(1)
            else:
                raise Exception("Pattern not found in the HTML.")
        else:
            raise Exception(
                f"Failed to fetch URL. Status code: {response.status_code}")
    except Exception as e:
        raise Exception(f"An error occurred while getting video URL: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoDownloaderApp()
    window.show()
    sys.exit(app.exec_())
