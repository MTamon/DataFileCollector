"""Directory instance for database collector"""

from __future__ import annotations

import os
import re
import shutil
from typing import Any, Callable, List, Iterable


class Condition:
    """Condition instance for database collector"""

    def __init__(self) -> None:
        self.only_terminal_file = False
        self.contain_literal = []
        self.exclude_literal = []
        self.contain_dirc = []
        self.exclude_dirc = []
        self.extention = []
        self.condition_func = []

    def __call__(self, file_path: str) -> bool:
        file_path = os.sep.join(re.split(r"[\\/]", file_path))

        if self.only_terminal_file:
            dirs_path = os.path.dirname(file_path)
            mems = os.listdir(dirs_path)
            for mem in mems:
                if os.path.isdir(os.path.join(dirs_path, mem)):
                    return False

        if self.contain_dirc != []:
            dircs = os.path.dirname(file_path).split(os.sep)
            exist = False
            for target_dirc in self.contain_dirc:
                if target_dirc in dircs:
                    exist = True
                    break
            if not exist:
                return False

        if self.exclude_dirc != []:
            dircs = os.path.dirname(file_path).split(os.sep)
            for target_dirc in self.exclude_dirc:
                if target_dirc in dircs:
                    return False

        if self.extention != []:
            ext = os.path.basename(file_path).split(".")[-1]
            if not ext in self.extention:
                return False

        if self.contain_literal != []:
            exist = False
            for literal in self.contain_literal:
                if literal in os.path.basename(file_path):
                    exist = True
                    break
            if not exist:
                return False

        if self.exclude_literal != []:
            for literal in self.exclude_literal:
                if literal in os.path.basename(file_path):
                    return False

        if self.condition_func != []:
            for condition in self.condition_func:
                if not condition(file_path):
                    return False

        return True

    def only_terminal(self, set_status: bool = True) -> Condition:
        """set condition, get file path only terminal files"""
        self.only_terminal_file = set_status

        return self

    def add_contain_filename(self, literal: List[str]) -> Condition:
        """set condition, get file path which include literal"""
        self.contain_literal += literal

        return self

    def add_exclude_filename(self, literal: List[str]) -> Condition:
        """set condition, get file path which exclude literal"""
        self.exclude_literal += literal

        return self

    def remove_contain_filename(self, literal: List[str]) -> Condition:
        """remove literal in registered literals"""
        new_list = []
        for c_l in self.contain_literal:
            if c_l in literal:
                continue
            new_list.append(c_l)
        self.contain_literal = new_list

        return self

    def remove_exclude_filename(self, literal: List[str]) -> Condition:
        """remove literal in registered literals for excluding"""
        new_list = []
        for c_l in self.exclude_literal:
            if c_l in literal:
                continue
            new_list.append(c_l)
        self.exclude_literal = new_list

        return self

    def add_contain_dirc(self, dirc_name: List[str]) -> Condition:
        """set condition, get file path which include 'dirc_name'"""
        self.contain_dirc += dirc_name

        return self

    def add_exclude_dirc(self, dirc_name: List[str]) -> Condition:
        """set condition, get file path which exclude 'dirc_name'"""
        self.exclude_dirc += dirc_name

        return self

    def remove_contain_dirc(self, dirc_name: List[str]) -> Condition:
        """remove directory-name in registered literals"""
        new_list = []
        for c_l in self.contain_dirc:
            if c_l in dirc_name:
                continue
            new_list.append(c_l)
        self.contain_dirc = new_list

        return self

    def remove_exclude_dirc(self, dirc_name: List[str]) -> Condition:
        """remove excluded directory-name in registered literals"""
        new_list = []
        for c_l in self.exclude_dirc:
            if c_l in dirc_name:
                continue
            new_list.append(c_l)
        self.exclude_dirc = new_list

        return self

    def specify_extention(self, extention: List[str]) -> Condition:
        """Specify the file extension."""
        self.extention += extention

        return self

    def remove_extentions(self, extentions: List[str]) -> Condition:
        """remove extentions in registered extentions"""
        new_list = []
        for c_l in self.extention:
            if c_l in extentions:
                continue
            new_list.append(c_l)
        self.extention = new_list

        return self

    def add_condition_func(self, condition: Callable[[str], bool]) -> Condition:
        """
        add original condition. 'condition' must be Callable &
        must have argment 'path'(str) & must return 'result'(bool).
        """
        self.condition_func.append(condition)

        return self

    def reset_condition_func(self) -> Condition:
        """reset original conditions"""
        self.condition_func = []

        return self


class Directory:
    """This class is used to represent a directory in a database collector."""

    def __init__(self, path: str, empty: bool = False) -> None:
        if path == "":
            raise ValueError(
                "'path' must not be empty. If you wont to set current directory, set './'."
            )

        path = os.sep.join(re.split(r"[\\|/]", path))
        name = path.split(os.sep)[-1]
        if path == f".{os.sep}":
            name = os.path.abspath(path).split(os.sep)[-1]
            path = os.path.join("..", name)

        self.name = name
        self.path = path
        self.abspath = os.path.abspath(path)

        self.empty = empty

        self.file_member = []
        self.dirc_member = []
        self.terminal = True

    def __str__(self) -> str:
        return self.path

    def __eq__(self, __o: str) -> bool:
        if not isinstance(__o, str):
            raise NotImplementedError()
        else:
            return __o == self.name

    def __call__(self, path: str) -> Directory:
        """Search the members of the hierarchy below this instance itself"""
        path_route = re.split(r"[\\|/]", path)
        if path_route[0] == ".":
            path_route = path_route[1:]

        if len(path_route) == 1:
            if path_route[0] == "":
                return self
            if path_route[0] in self.file_member:
                return self
            for dirc in self.dirc_member:
                if path_route[0] == dirc:
                    return dirc
            return None
        else:
            for dirc in self.dirc_member:
                if path_route[0] == dirc:
                    return dirc("/".join(path_route[1:]))
            return None

    def build_structure(self):
        """Generate & build directory structure"""

        self.update_member(self.empty)

        return self

    def get_file_path(
        self, conditions: List[Condition], serialize: bool = False
    ) -> list:
        """Get the path to the file matching the condition.

        Args:
        -----
            condition (Condition): The conditions of the file to be acquired are described.
            serialize (bool): Specifies how the directory list is returned.
        """
        file_list = []

        if isinstance(conditions, dict):
            conditions = [conditions[k] for k in conditions]
        if not isinstance(conditions, Iterable):
            conditions = [conditions]

        for file in self.file_member:
            if sum([condition(file) for condition in conditions]) != 0:
                out_form_path = "/".join(file.split(os.sep))
                file_list.append(out_form_path)

        for dirc in self.dirc_member:
            if serialize:
                file_list += dirc.get_file_path(conditions, serialize=serialize)
            else:
                file_list.append(dirc.get_file_path(conditions, serialize=serialize))

        return file_list

    def get_grouped_path_list(self, key: Callable[[str], str]) -> List[List[str]]:
        """Get grouped file path list with 'key'.

        Args:
            key (str): keyword for groping.

        Returns:
            List[List[str]]: grouped path list.
        """

        grouped = {}

        for mem in self.file_member:
            name = os.path.basename(mem)

            group = key(name)
            if not group in grouped:
                grouped[group] = [mem]
            else:
                grouped[group].append(mem)

        _result = []
        for _, path_list in grouped.items():
            _result.append(path_list)

        return _result

    def get_terminal_instances(self, serialize: bool = False) -> List[Directory]:
        """Get the terminal Directory instance list while preserving file structure
        or Get the terminal Directory instance serialized list.

        Args:
        -----
            serialize (bool): Specifies how the directory list is returned.
        """
        return self.get_all_instances(serialize=serialize, terminal_only=True)

    def get_all_instances(
        self, serialize: bool = False, terminal_only: bool = False
    ) -> list:
        """Get the Directory instance list while preserving file structure
        or Get Directory instance serialized list.
        """
        dir_list = []

        if self.terminal:
            return [self]

        for dirc in self.dirc_member:
            dir_list += dirc.get_all_instances(
                serialize=serialize, terminal_only=terminal_only
            )

        if not terminal_only:
            if serialize:
                dir_list = [self] + dir_list
            else:
                dir_list = [self, dir_list]

        if serialize or not terminal_only:
            return dir_list
        elif terminal_only:
            return [dir_list]

    def get_abspath(self) -> str:
        """get absolute path which is sep by '/'"""
        return "/".join(self.abspath.split(os.sep))

    def clone(self, conditions: List[Condition] = None) -> Directory:
        """copy Directory structure (option: with condition)"""

        clone = Directory(self.path, self.empty)

        if isinstance(conditions, dict):
            conditions = [conditions[k] for k in conditions]
        if not isinstance(conditions, Iterable):
            conditions = [conditions]

        clone.file_member = self.file_member.copy()
        clone.dirc_member = [
            directory.clone(conditions) for directory in self.dirc_member
        ]
        clone.terminal = self.terminal

        if conditions == [None]:
            return clone

        new_list = []
        for file in clone.file_member:
            if sum([condition(file) for condition in conditions]) != 0:
                new_list.append(file)
        clone.file_member = new_list

        return clone

    def incarnate(
        self,
        path: str,
        conditions: List[Condition] = None,
        printer: Callable[[str], Any] = None,
    ) -> int:
        """
        Incarnating instance as an actual directory.

        If a Condition is specified, the corresponding file will also be copied.

        Returns
        -------
        (int): number of made directory
        """

        path = os.sep.join(path.split("/"))

        if isinstance(conditions, dict):
            conditions = [conditions[k] for k in conditions]
        if not isinstance(conditions, Iterable):
            conditions = [conditions]

        mk_number = 0

        mk_path = os.path.join(path, self.name)
        if sum([condition(mk_path) for condition in conditions]) != 0:
            return 0
        if not os.path.isdir(mk_path):
            os.mkdir(mk_path)
            mk_number += 1
        if conditions is not None:
            self.copy_file(mk_path, conditions, printer)

        for dirc in self.dirc_member:
            mk_number += dirc.incarnate(mk_path, conditions, printer)

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
        conditions: List[Condition] = None,
        printer: Callable[[str], Any] = None,
        override: bool = False,
    ):
        """copy member files to path (option: with conditon)"""

        path = os.sep.join(path.split("/"))

        if isinstance(conditions, dict):
            conditions = [conditions[k] for k in conditions]
        if not isinstance(conditions, Iterable):
            conditions = [conditions]

        for file in self.file_member:
            file_path = "/".join(file.split(os.sep))
            file_name = os.path.basename(file_path)
            target_path = "/".join([path, file_name])

            if sum([condition(file) for condition in conditions]) != 0:
                if not os.path.isfile(target_path) or override:
                    shutil.copyfile(file_path, target_path)
                    if os.path.isfile(target_path) and override:
                        printer(f"ovrd: {file_path} -> {target_path}")
                    else:
                        printer(f"copy: {file_path} -> {target_path}")
                else:
                    printer(f"exst: {file_path} -> {target_path}")
