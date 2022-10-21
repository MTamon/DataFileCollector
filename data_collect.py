"""Database file path collector"""

import os

from material.directory import Condition, Directory


class Collector:
    """Database file path collector"""

    def __init__(self, condition: Condition, root_path: str):
        root_path = os.path.abspath(root_path)

        split_path = root_path.split("\\")
        last_dirc_name = split_path[-1]
        dirc_path = "\\".join(split_path[:-1])

        self.database = Directory(last_dirc_name, dirc_path)
        self.condition = condition

    def get_path(self) -> list:
        """
        Get the path to the file matching the condition &
        The directory structure is returned intact.
        """

        return self.database.get_file_path(self.condition)

    def serialize_path_list(self, file_path_struct: list):
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


if __name__ == "__main__":
    cond = Condition()
    cond.specify_extention("py")

    collector = Collector(cond, "./")
    results = collector.get_path()
    results = collector.serialize_path_list(results)

    for r in results:
        print(f"collect path: {r}")
