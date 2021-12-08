from application import Neo4jClient

# ====================创建neo4j终端app====================
neo4j_client = Neo4jClient("neo4j://localhost:7687", "neo4j", "admin123")
# ====================创建命名节点====================
neo4j_client.create_node("Person", "Shawn")
neo4j_client.create_node("Person", "John")
# ====================为命名节点添加属性====================
property_dict = {
    "kkk1": "vvv1",
    "kkk2": "vvv2",
}
neo4j_client.create_property_for_node("Person", "Shawn", property_dict)
# ====================创建关系,关系的属性为可选参数，可缺省====================
neo4j_client.create_relationship("Person",
                                 "Shawn",
                                 "Person",
                                 "John",
                                 "FRIENDS",
                                 {"since": 2012}, )
# ====================关闭====================
neo4j_client.close()
