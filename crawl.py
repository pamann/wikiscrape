import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
from hashlib import sha1
from time import sleep
import os

FOLDER_NAME = "NYC"
QUEUE_NAME = 'nyc_queue.txt'

# Wikipedia specific parameters
base_url = "https://en.wikipedia.org"
is_url = re.compile(r'^/wiki/.*')
no_files = re.compile(r'^https://en\.wikipedia\.org/wiki/.*\.(svg|png|jpg|wav|gif|ogg)')
no_wikipedia = re.compile(r'^https://en\.wikipedia\.org/wiki/(Wikipedia|Category|Template|Template_talk|Help|Portal|Special):.*')
no_library = re.compile(r'^https://en\.wikipedia\.org/wiki/ISBN_(\(identifier\)|Doi_\(identifier\)|JSTOR_\(identifier\))')


queue = []
with open('./queues/' + QUEUE_NAME, 'r', encoding='utf-8') as f:
    for url in f:
        if not re.match(no_files, url) and not re.match(no_wikipedia, url) and not re.match(no_library, url):
            queue.append(url.strip('\n '))

new_urls = []

try:
    os.mkdir('./toparse/' + FOLDER_NAME)
except:
    pass


for url in tqdm(queue):
    sleep(.05)
    try:
        r = requests.get(url)
    except:
        continue

    soup = BeautifulSoup(r.content, 'html.parser')
    content = soup.find('div', {'id': 'content'})

    filename = sha1(url.encode('utf-8')).hexdigest()[:10] + '.html'


    with open('./toparse/' + FOLDER_NAME + '/' + filename, 'w+', encoding='utf-8') as toparse:
        toparse.write(url)
        toparse.write('\n')
        toparse.write(r.text)

    for a in content.find_all('a'):
        href = a.get('href')
        if href and re.match(is_url, href):
            new_url = base_url + href
            new_urls.append(new_url)

with open('./queues/' + QUEUE_NAME, 'w', encoding='utf-8') as seed:
    for line in new_urls:
        seed.write(line)
        seed.write('\n')
