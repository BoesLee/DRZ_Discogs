"""The thing wants this for whatever usefullness that eludes me at this point in time!"""

import gzip
import datetime
import csv
import time
import xmltodict
import discogs_client


labels = {}


def main():
    """Get the all the releases from the dump and put it in a .csv!"""
    handle_xml()
    write_csv()


def handle_xml():
    """Dig trough the .xml parsingly!"""
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


def handle_data(l: list, d: dict):
    """Do stuff with the xmltodict.parser's stuff!

    Args:
        _ (list): The unused stuff.
        d (dict): The used stuff.

    Returns:
        bool: The xmltodict.parser needs it!
    """
    try:
        released = int(d["released"].split("-")[0])
    # check for better way to catch all errors except exit-things but this is fine, for now-ish
    except Exception:
        return True
    r_id = l[1][1]['id']
    _ = d["labels"]["label"]
    if isinstance(_, dict):
        label = _["@name"]
        update_labels(label, released, r_id)
    else:
        tmp = []
        for __, value in enumerate(_):
            if value["@name"] not in tmp:
                tmp.append(value["@name"])
        for __, label in enumerate(tmp):
            update_labels(label, released, r_id)
    return True


def update_labels(label: str, released: int, r_id: int):
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
                "releases": handle_releases(label, r_id),
            }
        }
    )
    print(f'Updated label, {len(labels)} labels found...of the 1097595')


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


def handle_releases(label: str, r_id: str):
    """Returns the release title(s) of some label!

    Args:
        title (str): Some release's title.
        label (str): Some release's label.

    Returns:
        list: Some label's release title(s).
    """
    try:
        labels[label]["releases"].append(r_id)
        return labels[label]["releases"]
    except KeyError:
        return [r_id]


def write_csv():
    """Write some csv's, has a list of noes to pass on to other functions!"""
    noes = ["n", "no", "no!"]
    past_years_csv(noes)
    between_years_csv(noes)
    between_years_csv2(noes)
    # while True:
    #     print("Please choose how to continue...")
    #     match input(
    #         "To summon a .csv with a random minimum and maximum amount of releases released between now and whenever: Type -p!\nTo summon a .csv with a random minimum and maximum amount of releases released between whenever and some later whenever: Type -b\nTo exit... Type exit!\n"
    #     ).casefold():
    #         case "-p":
    #             past_years_csv(noes)
    #         case "-b":
    #             between_years_csv(noes)
    #         case "exit":
    #             sys.exit("Exit-ed")
    #         case _:
    #             print("WRONG INPUT! TRY AGAIN!")


def past_years_csv(noes: list):
    """Summons a .csv with a random minimum and maximum amount of releases released between now and whenever!

    Args:
        noes (list): A list of noes.
    """
    try:
        # y = int(input("Last x years? x = "))
        # r_min = int(input("Minimum releases: "))
        # r_max = int(input("Maximum releases: "))
        # h_max = int(input("Maximum haves: "))
        y = 15
        r_min = 125
        r_max = 375
        h_max = 150

    except ValueError:
        if input("Do you want to try this again?").casefold() in noes:
            return
        past_years_csv(noes)
    current_year = datetime.date.today().year

    for label, _ in labels.items():
        first = _["first"]
        last = _["last"]
        releases = _["releases"]
        if last < (current_year - y) and r_min > len(releases) > r_max:
            print('Label passed!')
        else:
            ratio = handle_ratio(releases, h_max)
            if ratio is True:
                with open(f"Labels_(RELEASES:{r_min}-{r_max})(YEARS:Last {y}).csv","w", encoding="utf-8",) as f:
                    writer = csv.DictWriter(f, fieldnames=["Label", "First", "Last", "Releases"])
                    writer.writeheader()
                    writer.writerow({
                            "Label": label,
                            "First": first,
                            "Last": last,
                            "Releases": len(releases)
                        })


def between_years_csv(noes: list):
    """Summons a .csv with a random minimum and maximum amount of releases released between whenever and some later whenever!

    Args:
        noes (list): A list of noes.
    """
    try:
        # y_min = int(input("Earliest year: "))
        # y_max = int(input("Latest year: "))
        # r_min = int(input("Minimum releases: "))
        # r_max = int(input("Maximum releases: "))
        # h_max = int(input("Maximum haves: "))
        y_min = 1980
        y_max = 2005
        r_min = 5
        r_max = 10
        h_max = 150
    except ValueError:
        if input("Do you want to try this again?").casefold() in noes:
            return
        past_years_csv(noes)
    for label, _ in labels.items():
        first = _["first"]
        last = _["last"]
        releases = _["releases"]
        if first < y_min and last > y_max and r_min > len(releases) > r_max:
            print('Label passed!')
        else:
            ratio = handle_ratio(releases, h_max)
            if ratio is True:
                with open(f"Labels_(RELEASES:{r_min}-{r_max})(YEARS:{y_min}-{y_max}).csv","w", encoding="utf-8",) as f:
                    writer = csv.DictWriter(f, fieldnames=["Label", "First", "Last", "Releases"])
                    writer.writeheader()
                    writer.writerow({
                            "Label": label,
                            "First": first,
                            "Last": last,
                            "Releases": len(releases)
                        })

def between_years_csv2(noes: list):
    """Summons a .csv with a random minimum and maximum amount of releases released between whenever and some later whenever!

    Args:
        noes (list): A list of noes.
    """
    try:
        # y_min = int(input("Earliest year: "))
        # y_max = int(input("Latest year: "))
        # r_min = int(input("Minimum releases: "))
        # r_max = int(input("Maximum releases: "))
        # h_max = int(input("Maximum haves: "))
        y_min = 1980
        y_max = 2005
        r_min = 11
        r_max = 25
        h_max = 150
    except ValueError:
        if input("Do you want to try this again?").casefold() in noes:
            return
        past_years_csv(noes)
    for label, _ in labels.items():
        first = _["first"]
        last = _["last"]
        releases = _["releases"]
        if first < y_min and last > y_max and r_min > len(releases) > r_max:
            print('Label passed!')
        else:
            ratio = handle_ratio(releases, h_max)
            if ratio is True:
                with open(f"Labels_(RELEASES:{r_min}-{r_max})(YEARS:{y_min}-{y_max}).csv","w", encoding="utf-8",) as f:
                    writer = csv.DictWriter(f, fieldnames=["Label", "First", "Last", "Releases"])
                    writer.writeheader()
                    writer.writerow({
                            "Label": label,
                            "First": first,
                            "Last": last,
                            "Releases": len(releases)
                        })

def handle_ratio(releases: list, h_max: int):
    """Calculates some label's release's ratio

    Args:
        releases (list): Some label's release's list.
        h_max (int): Some release's maximum "haves"

    Returns:
        bool: To decide if some row gets written or not
    """
    ratio = 0
    total = len(releases)
    count = total
    print(f'Going trough {len(releases)} releases for this label!')
    dscg = discogs_client.Client(
        "ThatNysDiscogsThing/0.1", user_token="XKlIMSpbhzxCWlOUlXgZHYXfxiXXphYnMPFaAuyB"
    )
    for r_id in releases:
        time.sleep(0.8)
        release = dscg.release(r_id)
        haves = release.fetch('community')['have']
        wants = release.fetch('community')['want']
        if wants > haves and haves <= h_max:
            ratio += 1
        count -= 1
        if ratio >= round(total/3):
            print('Great succes!')
            return True
        if (count+ratio) < round(total/3):
            print('This one failed!')
            return False
        print(f'{count} releases left...')


if __name__ == "__main__":
    main()
