import json

from datetime import datetime

from gui.model.settings import app_settings
from gui.model.parameter import (
    Parameter,
    MultiParameter,
    OptionalParameter
)

class HistoryRecord():
    """
    A history record holds the information of a completed run necessary to
    show in the history.
    """
    def __init__(
            self,
            name: str,
            commands: list[str],
            operations: dict,
            parameters: dict,
            time_completed: datetime
    ):
        self._name = name
        self._commands = commands
        self._operations = operations
        self._parameters = parameters
        self._time_completed = time_completed

    @classmethod
    def from_history_file(cls) -> list["HistoryRecord"]:
        """
        Class method that retrieves data from a history file in the workspace
        and parses it into a list of history records.
        """
        history_records = []
        try: 
            with open(app_settings.workspace_path.absoluteFilePath(".history.json"), "r") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError(
                        f"Incorrect format in .history.json: {data}. "
                        + "Expected dict."
                    )
                for key in data.keys():
                    if not isinstance(data[key], dict):
                        raise ValueError(
                            f"Incorrect format in .history.json for {key}: {data[key]}. "
                            + "Expected dict."
                        )
                    try:
                        history_records.append(cls.from_dict(data[key]))
                    except ValueError as e:
                        print(f"Error parsing {key}")
                        print(e)
                return history_records
        except FileNotFoundError:
            print("No history file found in this workspace")
            return []
        except json.JSONDecodeError as e:
            print(e)
            print("History file not parseable. Might be empty or formatted incorrectly")
            return []
        
    @classmethod
    def from_dict(cls, dictionary: dict) -> "HistoryRecord":
        """
        Class method that takes a dictionary and parses it to construct a 
        history record. 

        :param dictionary: the dictionary that contains the record data
        :type dictionary: dict
        """
        if "name" not in dictionary:
            raise ValueError(
                f"Missing run name. Expected string."
            )
        
        name = dictionary.get("name")
        if not isinstance(name, str):
            raise ValueError(
                f"Invalid run name: {name}. "
                + "Expected string."
            )

        if "commands" not in dictionary:
            raise ValueError(
                f"Missing commands. Expected list."
            )
        commands = dictionary.get("commands")
        if not isinstance(commands, list):
            raise ValueError(
                f"Invalid commands object: {commands}. "
                + "Expected list."
            )
        
        for command in commands:
            if not isinstance(command, str):
                raise ValueError(
                    f"Invalid command type: {command}. "
                    + "Expected string."
                )
        
        if "operations" not in dictionary:
            raise ValueError("Missing operations. Expected dict.")
        
        operations = dictionary.get("operations")
        if not isinstance(operations, dict):
            raise ValueError(
                f"Invalid operations type: {operations}. "
                + "Expected dictionary."
            )
        
        if "index" not in operations:
            raise ValueError("Missing index in operations dictionary. Expected integer.")
        tree_index = operations.get("index")
        if not isinstance(tree_index, int):
            raise ValueError(
                f"Invalid tree index: {tree_index}. "
                + "Expected integer."
            )

        if "trees" not in operations:
            raise ValueError("Missing trees in operations dictionary. Expected list.")
        operations_list = operations.get("trees")
        if not isinstance(operations_list, list):
            raise ValueError(
                f"Invalid operations type: {operations_list}. "
                + "Expected list."
            )
        
        for operation in operations_list:
            if not isinstance(operation, dict):
                raise ValueError(
                    f"Invalid operation type: {operation}. "
                    + "Expected dictionary."
                )
            
        parameters = dictionary.get("parameters")
        if not isinstance(parameters, dict):
            raise ValueError(
                f"Invalid parameter object: {parameters}. "
                + "Expected dictionary."
            )

        if "time_completed" not in dictionary:
            raise ValueError("Missing time_completed. Expected string.")
        time_completed = dictionary.get("time_completed")
        if not isinstance(time_completed, str):
            raise ValueError(
                f"Invalid time_completed type: {time_completed}. "
                + "Expected string."
            )
        time_completed = datetime.strptime(time_completed, "%Y-%m-%d %H:%M:%S.%f")

        return cls(name, commands, operations, parameters, time_completed)

    def save_to_history(self) -> None:
        """
        Saves current run result to the history file of the workspace.
        """
        if not app_settings.workspace_path.exists(".history.json"):
            # If no history file exists
            with open(app_settings.workspace_path.absoluteFilePath(".history.json"), "w") as f:
                history = {}
                history[f"{self.time_completed}-{self.name}"] = self.to_dict()
                json.dump(history, f, indent=4, default=str)
        else:    
            # If a file exists
            with open(app_settings.workspace_path.absoluteFilePath(".history.json"), "r+") as f:
                history = {}
                try:
                    history = json.load(f)
                except:
                    # File could not be parsed
                    print("Problem reading history file: might be empty or incorrect format.")
                    print("Corrupted history file will be overwritten")
                    history = {}
                    f.truncate(0)
                if not isinstance(history, dict):
                    print("History file has incorrect format.")
                    history = {}
                history[f"{self.time_completed}-{self.name}"] = self.to_dict()
                f.seek(0)
                json.dump(history, f, indent=4, default=str)

    def to_dict(self) -> dict:
        """
        Makes a dictionary with the information of the current RunResult. This
        is used to store in the history file.
        """

        return {
            "name": self.name,
            "commands": self.commands,
            "operations": self.operations,
            "parameters": self.parameters,
            "time_completed": str(self.time_completed)
        }

    @property
    def name(self) -> str:
        """
        The name of the execution. This is the run_id of the parameter
        group list and run result. This is also the name of the directory
        where the output of the operation is stored.
        """
        return self._name
    
    @property
    def commands(self) -> list[str]:
        """
        The commands of an execution.
        """
        return self._commands

    @property
    def operations(self) -> dict:
        """
        The operatons that were run during an execution. Stored as a dictionary
        from operation name to a boolean that signifies whether the operation
        was performed.
        """
        return self._operations

    @property
    def parameters(self) -> dict:
        """
        A dictionary that holds the parameters that were used, with their 
        values.
        """
        return self._parameters
    
    @property
    def time_completed(self) -> datetime:
        """
        The time at which the run was completed. This is used to show how long 
        ago a run was completed.
        """
        return self._time_completed
    