from pywikiapi import wikipedia as pywiki
import wikipedia
import time
import json
from collections import Counter

nodes = set()
links = set()
root_term = "Halloween"

def fetch_links(root_term):
    site = pywiki('en')
    search_r = wikipedia.search(root_term)
    root = wikipedia.page(search_r[0])
    root_id = root.pageid
    count = 0
    aggregate_nodes([root_term], 3)
    for page in site.query(titles=root_term, format="json", pllimit="max", lhlimit="max", prop=["links", "linkshere"], redirects=True):
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
            aggregate_nodes(bidi_links, 2)
            for bidi_link in bidi_links[0:50]:
                for tt_page in site.query(titles=bidi_link, format="json", pllimit="max", lhlimit="max", prop=["links", "linkshere"], redirects=True):
                    for tt_page_s in tt_page.pages:
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
                        else: 
                            break

        else: 
            break
        
def aggregate_links(nodeid, res):
    obj = [(nodeid, link_dest) for link_dest in res]
    links.union(set(obj))

def aggregate_nodes(n_list, v):
    obj = [(node, v) for node in n_list]
    nodes.union(set(obj))

start_time = time.time()
fetch_links(root_term)
timer = time.time() - start_time

graph = {'nodes': list(nodes), 'links': list(links)}

with open(f'{root_term}.json', 'w') as outfile:
    json.dump(graph, outfile)

print(f"Runs in: {timer}")
