import os
from bs4 import BeautifulSoup
from hashlib import sha1
import re
from tqdm import tqdm
import json

KEYWORD = "beatles"
IN_FOLDER_NAME = "Beatles"
OUTFILE_NAME = "full_beatles"


nodes = {} # maps name to the node dict
links = {} # list of links
visited = set()

no_wikipedia = re.compile(r'^https://en\.wikipedia\.org/wiki/(Wikipedia|Category|Template|Template_talk|Help|Portal|Special):.*')
is_url = re.compile(r'^/wiki/.*')
kwrd = re.compile(r'^\s?' + KEYWORD + r'\s', re.IGNORECASE)

total_links = 0
for file in tqdm(os.listdir('./toparse/' + IN_FOLDER_NAME)):
    with open('./toparse/' + IN_FOLDER_NAME + '/' + file, 'r', encoding='utf-8') as f:
        href = f.readline().strip('\n')
        soup = BeautifulSoup(f.read(), 'html.parser')
        if not soup.body.findAll(text=kwrd):
            continue

        name = soup.find('title').text[:-12]
        id = int(sha1(href.encode('utf-8')).hexdigest()[:10], 16)


        description = ''
        for p in soup.find_all('p'):
            if len(p.text) > 100:
                description = p.text
                break

        node = {'id': id, 'href': href, 'name': name, 'description': description, 'value': 0}

        nodes[id] = node

        content = soup.find('div', {'id': 'content'})
        all_a = content.find_all('a')
        for a in all_a:
            a_link = a.get('href')
            if not a_link:
                continue
            full_link = "https://en.wikipedia.org" + a_link
            if re.match(is_url, a_link) and full_link in visited:
                other_id = int(sha1(full_link.encode('utf-8')).hexdigest()[:10], 16)
                nodes[other_id]['value'] += 1
                total_links += 1
                link = {'source': id, 'target': other_id}

                links[id + other_id] = link

        visited.add(href)

objects = {'nodes': list(nodes.values()), 'links': list(links.values())}

with open('graphs/' + OUTFILE_NAME + '.json', 'w+') as f:
    json.dump(objects, f)
