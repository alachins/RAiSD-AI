from pytest import fixture, raises
from unittest.mock import MagicMock
from gui.tests.utils.mock_signal import MockSignal

from gui.model.parameter import ParameterGroup



class TestParameterGroupUnit:
    """Unit tests for ParameterGroup class."""

    @fixture
    def mock_parameter(self):
        """Fixture that returns a factory for creating mock parameters"""

        def _make(enabled: bool = True, valid: bool = True, cli_output: str = "") -> MagicMock:
            """ Create a mock Parameter with a MockSignal """
            param = MagicMock()
            param.enabled = enabled
            param.valid = valid
            param.to_cli = MagicMock(return_value=cli_output)
            param.enabled_changed = MockSignal(bool)
            return param

        return _make

    def test_init_name(self):
        """Test that the group stores its name."""
        # arrange / act
        group = ParameterGroup(name="g")

        # assert
        assert group.name == "g"

    def test_init_empty_parameters(self):
        """Test ParameterGroup initialization when the parameters list is empty."""
        # arrange / act
        group = ParameterGroup(name="empty_group")

        # assert
        assert group.parameters == []
        assert not group.enabled

    def test_init_parameters_none_defaults_to_empty_list(self):
        """Test that parameter group without parameters defaults to an empty list."""
        # arrange / act
        group = ParameterGroup(name="g")

        # assert
        assert group.parameters == []

    def test_init_enabled_true_when_param_is_enabled(self, mock_parameter):
        """Test that a group initialised with at an enabled parameter reports enabled=True."""
        # arrange
        param = mock_parameter(enabled=True)

        # act
        group = ParameterGroup(name="g", parameters=[param])

        # assert
        assert group.enabled is True

    def test_init_enabled_false_when_params_disabled(self, mock_parameter):
        """Test that a group initialised with disabled parameter reports enabled=False."""
        # arrange
        param = mock_parameter(enabled=False)

        # act
        group = ParameterGroup(name="g", parameters=[param])

        # assert
        assert group.enabled is False

    def test_init_connects_enabled_changed_for_each_param(self, mock_parameter):
        """Test that __init__ connects to enabled_changed of every parameter."""
        # arrange
        param1 = mock_parameter()
        param2 = mock_parameter()

        # act
        ParameterGroup(name="g", parameters=[param1, param2])

        # assert
        assert len(param1.enabled_changed.slots) == 1
        assert len(param2.enabled_changed.slots) == 1

    def test_enabled_false_when_all_params_become_disabled(self, mock_parameter):
        """Test enabled becomes False when all parameters are disabled via signal."""
        # arrange
        param1 = mock_parameter(enabled=True)
        param2 = mock_parameter(enabled=True)
        group = ParameterGroup(name="g", parameters=[param1, param2])

        # act
        param1.enabled = False
        param1.enabled_changed.emit(False)

        # assert
        assert group.enabled is True

        # act
        param2.enabled = False
        param2.enabled_changed.emit(False)

        # assert
        assert group.enabled is False

    def test_add_parameter_appends_to_list(self, mock_parameter):
        """Test adding a parameter to an existing ParameterGroup actually adds the parameter to the group."""
        # arrange
        group = ParameterGroup(name="g")
        param = mock_parameter()

        # act
        group.add_parameter(param)

        # assert
        assert len(group.parameters) == 1
        assert group.parameters[0] is param

    def test_add_parameter_connects_enabled_changed(self, mock_parameter):
        """Test that add_parameter connects to the parameter's enabled_changed signal."""
        # arrange
        group = ParameterGroup(name="g")
        param = mock_parameter()

        # act
        group.add_parameter(param)

        # assert
        assert len(param.enabled_changed.slots) == 1

    def test_add_enabled_param_to_disabled_group_enables_group(self, mock_parameter):
        """Test that adding an enabled parameter to a disabled group updates the group's enabled state."""
        # arrange
        group = ParameterGroup(name="g")
        param = mock_parameter(enabled=True)

        # act
        group.add_parameter(param)

        # assert
        assert group.enabled is True

    def test_add_disabled_param_to_disabled_group_stays_disabled(self, mock_parameter):
        """Test that adding a disabled parameter to a disabled group leaves the group disabled."""
        # arrange
        group = ParameterGroup(name="g")
        param = mock_parameter(enabled=False)

        # act
        group.add_parameter(param)

        # assert
        assert group.enabled is False

    def test_add_disabled_param_to_enabled_group_stays_enabled(self, mock_parameter):
        """Test that adding a disabled parameter to an already-enabled group leaves the group enabled."""
        # arrange
        param_old = mock_parameter(enabled=True)
        group = ParameterGroup(name="g", parameters=[param_old])
        param_new = mock_parameter(enabled=False)

        # act
        group.add_parameter(param_new)

        # assert
        assert group.enabled is True

    def test_add_parameter_emits_enabled_changed_when_group_becomes_enabled(self, mock_parameter):
        """Test that enabled_changed is emitted when adding an enabled param enables the group."""
        # arrange
        group = ParameterGroup(name="g")
        emitted = []
        group.enabled_changed.connect(lambda v: emitted.append(v))
        param = mock_parameter(enabled=True)

        # act
        group.add_parameter(param)

        # assert
        assert emitted == [True]

    def test_add_parameter_does_not_emit_enabled_changed_when_state_unchanged(self, mock_parameter):
        """Test that enabled_changed is not emitted when add_parameter doesn't change enabled state."""
        # arrange
        param_old = mock_parameter(enabled=True)
        group = ParameterGroup(name="g", parameters=[param_old])
        emitted = []
        group.enabled_changed.connect(lambda v: emitted.append(v))
        param_new = mock_parameter(enabled=False)

        # act
        group.add_parameter(param_new)

        # assert
        assert emitted == []

    def test_valid_all_valid(self, mock_parameter):
        """Test validity of ParameterGroup when all parameters are valid."""
        # arrange
        param1 = mock_parameter(valid=True)
        param2 = mock_parameter(valid=True)
        group = ParameterGroup(name="g", parameters=[param1, param2])

        # act / assert
        assert group.valid

    def test_valid_one_invalid(self, mock_parameter):
        """Test validity of ParameterGroup when a single parameter is invalid."""
        # arrange
        param1 = mock_parameter(valid=True)
        param2 = mock_parameter(valid=False)
        group = ParameterGroup(name="g", parameters=[param1, param2])

        # act / assert
        assert not group.valid

    def test_valid_empty_group(self):
        """Test that an empty group is considered valid."""
        # arrange
        group = ParameterGroup(name="empty_group")

        # act / assert
        assert group.valid

    def test_to_cli_joins_nonempty_param_outputs(self, mock_parameter):
        """Test to_cli joins non-empty parameter CLI outputs with spaces."""
        # arrange
        param1 = mock_parameter(cli_output="-a val")
        param2 = mock_parameter(cli_output="-b")
        group = ParameterGroup(name="g", parameters=[param1, param2])

        # act
        result = group.to_cli("OP")

        # assert
        assert result == "-a val -b"

    def test_to_cli_skips_empty_param_outputs(self, mock_parameter):
        """Test to_cli skips parameters that return an empty string."""
        # arrange
        param1 = mock_parameter(cli_output="-a")
        param2 = mock_parameter(cli_output="")
        group = ParameterGroup(name="g", parameters=[param1, param2])

        # act
        result = group.to_cli("OP")

        # assert
        assert result == "-a"

    def test_to_cli_passes_operation_to_each_param(self, mock_parameter):
        """Test that to_cli forwards the operation string to every parameter."""
        # arrange
        param1 = mock_parameter(cli_output="-a")
        param2 = mock_parameter(cli_output="-b")
        group = ParameterGroup(name="g", parameters=[param1, param2])

        # act
        group.to_cli("MDL-GEN")

        # assert
        param1.to_cli.assert_called_once_with("MDL-GEN")
        param2.to_cli.assert_called_once_with("MDL-GEN")

    def test_to_cli_empty_group(self):
        """Test to_cli returns an empty string when the parameter list is empty."""
        # arrange
        group = ParameterGroup(name="empty_group")

        # act
        result = group.to_cli('MDL-GEN')

        # assert
        assert result == ""

    def test_to_cli_invalid_parameter(self, mock_parameter):
        """Test that a parameter group with valid parameter has the same CLI output
         as a parameter group with the same parameter, but invalid."""
        # arrange
        param_valid = mock_parameter(valid=True, cli_output="-flag_string val")
        group_valid = ParameterGroup(name="g", parameters=[param_valid])
        param_invalid = mock_parameter(valid=False, cli_output="-flag_string val")
        group_invalid = ParameterGroup(name="g", parameters=[param_invalid])

        # act
        result_valid = group_valid.to_cli("OP")
        result_invalid = group_invalid.to_cli("OP")

        # assert
        assert result_valid == result_invalid

    def test_iter(self, mock_parameter):
        """Test that iterating over a ParameterGroup yields its parameters."""
        # arrange
        param1 = mock_parameter()
        param2 = mock_parameter()
        group = ParameterGroup(name="g", parameters=[param1, param2])

        # act
        result = list(group)

        # assert
        assert result == [param1, param2]

    def test_iter_empty_group(self):
        """Test that iterating over an empty ParameterGroup yields nothing."""
        # arrange
        group = ParameterGroup(name="empty_group")

        # act
        result = list(group)

        # assert
        assert result == []

    def test_getitem(self, mock_parameter):
        """Test index access on a ParameterGroup."""
        # arrange
        param1 = mock_parameter()
        param2 = mock_parameter()
        group = ParameterGroup(name="g", parameters=[param1, param2])

        # act / assert
        assert group[0] is param1
        assert group[1] is param2

    def test_getitem_out_of_range(self):
        """Test that out-of-range index access raises IndexError."""
        # arrange
        group = ParameterGroup(name="g")

        # act / assert
        with raises(IndexError):
            _ = group[0]

    def test_str(self):
        """Test __str__ includes the group name and CLI output."""
        # arrange
        group = ParameterGroup(name="my_group")

        # act
        result = str(group)

        # assert
        assert "my_group" in result

