import argparse
import json
import os.path
import platform
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
import zipfile
from tkinter import ttk, messagebox
from urllib.error import URLError
from urllib.request import urlopen, urlretrieve


class Updater:
    def __init__(self, tk_root, current_version, url_json, destination_path, file_to_execute):
        self.start_time = None
        self.download_thread = None
        self.tk_root = tk_root
        self.current_version = current_version
        self.url_json = url_json
        self.destination_path = destination_path
        self.file_to_execute = file_to_execute
        self.temp_dir = tempfile.TemporaryDirectory()

        width = 300
        height = 90
        screen_width = tk_root.winfo_screenwidth()
        screen_height = tk_root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))

        tk_root.geometry(f'{width}x{height}+{x}+{y}')
        tk_root.title("LinSoTracker Updater")
        tk_root.protocol("WM_DELETE_WINDOW", self.on_closing)
        tk_root.resizable(False, False)

        self.label = tk.Label(tk_root, text="Updating in progress")
        self.label.grid(row=0, column=0, padx=5, pady=5)

        self.progressbar = ttk.Progressbar(tk_root, mode='determinate')
        self.progressbar.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        tk_root.grid_columnconfigure(0, weight=1)
        self.check_update()


    @staticmethod
    def detect_os():
        if platform.system() == 'Windows':
            return "win"
        elif platform.system() == 'Linux':
            return "linux"
        elif platform.system() == 'Darwin':
            if platform.machine() == 'arm64':
                return "macARM64"
            else:
                return "macIntel"

    def check_update(self):
        try:
            response = urlopen(self.url_json)
            data_json = json.loads(response.read())

            if "lastest_version" in data_json:
                if self.current_version != data_json["lastest_version"]:
                    build_url = data_json['url_base'].format(self.detect_os(), data_json['lastest_version'])
                    destination_path = os.path.join(self.temp_dir.name, os.path.basename(build_url))
                    self.start_download(url=build_url,
                                        destination=destination_path)
        except URLError:
            pass

    def on_closing(self):
        pass

    def start_download(self, url, destination):
        self.download_thread = threading.Thread(target=self.download_file, args=(url, destination))
        self.download_thread.start()

    def download_file(self, url, destination):
        try:
            urlretrieve(url, destination, self.progress_hook)
            self.extract_file(destination)
            self.launch_external_application()
            self.close_application()
        except:
            sys.exit()

    def progress_hook(self, count, block_size, total_size):
        progress = int(count * block_size * 100 / total_size)
        self.progressbar.config(value=progress)

    def extract_file(self, patch_path):
        if os.path.exists(patch_path):
            with zipfile.ZipFile(patch_path, 'r') as zip_patch:
                zip_patch.extractall(self.destination_path)

    def launch_external_application(self):
        app_process = subprocess.Popen([os.path.join(self.destination_path, self.file_to_execute)])
        os._exit(0)

    def close_application(self):
        self.tk_root.destroy()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--current_version", type=str, help="Current version of the tracker")
    parser.add_argument("--url_json", type=str, help="URL of the reference json")
    parser.add_argument("--destination_path", type=str, help="Where to extract the patch")
    parser.add_argument("--file_to_execute", type=str, help="File to execute after patch")

    args = parser.parse_args()

    if args.current_version and args.url_json and args.destination_path and args.file_to_execute:
        root = tk.Tk()
        app = Updater(root, args.current_version, args.url_json, args.destination_path, args.file_to_execute)
        root.mainloop()

