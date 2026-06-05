import pytest
import yaml

from PySide6.QtCore import (
    QDir,
    QFileInfo
)

from gui.model.settings import Settings

class TestSettings:
    """Tests for Settings class."""

    @pytest.fixture()
    def correct_settings_obj(self, tmp_path) -> dict:
        (tmp_path / "raisdai").write_text("")
        (tmp_path / "config.yml").write_text("")
        (tmp_path / "workspace").mkdir()
        settings_obj = { # TODO: Mocking QDir exists works but not for QFileInfo.
            "config_file" : f"{tmp_path}/config.yml",
            "environment_manager" : "conda",
            "environment_name" : "utwente",
            "executable" : f"{tmp_path}/raisdai",
            "workspace" : f"{tmp_path}/workspace"
        }
        return settings_obj

    def test_init_empty(self):
        """Test initialisation with no values."""
        # Act
        settings = Settings()

        # Assert
        assert settings._workspace_path == None
        assert settings._executable_file_path == None
        with pytest.raises(RuntimeError) as e:
            x = settings.executable_file_path == None
        assert settings._environment_manager == None
        with pytest.raises(RuntimeError) as e:
            x = settings.environment_manager == None
        with pytest.raises(RuntimeError) as e:
            x = settings.environment_manager_name == None
        assert settings._environment_name == None
        with pytest.raises(RuntimeError) as e:
            x = settings.environment_name == None
        assert settings._config_path == None
        with pytest.raises(RuntimeError) as e:
            x = settings.config_path == None

    def test_init_values(self):
        """Test initialisation with values."""
        # Arrange
        workspace_path = QDir("/home/raisd")
        executable_file_path = QFileInfo("/home/raisd/raisdai")
        environment_manager = 0
        environment_manager_name = Settings.environment_managers[environment_manager]
        environment_name = "raisdai"
        config_path = QFileInfo("/home/raisd/config.yml")

        # Act
        settings = Settings(
            workspace_path=workspace_path,
            executable_file_path=executable_file_path,
            environment_manager=environment_manager,
            environment_name=environment_name,
            config_path=config_path,
        )

        # Assert
        assert settings.workspace_path == workspace_path
        assert settings.executable_file_path == executable_file_path
        assert settings.environment_manager == environment_manager
        assert settings.environment_manager_name == environment_manager_name
        assert settings.environment_name == environment_name
        assert settings.config_path == config_path

    def test_yaml_file_not_found(self, monkeypatch):
        """Test from yaml with nonexistent file."""
        # Arrange
        monkeypatch.setattr(yaml, "load", lambda: FileNotFoundError)
        settings = Settings()

        # Act
        settings.from_yaml("")

        # Assert
        with pytest.raises(RuntimeError) as e:
            x = settings.workspace_path == None
        assert settings.executable_file_path == Settings.default_executable_file_path
        assert settings.environment_manager == Settings.default_environment_manager
        assert settings.environment_name== Settings.default_environment_name
        assert settings.config_path == Settings.default_config_path
    
    def test_yaml_correct_values(self, mocker, correct_settings_obj):
        """Test from yaml with valid values."""
        # Arrange
        mocked_correct_file = mocker.mock_open(read_data=f"{correct_settings_obj}")
        mocker.patch("builtins.open", mocked_correct_file)
        mocker.patch("PySide6.QtCore.QDir.exists", lambda x: True)
        mocker.patch("PySide6.QtCore.QFileInfo.exists", lambda x: True) # notwork why..?

        settings = Settings()

        # Act
        settings.from_yaml("file path")

        # Assert
        assert (settings.workspace_path.absolutePath() == 
                correct_settings_obj["workspace"])
        assert (settings.executable_file_path.absoluteFilePath() == 
                correct_settings_obj["executable"])
        assert (settings.environment_name == 
                correct_settings_obj["environment_name"])
        assert (settings.environment_manager_name == 
                correct_settings_obj["environment_manager"])
        assert (settings.config_path.absoluteFilePath() == 
                correct_settings_obj["config_file"])
    
    def test_yaml_incorrect_workspace_value(self, mocker, correct_settings_obj):
        """Test from yaml with invalid workspace value."""
        # Arrange
        correct_settings_obj["workspace"] = 0
        mocked_empty_file = mocker.mock_open(read_data=f"{correct_settings_obj}")
        mocker.patch("builtins.open", mocked_empty_file)
        settings = Settings()

        # Act, Assert 
        with pytest.raises(ValueError) as e:
            settings.from_yaml("file path")
        assert str(e.value) == "Incorrect type for workspace: '0', type: <class 'int'>, Expected string."

    def test_yaml_incorrect_executable_value(self, mocker, correct_settings_obj):
        """Test from yaml with invalid executable value."""
        # Arrange
        correct_settings_obj["executable"] = 0
        mocked_empty_file = mocker.mock_open(read_data=f"{correct_settings_obj}")
        mocker.patch("builtins.open", mocked_empty_file)
        settings = Settings()

        # Act, Assert 
        with pytest.raises(ValueError) as e:
            settings.from_yaml("file path")
        assert str(e.value) == "Incorrect type for executable path: '0', type: <class 'int'>, Expected string."   

    def test_yaml_incorrect_environment_manager_value(self, mocker, correct_settings_obj):
        """Test from yaml with invalid environment_manager value."""
        # Arrange
        correct_settings_obj["environment_manager"] = 0
        mocked_empty_file = mocker.mock_open(read_data=f"{correct_settings_obj}")
        mocker.patch("builtins.open", mocked_empty_file)
        settings = Settings()

        # Act, Assert 
        with pytest.raises(ValueError) as e:
            settings.from_yaml("file path")
        assert str(e.value) == "Incorrect type for environment manager: '0', type: <class 'int'>, Expected string."   

    def test_yaml_incorrect_environment_name_value(self, mocker, correct_settings_obj):
        """Test from yaml with invalid environment_name value."""
        # Arrange
        correct_settings_obj["environment_name"] = 0
        mocked_empty_file = mocker.mock_open(read_data=f"{correct_settings_obj}")
        mocker.patch("builtins.open", mocked_empty_file)
        settings = Settings()

        # Act, Assert 
        with pytest.raises(ValueError) as e:
            settings.from_yaml("file path")
        assert str(e.value) == "Incorrect type for environment name: '0', type: <class 'int'>, Expected string."   

    def test_yaml_incorrect_config_file_value(self, mocker, correct_settings_obj):
        """Test from yaml with invalid config_file value."""
        # Arrange
        correct_settings_obj["config_file"] = 0
        mocked_empty_file = mocker.mock_open(read_data=f"{correct_settings_obj}")
        mocker.patch("builtins.open", mocked_empty_file)
        settings = Settings()

        # Act, Assert 
        with pytest.raises(ValueError) as e:
            settings.from_yaml("file path")
        assert str(e.value) == "Incorrect type for config file: '0', type: <class 'int'>, Expected string."   

    def test_yaml_nonexistant_executable(self, mocker, correct_settings_obj):
        """Test from yaml with non existant executable value."""
        # Arrange
        correct_settings_obj["executable"] = ""
        mocked_empty_file = mocker.mock_open(read_data=f"{correct_settings_obj}")
        mocker.patch("builtins.open", mocked_empty_file)
        settings = Settings()

        # Act, Assert 
        with pytest.raises(ValueError) as e:
            settings.from_yaml("file path")
        assert str(e.value) == "Incorrect filepath for executable: '', This file does not exist."   

    def test_yaml_nonexistant_environment_manger(self, mocker, correct_settings_obj):
        """Test from yaml with non existant environment_manger value."""
        # Arrange
        correct_settings_obj["environment_manager"] = "incorrect"
        mocked_empty_file = mocker.mock_open(read_data=f"{correct_settings_obj}")
        mocker.patch("builtins.open", mocked_empty_file)
        settings = Settings()

        # Act, Assert 
        with pytest.raises(ValueError) as e:
            settings.from_yaml("file path")
        assert str(e.value) == "Incorrect environment manager: 'incorrect'. Must be one of: conda, micromamba."   

    def test_yaml_nonexistant_config_file(self, mocker, correct_settings_obj):
        """Test from yaml with non existant config_file value."""
        # Arrange
        correct_settings_obj["config_file"] = ""
        mocked_empty_file = mocker.mock_open(read_data=f"{correct_settings_obj}")
        mocker.patch("builtins.open", mocked_empty_file)
        settings = Settings()

        # Act, Assert 
        with pytest.raises(ValueError) as e:
            settings.from_yaml("file path")
        assert str(e.value) == "Incorrect filepath for config file: '', This file does not exist."

    def test_workspace_setter(self, tmp_path, mocker):
        """Test workspace setter writes to file and emits signals."""
        # Arrange
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text("")
        
        settings = Settings()
        workspace = QDir(str(tmp_path))
        
        mocker.patch.object(Settings, 'settings_file_path', str(settings_file))
        
        workspace_changed_spy = mocker.MagicMock()
        settings_changed_spy = mocker.MagicMock()
        settings.workspace_path_changed.connect(workspace_changed_spy)
        settings.settings_changed.connect(settings_changed_spy)
        
        # Act
        settings.workspace_path = workspace
        
        # Assert
        assert settings.workspace_path == workspace
        workspace_changed_spy.assert_called_once_with(workspace)
        settings_changed_spy.assert_called_once()

        assert settings_file.exists()
        content = yaml.load(settings_file.read_text(), Loader=yaml.Loader)
        assert content["workspace"] == str(tmp_path)

    def test_executable_file_path_setter(self, tmp_path, mocker):
        """Test executable file path setter writes to file and emits signals."""
        # Arrange
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text("")
        
        settings = Settings()
        executable_file_path = QFileInfo(settings_file)
        
        mocker.patch.object(Settings, 'settings_file_path', str(settings_file))
        
        executable_file_path_changed_spy = mocker.MagicMock()
        settings_changed_spy = mocker.MagicMock()
        settings.executable_file_path_changed.connect(executable_file_path_changed_spy)
        settings.settings_changed.connect(settings_changed_spy)
        
        # Act
        settings.executable_file_path = executable_file_path
        
        # Assert
        assert settings.executable_file_path == executable_file_path
        executable_file_path_changed_spy.assert_called_once_with(executable_file_path)
        settings_changed_spy.assert_called_once()

        assert settings_file.exists()
        content = yaml.load(settings_file.read_text(), Loader=yaml.Loader)
        assert content["executable"] == str(settings_file)

    def test_environment_manager_setter(self, tmp_path, mocker):
        """Test environment manager setter writes to file and emits signals."""
        # Arrange
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text("")
        
        settings = Settings()
        environment_manager = 1
        
        mocker.patch.object(Settings, 'settings_file_path', str(settings_file))
        
        environment_manager_changed_spy = mocker.MagicMock()
        settings_changed_spy = mocker.MagicMock()
        settings.environment_manager_changed.connect(environment_manager_changed_spy)
        settings.settings_changed.connect(settings_changed_spy)
        
        # Act
        settings.environment_manager = environment_manager
        
        # Assert
        assert settings.environment_manager == environment_manager
        environment_manager_changed_spy.assert_called_once_with(environment_manager)
        settings_changed_spy.assert_called_once()

        assert settings_file.exists()
        content = yaml.load(settings_file.read_text(), Loader=yaml.Loader)
        assert content["environment_manager"] == settings.environment_managers[1]

    def test_environment_name_setter(self, tmp_path, mocker):
        """Test environment name setter writes to file and emits signals."""
        # Arrange
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text("")
        
        settings = Settings()
        environment_name = "raise"
        
        mocker.patch.object(Settings, 'settings_file_path', str(settings_file))
        
        environment_name_changed_spy = mocker.MagicMock()
        settings_changed_spy = mocker.MagicMock()
        settings.environment_name_changed.connect(environment_name_changed_spy)
        settings.settings_changed.connect(settings_changed_spy)
        
        # Act
        settings.environment_name = environment_name
        
        # Assert
        assert settings.environment_name == environment_name
        environment_name_changed_spy.assert_called_once_with(environment_name)
        settings_changed_spy.assert_called_once()

        assert settings_file.exists()
        content = yaml.load(settings_file.read_text(), Loader=yaml.Loader)
        assert content["environment_name"] == "raise"

    def test_config_path_setter(self, tmp_path, mocker):
        """Test config path setter writes to file and emits signals."""
        # Arrange
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text("")
        
        settings = Settings()
        config_path = QFileInfo(settings_file)
        
        mocker.patch.object(Settings, 'settings_file_path', str(settings_file))
        
        config_path_changed_spy = mocker.MagicMock()
        settings_changed_spy = mocker.MagicMock()
        settings.config_path_changed.connect(config_path_changed_spy)
        settings.settings_changed.connect(settings_changed_spy)
        
        # Act
        settings.config_path = config_path
        
        # Assert
        assert settings.config_path == config_path
        config_path_changed_spy.assert_called_once_with(config_path)
        settings_changed_spy.assert_called_once()

        assert settings_file.exists()
        content = yaml.load(settings_file.read_text(), Loader=yaml.Loader)
        assert content["config_file"] == str(settings_file)

    def test_workspace_setter_no_settings_file(self, tmp_path, mocker):
        """Test workspace setter writes to file and emits signals."""
        # Arrange
        settings_file = tmp_path / "settings.yaml"
        
        settings = Settings()
        workspace = QDir(str(tmp_path))
        
        mocker.patch.object(Settings, 'settings_file_path', str(settings_file))
        
        workspace_changed_spy = mocker.MagicMock()
        settings_changed_spy = mocker.MagicMock()
        settings.workspace_path_changed.connect(workspace_changed_spy)
        settings.settings_changed.connect(settings_changed_spy)
        
        # Act
        settings.workspace_path = workspace
        
        # Assert
        assert settings.workspace_path == workspace
        workspace_changed_spy.assert_called_once_with(workspace)
        settings_changed_spy.assert_called_once()

        assert settings_file.exists()
        content = yaml.load(settings_file.read_text(), Loader=yaml.Loader)
        assert content["workspace"] == str(tmp_path)

    def test_executable_file_path_setter_no_settings_file(self, tmp_path, mocker):
        """Test executable file path setter writes to file and emits signals."""
        # Arrange
        settings_file = tmp_path / "settings.yaml"
        
        settings = Settings()
        executable_file_path = QFileInfo(settings_file)
        
        mocker.patch.object(Settings, 'settings_file_path', str(settings_file))
        
        executable_file_path_changed_spy = mocker.MagicMock()
        settings_changed_spy = mocker.MagicMock()
        settings.executable_file_path_changed.connect(executable_file_path_changed_spy)
        settings.settings_changed.connect(settings_changed_spy)
        
        # Act
        settings.executable_file_path = executable_file_path
        
        # Assert
        assert settings.executable_file_path == executable_file_path
        executable_file_path_changed_spy.assert_called_once_with(executable_file_path)
        settings_changed_spy.assert_called_once()

        assert settings_file.exists()
        content = yaml.load(settings_file.read_text(), Loader=yaml.Loader)
        assert content["executable"] == str(settings_file)

    def test_environment_manager_setter_no_settings_file(self, tmp_path, mocker):
        """Test environment manager setter writes to file and emits signals."""
        # Arrange
        settings_file = tmp_path / "settings.yaml"
        
        settings = Settings()
        environment_manager = 1
        
        mocker.patch.object(Settings, 'settings_file_path', str(settings_file))
        
        environment_manager_changed_spy = mocker.MagicMock()
        settings_changed_spy = mocker.MagicMock()
        settings.environment_manager_changed.connect(environment_manager_changed_spy)
        settings.settings_changed.connect(settings_changed_spy)
        
        # Act
        settings.environment_manager = environment_manager
        
        # Assert
        assert settings.environment_manager == environment_manager
        environment_manager_changed_spy.assert_called_once_with(environment_manager)
        settings_changed_spy.assert_called_once()

        assert settings_file.exists()
        content = yaml.load(settings_file.read_text(), Loader=yaml.Loader)
        assert content["environment_manager"] == settings.environment_managers[1]

    def test_environment_name_setter_no_settings_file(self, tmp_path, mocker):
        """Test environment name setter writes to file and emits signals."""
        # Arrange
        settings_file = tmp_path / "settings.yaml"
        
        settings = Settings()
        environment_name = "raise"
        
        mocker.patch.object(Settings, 'settings_file_path', str(settings_file))
        
        environment_name_changed_spy = mocker.MagicMock()
        settings_changed_spy = mocker.MagicMock()
        settings.environment_name_changed.connect(environment_name_changed_spy)
        settings.settings_changed.connect(settings_changed_spy)
        
        # Act
        settings.environment_name = environment_name
        
        # Assert
        assert settings.environment_name == environment_name
        environment_name_changed_spy.assert_called_once_with(environment_name)
        settings_changed_spy.assert_called_once()

        assert settings_file.exists()
        content = yaml.load(settings_file.read_text(), Loader=yaml.Loader)
        assert content["environment_name"] == "raise"

    def test_config_path_setter_no_settings_file(self, tmp_path, mocker):
        """Test config path setter writes to file and emits signals."""
        # Arrange
        settings_file = tmp_path / "settings.yaml"
        
        settings = Settings()
        config_path = QFileInfo(settings_file)
        
        mocker.patch.object(Settings, 'settings_file_path', str(settings_file))
        
        config_path_changed_spy = mocker.MagicMock()
        settings_changed_spy = mocker.MagicMock()
        settings.config_path_changed.connect(config_path_changed_spy)
        settings.settings_changed.connect(settings_changed_spy)
        
        # Act
        settings.config_path = config_path
        
        # Assert
        assert settings.config_path == config_path
        config_path_changed_spy.assert_called_once_with(config_path)
        settings_changed_spy.assert_called_once()

        assert settings_file.exists()
        content = yaml.load(settings_file.read_text(), Loader=yaml.Loader)
        assert content["config_file"] == str(settings_file)

    def test_all_settings_setter(self, tmp_path, mocker):
        """Test if multiple setters together modify the file and emit signals."""
        # Arrange
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text("")
        
        settings = Settings()
        mocker.patch.object(Settings, 'settings_file_path', str(settings_file))
        settings_changed_spy = mocker.MagicMock()
        settings.settings_changed.connect(settings_changed_spy)
        
        workspace = QDir(str(tmp_path))
        workspace_changed_spy = mocker.MagicMock()
        settings.workspace_path_changed.connect(workspace_changed_spy)
        
        executable_file_path = QFileInfo(settings_file)
        executable_file_path_changed_spy = mocker.MagicMock()
        settings.executable_file_path_changed.connect(executable_file_path_changed_spy)

        environment_manager = 1
        environment_manager_changed_spy = mocker.MagicMock()
        settings.environment_manager_changed.connect(environment_manager_changed_spy)

        environment_name = "raise"
        environment_name_changed_spy = mocker.MagicMock()
        settings.environment_name_changed.connect(environment_name_changed_spy)

        config_path = QFileInfo(settings_file)
        config_path_changed_spy = mocker.MagicMock()
        settings.config_path_changed.connect(config_path_changed_spy)

        # Act
        settings.workspace_path = workspace
        settings.executable_file_path = executable_file_path
        settings.environment_manager = environment_manager
        settings.environment_name = environment_name
        settings.config_path = config_path
        
        # Assert
        settings_changed_spy.assert_has_calls([]*5)

        assert settings.workspace_path == workspace
        workspace_changed_spy.assert_called_once_with(workspace)
        assert settings.executable_file_path == executable_file_path
        executable_file_path_changed_spy.assert_called_once_with(executable_file_path)
        assert settings.environment_manager == environment_manager
        environment_manager_changed_spy.assert_called_once_with(environment_manager)
        assert settings.environment_name == environment_name
        environment_name_changed_spy.assert_called_once_with(environment_name)
        assert settings.config_path == config_path
        config_path_changed_spy.assert_called_once_with(config_path)

        assert settings_file.exists()
        content = yaml.load(settings_file.read_text(), Loader=yaml.Loader)
        assert content["workspace"] == str(tmp_path)
        assert content["executable"] == str(settings_file)
        assert content["environment_manager"] == settings.environment_managers[1]
        assert content["environment_name"] == environment_name
        assert content["config_file"] == str(settings_file)
