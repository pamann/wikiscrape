from pywikiapi import wikipedia as pywiki
import wikipedia
import time
import json
from collections import Counter

nodes = []
links = []
root_term = "Halloween"

def fetch_links(root_term):
    site = pywiki('en')
    search_r = wikipedia.search(root_term)
    root = wikipedia.page(search_r[0])
    root_id = root.pageid
    count = 0
    for page in site.query(format="json", pllimit="max", titles=root_term, prop="links", redirects=True, plnamespace=0):
        page = page.pages[0]
        gen = []
        sub_nodes = []
        count += len(page.links)
        aggregate_links(root_term, page.links)
        nodes.append(root_term)
        for link in page.links:
            for page_2 in site.query(format="json", pllimit="max", titles=link.title, prop="links", redirects=True, plnamespace=0):
                if "links" in page_2.pages[0]:
                    scnd_l = page_2.pages[0].links
                    aggregate_links(link.title, scnd_l)
                    count += len(scnd_l)
                    nodes.append(link.title)
                    nodes.extend(list(l2.title for l2 in scnd_l))
        return count

def aggregate_links(node, res):
    obj = ({
        "source": node,
        "target": link_dest.title
    } for link_dest in res)
    links.extend(obj)

def count_nodes():
    counts = Counter(nodes)
    filtered_nodes = {k: c for k, c in counts.items() if c >= 20}
    filtered_counts = Counter(filtered_nodes)
    return (sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True), filtered_nodes)

start_time = time.time()
print(fetch_links(root_term))
timer = time.time() - start_time

(fnode_counts, fnodes) = count_nodes()

with open('{root_term}_links.json', 'w') as outfile:
    json.dump(links, outfile)

with open('{root_term}_nodes.json', 'w') as outfile:
    json.dump(nodes, outfile)

print(f"Number of nodes (pre-filter): {len(nodes)}")
print(f"Number of nodes (post-filter): {len(fnode_counts)}")
print(f"Runs in: {timer}")
