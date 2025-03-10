"""
This module provides functionality to display the directory structure of a project.

The main feature of this module is the ability to generate a visual representation
of the directory tree, which can be filtered based on specific criteria such as
excluding hidden files or only including Python files.

Classes:
    DisplayablePath: Represents a path in the directory tree and provides methods
    to generate a displayable version of the path.

Functions:
    is_not_hidden: Checks if a path is not hidden.
    is_not_dunder: Checks if a path is not a dunder (double underscore) file.
    is_not_excluded: Checks if a path is not in the list of excluded folders.
    my_criteria: Combines multiple criteria to filter paths.
    my_py_criteria: Filters paths to only include Python files and directories.

Commands:
    main: Typer command to generate and optionally save the directory tree.

Usage:
    Run this module as a script to generate the directory tree.
    Example:
        python project_tree.py --only-py --write-file
"""

# External imports
from pathlib import Path
from typing import Any, Generator

import typer
from loguru import logger

app = typer.Typer()


class DisplayablePath(object):
    """
    Represents a path in the directory tree.

    This class provides methods to generate a displayable version of the path,
    including options for displaying the path as part of a tree structure.
    """

    display_filename_prefix_middle = "├──"
    display_filename_prefix_last = "└──"
    display_parent_prefix_middle = "    "
    display_parent_prefix_last = "│   "

    def __init__(self, path: Path, parent_path: Any, is_last: bool) -> None:
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @classmethod
    def make_tree(
        cls, root: Path, parent: Any = None, is_last: bool = False, criteria: Any = None
    ) -> Generator["DisplayablePath", None, None]:
        """
        Generate a displayable tree structure starting from the root path.

        Args:
            root: The root directory to start the tree from.
            parent: The parent path in the tree.
            is_last: Boolean indicating if this is the last child in the directory.
            criteria: A function to filter which paths are included in the tree.

        Yields:
            DisplayablePath: An instance representing a path in the tree.
        """
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(
            [path for path in root.iterdir() if criteria(path)],
            key=lambda s: str(s).lower(),
        )
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(
                    path, parent=displayable_root, is_last=is_last, criteria=criteria
                )
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path: Path) -> bool:
        """
        Default criteria for including paths in the tree.

        Args:
            path: The path to check.

        Returns:
            bool: True if the path should be included, False otherwise.
        """
        return True

    @property
    def displayname(self) -> str:
        """
        Get the display name for the path.

        Returns:
            str: The display name, with a trailing slash for directories.
        """
        if self.path.is_dir():
            return self.path.name + "/"
        return self.path.name

    def displayable(self) -> str:
        """
        Get the displayable string for the path, including tree structure.

        Returns:
            str: The displayable string representing the path in the tree.
        """
        if self.parent is None:
            return self.displayname

        _filename_prefix = (
            self.display_filename_prefix_last
            if self.is_last
            else self.display_filename_prefix_middle
        )

        parts = ["{!s} {!s}".format(_filename_prefix, self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(
                self.display_parent_prefix_middle
                if parent.is_last
                else self.display_parent_prefix_last
            )
            parent = parent.parent

        return "".join(reversed(parts))


def is_not_hidden(this_path: Path) -> bool:
    """
    Check if a path is not hidden.

    Args:
        this_path: The path to check.

    Returns:
        bool: True if the path is not hidden, False otherwise.
    """
    return not this_path.name.startswith(".")


def is_not_dunder(this_path: Path) -> bool:
    """
    Check if a path is not a dunder (double underscore) file.

    Args:
        this_path: The path to check.

    Returns:
        bool: True if the path is not a dunder file, False otherwise.
    """
    if this_path.name == "__init__.py":
        return True  # Exception
    return not this_path.name.startswith("__")


def is_not_excluded(this_path: Path) -> bool:
    """
    Check if a path is not in the list of excluded folders.

    Args:
        this_path: The path to check.

    Returns:
        bool: True if the path is not excluded, False otherwise.
    """
    excluded_folders = ["venv", "old"]
    return this_path.name not in excluded_folders


def my_criteria(this_path: Path) -> bool:
    """
    Combine multiple criteria to filter paths.

    Args:
        this_path: The path to check.

    Returns:
        bool: True if the path meets all criteria, False otherwise.
    """
    is_not_hidden_ = is_not_hidden(this_path)
    is_not_excluded_ = is_not_excluded(this_path)
    is_not_dunder_ = is_not_dunder(this_path)
    return is_not_hidden_ and is_not_excluded_ and is_not_dunder_


def my_py_criteria(this_path: Path) -> bool:
    """
    Filter paths to only include Python files and directories.

    Args:
        this_path: The path to check.

    Returns:
        bool: True if the path is a Python file or directory, False otherwise.
    """
    if not my_criteria(this_path):
        return False
    if this_path.is_file():
        return this_path.suffix.lower() == ".py"
    return True


@app.command()
def main(
    path_file: str = typer.Argument("", help="The root path to generate the tree from."),
    only_py: bool = typer.Option(False, help="Include only Python files."),
    write_file: bool = typer.Option(True, help="Write the tree to a file."),
) -> str:
    """
    Generate and optionally save the directory tree structure.

    Args:
        path_file: The root path to generate the tree from.
        only_py: Boolean indicating if only Python files should be included.
        write_file: Boolean indicating if the tree should be saved to a file.

    Returns:
        str: The full path of the generated directory tree.
    """
    import os
    from datetime import datetime

    exec_time = datetime.today().strftime("%Y-%m-%d %H:%M")
    if not path_file:
        cpath = Path(__file__).parent.parent.parent
    else:
        cpath = Path(path_file)

    file_path = os.path.join(cpath, "project_structure.txt")
    criteria_function = my_py_criteria if only_py else my_criteria
    paths = DisplayablePath.make_tree(Path(cpath), criteria=criteria_function)

    # Build the output in memory
    lines = [
        "Created by Analitika: contact@analitika.fr",
        f"Folder PATH listing as of {exec_time}",
        "Created with tools.project_tree.DisplayablePath",
        "",
    ]
    for path_ in paths:
        lines.append(path_.displayable())

    fullpath = "\n".join(lines)

    # Write to file only if required
    if write_file:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(fullpath)
        logger.info("Printed Tree Structure in ./project_structure.txt...")

    logger.success(f"Processing project structure complete:\n{fullpath}")
    return fullpath


if __name__ == "__main__":
    # python .\src\utils\project_tree.py --only-py --write-file
    app()
