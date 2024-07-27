import os
import shutil
import json
from pathlib import Path
import mimetypes
import argparse
from colorama import Fore, Back, init

init(autoreset=True)

def config_file_path():
    return Path(os.path.expanduser("~")) / "downloads_organizer_config.json"

def load_configuration():
    default_settings = {
        "folder_names": {
            "Audio": ["mp3", "wav", "flac", "m4a", "aac", "ogg"],
            "Archive": ["zip", "rar", "7z", "tar", "gz"],
            "Code": ["py", "js", "html", "css", "java", "cpp", "c", "cs"],
            "Documents": ["pdf", "doc", "docx", "txt", "rtf", "xlsx", "pptx"],
            "Ebooks": ["epub", "mobi", "azw3"],
            "Images": ["jpg", "jpeg", "png", "gif", "bmp", "tiff"],
            "Programs": ["exe", "msi", "bat"],
            "Videos": ["mp4", "avi", "mkv", "mov", "wmv"],
            "Fonts": ["ttf", "otf", "woff"],
            "Torrents": ["torrent"]
        }
    }

    config_path = config_file_path()

    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            if "folder_names" not in user_config:
                raise ValueError("Invalid configuration format")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"{Back.YELLOW}{Fore.BLACK}WARN:{Fore.YELLOW}{Back.RESET} {e}. Using default settings.")
            user_config = default_settings
    else:
        print(f"{Back.YELLOW}{Fore.BLACK}WARN:{Fore.YELLOW}{Back.RESET} Configuration file not found. Using default settings.")
        user_config = default_settings

    return user_config

settings = load_configuration()
categories = settings["folder_names"]

downloads_path = Path(os.path.expanduser("~")) / "Downloads"

def determine_category(file):
    ext = file.suffix[1:].lower()
    
    for cat, exts in categories.items():
        if ext in exts:
            return cat
    
    mime_type, _ = mimetypes.guess_type(file)
    if mime_type:
        if mime_type.startswith('audio/'):
            return 'Audio'
        elif mime_type.startswith('video/'):
            return 'Videos'
        elif mime_type.startswith('image/'):
            return 'Images'
        elif mime_type.startswith('text/'):
            return 'Documents'
        elif mime_type.startswith('application/'):
            if 'pdf' in mime_type:
                return 'Documents'
            elif 'x-python' in mime_type or 'javascript' in mime_type:
                return 'Code'
    
    return 'Miscellaneous'

def organize_files():
    files_found = False
    for item in downloads_path.iterdir():
        if item.is_dir() or item.name.startswith('.'):
            continue

        files_found = True

        cat = determine_category(item)
        cat_path = downloads_path / cat
        
        if not cat_path.exists():
            cat_path.mkdir()

        try:
            shutil.move(str(item), str(cat_path))
            print(f"{Fore.CYAN}Moved {Fore.RESET}{item.name}{Fore.LIGHTBLACK_EX} to {Fore.CYAN}{cat}{Fore.RESET}")
        except shutil.Error as e:
            print(f"{Back.RED}ERR{Back.RESET} {str(e)}")

    if not files_found:
        print("There is nothing to do.")

def main():
    parser = argparse.ArgumentParser(description='Sort your Windows Downloads folder by file types.')
    parser.add_argument('--config', action='store_true', help='Print the location of the configuration file')
    args = parser.parse_args()

    if args.config:
        print(f"Configuration file location: {config_file_path()}")
        return

    organize_files()

if __name__ == '__main__':
    main()
