from io import FileIO
from json import dump, load, JSONDecodeError
from os import makedirs, listdir

from click import echo


def loadSafely(fp: FileIO) -> dict:
    try:    
        return load(fp)
    except JSONDecodeError:
        # file is probably completely empty
        # return non-empty to avoid index error
        return {0: ""}


def createJsonRetFileIO(fileName: str) -> FileIO:
    """
    1) create a file in 'w' mode
    2) return fileobj to that file in 'r+' mode
    """
    open(fileName, "w").close()
    return open(fileName, "r+")


class File_Directory_JSON_Worker:
    def __init__(self, novelPath: str, novelName: str, msg: tuple[str]) -> None:
        echo(msg[2])

        self.novelName = novelName
        self.novelPath = f"{novelPath}/{novelName}"
        self.novelPrfPath = f"{novelPath}/profile"

        self.retFilePath = lambda s: f"{self.novelPrfPath}/{novelName}_{s}.json"

        # <>_read.json & <>_toRead.json
        # return self.readFiles(*self.checkIfFilesExist())

    def createDirectoriesReturnTrueIfExists(self) -> bool:
        """create `self.novelPath`/profile/
        \nreturn True if FileExistsError raised,\nelse False"""
        try:
            makedirs(self.novelPrfPath)
            # if they don't exist, it should be safe to simply create the
            # required files
            return False
        except FileExistsError:
            # since the files already exist, the next step you should do
            # should be to read them
            return True

    def checkIfFilesExist(self) -> tuple[tuple[bool, str, FileIO | None]]:
        """Check for existence of
        <self.novelName>_read.json and <self.novelName>_toRead.json
        \nCreate them if they don't exist"""
        result = listdir(self.novelPrfPath)
        fileNameTuple = (self.retFilePath("read"), self.retFilePath("toRead"))
        fileExistanceList = [False, False]
        for fileName in result:
            if fileName == fileNameTuple[0]:
                fileExistanceList[0] = True
            elif fileName == fileNameTuple[1]:
                fileExistanceList[1] = True
            if fileExistanceList == [True, True]:
                break

        fileObjList = [None, None]
        for i in range(2):
            if not fileExistanceList[i]:
                fileObjList[i] = createJsonRetFileIO(fileNameTuple[i])
        return zip(fileExistanceList, fileNameTuple, fileObjList)

    def readFiles(
        self, f_s: tuple[tuple[bool, str, FileIO], ...]
    ) -> tuple[tuple[bool, dict[int, dict[str, int]], FileIO | None], ...]:
        """
        for returned tuple
        tuple[0] is f_r
        tuple[1] is f_tR
        """        
        # This actually get's a zip object
        f_r, f_tR = f_s

        return (
            (f_r[0], loadSafely(f_r[2]), f_r[2]),
            (f_tR[0], loadSafely(f_tR[2]), f_tR[2]),
        )

    def closeFileObjs(self, *fileObjsPlusDicts: tuple[FileIO, dict]) -> None:
        """Dump the data before closing file objects"""        
        for fileObjPlusDict in fileObjsPlusDicts:
            fileObj, d = fileObjPlusDict
            if fileObj:
                fileName = fileObj.name
                fileObj.close()
                dump(d, open(fileName, "w"), indent=2, sort_keys=True)
