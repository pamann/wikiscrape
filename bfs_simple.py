from pywikiapi import wikipedia as pywiki
import wikipedia
import time
import json
from collections import Counter
# import concurrent
from concurrent.futures import ThreadPoolExecutor
from concurrent import futures
from multiprocessing import Pool
import multiprocessing as mp
from multiprocessing import Queue

nodes = set()
links = set()
root_term = "Halloween"
site = pywiki('en')
pool = ThreadPoolExecutor(8) # 8 threads, adjust to taste and # of cores
jobs = []

def query_wiki(ttls):
    global site
    query = site.query(titles=ttls, format="json", pllimit="max", lhlimit="max", prop=["links", "linkshere"], redirects=True)
    return query

def process_comp_jobs(tt_page_s):
    print(tt_page_s)
    if 'links' in tt_page_s and 'linkshere' in tt_page_s:
        l = [v.title for v in tt_page_s.links]
        lh = [v.title for v in tt_page_s.linkshere]
        lset = set(l)
        lhset = set(lh)
        tt_bidi_links = lset.intersection(lhset)
        # print(f"Links: {len(l)}, lset: {len(lset)}")
        # print(f"Links here: {len(lh)}, lhset: {len(lhset)}")
        # print(f"Bidi links: {len(tt_bidi_links)}")
        aggregate_nodes(tt_bidi_links, 1)
        aggregate_links(tt_page_s.title, tt_bidi_links) 

def fetch_links(root_term):
    global jobs
    search_r = wikipedia.search(root_term)
    root = wikipedia.page(search_r[0])
    root_id = root.pageid
    count = 0
    aggregate_nodes([root_term], 3)
    for page in query_wiki(root_term):
        page = page.pages[0]
        gen = []
        sub_nodes = []
        if 'links' in page:
            l = [v.title for v in page.links]
            lh = [v.title for v in page.linkshere]
            olink_set = set(l)
            ilink_set = set(lh)
            bidi_links = [s.replace("'", "") for s in list(olink_set & ilink_set)]
            aggregate_links(root_term, bidi_links[0:50])
            aggregate_nodes(bidi_links, 2) # bidi links from root_term
            with ThreadPoolExecutor(8) as executor: # start threaded bidi links of second tier
                for bidi_link in bidi_links:
                    jobs.append(executor.submit(query_wiki, bidi_link))
                # print(list(futures.as_completed(jobs)))
                # queue = Queue(list(futures.as_completed(jobs)))

                pool = Pool(processes=50)
                [pool.apply_async(process_comp_jobs) # num_to_add is passed as an argument
                    for res in futures.as_completed(jobs)]
                pool.close()
                pool.terminate()
                pool.join()


                # with Pool(5) as p:
                #     p.map(process_comp_jobs, queue)
                # for job in futures.as_completed(jobs):
                #     # Read result from future
                #     result = job.result()
                #     # print(result)
                #     if result:
                #         for tt_page in result:
                #             with ThreadPoolExecutor(8) as executor:
                #                 for tt_page_s in tt_page.pages:
                #                     jobs.append(executor.submit(process_comp_jobs, tt_page_s))
        else: 
            break

def aggregate_links(nodeid, res):
    global links
    obj = [(nodeid, link_dest) for link_dest in res]
    links = links.union(set(obj))

def aggregate_nodes(n_list, v):
    global nodes
    obj = set([(node, v) for node in n_list])
    nodes = nodes.union(set(obj))

start_time = time.time()
fetch_links(root_term)
timer = time.time() - start_time

# unpack sets of tuples into lists of dicts
nodes = [{
    "name": name,
    "val": val
} for (name, val) in nodes]
links = [{
    "source": src,
    "target": dest
} for (src, dest) in links]

graph = {'nodes': nodes, 'links': list(links)}

with open(f'{root_term}.json', 'w') as outfile:
    json.dump(graph, outfile)

print(f"Runs in: {timer}")
