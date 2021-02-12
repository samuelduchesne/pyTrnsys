"""InitialInputValuesCollection module."""

import tabulate
from pint.quantity import _Quantity

from trnsystor.collections.variable import VariableCollection
from trnsystor.statement import Constant, Equation
from trnsystor.typevariable import TypeVariable
from trnsystor.utils import _parse_value


class InitialInputValuesCollection(VariableCollection):
    """Subclass of :class:`VariableCollection` specific to Initial Input
    Values

    Hint:
        Iterating over `InitialInputValuesCollection` will not pass Inputs that
        considered ``questions``. For example, Type15 (printer) has a question for
        the number of variables to be printed by the component. This question can be
        accessed with `.inputs[
        "How_many_variables_are_to_be_printed_by_this_component_"]` to
        modify the number of values. But when iterating over the initial inputs,
        the question will not be returned in the iterator; only regular inputs will.
    """

    def __init__(self):
        super().__init__()
        pass

    def __repr__(self):
        num_inputs = "{} Initial Input Values:\n".format(self.size)
        value: TypeVariable
        inputs = "\n".join(
            [
                '"{}": {:~P}'.format(key, value.default)
                for key, value in self.data.items()
            ]
        )
        return num_inputs + inputs

    def __iter__(self):
        """Iterate over inputs except questions."""
        return iter({k: v for k, v in self.data.items() if not v._is_question})

    def __getitem__(self, key):
        """
        Args:
            key:
        """
        if isinstance(key, int):
            type_variable = list(self.values())[key]
        else:
            type_variable = super(VariableCollection, self).__getitem__(key)
        return type_variable

    def __setitem__(self, key, value):
        """Set item."""

        if isinstance(value, TypeVariable):
            """if a TypeVariable is given, simply set it"""
            super().__setitem__(key, value)
        elif isinstance(value, (int, float, str)):
            """a str, float, int, etc. is passed"""
            value = _parse_value(
                value, self[key].type, self[key].unit, (self[key].min, self[key].max)
            )
            self[key].__setattr__("default", value)
        elif isinstance(value, _Quantity):
            self[key].__setattr__("default", value.to(self[key].value.units))
        elif isinstance(value, (Equation, Constant)):
            self[key].__setattr__("default", value)
        else:
            raise TypeError(
                "Cannot set a default value of type {} in this "
                "VariableCollection".format(type(value))
            )

    def _to_deck(self):
        """Returns the string representation for the Initial Input Values"""
        if self.size == 0:
            # Don't need to print empty inputs
            return ""

        head = "*** INITIAL INPUT VALUES\n"
        input_tuples = [
            (
                v.default.m if isinstance(v.default, _Quantity) else v.default,
                "! {}".format(v.name),
            )
            for v in self.values()
        ]
        core = tabulate.tabulate(input_tuples, tablefmt="plain", numalign="left")
        return head + core + "\n"
