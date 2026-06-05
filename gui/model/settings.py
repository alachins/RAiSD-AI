from yaml import load, Loader, dump

from PySide6.QtCore import (
    QObject, 
    QDir,
    QFileInfo,
    Signal,
)


class Settings(QObject):
    """
    Class to manage the application settings.

    Do not instantiate this class directly. 
    Use the `app_settings` singleton instance instead.
    """

    workspace_path_changed = Signal(QDir)
    executable_file_path_changed = Signal(QFileInfo)
    environment_manager_changed = Signal(int)
    environment_name_changed = Signal(str)
    config_path_changed = Signal(QFileInfo)
    settings_changed = Signal()

    settings_file_path = "gui/settings.yaml"
    environment_managers = ["conda", "micromamba"]

    default_executable_file_path = QFileInfo("RAiSD-AI-ZLIB")
    default_environment_manager = 0
    default_environment_name = "raisd-ai"
    default_config_path = QFileInfo("gui/config.yaml")

    def __init__(
            self,
            workspace_path: QDir | None = None,
            executable_file_path: QFileInfo | None = None,
            environment_manager: int | None = None,
            environment_name: str | None = None,
            config_path: QFileInfo | None = None,
            ):
        """
        Initialize the `Settings` class.
        """
        super().__init__()
        
        self._workspace_path = workspace_path
        self._executable_file_path = executable_file_path
        self._environment_manager = environment_manager
        self._environment_name = environment_name
        self._config_path = config_path

    def from_yaml(self, file_path: str) -> None:
        """
        Fill a settings object with values parsed from a yaml file.
        """
        try: 
            with open(file_path) as f:
                settings_text = f.read() or ""
            settings_obj = load(settings_text, Loader=Loader) or {}
        except FileNotFoundError:
            settings_obj = {}

        # Workspace
        if "workspace" in settings_obj:
            workspace_path = settings_obj["workspace"]
            if not isinstance(workspace_path, str):
                raise ValueError(
                    f"Incorrect type for workspace: '{workspace_path}', "
                    f"type: {type(workspace_path)}, "
                    "Expected string."
                )
            workspace = QDir(workspace_path)
            if workspace.exists():
            # Do not use setters because do not write to file
                self._workspace_path = workspace

        # Executable
        if "executable" in settings_obj:
            executable_file_path = settings_obj["executable"]
            if not isinstance(executable_file_path, str):
                raise ValueError(
                    f"Incorrect type for executable path: '{executable_file_path}', "
                    f"type: {type(executable_file_path)}, "
                    "Expected string."
                )
            executable_file = QFileInfo(executable_file_path)
            if not executable_file.exists():
                raise ValueError(
                    f"Incorrect filepath for executable: '{executable_file_path}', "
                    "This file does not exist."
                )
            self._executable_file_path = executable_file
        if not self._executable_file_path:
            self.executable_file_path = self.default_executable_file_path

        # Environment manager
        if "environment_manager" in settings_obj:
            environment_manager = settings_obj["environment_manager"]
            if not isinstance(environment_manager, str):
                raise ValueError(
                    f"Incorrect type for environment manager: '{environment_manager}', "
                    f"type: {type(environment_manager)}, "
                    "Expected string."
                )
            
            if environment_manager not in self.environment_managers:
                raise ValueError(
                    f"Incorrect environment manager: '{environment_manager}'. "
                    f"Must be one of: {', '.join([str(x) for x in self.environment_managers])}."
                )
            self._environment_manager = self.environment_managers.index(environment_manager)
        if self._environment_manager is None:
            self.environment_manager = self.default_environment_manager

        # Environment name
        if "environment_name" in settings_obj:
            environment_name = settings_obj["environment_name"]
            if not isinstance(environment_name, str):
                raise ValueError(
                    f"Incorrect type for environment name: '{environment_name}', "
                    f"type: {type(environment_name)}, "
                    "Expected string."
                )
            self._environment_name = environment_name
        if not self._environment_name:
            self.environment_name = self.default_environment_name

        # Config file
        if "config_file" in settings_obj:
            config = settings_obj["config_file"]
            if not isinstance(config, str):
                raise ValueError(
                    f"Incorrect type for config file: '{config}', "
                    f"type: {type(config)}, "
                    "Expected string."
                )
            config_file = QFileInfo(config)
            if not config_file.exists():
                raise ValueError(
                    f"Incorrect filepath for config file: '{config}', "
                    "This file does not exist."
                )
            self._config_path = config_file
        if not self._config_path:
            self.config_path = self.default_config_path

        
    @property
    def workspace_path(self) -> QDir:
        """
        Get the current workspace path.

        :return: The current workspace path.
        :rtype: QDir
        """
        if not self._workspace_path:
            raise RuntimeError("Workspace path used before it is set.")
        return self._workspace_path

    @workspace_path.setter
    def workspace_path(self, value: QDir) -> None:
        """
        Set the workspace path.

        :param value: The new workspace path.
        :type value: QDir
        """
        if self._workspace_path != value:
            try:
                with open(self.settings_file_path) as f:
                    settings_text = f.read() or ""
                    settings_obj = load(settings_text, Loader=Loader) or {}            
            except:
                settings_obj = {}
            self._workspace_path = value
            settings_obj["workspace"] = value.absolutePath()
            with open(self.settings_file_path, "w") as f:
                dump(settings_obj, f)
            self.workspace_path_changed.emit(value)
            self.settings_changed.emit()

    @property
    def executable_file_path(self) -> QFileInfo:
        """
        Get the current executable file path.

        :return: The current executable file path.
        :rtype: QFileInfo
        """
        if not self._executable_file_path:
            raise RuntimeError("Executable used before it is set.")
        return self._executable_file_path

    @executable_file_path.setter
    def executable_file_path(self, value: QFileInfo) -> None:
        """
        Set the executable file path.

        :param value: The new executable file path.
        :type value: QFileInfo
        """
        if self._executable_file_path != value:
            try:
                with open(self.settings_file_path) as f:
                    settings_text = f.read() or ""
                    settings_obj = load(settings_text, Loader=Loader) or {}            
            except:
                settings_obj = {}
            self._executable_file_path = value
            settings_obj["executable"] = value.absoluteFilePath()
            with open(self.settings_file_path, "w") as f:
                dump(settings_obj, f)
            self.executable_file_path_changed.emit(value)
            self.settings_changed.emit()

    @property
    def environment_manager(self) -> int:
        """
        Get index of the current environment manager.

        :return: The current environment manager.
        :rtype: int
        """
        if self._environment_manager is None:
            raise RuntimeError("Environment manager used before it is set.")
        return self._environment_manager

    @environment_manager.setter
    def environment_manager(self, value: int) -> None:
        """
        Set index of the environment manager.

        :param value: The new environment manager.
        :type value: int
        """
        if self._environment_manager != value:
            try:
                with open(self.settings_file_path) as f:
                    settings_text = f.read() or ""
                    settings_obj = load(settings_text, Loader=Loader) or {}            
            except:
                settings_obj = {}
            self._environment_manager = value
            settings_obj["environment_manager"] = self.environment_manager_name
            with open(self.settings_file_path, "w") as f:
                dump(settings_obj, f)
            self.environment_manager_changed.emit(value)
            self.settings_changed.emit()

    @property
    def environment_manager_name(self) -> str:
        """
        Get the name of the current environment manager.

        :return: The current environment manager.
        :rtype: str
        """
        if self._environment_manager is None:
            raise RuntimeError("Environment manager used before it is set.")
        return self.environment_managers[self._environment_manager]

    @property
    def environment_name(self) -> str:
        """
        Get the current environment name.

        :return: The current environment name.
        :rtype: str
        """
        if not self._environment_name:
            raise RuntimeError("Environment name used before it is set.")
        return self._environment_name

    @environment_name.setter
    def environment_name(self, value: str) -> None:
        """
        Set the environment name.

        :param value: The new environment name.
        :type value: str
        """
        if self._environment_name != value:
            try:
                with open(self.settings_file_path) as f:
                    settings_text = f.read() or ""
                    settings_obj = load(settings_text, Loader=Loader) or {}            
            except:
                settings_obj = {}
            self._environment_name = value
            settings_obj["environment_name"] = value
            with open(self.settings_file_path, "w") as f:
                dump(settings_obj, f)
            self.environment_name_changed.emit(value)
            self.settings_changed.emit()

    @property
    def config_path(self) -> QFileInfo:
        """
        Get the current config path.

        :return: The current config path.
        :rtype: QFileInfo
        """
        if not self._config_path:
            raise RuntimeError("Config path used before it is set.")
        return self._config_path

    @config_path.setter
    def config_path(self, value: QFileInfo) -> None:
        """
        Set the config path.

        :param value: The new config path.
        :type value: QFileInfo
        """
        if self._config_path != value:
            try:
                with open(self.settings_file_path) as f:
                    settings_text = f.read() or ""
                    settings_obj = load(settings_text, Loader=Loader) or {}            
            except:
                settings_obj = {}
            self._config_path = value
            settings_obj["config_file"] = value.absoluteFilePath()
            with open(self.settings_file_path, "w") as f:
                dump(settings_obj, f)
            self.config_path_changed.emit(value)
            self.settings_changed.emit()

# create a global singleton instance
app_settings = Settings()