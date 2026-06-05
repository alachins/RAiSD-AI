from pytest import approx, fixture, raises, skip
from unittest.mock import PropertyMock
from gui.tests.utils.mock_signal import MockSignal
import posixpath
import re

from collections.abc import Sequence

from gui.model.operation import (
    Operation, 
    OperationTree,
    FilePickerNode,
    OperationNode,
    OrCondition,
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
    Parameter,
)

class TestConditions:
    """Tests for conditions between parameters, and between parameters
    and operations."""

    @fixture()
    def operation_trees(self):
        self.operations = {
            "IMG-GEN": Operation(
                id="IMG-GEN",
                name="Image generation",
                description="Generates an image.",
                cli="-mdl",
                requires=[
                    Operation.Input(
                        name="Input file",
                        description="The input file.",
                        cli="-I ",
                        file=SingleFile([".ms", ".txt"]),
                    ),
                ],
                produces=SingleFile([".png"]),
                output_path=[
                    Operation.ConstPathFragment("Image."),
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
                    Operation.ConstPathFragment("Image."),
                    Operation.RunIdPathFragment(),
                ]
            ),
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
                        file=SingleFile([".png"]),
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
        self.trees, self.conditions = OperationTree.build_trees(
            self.operations,
            self.overwrite_parameter_builder,
        )
        self.categorized_operation_trees = [
            ('Operations', self.trees),
        ]

        print(self.trees)
        for tree in self.trees:
            print(tree.to_dict())
    
    @fixture()
    def set_operation_conditions(self,operation_trees, parameter_groups):
        for parameter in list(self.parameters_group1) + list(self.parameters_group2):
            conditions = []
            for operation_id in parameter.operations:
                conditions.append(self.conditions[operation_id])
            if len(conditions) > 1:
                condition = OrCondition(conditions)
            else: 
                condition = conditions[0]
            parameter.add_condition(condition)    

    @fixture()
    def parameter_groups(self):
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
        self.int_parameter = IntParameter(
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
            ]
        )
        self.optional_parameter = OptionalParameter(
            name='optional',
            description='This is optional',
            operations={'MDL-GEN'},
            default_value=False,
            parameter=self.int_parameter
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
        self.groups = [
            ParameterGroup(
                name='img',
                parameters=self.parameters_group1 # type: ignore
                ), 
            ParameterGroup(
                name='mdl',
                parameters=self.parameters_group2 # type: ignore
            ),
        ]

    @fixture()
    def run_record(self, mocker, operation_trees, parameter_groups):

        # RunRecord
        self.record = RunRecord(
            run_id_parameter=self.run_id_parameter,
            categorized_operation_trees=self.categorized_operation_trees,
            parameter_groups=self.groups,
        )

        print(self.record.operation_trees)
        for tree in self.record.operation_trees:
            print(tree.to_dict())

        # Mock workspace else it will lead to errors
        mocker.patch.object(
            type(rrecord.app_settings),
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir.current()
        )

    def test_enum_condition(self, parameter_groups):
        """Test an enumcondition."""
        # Arrange
        self.optional_parameter.add_condition(
            condition=EnumParameter.Condition(
                self.enum_parameter,
                [1]
            )
        )

        # Act and assert
        assert not self.optional_parameter.enabled  
        assert not self.optional_parameter.parameter.enabled

        self.enum_parameter.value = 1

        assert self.optional_parameter.enabled
        assert not self.optional_parameter.parameter.enabled

        self.optional_parameter.value = True

        assert self.optional_parameter.parameter.enabled

        self.enum_parameter.value = 0

        assert not self.optional_parameter.enabled  
        assert not self.optional_parameter.parameter.enabled

    def test_optional_parameter_condition(self, parameter_groups):
        """Test an optional parameter condition."""
        self.enum_parameter.add_condition(
            condition=OptionalParameter.Condition(
                parameter=self.optional_parameter,
                target_value=False
            )
        )

        # Assert
        assert self.enum_parameter.enabled
        assert not self.int_parameter.enabled
        assert not self.optional_parameter.value

        # Act
        self.optional_parameter.value = True

        # Assert
        assert self.int_parameter.enabled
        assert not self.enum_parameter.enabled
        assert self.optional_parameter.value

    def test_enabled_condition(self, parameter_groups):
        """Test an enabled condition"""
        # Arrange
        self.enum_parameter.add_condition(
            condition=Parameter.EnabledCondition(
                parameter=self.int_parameter,
                target_value=False,
            )
        )

        # Assert
        assert self.enum_parameter.enabled
        assert not self.int_parameter.enabled

        # Act
        self.optional_parameter.value = True

        # Assert
        assert self.int_parameter.enabled
        assert not self.enum_parameter.enabled

    def test_operation_conditions(self, set_operation_conditions, run_record):
        """Test that selecting different operations correctly enables and
        disables parameters."""
        # Arrange
        record = self.record

        # Assert
        assert self.enum_parameter.enabled
        assert not self.optional_parameter.enabled
        assert self.file_parameter.enabled
        assert self.multi_parameter.enabled

        # Act
        record.selected_operation_tree_index = 1

        # Assert
        assert self.enum_parameter.enabled
        assert self.optional_parameter.enabled
        assert not self.file_parameter.enabled
        assert not self.multi_parameter.enabled

        # Act
        record.operation_trees[1].root.file_consumers[0].selected_index = 1

        # Assert
        assert self.enum_parameter.enabled
        assert self.optional_parameter.enabled
        assert self.file_parameter.enabled
        assert self.multi_parameter.enabled