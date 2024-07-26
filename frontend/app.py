import streamlit as st
import requests # For making requests to your microservices
# from streamlit_extras.switch_page_button import switch_page

# Styles for chat-like appearance
css = """
.chat-container {
    display: flex;
    flex-direction: column;
    height: 500px;
    overflow-y: auto;
}
.user-message {
    background-color: #007bff;  /* Blue for user */
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 5px;
    align-self: end;
}
.bot-message {
    background-color: #e9ecef; /* Light gray for bot */ 
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 5px;
    align-self: start;
}
""" 

bot_template = """
<div class="bot-message">
    {{MSG}}
</div>
"""
user_template = """
<div class="user-message">
    {{MSG}}
</div>
"""

# --- Helper Functions (Adapt these to communicate with your microservices) ---
def process_text_with_service(text, table_name):
    response = requests.post("http://text_processing_service:5001/process_text", 
                            json={"text": text, "table_name": table_name})
    if response.status_code == 200:
        return response.json().get('message', "Text processed successfully!")
    else:
        return "An error occurred while processing the text."

def process_image_with_service(image, table_name):
    files = {"image": image}  
    response = requests.post("http://image_processing_service:5002/process_image", 
                             files=files, 
                             data={"table_name": table_name})

    if response.status_code == 200:
        return response.json().get('message', "Image processed successfully!")
    else:
        return "An error occurred while processing the image."
def process_audio_with_service(audio, table_name):
    files = {"audio": audio}  
    response = requests.post("http://audio_processing_service:5003/process_audio", 
                             files=files, 
                             data={"table_name": table_name})

    if response.status_code == 200:
        return response.json().get('message', "Audio processed successfully!")
    else:
        return "An error occurred while processing the audio."

def query_knowledge_graph(query, table_name):
    response = requests.post("http://query_processing_service:5004/query", 
                            json={"query": query, "table_name": table_name})
    if response.status_code == 200:
        return response.json().get('response', "No results found.")
    else:
        return "An error occurred while querying the knowledge graph."

def query_data_knowledge_graph(query, table_name):
    response = requests.post("http://query_data_processing_service:5005/retrieve", 
                            json={"query": query, "table_name": table_name})
    if response.status_code == 200:
        return response.json().get('response', "No results found.")
    else:
        return "An error occurred while querying the knowledge graph."

# --- Streamlit App Structure ---
# st.set_page_config(page_title="Knowledge Graph App", page_icon=":brain:")
# Apply a light theme 
st.set_page_config(
    page_title="Knowledge Graph App", 
    page_icon=":brain:",
    layout="wide",  # Optional: Use the wide layout for more space
    initial_sidebar_state="expanded" # Optional: Start with an expanded sidebar
)
st.title("Multimodal Knowledge Graph Application")
tab_titles = ["Knowledge Graph Creation", "Knowledge Graph Querying", "Data Retrieval with KQ"]
tabs = st.tabs(tab_titles)

# --- Tab 1: Knowledge Graph Creation ---
with tabs[0]:
    st.header("Create Knowledge Graph")

    # Choose Input Method
    input_method = st.radio("Select input method:", ("Text", "Image", "Audio"))

    table_name = st.text_input("Enter an ID for the Knowledge Graph:", key="table_name")

    if input_method == "Text":
        user_query = st.text_area("Enter the text:", key="text_input")
        if st.button("Push text to Knowledge Graph"):
            if user_query and table_name:
                result = process_text_with_service(user_query, table_name)
                st.success(result)
            else:
                st.warning("Please enter text and a table name.")

    elif input_method == "Image":
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])
        if st.button("Push image to Knowledge Graph"):
            if uploaded_image and table_name:
                result = process_image_with_service(uploaded_image, table_name)
                st.success(result)
            else:
                st.warning("Please upload an image and enter a table name.")

    elif input_method == "Audio":
        uploaded_audio = st.file_uploader("Upload an audio", type=["wav", "mp3"])
        if st.button("Push audio to Knowledge Graph"):
            if uploaded_audio and table_name:
                result = process_audio_with_service(uploaded_audio, table_name)
                st.success(result)
            else:
                st.warning("Please upload an audio and enter a table name.")

# --- Tab 2: Knowledge Graph Querying ---
with tabs[1]:
    st.header("Query the Knowledge Graph")
    table_name2 = st.text_input("Knowledge Graph ID:", key="table_name2")
    
    if 'chat_hist' not in st.session_state:
        st.session_state.chat_hist = []

    # Display chat history
    for chat_entry in st.session_state.chat_hist:
        st.markdown(user_template.replace("{{MSG}}", chat_entry['query']), unsafe_allow_html=True)
        st.markdown(bot_template.replace("{{MSG}}", chat_entry['response']), unsafe_allow_html=True)

    user_query2 = st.text_input("Enter your query:", key="query_input")
    if st.button("Ask"):
        if user_query2 and table_name2:
            result = query_knowledge_graph(user_query2, table_name2)
            st.session_state.chat_hist.append({
                'query': user_query2,
                'response': result
            })
            st.markdown(user_template.replace("{{MSG}}", user_query2), unsafe_allow_html=True)
            st.markdown(bot_template.replace("{{MSG}}", result), unsafe_allow_html=True)
        else:
            st.warning("Please enter a query and a table name.")

# --- Tab 3: Data Retrieval with Knowledge Graph ---
with tabs[2]:
    st.header("Data Retrieval with the Knowledge Graph")
    table_name3 = st.text_input("Knowledge Graph ID:", key="table_name3")
    
    if 'chat_hist' not in st.session_state:
        st.session_state.chat_hist = []

    # Display chat history
    for chat_entry in st.session_state.chat_hist:
        st.markdown(user_template.replace("{{MSG}}", chat_entry['query']), unsafe_allow_html=True)
        st.markdown(bot_template.replace("{{MSG}}", chat_entry['response']), unsafe_allow_html=True)

    user_query3 = st.text_input("Enter your query:", key="retrieve_input")
    if st.button("Retrieve"):
        if user_query3 and table_name3:
            result = query_data_knowledge_graph(user_query3, table_name3)
            st.session_state.chat_hist.append({
                'query': user_query3,
                'response': result
            })
            st.markdown(user_template.replace("{{MSG}}", user_query3), unsafe_allow_html=True)
            st.markdown(bot_template.replace("{{MSG}}", result), unsafe_allow_html=True)
        else:
            st.warning("Please enter a query and a table name.")
