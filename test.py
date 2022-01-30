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

''.join(regExpSplit(" |\n", js))