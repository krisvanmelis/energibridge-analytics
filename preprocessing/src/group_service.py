"""
Module containing a service with functionality for experiment groups.
"""
from typing import List, Optional

from models.group import Group


class GroupService:
    """
    Service with functionality for experiment groups.
    """
    _groups: List[Group]

    def __init__(self):
        self._groups = [
            Group(
                name="sample visualization",
                folder_path="csv-data/preprocessing_output",
            )
        ]

    def find_group(self, group_name: str) -> Optional[Group]:
        """
        Find group by name.

        :param group_name: Name of group
        :return: Group if found else None
        """
        for group in self._groups:
            if group.name.lower() == group_name.lower():
                return group
        return None

    def get_groups(self) -> List[Group]:
        """
        Get list of all group parseable by frontend.

        :return: List of Groups
        """
        return self._groups

    def add_group(self, group_name: str, folder_path: str) -> List[Group]:
        """
        Add group to list of groups.
        Throws error if group already exists or data is not found.

        :param group_name: Name of group
        :param folder_path: Folder path where trial data is located
        :return: New list of groups
        """
        if self.find_group(group_name) is not None:
            raise ValueError(f'Group with name "{group_name}" already exists.')

        group = Group(group_name, folder_path)
        self._groups.append(group)
        return self._groups

    def delete_group(self, group_name: str) -> List[Group]:
        """
        Delete group from list of groups by name.
        Throws error if group does not exist.

        :param group_name: Name of group
        :return: New list of Groups
        """
        if self.find_group(group_name) is None:
            raise ValueError(f'Group with name "{group_name}" does not exist.')

        self._groups = [group for group in self._groups if group.name.lower() != group_name.lower()]
        return self._groups
