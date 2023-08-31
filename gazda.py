from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import logging
import os


class FileSorter:
    def __init__(self, directory_path):
        self.source_path = Path(directory_path)
        self.extensions = set()

        logging.basicConfig(filename='file_sorter.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def collect_extensions(self):
        for file_path in self.source_path.rglob("*.*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
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
        logging.info(f"File {file_path.name} moved to {destination_folder}")

    def sort_files(self, destination_folder):
        with ThreadPoolExecutor() as executor:
            futures = []
            for file_path in self.source_path.rglob("*.*"):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    extension = file_path.suffix[1:]
                    folder_name = extension.upper() + "_Files"
                    destination_folder = self.source_path / folder_name

                    futures.append(executor.submit(self.move_file, file_path, destination_folder))

            for future in futures:
                future.result()

    def remove_empty_folders(self):
        for folder in self.source_path.iterdir():
            if folder.is_dir() and not any(folder.iterdir()):
                folder.rmdir()
                logging.info(f"Empty folder {folder.name} deleted.")

    def check_write_permission(self):
        if not os.access(self.source_path, os.W_OK):
            print(f"You need more rights to sort {self.source_path} folder.")
            return False
        return True

    def sort(self):
        # ...

        if not self.check_write_permission():
            return

        self.collect_extensions()
        self.create_folders()

        with ThreadPoolExecutor() as executor:
            executor.submit(self.sort_files, self.source_path)

        self.remove_empty_folders()
        
        hidden_files_present = any(
            file_path.is_file() and file_path.name.startswith('.')
            for file_path in self.source_path.rglob("*.*")
        )
        
        if hidden_files_present:
            logging.warning("Hiden files in this folder.")

        logging.info("Sorting is completed.")

def main():
    source_directory = input(f">>> Input folder path: ")
    sorter = FileSorter(source_directory)
    sorter.sort()

if __name__ == "__main__":
    main()
