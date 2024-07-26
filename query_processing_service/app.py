from flask import Flask, request, jsonify
from langchain_community.llms import Ollama 
from langchain_core.prompts import PromptTemplate
from langchain_community.graphs import Neo4jGraph
import ast
import pandas as pd
# from neo4j import GraphDatabase  # Add this import 
from py2neo import Graph, Node, Relationship
from langchain_google_genai import ChatGoogleGenerativeAI
import os

app = Flask(__name__)

neo4j_url = 'neo4j://neo4j:7687'
neo4j_username = 'neo4j'
neo4j_password = '12345678'

graph2 = Graph(neo4j_url, auth=(neo4j_username, neo4j_password))
# llm = OpenAI(openai_api_key=openai_api_key, temperature=0.0) 
# llm = Ollama(model="llama3", base_url="http://query_processing_service:11434") 
os.environ["GOOGLE_API_KEY"] ='___'
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

refined_user_query_neo4j = """Your task is to refine the user query for spelling mistakes and syntax errors according to the Table Description part below. Do not add any information on your own in the refined query, just check for spellings and correct them according to the words in Table Description given below.

The user query to be refined is: {user_input}

Table Description for Correct syntax of Cypher query to be generated: 
{df_string}

Output Format:
The output must be a simple sentence made in accordance to the user query with correct syntax according to the given words.
If the user query is already having correct syntax according to the Table Description, then just return the user query itself without any refinement and do not provide any extra sentence.
Do not provide any extra sentence.
"""

pr2 = """
Your task is to create a Cypher Query to be run in Neo4j. 
Refer this table description and given examples to generate Cypher queries with appropriate syntax. This table also contains source node, relation, target node. Each row is a relation between From Asset and To Asset.

Table Description for Correct syntax of Cypher query to be generated:
{df_string}

Consider these Given examples for reference about how the syntax of the cypher query should be. Always use syntax n.name="node_name" for node_name.
Given examples:
Example 1:
    user_query: "Give all the nodes that are connected to node with name "Alice"",
    cypher_generated: MATCH (alice:Node {{ name: 'Alice' }})-[r]-(other:Node) RETURN other.name AS ConnectedNodeName, type(r) AS RelationshipType;
Example 2:
    user_query: "Give any information about node_name.",
    cypher_generated: MATCH (n:Node)-[r]->(m:Node) RETURN n.name AS Source_Node, type(r) AS Relationship, m.name AS Target_Node;
Example 3:
    user_query: "Are Alice and Bob connected?",
    cypher_generated: MATCH (a:Node {{name: 'Alice'}}), (b:Node {{name: 'Bob'}}) RETURN EXISTS((a)-[*]-(b)) AS AreConnected;

*Notice*: The information about the entity that user_query is asking for exists in the nodes that are connected to the entity's node:
Example 4:
    user_query: "How old is Alice?",
    cypher_generated: MATCH (a:Node {{name: 'Alice'}})-[r:age]->(age) RETURN age.name AS Age;

Generate the Cypher query for the user_query.
The user_query is : {user_input}
*Attention*: Only give the generated Cypher query as output with no extra word or information.
"""

NLP = """
Given a user_query: 
{user_input} 

and its output response: 
{response0}

Use the user_query and its output response given above to generate output in simple English without missing any point.
"""

def shubhNeo4j(user_query):
    df_string = f"""
    Source_Node Relationship    Target_Node
    0       Alice           is         Lawyer
    1       Alice          age        25years
    2       Alice     roommate            Bob
    3         Bob           is     Journalist
    4       Alice         owns  www.alice.com
    5         Bob         owns    www.bob.com
    """

    prompt10 = PromptTemplate(
        template = refined_user_query_neo4j,
        input_variables=["user_input", "df_string"]
    )
    chain10 = prompt10 | llm
    response15 = chain10.invoke({"user_input": user_query, "df_string": df_string})
    response14 = response15.content
    print("Response14 is : ")
    print(response14)
    print("*****r14*****")

    prompt1 = PromptTemplate(
        template = pr2,
        input_variables=["user_input", "df_string"]
    )   
    chain = prompt1 | llm 
    r1 = chain.invoke({"user_input": user_query, "df_string": df_string})
    r2 = r1.content
    print(r2)
    response0 = graph2.query(r2)
    print("*****")
    print(response0)
    print("**********")

    prompt2 = PromptTemplate(
        template = NLP,
        input_variables=["user_input","response0"]
    )
    chain2 = prompt2 | llm
    r1 = chain2.invoke({"user_input": user_query, "response0": response0})
    response = r1.content
    print(response)
    
    return response

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    user_query = data.get('query')
    if user_query:
        try:
            result = shubhNeo4j(user_query)
            return jsonify({'status': 'success', 'response': result})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    else:
        return jsonify({'status': 'error', 'message': 'Missing query'})


if __name__ == '__main__':
    app.run(debug=True, host='query_processing_service', port=5004) 
    
# Test a little
# result = shubhNeo4j("Give me Alice's Age?")

