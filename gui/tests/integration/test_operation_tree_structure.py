from pytest import fixture
from unittest.mock import PropertyMock
import posixpath
import re

from collections.abc import Sequence

from gui.model.operation import (
    Operation, 
    OperationTree,
    FilePickerNode,
    OperationNode,
)

from PySide6.QtCore import QDir

from gui.model.operation.file_structure import SingleFile
from gui.model.run_record import RunRecord
import gui.model.run_record as rrecord
from gui.model.parameter import (
    RegexConstraint,
    ParameterGroup,
    BoolParameter,
    EnumParameter,
    StringParameter,
    Parameter
)

class TestOperationTreeStructures:
    """Tests for the structures to do with the OperationTree class. That 
    includes the RunRecord who holds it and the classes inside the tree."""

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
        self.trees, _ = OperationTree.build_trees(
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
    def run_record(self, mocker, operation_trees):
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
        
        # Parameter groups
        self.parameters_group1: Sequence[Parameter] = [
        ]
        self.parameters_group2: Sequence[Parameter] = [
            self.enum_parameter,
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

        # RunRecord
        self.record = RunRecord(
            run_id_parameter=self.run_id_parameter,
            categorized_operation_trees=self.categorized_operation_trees,
            parameter_groups=self.parameter_groups,
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

    def test_operation_trees_structure(self, operation_trees):
        """Test OperationTree initialization."""
        # Arrange
        trees = self.trees

        # Assert
        assert len(trees) == 2      # img-gen and mdl-gen

        img_gen_tree = trees[0]
        assert img_gen_tree.get_operation_ids() == ["Image generation"]
        assert img_gen_tree.root.id == "IMG-GEN"
        assert img_gen_tree.root.valid == False # File consumer is not valid
        assert "Image." in img_gen_tree.root.overwrite_file
        assert len(img_gen_tree.root.file_consumers) == 1
        consumer = img_gen_tree.root.file_consumers[0]
        assert len(consumer.producers) == 1 
        assert isinstance(consumer.producers[0], FilePickerNode)

        mdl_gen_tree = trees[1]
        assert mdl_gen_tree.get_operation_ids() == ["Model training"]
        assert mdl_gen_tree.root.id == "MDL-GEN"
        assert mdl_gen_tree.root.valid == False
        assert "Model." in mdl_gen_tree.root.overwrite_file
        assert len(mdl_gen_tree.root.file_consumers) == 1
        consumer = mdl_gen_tree.root.file_consumers[0]
        assert len(consumer.producers) == 2
        assert isinstance(consumer.producers[0], FilePickerNode)
        assert isinstance(consumer.producers[1], OperationNode)
        
        sub_tree = consumer.producers[1]
        assert sub_tree.get_operation_ids() == ["Image generation"]
        assert len(sub_tree.file_consumers) == 1
        consumer = sub_tree.file_consumers[0]
        assert len(consumer.producers) == 1 
        assert isinstance(consumer.producers[0], FilePickerNode)

    def test_valid_change(self, run_record, tmp_path):
        # Arrange
        record = self.record
        trees = record.operation_trees
        file = tmp_path / "file"
        file.write_text("")

        # Act and assert
        assert not record.operations_valid
        producer = trees[0].root.file_consumers[0].producers[0]
        assert isinstance(producer, FilePickerNode)
        producer.file = tmp_path / "file"
        assert record.operations_valid
        record.selected_operation_tree_index = 1
        assert not record.operations_valid
        assert record.valid # Not dependent on operations valid

    def test_reset(self, run_record, tmp_path):
        # Arrange
        record = self.record
        trees = record.operation_trees
        file = tmp_path / "file"
        file.write_text("")
        producer = trees[0].root.file_consumers[0].producers[0]
        assert isinstance(producer, FilePickerNode)
        producer.file = tmp_path / "file"
        record.selected_operation_tree_index = 1
        trees[1].root.file_consumers[0].selected_index = 1

        # Act
        record.reset()

        # Assert
        assert producer.file == None
        assert record.selected_operation_tree_index == 0
        assert trees[1].root.file_consumers[0].selected_index == 0

    def test_trees_getter(self, run_record):
        # Arrange
        record = self.record

        # Act
        retrieved_trees = record.operation_trees

        # Assert
        assert retrieved_trees == self.trees
    
    def test_selected_operation_tree_index(self, run_record, mocker):
        # Arrange 
        record = self.record
        index_spy = mocker.MagicMock()
        record.selected_operation_tree_index_changed.connect(index_spy)
        valid_spy = mocker.MagicMock()
        record.operations_valid_changed.connect(valid_spy)

        # Assert
        assert record.operation_trees[0].enabled
        assert record.selected_operation_tree_index == 0
        assert not record.operations_valid

        # Act
        record.selected_operation_tree_index = 1

        # Assert
        assert not record.operation_trees[0].enabled
        assert record.operation_trees[1].enabled
        assert record.selected_operation_tree_index == 1
        index_spy.assert_called_once_with(1)
        valid_spy.assert_called_once_with(False)

    def test_tree_to_dict(self, operation_trees, tmp_path):
        # Arrange
        trees = self.trees
        file = tmp_path / "file"
        file.write_text("")
        producer_node = trees[0].root.file_consumers[0].producers[0]
        assert isinstance(producer_node, FilePickerNode)
        producer_node.file = tmp_path / "file"
        trees[1].root.file_consumers[0].selected_index = 1

        # Act
        dict1 = trees[0].to_dict()
        dict2 = trees[1].to_dict()
        print(dict1)
        print(dict2)

        # Assert
        assert "file_consumers" in dict1
        assert len(dict1["file_consumers"]) == 1
        consumer = dict1["file_consumers"][0]
        assert "selected" in consumer
        assert consumer["selected"] == 0
        assert "file_producers" in consumer
        assert len(consumer["file_producers"]) == 1
        producer = consumer["file_producers"][0]
        assert "file_path" in producer
        assert producer["file_path"] == tmp_path / "file"

        assert "file_consumers" in dict2
        assert len(dict2["file_consumers"]) == 1
        consumer = dict2["file_consumers"][0]
        assert "selected" in consumer
        assert consumer["selected"] == 1
        assert "file_producers" in consumer
        assert len(consumer["file_producers"]) == 2
        producer = consumer["file_producers"][1]
        assert "file_consumers" in producer
    
    def test_populate_from_dict(self, operation_trees):
        # Arrange
        trees = self.trees
        dict1 = {
            'file_consumers': [
                {'selected': 0, 
                 'file_producers': [
                     {'file_path': posixpath.abspath('tmp/pytest-of-loes/pytest-21/test_tree_to_dict0/file')}
                     ]
                }
            ], 
            'parameters': {}}
        dict2 = {
            'file_consumers': [
                {
                    'selected': 1, 
                    'file_producers': [
                        {
                            'file_path': None
                        }, {
                            'file_consumers': [
                                {
                                    'selected': 0, 
                                    'file_producers': [
                                        {
                                            'file_path': None
                                        }
                                    ]
                                }
                            ],
                            'parameters': {}
                        }
                    ]
                }
                ], 
            'parameters': {}}

        # Act
        trees[0].populate_from_dict(dict1)
        trees[1].populate_from_dict(dict2)

        # Assert
        assert trees[0].root.file_consumers[0].producers[0].file
        assert trees[1].root.file_consumers[0].selected_index == 1


