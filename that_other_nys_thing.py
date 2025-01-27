"""The Pylint-thing wants this for whatever usefullness that eludes me at this point in time"""

import os
import time
import csv
import sys
import discogs_client


def main():
    """_summary_"""
    open_csv()


def open_csv():
    """_summary_"""
    print("\nPlease select the number preceding the desired .csv")
    l = [f for f in os.listdir("./") if f.endswith(".csv")]
    for i, s in enumerate(l, start=1):
        print(f"{i}: {s}")
    if not l:
        print("No .csv fount.\nRedirecting...")
        sys.exit("Nowhere to redirect to...yet! Exitting...")

    try:
        with open(l[int(input("Select file: ")) - 1], encoding="utf-8") as f:
            r = csv.DictReader(f)
            for _ in r:
                discogs(_["artist"], _["title"])
    except (ValueError, IndexError):
        print("Invalid Input...")
        open_csv()


def discogs(artist: str, title: str):
    """_summary_

    Args:
        artist (str): _description_
        title (str): _description_
    """
    print(title)
    d = discogs_client.Client(
        "ThatNysDiscogsThing/0.1", user_token="XKlIMSpbhzxCWlOUlXgZHYXfxiXXphYnMPFaAuyB"
    )
    try:
        results = d.search(title, artist=artist, type="release")
    except Exception:
        pass
    if not results:
        write_csv(title)
    for i in range(results.pages):
        for _ in results.page(i):
            try:
                release = _
            except Exception:
                pass
            try:
                formats = [_.formats[0]["name"]] + [_.formats[0]["descriptions"]]
            except Exception:
                pass
            try:
                tracklist = _.tracklist
            except Exception:
                pass
            write_csv(title, release, formats, tracklist)


def write_csv(
    title: str, release: str = None, formats: list = None, tracklist: list = None
):
    """_summary_

    Args:
        title (str): _description_
        release (str, optional): _description_. Defaults to None.
        formats (list, optional): _description_. Defaults to None.
        tracklist (list, optional): _description_. Defaults to None.
    """
    file_exists = os.path.isfile("ThatOtherNysThing.csv")
    with open(
        "ThatOtherNysThing.csv",
        "a",
        encoding="utf-8",
    ) as f:
        w = csv.DictWriter(
            f,
            fieldnames=["title", "release", "format", "tracklist"],
        )
        if not file_exists:
            w.writeheader()
        w.writerow(
            {
                "title": title,
                "release": release if release is not None else "",
                "format": formats if formats is not None else "",
                "tracklist": list(tracklist) if tracklist is not None else "",
            }
        )
    time.sleep(0.9)


if __name__ == "__main__":
    main()
