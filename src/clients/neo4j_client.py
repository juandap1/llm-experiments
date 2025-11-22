import os
from neo4j import GraphDatabase

class Neo4jClient:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://neo4j_graphdb:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password123")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_graph_data(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)-[r]->(m)
                RETURN n, r, m
                LIMIT 100
            """)
            nodes = {}
            edges = []
            
            for record in result:
                source = record["n"]
                target = record["m"]
                rel = record["r"]
                
                # Add nodes if not already added
                if source.element_id not in nodes:
                    nodes[source.element_id] = {
                        "id": source.element_id,
                        "labels": list(source.labels),
                        "properties": dict(source)
                    }
                
                if target.element_id not in nodes:
                    nodes[target.element_id] = {
                        "id": target.element_id,
                        "labels": list(target.labels),
                        "properties": dict(target)
                    }
                
                # Add edge
                edges.append({
                    "id": rel.element_id,
                    "source": source.element_id,
                    "target": target.element_id,
                    "type": rel.type,
                    "properties": dict(rel)
                })
                
            return {"nodes": list(nodes.values()), "edges": edges}
