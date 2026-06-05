from dataclasses import dataclass

from PySide6.QtCore import (
    QFileInfo,
)


@dataclass
class FileStructure():
    def matches(self, file_path: str) -> bool:
        raise NotImplementedError()


@dataclass
class SingleFile(FileStructure):
    formats: list[str]

    def matches(self, file_path: str) -> bool:
        file_info = QFileInfo(file_path)
        return file_info.isFile()


@dataclass
class Directory(FileStructure):
    contents: list[FileStructure]

    def matches(self, file_path: str) -> bool:
        # TODO: maybe check directory contents as well?
        file_info = QFileInfo(file_path)
        return file_info.isDir()
