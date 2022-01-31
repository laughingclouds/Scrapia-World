from cmd import Cmd
from json import load
from os import system as systemCmd, listdir

import click

import scrapia_shell
from sw_utils import get_chapter_number_list, clrScrn


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




@cli.command()
@click.argument("novel_name", type=str)
def count_words(novel_name: str) -> None:
    """Returns the word count of all the files within a directory. Takes in a list of filenames."""
    word_count: int = 0
    with open("novel_page_info.json", "r") as fobj:
        novel_info_dict = load(fobj)["novel_page_info"][novel_name]
    BASE_PATH = novel_info_dict["NOVEL_PATH"]  # Base path for the novel

    for filename in listdir(BASE_PATH):
        with open(f"{BASE_PATH}/{filename}", "r") as file_object:
            chapter_content = file_object.read()
            word_count += len(chapter_content.split())

    click.echo(word_count)


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
@click.argument("novel_name", type=str)
def check(
    novel_name: str, latest_chapter: bool = False, list_all_chapters: bool = False
):
    """Check wether any chapters are missing."""

    # This open the json file to return the path of the novel `novel_name`. Open the json to know its structure.
    with open("novel_page_info.json", "r") as novel_page_info_fobj:
        novel_page_dict: dict[str, str] = load(novel_page_info_fobj)["novel_page_info"][
            novel_name
        ]
        chapter_list: list[str] = listdir(novel_page_dict["NOVEL_SAVE_PATH_BASE"])

    sorted_chapter_list: list[int] = get_chapter_number_list(chapter_list)

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
        click.echo(
            f"There seems to be a problem, please check if the following chapters exist:\n{possible_missing_chapters}"
        )

    if latest_chapter:
        click.echo(f"This is the latest chapter number: {sorted_chapter_list[-1]}")
    if list_all_chapters:
        click.echo(f"Here is the list of all the chapters:\n{sorted_chapter_list}")


@cli.command()
def cls():
    """clear screen"""
    clrScrn(click.clear)


@cli.command()
@click.option("-n", default=1, help="Number of greetings")
@click.argument("name")
def greet(n, name):
    """Greets you (`name`) `n` times"""
    for _ in range(n):
        click.echo(f"Hello {name}")


@cli.command()
@click.option(
    "-headless",
    default=1,
    help="Start in headless mode. Default value is 1. "
    + "Set to 0, to start in graphical mode.",
)
@click.argument("novel_name")
@click.pass_context
def shell(ctx, headless: int, novel_name: str):
    """Start a scraping session in a shell"""
    safe = "You are safe to go if you're in the terminal."
    warning = "Warning, invoking this within the shell will restart it."
    option = input(f"{warning} {safe}\nContinue? (y/n): ")
    if option == "y":
        OverrideDefault(headless, novel_name, ctx).cmdloop()
    else:
        return None


if __name__ == "__main__":
    cli()
