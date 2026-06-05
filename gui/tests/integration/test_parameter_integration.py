from pytest import fixture
import re

from gui.model.parameter import (
    Condition,
    IntervalConstraint,
    MaxLengthConstraint,
    RegexConstraint,
    BoolParameter,
    IntParameter,
    FloatParameter,
    StringParameter,
    EnumParameter,
    FileParameter,
    OptionalParameter,
    MultiParameter,
)

class TestBoolParameter:
    """Tests for BoolParameter class."""

    @fixture(autouse=True)
    def set_bool_param(self):
        self.bool_param = BoolParameter(
            name="testbool", 
            description="Test bool parameter", 
            flag="--testbool", 
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value=False
        )

        # Add a condition to control the parameter's enabled status.
        self.condition = Condition(
            value=True,
        )
        self.bool_param.add_condition(self.condition)

    def test_init_values(self):
        """Test BoolParameter initialization with default value."""
        param = self.bool_param
        assert param.name == "testbool"
        assert param.description == "Test bool parameter"
        assert param.flag == "--testbool"
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.value is False
        assert param.default_value is False
        assert param.enabled

    def test_set_value(self):
        """Test setting BoolParameter value."""
        param = self.bool_param
        param.value = True
        assert param.value is True

    def test_reset_value(self):
        """Test resetting BoolParameter value to default."""
        param = self.bool_param
        param.value = True
        param.reset_value()
        assert param.value is False

    def test_enabled(self):
        """Test `BoolParameter`'s `enabled` property."""
        # Arrange
        param = self.bool_param
        condition = self.condition

        # Act
        condition.value = False
        # Assert
        assert not param.enabled

        # Act
        condition.value = True
        # Assert
        assert param.enabled

    def test_enabled_signal(self):
        """
        Test that the `enabled_changed` signal of `BoolParameter` is
        emitted when its condition becomes `True`.
        """
        param = self.bool_param
        condition = self.condition

        # Arrange
        condition.value = False
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = True

        # Assert
        assert self.signal_emitted

    def test_disabled_signal(self):
        """
        Test that the `enabled_changed` signal of `BoolParameter` is
        emitted when its condition becomes `False`.
        """
        param = self.bool_param
        condition = self.condition

        # Arrange
        condition.value = True
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert not new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = False

        # Assert
        assert self.signal_emitted

    def test_valid(self):
        """Test BoolParameter validity."""
        param = self.bool_param
        assert param.valid is True

    def test_to_cli(self):
        """Test BoolParameter command-line representation."""
        param = self.bool_param
        condition = self.condition
        assert param.to_cli('IMG-GEN') == ""
        param.value = True
        assert param.to_cli('SWP-SCN') == ""
        assert param.to_cli('IMG-GEN') == param.flag
        assert param.to_cli('MDL-GEN') == param.flag
        condition.value = False
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when BoolParameter value changes."""
        # arrange
        param = self.bool_param
        self.signal_emitted = False
        self.new_value = True
        self.value = False
        self.valid = False

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted is True
        assert self.value == self.new_value
        assert self.valid == True

class TestIntParameter:
    """Tests for IntParameter class."""

    @fixture(autouse=True)
    def set_int_param(self):
        self.int_param = IntParameter(
            name="testint", 
            description="Test int parameter", 
            flag="--testint ", 
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value=0, 
            constraints=[
                IntervalConstraint(
                    lower_bound=-10,
                    upper_bound=10,
                ),
            ],
        )

        # Add a condition to control the parameter's enabled status.
        self.condition = Condition(
            value=True,
        )
        self.int_param.add_condition(self.condition)
    
    def test_init_values(self):
        """Test IntParameter initialization with default value."""
        param = self.int_param
        assert param.name == "testint"
        assert param.description == "Test int parameter"
        assert param.flag == "--testint "
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.value == 0
        assert param.default_value == 0
        assert len(param.constraints) == 1
        assert param.enabled

    def test_set_value(self):
        """Test setting IntParameter value."""
        param = self.int_param
        param.value = 5
        assert param.value == 5

    def test_reset_value(self):
        """Test resetting IntParameter value to default."""
        param = self.int_param
        param.value = 5
        param.reset_value()
        assert param.value == 0

    def test_enabled(self):
        """Test `IntParameter`'s `enabled` property."""
        # Arrange
        param = self.int_param
        condition = self.condition

        # Act
        condition.value = False
        # Assert
        assert not param.enabled

        # Act
        condition.value = True
        # Assert
        assert param.enabled

    def test_enabled_signal(self):
        """
        Test that the `enabled_changed` signal of `IntParameter` is
        emitted when its condition becomes `True`.
        """
        param = self.int_param
        condition = self.condition

        # Arrange
        condition.value = False
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = True

        # Assert
        assert self.signal_emitted

    def test_disabled_signal(self):
        """
        Test that the `enabled_changed` signal of `IntParameter` is
        emitted when its condition becomes `False`.
        """
        param = self.int_param
        condition = self.condition

        # Arrange
        condition.value = True
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert not new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = False

        # Assert
        assert self.signal_emitted

    def test_valid(self):
        """Test IntParameter validity."""
        param = self.int_param
        assert param.valid
        param.value = -15
        assert not param.valid
        param.value = 15
        assert not param.valid
        param.value = 5
        assert param.valid

    def test_to_cli(self):
        """Test IntParameter command-line representation."""
        param = self.int_param
        condition = self.condition
        assert param.to_cli('IMG-GEN') == f"{param.flag}{param.value}"
        param.value = new_value = 5
        assert param.to_cli('MDL-GEN') == f"{param.flag}{new_value}"
        assert param.to_cli('SWP_SCN') == ""
        condition.value = False
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when IntParameter value changes."""
        # arrange
        param = self.int_param
        self.signal_emitted = False
        self.value = 1
        self.new_value = 5
        self.valid = False

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted
        assert self.value == self.new_value
        assert self.valid

    def test_invalid_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when IntParameter value changes."""
        # arrange
        param = self.int_param
        self.signal_emitted = False
        self.value = 1
        self.new_value = 15
        self.valid = True

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        # act
        param.value_changed.connect(on_value_changed)
        param.value = self.new_value

        # assert
        assert self.signal_emitted
        assert self.value == self.new_value
        assert not self.valid

class TestFloatParameter:
    """Tests for FloatParameter class."""

    @fixture(autouse=True)
    def set_float_param(self):
        self.float_param = FloatParameter(
            name="testfloat", 
            description="Test float parameter", 
            flag="--testfloat ", 
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value=0.0, 
            constraints=[
                IntervalConstraint(
                    lower_bound=-10.0,
                    upper_bound=10.0,
                ),
            ],
        )

        # Add a condition to control the parameter's enabled status.
        self.condition = Condition(
            value=True,
        )
        self.float_param.add_condition(self.condition)
    
    def test_init_values(self):
        """Test FloatParameter initialization with default value."""
        param = self.float_param
        assert param.name == "testfloat"
        assert param.description == "Test float parameter"
        assert param.flag == "--testfloat "
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.value == 0.0
        assert param.default_value == 0.0
        assert len(param.constraints) == 1

    def test_set_value(self):
        """Test setting FloatParameter value."""
        param = self.float_param
        param.value = 5.0
        assert param.value == 5.0

    def test_reset_value(self):
        """Test resetting FloatParameter value to default."""
        param = self.float_param
        param.value = 5.0
        param.reset_value()
        assert param.value == 0.0

    def test_enabled(self):
        """Test `FloatParameter`'s `enabled` property."""
        # Arrange
        param = self.float_param
        condition = self.condition

        # Act
        condition.value = False
        # Assert
        assert not param.enabled

        # Act
        condition.value = True
        # Assert
        assert param.enabled

    def test_enabled_signal(self):
        """
        Test that the `enabled_changed` signal of `FloatParameter` is
        emitted when its condition becomes `True`.
        """
        param = self.float_param
        condition = self.condition

        # Arrange
        condition.value = False
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = True

        # Assert
        assert self.signal_emitted

    def test_disabled_signal(self):
        """
        Test that the `enabled_changed` signal of `FloatParameter` is
        emitted when its condition becomes `False`.
        """
        param = self.float_param
        condition = self.condition

        # Arrange
        condition.value = True
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert not new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = False

        # Assert
        assert self.signal_emitted

    def test_valid(self):
        """Test FloatParameter validity."""
        param = self.float_param
        assert param.valid
        param.value = -15.0
        assert not param.valid
        param.value = 15.0
        assert not param.valid
        param.value = 5.0
        assert param.valid

    def test_to_cli(self):
        """Test FloatParameter command-line representation."""
        param = self.float_param
        condition = self.condition
        assert param.to_cli('IMG-GEN') == f"{param.flag}{param.value}"
        param.value = new_value = 5.0
        assert param.to_cli('MDL-GEN') == f"{param.flag}{new_value}"
        assert param.to_cli('SWP-SCN') == ""
        condition.value = False
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when FloatParameter value changes."""
        # arrange
        param = self.float_param
        self.signal_emitted = False
        self.value = 1.0
        self.new_value = 5.0
        self.valid = False

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted
        assert self.value == self.new_value
        assert self.valid

    def test_invalid_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when FloatParameter value changes."""
        # arrange
        param = self.float_param
        self.signal_emitted = False
        self.value = 1.0
        self.new_value = 15.0
        self.valid = True

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted
        assert self.value == self.new_value
        assert not self.valid

class TestStringParameter:
    """Tests for StringParameter class."""

    @fixture(autouse=True)
    def set_string_param(self):
        self.string_param = StringParameter(
            name="teststring",
            description="Test string parameter",
            flag="--teststring ",
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value="default",
            constraints=[
                MaxLengthConstraint(20),
                RegexConstraint(
                    pattern=re.compile(r"\b[a-z]+\b"),
                    hint="Only lowercase letters.",
                ),
            ],
        )

        # Add a condition to control the parameter's enabled status.
        self.condition = Condition(
            value=True,
        )
        self.string_param.add_condition(self.condition)

    def test_init_values(self):
        """Test StringParameter initialization with default value."""
        param = self.string_param
        assert param.name == "teststring"
        assert param.description == "Test string parameter"
        assert param.flag == "--teststring "
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.value == "default"
        assert param.default_value == "default"
        assert len(param.constraints) == 2

    def test_set_value(self):
        """Test setting StringParameter value."""
        param = self.string_param
        param.value = "new_value"
        assert param.value == "new_value"

    def test_reset_value(self):
        """Test resetting StringParameter value to default."""
        param = self.string_param
        param.value = "new_value"
        param.reset_value()
        assert param.value == "default"

    def test_enabled(self):
        """Test `StringParameter`'s `enabled` property."""
        # Arrange
        param = self.string_param
        condition = self.condition

        # Act
        condition.value = False
        # Assert
        assert not param.enabled

        # Act
        condition.value = True
        # Assert
        assert param.enabled

    def test_enabled_signal(self):
        """
        Test that the `enabled_changed` signal of `StringParameter` is
        emitted when its condition becomes `True`.
        """
        param = self.string_param
        condition = self.condition

        # Arrange
        condition.value = False
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = True

        # Assert
        assert self.signal_emitted

    def test_disabled_signal(self):
        """
        Test that the `enabled_changed` signal of `StringParameter` is
        emitted when its condition becomes `False`.
        """
        param = self.string_param
        condition = self.condition

        # Arrange
        condition.value = True
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert not new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = False

        # Assert
        assert self.signal_emitted

    def test_valid_length(self):
        """Test StringParameter length validity."""
        param = self.string_param
        assert param.valid
        param.value = "2invalidvaluesarewalkingonthestreet"
        assert not param.valid
        param.value = "validvalue"
        assert param.valid

    def test_valid_pattern(self):
        """Test StringParameter pattern validity."""
        param = self.string_param
        assert param.valid
        param.value = "invalid value"
        assert not param.valid
        param.value = "validvalue"
        assert param.valid

    def test_to_cli(self):
        """Test StringParameter command-line representation."""
        param = self.string_param
        condition = self.condition
        assert param.to_cli('IMG-GEN') == f"{param.flag}{param.value}"
        param.value = new_value = "new_value"
        assert param.to_cli('MDL-GEN') == f"{param.flag}{new_value}"
        assert param.to_cli('SWP-SCN') == ""
        condition.value = False
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when StringParameter value changes."""
        # arrange
        param = self.string_param
        self.signal_emitted = False
        self.value = ""
        self.new_value = "newvalue"
        self.valid = False

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted
        assert self.value == self.new_value
        assert self.valid

    def test_invalid_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when StringParameter value changes."""
        # arrange
        param = self.string_param
        self.signal_emitted = False
        self.value = "a"
        self.new_value = "invalid value"
        self.valid = True

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted
        assert self.value == self.new_value
        assert not self.valid

class TestEnumParameter:
    """Tests for EnumParameter class."""

    @fixture(autouse=True)
    def set_enum_param(self):
        self.enum_param = EnumParameter(
            name="testenum",
            description="Test enum parameter",
            flag="--testenum ",
            operations={'IMG-GEN', 'MDL-GEN'},
            options=[("discard SNP", "D"), ("input N per SNP", "I"), ("represent N through a mask", "M 2"), ("ignore allele pairs with N", "A")],
            default_value= 0,
        )

        # Add a condition to control the parameter's enabled status.
        self.condition = Condition(
            value=True,
        )
        self.enum_param.add_condition(self.condition)

    def test_init_values(self):
        """Test EnumParameter initialization with default value"""
        param = self.enum_param
        assert param.name == "testenum"
        assert param.description == "Test enum parameter"
        assert param.flag == "--testenum "
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.options[1] == "input N per SNP"
        assert param.default_value == 0

    def test_set_value(self):
        """Test setting EnumParameter value."""
        param = self.enum_param
        param.value = 1
        assert param.value == 1
    
    def rest_reset_value(self):
        """Test resetting EnumParameter value."""
        param = self.enum_param
        param.value = 1
        param.reset_value()
        assert param.value == 0

    def test_enabled(self):
        """Test `EnumParameter`'s `enabled` property."""
        # Arrange
        param = self.enum_param
        condition = self.condition

        # Act
        condition.value = False
        # Assert
        assert not param.enabled

        # Act
        condition.value = True
        # Assert
        assert param.enabled

    def test_enabled_signal(self):
        """
        Test that the `enabled_changed` signal of `EnumParameter` is
        emitted when its condition becomes `True`.
        """
        param = self.enum_param
        condition = self.condition

        # Arrange
        condition.value = False
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = True

        # Assert
        assert self.signal_emitted

    def test_disabled_signal(self):
        """
        Test that the `enabled_changed` signal of `EnumParameter` is
        emitted when its condition becomes `False`.
        """
        param = self.enum_param
        condition = self.condition

        # Arrange
        condition.value = True
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert not new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = False

        # Assert
        assert self.signal_emitted
    
    def test_to_cli(self):
        """Test EnumParameter command-line representation."""
        param = self.enum_param
        condition = self.condition
        assert param.to_cli('IMG-GEN') == "--testenum D"
        param.value = new_value = 3
        assert param.to_cli('MDL-GEN') == "--testenum A"
        assert param.to_cli('SWP-SCN') == ""
        condition.value = False
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when EnumParameter value changes."""
        # arrange
        param = self.enum_param
        self.signal_emitted = False
        self.value = 5
        self.new_value = 3
        self.valid = False

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted
        assert self.value == self.new_value
        assert self.valid

    def test_invalid_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when EnumParameter value changes."""
        # arrange
        param = self.enum_param
        self.signal_emitted = False
        self.value = 0
        self.new_value = 5
        self.valid = True

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted
        assert self.value == self.new_value
        assert not self.valid

class TestFileParameter:
    """Tests for FileParameter class."""

    @fixture(autouse=True)
    def set_file_param(self, tmp_path):

        self.valid_file = tmp_path / "sample.vcf"
        self.valid_file.write_text("data")
        self.second_valid_file = tmp_path / "test.vcf"
        self.second_valid_file.write_text("data")
        self.invalid_file = tmp_path / "sample.txt"
        self.invalid_file.write_text("data")

        self.file_param = FileParameter(
            name="testfile",
            description="Test file parameter",
            flag="--testfile ",
            operations={'IMG-GEN', 'MDL-GEN'},
            accepted_formats=[".vcf"],
            strict=True,
            multiple=True,
            default_value=[str(self.valid_file)]
        )

        # Add a condition to control the parameter's enabled status.
        self.condition = Condition(
            value=True,
        )
        self.file_param.add_condition(self.condition)

    def test_init_values(self):
        """Test FileParameter initialization with default value."""
        param = self.file_param
        assert param.name == "testfile"
        assert param.description == "Test file parameter"
        assert param.flag == "--testfile "
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.accepted_formats == [".vcf"]
        assert param.strict
        assert param.multiple

    def test_set_value(self):
        """Test setting FileParameter value."""
        param = self.file_param
        param.value = [str(self.valid_file)]
        assert param.value == [str(self.valid_file)]

    def test_reset_value(self):
        """Test resetting FileParameter value to default."""
        param = self.file_param
        param.value = ["newfile.txt"]
        param.reset_value()
        assert param.value == [str(self.valid_file)]

    def test_enabled(self):
        """Test `StringParameter`'s `enabled` property."""
        # Arrange
        param = self.file_param
        condition = self.condition

        # Act
        condition.value = False
        # Assert
        assert not param.enabled

        # Act
        condition.value = True
        # Assert
        assert param.enabled

    def test_enabled_signal(self):
        """
        Test that the `enabled_changed` signal of `StringParameter` is
        emitted when its condition becomes `True`.
        """
        param = self.file_param
        condition = self.condition

        # Arrange
        condition.value = False
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = True

        # Assert
        assert self.signal_emitted

    def test_disabled_signal(self):
        """
        Test that the `enabled_changed` signal of `StringParameter` is
        emitted when its condition becomes `False`.
        """
        param = self.file_param
        condition = self.condition

        # Arrange
        condition.value = True
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert not new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = False

        # Assert
        assert self.signal_emitted

    def test_valid_format(self):
        """Test FileParameter format validity."""
        param = self.file_param
        param.value = [str(self.valid_file)]
        assert param.valid

    def test_valid_file_count(self):
        """Test FileParameter validity when no file is selected."""
        param = self.file_param
        param.value = [str(self.invalid_file)]
        assert not param.valid
    
    def test_multiple_false_rejects_two_files(self):
        """Two files should be invalid when multiple=False."""
        param = FileParameter(
            name="testfile",
            description="Test file parameter",
            flag="--testfile",
            operations={'IMG-GEN', 'MDL-GEN'},
            accepted_formats=[".vcf"],
            strict=True,
            multiple=False,
            default_value=[str(self.valid_file)]
        )
        param.value = [str(self.valid_file), str(self.valid_file)]
        assert not param.valid

    def test_multiple_true_accepts_two_files(self):
        """Two valid files should be valid when multiple=True."""
        param = self.file_param
        param.value = [str(self.valid_file), str(self.second_valid_file)]
        assert param.valid

    def test_to_cli(self):
        """Test FileParameter command-line representation."""
        param = self.file_param
        # Doesn't make much sense, but it's expected behavior.
        assert (
            param.to_cli('IMG-GEN')
            == f"--testfile {self.valid_file}"
        )

    def test_value_changed_emitted(self):
        """Test that value_changed signal is emitted when FileParameter value changes."""
        # For now, no way to test for valid value. Maybe we make a temp file?
        # arrange
        param = self.file_param
        self.signal_emitted = False
        self.value = []
        self.new_value = [str(self.second_valid_file)]
        self.valid = True

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted
        assert self.value == self.new_value
        assert self.valid


class TestOptionalParameter:
    """Tests for OptionalParameter class."""

    @fixture(autouse=True)
    def set_optional_parameter(self):
        self.int_param = IntParameter(
            name="testint",
            description="Test int parameter",
            flag="--testint ",
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value=0,
            constraints=[
                IntervalConstraint(
                    lower_bound=-10,
                    upper_bound=10,
                ),
            ],
        )

        self.optional_param = OptionalParameter(
            name="testoptional",
            description="Test optional parameter",
            operations={"IMG-GEN", "MDL-GEN"},
            default_value = True,
            parameter=self.int_param,
        )

        # Add a condition to control the parameter's enabled status.
        self.condition = Condition(
            value=True,
        )
        self.optional_param.add_condition(self.condition)

    def test_init_values(self):
        """Test OptionalParameter initialization with default value."""
        param = self.optional_param
        assert param.name == "testoptional"
        assert param.description == "Test optional parameter"
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.default_value
        assert param.parameter == self.int_param
        assert self.int_param.enabled
        assert param.enabled

    def test_set_value(self):
        """Test setting OptionalParameter value."""
        param = self.optional_param
        param.value = False
        assert not self.int_param.enabled

    def test_reset_value(self):
        """Test resetting OptionalParameter value."""
        param = self.optional_param
        param.value = False
        param.reset_value()
        assert self.int_param.enabled

    def test_enabled(self):
        """Test `OptionalParameter`'s `enabled` property."""
        # Arrange
        param = self.optional_param
        condition = self.condition

        # Act
        condition.value = False
        # Assert
        assert not param.enabled
        assert not param.parameter.enabled

        # Act
        condition.value = True
        # Assert
        assert param.enabled
        assert param.parameter.enabled

    def test_enabled_signal(self):
        """
        Test that the `enabled_changed` signal of `OptionalParameter` is
        emitted when its condition becomes `True`.
        """
        param = self.optional_param
        condition = self.condition

        # Arrange
        condition.value = False
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = True

        # Assert
        assert self.signal_emitted

    def test_disabled_signal(self):
        """
        Test that the `enabled_changed` signal of `OptionalParameter` is
        emitted when its condition becomes `False`.
        """
        param = self.optional_param
        condition = self.condition

        # Arrange
        condition.value = True
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert not new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = False

        # Assert
        assert self.signal_emitted

    def test_valid(self):
        """Test OptionalParameter validity."""
        param = self.optional_param
        assert param.valid
        param.value = False
        assert param.valid
        self.int_param.value = -11
        assert param.valid
        param.value = True
        assert not param.valid

    def test_to_cli(self):
        """Test OptionalParameter comand-line representation."""
        param = self.optional_param
        # If OptionalParameter value is true, to_cli gives the cli
        # represenation of the inner parameter.
        assert param.to_cli('IMG-GEN') == "--testint 0"
        assert param.to_cli('SWP-SCN') == ""
        param.value = False
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when OptionalParameter values changes."""
        # arrange
        param = self.optional_param
        self.signal_emitted = False
        self.value = True
        self.new_value = False
        self.valid = False

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted
        assert self.value == self.new_value
        assert self.valid


class TestMultiParameter:
    """Tests for MultiParameter class."""

    @fixture(autouse=True)
    def set_multi_param(self):
        self.int_param = IntParameter(
            name="testint",
            description="Test int parameter",
            flag="",
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value=0,
            constraints=[
                IntervalConstraint(
                    lower_bound=-10,
                    upper_bound=10,
                ),
            ],
        )
        self.bool_param = BoolParameter(
            name="testbool", 
            description="Test bool parameter", 
            flag="--testbool", 
            operations={'IMG-GEN'},
            default_value=False
        )
        self.multi_param = MultiParameter(
            name="testmulti",
            description="Test multi parameter",
            flag="--testmulti",
            operations={"IMG-GEN", "MDL-GEN"},
            parameters=[self.int_param, self.bool_param]
        )

        # Add a condition to control the parameter's enabled status.
        self.condition = Condition(
            value=True,
        )
        self.multi_param.add_condition(self.condition)

    def test_init_values(self):
        """Test MultiParameter initial values"""
        param = self.multi_param
        assert param.name == "testmulti"
        assert param.description == "Test multi parameter"
        assert param.flag == "--testmulti"
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.value == ()
        assert param.enabled
        assert param.parameters == [self.int_param, self.bool_param]
        assert all(inner.enabled for inner in param.parameters)

    def test_reset_value(self):
        """Test resetting MultiParameter's inner parameters to default."""
        param=self.multi_param
        self.int_param.value = 5
        self.bool_param.value = True
        param.reset_value()
        assert self.int_param.value == 0
        assert self.bool_param.value == False

    def test_enabled(self):
        """Test `MultiParameter`'s `enabled` property."""
        # Arrange
        param = self.multi_param
        condition = self.condition

        # Act
        condition.value = False
        # Assert
        assert not param.enabled
        assert all(not inner.enabled for inner in param.parameters)

        # Act
        condition.value = True
        # Assert
        assert param.enabled
        assert all(inner.enabled for inner in param.parameters)

    def test_enabled_signal(self):
        """
        Test that the `enabled_changed` signal of `MultiParameter` is
        emitted when its condition becomes `True`.
        """
        param = self.multi_param
        condition = self.condition

        # Arrange
        condition.value = False
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = True

        # Assert
        assert self.signal_emitted

    def test_disabled_signal(self):
        """
        Test that the `enabled_changed` signal of `MultiParameter` is
        emitted when its condition becomes `False`.
        """
        param = self.multi_param
        condition = self.condition

        # Arrange
        condition.value = True
        self.signal_emitted = False

        def on_enabled_changed(new_enabled):
            self.signal_emitted = True
            assert not new_enabled

        param.enabled_changed.connect(on_enabled_changed)

        # Act
        condition.value = False

        # Assert
        assert self.signal_emitted

    def test_valid(self):
        """Test MultiParameter validity."""
        param = self.multi_param
        assert param.valid
        self.int_param.value = -11
        assert not param.valid

    def test_to_cli(self):
        """Test MultiParameter command-line representation."""
        param = self.multi_param
        assert param.to_cli('IMG-GEN') == f"{param.flag}{self.int_param.value}"
        self.bool_param.value = True
        assert param.to_cli('IMG-GEN') == f"{param.flag}{self.int_param.value} {self.bool_param.flag}"
        assert param.to_cli('SWP_SCN') == ""
