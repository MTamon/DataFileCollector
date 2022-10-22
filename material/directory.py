"""Directory instance for database collector"""

import os
from typing import List


class Condition:
    """Condition instance for database collector"""

    def __init__(self) -> None:
        self.only_terminal_file = False
        self.contain_literal = []
        self.contain_dirc = []
        self.extention = []

    def __call__(self, file_path: str, terminal: bool) -> bool:
        if self.only_terminal_file:
            if not terminal:
                return False

        if not self.contain_dirc == []:
            dircs = os.path.dirname(file_path).split("\\")
            for target_dirc in self.contain_dirc:
                if not target_dirc in dircs:
                    return False

        if not self.extention == []:
            ext = file_path.split(".")[-1]
            if not ext in self.extention:
                return False

        if not self.contain_literal == []:
            for literal in self.contain_literal:
                if not literal in file_path:
                    return False

        return True

    def only_terminal(self, set_status: bool = True):
        """set condition, get file path only terminal files"""
        self.only_terminal_file = set_status

    def add_contains_filename(self, literal: str):
        """set condition, get file path which include literal"""
        self.contain_literal.append(literal)

    def remove_contains_filename(self, literal: List[str]):
        """remove literal in registered literals"""
        new_list = []
        for c_l in self.contain_literal:
            if c_l in literal:
                continue
            new_list.append(c_l)
        self.contain_literal = new_list

    def add_contains_dirc(self, dirc_name: str):
        """set condition, get file path which include directory-name"""
        self.contain_dirc.append(dirc_name)

    def remove_contains_dirc(self, dirc_name: List[str]):
        """remove directory-name in registered literals"""
        new_list = []
        for c_l in self.contain_dirc:
            if c_l in dirc_name:
                continue
            new_list.append(c_l)
        self.contain_dirc = new_list

    def specify_extention(self, extention: str):
        """Specify the file extension."""
        self.extention.append(extention)

    def remove_extentions(self, extentions: List[str]):
        """remove extentions in registered extentions"""
        new_list = []
        for c_l in self.extention:
            if c_l in extentions:
                continue
            new_list.append(c_l)
        self.extention = new_list


class Directory:
    """This class is used to represent a directory in a database collector."""

    def __init__(self, name: str, path: str) -> None:

        self.name = name
        self.path = path
        self.own_path = os.path.join(path, name)

        list_member = os.listdir(self.own_path)
        dirc_member = []
        file_member = []
        for member in list_member:
            if os.path.isfile(os.path.join(self.own_path, member)):
                file_member.append(os.path.join(self.own_path, member))
            else:
                dirc_member.append(os.path.join(self.own_path, member))

        self.dirc_member = [
            Directory(dirc_name, self.own_path) for dirc_name in dirc_member
        ]
        self.file_member = file_member

        self.terminal = len(dirc_member) == 0

    def get_file_path(self, condition: Condition) -> list:
        """Get the path to the file matching the condition.

        Args:
            condition (Condition): The conditions of the file to be acquired are described.
        """
        file_list = []

        for file in self.file_member:
            if condition(file, self.terminal):
                file_list.append(file)

        for dirc in self.dirc_member:
            file_list.append(dirc.get_file_path(condition))

        return file_list
