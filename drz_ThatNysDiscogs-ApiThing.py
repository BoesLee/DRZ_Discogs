"""_summary_
"""
import csv
import re
import gzip
import sys
import discogs_client
import xmltodict
import time

MAX_HAVES = 150


l = []
labels = {}

def main():

    read_csv()
    # handle_xml()

def read_csv():

    with open('Labels(RELEASES:125-375)(YEARS:Last 15).csv','r' , newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print('Reading file...')
        for row in reader:
            update_labels(row)

def update_labels(label: dict):

    labels.update(
        {
            label['Label']: {
                "first": label['First'],
                "last": label['Last'],
                "releases": handle_releases(label['Releases']),
            }
        }
    )
    
    
def handle_releases(_: str):
    
    
    l.append(_)
    if len(l) <= 1:
        sys.exit(print(l[0]))
        
    
    
    
    
    
    
    
    
    
    # ratio = 0

    # _ = dscg.label(label['id'])
    # pages = _.releases.pages
    # for i in range(pages):
    #     # pprint.pp(f'\n PAGE {i+1} OF {pages}\n{label.releases.page(i)}')
    #     for release in _.releases.page(i):
    #         print(release)
    #         r_id = release.id
    #         time.sleep(1)
    #         handle_ratio(r_id, ratio)
    #         print(f'{int(tmp[label['name']]['releases']) -1} releases left')
    # label['ratio'] = ratio
    # if label['ratio']/tmp[label['name']]['releases'] >= 0.33:
    #     build_labels(label)


def handle_xml():

    try:
        xmltodict.parse(
            gzip.open(input("XML.GZ Filename: ") or "labels(RELEASES:125-375)(YEARS:Last 15).csv"),
            item_depth=2,
            item_callback=handle_data,
        )
    except FileNotFoundError:
        print("FileNotFoundError Error Message")
        main()
    except KeyboardInterrupt:
        sys.exit("KeyboardInterupt Detected")





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
