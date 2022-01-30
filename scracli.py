from cmd import Cmd
from json import load
from os import system as systemCmd, listdir
from tkinter import EXCEPTION

import click
from click._compat import WIN

import scrapia_shell


@click.group("scracli", invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Command line tool for working with downloaded content"""
    pass

class OverrideDefault(scrapia_shell.ScrapiaShell):
    """Overrides `default` function of `ScrapiaShell`"""
    # We will not define a __init__ because we want to use
    # the base classes' __init__

    def default(self, line: str):
        subcommand = cli.commands.get(line)
        if subcommand:
            self.ctx.invoke(subcommand)
        else:
            return Cmd.default(self, line)


def _get_chapter_number_list(chapter_list: list[str]) -> list[int]:
    """Returns a sorted (asc) list of all the chapter numbers in the file. We can later check and see whether
    all the chapters are present in ascending order and whether any chapter is missing or not."""

    def _get_number_from_string(string_: str) -> int:
        """A function to get a number from a string, for example, getting a chapter number from the chapter title."""
        number_as_str: str = ''
        was_prev_element_digit: bool = False
        for element in string_:
            if element.isdigit():
                number_as_str += element
                was_prev_element_digit = True
            elif not(element.isdigit()) and was_prev_element_digit:
                return int(number_as_str)
            else:
                continue
        return int(number_as_str)

    sorted_chapter_list: list[int] = [_get_number_from_string(chapter_title) for chapter_title in chapter_list]
    sorted_chapter_list.sort()
    return sorted_chapter_list

def _return_novel_info_dict(novel_name: str) -> dict[str, str]:
    """Returns a dictionary with info on `novel_name`. Refer to the json file to what info is given."""

    with open("novel_page_info.json", 'r') as novel_page_fobj:
        return load(novel_page_fobj)["novel_page_info"][novel_name]

def _return_chapter_list(path: str) -> list[str]:
    return listdir(path)

@cli.command()
@click.argument('novel_name', type=str)
def count_words(novel_name: str) -> None:
    """Returns the word count of all the files within a directory. Takes in a list of filenames."""
    word_count: int = 0
    novel_info_dict = _return_novel_info_dict(novel_name)
    BASE_PATH = novel_info_dict["NOVEL_SAVE_PATH_BASE"]  # Base path for the novel

    for filename in _return_chapter_list(BASE_PATH):
        with open(f"{BASE_PATH}/{filename}", 'r') as file_object:
            chapter_content = file_object.read()
            word_count += len(chapter_content.split())
    
    click.echo(word_count)


@cli.command()
@click.option("--latest-chapter", is_flag=True, flag_value=True,
    help="This will show the latest chapter number as well.")
@click.option("--list-all-chapters", is_flag=True, flag_value=True,
    help="This will return the list of all the chapters.")
@click.argument("novel_name", type=str)
def check(novel_name: str, latest_chapter: bool=False, list_all_chapters: bool=False):
    """Check wether any chapters are missing."""

    # This open the json file to return the path of the novel `novel_name`. Open the json to know its structure.
    with open("novel_page_info.json", 'r') as novel_page_info_fobj:
        novel_page_dict: dict[str, str] = load(novel_page_info_fobj)["novel_page_info"][novel_name]
        chapter_list: list[str] = listdir(novel_page_dict['NOVEL_SAVE_PATH_BASE'])

    sorted_chapter_list: list[int] = _get_chapter_number_list(chapter_list)

    n = len(sorted_chapter_list)

    flag: bool = False  # using this you can find more than one missing chapters
    possible_missing_chapters: list[str] = []
    for i in range(0, n - 1):
        if sorted_chapter_list[i + 1] != sorted_chapter_list[i] + 1:
            flag = True
            possible_missing_chapters.append(sorted_chapter_list[i] + 1)
    if not flag:
        click.echo("Everythings fine chap.")
    else:
        click.echo(f"There seems to be a problem, please check if the following chapters exist:\n{possible_missing_chapters}")

    if latest_chapter:
        click.echo(f"This is the latest chapter number: {sorted_chapter_list[-1]}")
    if list_all_chapters:
        click.echo(f"Here is the list of all the chapters:\n{sorted_chapter_list}")


@cli.command()
def cls():
    """clear screen"""
    try: 
        if WIN:
            systemCmd("cls")
        else:
            systemCmd("clear")
    except EXCEPTION:
        click.clear()



@cli.command()
@click.option("-n", default=1, help="Number of greetings")
@click.argument("name")
def greet(n, name):
    """Greets you (`name`) `n` times"""
    for _ in range(n):
        click.echo(f"Hello {name}")

@cli.command()
@click.argument("novel_name")
@click.pass_context
def shell(ctx, novel_name: str):
    """Start a scraping session in a shell"""
    safe: str = "You are safe to go if you're in the terminal."
    option = input(f"Warning, invoking this within the shell will restart it.{safe}\nContinue? (y/n): ")
    if option == 'y':
        OverrideDefault(novel_name, ctx).cmdloop()
    else:
        return None

if __name__ == "__main__":
    cli()
