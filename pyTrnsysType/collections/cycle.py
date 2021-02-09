# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2019 - 2021. Samuel Letellier-Duchesne and pyTrnsysType contributors  +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import collections


class CycleCollection(collections.UserList):
    """Collection of :class:`pyTrnsysType.typecycle.TypeCycle`"""

    def __getitem__(self, key):
        """Get item by key.

        Args:
            key:
        """
        value = super().__getitem__(key)
        return value
