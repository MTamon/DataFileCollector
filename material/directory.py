"""Directory instance for database collector"""

from __future__ import annotations

import os
import subprocess
import shutil
from typing import Any, Callable, List


class Condition:
    """Condition instance for database collector"""

    def __init__(self) -> None:
        self.only_terminal_file = False
        self.contain_literal = []
        self.contain_dirc = []
        self.extention = []
        self.condition_func = []

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

        if not self.condition_func == []:
            for condition in self.condition_func:
                if not condition(file_path):
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

    def add_condition_func(self, condition: Callable[[str], bool]):
        """
        add original condition. 'condition' must be Callable &
        must have argment 'path'(str) & must return 'result'(bool).
        """
        self.condition_func.append(condition)


class Directory:
    """This class is used to represent a directory in a database collector."""

    def __init__(self, path: str, empty: bool = False) -> None:
        path = "\\".join(path.split("/"))
        name = path.split("\\")[-1]
        if path == ".\\":
            name = os.path.abspath(path).split("\\")[-1]
            path = os.path.join("..", name)

        self.name = name
        self.path = path

        self.empty = empty

        self.file_member = []
        self.dirc_member = []
        self.terminal = True

    def build_structure(self):
        """Generate & build directory structure"""

        self.update_member(self.empty)

        return self

    def get_file_path(self, condition: Condition) -> list:
        """Get the path to the file matching the condition.

        Args:
        -----
            condition (Condition): The conditions of the file to be acquired are described.
        """
        file_list = []

        for file in self.file_member:
            if condition(file, self.terminal):
                file_list.append(file)

        for dirc in self.dirc_member:
            file_list.append(dirc.get_file_path(condition))

        return file_list

    def clone(self, condition: Condition = None) -> Directory:
        """copy Directory structure (option: with condition)"""

        clone = Directory(self.path, self.empty)

        clone.file_member = self.file_member.copy()
        clone.dirc_member = [
            directory.clone(condition) for directory in self.dirc_member
        ]
        clone.terminal = self.terminal

        if condition is None:
            return clone

        new_list = []
        for file in clone.file_member:
            if condition(file, clone.terminal):
                new_list.append(file)
        clone.file_member = new_list

        return clone

    def incarnate(
        self,
        path: str,
        condition: Condition = None,
        printer: Callable[[str], Any] = None,
    ) -> int:
        """
        Incarnating instance as an actual directory.

        If a Condition is specified, the corresponding file will also be copied.

        Returns
        -------
        (int): number of made directory
        """

        path = "\\".join(path.split("/"))

        mk_number = 0

        mk_path = os.path.join(path, self.name)
        if not os.path.isdir(mk_path):
            os.mkdir(mk_path)
            mk_number += 1
        if condition is not None:
            self.copy_file(mk_path, condition, printer)

        for dirc in self.dirc_member:
            mk_number += dirc.incarnate(mk_path, condition, printer)

        return mk_number

    def hollow(self) -> Directory:
        """clone instance & remove its file member"""

        target = self.clone()
        target.file_member = []
        for children in target.dirc_member:
            children.hollow()

        return target

    def update_member(self, empty: bool = False):
        """update directory member"""

        list_member = os.listdir(self.path)
        dirc_member = []
        file_member = []
        for member in list_member:
            if os.path.isfile(os.path.join(self.path, member)):
                file_member.append(os.path.join(self.path, member))
            else:
                dirc_member.append(member)

        self.destruct()

        self.dirc_member = [
            Directory(os.path.join(self.path, dirc_name), empty)
            for dirc_name in dirc_member
        ]
        self.file_member = file_member

        self.terminal = len(dirc_member) == 0
        for dirc in self.dirc_member:
            dirc.update_member(empty)

        if empty:
            self.file_member = []

    def destruct(self) -> None:
        """Destruct members"""

        if self.terminal:
            return

        for dirc_obj in self.dirc_member:
            dirc_obj.destruct()
            del dirc_obj

        return

    def copy_file(
        self,
        path: str,
        condition: Condition = None,
        printer: Callable[[str], Any] = None,
    ):
        """copy member files to path (option: with conditon)"""

        path = "/".join(path.split("\\"))

        for file in self.file_member:
            file_path = "/".join(file.split("\\"))
            file_name = os.path.basename(file_path)
            target_path = "/".join([path, file_name])

            if condition(file, self.terminal):
                shutil.copyfile(file_path, target_path)
                printer(f"copy: {file_path} -> {target_path}")
                # com = f"cp {file_path} {path}".split(" ")
                # try:
                #     subprocess.run(com, check=True)
                # except subprocess.CalledProcessError:
                #     if printer is not None:
                #         printer(
                #             f"command: '{' '.join(com)}' is faild! -> called process error"
                #         )
                # else:
                #     if printer is not None:
                #         printer(f"command: '{' '.join(com)}' is success!")
