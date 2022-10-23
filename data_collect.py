"""Database file path collector"""

import os

from material.directory import Condition, Directory


class Collector:
    """Database file path collector"""

    def __init__(self, condition: Condition, root_path: str, abspath: bool = False):
        if abspath:
            root_path = os.path.abspath(root_path)

        self.database = Directory(root_path).build_structure()
        self.condition = condition

    def get_path(self) -> list:
        """
        Get the path to the file matching the condition &
        The directory structure is returned intact.
        """

        return self.database.get_file_path(self.condition)

    @staticmethod
    def serialize_path_list(file_path_struct: list):
        """Serialize get_path() return value."""

        def flatten(list_struct: list):
            flatten_list = []
            for element in list_struct:
                if isinstance(element, (list, tuple)):
                    flatten_list += flatten(element)
                else:
                    flatten_list.append(element)

            return flatten_list

        serialized_list = flatten(file_path_struct)

        return serialized_list

    @staticmethod
    def group_dir_file(file_path_struct: list):
        """Grouping get_path() return value with same directory site."""

        def grouping(list_struct: list):
            group_list = []
            files = []
            for element in list_struct:
                if isinstance(element, (list, tuple)):
                    group_list += grouping(element)
                else:
                    files.append(element)

            if files != []:
                group_list = [files, *group_list]

            return group_list

        grouped_list = grouping(file_path_struct)

        return grouped_list

    def get_directory_instance(self) -> Directory:
        """Return Directory instance which useed this Collector"""
        return self.database

    def __str__(self):
        out_str = ""
        struct_path = self.get_path()

        for file_path in self.serialize_path_list(struct_path):
            out_str += f"collect path: {file_path}\n"

        return out_str


if __name__ == "__main__":
    # example1
    cond = Condition()
    cond.specify_extention("py")

    collector = Collector(cond, "./")
    results = collector.get_path()
    serialized_results = Collector.serialize_path_list(results)
    grouped_results = Collector.group_dir_file(results)

    for r in serialized_results:
        print(f"collect path: {r}")
    print()

    for r in grouped_results:
        print(f"group: {r}")
    print()

    # example2
    collector = Collector(cond, "./out/exp1")
    structures = collector.get_directory_instance()
    print(collector)

    os.mkdir("./out/exp1/ABCD")
    f = open("./out/exp1/ABCD/exit.py", "w")
    f.close()

    cloned = structures.clone()
    structures.update_member()

    os.remove("./out/exp1/ABCD/exit.py")
    os.rmdir("./out/exp1/ABCD")

    collector.database = cloned
    print(collector)

    collector.database = structures
    print(collector)

    print("incarnated:", cloned.incarnate("./out/out", cond, print))

    cloned.destruct()
