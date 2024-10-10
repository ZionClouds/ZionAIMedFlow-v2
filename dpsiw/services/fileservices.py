

import logging
import os


def read_text_file(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()


def get_file_name_and_extension(file_path: str) -> tuple:
    file_name, file_extension = os.path.splitext(os.path.basename(file_path))
    return file_name, file_extension


def write_text_file(filename: str, content: str) -> None:
    with open(filename, "w") as f:
        f.write(content)


def append_text_file(filename: str, content: str) -> None:
    with open(filename, "a") as f:
        f.write(content)


def delete_file(file_path: str) -> None:
    try:
        os.remove(file_path)
    except FileNotFoundError:
        logging.error(f"File {file_path} not found")
