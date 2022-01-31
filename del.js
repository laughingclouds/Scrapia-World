let elementList = document.getElementsByTagName("span");
let isFirstMatch = true;
for (let element of elementList) {
    if (element.innerText.startsWith("Volume")) {
        if (isFirstMatch) {
            isFirstMatch = false;
            continue;
        } else {
            element.click()
        }
    }
}

function getElementByXpath(path) {
    return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
}

var xpathResult = document.evaluate( xpathExpression, contextNode, namespaceResolver, resultType, result );