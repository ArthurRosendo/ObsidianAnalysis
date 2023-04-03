import os.path
from collections import deque
from pathlib import Path

import obsidiantools.api as otools

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    string_path = input("Vault path:")

    string_path = string_path.strip(r'"')
    path_vault = Path(string_path)

    if not (os.path.exists(path_vault)):
        print("File doesn't exists")
        exit()
    else:
        print("File exists.")

    vault = otools.Vault(path_vault).connect().gather()
    graph = vault.graph

    # Remove nodes with tags
    string_tags_to_remove = input("Tags to be removed, separated by commas: ")
    if string_tags_to_remove:
        tags_to_remove = string_tags_to_remove.split(',')

        nodes_to_remove = list()
        for node in graph:
            try:
                if any(x in tags_to_remove for x in vault.get_tags(node)):
                    nodes_to_remove.append(node)
            except ValueError:
                # Node likely doesn't exist as a note, meaning it is not possible for it to have tags
                print(
                    "A note has an outgoing link that doesn't exists as a note, tags can't be evaluated for something that doesn't exists. Rest of the code may break as no intensive test was done with missing nodes.")
                continue
        for x in nodes_to_remove:
            graph.remove_node(x)

    # NOTE: The definition of:
    # "incoming" = Backlinks, nodes that point to this node
    # "outgoing" = Outlinks, nodes that this points to
    bilateral = dict(list())
    outgoing_unilateral = dict(list())
    incoming_unilateral = dict(list())
    for node1 in graph.nodes():
        for node2 in graph.nodes():
            # Bilateral
            if graph.has_edge(node1, node2) and graph.has_edge(node2, node1):
                if node2 not in bilateral.keys() or bilateral[node2] is None:
                    bilateral[node2] = list()
                bilateral[node2].append(node1)
            else:
                if graph.has_edge(node2, node1):
                    if node2 not in outgoing_unilateral.keys() or outgoing_unilateral[node2] is None:
                        outgoing_unilateral[node2] = list()
                    outgoing_unilateral[node2].append(node1)
                else:
                    if graph.has_edge(node1, node2):
                        if node2 not in incoming_unilateral.keys() or incoming_unilateral[node2] is None:
                            incoming_unilateral[node2] = list()
                        incoming_unilateral[node2].append(node1)


    # Source: https://stackoverflow.com/questions/1495510/combining-dictionaries-of-lists-in-python
    def merge_dols(dol1, dol2):
        keys = set(dol1).union(dol2)
        no = []
        return dict((k, dol1.get(k, no) + dol2.get(k, no)) for k in keys)


    # Bilateral relationships
    # TODO: Double check if copy() is necessary here, it probably isn't.
    nodes_most_outgoing = merge_dols(outgoing_unilateral.copy(), bilateral.copy())
    nodes_most_incoming = merge_dols(incoming_unilateral.copy(), bilateral.copy())

    # Print
    mylist = list(bilateral.items())
    mylist = [[mylist[x][0], len(mylist[x][1])] for x in range(0, len(mylist))]
    print("Bilateral: " + str(sorted(mylist, key=lambda x: x[1], reverse=True)))
    mylist = list(outgoing_unilateral.items())
    mylist = [[mylist[x][0], len(mylist[x][1])] for x in range(0, len(mylist))]
    print("Unilateral outgoing: " + str(sorted(mylist, key=lambda x: x[1], reverse=True)))
    mylist = list(incoming_unilateral.items())
    mylist = [[mylist[x][0], len(mylist[x][1])] for x in range(0, len(mylist))]
    print("Unilateral incoming: " + str(sorted(mylist, key=lambda x: x[1], reverse=True)))
    mylist = list(nodes_most_outgoing.items())
    mylist = [[mylist[x][0], len(mylist[x][1])] for x in range(0, len(mylist))]
    print("Outgoing (incld. bilateral): " + str(sorted(mylist, key=lambda x: x[1], reverse=True)))
    mylist = list(nodes_most_incoming.items())
    mylist = [[mylist[x][0], len(mylist[x][1])] for x in range(0, len(mylist))]
    print("Incoming (incld. bilateral): " + str(sorted(mylist, key=lambda x: x[1], reverse=True)))
