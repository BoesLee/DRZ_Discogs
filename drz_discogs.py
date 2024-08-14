"""The thing wants this for whatever usefullness that eludes me at this point in time!"""
import gzip
import sys
import datetime
import csv
import xmltodict

labels = {}


def main():
    """Get the DISCOGS releases from the dump and put it in a .csv!
    """
    try:
        xmltodict.parse(
            # research if possible to use regex to find the file and ask to confirm
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


def handle_data(_: list, d: dict):
    """Do stuff with the xmltodict.parser's stuff!

    Args:
        _ (list): The unused stuff.
        d (dict): The used stuff.

    Returns:
        bool: The xmltodict.parser needs it!
    """
    try:
        released = int(d["released"].split("-")[0])
    # check for better way to catch all errors except exit-things but this is fine for now
    except Exception:
        return True
    title = d["title"]
    _ = d["labels"]["label"]
    if isinstance(_, dict):
        label = _["@name"]
        update_labels(title, label, released)
    else:
        tmp = []
        for __, value in enumerate(_):
            if value["@name"] not in tmp:
                tmp.append(value["@name"])
        for __, label in enumerate(tmp):
            update_labels(title, label, released)
    return True


def update_labels(title: str, label: str, released: int):
    """Make a dict with all the things!

    Args:
        title (str): Some release's title.
        label (str): Some release's label.
        released (int): Some release's release date.
    """
    labels.update(
        {
            label: {
                "first": handle_first_release(label, released),
                "last": handle_last_release(label, released),
                "releases": handle_releases(title, label),
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
        if released > labels[label]["first"]:
            return labels[label]["first"]
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
        if released < labels[label]["last"]:
            return labels[label]["last"]
    except KeyError:
        pass
    return released


def handle_releases(title: str, label: str):
    """Returns the release title(s) of some label!

    Args:
        title (str): Some release's title.
        label (str): Some release's label.

    Returns:
        list: Some label's release title(s).
    """
    try:
        labels[label]["releases"].append(title)
        return labels[label]["releases"]
    except KeyError:
        return [title]


def write_csv():
    """Write some csv's, has a list of noes to pass on to other functions!"""
    noes = [
        "n",
        "no",
        "nope",
    ]
    past_years_csv(noes)
    between_years_csv(noes)


def past_years_csv(noes: list):
    """Summons a .csv with a random minimum and maximum amount of releases released between now and whenever!

    Args:
        noes (list): A list of noes.
    """
    while True:
        if (
            input(
                'Type skip to SKIP "past year csv" mode, else just press enter\n'
            ).casefold()
            == "skip"
        ):
            return
        try:
            y = int(input("Last x years? x = "))
            r_min = input("Minimum releases: ")
            r_max = input("Maximum releases: ")
        except ValueError:
            print("INCORRECT USAGE ERROR!\ninput a number like 123...")
            past_years_csv(noes)
        current_year = datetime.date.today().year
        with open(
            f"Labels(RELEASES:{r_min}-{r_max})(YEARS:Last {y}).csv",
            "w",
            encoding="utf-8",
        ) as f:
            writer = csv.DictWriter(
                f, fieldnames=["Label", "First", "Last", "Releases"]
            )
            writer.writeheader()
            for label, _ in labels.items():
                first = _["first"]
                last = _["last"]
                releases = _["releases"]
                if last <= (current_year - y) and r_min <= len(releases) <= r_max:
                    writer.writerow(
                        {
                            "Label": label,
                            "First": first,
                            "Last": last,
                            "Releases": releases,
                        }
                    )

        if (input("Want to do this again?")).casefold() in noes:
            break


def between_years_csv(noes: list):
    """Summons a .csv with a random minimum and maximum amount of releases released between whenever and some later whenever!

    Args:
        noes (list): A list of noes.
    """
    while True:
        if (
            input(
                'Type skip to SKIP "between year csv" mode, else just press enter\n'
            ).casefold()
            == "skip"
        ):
            return
        try:
            y_min = input("Earliest year: ")
            y_max = input("Latest year: ")
            r_min = input("Minimum releases: ")
            r_max = input("Maximum releases: ")
        except ValueError:
            print("INCORRECT USAGE ERROR!\ninput a number like 123...")
            past_years_csv(noes)
        with open(
            f"Labels_(RELEASES:{r_min}-{r_max})(YEARS:{y_min}-{y_max}).csv",
            "w",
            encoding="utf-8",
        ) as f:
            writer = csv.DictWriter(
                f, fieldnames=["Label", "First", "Last", "Releases"]
            )
            writer.writeheader()
            for label, _ in labels.items():
                first = _["first"]
                last = _["last"]
                releases = _["releases"]
                if first >= y_min and last <= y_max and r_min <= len(releases) <= r_max:
                    writer.writerow(
                        {
                            "Label": label,
                            "First": first,
                            "Last": last,
                            "Releases": releases,
                        }
                    )
        if (input("Want to do this again?")).casefold() in noes:
            break


if __name__ == "__main__":
    main()
    sys.exit(0)
