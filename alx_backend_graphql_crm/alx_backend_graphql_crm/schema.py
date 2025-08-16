#For projects implementing GraphQL 
# APIs with libraries like Graphene-Django, schema.py is where the GraphQL schema is defined, 
# including types, queries, mutations, and relationships.

import graphene
from crm import schema as crm_schema

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

class Mutation(crm_schema.Mutation, graphene.ObjectType):
    pass
    

#schema = graphene.Schema(query=Query)
schema = graphene.Schema(query=Query, mutation=Mutation)