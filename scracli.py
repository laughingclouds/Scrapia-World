from cmd import Cmd
from json import load
from os import system as systemCmd, listdir

import click

from scrapia_shell import ScrapiaShell
from sw_utils import get_chapter_number_list, clrScrn


@click.group("scracli", invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Command line tool for working with downloaded content"""
    pass


class OverrideDefault(ScrapiaShell):
    """Overrides `default` function of `ScrapiaShell`"""

    def __init__(self, isHeadless, novelName, ctx: click.Context):
        self.ctx = ctx
        ScrapiaShell.__init__(self, isHeadless, novelName, ctx)

    def default(self, line: str):
        subcommand = cli.commands.get(line)
        if subcommand:
            self.ctx.invoke(subcommand)
        else:
            return Cmd.default(self, line)


@cli.command()
@click.argument("novel_name", type=str)
def count_words(novel_name: str) -> None:
    """
    Returns the word count of all the files within a directory.
    """
    word_count: int = 0
    with open("novel_page_info.json", "r") as fobj:
        novel_info_dict = load(fobj)["novel_page_info"][novel_name]
    NOVEL_PATH = novel_info_dict["NOVEL_PATH"]  # Base path for the novel

    for filename in listdir(NOVEL_PATH):
        with open(f"{NOVEL_PATH}/{filename}", "r") as file_object:
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
def check(novelName: str, latestChapter: bool = False, listAllChapters: bool = False):
    """Check wether any chapters are missing."""

    # This open the json file to return the path of the novel `novel_name`.
    # Open the json to know its structure.
    with open("novel_page_info.json", "r") as fobj:
        novelPageDict: dict[str, str] = load(fobj)["novel_page_info"][novelName]
        chapterList: list[str] = listdir(novelPageDict["NOVEL_PATH"])

    sortedChapterList: list[int] = get_chapter_number_list(chapterList)

    n = len(sortedChapterList)

    # find more than one missing chapters using this
    flag: bool = False
    possible_missing_chapters: list[str] = []
    for i in range(0, n - 1):
        if sortedChapterList[i + 1] != sortedChapterList[i] + 1:
            flag = True
            possible_missing_chapters.append(sortedChapterList[i] + 1)
    if not flag:
        click.echo("Everythings fine chap.")
    else:
        click.echo(
            "".join(
                (
                    "There seems to be a problem, please ",
                    "check if the following chapters exist:\n",
                    f"{possible_missing_chapters}",
                )
            )
        )

    if latestChapter:
        click.echo(f"Latest chapter number: {sortedChapterList[-1]}")
    if listAllChapters:
        click.echo(f"List of all chapters:\n{sortedChapterList}")


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
    "--headless",
    default=1,
    help="Start in headless mode. Default value is 1. "
    + "Set to 0, to start in graphical mode.",
)
@click.argument("novel_name")
@click.pass_context
def shell(ctx: click.Context, headless: int, novel_name: str):
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
