import boto3 
from flask import Flask, request, jsonify
from langchain_community.llms import Ollama 
from langchain_core.prompts import PromptTemplate
from langchain_community.graphs import Neo4jGraph
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import ast
import pandas as pd
from py2neo import Graph, Node, Relationship

app = Flask(__name__)

# --- AWS Configuration ---
AWS_ACCESS_KEY_ID = '___' 
AWS_SECRET_ACCESS_KEY = '___'
S3_BUCKET_NAME = 'aiknowledgegraph' 

neo4j_url = 'neo4j://neo4j:7687'
neo4j_username = 'neo4j'
neo4j_password = '12345678'
graph2 = Graph(neo4j_url, auth=(neo4j_username, neo4j_password))

# llm = Ollama(model="llama3", base_url="http://localhost:11434") 
os.environ["GOOGLE_API_KEY"] ='___'
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

# --- Prompt Templates (You can adjust these as needed) ---
keyterm_extraction_prompt = """
Your task is to extract relevant keyterms from a user's query. 
The user query is: {user_input}
Return a list of keyterms: 
[keyterm1, keyterm2, ...] 
keyterm examples: Semantic Learning, System Flow, Deep JSCC, etc.
After generate the keyterms, capitalize the first letter of each word in a term.
*Attention*: Only give the generated keyterm in the given format [keyterm1, keyterm2, ...] 
Don't give any other extra word or information, the list of keyterms only.
"""

# --- Helper Functions ---

def extract_keyterms(user_query):
    prompt_template = PromptTemplate(
        template=keyterm_extraction_prompt,
        input_variables=["user_input"]
    )
    chain = prompt_template | llm
    response = chain.invoke({"user_input": user_query})
    keyterms_str = response.content.strip()  
    keyterms = [kw.strip() for kw in keyterms_str[1:-1].split(",")]
    return keyterms

def get_related_keyterms_from_neo4j(keyterms):
    related_keyterms = set(keyterms)  # Start with initial keyterms
    for keyterm in keyterms:
        try:
            # Query Neo4j for related nodes (adjust the Cypher query as needed)
            query = " MATCH (n:Node {name: '{keyterm}'})-[r]-(m:Node) RETURN m.name AS related_keyterm"
            results = graph2.query(query)
            for record in results:
                related_keyterms.add(record["related_keyterm"])
        except Exception as e:
            print(f"Error querying Neo4j for '{keyterm}': {e}")
    return list(related_keyterms)

def search_s3(keyterms):
    s3 = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    
    matching_objects = []
    
    # 1. Build S3 Object Tagging Search Expression
    tag_filters = [
        {
            'Key': keyterm,  # Using keyterms as tag keys
            'Value': 'true'  # You can adjust the value if needed 
        } 
        for keyterm in keyterms
    ]

    # 3. Perform the S3 Search (using pagination)
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=S3_BUCKET_NAME):
        for obj in page.get('Contents', []):
            # Retrieve tags for each object
            response = s3.get_object_tagging(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
            object_tags = {tag['Key']: tag['Value'] for tag in response.get('TagSet', [])}

            # Check if object tags match any of the keyterms
            if any(keyterm in object_tags for keyterm in keyterms):
                matching_objects.append(obj['Key'])

    return matching_objects

def getFileNamesFromCloud(user_query):
    # Extract keyterms from the User Query
    keyterms = extract_keyterms(user_query)
    print("keyterms extracted:", keyterms)

    # Get Related keyterms from Neo4j
    related_keyterms = get_related_keyterms_from_neo4j(keyterms)
    print("Related keyterms from Neo4j:", related_keyterms)

    # Search S3 using combined keyterms
    retrieved_objects = search_s3(related_keyterms)
    print("Retrieved objects: ", retrieved_objects)

    return str(retrieved_objects)  # Return the list of file names

# --- Flask App Route ---
@app.route('/retrieve', methods=['POST'])
def retrieve():
    data = request.get_json()
    user_query = data.get('query')
    if user_query:
        try:
            retrieved_file_names = getFileNamesFromCloud(user_query)
            return jsonify({'status': 'success', 'response': retrieved_file_names})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    else:
        return jsonify({'status': 'error', 'message': 'Missing query'})


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5005) 
    

# result = getFileNamesFromCloud("What is semantic communication?")
# print (result)
