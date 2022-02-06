class JSHelpScripts:
    def openAccordian(self, accordianText: str, tagName: str='span') -> None:
        return ''.join(
            (
                f"let spanList = document.getElementsByTagName('{tagName}');",
                "let c = 0;", "for(let span of spanList){",
                f"if(span.innerText.startsWith('{accordianText}'))", "{",
                "if(c != 0){", "span.click();", "}c++;","}","}"
            )
        )

    def clickElementWithInnerTextS(
        self, tagName: str, innerText: str, toLowerCase: bool = True
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

    def clickFirstElementFromElementList(self, tagName: str) -> str:
        return f"""document.getElementsByTagName("{tagName}")[0].click();"""

    def clickElementStartingWithStrS(self, tagName: str, startingTxt: str) -> str:
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

    def clickFrmSecElementStartingWithStrS(self, tagName: str, startingTxt: str) -> str:
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

    def getXpathStrFrClsNames(self, tagName: str, *styleClassNames: str) -> str:
        returnStr = f"//{tagName}["
        repeatingStr = lambda s: f"contains(@class, '{s}')"
        numOfClasses = len(styleClassNames)
        c = 0
        while c < numOfClasses - 1:
            returnStr += repeatingStr(styleClassNames[c]) + " and "
            c += 1

        returnStr += f"{repeatingStr(styleClassNames[c])}]"
        return returnStr

    def convert2UglyJS(self, jsScript: str) -> str:
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
