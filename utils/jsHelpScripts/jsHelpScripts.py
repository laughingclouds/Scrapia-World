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
