from io import FileIO
from json import load
from os import makedirs, listdir


class File_Directory_JSON_Worker:
    def __init__(
        self, basePath: str, novelName: str
    ) -> tuple[tuple[bool, dict[int, str] | None]]:
        self.novelName = novelName
        self.novelPath = f"{basePath}/{novelName}"
        self.novelPrfPath = f"{basePath}/{novelName}/profile/"
        self.retFilePath = lambda s: f"{self.novelPrfPath}/{novelName}_{s}.json"

        self.createDirectoriesReturnTrueIfExists()
        # <>_read.json & <>_toRead.json
        return self.readFiles(*self.checkIfFilesExist())

    def createDirectoriesReturnTrueIfExists(self) -> bool:
        """create `self.novelPath`/profile/
        \nreturn True if FileExistsError raised,\nelse False"""
        try:
            makedirs(self.novelPrfPath)
            return False
        except FileExistsError:
            return True

    def checkIfFilesExist(self) -> tuple[tuple[bool, str, FileIO | None]]:
        """Check for existence of
        <self.novelName>_read.json and <self.novelName>_toRead.json
        \nCreate them if they don't exist"""
        result = listdir(self.novelPrfPath)
        fileNameTuple = (self.retFilePath("read"), self.retFilePath("toRead"))
        fileExistanceList = [False, False]
        for fileName in result:
            if fileName == fileExistanceList[0]:
                fileExistanceList[0] = True
            elif fileName == fileExistanceList[1]:
                fileExistanceList[1] = True
            if fileExistanceList == [True, True]:
                break

        fileObjList = [None, None]
        for i in range(2):
            if not fileExistanceList[i]:
                fileObjList[i] = open(f"{self.novelPrfPath}/{fileNameTuple[i]}", "r+")
        return tuple(zip(fileExistanceList, fileNameTuple, fileObjList))

    def readFiles(self, *f_s: tuple[bool, str, FileIO]):
        f_r, f_tR = f_s        
        return (
            (f_r[0], load(f_r), f_r[2]),
            (f_tR[0], load(f_tR[2]), f_tR[2])
        )
