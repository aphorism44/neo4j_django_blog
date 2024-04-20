from neo4j import GraphDatabase
from decouple import config


class Neo4jCRUDOperations:
    def __init__(self):
        #TODO - make these functions take in username for multiple users
        # in future, use this when a user is created; for demo run this;
        # CREATE (u:User {email: 'd-jesse@comcast.net', password: 'password',created_at: TIMESTAMP()})-[:HAS_ACCOUNT]->(a:Account {created_at: TIMESTAMP()})-[:HAS_ENTRY]->(e:Entry{created_at: TIMESTAMP()}) RETURN e
        self.active = True
    
    def connect(self):
        self._driver = GraphDatabase.driver(config('LOCAL_BOLT_URI')
                                            , auth=(config('LOCAL_NEO4J_USERNAME')
                                            , config('LOCAL_NEO4J_PASSWORD')))

    def close(self):
        if self._driver is not None:
            self._driver.close()
    
    def get_latest_entry(self, email):
        with self._driver.session() as session:
            try:
                result = session.execute_read(self._get_latest_entry, email)
            except Exception as e:
                print(e)
                return None
            if result:
                return result[0]['e'], result[0]['latest_entry_id']
            else:
                return None
    
    def get_first_entry(self, email):
        with self._driver.session() as session:
            try:
                result = session.execute_read(self._get_first_entry, email)
            except Exception as e:
                print(e)
                return None
            if result:
                return result[0]['e'], result[0]['first_entry_id']
            else:
                return None
    
    def get_entry_by_id(self, entry_id):
        with self._driver.session() as session:
            try:
                result = session.execute_read(self._get_entry_by_id, entry_id)
            except Exception as e:
                print(e)
                return None
            if result:
                return result[0]['e'], result[0]['latest_entry_id']
            else:
                return None
    
    def create_empty_entry(self, email):
        with self._driver.session() as session:
            try:
                result = session.execute_write(self._create_empty_entry, email)
            except Exception as e:
                print(e)
                return None
            if result:
                return result[0]['new_entry_id']
            return None
    
    def update_entry(self, entry_id, text):
        with self._driver.session() as session:
            if entry_id is None:
                return None
            try:
                result = session.execute_write(self._update_entry, entry_id, text)
            except Exception as e:
                print(e)
                return None
            if result:
                return result[0]['e']
            return None
    
    def link_entry_chain(self, entry_id_from, entry_id_to):
        with self._driver.session() as session:
            if entry_id_from is None or entry_id_to is None:
                return None
            try:
                result = session.execute_write(self._link_entry_chain, entry_id_from, entry_id_to)
            except Exception as e:
                print(e)
                return None
            if result:
                return result[0]['to'], result[0]['from']
            else:
                return None
    
    def get_next_entry(self, email, entry_id):
        with self._driver.session() as session:
            if email is None or entry_id is None:
                return None
            try:
                result = session.execute_read(self._get_next_entry, email, entry_id)
            except Exception as e:
                print(e)
                return None
            if result:
                return result[0]['e2'], result[0]['next_id'] 
            else:
                return None
        
    def get_previous_entry(self, email, entry_id):
        with self._driver.session() as session:
            if email is None or entry_id is None:
                return None
            try:
               result = session.execute_read(self._get_previous_entry, email, entry_id)
            except Exception as e:
                print(e)
                return None
            if result:
                return result[0]['e2'], result[0]['previous_id']
            else:
                return None
    
    def get_all_entries(self, email):
        with self._driver.session() as session:
            if email is None:
                return None
            try:
                results = session.execute_read(self._get_all_entries, email)
            except Exception as e:
                print(e)
                return None
            if results:
                return results
            return None
        
    def add_keyword(self, email, keyword):
        with self._driver.session() as session:
            if email is None or keyword is None:
                return None
            try:
                result = session.execute_write(self._add_keyword, email, keyword)
            except Exception as e:
                print(e)
                return None
            if result:
                return result[0]['k'], result[0]['keyword_id']
            return None

    def attach_keyword_to_entry(self, email, keyword, phrase, entry_id):
        with self._driver.session() as session:
            if email is None or keyword is None or phrase is None or entry_id is None:
                return None
            try:
                result = session.execute_write(self._attach_keyword_to_entry, email, keyword, phrase, entry_id)
            except Exception as e:
                print(e)
                return None
            if result:
                return result[0]['k'], result[0]['keyword_id']
            return None
    
    def get_navigation_information(self, email):
        with self._driver.session() as session:
            if email is None:
                return None
            try:
                results = session.execute_read(self._get_navigation_information, email)
            except Exception as e:
                print(e)
                return None
            if results:
                return results
            return None

    def get_keyword(self, email, keyword):
        with self._driver.session() as session:
            if email is None or keyword is None:
                return None
            try:
                result = session.execute_read(self._get_keyword, email, keyword)
            except Exception as e:
                print(e)
                return None
            if result:
                return result[0]['k'], result[0]['keyword_id'] 
            else:
                return None

    def get_all_keywords(self, email):
        with self._driver.session() as session:
            if email is None:
                return None
            try:
                results = session.execute_read(self._get_all_keywords, email)
            except Exception as e:
                print(e)
                return None
            if results:
                return results
            return None

    def get_all_entry_keywords(self, email, entry_id):
        with self._driver.session() as session:
            if email is None or entry_id is None:
                return None
            try:
                results = session.execute_read(self._get_all_entry_keywords, email, entry_id)
            except Exception as e:
                print(e)
                return None
            if results:
                return results
            return None
    
    def get_all_keyword_entries(self, email, keyword):
        with self._driver.session() as session:
            if email is None or keyword is None:
                return None
            try:
                results = session.execute_read(self._get_all_keyword_entries, email, keyword)
            except Exception as e:
                print(e)
                return None
            if results:
                return results
            return None

    @staticmethod
    def _get_first_entry(tx, email):
        result = tx.run("MATCH (u:User {email: $email})-[:HAS_ACCOUNT]->(a:Account)-[:HAS_ENTRY]->(e:Entry) WITH e ORDER BY e.created_at LIMIT 1 RETURN e, elementId(e) as first_entry_id", email=email)
        return result.data()

    @staticmethod
    def _get_latest_entry(tx, email):
        result = tx.run("MATCH (u:User {email: $email})-[:HAS_ACCOUNT]->(a:Account)-[:HAS_ENTRY]->(e:Entry) WITH e ORDER BY e.created_at DESC LIMIT 1 RETURN e, elementId(e) as latest_entry_id", email=email)
        return result.data()
    
    @staticmethod
    def _get_entry_by_id(tx, entry_id):
        result = tx.run("MATCH (e:Entry) WHERE elementId(e) = $entry_id RETURN e, elementId(e) as latest_entry_id", entry_id=entry_id)
        return result.data()
    
    @staticmethod
    def _create_empty_entry(tx, email):
        result = tx.run("MATCH (u:User {email: $email})-[:HAS_ACCOUNT]->(a:Account) CREATE (a)-[:HAS_ENTRY]->(e:Entry {created_at: TIMESTAMP()}) RETURN elementId(e) AS new_entry_id", email=email)
        return result.data()
    
    @staticmethod
    def _update_entry(tx, entry_id, text):
        result = tx.run("MATCH (e:Entry) WHERE elementId(e) = $entry_id SET e.text = $text RETURN e", entry_id=entry_id, text=text)
        return result.data()

    @staticmethod
    def _link_entry_chain(tx, entry_id_from, entry_id_to):
        result = tx.run("MATCH (from:Entry), (to:Entry) WHERE elementId(from) = $entry_id_from AND elementId(to) = $entry_id_to CREATE (from)-[:HAS_NEXT_ENTRY]->(to) RETURN to, from", entry_id_from=entry_id_from, entry_id_to=entry_id_to)
        return result.data()
    
    @staticmethod
    def _get_next_entry(tx, email, entry_id):
        result = tx.run("MATCH (u:User {email: $email})-[:HAS_ACCOUNT]->(a:Account)-[:HAS_ENTRY]->(e1:Entry)-[:HAS_NEXT_ENTRY]->(e2:Entry) WHERE elementId(e1) = $entry_id  RETURN e2, elementId(e2) AS next_id", email=email, entry_id=entry_id)
        return result.data()
    
    @staticmethod
    def _get_previous_entry(tx, email, entry_id):
        result = tx.run("MATCH (u:User {email: $email})-[:HAS_ACCOUNT]->(a:Account)-[:HAS_ENTRY]->(e1:Entry)<-[:HAS_NEXT_ENTRY]-(e2:Entry) WHERE elementId(e1) = $entry_id  RETURN e2, elementId(e2) AS previous_id", email=email, entry_id=entry_id)
        return result.data()

    @staticmethod
    def _get_all_entries(tx, email):
        result = tx.run("MATCH (u:User {email: $email})-[:HAS_ACCOUNT]->(a:Account)-[:HAS_ENTRY]->(e:Entry) WITH e ORDER BY e.created_at DESC RETURN e, elementId(e) AS entry_id", email=email)
        return result.data()
    
    @staticmethod
    def _add_keyword(tx, email, keyword):
        result = tx.run("MATCH (u:User {email: $email})-[:HAS_ACCOUNT]->(a:Account) MERGE (a)-[r:HAS_KEYWORD]->(k:Keyword {keyword: $keyword, user: $email, created_at: TIMESTAMP()}) RETURN k, elementId(k) AS keyword_id", email=email, keyword=keyword)
        return result.data()
    
    @staticmethod
    def _attach_keyword_to_entry(tx, email, entry_id, phrase, keyword):
        result = tx.run("MATCH (e:Entry), (k:Keyword{user:$email, keyword:$keyword}) WHERE elementId(e) = $entry_id MERGE (k)-[:IN_ENTRY {phrase: $phrase }]->(e) RETURN k, elementId(k) AS keyword_id", email=email, entry_id=entry_id, phrase=phrase, keyword=keyword)
        return result.data()
    
    @staticmethod
    def _get_navigation_information(tx, email):
        result = tx.run(" MATCH (k:Keyword{user:email})-[r:IN_ENTRY]->(e:Entry) RETURN k.keyword as keyword, r.phrase as phrase, elementId(e) AS entry_id ORDER BY k.keyword", email=email)
        return result.data()
    
    @staticmethod
    def _get_keyword(tx, email, keyword):
        result = tx.run(" MATCH (k:Keyword{user:$email, keyword:$keyword}) RETURN k, elementId(k) as as keyword_id", email=email,keyword=keyword)
        return result.data()
    
    @staticmethod
    def _get_all_keywords(tx, email):
        result = tx.run(" MATCH (k:Keyword{user:$email}) RETURN k.keyword as keyword ORDER BY keyword", email=email)
        return result.data()
    
    @staticmethod
    def _get_all_entry_keywords(tx, email, entry_id):
        result = tx.run("MATCH (e:Entry)<-[r:IN_ENTRY]-(k:Keyword{user:$email}) WHERE elementId(e) = $entry_id RETURN k.keyword AS keyword, elementId(k) AS keyword_id", email=email, entry_id=entry_id)
        return result.data()
    
    @staticmethod
    def _get_all_keyword_entries(tx, email, keyword):
        result = tx.run("MATCH (k:Keyword {keyword:$keyword, user: $email})-[r:IN_ENTRY]->(e:Entry) RETURN r.phrase AS phrase, elementId(e) AS entry_id", email=email, keyword=keyword)
        return result.data()
    
    
