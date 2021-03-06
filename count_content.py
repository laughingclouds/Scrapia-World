from os import listdir
from pathlib import Path

import click

from sw_utils import get_chapter_number_list, clrScrn


@click.group()
def cli():
    """A command line utility to work with text in a file."""
    pass


BASE_DIR = (
    Path(__file__).resolve().parent
)  # BASE_DIR is the directory in which this python script lies
present_directory_filename_list = listdir()

NOVEL_FILE_NAME = ""
# This is here because we assume this file to be in the same folder as the
# novel folder
for filename in present_directory_filename_list:
    if not filename.endswith(".py"):
        NOVEL_FILE_NAME = filename

child_directory_filename_list = listdir(f"{BASE_DIR}/{NOVEL_FILE_NAME}/")


def count_words(fileNames: list[str], novelPath: str) -> int:
    """
    Return word count of all the files within a directory

    NOTE input is list of filenames(str)"""
    word_count: int = 0
    for filename in fileNames:
        with open(f"{novelPath}/{filename}", "r") as file_object:
            chapter_content = file_object.read()
            word_count += len(chapter_content.split())

    return word_count


@cli.command()
@click.option(
    "--latest-chapter",
    is_flag=True,
    flag_value=True,
    help="This will show the latest chapter number as well.",
)
@click.option(
    "--list-all-chapters",
    is_flag=True,
    flag_value=True,
    help="This will return the list of all the chapters.",
)
def check(latest_chapter: bool = False, list_all_chapters: bool = False):
    """Check wether any chapters are missing."""

    chapter_number_list: list[int] = get_chapter_number_list(
        child_directory_filename_list
    )

    n = len(chapter_number_list)

    flag: bool = False
    possible_missing_chapters: list[str] = []
    for i in range(0, n - 1):
        if chapter_number_list[i + 1] != chapter_number_list[i] + 1:
            flag = True
            possible_missing_chapters.append(chapter_number_list[i] + 1)
    if not flag:
        click.echo("Everythings fine chap.")
    else:
        click.echo(
            f"There seems to be a problem, please check if the following chapters exist:\n{possible_missing_chapters}"
        )

    if latest_chapter:
        click.echo(f"This is the latest chapter number: {chapter_number_list[-1]}")
    if list_all_chapters:
        click.echo(f"Here is the list of all the chapters:\n{chapter_number_list}")


@cli.command()
def cls():
    """clear screen"""
    clrScrn(click.clear)


if __name__ == "__main__":
    cli()
