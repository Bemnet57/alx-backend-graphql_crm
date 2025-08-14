#For projects implementing GraphQL 
# APIs with libraries like Graphene-Django, schema.py is where the GraphQL schema is defined, 
# including types, queries, mutations, and relationships.

import graphene

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

schema = graphene.Schema(query=Query)
