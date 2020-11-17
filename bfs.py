from pywikiapi import wikipedia as pywiki
import wikipedia
import time
import json
from collections import Counter

# TODO: switch query root term to be generator for extracts from linked pages instead of filtering by hitting the api every time

nodes = []
links = []
root_term = "Halloween"


def parse_text(l):
    print(l)
    # site = pywiki('en')

    # ext = wikipedia.search(l.title)[0]
    # https://en.wikipedia.org/w/api.php?action=opensearch&search=bee&limit=1&format=json
    # for page in site.query(titles=ext, format="json", prop="extracts"):
        # print(root_term in page.pages[0].extract)
    # return root_term in page.pages[0].extract

def fetch_links(root_term):
    site = pywiki('en')
    search_r = wikipedia.search(root_term)
    root = wikipedia.page(search_r[0])
    root_id = root.pageid
    count = 0
    for page in site.query(generator="alllinks", galtitle=root_term, format="json", pllimit="max", lhlimit="max", prop=["links", "extracts"], redirects=True):
        page = page.pages[0]
        gen = []
        sub_nodes = []
        count += len(page.links)
        # print(page)
        links = page.links
        print(links[0])
        ext = page.extract
        res = {links[i].title: ext[i] for i in range(len(links))} 
        print(res)
        # links = {links: p for links, p in page if root_term in p.extract}
        # links = list(filter(parse_text, page.values()))
        aggregate_links(root_term, page.links)
        nodes.append(root_term)
        for tier_s in site.query(format="json", pllimit="max", titles=links, prop="links", redirects=True, plnamespace=0):
            print(tier_s)
            if "links" in tier_s.pages[0]:
                scnd_l = tier_s.pages[0].links
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

# with open('{root_term}_links.json', 'w') as outfile:
#     json.dump(links, outfile)

# with open('{root_term}_nodes.json', 'w') as outfile:
#     json.dump(nodes, outfile)

print(f"Number of nodes (pre-filter): {len(nodes)}")
print(f"Number of nodes (post-filter): {len(fnode_counts)}")
print(f"Runs in: {timer}")
