from re import compile
from typing import Any, Iterator
from yaml import load, Loader
from datetime import datetime

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from gui.model.settings import app_settings
from gui.model.operation import (
    Operation,
    OperationTree,
    FileStructure,
    SingleFile,
    Directory,
)
from gui.model.history_record import HistoryRecord
from gui.model.parameter import (
    Constraint,
    IntervalConstraint,
    EvenConstraint,
    MaxLengthConstraint,
    RegexConstraint,
    ParameterGroup,
    Parameter,
    OptionalParameter,
    MultiParameter,
    CountedMultiParameter,
    BoolParameter,
    IntParameter,
    FloatParameter,
    EnumParameter,
    StringParameter,
    StringTableParameter,
    FileParameter,
)
from gui.model.parameter.condition import (
    AndCondition,
    Condition,
    OrCondition,
)


class RunRecord(QObject):
    """
    A list of parameters for a terminal command.

    The parameters are organized in `ParameterGroup` objects, based on
    the operation mode they correspond to and how they relate.
    """

    run_id_valid_changed = Signal(bool)
    operations_valid_changed = Signal(bool)
    selected_operation_tree_index_changed = Signal(int)

    def __init__(
            self,
            run_id_parameter: StringParameter,
            categorized_operation_trees: list[tuple[str, list[OperationTree]]],
            parameter_groups: list[ParameterGroup] | None = None,
    ) -> None:
        """
        Initialize a `RunRecord` object.

        :param parameter_groups: the groups of parameters
        :type parameter_groups: list[ParameterGroup] | None
        """
        super().__init__()
        self._run_id_parameter = run_id_parameter
        self._run_id = run_id_parameter.value
        self._run_id_parameter.value_changed.connect(
            self._run_id_parameter_value_changed
        )
        self._categorized_operation_trees = categorized_operation_trees
        for tree in self.operation_trees:
            tree.valid_changed.connect(self._operation_tree_valid_changed)
        self._selected_operation_tree_index = 0
        self._parameter_groups = parameter_groups or []
        # Set using setter
        self.selected_operation_tree_index = 0

        app_settings.workspace_path_changed.connect(
            self._workspace_path_changed,
        )

    @classmethod
    def from_yaml(cls, file_path: str) -> "RunRecord":
        """
        Create a list of parameters from a YAML file.

        :param file_path: the path to the configuration file
        :type file_path: str

        :return: the parameter list
        :rtype: Self
        """

        id_to_parameter: dict[str, Parameter[Any]] = {}
        parameters: list[Parameter[Any]] = []
        parameter_to_constraint_objs: dict[Parameter[Any], list[dict]] = {}
        parameter_to_condition_objs: dict[Parameter[Any], list[dict]] = {}

        def parse_file_structure(
                obj: dict,
        ) -> FileStructure:
            if "type" not in obj:
                raise ValueError("File structure type missing.")
            file_type = obj["type"]
            match file_type:
                case "file" | "single" | "single file":
                    formats = obj.get("formats", [])
                    if not isinstance(formats, list):
                        raise ValueError("Invalid format list for single file.")
                    for format in formats:
                        if not isinstance(format, str):
                            raise ValueError(
                                f"Invalid format for single file: {format}. "
                                + "Expected string."
                            )

                    return SingleFile(formats)
                case "folder" | "directory" | "dir":
                    contents_list = obj.get("contents", [])
                    if not isinstance(contents_list, list):
                        raise ValueError("Invalid contents list for directory.")
                    contents = []
                    for contents_obj in contents_list:
                        if not isinstance (contents_obj, dict):
                            raise ValueError(
                                f"Invalid item in contents for directory: {contents_obj}."
                                + "Expected object."
                            )
                        contents.append(parse_file_structure(contents_obj))

                    return Directory(contents)
                case _:
                    raise ValueError(
                        f"Invalid file structure. Unknown file type {file_type}"
                    )

        def parse_operation_input(obj: dict) -> Operation.Input:
            if "name" not in obj:
                raise ValueError("Missing name for operation input.")
            name = obj["name"]
            if not isinstance(name, str):
                raise ValueError(
                    f"Invalid input file name: {name}. Expected a string."
                )

            description = obj.get("description", "") or ""
            if not isinstance(description, str):
                raise ValueError(
                    f"Invalid description for input file {name}: {description}"
                    + ". Expected a string or null."
                )

            cli = obj.get("cli", "") or ""
            if not isinstance(cli, str):
                raise ValueError(
                    f"Invalid CLI representation for input file {name}: {cli}."
                    + " Expected a string or null."
                )

            if "file" not in obj:
                raise ValueError(
                    f"Missing file structure for input file {name}.")
            file_obj = obj["file"]
            file = parse_file_structure(file_obj)

            return Operation.Input(
                name=name,
                description=description,
                cli=cli,
                file=file,
            )

        def parse_path_fragment(obj: str | dict) -> Operation.PathFragment:
            if isinstance(obj, str):
                return Operation.ConstPathFragment(obj)
            if not isinstance(obj, dict):
                raise ValueError(
                    f"Invalid value for path fragment: {obj}. Expected string "
                    + "or object."
                )

            if "type" not in obj:
                raise ValueError("Missing type for path fragment object.")
            path_fragment_type = obj["type"]
            match path_fragment_type:
                case "const":
                    if "value" not in obj:
                        raise ValueError(
                            "Missing value for const path fragment object."
                        )
                    value = obj["value"]
                    if not isinstance(value, str):
                        raise ValueError(
                            "Invalid value for const path fragment object: "
                            + f"{value}. Expected a string."
                        )
                    return Operation.ConstPathFragment(value=value)
                case "run id":
                    return Operation.RunIdPathFragment()
                case "slash":
                    return Operation.SlashPathFragment()
                case "parameter":
                    if "id" not in obj:
                        raise ValueError(
                            "Missing ID for parameter value path fragment "
                            + "object."
                        )
                    parameter_id = obj["id"]
                    if not isinstance(parameter_id, str):
                        raise ValueError(
                            "Invalid ID for parameter value path fragment "
                            + f"object: {parameter_id}. Expected a string."
                        )
                    return Operation.ParameterValuePathFragment(
                        parameter_id=parameter_id
                    )
                case _:
                    raise ValueError(
                        "Unknown type for path fragment object: "
                        + f"{path_fragment_type}."
                    )

        def parse_operation(
                obj: dict,
                id: str,
        ) -> Operation:
            name = obj.get("name", "") or ""
            if not isinstance(name, str):
                raise ValueError(
                    f"Invalid operation name: {name}. Expected string or null."
                )

            description = obj.get("description", "") or ""
            if not isinstance(description, str):
                raise ValueError(
                    f"Invalid description for operation {name}: {description}."
                    + " Expected string or null."
                )
            
            cli = obj.get("cli", "") or ""
            if not isinstance(cli, str):
                raise ValueError(
                    f"Invalid CLI representation for operation {name}: {cli}."
                    + " Expected string or null."
                )

            requires = []
            requires_list = obj.get("input", []) or []
            if not isinstance(requires_list, list):
                raise ValueError(
                    f"Invalid input for operation {name}: {requires_list}."
                    + "Expected list."
                )
            for requires_obj in requires_list:
                if not isinstance (requires_obj, dict):
                    raise ValueError(
                        f"Invalid item in input list: {requires_obj}. "
                        + "Expected object."
                    )
                
                requires.append(parse_operation_input(requires_obj))

            # Output path and file structure
            if "output" not in obj:
                raise ValueError(
                    f"Missing output object for operation {name}."
                )
            output_obj = obj["output"]
            if not isinstance(output_obj, dict):
                raise ValueError(
                    f"Invalid output object for operation {name}: {output_obj}"
                    + ". Expected an object."
                )

            if "path" not in output_obj:
                raise ValueError(
                    f"No output path provided for operation {name}."
                )
            output_path_fragments_list = output_obj["path"]
            if not isinstance(output_path_fragments_list, list):
                raise ValueError(
                    f"Invalid output path for operation {name}: "
                    + f"{output_path_fragments_list}. Expected a list."
                )
            output_path_fragments: list[Operation.PathFragment] = []
            for path_fragment_obj in output_path_fragments_list:
                output_path_fragments.append(
                    parse_path_fragment(path_fragment_obj),
                )

            if "file" not in output_obj:
                raise ValueError(
                    f"Missing output file structure for operation {name}."
                )
            produces_obj = output_obj["file"]
            if not isinstance(produces_obj, dict):
                raise ValueError(
                    f"Invalid output file structure for operation {name}: "
                    + f"{produces_obj}. Expected an object."
                )
            produces = parse_file_structure(produces_obj)

            # Overwrite path and parameter
            if "overwrite" not in obj:
                raise ValueError(
                    f"Missing overwrite object for operation {name}."
                )
            overwrite_obj = obj["overwrite"]
            if not isinstance(overwrite_obj, dict):
                raise ValueError(
                    f"Invalid overwrite object for operation {name}: "
                    + f"{overwrite_obj}. Expected an object."
                )

            if "path" not in overwrite_obj:
                raise ValueError(
                    f"No overwrite path provided for operation {name}."
                )
            overwrite_path_fragments_list = overwrite_obj["path"]
            if not isinstance(overwrite_path_fragments_list, list):
                raise ValueError(
                    f"Invalid output path for operation {name}: "
                    + f"{overwrite_path_fragments_list}. Expected a list."
                )
            overwrite_path_fragments: list[Operation.PathFragment] = []
            for path_fragment_obj in overwrite_path_fragments_list:
                overwrite_path_fragments.append(
                    parse_path_fragment(path_fragment_obj),
                )

            if "parameter" not in overwrite_obj:
                raise ValueError(
                    f"Missing overwrite parameter for operation {name}."
                )
            overwrite_parameter_obj = overwrite_obj["parameter"]
            overwrite_parameter_builder = (
                lambda: parse_parameter(
                    obj=overwrite_parameter_obj,
                    operations={id},
                )
            )

            parameters_obj = obj.get("parameters", {}) or {}
            if not isinstance(parameters_obj, dict):
                raise ValueError(
                    f"Invalid parameters object for operation {name}: "
                    + f"{parameters_obj}. Expected an object or null."
                )
            parameter_builders = {}
            for parameter_id in parameters_obj:
                parameter_obj = parameters_obj[parameter_id]
                parameter_builders[parameter_id] = (
                    lambda obj=parameter_obj: parse_parameter(
                        obj=obj,
                        operations={id},
                    )
                )

            return Operation(
                id=id,
                name=name,
                description=description,
                cli=cli,
                requires=requires,
                produces=produces,
                output_path=output_path_fragments,
                overwrite_path=overwrite_path_fragments,
                overwrite_parameter_builder=overwrite_parameter_builder,
                parameter_builders=parameter_builders,
            )

        def parse_parameter(
                obj: dict,
                operations: set[str]
        ) -> Parameter[Any]:
            name = obj.get("name", "") or ""
            if not isinstance(name, str):
                raise ValueError(
                    f"Invalid parameter name: {name}. Expected string or null."
                )

            description = obj.get("description", "") or ""
            if not isinstance(description, str):
                raise ValueError(
                    f"Invalid description for parameter {name}: {description}."
                    + " Expected string or null."
                )

            if "type" not in obj:
                raise ValueError("Parameter type missing.")
            parameter_type = obj["type"]

            flag = obj.get("cli", "") or ""
            if not isinstance(flag, str):
                raise ValueError(
                    f"Invalid CLI representation for parameter {name}: {flag}."
                    + " Expected string or null."
                )

            parameter_operations = set(operations)

            if "operations" in obj:
                operation_diffs_obj = obj["operations"]
                if not isinstance(operation_diffs_obj, dict):
                    raise ValueError(
                        f"Invalid value of 'operations' for parameter {name}: "
                        + f"{operation_diffs_obj}. Expected an object."
                    )
                if "add" in operation_diffs_obj:
                    operations_add_list = operation_diffs_obj["add"]
                    if not isinstance(operations_add_list, list):
                        raise ValueError(
                            "Invalid value of 'operations.add' for parameter "
                            + f"{name}: {operations_add_list} Expected a list."
                        )
                    for operation_id in operations_add_list:
                        if not isinstance(operation_id, str):
                            raise ValueError(
                                "Invalid operation ID added for parameter "
                                + f"{name}: {operation_id}. Expected a string."
                            )
                        parameter_operations.add(operation_id)
                if "remove" in operation_diffs_obj:
                    operations_remove_list = operation_diffs_obj["remove"]
                    if not isinstance(operations_remove_list, list):
                        raise ValueError(
                            "Invalid value of 'operations.remove' for "
                            + f" parameter {name}: {operations_remove_list}. "
                            + "Expected a list."
                        )
                    for operation_id in operations_remove_list:
                        if not isinstance(operation_id, str):
                            raise ValueError(
                                "Invalid operation ID removed for parameter "
                                + f"{name}: {operation_id}. Expected a string."
                            )
                        parameter_operations.remove(operation_id)

            parameter: Parameter

            match parameter_type:
                case "int":
                    if "default" not in obj:
                        raise ValueError(
                            "No default value provided "
                            + f"for int parameter {name}."
                        )
                    default_value = obj["default"]
                    if not isinstance(default_value, int):
                        raise ValueError(
                            f"Invalid default value for int parameter {name}: "
                            + f"{default_value}. Expected int."
                        )

                    parameter = IntParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        default_value,
                    )
                case "float":
                    if "default" not in obj:
                        raise ValueError(
                            "No default value provided "
                            + f"for float parameter {name}."
                        )
                    default_value = obj["default"]
                    if (not isinstance(default_value, int)
                        and not isinstance(default_value, float)):
                        raise ValueError(
                            f"Invalid default value for float parameter {name}"
                            + f": {default_value}. Expected float."
                        )

                    parameter = FloatParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        default_value,
                    )
                case "bool":
                    if "default" not in obj:
                        raise ValueError(
                            "No default value provided "
                            + f"for bool parameter {name}."
                        )
                    default_value = obj["default"]
                    if not isinstance(default_value, bool):
                        raise ValueError(
                            f"Invalid default value for bool parameter {name}"
                            + f": {default_value}. Expected bool."
                        )
                    
                    parameter = BoolParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        default_value,
                    )
                case "enum":
                    options: list[tuple[str, str]] = []
                    options_list = obj.get("options", [])
                    for option_obj in options_list:
                        if "name" not in option_obj:
                            raise ValueError(
                                "An enum option does not have a name "
                                + f"for enum parameter {name}."
                            )
                        option_name = option_obj["name"]
                        if not isinstance(option_name, str):
                            raise ValueError(
                                f"Invalid option name for parameter {name}: "
                                + f"{option_name}. Expected string."
                            )

                        option_cli = option_obj.get("cli", "") or ""
                        if not isinstance(option_cli, str):
                            raise ValueError(
                                "Invalid CLI representation for parameter "
                                + f"{name}: {option_cli}. Expected string or "
                                + "null."
                            )

                        options.append((option_name, option_cli))

                    default_value = obj.get("default", 0)
                    if not isinstance(default_value, int):
                        raise ValueError(
                            f"Invalid default value for enum parameter {name}:"
                            + f" {default_value}. Expected int or null."
                        )
                    
                    parameter = EnumParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        options,
                        default_value,
                    )
                case "str":
                    default_value = obj.get("default", "") or ""
                    if not isinstance(default_value, str):
                        raise ValueError(
                            "Invalid default value for string parameter "
                            + f"{name}: {default_value}. Expected string or "
                            + "null."
                        )

                    max_length = obj.get("max_length", None)
                    if (max_length is not None
                        and not isinstance(max_length, int)):
                        raise ValueError(
                            f"Invalid max length for string parameter {name}: "
                            + f"{max_length}. Expected int or null."
                        )

                    parameter = StringParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        default_value,
                    )
                case "string table":
                    if "columns" not in obj:
                        raise ValueError(
                            "Missing list of column descriptions for string "
                            + f"table parameter {name}."
                        )
                    columns_list = obj["columns"]
                    if not isinstance(columns_list, list):
                        raise ValueError(
                            "Invalid list of column descriptions for string "
                            + f"table parameter {name}."
                        )
                    columns: list[tuple[str, str, list[Constraint[str]]]] = []
                    for column_obj in columns_list:
                        if not isinstance(column_obj, dict):
                            raise ValueError(
                                "Invalid column description for string table "
                                + f"parameter {name}: {column_obj}. Expected "
                                + "an object."
                            )

                        if "name" not in column_obj:
                            raise ValueError(
                                "Missing column name for string table "
                                + f"parameter {name}."
                            )
                        column_name = column_obj["name"]
                        if not isinstance(column_name, str):
                            raise ValueError(
                                "Invalid column name for string table "
                                + f"parameter {name}: {column_name}. Expected "
                                + "a string."
                            )

                        column_default = column_obj.get("default", "") or ""
                        if not isinstance(column_default, str):
                            raise ValueError(
                                "Invalid column default value for string table"
                                + f" parameter {name}: {column_default}. "
                                + "Expected a string or null."
                            )

                        constraints_list = column_obj.get(
                            "constraints", []
                        ) or []
                        if not isinstance(constraints_list, list):
                            raise ValueError(
                                "Invalid constraints list for column "
                                + f"{column_name} of string table parameter "
                                + f"{name}: {constraints_list}. Expected a "
                                + "list or null."
                            )
                        column_constraints: list[Constraint[str]] = []
                        for constraint_obj in constraints_list:
                            if not isinstance(constraint_obj, dict):
                                raise ValueError(
                                    "Invalid constraint for column "
                                    + f"{column_name} of string table "
                                    + f"parameter {name}: {constraint_obj}. "
                                    + "Expected an object."
                                )
                            column_constraints.append(
                                parse_constraint(constraint_obj)
                            )
                        columns.append(
                            (
                                column_name,
                                column_default,
                                column_constraints,
                            ),
                        )

                    if "rows" not in obj:
                        raise ValueError(
                            "Missing allowed row counts for string table "
                            + f"parameter {name}."
                        )
                    allowed_row_counts = obj["rows"]
                    for count in allowed_row_counts:
                        if not isinstance(count, int):
                            raise ValueError(
                                "Invalid allowed row count for string table "
                                + f"parameter {name}: {count}. Expected an "
                                + "integer."
                            )

                    if "separator" not in obj:
                        raise ValueError(
                            "Missing separator for string table parameter "
                            + f"{name}."
                        )
                    separator = obj["separator"]
                    if not isinstance(separator, str):
                        raise ValueError(
                            "Invalid separator for string pair list parameter "
                            + f"{name}: {separator}. Expected a string."
                        )
        
                    parameter = StringTableParameter(
                        name,
                        description,
                        flag,
                        operations,
                        columns,
                        allowed_row_counts,
                        separator,
                    )
                case "file":
                    accepted_formats = obj.get("formats", None)
                    if accepted_formats is not None and not isinstance(accepted_formats, list):
                        raise ValueError(
                            "Invalid list of file formats for file parameter "
                            + f"{name}: {accepted_formats}. Expected list or "
                            + "None."
                        )
                    if accepted_formats is not None:
                        for format in accepted_formats:
                            if not isinstance(format, str):
                                raise ValueError(
                                    "Invalid accepted format for file parameter "
                                    + f"{name}: {format}. Expected string."
                                )

                    strict = obj.get("strict", False)
                    if not isinstance(strict, bool):
                        raise ValueError(
                            "Invalid strict property for file parameter "
                            + f"{name}: {strict}. Expected bool or null."
                        )
                    if strict and not accepted_formats:
                        raise ValueError(
                            f"Strict file parameter {name} has no accepted "
                            + "file formats."
                        )

                    multiple = obj.get("multiple", False)
                    if not isinstance(multiple, bool):
                        raise ValueError(
                            "Invalid multiple property for file parameter "
                            + f"{name}: {multiple}. Expected bool or null."
                        )

                    parameter = FileParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        accepted_formats,
                        strict,
                        multiple,
                    )
                case "optional":
                    default_value = obj.get("default", False) or False
                    if not isinstance(default_value, bool):
                        raise ValueError(
                            "Invalid default value for optional parameter "
                            + f"{name}: {default_value}. Expected bool or "
                            + "null."
                        )

                    if "parameter" not in obj:
                        raise ValueError(
                            "Inner parameter not provided "
                            + f"for optional parameter {name}."
                        )
                    inner_parameter = parse_parameter(
                        obj["parameter"],
                        operations,
                    )

                    parameter = OptionalParameter(
                        name,
                        description,
                        parameter_operations,
                        default_value,
                        inner_parameter,
                    )
                case "multi":
                    if "parameters" not in obj:
                        raise ValueError(
                            f"Inner parameters not provided "
                            + f"for multi-value parameter {name}."
                        )
                    parameters_list = obj["parameters"]
                    if not isinstance(parameters_list, list):
                        raise ValueError(
                            "Invalid inner parameter list for multi-value "
                            + f"parameter {name}: {parameters_list}. Expected "
                            + "a list."
                        )
                    inner_parameters: list[Parameter[Any]] = []
                    for inner_parameter_obj in parameters_list:
                        inner_parameters.append(
                            parse_parameter(
                                inner_parameter_obj,
                                operations,
                            ),
                        )

                    parameter = MultiParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        inner_parameters,
                    )
                case (
                    "multi counted"
                    | "counted multi"
                    | "multi count"
                    | "count multi"
                ):
                    if "parameters" not in obj:
                        raise ValueError(
                            f"Inner parameters not provided "
                            + f"for counted multi-value parameter {name}."
                        )
                    parameters_list = obj["parameters"]
                    if not isinstance(parameters_list, list):
                        raise ValueError(
                            "Invalid inner parameter list for counted multi-"
                            + f"value parameter {name}: {parameters_list}. "
                            + "Expected a list."
                        )
                    inner_parameters: list[Parameter[Any]] = []
                    for inner_parameter_obj in parameters_list:
                        inner_parameters.append(
                            parse_parameter(
                                inner_parameter_obj,
                                operations,
                            ),
                        )

                    parameter = CountedMultiParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        inner_parameters,
                    )
                case _:
                    raise ValueError(
                        f"Invalid or missing type for parameter {name}: "
                        + f"{parameter_type}."
                    )

            parameters.append(parameter)

            constraint_objs = obj.get("constraints", []) or []
            if not isinstance(constraint_objs, list):
                raise ValueError(
                    f"Invalid constraint list for parameter {name}: "
                    + f"{constraint_objs}. Expected a list."
                )
            parameter_to_constraint_objs[parameter] = constraint_objs

            condition_objs = obj.get("conditions", [])
            if not isinstance(condition_objs, list):
                raise ValueError(
                    f"Invalid condition list for parameter {name}: "
                    + f"{condition_objs}. Expected list or null."
                )
            parameter_to_condition_objs[parameter] = condition_objs

            return parameter

        def parse_constraint(obj: dict) -> Constraint:
            if "type" not in obj:
                raise ValueError("Missing type for constraint.")
            constraint_type = obj["type"]

            match constraint_type:
                case "interval":
                    lower_bound = obj.get("min")
                    if (lower_bound is not None
                        and not isinstance(lower_bound, (int, float))):
                        raise ValueError(
                            "Invalid min for interval constraint: "
                            + f"{lower_bound}. Expected int or float."
                        )

                    lower_bound_inclusive = obj.get("min_inclusive", True)
                    if not isinstance(lower_bound_inclusive, bool):
                        raise ValueError(
                            "Invalid value for min_inclusive in interval "
                            + f"constraint: {lower_bound_inclusive}. Expected "
                            + "a bool."
                        )

                    upper_bound = obj.get("max")
                    if (upper_bound is not None
                        and not isinstance(upper_bound, (int, float))):
                        raise ValueError(
                            "Invalid max for interval constraint: "
                            + f"{upper_bound}. Expected int or float."
                        )

                    upper_bound_inclusive = obj.get("max_inclusive", True)
                    if not isinstance(upper_bound_inclusive, bool):
                        raise ValueError(
                            "Invalid value for max_inclusive in interval "
                            + f"constraint: {upper_bound_inclusive}. Expected "
                            + "a bool."
                        )

                    return IntervalConstraint(
                        lower_bound=lower_bound,
                        lower_bound_inclusive=lower_bound_inclusive,
                        upper_bound=upper_bound,
                        upper_bound_inclusive=upper_bound_inclusive,
                    )
                case "even":
                    return EvenConstraint()
                case "max length":
                    if "length" not in obj:
                        raise ValueError(
                            "Missing length for max length constraint."
                        )
                    max_length = obj["length"]
                    if not isinstance(max_length, int):
                        raise ValueError(
                            "Invalid length for max length constraint: "
                            + f"{max_length}. Expected an int."
                        )

                    return MaxLengthConstraint(
                        max_length=max_length,
                    )
                case "regex":
                    if "pattern" not in obj:
                        raise ValueError(
                            "Missing pattern for regex constraint."
                        )
                    pattern = obj["pattern"]
                    if not isinstance(pattern, str):
                        raise ValueError(
                            f"Invalid pattern for regex constraint: {pattern}."
                            + " Expected a string."
                        )

                    if "hint" not in obj:
                        raise ValueError("Missing hint for regex constraint.")
                    hint = obj["hint"]
                    if not isinstance(hint, str):
                        raise ValueError(
                            f"Invalid hint for regex constraint: {hint}. "
                            + "Expected a string."
                        )

                    return RegexConstraint(
                        pattern=compile(pattern),
                        hint=hint,
                    )
                case _:
                    raise ValueError(
                        f"Invalid constraint type {constraint_type}."
                    )

        def parse_parameter_group(obj: dict) -> ParameterGroup:
            name = obj.get("name", "") or ""
            if not isinstance(name, str):
                raise ValueError(
                    f"Invalid name for parameter group: {name}. Expected "
                    + "string or null."
                )

            operations = obj.get("operations", [])
            if not isinstance(operations, list):
                raise ValueError(
                    f"Invalid operations list for parameter group {name}: "
                    + f"{operations}. Expected list or null."
                )
            for operation in operations:
                if not isinstance(operation, str):
                    raise ValueError(
                        f"Invalid operation for parameter group {name}: "
                        + f"{operation}. Expected string."
                    )

            if "parameters" not in obj:
                raise ValueError(
                    f"Parameter group {name} does has no parameters object."
                )
            parameters_obj = obj["parameters"]
            if not isinstance(parameters_obj, dict):
                raise ValueError(
                    f"Invalid parameters field of parameter group {name}: "
                    + f" {parameters_obj}. Expected an object."
                )
            parameters: list[Parameter[Any]] = []
            for parameter_id, parameter_obj in obj["parameters"].items():
                if not isinstance(parameter_id, str):
                    raise ValueError(
                        f"Invalid parameter id: {parameter_id}. Expected "
                        + "string."
                    )
                parameter = parse_parameter(parameter_obj, set(operations))
                parameters.append(parameter)
                id_to_parameter[parameter_id] = parameter
            return ParameterGroup(name, parameters)

        def parse_condition(obj: dict) -> Condition:
            if "type" not in obj:
                raise ValueError("Parameter condition has no type.")
            
            condition_type = obj["type"]

            match condition_type:
                case "or":
                    if "conditions" not in obj:
                        raise ValueError(
                            "Missing list of child conditions for 'or' "
                            + "condition."
                        )
                    conditions_list = obj["conditions"]
                    if not isinstance(conditions_list, list):
                        raise ValueError(
                            "Invalid child condition list for 'or' condition: "
                            + f"{conditions_list}. Expected a list."
                        )

                    conditions: list[Condition] = []
                    for condition_obj in conditions_list:
                        conditions.append(
                            parse_condition(condition_obj)
                        )

                    return OrCondition(
                        conditions,
                    )
                case "enabled":
                    if "parameter" not in obj:
                        raise ValueError(
                            "Enabled condition has no target parameter."
                        )
                    parameter_id = obj["parameter"]
                    if not isinstance(parameter_id, str):
                        raise ValueError(
                            "Invalid target parameter ID for enabled condition"
                            + f": {parameter_id}. Expected string."
                        )

                    parameter = id_to_parameter[parameter_id]

                    target_value = obj.get("value", True)
                    if target_value is None:
                        target_value = True
                    if not isinstance(target_value, bool):
                        raise ValueError(
                            "Invalid target value for enabled condition: "
                            + f"{target_value}. Expected bool or null."
                        )
                    
                    return Parameter.EnabledCondition(
                        parameter,
                        target_value,
                    )
                case "opt" | "optional":
                    if "parameter" not in obj:
                        raise ValueError(
                            "Optional condition has no target parameter."
                        )
                    parameter_id = obj["parameter"]
                    if not isinstance(parameter_id, str):
                        raise ValueError(
                            "Invalid target parameter ID for optional "
                            + f"condition: {parameter_id}. Expected string."
                        )

                    parameter = id_to_parameter[parameter_id]
                    if not isinstance(parameter, OptionalParameter):
                        raise ValueError(
                            "Bool condition references non-optional parameter "
                            + f"{parameter_id}."
                        )

                    target_value = obj.get("value", True)
                    if target_value is None:
                        target_value = True
                    if not isinstance(target_value, bool):
                        raise ValueError(
                            "Invalid target value for optional condition: "
                            + f"{target_value}. Expected bool or null."
                        )

                    return OptionalParameter.Condition(
                        parameter,
                        target_value,
                    )
                case "bool":
                    if "parameter" not in obj:
                        raise ValueError(
                            "Bool condition has no target parameter."
                        )
                    parameter_id = obj["parameter"]
                    if not isinstance(parameter_id, str):
                        raise ValueError(
                            "Invalid target parameter ID for bool condition: "
                            + f"{parameter_id}. Expected string."
                        )

                    parameter = id_to_parameter[parameter_id]
                    if not isinstance(parameter, BoolParameter):
                        raise ValueError(
                            "Bool condition references non-bool parameter "
                            + f"{parameter_id}."
                        )

                    target_value = obj.get("value", True)
                    if target_value is None:
                        target_value = True
                    if not isinstance(target_value, bool):
                        raise ValueError(
                            "Invalid target value for bool condition: "
                            + f"{target_value}. Expected bool or null."
                        )

                    return BoolParameter.Condition(
                        parameter,
                        target_value,
                    )
                case "enum":
                    if "parameter" not in obj:
                        raise ValueError("Enum condition has no target parameter.")
                    parameter_id = obj["parameter"]
                    parameter = id_to_parameter[parameter_id]
                    if not isinstance(parameter, EnumParameter):
                        raise ValueError("Enum condition is referencing a non-enum parameter.")

                    if "values" not in obj:
                        raise ValueError("Enum condition has no list of target values.")
                    target_values = obj["values"]
                    if not isinstance(target_values, list):
                        raise ValueError(
                            "Invalid target value list for enum condition: "
                            + f"{target_values}. Expected a list of ints."
                        )
                    for target_value in target_values:
                        if not isinstance(target_value, int):
                            raise ValueError(
                                f"Invalid target value for enum condition: "
                                + f"{target_value}. Expected int."
                            )

                    return EnumParameter.Condition(
                        parameter,
                        target_values,
                    )
                case _:
                    raise ValueError(f"Invalid condition type '{condition_type}'.")

        with open(file_path) as f:
            config_text = f.read()

        config_obj = load(config_text, Loader=Loader)

        operations = {}
        mode_operation_ids: list[tuple[str, list[str]]] = []
        if "modes" not in config_obj:
            raise ValueError("Configuration file contains no list of modes.")
        mode_list = config_obj["modes"]
        if not isinstance(mode_list, list):
            raise ValueError(
                f"Invalid mode list: {mode_list}. Expected a list."
            )
        for mode_obj in mode_list:
            if not isinstance(mode_obj, dict):
                raise ValueError(f"Invalid mode: {mode_obj}. Expected object.")
            if "name" not in mode_obj:
                raise ValueError("Mode has no name.")
            mode_name = mode_obj.get("name")
            if not isinstance(mode_name, str):
                raise ValueError(
                    f"Invalid mode name: {mode_name}. Expected string."
                )
            if "operations" not in mode_obj:
                raise ValueError(f"Mode has no operation list.")
            operations_obj = mode_obj["operations"]
            if not isinstance(operations_obj, dict):
                raise ValueError(
                    f"Invalid operations dictionary: {operations_obj}. "
                    + "Expected an object."
                )
            current_mode_op_ids = []
            for operation_id in operations_obj:
                operation_obj = operations_obj[operation_id]
                if not isinstance(operation_obj, dict):
                    raise ValueError(
                        f"Invalid operation: {operation_obj}"
                        + "Expected an object."
                    )
                operations[operation_id] = parse_operation(operation_obj, operation_id)
                current_mode_op_ids.append(operation_id)
            mode_operation_ids.append((mode_name, current_mode_op_ids))
        if "run_id_parameter" not in config_obj:
            raise ValueError(
                "Run ID parameter missing from configuration file!"
            )
        run_id_parameter_obj = config_obj["run_id_parameter"]
        if not isinstance(run_id_parameter_obj, dict):
            raise ValueError(
                "Invalid value for run ID parameter: "
                + f"{run_id_parameter_obj}. Expected object."
            )
        run_id_parameter = parse_parameter(
            run_id_parameter_obj,
            # Assign the run ID parameter to all operations so it is
            # always present.
            set(operations.keys()),
        )
        if not isinstance(run_id_parameter, StringParameter):
            raise ValueError(
                f"Invalid run ID parameter: {run_id_parameter}. "
                + "Expected string parameter."
            )
        id_to_parameter["run-id"] = run_id_parameter

        if "common_directory_overwrite_parameter" not in config_obj:
            raise ValueError(
                "Missing overwrite parameter definition for common parent "
                + "directory nodes."
            )
        overwrite_parameter_obj = config_obj[
            "common_directory_overwrite_parameter"
        ]
        if not isinstance(overwrite_parameter_obj, dict):
            raise ValueError(
                "Invalid value for common parent directory node overwrite "
                + f"parameter: {overwrite_parameter_obj}. Expected object."
            )
        overwrite_parameter_builder = (
            lambda: parse_parameter(
                overwrite_parameter_obj,
                operations=set(operations.keys()),
            )
        )

        parameter_groups = []
        for parameter_group_obj in config_obj["parameter_groups"]:
            parameter_groups.append(parse_parameter_group(parameter_group_obj))

        operation_trees, operation_conditions = OperationTree.build_trees(
            operations,
            overwrite_parameter_builder,
        )

        # Build a mapping from operation ID to its tree
        op_id_to_tree = {}
        for tree in operation_trees:
            op_id_to_tree[tree.root.id] = tree

        # Group trees by mode
        categorized_operation_trees: list[tuple[str, list[OperationTree]]] = []
        for mode_name, op_ids in mode_operation_ids:
            mode_trees = [op_id_to_tree[op_id] for op_id in op_ids]
            categorized_operation_trees.append((mode_name, mode_trees))

        result = cls(run_id_parameter, categorized_operation_trees, parameter_groups)

        for param in parameters:
            for constraint_obj in parameter_to_constraint_objs[param]:
                if not isinstance(constraint_obj, dict):
                    raise ValueError(
                        f"Invalid constraint for parameter {param}: "
                        + f"{constraint_obj}. Expected an object."
                    )

                param.add_constraint(
                    parse_constraint(constraint_obj),
                )

        for parameter in parameters:
            for condition_obj in parameter_to_condition_objs[parameter]:
                parameter.add_condition(parse_condition(condition_obj))

            operation_condition = OrCondition()
            for operation_id in parameter.operations:
                operation_condition.add_condition(
                    operation_conditions[operation_id]
                )
            parameter.add_condition(operation_condition)

        return result
    
    def to_history_record(self) -> HistoryRecord:
        """
        Makes a history record with the information of the current RunResult.
        """
        parameters_dict = {}
        for parameter_group in self.parameter_groups:
            for parameter in parameter_group:
                parameters_dict[parameter.name] = parameter.to_dict()

        return HistoryRecord(
            self.run_id,
            self.to_cli(),
            {"index": self.selected_operation_tree_index,
             "trees": [tree.to_dict() for tree in self.operation_trees]},
            parameters_dict,
            datetime.now()
        )
    
    def populate(self, history_record: HistoryRecord) -> None:
        """
        Populate the current run result with the contents of a history record.
        This is used to fill the ResultsWidget in history with the contents
        of records when a user clicks on them.
        """
        self.run_id = history_record.name
        for i, tree in enumerate(self.operation_trees):
            operations_list = history_record.operations.get("trees")
            if operations_list != None:
                tree.populate_from_dict(operations_list[i])
        index = history_record.operations.get("index")
        if index is not None:
            self.selected_operation_tree_index = index
        
        dictionary = history_record.parameters
        for parameter_group in self.parameter_groups:
            for parameter in parameter_group:
                if parameter.name in dictionary:
                    parameter.populate(dictionary[parameter.name])
                    #TODO: validity checking?
        self._time_completed = history_record.time_completed
    
    def reset(self) -> None:
        self.selected_operation_tree_index = 0
        for tree in self.operation_trees:
            tree.reset()
        self.run_id_parameter.reset_value()
        for parameter_group in self.parameter_groups:
            for parameter in parameter_group:
                    parameter.reset_value()

    @property
    def run_id_parameter(self) -> StringParameter:
        return self._run_id_parameter

    @property
    def run_id(self) -> str:
        return self.run_id_parameter.value

    @run_id.setter
    def run_id(self, new_run_id: str) -> None:
        if self.run_id_parameter.value == new_run_id:
            return # Nothing actually changed
        self.run_id_parameter.value = new_run_id

    @property
    def run_id_valid(self) -> bool:
        return self.run_id_parameter.valid

    @property
    def base_directory_path(self) -> str:
        return app_settings.workspace_path.absoluteFilePath(self.run_id)

    @property
    def categorized_operation_trees(self) -> list[tuple[str, list[OperationTree]]]:
        """Operation trees grouped by mode name."""
        return self._categorized_operation_trees

    @property
    def operation_trees(self) -> list[OperationTree]:
        """Flat list of all operation trees."""
        return [
            tree
            for _, trees in self._categorized_operation_trees
            for tree in trees
        ]

    @property
    def selected_operation_tree(self) -> OperationTree:
        return self.operation_trees[self.selected_operation_tree_index]

    @property
    def selected_operation_tree_index(self) -> int:
        return self._selected_operation_tree_index

    @selected_operation_tree_index.setter
    def selected_operation_tree_index(self, new_index: int) -> None:
        self.selected_operation_tree.enabled = False
        self._selected_operation_tree_index = new_index
        self.selected_operation_tree_index_changed.emit(new_index)
        self.selected_operation_tree.enabled = True
        self.operations_valid_changed.emit(self.operations_valid)

    @property
    def operations_valid(self) -> bool:
        return self.selected_operation_tree.valid

    @property
    def parameter_groups(self) -> list[ParameterGroup]:
        """
        The list of groups in the parameter list.
        """
        return self._parameter_groups

    @property
    def parameters(self) -> list[Parameter]:
        result = []
        for parameter_group in self:
            result.extend(parameter_group)
        return result

    @property
    def valid(self) -> bool:
        """
        Whether the current parameter values are valid.

        The list is valid if and only if every group is valid.
        """
        return all(
            [self._run_id_parameter.valid]
            + [group.valid for group in self]
        )

    def to_cli(self) -> list[str]:
        """
        Produce command-line instructions for the current parameter
        values.

        A separate instruction is produced for each active operation. The
        command is obtained by prepending the list command to the operations's 
        command to the combination of applicable groups' CLI representations.

        :return: the list of instructions
        :rtype: list[str]
        """

        return self.selected_operation_tree.to_cli(
            self.run_id_parameter,
            self.parameters,
        )

    def __iter__(self) -> Iterator[ParameterGroup]:
        return iter(self.parameter_groups)

    def __getitem__(self, i) -> ParameterGroup:
        return self.parameter_groups[i]

    @Slot(str, bool)
    def _run_id_parameter_value_changed(
        self,
        new_run_id: str,
        new_valid: bool,
    ) -> None:
        self.run_id_valid_changed.emit(self.run_id_valid)
        for operation_tree in self.operation_trees:
            operation_tree.run_id = new_run_id
            operation_tree.base_directory_path = self.base_directory_path

    @Slot(bool)
    def _operation_tree_valid_changed(self, new_valid: bool) -> None:
        self.operations_valid_changed.emit(self.operations_valid)

    @Slot()
    def _workspace_path_changed(self) -> None:
        for tree in self.operation_trees:
            tree.base_directory_path = self.base_directory_path
