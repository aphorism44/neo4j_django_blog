
Django + Neo4J Driver

This app's functionality was taken from the "polls' tutorial at the official site:

https://docs.djangoproject.com/en/4.2/intro/tutorial01/

However, it was adapted to use _only_ the Neo4J Driver (and not other derivative libraries like neomodel):

https://neo4j.com/docs/api/python-driver/current/index.html

The graph-edge model is a straightforward modelling of the relational tables of the original tutorial.

This was a development-only POC and NOT for production.


# django setup
python -m django startproject blog_engine
# create an app
python manage.py startapp blog

python -m venv .venv
# virtual start
.venv/scripts/activate

# install reqiurements
python3 -m pip install -r requirements.txt

python manage.py runserver
# (http://localhost:8000/polls/)

# You cannot install anything beyond the neo4j python driver in Python 12+. #

# Necessary pre-use Neo4j DB setup
CREATE CONSTRAINT FOR (u:User) REQUIRE u.email IS UNIQUE;
# in future, use this when a user is created
CREATE (u:User {email: 'd-jesse@comcast.net', password: 'password', created_at: TIMESTAMP()})-[:HAS_ACCOUNT]->(a:Account {created_at: TIMESTAMP()})-[:HAS_ENTRY]->(e:Entry{created_at: TIMESTAMP()})



# Useful Cipher
# test connecion
MATCH (n) RETURN count(n) as node_count
# get whole graph
MATCH (n) RETURN n
# erase whole graph
MATCH (n) DETACH DELETE n

# useful command lines
rm -r -fo .git
python manage.py runserver