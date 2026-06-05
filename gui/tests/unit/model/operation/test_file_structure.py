"""
The FileStructure classes are dataclasses, 
therefore we won't test apart from their methods. 
However, in case this changes, these tests must be adjusted!
"""
import pytest

from gui.model.operation import (
    FileStructure,
    SingleFile, 
    Directory,
)


class TestFileStructure:
    def test_file_structure(self):
        file_structure = FileStructure()
        with pytest.raises(NotImplementedError):
            file_structure.matches("")

class TestSingleFile:
    def test_single_file_not_existing(self, mocker):
        # Arrange
        formats = []
        file_path = "/home/raisd/file.txt"
        mocker.patch(
            "PySide6.QtCore.QFileInfo.isFile", 
            return_value = False
        )

        # Act
        single_file = SingleFile(formats=formats)

        # Assert
        assert not single_file.matches(file_path=file_path)

    def test_single_file_existing(self, mocker):
        # Arrange
        formats = []
        file_path = "/home/raisd/file.txt"
        mocker.patch(
            "PySide6.QtCore.QFileInfo.isFile", 
            return_value = True
        )

        # Act
        single_file = SingleFile(formats=formats)

        # Assert
        assert single_file.matches(file_path=file_path)

class TestDirectory:
    def test_directory_not_existing(self, mocker):
        # Arrange
        contents = []
        file_path = "/home/raisd/"
        mocker.patch(
            "PySide6.QtCore.QFileInfo.isDir", 
            return_value = False
        )

        # Act
        directory = Directory(contents=contents)

        # Assert
        assert not directory.matches(file_path=file_path)

    def test_directory_existing(self, mocker):
        # Arrange
        contents = []
        file_path = "/home/raisd/"
        mocker.patch(
            "PySide6.QtCore.QFileInfo.isDir", 
            return_value = True
        )

        # Act
        directory = Directory(contents=contents)

        # Assert
        assert directory.matches(file_path=file_path)