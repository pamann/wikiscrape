from pywikiapi import wikipedia as pywiki
import wikipedia
import time
import json
from concurrent.futures import ThreadPoolExecutor
from concurrent import futures
from multiprocessing import Pool
from multiprocessing import Queue
import hashlib

nodes = set()
links = set()
root_term = "Halloween"
site = pywiki('en')
pool = ThreadPoolExecutor(8) # 8 threads, adjust to taste and # of cores
jobs = []

def query_wiki(ttls, tier):
    global site
    for page in site.query(titles=ttls, format="json", pllimit="max", lhlimit="max", prop=["links", "linkshere", "description"], redirects=True):
        page = page.pages[0]
        return process_comp_jobs(page, tier, page.description)
    

def process_comp_jobs(tt_page_s, tier, desc):
    if 'links' in tt_page_s and 'linkshere' in tt_page_s:
        l = [v.title for v in tt_page_s.links]
        lh = [v.title for v in tt_page_s.linkshere]
        lset = set(l)
        lhset = set(lh)
        tt_bidi_links = lset.intersection(lhset)
        aggregate_nodes(tt_bidi_links, tier, desc)
        aggregate_links(tt_page_s.title, tt_bidi_links) 
        return tt_bidi_links

def fetch_links(root_term):
    global jobs
    search_r = wikipedia.search(root_term)
    root = wikipedia.page(search_r[0])
    root_id = root.pageid
    summary = root.summary.split('.')[0]
    count = 0
    aggregate_nodes([root_term], 3, summary)
    bidi_links = query_wiki(root_term, 2)

    with ThreadPoolExecutor(8) as executor: # start threaded bidi links of second tier
        for bidi_link in bidi_links:
            jobs.append(executor.submit(query_wiki, bidi_link, 1))
        query_pool = Pool(processes=50)
        tt_pool = [query_pool.apply_async(query_wiki, (p, 1))
            for p in futures.as_completed(jobs)]

        query_pool.close()
        query_pool.terminate()
        query_pool.join()
  
def aggregate_links(nodeid, res):
    global links
    obj = [(nodeid, link_dest) for link_dest in res]
    links = links.union(set(obj))

def aggregate_nodes(n_list, v, desc=''):
    global nodes
    obj = set([(node, v, desc) for node in n_list])
    nodes = nodes.union(set(obj))

start_time = time.time()
fetch_links(root_term)
timer = time.time() - start_time

# unpack sets of tuples into lists of dicts
nodes = [{
    "name": name,
    "id": hashlib.md5(name.encode('utf-8')).hexdigest(),
    "val": val,
    "description": desc,
} for (name, val, desc) in nodes]
links = [{
    "source": src,
    "target": dest
} for (src, dest) in links]

graph = {'nodes': nodes, 'links': list(links)}

# print(nodes)
print(len(nodes))
with open(f'{root_term}.json', 'w') as outfile:
    json.dump(graph, outfile)

print(f"Runs in: {timer}")
