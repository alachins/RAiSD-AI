from pytest import approx, fixture
from unittest.mock import PropertyMock
from gui.tests.utils.mock_signal import MockSignal
from PySide6.QtCore import QDir

from gui.model.run_record import RunRecord
import gui.model.run_record as rrecord
from gui.model.parameter import (
    IntervalConstraint,
    MaxLengthConstraint,
    RegexConstraint,
    OptionalParameter,
    MultiParameter,
    BoolParameter,
    IntParameter,
    FloatParameter,
    EnumParameter,
    StringParameter,
    FileParameter,
)


class TestRunRecord:
    """Tests for ParameterGroupList class."""

    @fixture(autouse=True)
    def set_run_record(self, mocker):
        # Run id parameter
        self.run_id_parameter = mocker.Mock()
        self.run_id_parameter.valid = True
        self.run_id_parameter.value = "hi"
        self.run_id_parameter.to_cli = mocker.Mock(return_value="-n hi")
        self.run_id_parameter.reset_value = mocker.MagicMock()
        mock_signal = MockSignal()
        self.run_id_parameter.value_changed.emit = mock_signal.emit
        self.run_id_parameter.value_changed.connect = mock_signal.connect

        # Parameter 1
        self.parameter1 = mocker.Mock()
        self.parameter1.name = "param"
        self.parameter1.valid = True
        self.parameter1.operations = {'IMG-GEN'}
        self.parameter1.populate = mocker.MagicMock()
        self.parameter1.to_cli = mocker.Mock(return_value="-I asdfohds")
        self.parameter1.reset_value = mocker.MagicMock()
        self.parameters = [self.parameter1]

        # Parameter groups
        self.parameter_group1 = mocker.Mock()
        self.parameter_group1.name = 'img'
        self.parameter_group1.parameters = []
        self.parameter_group1.__iter__ = mocker.Mock(side_effect=lambda: iter(self.parameter_group1.parameters))

        self.parameter_group2 = mocker.Mock()
        self.parameter_group2.name = "mdl"
        self.parameter_group2.parameters = [self.parameter1]
        self.parameter_group2.__iter__ = mocker.Mock(side_effect=lambda: iter(self.parameter_group2.parameters))
        
        self.parameter_groups = [
            self.parameter_group1, 
            self.parameter_group2
        ]
        
        # Operation trees
        self.operation_tree_mdl_gen = mocker.Mock()
        self.operation_tree_mdl_gen.to_cli = mocker.Mock(return_value=["cli1"])
        self.operation_tree_mdl_gen.populate_from_dict = mocker.MagicMock()
        tree_signal = MockSignal()
        self.operation_tree_mdl_gen.valid_changed.emit = tree_signal.emit
        self.operation_tree_mdl_gen.valid_changed.connect = tree_signal.connect
        
        self.operation_tree_mdl_tst = mocker.Mock()
        self.operation_tree_mdl_tst.to_cli = mocker.Mock(return_value=["cli2"])
        self.operation_tree_mdl_tst.populate_from_dict = mocker.MagicMock()

        self.operation_trees = [self.operation_tree_mdl_gen, self.operation_tree_mdl_tst]
        self.categorized_operation_trees = [
            ("MDL-GEN", [self.operation_tree_mdl_gen]),
            ("MDL-TST", [self.operation_tree_mdl_tst])
        ]
        
        # Run record
        self.run_record = RunRecord(
            run_id_parameter=self.run_id_parameter,
            categorized_operation_trees=self.categorized_operation_trees,
            parameter_groups=self.parameter_groups,
        )
    
    def test_init_values(self):
        """Test that initialisation of a RunRecord sets its values correctly."""
        # Arrange
        run_id_parameter = self.run_id_parameter
        record = self.run_record
        groups = self.parameter_groups

        # Assert
        assert record.run_id_parameter == run_id_parameter
        assert record.categorized_operation_trees == self.categorized_operation_trees
        assert record.operation_trees == self.operation_trees
        assert record.parameter_groups == groups
        assert record.parameters == self.parameters

    def test_to_history_record(self):
        """Test that a RunRecord is made into a HistoryRecord correctly."""
        # Arrange
        run_record = self.run_record

        # Act
        history_record = run_record.to_history_record()

        # Assert
        assert history_record.name == run_record.run_id_parameter.value
        assert history_record.commands == run_record.to_cli()
        assert history_record.operations["index"] == run_record.selected_operation_tree_index
        assert history_record.operations["trees"] == [tree.to_dict() for tree in run_record.operation_trees]
        assert len(history_record.parameters) == len(run_record.parameters)
        for param in run_record.parameters:
          assert param.name in history_record.parameters.keys()
    
    def test_populate(self, mocker):
        """Test that a RunRecord is populated correctly from the values of a 
        HistoryRecord."""
        # Arrange
        history_record = mocker.Mock()
        history_record.name = "history"
        history_record.operations = {
            "index": 1,
            "trees": ["bla", "blo"]
        }
        history_record.parameters = {"param": 2}
        run_record = self.run_record

        # Act
        run_record.populate(history_record)

        # Assert
        assert run_record.run_id == "history"
        assert run_record.run_id_parameter.value == "history"
        assert run_record.selected_operation_tree_index == 1
        assert run_record.selected_operation_tree == self.operation_trees[1]
        self.operation_tree_mdl_gen.populate_from_dict.assert_called_once_with("bla")
        self.operation_tree_mdl_tst.populate_from_dict.assert_called_once_with("blo")
        self.parameter1.populate.assert_called_once_with(2)

    def test_reset(self):
        """Test that the reset() function of a RunRecord correctly resets
        the contents of the RunRecord."""
        # Arrange
        run_record = self.run_record
        run_record.selected_operation_tree_index = 1
        assert run_record.selected_operation_tree_index == 1

        # Act
        run_record.reset()

        # Assert
        assert run_record.selected_operation_tree_index == 0
        self.run_id_parameter.reset_value.assert_called_once()
        self.parameter1.reset_value.assert_called_once()
    
    def test_run_id_setter(self, mocker):
        """Test that the run_id setter correctly sets the value of the 
        run_id_parameter."""
        # Arrange
        run_record = self.run_record
        print(run_record.run_id_parameter)                    

        # Change to same name
        run_record.run_id = "hi"
        assert run_record.run_id_parameter.value == "hi"

        # Change to different name
        run_record.run_id = "no"
        assert run_record.run_id_parameter.value == "no"
    
    def test_valid(self):
        """Test that the valid attribute of a RunRecord is correctly returned
        dependent on its values."""
        record = self.run_record
        
        record.parameter_groups[0].valid = False # type: ignore
        assert not record.valid
        record.parameter_groups[0].valid = True # type: ignore
        assert record.valid
        record.run_id_parameter.valid = False # type: ignore
        assert not record.run_id_valid
        assert not record.valid

    def test_base_directory_path(self, mocker, tmp_path):
        """Test that the base directory path of the run record is returned 
        correctly."""
        # Arrange
        dir = QDir(str(tmp_path))
        mocker.patch.object(
            type(rrecord.app_settings),
            "workspace_path",
            new_callable=PropertyMock,
            return_value=dir
        )

        # Act
        path = self.run_record.base_directory_path

        # Assert
        assert path == dir.absoluteFilePath("hi")

    def test_run_id_parameter_value_changed(self, mocker):
        # Arrange
        record = self.run_record
        valid_changed_spy = mocker.MagicMock()
        record.run_id_valid_changed.connect(valid_changed_spy)
        mocker.patch.object(
            type(rrecord.app_settings),
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir()
        )

        # Act
        record.run_id_parameter.value_changed.emit("new", False)

        # Assert
        valid_changed_spy.assert_called_once()
        
    def test_operations_valid_changed(self, mocker):
        # Arrange
        record = self.run_record
        valid_changed_spy = mocker.MagicMock()
        record.operations_valid_changed.connect(valid_changed_spy)
        mocker.patch.object(
            type(rrecord.app_settings),
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir()
        )

        # Act
        self.operation_tree_mdl_gen.valid_changed.emit(False)

        # Assert
        valid_changed_spy.assert_called_once()

    def test_to_cli(self):
        """Test that the to_cli of a RunRecord returns the correct command-line
        representation based on its contents."""
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


class TestParameterGroupListFromYaml:
    """Tests for the `ParameterGroupList#from_yaml` class method."""

    def test_correct(self):
        # arrange
        path = "gui/tests/unit/model/resources/correct.yaml"

        # act
        parameter_list = RunRecord.from_yaml(path)

        # assert
        assert len(parameter_list.operation_trees) == 2
        assert len(parameter_list.parameter_groups) == 9

        # Bool
        bool_group = parameter_list.parameter_groups[0]
        assert bool_group.name == "Boolean parameters"
        assert len(bool_group.parameters) == 2

        true_bool = bool_group.parameters[0]
        assert isinstance(true_bool, BoolParameter)
        assert true_bool.name == "True bool"
        assert (
            true_bool.description
            == "This boolean parameter is true by default."
        )
        assert true_bool.flag == "--true-bool"
        assert true_bool.default_value == True
        assert len(true_bool.constraints) == 0

        false_bool = bool_group.parameters[1]
        assert isinstance(false_bool, BoolParameter)
        assert false_bool.name == "False bool"
        assert (
            false_bool.description
            == "A bool parameter that is false by default."
        )
        assert false_bool.flag == "--false-bool"
        assert false_bool.default_value == False
        assert len(false_bool.constraints) == 0

        # Int
        int_group = parameter_list.parameter_groups[1]
        assert int_group.name == "Integer parameters"
        assert len(int_group.parameters) == 7

        any_int_1 = int_group.parameters[0]
        assert isinstance(any_int_1, IntParameter)
        assert any_int_1.name == "Unbounded int"
        assert (
            any_int_1.description
            == "This integer can take any value."
        )
        assert any_int_1.flag == "--unbounded-int"
        assert any_int_1.default_value == 0
        assert len(any_int_1.constraints) == 0

        any_int_2 = int_group.parameters[1]
        assert isinstance(any_int_2, IntParameter)
        assert any_int_2.name == "Another unbounded int"
        assert (
            any_int_2.description
            == "This time, the constraints are empty."
        )
        assert any_int_2.flag == "--int-unrestricted"
        assert any_int_2.default_value == 100
        assert len(any_int_2.constraints) == 0

        min_int_1 = int_group.parameters[2]
        assert isinstance(min_int_1, IntParameter)
        assert min_int_1.name == "Lower-bounded int"
        assert (
            min_int_1.description
            == "This integer must be at least 50."
        )
        assert min_int_1.flag == "-i50"
        assert min_int_1.default_value == 75
        assert len(min_int_1.constraints) == 1
        # TODO: is there a better way to check this than accessing the
        # private field of the parameter?
        min_int_1_constraint = min_int_1._constraints[0]
        assert isinstance(min_int_1_constraint, IntervalConstraint)
        assert min_int_1_constraint._lower_bound == 50
        assert min_int_1_constraint._lower_bound_inclusive
        assert min_int_1_constraint._upper_bound is None

        min_int_2 = int_group.parameters[3]
        assert isinstance(min_int_2, IntParameter)
        assert min_int_2.name == "Another lower-bounded int"
        assert (
            min_int_2.description
            == "Values 30+, upper bound is null."
        )
        assert min_int_2.flag == "-i30"
        assert min_int_2.default_value == 1300
        assert len(min_int_2.constraints) == 1
        min_int_2_constraint = min_int_2._constraints[0]
        assert isinstance(min_int_2_constraint, IntervalConstraint)
        assert min_int_2_constraint._lower_bound == 30
        assert min_int_2_constraint._lower_bound_inclusive
        assert min_int_2_constraint._upper_bound is None

        max_int_1 = int_group.parameters[4]
        assert isinstance(max_int_1, IntParameter)
        assert max_int_1.name == "Upper-bounded int"
        assert (
            max_int_1.description
            == "This integer must be no more than 10."
        )
        assert max_int_1.flag == "-i10"
        assert max_int_1.default_value == -19
        assert len(max_int_1.constraints) == 1
        max_int_1_constraint = max_int_1._constraints[0]
        assert isinstance(max_int_1_constraint, IntervalConstraint)
        assert max_int_1_constraint._lower_bound is None
        assert max_int_1_constraint._upper_bound == 10
        assert max_int_1_constraint._upper_bound_inclusive

        max_int_2 = int_group.parameters[5]
        assert isinstance(max_int_2, IntParameter)
        assert max_int_2.name == "Another upper-bounded int"
        assert (
            max_int_2.description
            == "No more than 15. Lower bound is null."
        )
        assert max_int_2.flag == "-i15"
        assert max_int_2.default_value == 15
        assert len(max_int_2.constraints) == 1
        max_int_2_constraint = max_int_2._constraints[0]
        assert isinstance(max_int_2_constraint, IntervalConstraint)
        assert max_int_2_constraint._lower_bound is None
        assert max_int_2_constraint._upper_bound == 15
        assert max_int_2_constraint._upper_bound_inclusive

        bounded_int = int_group.parameters[6]
        assert isinstance(bounded_int, IntParameter)
        assert bounded_int.name == "Bounded int"
        assert (
            bounded_int.description
            == "This int is from 1 to 10."
        )
        assert bounded_int.flag == "-i1-10"
        assert bounded_int.default_value == 7
        assert len(bounded_int.constraints) == 1
        bounded_int_constraint = bounded_int._constraints[0]
        assert isinstance(bounded_int_constraint, IntervalConstraint)
        assert bounded_int_constraint._lower_bound == 1
        assert bounded_int_constraint._lower_bound_inclusive
        assert bounded_int_constraint._upper_bound == 10
        assert bounded_int_constraint._upper_bound_inclusive

        #Float
        float_group = parameter_list.parameter_groups[2]
        assert float_group.name == "Floating-point parameters"
        assert len(float_group.parameters) == 7

        any_float_1 = float_group.parameters[0]
        assert isinstance(any_float_1, FloatParameter)
        assert any_float_1.name == "Unbounded float"
        assert (
            any_float_1.description
            == "This float can take any value."
        )
        assert any_float_1.flag == "--unbounded-float"
        assert any_float_1.default_value == approx(-3.14159)
        assert len(any_float_1.constraints) == 0

        any_float_2 = float_group.parameters[1]
        assert isinstance(any_float_2, FloatParameter)
        assert any_float_2.name == "Another unbounded float"
        assert (
            any_float_2.description
            == "This time, the constraints are empty."
        )
        assert any_float_2.flag == "--float-unrestricted"
        assert any_float_2.default_value == approx(123.456)
        assert len(any_float_2.constraints) == 0

        min_float_1 = float_group.parameters[2]
        assert isinstance(min_float_1, FloatParameter)
        assert min_float_1.name == "Lower-bounded float"
        assert (
            min_float_1.description
            == "This float must be at least 1.5."
        )
        assert min_float_1.flag == "-f1.5"
        assert min_float_1.default_value == approx(1.9)
        assert len(min_float_1.constraints) == 1
        min_float_1_constraint = min_float_1._constraints[0]
        assert isinstance(min_float_1_constraint, IntervalConstraint)
        assert min_float_1_constraint._lower_bound == approx(1.5)
        assert min_float_1_constraint._lower_bound_inclusive
        assert min_float_1_constraint._upper_bound is None

        min_float_2 = float_group.parameters[3]
        assert isinstance(min_float_2, FloatParameter)
        assert (
            min_float_2.description
            == "Values 3.1+, upper bound is null."
        )
        assert min_float_2.flag == "-f3.1"
        assert min_float_2.default_value == approx(1300)
        assert len(min_float_2.constraints) == 1
        min_float_2_constraint = min_float_2._constraints[0]
        assert isinstance(min_float_2_constraint, IntervalConstraint)
        assert min_float_2_constraint._lower_bound == approx(3.1)
        assert min_float_2_constraint._lower_bound_inclusive
        assert min_float_2_constraint._upper_bound is None

        max_float_1 = float_group.parameters[4]
        assert isinstance(max_float_1, FloatParameter)
        assert max_float_1.name == "Upper-bounded float"
        assert (
            max_float_1.description
            == "This float must be no more than -190.45."
        )
        assert max_float_1.flag == "-f-190.45"
        assert max_float_1.default_value == approx(-199)
        assert len(max_float_1.constraints) == 1
        max_float_1_constraint = max_float_1._constraints[0]
        assert isinstance(max_float_1_constraint, IntervalConstraint)
        assert max_float_1_constraint._lower_bound is None
        assert max_float_1_constraint._upper_bound == approx(-190.45)
        assert max_float_1_constraint._upper_bound_inclusive

        max_float_2 = float_group.parameters[5]
        assert isinstance(max_float_2, FloatParameter)
        assert max_float_2.name == "Another upper-bounded float"
        assert (
            max_float_2.description
            == "No more than 13.13. Lower bound is null."
        )
        assert max_float_2.flag == "-f13.13"
        assert max_float_2.default_value == approx(-23094)
        assert len(max_float_2.constraints) == 1
        max_float_2_constraint = max_float_2._constraints[0]
        assert isinstance(max_float_2_constraint, IntervalConstraint)
        assert max_float_2_constraint._lower_bound is None
        assert max_float_2_constraint._upper_bound == approx(13.13)
        assert max_float_2_constraint._upper_bound_inclusive

        bounded_float = float_group.parameters[6]
        assert isinstance(bounded_float, FloatParameter)
        assert bounded_float.name == "Bounded float"
        assert (
            bounded_float.description
            == "This float is between 0 and 1."
        )
        assert bounded_float.flag == "-f0-1"
        assert bounded_float.default_value == approx(0)
        assert len(bounded_float.constraints) == 1
        bounded_float_constraint = bounded_float._constraints[0]
        assert isinstance(bounded_float_constraint, IntervalConstraint)
        assert bounded_float_constraint._lower_bound == approx(0)
        assert bounded_float_constraint._lower_bound_inclusive
        assert bounded_float_constraint._upper_bound == approx(1)
        assert bounded_float_constraint._upper_bound_inclusive

        # Enum
        enum_group = parameter_list.parameter_groups[3]
        assert enum_group.name == "Enum parameters"
        assert len(enum_group.parameters) == 2

        cli_enum = enum_group.parameters[0]
        assert isinstance(cli_enum, EnumParameter)
        assert cli_enum.name == "Enum parameter"
        assert (
            cli_enum.description
            == "Choose from a list of four values."
        )
        assert cli_enum.flag == "--enum"
        assert cli_enum.default_value == 2
        assert cli_enum.options == [
            "First option",
            "Second option",
            "Third option",
            "Fourth option",
        ]
        assert len(cli_enum.constraints) == 0

        no_cli_enum = enum_group.parameters[1]
        assert isinstance(no_cli_enum, EnumParameter)
        assert no_cli_enum.name == "Dummy enum parameter"
        assert (
            no_cli_enum.description
            == "This parameter will not be in the CLI."
        )
        assert no_cli_enum.flag == ""
        assert no_cli_enum.default_value == 0
        assert no_cli_enum.options == [
            "Choose this...",
            "...or this!",
            "Or even this.",
        ]
        assert len(no_cli_enum.constraints) == 0

        # String
        string_group = parameter_list.parameter_groups[4]
        assert string_group.name == "String parameters"
        assert len(string_group.parameters) == 5

        any_str = string_group.parameters[0]
        assert isinstance(any_str, StringParameter)
        assert any_str.name == "String"
        assert (
            any_str.description
            == "Enter a string. Anything goes!"
        )
        assert any_str.flag == "-s"
        assert any_str.default_value == ""
        assert len(any_str.constraints) == 0

        max_len_str = string_group.parameters[1]
        assert isinstance(max_len_str, StringParameter)
        assert max_len_str.name == "Bounded string"
        assert (
            max_len_str.description
            == "Type at most 4 characters."
        )
        assert max_len_str.flag == "--s-max4"
        assert max_len_str.default_value == ""
        assert len(max_len_str.constraints) == 1
        max_len_str_constraint = max_len_str._constraints[0]
        assert isinstance(max_len_str_constraint, MaxLengthConstraint)
        assert max_len_str_constraint._max_length == 4

        pattern_str = string_group.parameters[2]
        assert isinstance(pattern_str, StringParameter)
        assert pattern_str.name == "Pattern string"
        assert (
            pattern_str.description
            == "This parameter must be only As and Bs."
        )
        assert pattern_str.flag == "--sAB"
        assert pattern_str.default_value == ""
        assert len(pattern_str.constraints) == 1
        pattern_str_constraint = pattern_str._constraints[0]
        assert isinstance(pattern_str_constraint, RegexConstraint)
        pattern_str_constraint._set_value("C")
        assert not pattern_str_constraint.valid
        assert pattern_str_constraint.hint == "Any number of A or B."

        max_len_pattern_str = string_group.parameters[3]
        assert isinstance(max_len_pattern_str, StringParameter)
        assert max_len_pattern_str.name == "Bounded pattern string"
        assert (
            max_len_pattern_str.description
            == "This parameter must be at most 10 digits."
        )
        assert max_len_pattern_str.flag == "--phone-number"
        assert max_len_pattern_str.default_value == ""
        assert len(max_len_pattern_str.constraints) == 2
        max_len_constraint = max_len_pattern_str._constraints[0]
        assert isinstance(max_len_constraint, MaxLengthConstraint)
        assert max_len_constraint._max_length == 10
        pattern_constraint = max_len_pattern_str._constraints[1]
        assert isinstance(pattern_constraint, RegexConstraint)
        pattern_constraint.value = "invalid"
        assert not pattern_constraint.valid
        assert pattern_constraint.hint == "Only digits."

        default_str = string_group.parameters[4]
        assert isinstance(default_str, StringParameter)
        assert default_str.name == "Default value string"
        assert (
            default_str.description
            == "This string already has a default value."
        )
        assert default_str.flag == "--default-str"
        assert default_str.default_value == "Hello"
        assert len(default_str.constraints) == 1
        default_str_constraint = default_str._constraints[0]
        assert isinstance(default_str_constraint, MaxLengthConstraint)
        assert default_str_constraint._max_length == 20

        # File
        file_group = parameter_list.parameter_groups[5]
        assert file_group.name == "File parameters"
        assert len(file_group.parameters) == 6

        any_file = file_group.parameters[0]
        assert isinstance(any_file, FileParameter)
        assert any_file.name == "Any file"
        assert (
            any_file.description
            == "This allows one file of any type."
        )
        assert any_file.flag == "--any-file"
        assert any_file.default_value == []
        assert not any_file.strict
        assert any_file.accepted_formats is None
        assert any_file.expected_formats is None
        assert not any_file.multiple
        assert len(any_file.constraints) == 0

        any_files = file_group.parameters[1]
        assert isinstance(any_files, FileParameter)
        assert any_files.name == "Any files"
        assert (
            any_files.description
            == "This allows many files of any type."
        )
        assert any_files.flag == "--any-files"
        assert any_files.default_value == []
        assert not any_files.strict
        assert any_files.accepted_formats is None
        assert any_files.expected_formats is None
        assert any_files.multiple
        assert len(any_files.constraints) == 0

        not_strict_file = file_group.parameters[2]
        assert isinstance(not_strict_file, FileParameter)
        assert not_strict_file.name == "Expected type file"
        assert (
            not_strict_file.description
            == "One file of any type, image expected."
        )
        assert not_strict_file.flag == "--image"
        assert not_strict_file.default_value == []
        assert not not_strict_file.strict
        assert not_strict_file.accepted_formats is None
        assert not_strict_file.expected_formats == [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
        ]
        assert not not_strict_file.multiple
        assert len(not_strict_file.constraints) == 0

        not_strict_multiple_files = file_group.parameters[3]
        assert isinstance(not_strict_multiple_files, FileParameter)
        assert not_strict_multiple_files.name == "Expected type files"
        assert (
            not_strict_multiple_files.description
            == "Multiple files, videos expected."
        )
        assert not_strict_multiple_files.flag == "--images"
        assert not_strict_multiple_files.default_value == []
        assert not not_strict_multiple_files.strict
        assert not_strict_multiple_files.accepted_formats is None
        assert not_strict_multiple_files.expected_formats == [
            ".mp4",
            ".webm",
        ]
        assert not_strict_multiple_files.multiple
        assert len(not_strict_multiple_files.constraints) == 0

        strict_file = file_group.parameters[4]
        assert isinstance(strict_file, FileParameter)
        assert strict_file.name == "Specific type file"
        assert (
            strict_file.description
            == "One audio file."
        )
        assert strict_file.flag == "--song"
        assert strict_file.default_value == []
        assert strict_file.strict
        assert strict_file.accepted_formats == [
            ".mp3",
            ".wav",
        ]
        assert strict_file.expected_formats is None
        assert not strict_file.multiple
        assert len(strict_file.constraints) == 0

        strict_multiple_files = file_group.parameters[5]
        assert isinstance(strict_multiple_files, FileParameter)
        assert strict_multiple_files.name == "Specific type files"
        assert (
            strict_multiple_files.description
            == "Multiple document files."
        )
        assert strict_multiple_files.flag == "--docs"
        assert strict_multiple_files.default_value == []
        assert strict_multiple_files.strict
        assert strict_multiple_files.accepted_formats == [
            ".doc",
            ".docx",
            ".odf",
            ".pdf",
        ]
        assert strict_multiple_files.expected_formats is None
        assert strict_multiple_files.multiple
        assert len(strict_multiple_files.constraints) == 0

        # Optional
        optional_group = parameter_list.parameter_groups[6]
        assert optional_group.name == "Optional parameters"
        assert len(optional_group.parameters) == 6

        opt_bool = optional_group.parameters[0]
        assert isinstance(opt_bool, OptionalParameter)
        assert opt_bool.name == "Optional bool"
        assert opt_bool.description == "An optional bool parameter."
        assert not opt_bool.default_value
        assert len(opt_bool.constraints) == 0
        inner_bool = opt_bool.parameter
        assert isinstance(inner_bool, BoolParameter)
        assert inner_bool.name == "Inner bool"
        assert inner_bool.description == "The inner parameter."
        assert inner_bool.flag == "--opt-bool"
        assert not inner_bool.default_value
        assert len(inner_bool.constraints) == 0

        opt_int = optional_group.parameters[1]
        assert isinstance(opt_int, OptionalParameter)
        assert opt_int.name == "Optional int"
        assert (
            opt_int.description
            == "An optional int parameter, default true."
        )
        assert opt_int.default_value
        assert len(opt_int.constraints) == 0
        inner_int = opt_int.parameter
        assert isinstance(inner_int, IntParameter)
        assert inner_int.name == "Inner int parameter"
        assert inner_int.description == ""
        assert inner_int.flag == "--opt-int"
        assert inner_int.default_value == 1
        assert len(inner_int.constraints) == 1
        inner_int_constraint = inner_int._constraints[0]
        assert isinstance(inner_int_constraint, IntervalConstraint)
        assert inner_int_constraint._lower_bound == 1
        assert inner_int_constraint._lower_bound_inclusive
        assert inner_int_constraint._upper_bound is None

        opt_float = optional_group.parameters[2]
        assert isinstance(opt_float, OptionalParameter)
        assert opt_float.name == "Optional float"
        assert opt_float.description == "An optional float parameter."
        assert not opt_float.default_value
        assert len(opt_float.constraints) == 0
        inner_float = opt_float.parameter
        assert isinstance(inner_float, FloatParameter)
        assert inner_float.name == "Inner float parameter"
        assert inner_float.description == ""
        assert inner_float.default_value == approx(-1.1)
        assert len(inner_float.constraints) == 0

        opt_enum = optional_group.parameters[3]
        assert isinstance(opt_enum, OptionalParameter)
        assert opt_enum.name == "Optional enum"
        assert opt_enum.description == "An optional enum parameter."
        assert not opt_enum.default_value
        assert len(opt_enum.constraints) == 0
        inner_enum = opt_enum.parameter
        assert isinstance(inner_enum, EnumParameter)
        assert inner_enum.name == ""
        assert (
            inner_enum.description
            == "An inner enum parameter with no name."
        )
        assert inner_enum.flag == "--opt-enum"
        assert inner_enum.default_value == 1
        assert inner_enum.options == ["A", "B", "C"]
        assert len(inner_enum.constraints) == 0

        opt_str = optional_group.parameters[4]
        assert isinstance(opt_str, OptionalParameter)
        assert opt_str.name == "Optional string"
        assert opt_str.description == "An optional string parameter."
        assert not opt_str.default_value
        assert len(opt_str.constraints) == 0
        inner_str = opt_str.parameter
        assert isinstance(inner_str, StringParameter)
        assert inner_str.name == ""
        assert inner_str.description == "The string."
        assert inner_str.flag == "--opt-str"
        assert inner_str.default_value == "example"
        assert len(inner_str.constraints) == 1
        inner_str_constraint = inner_str._constraints[0]
        assert isinstance(inner_str_constraint, MaxLengthConstraint)
        assert inner_str_constraint._max_length == 20

        opt_file = optional_group.parameters[5]
        assert isinstance(opt_file, OptionalParameter)
        assert opt_file.name == "Optional files"
        assert opt_file.description == "An optional multi-file parameter."
        assert not opt_str.default_value
        assert len(opt_str.constraints) == 0
        inner_file = opt_file.parameter
        assert isinstance(inner_file, FileParameter)
        assert inner_file.name == ""
        assert inner_file.description == ""
        assert inner_file.flag == "--opt-files"
        assert inner_file.default_value == []
        assert not inner_file.strict
        assert inner_file.multiple
        assert len(inner_file.constraints) == 0

        # Multi-value
        multi_group = parameter_list.parameter_groups[7]
        assert multi_group.name == "Multi-value parameters"
        assert len(multi_group.parameters) == 2

        int_int_int = multi_group.parameters[0]
        assert isinstance(int_int_int, MultiParameter)
        assert int_int_int.name == "Three integers"
        assert (
            int_int_int.description
            == "A parameter with three integer values."
        )
        assert int_int_int.flag == "-3i"
        assert len(int_int_int.constraints) == 0
        assert len(int_int_int.parameters) == 3
        first_int = int_int_int.parameters[0]
        assert isinstance(first_int, IntParameter)
        assert first_int.name == "First integer"
        assert first_int.description == ""
        assert first_int.default_value == 0
        assert len(first_int.constraints) == 0
        second_int = int_int_int.parameters[1]
        assert isinstance(second_int, IntParameter)
        assert second_int.name == "Second integer"
        assert second_int.description == ""
        assert second_int.default_value == 0
        assert len(second_int.constraints) == 1
        second_int_constraint = second_int._constraints[0]
        assert isinstance(second_int_constraint, IntervalConstraint)
        assert second_int_constraint._lower_bound == 0
        assert second_int_constraint._lower_bound_inclusive
        assert second_int_constraint._upper_bound == 10
        assert second_int_constraint._upper_bound_inclusive
        third_int = int_int_int.parameters[2]
        assert isinstance(third_int, IntParameter)
        assert third_int.name == "Third integer"
        assert third_int.description == ""
        assert third_int.default_value == 0
        assert len(third_int.constraints) == 1
        third_int_constraint = third_int._constraints[0]
        assert isinstance(third_int_constraint, IntervalConstraint)
        assert third_int_constraint._lower_bound == 0
        assert third_int_constraint._lower_bound_inclusive
        assert third_int_constraint._upper_bound is None

        bool_float_file_enum = multi_group.parameters[1]
        assert isinstance(bool_float_file_enum, MultiParameter)
        assert bool_float_file_enum.name == "Mixed parameter"
        assert (
            bool_float_file_enum.description
            == "A parameter with four values."
        )
        assert bool_float_file_enum.flag == "-4"
        assert len(bool_float_file_enum.constraints) == 0
        assert len(bool_float_file_enum.parameters) == 4
        bool_child = bool_float_file_enum.parameters[0]
        assert isinstance(bool_child, BoolParameter)
        assert bool_child.name == "The bool"
        assert bool_child.description == ""
        assert bool_child.default_value
        assert len(bool_child.constraints) == 0
        float_child = bool_float_file_enum.parameters[1]
        assert isinstance(float_child, FloatParameter)
        assert float_child.name == "The float"
        assert float_child.description == ""
        assert float_child.default_value == approx(1.0)
        assert len(float_child.constraints) == 1
        float_child_constraint = float_child._constraints[0]
        assert isinstance(float_child_constraint, IntervalConstraint)
        assert float_child_constraint._lower_bound == approx(0.0)
        assert float_child_constraint._lower_bound_inclusive
        assert float_child_constraint._upper_bound is None
        file_child = bool_float_file_enum.parameters[2]
        assert isinstance(file_child, FileParameter)
        assert file_child.name == "The file"
        assert file_child.description == ""
        assert file_child.default_value == []
        assert not file_child.strict
        assert file_child.accepted_formats is None
        assert file_child.expected_formats == [".ms", ".vcf"]
        assert not file_child.multiple
        assert len(file_child.constraints) == 0
        enum_child = bool_float_file_enum.parameters[3]
        assert isinstance(enum_child, EnumParameter)
        assert enum_child.name == "The enum"
        assert enum_child.description == "Choose one."
        assert enum_child.default_value == 1
        assert enum_child.options == ["Option 0", "Option 1", "Option 2"]
        assert len(enum_child.constraints) == 0

        # Nested
        nested_group = parameter_list.parameter_groups[8]
        assert nested_group.name == "Nested parameters"
        assert len(nested_group.parameters) == 2

        opt_multi = nested_group.parameters[0]
        assert isinstance(opt_multi, OptionalParameter)
        assert opt_multi.name == "Optional multi-value"
        assert (
            opt_multi.description
            == "An optional parameter with two values."
        )
        assert opt_multi.default_value
        assert len(opt_multi.constraints) == 0
        multi_child = opt_multi.parameter
        assert isinstance(multi_child, MultiParameter)
        assert multi_child.name == ""
        assert (
            multi_child.description
            == "The inner, multi-value parameter."
        )
        assert len(multi_child.constraints) == 0
        assert len(multi_child.parameters) == 2
        float_grandchild = multi_child.parameters[0]
        assert isinstance(float_grandchild, FloatParameter)
        assert float_grandchild.name == "A float"
        assert float_grandchild.description == ""
        assert float_grandchild.default_value == approx(0.99)
        assert len(float_grandchild.constraints) == 1
        float_grandchild_constraint = float_grandchild._constraints[0]
        assert isinstance(float_grandchild_constraint, IntervalConstraint)
        assert float_grandchild_constraint._lower_bound == approx(0)
        assert float_grandchild_constraint._lower_bound_inclusive
        assert float_grandchild_constraint._upper_bound == approx(1)
        assert float_grandchild_constraint._upper_bound_inclusive
        str_grandchild = multi_child.parameters[1]
        assert isinstance(str_grandchild, StringParameter)
        assert str_grandchild.name == "A string"
        assert str_grandchild.description == "Type anything."
        assert str_grandchild.default_value == ""
        assert len(str_grandchild.constraints) == 0

        multi_opt = nested_group.parameters[1]
        assert isinstance(multi_opt, MultiParameter)
        assert multi_opt.name == "Multiple optionals"
        assert (
            multi_opt.description
            == "A multi parameter where some are optional."
        )
        assert multi_opt.flag == ""
        assert len(multi_opt.constraints) == 0
        assert len(multi_opt.parameters) == 3
        first_child = multi_opt.parameters[0]
        assert isinstance(first_child, OptionalParameter)
        assert first_child.name == ""
        assert first_child.description == ""
        assert not first_child.default_value
        assert len(first_child.constraints) == 0
        int_grandchild = first_child.parameter
        assert isinstance(int_grandchild, IntParameter)
        assert int_grandchild.name == ""
        assert int_grandchild.description == ""
        assert int_grandchild.flag == ""
        assert int_grandchild.default_value == 6
        assert len(int_grandchild.constraints) == 0
        second_child = multi_opt.parameters[1]
        assert isinstance(second_child, FloatParameter)
        assert second_child.name == ""
        assert second_child.description == "This float is required."
        assert second_child.flag == ""
        assert second_child.default_value == approx(2.5)
        assert len(second_child.constraints) == 1
        second_child_constraint = second_child._constraints[0]
        assert isinstance(second_child_constraint, IntervalConstraint)
        assert second_child_constraint._lower_bound is None
        assert second_child_constraint._upper_bound == approx(2.5)
        assert second_child_constraint._upper_bound_inclusive
        third_child = multi_opt.parameters[2]
        assert isinstance(third_child, OptionalParameter)
        assert third_child.name == "Another float?"
        assert third_child.description == ""
        assert third_child.default_value
        assert len(third_child.constraints) == 0
        float_grandchild = third_child.parameter # Reused variable
        assert isinstance(float_grandchild, FloatParameter)
        assert float_grandchild.name == "The second float"
        assert float_grandchild.description == ""
        assert float_grandchild.default_value == approx(100.8)
        assert len(float_grandchild.constraints) == 0
