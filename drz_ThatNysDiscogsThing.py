"""_summary_
"""
import csv
import gzip
import sys
import discogs_client
import xmltodict
import time

MAX_HAVES = 150


l = []
tmp = {}
labels = {}

def main():

    read_csv()
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


def read_csv():

    with open(f'{input('CSV Filename: ')}.csv','r' , newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print('Reading file...')
        for row in reader:
            l.append(row['Label'])
            tmp.update(
                {
                    row['Label']: {
                        'first': row['First'],
                        'last': row['Last'],
                        'releases': row['Releases'],
                    }
                }
            )


def handle_data(__, d: dict):
    try:
        contactinfo = d['contactinfo']
    except KeyError:
        contactinfo = ''
    try:
        profile = d['profile']
    except KeyError:
        profile = ''
    try:
        urls = d['urls']['url']
    except KeyError:
        urls = ''
    label = {
        'contactinfo': contactinfo,
        'profile': profile,
        'urls':  urls
    }
    label['name'] = d['name']
    label['id'] = d['id']
    print(f'\nHandling label {label['name']}')
    if label['name'] in l:
        l.remove(label['name'])
        print(len(l))
        handle_discogs(label)
    return True


def handle_discogs(label: dict):
    ratio = 0
    dscg = discogs_client.Client(
        "ThatNysDiscogsThing/0.1", user_token="XKlIMSpbhzxCWlOUlXgZHYXfxiXXphYnMPFaAuyB"
    )
    _ = dscg.label(label['id'])
    pages = _.releases.pages
    for i in range(pages):
        # pprint.pp(f'\n PAGE {i+1} OF {pages}\n{label.releases.page(i)}')
        for release in _.releases.page(i):
            print(release)
            r_id = release.id
            time.sleep(1)
            handle_ratio(r_id, ratio)
            print(f'{int(tmp[label['name']]['releases']) -1} releases left')
    label['ratio'] = ratio
    if label['ratio']/tmp[label['name']]['releases'] >= 0.33:
        build_labels(label)


def handle_ratio(r_id:int, ratio: int):
    """_summary_

    Args:
        _ (_type_): _description_
        __ (_type_): _description_

    Returns:
        _type_: _description_
    """
    dscg = discogs_client.Client(
        "ThatNysDiscogsThing/0.1", user_token="XKlIMSpbhzxCWlOUlXgZHYXfxiXXphYnMPFaAuyB"
    )
    release = dscg.release(r_id)
    print(release)
    haves = release.fetch('community')['have']
    wants = release.fetch('community')['want']
    if wants > haves and haves <= MAX_HAVES:
        ratio += 1
    return ratio
        
        
def build_labels(label: dict):
    labels.update(
        {
            label['name']: {
                'first': tmp[label['name']]['first'],
                'last': tmp[label['name']]['last'],
                'releases': tmp[label['name']]['releases'],
                'ratio': label['ratio'],
                'contactinfo': label['contactinfo'],
                'profile': label['profile'],
                'urls': label['urls']
            }
        }
    )


if __name__ == "__main__":
    main()
    sys.exit()
