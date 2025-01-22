"""The Pylint-thing wants this for whatever usefullness that eludes me at this point in time"""

import os
import csv
import sys
import discogs_client

tmp = {}
ex = {}


def main():

    openCSV()
    writeCSV()


def openCSV():
    l = [f for f in os.listdir("./") if f.endswith(".csv")]
    for i, s in enumerate(l, start=1):
        print(f"{i}: {s}")
    if not l:
        print("No .csv fount.\nRedirecting...")
        sys.exit("Nowhere to redirect to...yet! Exitting...")
    with open(l[int(input("Select file: ")) - 1], encoding="utf-8") as f:
        r = csv.DictReader(f)
        for release_title, artist in r:
            discogsAPI(release_title, artist)


def discogsAPI(release_title=str, artist=str):
    d = discogs_client.Client(
        "ThatNysDiscogsThing/0.1", user_token="XKlIMSpbhzxCWlOUlXgZHYXfxiXXphYnMPFaAuyB"
    )
    # make a separate dict to catch the exceptions
    results = d.search(release_title, artist=artist, type="release,master")


tmp.setdefault("someAlbumsName", []).append("someReleaseTitle")


def writeCSV():
    for release, release_title in tmp.items():
        with open(
            "ThatOtherNysThing.csv",
            "a",
            encoding="utf-8",
        ) as f:
            w = csv.DictWriter(
                f,
                fieldnames=["Artist", "Release title"],
            )
            w.writerow({"Release": release, "Release title": list(release_title)})
