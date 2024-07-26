from flask import Flask, request, jsonify
from langchain_community.llms import Ollama 
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_core.prompts import PromptTemplate
from langchain_community.graphs import Neo4jGraph
import ast
import pandas as pd
# from neo4j import GraphDatabase  # Add this import 
from py2neo import Graph, Node, Relationship
from flask_cors import CORS

neo4j_url = 'neo4j://neo4j:7687'
neo4j_username = 'neo4j'
neo4j_password = '12345678'

app = Flask(__name__)
CORS(app)
graph = Graph(neo4j_url, auth=(neo4j_username, neo4j_password))
# llm1 = OpenAI(openai_api_key=openai_api_key, temperature=0.0) 
# llm = Ollama(model="llama3", base_url="http://text_processing_service:11434") 
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

pr = """# Knowledge Graph Instructions for Llama2
## 1. Overview
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph. You are a data scientist working for a company that is building a graph database. Your task is to extract information from data and convert it into three words with meaning Source_Node, Relationship, Target_Node. The first and third words are to be used as nodes and the second word is to be used as relationship. So, maintain consistency in spelling and capital letter such that node with same name is formed only once later.
- **Nodes** represent entities and concepts. They're akin to Wikipedia nodes.
- The aim is to achieve simplicity and clarity in the knowledge graph, making it accessible for a vast audience.
## 2. Labeling Nodes
- **Consistency**: Ensure you use basic or elementary types for node labels.
  - For example, when you identify an entity representing a person, always label it as **"person"**. Avoid using more specific terms like "mathematician" or "scientist".
- **Node IDs**: Never utilize integers as node IDs. Node IDs should be names or human-readable identifiers found in the text.
## 3. Handling Numerical Data and Dates
- Numerical data, like age or other related information, should be incorporated as attributes or properties of the respective nodes.
- **No Separate Nodes for Dates/Numbers**: Do not create separate nodes for dates or numerical values. Always attach them as attributes or properties of nodes.
- **Property Format**: Properties must be in a key-value format.
- **Quotation Marks**: Never use escaped single or double quotes within property values.
- **Naming Convention**: Use camelCase for property keys, e.g., `birthDate`.
## 4. Coreference Resolution
- **Maintain Entity Consistency**: When extracting entities, it's vital to ensure consistency.
If an entity, such as "John Doe", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Joe", "he"), 
always use the most complete identifier for that entity throughout the knowledge graph. In this example, use "John Doe" as the entity ID.  
Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial. 
## 5. Strict Compliance
Adhere to the rules strictly. Non-compliance will result in termination. Only return the list and nothing else. No extra word or sentence.

Example:
Data: Alice lawyer and is 25 years old and Bob is her roommate since 2001. Bob works as a journalist. Alice owns a the webpage www.alice.com and Bob owns the webpage www.bob.com.

List created is given below. Only return this list and nothing else. No extra word or sentence.
['Alice~~is~~Lawyer', 'Alice~~age~~25years', 'Alice~~roommate~~Bob', 'Bob~~is~~Journalist', 'Alice~~owns~~www.alice.com', 'Bob~~owns~~www.bob.com']

Here is the question data: {user_input}
Remember to only return the list and nothing else. No extra word or sentence.
"""

def extract_list_from_response(response):
    start_idx = response.content.find('[')
    end_idx = response.content.find(']')
    
    if start_idx == -1 or end_idx == -1 or start_idx > end_idx:
        raise ValueError("The response does not contain a valid list format")
    
    list_str = response.content[start_idx:end_idx + 1]
    return list_str

#Knowledge Graph from Text
def KG_from_Text(user_query, table_name):
    prompt = PromptTemplate(
        template = pr,
        input_variables=["user_input"]
    )
    chain = prompt | llm
    p1 = chain.invoke({"user_input": user_query})

    # print(p1)
    a1 = extract_list_from_response(p1)
    df_list = ast.literal_eval(a1)
    split_data = [item.split('~~', 2) for item in df_list]
    df = pd.DataFrame(split_data, columns=['Source_Node', 'Relationship', 'Target_Node'])

    for index, row in df.iterrows():
        source_node = Node("Node", name=row['Source_Node'], table_name=table_name)
        target_node = Node("Node", name=row['Target_Node'], table_name=table_name)
        relationship_type = row['Relationship']
        
        # Merge nodes in the graph
        graph.merge(source_node, "Node", "name")
        graph.merge(target_node, "Node", "name")
        
        # Create relationship between nodes
        relationship = Relationship(source_node, relationship_type, target_node)
        
        # Merge relationship in the graph
        graph.merge(relationship)
    print("Data imported into Neo4j graph database successfully.")
    result = "Data imported into Neo4j graph database successfully."
    return result

@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.get_json()
    user_query = data.get('text')
    table_name = data.get('table_name')
    if user_query and table_name:
        try:
            result = KG_from_Text(user_query, table_name)
            return jsonify({'status': 'success', 'message': result})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    else:
        return jsonify({'status': 'error', 'message': 'Missing text or table_name'})


if __name__ == '__main__':
    app.run(debug=True, host='text_processing_service', port=5001) 

# result = KG_from_Text("What is e", "JSCC")
# print (result)