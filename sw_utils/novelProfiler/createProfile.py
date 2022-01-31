from io import FileIO


def closeFileObjects(*fileObjs: FileIO):
    for fileObj in fileObjs:
        fileObj.close()
