# -*- coding: utf-8 -*-

# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

import scraperwiki
import requests
import lxml.html
import urlparse

# source_url = 'http://www.assemblee-nationale.mg/?page_id=6549'
source_url = 'http://www.assemblee-nationale.mg/?page_id=5217'
response = requests.get(source_url)

root = lxml.html.fromstring(response.text)

lis = root.get_element_by_id('deputes').cssselect('li')

data = []

for li in lis:
    member = {
        'chamber': 'National Assembly',
        'term_id': 2013,
        }

    member['details_url'] = li.cssselect('a')[0].get('href')

    split_url = urlparse.urlsplit(member['details_url'])
    member['page_id'] = urlparse.parse_qs(split_url.query)['depute'][0]

    img = li.cssselect('img')[0]
    member['image'] = img.get('src')
    member['name'] = img.get('title')

    member_resp = requests.get(member['details_url'])
    member_root = lxml.html.fromstring(member_resp.text)

    mfiche = member_root.cssselect('.mfiche')
    pairs = [(x.text, x.tail) for x in mfiche[0]]

    for key, val in pairs:
        key = key.strip() if key else ''
        val = val.strip() if val else ''

        if not key or not val:
            continue
        if key == u'Nom:':
            member['name'] = val
        elif key == u'District:':
            member['district'] = val
        elif key == u'Région:':
            member['region'] = val
        elif key == u'Parti:':
            member['party'] = val
        elif key == u'Fonction parlementaire:':
            member['executive'] = val
        elif key == u'Age:':
            # I see no point in us storing age, that'll just go out of date
            continue
# Things we're not handling yet:
# 'Membre des commissions:'

# These appear commented out in the source.
# 'Adresse:':
# 'Date de naissance:':
# 'Contacts t\xe9l\xe9phonique:'
# 'Province:'
# 'R\xe9gion d'origine:'
        else:
            import pdb;pdb.set_trace()

    data.append(member)

scraperwiki.sqlite.save(unique_keys=['page_id'], data=data)

legislatures_data = [
    {'id': 2013, 'name': '2013-1018', 'start_date': '2013-12-20', 'end_date': 2018},
    ]

scraperwiki.sqlite.save(unique_keys=['id'], data=legislatures_data, table_name='terms')
