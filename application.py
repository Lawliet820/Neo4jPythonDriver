from neo4j import GraphDatabase


class Neo4jClient:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # ====================创建命名节点====================
    def create_node(self, node_label, node_name):
        with self.driver.session() as session:
            session.write_transaction(self._create_node,
                                      node_label, node_name)

    @staticmethod
    def _create_node(tx, node_label, node_name):
        query = ("CREATE (a: %s { name: $node_name })"
                 % node_label)
        tx.run(query, node_name=node_name)

    # ====================为命名节点添加属性====================
    def create_property_for_node(self, node_label, node_name, property_dict):
        with self.driver.session() as session:
            node_id = session.write_transaction(self._query_node_id,
                                                node_label, node_name)
            for k, v in property_dict.items():
                session.write_transaction(self._create_property_for_node,
                                          node_id, node_label, k, v)

    @staticmethod
    def _create_property_for_node(tx, node_id, node_label, property_key, property_value):
        query = ("MATCH (a: %s) "
                 "WHERE id(a) = $id "
                 "SET a.%s = $property_value"
                 % (node_label,
                    property_key))
        tx.run(query, id=node_id, property_value=property_value)

    # ====================通用方法:查找节点id====================
    def query_node_id(self, node_label, node_name):
        with self.driver.session() as session:
            node_id = session.read_transaction(self._query_node_id, node_label, node_name)
        return node_id

    @staticmethod
    def _query_node_id(tx, node_label, node_name):
        query = ("MATCH (a: %s { name: $node_name }) "
                 "RETURN id(a) AS node_id"
                 % node_label)
        result = tx.run(query, node_name=node_name)
        record = result.single()
        return record["node_id"]

    # ====================创建关系====================
    def create_relationship(self,
                            node_1_label,
                            node_1_name,
                            node_2_label,
                            node_2_name,
                            relationship_type,
                            property_dict=None, ):
        with self.driver.session() as session:

            if not property_dict:
                session.write_transaction(self._create_relationship,
                                          node_1_label,
                                          node_1_name,
                                          node_2_label,
                                          node_2_name,
                                          relationship_type, )
            else:
                for k, v in property_dict.items():
                    session.write_transaction(self._create_relationship,
                                              node_1_label,
                                              node_1_name,
                                              node_2_label,
                                              node_2_name,
                                              relationship_type,
                                              k,
                                              v, )

    @staticmethod
    def _create_relationship(tx,
                             node_1_label,
                             node_1_name,
                             node_2_label,
                             node_2_name,
                             relationship_type,
                             property_key=None,
                             property_value=None, ):

        if not property_key:
            query = ("MATCH (a: %s {name: $node_1_name}), "
                     "(b: %s {name: $node_2_name}) "
                     "MERGE (a)-[: %s]->(b)"
                     % (node_1_label,
                        node_2_label,
                        relationship_type,))
            tx.run(query,
                   node_1_name=node_1_name,
                   node_2_name=node_2_name, )
        else:
            query = ("MATCH (a: %s {name: $node_1_name}), "
                     "(b: %s {name: $node_2_name}) "
                     "MERGE (a)-[: %s {%s: $property_value}]->(b)"
                     % (node_1_label,
                        node_2_label,
                        relationship_type,
                        property_key,))
            tx.run(query,
                   node_1_name=node_1_name,
                   node_2_name=node_2_name,
                   property_value=property_value)

    # ====================获取最短路径，要求图节点之间关系有方向，有cost属性====================
    def query_short_path(self,
                         start_node_label,
                         start_node_name,
                         end_node_label,
                         end_node_name,
                         node_label_list,
                         relationship_type,
                         relationship_properties='cost',
                         relationship_weight_property='cost', ):
        with self.driver.session() as session:
            path_list = session.read_transaction(self._query_short_path,
                                                 start_node_label,
                                                 start_node_name,
                                                 end_node_label,
                                                 end_node_name,
                                                 node_label_list,
                                                 relationship_type,
                                                 relationship_properties,
                                                 relationship_weight_property)
        return path_list

    @staticmethod
    def _query_short_path(tx,
                          start_node_label,
                          start_node_name,
                          end_node_label,
                          end_node_name,
                          node_label_list,
                          relationship_type,
                          relationship_properties,
                          relationship_weight_property):
        query = ("MATCH (start: %s {name: $start_node_name}), "
                 "(end: %s {name: $end_node_name}) "
                 "CALL gds.alpha.shortestPath.stream"
                 "("
                 "  {"
                 "    nodeProjection: %s,"
                 "    relationshipProjection: "
                 "    {"
                 "      ROAD: "
                 "      {"
                 "        type: $relationship_type,"
                 "        properties: $relationship_properties,"
                 "        orientation: 'NATURAL'"
                 "      }"
                 "    },"
                 "    startNode: start,"
                 "    endNode: end,"
                 "    relationshipWeightProperty: $relationship_weight_property"
                 "  }"
                 ") "
                 "YIELD nodeId, cost "
                 "RETURN gds.util.asNode(nodeId).name AS name"
                 % (start_node_label,
                    end_node_label,
                    node_label_list))
        result = tx.run(query,
                        start_node_name=start_node_name,
                        end_node_name=end_node_name,
                        relationship_type=relationship_type,
                        relationship_properties=relationship_properties,
                        relationship_weight_property=relationship_weight_property)
        path_list = [record["name"] for record in result]
        return path_list
