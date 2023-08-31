from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import logging
import os


class FileSorter:
    def __init__(self, directory_path):
        self.source_path = Path(directory_path)
        self.extensions = set()

        self.logger = logging.getLogger('file_sorter')
        self.logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        file_handler = logging.FileHandler('file_sorter.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def collect_extensions(self):
        for file_path in self.source_path.rglob("*.*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                extension = file_path.suffix[1:]
                self.extensions.add(extension)

    def create_folders(self):
        for extension in self.extensions:
            folder_name = extension.upper() + "_Files"
            folder_path = self.source_path / folder_name
            folder_path.mkdir(exist_ok=True)

    def move_file(self, file_path, destination_folder):
        destination_file_path = destination_folder / file_path.name
        if destination_file_path.exists():
            suffix = 1
            while destination_file_path.exists():
                new_file_name = f"{file_path.stem}_{suffix}{file_path.suffix}"
                destination_file_path = destination_folder / new_file_name
                suffix += 1
        file_path.rename(destination_file_path)
        self.logger.debug(f"File {file_path.name} moved to {destination_folder}")

    def sort_files(self, destination_folder):
        with ThreadPoolExecutor() as executor:
            futures = []
            for file_path in self.source_path.rglob("*.*"):
                if file_path.is_file() and not file_path.name.startswith("."):
                    extension = file_path.suffix[1:]
                    folder_name = extension.upper() + "_Files"
                    destination_folder = self.source_path / folder_name

                    futures.append(
                        executor.submit(self.move_file, file_path, destination_folder)
                    )

            for future in futures:
                future.result()

    def remove_empty_folders(self):
        for folder in sorted(self.source_path.rglob('*'), key=lambda p: p.as_posix(), reverse=True):
            if folder.is_dir() and not any(folder.iterdir()):
                folder.rmdir()
                self.logger.info(f"Empty folder {folder.name} deleted.")

    def check_write_permission(self):
        if not os.access(self.source_path, os.W_OK):
            self.logger.warning(f"You need more rights to sort {self.source_path} folder.")
            return False
        return True

    def sort(self):

        self.logger.info("Sorting has started")

        if not self.check_write_permission():
            return

        self.collect_extensions()
        self.create_folders()

        with ThreadPoolExecutor() as executor:
            executor.submit(self.sort_files, self.source_path)

        self.remove_empty_folders()

        hidden_files_present = any(
            file_path.is_file() and file_path.name.startswith(".")
            for file_path in self.source_path.rglob("*.*")
        )

        if hidden_files_present:
            self.logger.warning("Hiden files in this folder.")

        self.logger.info("Sorting is completed.")


def main():
    '''Gazda is a program created to sort files in a chosen directory.'''
    source_directory = input(f">>> Input folder path: ")
    sorter = FileSorter(source_directory)
    sorter.sort()


if __name__ == "__main__":
    main()
