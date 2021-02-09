# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2019 - 2021. Samuel Letellier-Duchesne and pyTrnsysType contributors  +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import collections

import tabulate
from pyTrnsysType.component import Component

from pyTrnsysType.name import Name
from pyTrnsysType.statement import Equation
from pyTrnsysType.studio import StudioHeader


class EquationCollection(Component, collections.UserDict):
    """A class that behaves like a dict and that collects one or more
    :class:`Equations`. This class behaves a little bit like the equation
    component in the TRNSYS Studio, meaning that you can list equation in a
    block, give it a name, etc.

    You can pass a dict of Equation or you can pass a list of Equation. In
    this case, the :attr:`Equation.name` attribute will be used as a key.

    Hint:
        Creating equations in PyTrnsysType is done trough the :class:`Equation`
        class. Equations are than collected in this EquationCollection. See the
        :class:`Equation` class for more details.
    """

    def __init__(self, mutable=None, name=None, **kwargs):
        """Initialize a new EquationCollection.

        Example:
            >>> equa1 = Equation.from_expression("TdbAmb = [011,001]")
            >>> equa2 = Equation.from_expression("rhAmb = [011,007]")
            >>> EquationCollection([equa1, equa2])

        Args:
            mutable (Iterable, optional): An iterable (dict or list).
            name (str): A user defined name for this collection of equations.
                This name will be used to identify this block of equations in
                the .dck file;
        """
        if isinstance(mutable, list):
            _dict = {f.name: f for f in mutable}
        else:
            _dict = mutable
        super(EquationCollection, self).__init__(_dict, meta=None, name=name, **kwargs)

    def __getitem__(self, key):
        """
        Args:
            key:
        """
        if isinstance(key, int):
            value = list(self.data.values())[key]
        else:
            value = super().__getitem__(key)
        return value

    def __hash__(self):
        return self.unit_number

    def __repr__(self):
        return self._to_deck()

    def __setitem__(self, key, value):
        # optional processing here
        value.model = self
        super().__setitem__(key, value)

    def update(self, E=None, **F):
        """D.update([E, ]**F). Update D from a dict/list/iterable E and F.
        If E is present and has a .keys() method, then does:  for k in E: D[
        k] = E[k]
        If E is present and lacks a .keys() method, then does:  for eq.name,
        eq in E: D[eq.name] = eq
        In either case, this is followed by: for k in F:  D[k] = F[k]

        Args:
            E (list, dict or Equation): The equation to add or update in D (
                self).
            F (list, dict or Equation): Other Equations to update are passed.

        Returns:
            None
        """
        if isinstance(E, Equation):
            E.model = self
            _e = {E.name: E}
        elif isinstance(E, list):
            _e = {eq.name: eq for eq in E}
        else:
            for v in E.values():
                if not isinstance(v, Equation):
                    raise TypeError(
                        "Can only update an EquationCollection with an"
                        "Equation, not a {}".format(type(v))
                    )
            _e = {v.name: v for v in E.values()}
        k: Equation
        for k in F:
            if isinstance(F[k], dict):
                _f = {v.name: v for k, v in F.items()}
            elif isinstance(F[k], list):
                _f = {eq.name: eq for eq in F[k]}
            else:
                raise TypeError(
                    "Can only update an EquationCollection with an"
                    "Equation, not a {}".format(type(F[k]))
                )
            _e.update(_f)
        super(EquationCollection, self).update(_e)

    def setdefault(self, key, value=None):
        if key not in self:
            self[key] = value
        return self[key]

    @property
    def size(self):
        return len(self)

    @property
    def unit_number(self):
        return self._unit

    @property
    def unit_name(self):
        """This type does not have a unit_name. Return component name"""
        return self.name

    @property
    def model(self):
        """This model does not have a proforma. Return class name."""
        return self.__class__.__name__

    def _to_deck(self):
        """To deck representation

        Examples::

            EQUATIONS n
            NAME1 = ... equation 1 ...
            NAME2 = ... equation 2 ...
            •
            •
            •
            NAMEn = ... equation n ...
        """
        header_comment = '* EQUATIONS "{}"\n\n'.format(self.name)
        head = "EQUATIONS {}\n".format(len(self))
        v_ = ((equa.name, "=", equa._to_deck()) for equa in self.values())
        core = tabulate.tabulate(v_, tablefmt="plain", numalign="left")
        return str(header_comment) + str(head) + str(core)

    def _get_inputs(self):
        """inputs getter. Sorts by order number each time it is called"""
        return self

    def _get_outputs(self):
        """outputs getter. Since self is already a  dict, return self."""
        return self

    def _get_ordered_filtered_types(self, classe_, store):
        """
        Args:
            classe_:
            store:
        """
        return collections.OrderedDict(
            (attr, self._meta[store][attr])
            for attr in sorted(
                self._get_filtered_types(classe_, store),
                key=lambda key: self._meta[store][key].order,
            )
        )

    def _get_filtered_types(self, classe_, store):
        """
        Args:
            classe_:
            store:
        """
        return filter(
            lambda kv: isinstance(self._meta[store][kv], classe_), self._meta[store]
        )
