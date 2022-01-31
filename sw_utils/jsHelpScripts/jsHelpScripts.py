def clickElementWithInnerTextS(
    tagName: str, innerText: str, toLowerCase: bool = True
) -> str:
    """Script to click an element which has innertext `S`"""

    def appendLowerCase(originalStr: str) -> str:
        if toLowerCase:
            originalStr += ".toLowerCase()"
        return originalStr

    return "".join(
        (
            "let elementList=document",
            f""".getElementsByTagName("{tagName}");""",
            "for(let element of elementList){",
            appendLowerCase("if(element.innerText"),
            f"""=="{innerText}")""",
            "{",
            "element.click();",
            "}",
            "}",
        )
    )


def clickFirstElementFromElementList(tagName: str) -> str:
    return f"""document.getElementsByTagName("{tagName}")[0].click();"""


def clickElementStartingWithStrS(tagName: str, startingTxt: str) -> str:
    return "".join(
        (
            "let elementList=document",
            f""".getElementsByTagName("{tagName}");""",
            "for(let element of elementList){",
            f"""if(element.innerText.startsWith("{startingTxt}"))""",
            "{element.click();}",
            "}",
        )
    )


def clickFrmSecElementStartingWithStrS(tagName: str, startingTxt: str) -> str:
    return "".join(
        (
            "let elementList=document",
            f""".getElementsByTagName("{tagName}");""",
            "for(let element of elementList){",
            f"""if(element.innerText.startsWith("{startingTxt}"))""",
            "{",
            "if(element)",
            "element.click();}",
            "}",
        )
    )


def convert2UglyJS(jsScript: str) -> str:
    """Convert a proper javascript script into an ugly script with no spaces"""
    symbols = jsScript.replace("\n", " ").split(" ")
    symbols = [symbol for symbol in symbols if symbol not in (" ", "")]

    js = ""
    n = len(symbols) - 1
    for i in range(0, n):
        currSymbol = symbols[i]
        nextSymbol = symbols[i + 1]
        if (not currSymbol[-1].isalpha()) or (not nextSymbol.isalpha()):
            js += currSymbol + nextSymbol
        else:
            js += f"{currSymbol} {nextSymbol}"
    return js
