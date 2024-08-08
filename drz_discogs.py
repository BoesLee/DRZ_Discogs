"""
gzip to open .gz's, ofc
sys for exit messages
datetime for time reasons
csv for obvious reasons
inflect because its easier to read letters then numbers
xmltodict for other obvious reasons
"""

import gzip
import sys
import datetime
import csv
import inflect
import xmltodict

# Date related requirements
MINUS_YEARS = 15
RELEASED_MIN = 1980
RELEASED_MAX = 2005
# Releases related requirements
RELEASES_MIN = 125
RELEASES_MIN_A = 5
RELEASES_MIN_B = 11
RELEASES_MAX = 375
RELEASES_MAX_A = 10
RELEASES_MAX_B = 25
# Program related things
RELEASES = 0
EXCEPTIONS = 0
labels = {}


# FIX DOCSTRINGS
def main():
    """Parse .XML.GZ file to CSV"""
    try:
        xmltodict.parse(
            gzip.open(input("Filename: ") or "discogs_20240701_releases.xml.gz"),
            item_depth=2,
            item_callback=handle_data,
        )
    except FileNotFoundError:
        print("FileNotFoundError Error Message")
        main()
    except KeyboardInterrupt:
        print("KeyboardInterupt Detected")
    write_csv()


def handle_data(_, data):
    """_summary_

    Args:
        _ (_list_): _description_
        data (_dict_): _description_

    Returns:
        _bool_: _description_
    """
    global RELEASES
    global EXCEPTIONS
    RELEASES += 1
    try:
        released = int(data["released"].split("-")[0])
    except Exception:
        EXCEPTIONS += 1
        return True
    data = data["labels"]["label"]
    if isinstance(data, dict):
        label = data["@name"]
        update_labels(label, released)
    else:
        tmp = []
        for _, value in enumerate(data):
            if value["@name"] not in tmp:
                tmp.append(value["@name"])
        for _, label in enumerate(tmp):
            update_labels(label, released)
    print(RELEASES)
    return True


def update_labels(label, released):
    """_summary_

    Args:
        label (_str_): Key for labels dict, returns an int
        released (_int_): Release Date

    Returns:
        _bool_: ...
    """
    labels.update(
        {
            label: [
                handle_first_release(label, released),
                handle_last_release(label, released),
                handle_releases_count(label),
            ]
        }
    )
    return True


def handle_first_release(label, released):
    """_summary_

    Args:
        label (_str_): Key for labels dict, returns an int
        released (_int_): Release Date

    Returns:
        _int_: Result of comparing two int's
    """
    try:
        if released > labels[label][0]:
            return labels[label][0]
    except KeyError:
        pass
    return released


def handle_last_release(label, released):
    """_summary_

    Args:
        label (_str_): Key for labels dict, returns an int
        released (_int_): Release Date

    Returns:
        _int_: Result of comparing two int's
    """
    try:
        if released < labels[label][0]:
            return labels[label][0]
    except KeyError:
        pass
    return released


def handle_releases_count(label):
    """_summary_

    Args:
        label (_list_): _description_

    Returns:
        _int_: _description_
    """
    try:
        _ = int(labels[label][2]) + 1
    except KeyError:
        return 1
    return _


def write_csv():
    """Write to CSV from labels dict"""
    current_year = datetime.date.today().year
    # CSV request 1
    with open(
        f"labels_{RELEASES_MIN}-{RELEASES_MAX}Releases_Last-{MINUS_YEARS}-years.csv",
        "w",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=["Label", "First release", "Last release", "Releases"]
        )
        writer.writeheader()
        for _ in sorted(labels.items()):
            first_release = int(_[1][0])
            last_release = int(_[1][1])
            releases = _[1][2]
            if (
                last_release <= (current_year - MINUS_YEARS)
                and RELEASES_MIN <= releases <= RELEASES_MAX
            ):
                writer.writerow(
                    {
                        "Label": _[0],
                        "First release": first_release,
                        "Last release": last_release,
                        "Releases": releases,
                    }
                )
    # CSV request 2
    with open(
        f"labels_{RELEASES_MIN_A}-{RELEASES_MAX_A}Releases_Years{RELEASED_MIN}-{RELEASED_MAX}.csv",
        "w",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=["Label", "First release", "Last release", "Releases"]
        )
        writer.writeheader()
        for _ in sorted(labels.items()):
            first_release = int(_[1][0])
            last_release = int(_[1][1])
            releases = _[1][2]
            if (
                first_release >= RELEASED_MIN
                and last_release <= RELEASED_MAX
                and RELEASES_MIN_A <= releases <= RELEASES_MAX_A
            ):
                writer.writerow(
                    {
                        "Label": _[0],
                        "First release": first_release,
                        "Last release": last_release,
                        "Releases": releases,
                    }
                )
    # CSV request 3
    with open(
        f"labels_{RELEASES_MIN_B}-{RELEASES_MAX_B}Releases_Years{RELEASED_MIN}-{RELEASED_MAX}.csv",
        "w",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=["Label", "First release", "Last release", "Releases"]
        )
        writer.writeheader()
        for _ in sorted(labels.items()):
            first_release = int(_[1][0])
            last_release = int(_[1][1])
            releases = _[1][2]
            if (
                first_release >= RELEASED_MIN
                and last_release <= RELEASED_MAX
                and RELEASES_MIN_B <= releases <= RELEASES_MAX_B
            ):
                writer.writerow(
                    {
                        "Label": _[0],
                        "First release": first_release,
                        "Last release": last_release,
                        "Releases": releases,
                    }
                )


if __name__ == "__main__":
    main()
    sys.exit(
        (
            f"{(round((EXCEPTIONS/RELEASES)*100))}% exceptions\n{inflect.engine().number_to_words(len(labels))} labels found"
        )
    )
