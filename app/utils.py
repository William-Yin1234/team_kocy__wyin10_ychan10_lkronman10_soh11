import sqlite3
import time
import datetime


def select_entries_by_author(db_file, author_id=None, exclude=False):

    db = sqlite3.connect(db_file)
    cursor = db.cursor()
    if author_id:
        if exclude:
            cursor.execute("select * from entries where author_id != ?", (author_id,))
        else:
            cursor.execute("select * from entries where author_id = ?", (author_id,))
    else:
        cursor.execute("select * from entries")
    entries_tuples = cursor.fetchall()

    entries = []
    for tuple in entries_tuples:
        cursor.execute("select username from users where id = ?", (tuple[1],))
        author_name = cursor.fetchone()[0]
        date = datetime.datetime.fromtimestamp(int(tuple[3]))
        entry = {"title": tuple[4], "body": tuple[2], "author": author_name, "date": date, "author_id": tuple[1], "id": tuple[0]}
        entries.append(entry)
    db.close()

    def sort_by_date(entry):
        return entry["date"]
    entries_sorted = sorted(entries, key=sort_by_date, reverse=True)

    return entries_sorted


def verify_user_owns_entry(db_file, entry_id, user_id):

    db = sqlite3.connect(db_file)
    cursor = db.cursor()
    cursor.execute("select * from entries where id = ?", (entry_id,))
    entry = cursor.fetchone()
    if not entry:
        db.close()
        return (404, None)
    elif entry[1] != user_id:
        db.close()
        return (403, None)

    return (0, entry)
