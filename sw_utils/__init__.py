from types import FunctionType
from click._compat import WIN
from os import system as systemCmd

from .termcolor import colored
from .novelProfiler import NovelProfiler, jsHelpScripts


def clrScrn(clearFuncClick: FunctionType):
    """clear screen\n
    Input is click.clear()\n
    Or any function that clears the screen"""
    try:
        if WIN:
            systemCmd("cls")
        else:
            systemCmd("clear")
    except Exception as e:
        clearFuncClick()


def get_chapter_number_list(chapter_list: list[str]) -> list[int]:
    """Returns a sorted (asc) list of all the chapter numbers in the file. We can later check and see whether
    all the chapters are present in ascending order and whether any chapter is missing or not."""

    def get_number_from_string(string_: str) -> int:
        """A function to get a number from a string, for example, getting a chapter number from the chapter title."""
        number_as_str: str = ""
        was_prev_element_digit: bool = False
        for element in string_:
            if element.isdigit():
                number_as_str += element
                was_prev_element_digit = True
            elif not (element.isdigit()) and was_prev_element_digit:
                return int(number_as_str)
            else:
                continue
        return int(number_as_str)

    sorted_chapter_list: list[int] = [
        get_number_from_string(chapter_title) for chapter_title in chapter_list
    ]
    sorted_chapter_list.sort()
    return sorted_chapter_list
