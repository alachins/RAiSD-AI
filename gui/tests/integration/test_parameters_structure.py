from pytest import fixture
from unittest.mock import PropertyMock
import re

from collections.abc import Sequence

from gui.model.operation import (
    Operation, 
    OperationTree,
)

from PySide6.QtCore import QDir

from gui.model.operation.file_structure import SingleFile
from gui.model.run_record import RunRecord
import gui.model.run_record as rrecord
from gui.model.parameter import (
    IntervalConstraint,
    RegexConstraint,
    ParameterGroup,
    OptionalParameter,
    MultiParameter,
    BoolParameter,
    IntParameter,
    EnumParameter,
    StringParameter,
    FileParameter,
    Parameter
)

class TestParametersStructure:
    """Tests the structures in which parameters are held. This includes the 
    RunRecord, Parameter and ParameterGroup."""

    @fixture(autouse=True)
    def set_run_record(self, mocker):
        # Parameters
        self.run_id_parameter = StringParameter(
            name='name',
            description='description',
            flag='-f ',
            operations={'MDL-GEN'},
            default_value='default',
            constraints=[
                RegexConstraint(
                    pattern=re.compile(r"\b[a-z]+\b"),
                    hint="Only lowercase letters.",
                ),
            ],
        )
        self.enum_parameter = EnumParameter (
            name="Run ID",
            description="Fill in a name to identify your run.",
            flag="-n ",
            operations={"IMG-GEN", "MDL-GEN"},
            options=[("name1", "1"),("name2","2")],
            default_value=0,
        )
        self.optional_parameter = OptionalParameter(
            name='optional',
            description='This is optional',
            operations={'MDL-GEN'},
            default_value=False,
            parameter=IntParameter(
              name='int',
              description='description',
              flag='-i ',
              operations={'MDL-GEN'},
              default_value=3,
              constraints=[
                  IntervalConstraint(
                      lower_bound=2,
                      lower_bound_inclusive=False,
                      upper_bound=7,
                      upper_bound_inclusive=False,
                  ),
              ],
          )
        )
        self.file_parameter = FileParameter (
            name="file",
            description="file",
            flag="-fi ",
            operations={"IMG-GEN"}
        )
        self.multi_parameter = MultiParameter ( #type: ignore
                    name="multi",
                    description="descr",
                    flag="-m ",
                    operations={'IMG-GEN'},
                    parameters=[self.file_parameter]
                )
        
        # Parameter groups
        self.parameters_group1: Sequence[Parameter] = [
            self.multi_parameter
        ]
        self.parameters_group2: Sequence[Parameter] = [
            self.enum_parameter,
            self.optional_parameter
        ]
        self.parameter_groups = [
            ParameterGroup(
                name='img',
                parameters=self.parameters_group1 # type: ignore
                ), 
            ParameterGroup(
                name='mdl',
                parameters=self.parameters_group2 # type: ignore
            ),
        ]
        
        # Operations
        self.operations = {
            "MDL-GEN": Operation(
                id="MDL-GEN",
                name="Model training",
                description="Perform a model training.",
                cli="-mdl",
                requires=[
                    Operation.Input(
                        name="Input file",
                        description="The input file.",
                        cli="-I ",
                        file=SingleFile([".ms", ".txt"]),
                    ),
                ],
                produces=SingleFile([".txt"]),
                output_path=[
                    Operation.ConstPathFragment("Model."),
                    Operation.RunIdPathFragment(),
                ],
                overwrite_parameter_builder=(
                    lambda: BoolParameter(
                        name="Overwrite output?",
                        description="",
                        flag="-overwrite",
                        operations={"mdl"},
                        default_value=False,
                    )
                ),
                parameter_builders={},
                overwrite_path=[
                    Operation.ConstPathFragment("Model."),
                    Operation.RunIdPathFragment(),
                ]
            ),
        }
        self.overwrite_parameter_builder = (
            lambda: BoolParameter(
                name="Overwrite output directory",
                description="Are you sure you want to overwrite?",
                flag="-frm",
                operations={"MDL-GEN"},
                default_value=False,
            )
        )
        self.operation_trees, _ = OperationTree.build_trees(
            self.operations,
            self.overwrite_parameter_builder,
        )
        self.categorized_operation_trees = [
            ('Operations', self.operation_trees),
        ]

        # RunRecord
        self.run_record = RunRecord(
            run_id_parameter=self.run_id_parameter,
            categorized_operation_trees=self.categorized_operation_trees,
            parameter_groups=self.parameter_groups,
        )

        # Mock workspace else it will lead to errors
        mocker.patch.object(
            type(rrecord.app_settings),
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir.current()
        )

    def test_valid_based_on_params(self, tmp_path):
        """Test whether the validity of parameters is passed along from 
        Parameter to ParameterGroup to RunRecord correctly."""
        # Arrange
        record = self.run_record
        file = tmp_path / "file"
        file.write_text("")

        # Act and Assert
        assert not record.valid
        self.file_parameter.value = [tmp_path / "file"]
        assert self.run_id_parameter.valid
        assert self.file_parameter.valid
        assert self.enum_parameter.valid
        assert self.multi_parameter.valid
        assert record.valid

        assert record.valid
        self.run_id_parameter.value = "HI"
        assert not record.valid
        self.run_id_parameter.reset_value()

        self.optional_parameter.parameter.value = 0
        self.optional_parameter.value = True
        assert not record.valid
        self.optional_parameter.parameter.reset_value()

        self.file_parameter.reset_value()

    def test_reset(self, mocker):
        """Test that the parameters are reset correctly when the RunRecord is
        reset, and the correct signals are emitted."""
        # Arrange
        record = self.run_record
        self.run_id_parameter.value = "new"
        run_id_reset_spy = mocker.MagicMock()
        self.run_id_parameter.value_reset.connect(run_id_reset_spy)

        self.enum_parameter.value = 1
        enum_reset_spy = mocker.MagicMock()
        self.enum_parameter.value_reset.connect(enum_reset_spy)

        self.optional_parameter.value = True
        self.optional_parameter.parameter.value = 5
        optional_reset_spy = mocker.MagicMock()
        int_reset_spy = mocker.MagicMock()
        self.optional_parameter.value_reset.connect(optional_reset_spy)
        self.optional_parameter.parameter.value_reset.connect(int_reset_spy)

        # Act
        record.reset()

        # Assert
        assert self.run_id_parameter.value == "default"
        run_id_reset_spy.assert_called_once()

        assert self.enum_parameter.value == 0
        enum_reset_spy.assert_called_once()

        assert self.optional_parameter.value == False
        optional_reset_spy.assert_called_once()

        assert self.optional_parameter.parameter.value == 3
        int_reset_spy.assert_called_once()

    def test_run_id_setter(self, mocker):
        """Test that the RunRecord run_id setter also changes the underlyig
        run_id_parameter, which in turn emits a signal."""
        # Arrange
        record = self.run_record
        signal_spy = mocker.MagicMock()
        self.run_id_parameter.value_changed.connect(signal_spy)

        # Act
        record.run_id = "new"

        # Assert
        assert record.run_id == "new"
        assert record.run_id_parameter.value == "new"
        signal_spy.assert_called_once_with("new", True)

    def test_parameters_getter(self):
        """Test if the parameters property of the RunRecord correctly combines
        the parameters from the parameter groups."""
        # Arrange
        record = self.run_record
        parameters = list(self.parameters_group1) + list(self.parameters_group2)

        # Act
        record_parameters = record.parameters

        # Assert
        assert len(record_parameters) == len(parameters)
        for parameter in parameters:
            assert parameter in record_parameters
        
    def test_to_cli(self):
        # Arrange
        record = self.run_record

        # Act
        instructions = record.to_cli()

        # Assert
        assert len(instructions) == 1
        assert instructions == record.selected_operation_tree.to_cli(
            run_id_parameter=self.run_id_parameter,
            parameters=record.parameters,
        )

        instruction = instructions[0]
        assert "-I" in instruction
        assert "-f" in instruction
        assert "-n" in instruction

        # Act
        self.optional_parameter.value = True
        instructions = record.to_cli()

        # Assert
        assert len(instructions) == 1
        assert instructions == record.selected_operation_tree.to_cli(
            run_id_parameter=self.run_id_parameter,
            parameters=record.parameters,
        )

        instruction = instructions[0]
        assert "-I" in instruction
        assert "-f" in instruction
        assert "-n" in instruction
        assert "-i" in instruction