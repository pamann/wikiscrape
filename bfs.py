from pywikiapi import wikipedia as pywiki
import wikipedia
import time

root_term = "Homer Simpson"
nodes = []
links = []

def fetch_links(root_term):
    site = pywiki('en')
    search_r = wikipedia.search(root_term)
    root = wikipedia.page(search_r[0])
    root_id = root.pageid
    count = 0
    for page in site.query(generator="links", titles=root_term, format="json", prop=["links", "pageprops"], gpllimit="max"):
        count += 1
        if count == 2:
            break
        sub_nodes = []
        link_data = list({ "meta": {"id": (page.pageid if "pageid" in page else "null") , "name": page.title}} for page in page.pages)
        res = {"meta": { "name": (page.title if "title" in page else "null"), "id": (page.pageid if "pageid" in page else "null") }, "links": link_data}            
        print(res)

def aggregate_links(links, node):
    links.append({node: links})

start_time = time.time()
fetch_links("Halloween")
timer = time.time() - start_time

print(nodes)
print(len(nodes))
print(f"Runs in: {timer}")

