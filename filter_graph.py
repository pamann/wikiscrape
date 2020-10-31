import json

INFILE_NAME = "full_beatles"
NUM_NODES = 15
OUTFILE_NAME = "Beatles" + str(NUM_NODES)

high_value = set()
final_nodes = []
final_links = []
with open('graphs/' + INFILE_NAME + '.json') as f:
    objects = json.loads(f.read())
    nodes = objects['nodes']
    links = objects['links']
    i = 0

    nodes.sort(key=lambda x: x["value"])
    final_nodes = nodes[len(nodes) - NUM_NODES: len(nodes)]

    total_links = 0
    for node in final_nodes:
        total_links += node['value']
        high_value.add(node['id'])

    for node in final_nodes:
        node['value'] /= total_links

    for link in links:
        if link['source'] in high_value:
            if link['target'] in high_value:
                final_links.append(link)

objects = {'nodes': final_nodes, 'links': final_links}

test_set = set()
for link in final_links:
    if link['source'] + link['target'] in test_set:
        print(link['source'] + link['target'])
    else:
        test_set.add(link['source'] + link['target'])


with open('graphs/' + OUTFILE_NAME +'.json', 'w+') as f:
    json.dump(objects, f)

