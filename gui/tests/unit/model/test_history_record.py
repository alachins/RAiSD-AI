import pytest
import tempfile
import json
from unittest.mock import PropertyMock
from datetime import datetime
from PySide6.QtCore import QDir
from gui.model.settings import app_settings
from gui.model.history_record import HistoryRecord
import gui.model.history_record as history_record


class TestHistoryRecord:
    """Tests for HistoryRecord class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.name = "name"
        self.command1 = "command1"
        self.command2 = "command2"
        self.commands = [self.command1, self.command2]
        self.index = 0
        self.trees = [{},{}]
        self.operations = {
            "index": self.index,
            "trees": self.trees
        }
        self.parameter = 1
        self.parameters = {"param": self.parameter}
        self.time_completed = datetime.now()

        self.history_record = HistoryRecord(
            name=self.name,
            commands=self.commands,
            operations=self.operations,
            parameters=self.parameters,
            time_completed=self.time_completed
        )

    def test_init_values(self):
        """Test HistoryRecord values are set correcly through init."""
        assert self.history_record.name == self.name
        assert self.history_record.commands == self.commands
        assert self.history_record.operations == self.operations
        assert self.history_record.parameters == self.parameters
        assert self.history_record.time_completed == self.time_completed

    def test_from_history_file_not_found(self, mocker):
        """Test that a nonexisting history file is handled correctly."""
        # Arrange
        dict = ""
        temp_dir = tempfile.TemporaryDirectory()
        qdir = QDir(temp_dir.name)
        mocker.patch.object(
            type(history_record.app_settings), 
            "workspace_path",
            new_callable=PropertyMock,
            return_value=qdir)
        
        # Act
        history_records = HistoryRecord.from_history_file()

        # Assert
        assert history_records == []
    
    def test_from_history_file_emtpy(self, mocker):
        """Test that an empty history file is handled correctly."""
        # Arrange
        dict = ""
        mocked_history_file = mocker.mock_open(read_data=f"{dict}")
        mocker.patch("builtins.open", mocked_history_file)
        mocker.patch.object(
            type(history_record.app_settings), 
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir.current())
        
        # Act
        history_records = HistoryRecord.from_history_file()

        # Assert
        assert history_records == []

    def test_from_history_file_incorrect_format(self, mocker):
        """Test that a history file with an incorrect format is handled correctly."""
        # Arrange
        dict = f"""[]"""
        mocked_history_file = mocker.mock_open(read_data=f"{dict}")
        mocker.patch("builtins.open", mocked_history_file)
        mocker.patch.object(
            type(history_record.app_settings), 
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir.current())
        
        # Assert
        with pytest.raises(ValueError, 
            match=r"Incorrect format in .history.json: \[\]. Expected dict."):
            history_records = HistoryRecord.from_history_file()

    def test_from_history_file_incorrect_keys(self, mocker):
        """Test that a history file containing a wrongly formatted run is handled
        correctly."""
        # Arrange
        dict = f"""{{"hi": []}}"""
        mocked_history_file = mocker.mock_open(read_data=f"{dict}")
        mocker.patch("builtins.open", mocked_history_file)
        mocker.patch.object(
            type(history_record.app_settings), 
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir.current())
        
        # Assert
        with pytest.raises(ValueError, 
            match=r"Incorrect format in .history.json for hi: \[\]. Expected dict."):
            history_records = HistoryRecord.from_history_file()
    
    def test_from_history_file_incorrect_value(self, mocker):
        """Test that a history file containing a wrongly formatted run is handled
        correctly."""
        # Arrange
        dict = f"""{{"hi": {{}}}}"""
        mocked_history_file = mocker.mock_open(read_data=f"{dict}")
        mocker.patch("builtins.open", mocked_history_file)
        mocker.patch.object(
            type(history_record.app_settings), 
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir.current())
        
        # Act
        history_records = HistoryRecord.from_history_file()

        # Assert
        assert history_records == []
            
    def test_from_history_file_single_record(self, mocker):
        """Test that a history file containing a single completed run is parsed
        correctly."""
        # Arrange
        dict = f"""{{"hi": {{"name": "{self.name}", 
            "commands": ["{self.command1}","{self.command2}"], 
            "operations": {{"index": {self.index}, 
            "trees": {self.trees}}}, 
            "parameters": {{"param": {self.parameter}}},
            "time_completed": "{str(self.time_completed)}"}}}}"""
        mocked_history_file = mocker.mock_open(read_data=f"{dict}")
        mocker.patch("builtins.open", mocked_history_file)
        mocker.patch.object(
            type(history_record.app_settings), 
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir.current())
        
        # Act
        history_records = HistoryRecord.from_history_file()

        # Assert
        assert len(history_records) is 1
        record = history_records[0]
        assert isinstance(record, HistoryRecord)
        assert record.name == self.name
        assert record.commands == self.commands
        assert record.operations == self.operations
        assert record.parameters == self.parameters
        assert record.time_completed == self.time_completed

    def test_from_history_file_multiple_records(self, mocker):
        """"Test that a history file containing multiple records is parsed 
        correctly."""
        # Arrange
        dict = f"""{{"hi": {{"name": "{self.name}", 
            "commands": ["{self.command1}","{self.command2}"], 
            "operations": {{"index": {self.index}, 
            "trees": {self.trees}}}, 
            "parameters": {{"param": {self.parameter}}},
            "time_completed": "{str(self.time_completed)}"}},
            "hello": {{"name": "{self.name}", 
            "commands": ["{self.command1}","{self.command2}"], 
            "operations": {{"index": {self.index}, 
            "trees": {self.trees}}}, 
            "parameters": {{"param": {self.parameter}}},
            "time_completed": "{str(self.time_completed)}"}}}}"""
        mocked_history_file = mocker.mock_open(read_data=f"{dict}")
        mocker.patch("builtins.open", mocked_history_file)
        mocker.patch.object(
            type(history_record.app_settings), 
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir.current())
        
        # Act
        history_records = HistoryRecord.from_history_file()

        # Assert
        assert len(history_records) is 2
        record = history_records[0]
        assert isinstance(record, HistoryRecord)
        assert record.name == self.name
        assert record.commands == self.commands
        assert record.operations == self.operations
        assert record.parameters == self.parameters
        assert record.time_completed == self.time_completed
        record = history_records[1]
        assert isinstance(record, HistoryRecord)
        assert record.name == self.name
        assert record.commands == self.commands
        assert record.operations == self.operations
        assert record.parameters == self.parameters
        assert record.time_completed == self.time_completed
        
    def test_from_dict_name(self):
        """Test that the name attribute is collected correctly from a dict."""
        # Arrange
        dict_empty = {}
        dict_wrong_format = {"name": 5}
        dict_correct = {"name": self.name}

        # Assert
        with pytest.raises(ValueError, match="Missing run name. Expected string."):
            HistoryRecord.from_dict(dict_empty)
        
        with pytest.raises(ValueError, match="Invalid run name: 5. Expected string."):
            HistoryRecord.from_dict(dict_wrong_format)

        with pytest.raises(ValueError, match=r"[^name]"):
            HistoryRecord.from_dict(dict_correct)

    def test_from_dict_commands(self):
        """Test that the commands attribute is collected correctly from a dict."""
        # Arrange
        dict_missing = {"name": self.name}
        dict_wrong_format = {"name": self.name, "commands": 5}
        dict_wrong_inner_format = {"name": self.name, "commands": [7, 2]}
        dict_correct = {"name": self.name, "commands": self.commands}

        # Assert
        with pytest.raises(ValueError, match="Missing commands. Expected list."):
            HistoryRecord.from_dict(dict_missing)

        with pytest.raises(ValueError, match="Invalid commands object: 5. Expected list."):
            HistoryRecord.from_dict(dict_wrong_format)

        with pytest.raises(ValueError, match=r"Invalid command type: (7|2). Expected string."):
            HistoryRecord.from_dict(dict_wrong_inner_format)

        with pytest.raises(ValueError, match=r"[^command]"):
            HistoryRecord.from_dict(dict_correct)

    def test_from_dict_operations(self):
        """Test that the operations attribute is collected correctly from a dict."""
        # Arrange
        dict_missing = {"name": self.name, "commands": self.commands}
        dict_wrong_format = {"name": self.name, "commands": self.commands, "operations": 5}
        dict_correct = {"name": self.name, "commands": self.commands, "operations": self.operations}

        # Assert
        with pytest.raises(ValueError, match="Missing operations. Expected dict."):
            HistoryRecord.from_dict(dict_missing)

        with pytest.raises(ValueError, match="Invalid operations type: 5. Expected dictionary."):
            HistoryRecord.from_dict(dict_wrong_format)
        
        with pytest.raises(ValueError, match=r"[^operation]"):
            HistoryRecord.from_dict(dict_correct)

    def test_from_dict_tree_index(self):
        """Test that the tree index attribute in the operations dictionary is 
        collected correctly."""
        # Arrange
        dict_missing = {"name": self.name, "commands": self.commands, 
                        "operations": {}}
        dict_wrong_format = {"name": self.name, "commands": self.commands, 
                        "operations": {"index": "HI"}}
        dict_correct = {"name": self.name, "commands": self.commands, 
                        "operations": {"index": 1}}
        
        # Assert
        with pytest.raises(ValueError, match="Missing index in operations dictionary. Expected integer."):
            HistoryRecord.from_dict(dict_missing)

        with pytest.raises(ValueError, match="Invalid tree index: HI. Expected integer."):
            HistoryRecord.from_dict(dict_wrong_format)
        
        with pytest.raises(ValueError, match=r"[^index]"):
            HistoryRecord.from_dict(dict_correct)

    def test_from_dict_operation_trees(self):
        """Test that the tree index attribute in the operations dictionary is 
        collected correctly."""
        # Arrange
        dict_missing = {"name": self.name, "commands": self.commands, 
                        "operations": {"index": 1}}
        dict_wrong_format = {"name": self.name, "commands": self.commands, 
                        "operations": {"index": 1, "trees": 3}}
        dict_wrong_inner_format = {"name": self.name, "commands": self.commands, 
                        "operations": {"index": 1, "trees": [6]}}
        dict_correct = {"name": self.name, "commands": self.commands, 
                        "operations": self.operations}
        
        # Assert
        with pytest.raises(ValueError, match="Missing trees in operations dictionary. Expected list."):
            HistoryRecord.from_dict(dict_missing)

        with pytest.raises(ValueError, match='Invalid operations type: 3. Expected list.'):
            HistoryRecord.from_dict(dict_wrong_format)

        with pytest.raises(ValueError, match='Invalid operation type: 6. Expected dict.'):
            HistoryRecord.from_dict(dict_wrong_inner_format)
        
        with pytest.raises(ValueError, match=r"[^tree]"):
            HistoryRecord.from_dict(dict_correct)

    def test_from_dict_parameters(self):
        """Test that the parameters attribute is collected correctly from a 
        dictionary."""
        # Arrange
        dict_wrong_format = {"name": self.name, "commands": self.commands, 
                        "operations": self.operations, "parameters": 6}
        dict_correct = {"name": self.name, "commands": self.commands, 
                        "operations": self.operations, "parameters": self.parameters}
        
        # Assert
        with pytest.raises(ValueError, match='Invalid parameter object: 6. Expected dictionary.'):
            HistoryRecord.from_dict(dict_wrong_format)
        
        with pytest.raises(ValueError, match=r"[^parameter]"):
            HistoryRecord.from_dict(dict_correct)

    def test_from_dict_time_completed(self):
        """Test that the time_completed attribute is collected correctly
        from a dictionary."""
        # Arrange
        dict_missing = {"name": self.name, "commands": self.commands, 
                        "operations": self.operations, 
                        "parameters": self.parameters}
        dict_wrong_format = {"name": self.name, "commands": self.commands, 
                        "operations": self.operations, 
                        "parameters": self.parameters,
                        "time_completed": 6}
        dict_correct = {"name": self.name, "commands": self.commands, 
                        "operations": self.operations, 
                        "parameters": self.parameters,
                        "time_completed": str(self.time_completed)}
        
        # Act
        history_record = HistoryRecord.from_dict(dict_correct)
        
        # Assert
        with pytest.raises(ValueError, match="Missing time_completed. Expected string."):
            HistoryRecord.from_dict(dict_missing)

        with pytest.raises(ValueError, match='Invalid time_completed type: 6. Expected string.'):
            HistoryRecord.from_dict(dict_wrong_format)
        
        assert isinstance(history_record, HistoryRecord)

    def test_from_dict_values(self):
        """Test that a complete HistoryRecord is correctly collected from a 
        dictionary."""
        # Arrange
        dict = {
            "name": self.name, 
            "commands": self.commands, 
            "operations": self.operations, 
            "parameters": self.parameters,
            "time_completed": str(self.time_completed)
        }

        # Act
        history_record = HistoryRecord.from_dict(dict)

        # Assert
        assert history_record.name == self.history_record.name
        assert history_record.commands == self.history_record.commands
        assert history_record.operations == self.history_record.operations
        assert history_record.parameters == self.history_record.parameters
        assert history_record.time_completed == self.history_record.time_completed    

    def test_save_to_history_one_record(self,tmp_path, mocker):
        """Test that a record is correctly saved to history."""
        # Arrange
        mocker.patch.object(
            type(history_record.app_settings), 
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir(str(tmp_path)))

        history_file = tmp_path / ".history.json"
        history_file.write_text("{}")
        
        # Act
        self.history_record.save_to_history()

        # Assert
        with open(QDir(str(tmp_path)).absoluteFilePath(".history.json")) as f:
            history = json.load(f)
            assert isinstance(history, dict)
            assert len(history.keys()) == 1
            
            record = history[f"{str(self.time_completed)}-{self.name}"]
            assert record["name"] == self.name
            assert record["commands"] == self.commands
            assert record["operations"] == self.operations
            assert record["parameters"] == self.parameters
            assert record["time_completed"] == str(self.time_completed)

    def test_save_to_history_multiple_records(self,tmp_path, mocker):
        """Test that multiple records are correctly saved to history."""
        # Arrange
        mocker.patch.object(
            type(history_record.app_settings), 
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir(str(tmp_path)))

        history_file = tmp_path / ".history.json"
        history_file.write_text("{}")

        now = datetime.now()
        new_history_record = HistoryRecord(
            name="test",
            commands=["command", "and one more"],
            operations={"index": 2, "trees":[{}]},
            parameters={},
            time_completed=now
        )
        
        # Act
        new_history_record.save_to_history()
        self.history_record.save_to_history()

        # Assert
        with open(QDir(str(tmp_path)).absoluteFilePath(".history.json")) as f:
            history = json.load(f)
            assert isinstance(history, dict)
            assert len(history.keys()) == 2

            record = history[f"{str(now)}-test"]
            assert record["name"] == "test"
            assert record["commands"] == ["command", "and one more"]
            assert record["operations"] == {"index": 2, "trees":[{}]}
            assert record["parameters"] == {}
            assert record["time_completed"] == str(now)

            record = history[f"{str(self.time_completed)}-{self.name}"]
            assert record["name"] == self.name
            assert record["commands"] == self.commands
            assert record["operations"] == self.operations
            assert record["parameters"] == self.parameters
            assert record["time_completed"] == str(self.time_completed)
    
    def test_save_to_history_no_file(self,tmp_path, mocker):
        """Test that a record is correctly saved to history even if no history 
        file exists."""
        # Arrange
        mocker.patch.object(
            type(history_record.app_settings), 
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir(str(tmp_path)))
        
        # Act
        self.history_record.save_to_history()

        # Assert
        with open(QDir(str(tmp_path)).absoluteFilePath(".history.json")) as f:
            history = json.load(f)
            assert isinstance(history, dict)
            assert len(history.keys()) == 1
            
            for key in history.keys():
                record = history[key]
                assert record["name"] == self.name
                assert record["commands"] == self.commands
                assert record["operations"] == self.operations
                assert record["parameters"] == self.parameters
                assert record["time_completed"] == str(self.time_completed)

    def test_save_to_history_empty_file(self,tmp_path, mocker):
        """Test that a record is correctly saved to history even if the history
        file is empty."""
        # Arrange
        mocker.patch.object(
            type(history_record.app_settings), 
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir(str(tmp_path)))

        history_file = tmp_path / ".history.json"
        history_file.write_text("")
        
        # Act
        self.history_record.save_to_history()

        # Assert
        with open(QDir(str(tmp_path)).absoluteFilePath(".history.json")) as f:
            history = json.load(f)
            assert isinstance(history, dict)
            assert len(history.keys()) == 1
            
            for key in history.keys():
                record = history[key]
                assert record["name"] == self.name
                assert record["commands"] == self.commands
                assert record["operations"] == self.operations
                assert record["parameters"] == self.parameters
                assert record["time_completed"] == str(self.time_completed)
    
    def test_save_to_history_wrong_format_file(self,tmp_path, mocker):
        """Test that a record is correctly saved to history even if the file 
        has the wrong format."""
        # Arrange
        mocker.patch.object(
            type(history_record.app_settings), 
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir(str(tmp_path)))

        history_file = tmp_path / ".history.json"
        history_file.write_text("[]")
        
        # Act
        self.history_record.save_to_history()

        # Assert
        with open(QDir(str(tmp_path)).absoluteFilePath(".history.json")) as f:
            history = json.load(f)
            assert isinstance(history, dict)
            assert len(history.keys()) == 1
            
            for key in history.keys():
                record = history[key]
                assert record["name"] == self.name
                assert record["commands"] == self.commands
                assert record["operations"] == self.operations
                assert record["parameters"] == self.parameters
                assert record["time_completed"] == str(self.time_completed)

    def test_to_dict(self):
        # Act
        dictionary = self.history_record.to_dict()


        # Assert
        assert isinstance(dictionary, dict)

        assert "name" in dictionary
        assert isinstance(dictionary["name"], str)
        assert dictionary["name"] == self.history_record.name

        assert "commands" in dictionary
        assert isinstance(dictionary["commands"], list)
        for command in dictionary["commands"]:
            assert isinstance(command, str)
        assert dictionary["commands"] == self.history_record.commands

        assert "operations" in dictionary
        assert isinstance(dictionary["operations"], dict)
        assert "index" in dictionary["operations"]
        assert isinstance(dictionary["operations"]["index"], int)
        assert "trees" in dictionary["operations"]
        assert isinstance(dictionary["operations"]["trees"], list)
        assert dictionary["operations"] == self.history_record.operations
        
        assert "time_completed" in dictionary
        assert isinstance(dictionary["time_completed"], str)
        assert dictionary["time_completed"] == str(self.time_completed)

    def test_to_and_from_dict(self):
        # Act
        dictionary = self.history_record.to_dict()
        history_record = HistoryRecord.from_dict(dictionary)

        # Assert
        assert history_record.name == self.history_record.name
        assert history_record.commands == self.history_record.commands
        assert history_record.operations == self.history_record.operations
        assert history_record.parameters == self.history_record.parameters
        assert history_record.time_completed == self.history_record.time_completed    
