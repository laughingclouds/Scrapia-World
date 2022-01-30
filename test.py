"""TODO: Unimportant, delete later"""
from re import split as regExpSplit

js = """document.getElementsByTagName("button")[0].click();
                let btnList = document.getElementsByTagName("button");

                for (let btn of btnlist) {
                if (btn.innerText.toLowerCase() == "log in") {
                    btn.click();
                    }
                }
            """

"".join(regExpSplit(" |\n", js))


def do_getChapterNumberFrmURL(
    url: str, return_as_is: bool = False, *args
) -> int | None:
    # This returns only the relevant part (the part with the chapter no)
    url = list(
        reversed(
            url.removeprefix("https://www.wuxiaworld.com/novel/")
            .rstrip("/")
            .replace("-", " ")
            .split(" ")
        )
    )
    number_as_str: str = ""
    for element in url:
        if element.isdecimal():
            number_as_str = element
            break
    if return_as_is:
        return number_as_str
    else:
        return int(number_as_str)


if __name__ == "__main__":
    print(do_getChapterNumberFrmURL("https://www.wuxiaworld.com/novel/against-the-gods/atg-chapter-1926", return_as_is=True))
