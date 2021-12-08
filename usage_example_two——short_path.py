from application import Neo4jClient

neo4j_client = Neo4jClient("neo4j://localhost:7687", "neo4j", "admin123")

GRAPH = {
    'world': ['floor1-room1', 'floor1-stair3', 'floor1-stair4'],
    'floor1-room1': ['floor1-stair1', 'world'],
    'floor1-stair1': ['floor1-room1', 'floor1-stair1-platform1'],
    'floor1-stair1-platform1': ['floor1-stair1', 'floor1-stair2'],
    'floor1-stair2': ['floor1-stair1-platform1', 'floor2-platform3'],
    'floor1-stair3': ['world', 'floor2-platform2'],
    'floor1-stair4': ['world', 'floor2-platform1'],
    'floor2-platform1': ['world', 'floor1-stair4', 'floor2-room2', 'floor2-platform3'],
    'floor2-platform2': ['world', 'floor1-stair3', 'floor2-stair5', 'floor2-room2', 'floor2-platform3'],
    'floor2-platform3': ['world', 'floor2-platform1', 'floor2-platform2', 'floor2-room2', 'floor1-stair2',
                         'floor1-room1'],
    'floor2-room2': ['floor2-platform1', 'floor2-platform3', 'floor2-platform2', 'floor1-stair4'],
    'floor2-stair5': ['floor2-platform2', 'floor3-platform4'],
    'floor3-platform4': ['floor2-stair5', 'world']
}

list_path = ['world',
             'floor1-room1', 'floor1-stair1', 'floor1-stair1-platform1', 'floor1-stair2',
             'floor2-platform3', 'floor2-platform1', 'floor2-room3', 'floor2-platform2', 'floor2-stair5',
             'floor3-platform4']

for node in list_path:
    label = node if len(node) < 6 else node[:6]
    neo4j_client.create_node(label, node)

for k, v in GRAPH.items():
    node1 = k
    if k == "world":
        label1 = "world"
    else:
        label1 = k[:6]
    for node2 in v:
        if node2 == "world":
            label2 = "world"
        else:
            label2 = node2[:6]
        neo4j_client.create_relationship(label1,
                                         node1,
                                         label2,
                                         node2,
                                         "JUNCTION",
                                         {"cost": 5}, )

path_list = neo4j_client.query_short_path("world", "world", "floor3", "floor3-platform4",
                                          "['world', 'floor1', 'floor2', 'floor3']", 'JUNCTION')

print(path_list)

neo4j_client.close()
