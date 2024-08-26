"""The Pylint-thing wants this for whatever usefullness that eludes me at this point in time!"""

from datetime import datetime
import os
import time
import csv
import gzip
import pickle
import sys
import xmltodict
import discogs_client

xml_dict = {}


def main():
    """Match input to redirect somewhere!"""
    # LOOK UP ARGPARSE STUFF!
    while True:
        match input(
            "Input:\n-u: Update from XML\n-c: Create a CSV\n-e: Exit\n"
        ) or sys.argv[1]:
            case "-u":
                select_xml()
            case "-c":
                pickle_dict()
                handle_csv()
            case "-e":
                sys.exit(0)
            case _:
                print("Invalid input.")


def select_xml():
    """Select some .xml!"""
    l = [f for f in os.listdir("./") if f.endswith("releases.xml.gz")]
    for i, s in enumerate(l, start=1):
        print(f"{i}) {s}")
    if not l:
        sys.exit(
            "No releases.xml.gz file found!\nGet one from:\nshttps://discogs-data-dumps.s3.us-west-2.amazonaws.com/index.html"
        )
    try:
        handle_xml(l[int(input("Select file: ")) - 1])
    except IndexError:
        print("Invalid selection!")
        if input("Try again? ").casefold().startswith("n"):
            main()
        select_xml()


def handle_xml(filename: str):
    """Dig trough the .xml parsingly!

    Args:
        filename (str): Some file's name

    Returns:
        bool: Consider if things need savin'
    """
    try:
        xmltodict.parse(
            # research if possible to use regex to find the file and ask to confirm
            gzip.open(filename),
            item_depth=2,
            item_callback=handle_data,
        )
    except FileNotFoundError:
        print("XML FileNotFoundError Error Message")
        main()
    except KeyboardInterrupt:
        sys.exit("\nKeyboardInterupt Detected")
    if input(f"Save {filename}? ").casefold().startswith("n"):
        main()
    save_dict()
    if input("Create CSV? ").casefold().startswith("n"):
        main()
    handle_csv()


def handle_data(l: list, d: dict):
    """Do stuff with the xmltodict.parser's stuff!

    Args:
        _ (list): The mostly unused stuff.
        d (dict): The mostly used stuff.

    Returns:
        bool: The xmltodict.parser needs it!
    """
    try:
        released = int(d["released"].split("-")[0])
    # check for better way to catch all errors except exit-things but this is fine, for now-ish
    except Exception:
        return True
    r_id = l[1][1]["id"]
    _ = d["labels"]["label"]
    if isinstance(_, dict):
        label = _["@name"]
        l_id = _["@id"]
        update_dict(label, released, r_id, l_id)
    else:
        tmp = []
        for __, value in enumerate(_):
            if value["@name"] not in tmp:
                tmp.append([value["@name"], value["@id"]])
        for __, label in enumerate(tmp):
            update_dict(label[0], released, r_id, label[1])
    return True


def update_dict(label: str, released: int, r_id: int, l_id: int):
    """Make a dict with all the things!

    Args:
        title (str): Some release's title.
        label (str): Some release's label.
        released (int): Some release's release date.
    """
    xml_dict.update(
        {
            label: {
                "first": handle_first_release(label, released),
                "last": handle_last_release(label, released),
                "releases": handle_r_id(label, r_id),
                "discogs": f"https://www.discogs.com/label/{l_id}-{label.replace(' ', '-')}",
            }
        }
    )


def handle_first_release(label: str, released: int):
    """Discover some label's earliest release date!

    Args:
        label (str): Some release's label.
        released (int): Some release's release date.

    Returns:
        int: Some label's earliest release.
    """
    try:
        if released > xml_dict[label]["first"]:
            return xml_dict[label]["first"]
    except KeyError:
        pass
    return released


def handle_last_release(label: str, released: int):
    """Discover some label's latest release date!

    Args:
        label (str): Some release's label.
        released (int): Some release's release date.

    Returns:
        int: Some label's latest release.
    """
    try:
        if released < xml_dict[label]["last"]:
            return xml_dict[label]["last"]
    except KeyError:
        pass
    return released


def handle_r_id(label: str, r_id: str):
    """Returns the release title(s) of some label!

    Args:
        title (str): Some release's title.
        label (str): Some release's label.

    Returns:
        list: Some label's release title(s).
    """
    try:
        xml_dict[label]["releases"].append(r_id)
        return xml_dict[label]["releases"]
    except KeyError:
        return [r_id]


def save_dict():
    """Dump labels dict"""
    try:
        with open(input("Save as: ")+(".dict"), "wb") as _:
            pickle.dump(xml_dict, _)
        _.close()
    except FileNotFoundError:
        print("FileNotFoundError Error Message")


def pickle_dict():
    """Do stuff with pickle dict!"""
    l = [f for f in os.listdir("./") if f.endswith(".dict")]
    for i, s in enumerate(l, start=1):
        print(f"{i}) {s}")
    if not l:
        print("No dictionaries fount.\nRedirecting...")
        select_xml()
    with open(l[int(input("Select file: ")) - 1], "rb") as f:
        while True:
            try:
                (xml_dict.update(pickle.load(f)))
            except EOFError:
                break


def handle_csv():
    """Summons some .csv!"""
    if input("Use defaults? ").casefold().startswith("y"):
        try:
            exclude = {"now": datetime.now().year, "excl": 15}
            between = {"min": 1980, "max": 2005}
            a = {"min": 125, "max": 375}
            b = {"min": 5, "max": 10}
            c = {"min": 11, "max": 25}

        except ValueError:
            if input("Do you want to try this again? ").casefold().startswith("n"):
                main()
            handle_csv()
    else:
        # MAKE THIS and ADJUST REST LATER
        ...
    count = 0
    for label, _ in xml_dict.items():
        first = _["first"]
        last = _["last"]
        rels = _["releases"]
        r_total = len(rels)
        discogs = _["discogs"]
        if a["min"] < r_total < a["max"] and last < (exclude["now"] - exclude["excl"]):
            ratio = handle_ratio(rels)
            if ratio is True:
                with open(
                    f"ThatNysThing|Between_{a['min']}_and_{a['max']}_releases|Exclude_last_{exclude['excl']}_years)_since_{exclude['now']}.csv",
                    "a",
                    encoding="utf-8",
                ) as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=[
                            "Label",
                            "First",
                            "Last",
                            "Releases",
                            "Discogs",
                        ],
                    )
                    writer.writerow(
                        {
                            "Label": label,
                            "First": first,
                            "Last": last,
                            "Releases": r_total,
                            "Discogs": discogs,
                        }
                    )

        if first < between["min"] or last > between["max"]:
            pass
        else:
            if b["min"] < r_total < b["max"]:
                ratio = handle_ratio(rels)
                if ratio is True:
                    with open(
                        f"ThatNysThing|Between_{b['min']}_and_{b['max']}_releases|From_{between['min']}_to_{between['max']}).csv",
                        "a",
                        encoding="utf-8",
                    ) as f:
                        writer = csv.DictWriter(
                            f,
                            fieldnames=[
                                "Label",
                                "First",
                                "Last",
                                "Releases",
                                "Discogs",
                            ],
                        )
                        writer.writerow(
                            {
                                "Label": label,
                                "First": first,
                                "Last": last,
                                "Releases": r_total,
                                "Discogs": discogs,
                            }
                        )
                else:
                    pass

            elif c["min"] < r_total < c["max"]:
                ratio = handle_ratio(rels)
                if ratio is True:
                    with open(
                        f"ThatNysThing|Between_{c['min']}_and_{c['max']}_releases|From_{between['min']}_to_{between['max']}).csv",
                        "a",
                        encoding="utf-8",
                    ) as f:
                        writer = csv.DictWriter(
                            f,
                            fieldnames=[
                                "Label",
                                "First",
                                "Last",
                                "Releases",
                                "Discogs",
                            ],
                        )
                        writer.writerow(
                            {
                                "Label": label,
                                "First": first,
                                "Last": last,
                                "Releases": r_total,
                                "Discogs": discogs,
                            }
                        )
                else:
                    pass
        count += 1
        print(f"{count} / {len(xml_dict)}")


def handle_ratio(rels: list):
    """Calculates some label's release's ratio

    Args:
        releases (list): Some label's release's list.
        h_max (int): Some release's maximum 'haves'

    Returns:
        bool: Deciding whether some row gets written
    """
    # LOOK TO MAKE THIS SAVE THE RATIOS AS TO AVOID THE LENGTHY SHIIT
    ratio = 0
    total = len(rels)
    count = total
    max_haves = 150
    print(f"Going trough {len(rels)} releases for this label!")
    dscg = discogs_client.Client(
        "ThatNysDiscogsThing/0.1", user_token="XKlIMSpbhzxCWlOUlXgZHYXfxiXXphYnMPFaAuyB"
    )
    for r_id in rels:
        try:
            release = dscg.release(r_id)
            haves = release.fetch("community")["have"]
            wants = release.fetch("community")["want"]
        # check for better way to catch all errors except exit-things but this is fine, for now-ish
        except Exception:
            pass
        if wants > haves and haves <= max_haves:
            ratio += 1
        count -= 1
        if ratio >= round(total / 3):
            print("Great succes!")
            return True
        if (count + ratio) < round(total / 3):
            print("This one failed!")
            return False
        print(f"{count} releases left... Ratio: {ratio}")
        # Slow down request speed 'cause whiny API
        time.sleep(0.9)


if __name__ == "__main__":
    main()
