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
        f_r, f_tR = self.checkIfFilesExist()
        

    def createDirectoriesReturnTrueIfExists(self) -> bool:
        """create `self.novelPath`/profile/
        \nreturn True if FileExistsError raised,\nelse False"""
        try:
            makedirs(self.novelPrfPath)
            return False
        except FileExistsError:
            return True

    def checkIfFilesExist(self):
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

        for i in range(2):
            if not fileExistanceList[i]:
                open(f"{self.novelPrfPath}/{fileNameTuple[i]}", "w")
        return tuple(zip(fileExistanceList, fileNameTuple))

    def readFiles(self, f_r: tuple[bool, str], f_tR: tuple[bool, str]):
        """
        f_r[0] == \n
        False -> Don't return fobj\n
        True -> Return f_rReadFobj\n

        f_tR[0] == \n
        False -> Return f_tRWriteFObj\n
        True -> 
        """
        f_rWriteFObj = open(f_r[1], 'w')
        f_tRWriteFObj = open(f_tR[1], 'w')
        pass
