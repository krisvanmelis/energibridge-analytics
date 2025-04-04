"""
Module containing a service with functionality for experiment groups.
"""
from typing import List, Optional
import os

from models.group import Group


class GroupService:
    """
    Service with functionality for experiment groups.
    """
    _groups: List[Group]

    def __init__(self):
        print('Looking for existing groups in:', Group.output_folder)
        if not os.path.exists(Group.output_folder):
            os.makedirs(Group.output_folder)
        # self._groups = [Group(f, is_import=True)
        #                 for f in os.listdir(Group.output_folder)
        #                 if os.path.isdir(os.path.join(Group.output_folder, f))]


        self._groups = []

        # Auto import all groups from the input folder
        for folder in os.listdir(Group.input_folder):
            self._groups.append(Group(folder))


        print('Found the following groups:', [group.name for group in self._groups])
        #print(f'No. cores found in first group: {str(self._groups[0].no_cores)}')

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