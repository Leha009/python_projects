import os
import shutil
import requests

VERSION_FILE = "version.txt"
UPDATE_FILE_EXT = ".tar.gz"

class Version(str):
    def __lt__(self, value: str) -> bool:
        if not self.strip():
            return True
        if not value.strip():
            return False

        v1 = list(map(int, self.split('.')))
        v2 = list(map(int, value.split('.')))

        while len(v1) < len(v2):
            v1.append(0)
        while len(v2) < len(v1):
            v2.append(0)

        for a, b in zip(v1, v2):
            if a < b:
                return True
            if a > b:
                return False

        return False

class Updater():
    def __init__(self, update_server_addr: str, app_name: str) -> None:
        self.update_server_addr = update_server_addr
        self.app_name = app_name

    def get_current_version(self) -> Version:
        if not os.path.exists(VERSION_FILE):
            return Version("0")

        with open(VERSION_FILE) as f:
            return Version(f.read())

    def get_last_version_from_server(self) -> Version | None:
        response = requests.get(f"{self.update_server_addr}/versions", params={
            "app": self.app_name
        })
        if not response.ok:
            return None

        results = response.json()
        return Version(results["last_version"])

    def download_version(self, version: str) -> str | None:
        response = requests.get(f"{self.update_server_addr}/get_version", params={
            "app": self.app_name,
            "version": version
        })

        if not response.ok:
            return None

        tmp_folder = "/tmp" if os.path.exists("/tmp") else "tmp"

        file_path = f"{tmp_folder}/{version}{UPDATE_FILE_EXT}"
        with open(file_path, "wb") as f:
            f.write(response.content)

        return file_path

    def update(self, version: str | None = None) -> bool:
        if version is None:
            version = self.get_last_version_from_server()
            if version is None:
                return False

        self.__print(f"Скачиваем версию {version}")
        tar_path = self.download_version(version)
        if tar_path is None:
            self.__print("Не удалось скачать обновление :(")
            return False

        shutil.unpack_archive(tar_path, ".")
        req_file = "requirements.txt"
        if os.path.exists(req_file):
            install_packages = list()
            remove_packages = list()
            with open(req_file, encoding="utf-8") as f:
                for line in f:
                    if line.startswith('-'):
                        remove_packages.append(line[1:])
                    else:
                        install_packages.append(line)

            if len(remove_packages):
                remove_packages = " ".join(remove_packages)
                os.system(f"pip uninstall -y {remove_packages}")

            if len(install_packages):
                install_packages = " ".join(install_packages)
                os.system(f"pip install {install_packages}")

            os.remove(req_file)

        with open(VERSION_FILE, "w") as f:
            f.write(version)

        self.__print(f"Версия {version} установлена!")
        return True

    def updates_available(self) -> bool:
        current_version = self.get_current_version()
        last_version = self.get_last_version_from_server()
        return last_version is not None and current_version < last_version

    def __print(self, text: str) -> None:
        print("*"*80)
        print(f"{text:{' '}^80}")
        print("*"*80)
