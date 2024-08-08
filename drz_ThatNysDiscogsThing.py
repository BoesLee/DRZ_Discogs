"""_summary_
"""
import csv
import gzip
import sys
import discogs_client
import xmltodict
import pprint

MAX_HAVES = 150


l = []
labels = {}

def main():
    """Parse .XML.GZ file to CSV"""
    build_l()
    i = len(l)
    try:
        xmltodict.parse(
            gzip.open(input("XML.GZ Filename: ") or "discogs_20240701_labels.xml.gz"),
            item_depth=2,
            item_callback=handle_data,
        )
    except FileNotFoundError:
        print("FileNotFoundError Error Message")
        main()
    except KeyboardInterrupt:
        sys.exit("KeyboardInterupt Detected")
    print(i)
    print(f'{round((len(l)/i)*100)}% Mess')


def build_l():
    with open(f'{input('CSV Filename: ') or 'labels_5-10_Years1980-2005'}.csv','r' , newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            l.append(row['Label'])


def handle_data(__, _):
    label = _
    if label['name'] in l:
        l.remove(label['name'])
    handle_discogs(label)

    
    # print(len(l))
    return True


def handle_discogs(d:dict):
    dscg = discogs_client.Client(
        "ThatNysDiscogsThing/0.1", user_token="XKlIMSpbhzxCWlOUlXgZHYXfxiXXphYnMPFaAuyB"
    )
    label = dscg.label(d['id'])
    pages = label.releases.pages
    for i in range(pages):
        # pprint.pp(f'\n PAGE {i+1} OF {pages}\n{label.releases.page(i)}')
        for release in label.releases.page(i):
            update_labels(d, release.id)


def update_labels(d: dict, i: int):
    # GET THE CSV STUFF
    labels.update(
        {
            d['name']: [
                d['First release'],
                d['Last release'],
                d['Releases'],
                handle_ratio(d['Label'], i),
            ]
        }
    )
    return True


def handle_ratio(s:str, i:int):
    """_summary_

    Args:
        _ (_type_): _description_
        __ (_type_): _description_

    Returns:
        _type_: _description_
    """    
    _ = d.search(label=s,type="label")
    # try:
    ratio = labels[s][3]
    # except 
    print(ratio)
    community = _.fetch("community")
    if community["want"] > community["have"] and community["have"] <= MAX_HAVES:
        ratio += 1
    print(f'https://www.discogs.com{_.fetch("uri")}')
    return True

def handle_extras():
    try:
        contactinfo = label['contactinfo']
    except KeyError:
        pass
    try:
        profile = label['profile']
    except KeyError:
        pass
    try:
        urls = label['urls']['url']
    except KeyError:
        pass
if __name__ == "__main__":
    main()
    sys.exit()
