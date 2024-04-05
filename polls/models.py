from neo4j import GraphDatabase
from decouple import config


class Neo4jCRUDOperations:
    def __init__(self):
        #TODO - make these functions take in username for multiple users
        # in future, use this when a user is created; for demo run this;
        # CREATE (u:User {email: 'd-jesse@comcast.net', password: 'password',created_at: TIMESTAMP()})-[:HAS_ACCOUNT]->(a:Account {created_at: TIMESTAMP()})-[:HAS_ENTRY]->(e:Entry{created_at: TIMESTAMP()}) RETURN e
        self.active = True
    
    def connect(self):
        print(config('LOCAL_BOLT_URI'))
        print(config('LOCAL_NEO4J_USERNAME'))
        print(config('LOCAL_NEO4J_PASSWORD'))
        self._driver = GraphDatabase.driver(config('LOCAL_BOLT_URI')
                                            , auth=(config('LOCAL_NEO4J_USERNAME')
                                            , config('LOCAL_NEO4J_PASSWORD')))

    def close(self):
        if self._driver is not None:
            self._driver.close()
    
    def get_latest_entry(self, email):
        with self._driver.session() as session:
            result = session.read_transaction(self._get_latest_entry, email)
            if result:
                return result[0]['e']
            else:
                return None
    
    def create_empty_entry(self, email):
        with self._driver.session() as session:
            result = session.write_transaction(self._create_empty_entry, email)
            if result:
                return result[0]['new_entry_id']
            return None
    
    def update_entry(self, entry_id, text):
        with self._driver.session() as session:
            if entry_id is None:
                return None
            result = session.write_transaction(self._update_entry, entry_id, text)
            if result:
                return result[0]['q']
            return None
    
    def link_entry_chain(self, entry_id_from, entry_id_to):
        with self._driver.session() as session:
            if entry_id_from is None or entry_id_to is None:
                return None
            result = session.write_transaction(self._link_entry_chain, entry_id_from, entry_id_to)
            if result:
                return result[0]['entry_id_to']
            else:
                return None
    
    def get_next_entry(self, email, entry_id):
        with self._driver.session() as session:
            if email is None or entry_id is None:
                return None
        result = session.write_transaction(self._get_next_entry, email, entry_id)
        if result:
            return result[0]['e']
        else:
            return None
        
    def get_previous_entry(self, email, entry_id):
        with self._driver.session() as session:
            if email is None or entry_id is None:
                return None
        result = session.write_transaction(self._get_previous_entry, email, entry_id)
        if result:
            return result[0]['e']
        else:
            return None
    
    def get_all_entries(self, email):
        with self._driver.session() as session:
            if email is None:
                return None
            results = session.write_transaction(self._get_all_entries, email)
            if results:
                return results[0]
            return None
    
    @staticmethod
    def _get_latest_entry(tx, email):
        result = tx.run("MATCH (u:User {email: $email})-[:HAS_ACCOUNT]->(a:Account)-[:HAS_ENTRY]->(e:Entry) WITH e ORDER BY e.created_at DESC LIMIT 1 RETURN e", email=email)
        return result.data()
    
    @staticmethod
    def _create_empty_entry(tx, email):
        result = tx.run("MATCH (u:User {email: $email})-[:HAS_ACCOUNT]->(a:Account) CREATE (a)-[:HAS_ENTRY]->(e:Entry {created_at: TIMESTAMP()}) RETURN ID(e) AS new_entry_id", email=email)
        return result.data()
    
    @staticmethod
    def _update_entry(tx, entry_id, text):
        result = tx.run("MATCH (e:Entry) WHERE ID(e) = $entry_id SET e.text = $text RETURN e", entry_id=entry_id, text=text)
        return result.data()

    
    @staticmethod
    def _link_entry_chain(tx, entry_id_from, entry_id_to):
        result = tx.run("MATCH (from:Entry), (to:Entry) WHERE ID(from) = $entry_id_from AND ID(to) = $entry_id_to CREATE (from)-[:HAS_NEXT_ENTRY]->(to) RETURN to, from", entry_id_from=entry_id_from, entry_id_to=entry_id_to)
        return result.data()
    
    @staticmethod
    def _get_next_entry(tx, email, entry_id):
        result = tx.run("MATCH (u:User {email: $email})-[:HAS_ACCOUNT]->(a:Account)-[:HAS_ENTRY]->(e1:Entry)-[:HAS_NEXT_ENTRY]->(e2:Entry) WHERE ID(e1) = $entry_id  RETURN e2", email=email, entry_id=entry_id)
        return result.data()
    
    @staticmethod
    def _get_previous_entry(tx, email, entry_id):
        result = tx.run("MATCH (u:User {email: $email})-[:HAS_ACCOUNT]->(a:Account)-[:HAS_ENTRY]->(e1:Entry)<-[:HAS_NEXT_ENTRY]-(e2:Entry) WHERE ID(e1) = $entry_id  RETURN e2", email=email, entry_id=entry_id)
        return result.data()

    @staticmethod
    def _get_all_entries(tx, email):
        result = tx.run("MATCH (u:User {email: $email})-[:HAS_ACCOUNT]->(a:Account)-[:HAS_ENTRY]->(e:Entry) WITH e ORDER BY e.created_at DESC RETURN e", email=email)
        return result.data()
    
    