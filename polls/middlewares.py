from .models import Neo4jCRUDOperations

class Neo4jMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.neo4j_crud = Neo4jCRUDOperations()
        self.neo4j_crud.connect()

    def __call__(self, request):
        request.neo4j_crud = self.neo4j_crud
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        self.neo4j_crud.close()

    def process_template_response(self, request, response):
        self.neo4j_crud.close()
        return response
