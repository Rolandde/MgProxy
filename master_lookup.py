import json
import requests
from collections import OrderedDict
from lxml import html


def urlHtmlToJpg(url_list):
    result = []

    for url in url_list:
        parsed = url.split('/')
        set_name, number_html = parsed[1], parsed[3]
        number = number_html.split('.')[0]

        new_url = '/{}/{}.jpg'.format(set_name, number)
        result.append(new_url)

    return result


def getSetInfo(set_name):
    set_request = '++e:{}/en'.format(set_name)
    param = {'q': set_request, 'v': 'list', 's': 'issue'}
    page = requests.get('http://magiccards.info/query', params=param)
    tree = html.fromstring(page.text)

    name = tree.xpath('//table[3]//tr/td[2]/a//text()')
    url = tree.xpath('//table[3]//tr/td[2]/a/@href')
    url = urlHtmlToJpg(url)

    return tuple(zip(name, url))


def getSetConversion():
    j_get = requests.get('http://mtgjson.com/json/AllSets.json')
    j_text = j_get.content
    j_text = j_text.decode('utf-8')
    j_info = json.loads(j_text, object_pairs_hook=OrderedDict)

    result = OrderedDict()

    for code, mgset in j_info.items():
        if 'magicCardsInfoCode' in mgset:
            result[code] = mgset['magicCardsInfoCode']

    return result


def cardMaster():
    card_master = OrderedDict()
    set_conversion = getSetConversion()

    for code in set_conversion:
        card_info = getSetInfo(set_conversion[code])

        for info in card_info:
            card_name = info[0]
            card_url = info[1]

            if card_name not in card_master:
                card_master[card_name] = OrderedDict()

            card_set = card_master[card_name]

            if code not in card_set:
                card_set[code] = [card_url]
            else:
                card_set[code].append(card_url)

    return card_master


if __name__ == "__main__":
    to_write = open('master.json', 'w')
    to_write.write(json.dumps(cardMaster()))
