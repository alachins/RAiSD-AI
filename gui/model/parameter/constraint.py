from re import Pattern
from typing import Generic, TypeVar
from PySide6.QtCore import QObject, Signal

T = TypeVar("T")


class Constraint(QObject, Generic[T]):
    hint_changed = Signal(str)
    enabled_changed = Signal(bool)
    valid_changed = Signal(bool)

    def __init__(self, value: T | None = None) -> None:
        super().__init__()
        self._value = value

    @property
    def hint(self) -> str:
        raise NotImplementedError()
    
    @property
    def enabled(self) -> bool:
        return True

    @property
    def valid(self) -> bool:
        raise NotImplementedError()

    def _set_value(self, new_value: T) -> None:
        old_hint = self.hint
        old_enabled = self.enabled
        old_valid = self.valid

        self._value = new_value

        if self.hint != old_hint:
            self.hint_changed.emit(self.hint)
        if self.enabled != old_enabled:
            self.enabled_changed.emit(self.enabled)
        if self.valid != old_valid:
            self.valid_changed.emit(self.valid)

    value = property(fset=_set_value)

    def copy(self) -> "Constraint":
        """
        Create a copy of the constraint.
        """
        raise NotImplementedError()


X = TypeVar("X", bound=float)


class IntervalConstraint(Constraint[X]):
    def __init__(
            self,
            lower_bound: X | None = None,
            lower_bound_inclusive: bool = True,
            upper_bound: X | None = None,
            upper_bound_inclusive: bool = True,
            value: X | None = None,
    ) -> None:
        """
        Initialize an `IntervalConstraint` object.

        At least one of the arguments `lower_bound` and `upper_bound`
        must not be `None`.

        :param lower_bound: the lower bound of the interval
        :type lower_bound: int | None

        :param lower_bound_inclusive: whether the lower bound is
        inclusive
        :type lower_bound_inclusive: bool

        :param upper_bound: the upper bound of the interval
        :type upper_bound: int | None

        :param upper_bound_inclusive: whether the upper bound is
        inclusive
        :type upper_bound_inclusive: bool
        """
        super().__init__(value=value)

        if lower_bound is None and upper_bound is None:
            raise ValueError("Both bounds None for interval constraint.")
        self._lower_bound = lower_bound
        self._lower_bound_inclusive = lower_bound_inclusive
        self._upper_bound = upper_bound
        self._upper_bound_inclusive = upper_bound_inclusive

    @property
    def hint(self) -> str:
        if self._lower_bound is None:
            if self._upper_bound_inclusive:
                return f"Less than or equal to {self._upper_bound}."
            return f"Less than {self._upper_bound}."
        if self._upper_bound is None:
            if self._lower_bound_inclusive:
                return f"Greater than or equal to {self._lower_bound}."
            return f"Greater than {self._lower_bound}."
        return (
            f"Between {self._lower_bound} "
            + f"({"in" if self._lower_bound_inclusive else "ex"}clusive) "
            + f"and {self._upper_bound} "
            + f"({"in" if self._upper_bound_inclusive else "ex"}clusive)."
        )

    @property
    def valid(self) -> bool:
        if self._value is None:
            return False
        if self._lower_bound is not None:
            if self._lower_bound_inclusive:
                if self._value < self._lower_bound:
                    return False
            elif self._value <= self._lower_bound:
                return False
        if self._upper_bound is not None:
            if self._upper_bound_inclusive:
                if self._value > self._upper_bound:
                    return False
            elif self._value >= self._upper_bound:
                return False
        return True

    def copy(self) -> "IntervalConstraint":
        return IntervalConstraint(
            lower_bound=self._lower_bound,
            lower_bound_inclusive=self._lower_bound_inclusive,
            upper_bound=self._upper_bound_inclusive,
            upper_bound_inclusive=self._upper_bound_inclusive,
            value=self._value
        )


class EvenConstraint(Constraint[int]):
    @property
    def hint(self) -> str:
        return "The value must be even."

    @property
    def valid(self) -> bool:
        if self._value is None:
            return False
        return self._value % 2 == 0

    def copy(self) -> "EvenConstraint":
        return EvenConstraint(
            value=self._value,
        )


class MaxLengthConstraint(Constraint[str]):
    def __init__(self, max_length: int, value: str | None = None) -> None:
        super().__init__(value=value)
        self._max_length = max_length

    @property
    def hint(self) -> str:
        return f"Maximum {self._max_length} characters."

    @property
    def valid(self) -> bool:
        if self._value is None:
            return False
        return len(self._value) <= self._max_length

    def copy(self) -> "MaxLengthConstraint":
        return MaxLengthConstraint(
            max_length=self._max_length,
            value=self._value,
        )


class RegexConstraint(Constraint[str]):
    def __init__(
            self,
            pattern: Pattern,
            hint: str,
            value: str | None = None,
    ) -> None:
        super().__init__(value=value)
        self._pattern = pattern
        self._hint = hint

    @property
    def hint(self) -> str:
        return self._hint

    @property
    def valid(self) -> bool:
        if self._value is None:
            return False
        return self._pattern.fullmatch(self._value) is not None

    def copy(self) -> "RegexConstraint":
        return RegexConstraint(
            pattern=self._pattern,
            hint=self._hint,
            value=self._value,
        )
