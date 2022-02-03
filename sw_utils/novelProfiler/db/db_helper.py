import sqlite3
from pathlib import Path

from click import echo

from .jsHelpScripts import JSHelpScripts


class DBHelper(JSHelpScripts):
    def __init__(self, msg: tuple[str]):
        echo(msg[3])
        echo(msg[4])

    def getChapterNumberFrmDB(
        self,
        con: sqlite3.Connection | None,
        cur: sqlite3.Cursor | None,
        table_name: str,
        novel_name: str,
    ) -> int:
        if (con, cur) == (None, None):
            return
        if con is not None:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
        cur.execute(f"SELECT * from {table_name}")
        r = cur.fetchone()
        return r[novel_name]

    def getConAndCur(self, dbName: str):
        """Get a DB connection and cursor.
        NOTE: The database is assumed to be in the same directory as this file."""
        baseDirectory = Path(__file__).resolve().parent
        con = sqlite3.connect(f"{baseDirectory}/wuxiaworld")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        return (con, cur)
        # print(getChapterNumber(con, None, "current_chapter", "ATG"))

    def updateCurrentChapterNumberOfNovel(
        self,
        con: sqlite3.Connection,
        cur: sqlite3.Cursor | None,
        table_name: str,
        novel_name: str,
        new_val: int,
    ):
        if cur is None:
            cur = con.cursor()

        with con:
            cur.execute(f"UPDATE {table_name} SET {novel_name}={new_val}")


if __name__ == "__main__":
    # con = sqlite3.connect("wuxiaworld")
    # con.row_factory = sqlite3.Row
    # cur = con.cursor()
    # getConAndCur("")
    DBHelper.getConAndCur("")
