# Multimodal Knowledge Graph System

This repository contains a set of microservices to create, process, and query a multimodal knowledge graph from various input sources like text, images, and audio. The system is built using Docker and can be easily deployed using Docker Compose.

## Table of Contents
- [Multimodal Knowledge Graph System](#multimodal-knowledge-graph-system)
  - [Table of Contents](#table-of-contents)
  - [Architecture Overview](#architecture-overview)
  - [Tech Stack](#tech-stack)
  - [Microservices](#microservices)
    - [Text Processing Service](#text-processing-service)
    - [Image Processing Service](#image-processing-service)
    - [Audio Processing Service](#audio-processing-service)
    - [Query Processing Service](#query-processing-service)
    - [Query Data Processing Service](#query-data-processing-service)
    - [Frontend Service](#frontend-service)
    - [Neo4j Database](#neo4j-database)
  - [Setup and Running](#setup-and-running)
    - [Usage](#usage)

## Architecture Overview

The application consists of multiple microservices, each responsible for handling different types of input and processing them to populate a knowledge graph stored in a Neo4j database. The knowledge graph is then used to query information, or support the data retrieval process. The services communicate with each other via REST APIs.

## Tech Stack

The application is built using the following technologies:

- **Programming Languages:** Python
- **Web Frameworks:** Flask, Streamlit
- **Machine Learning Libraries & Models:** Whisper, Transformers, Google Generative AI (Gemini 1.5 Pro)
- **Graph Database:** Neo4j
- **Cloud Services:** AWS S3 (for data storage)
- **Containerization:** Docker

## Microservices

### Text Processing Service
- **Path:** `./text_processing_service`
- **Port:** `5001`
- **Description:** This service processes text input to extract relevant entities and relationships to populate the knowledge graph in Neo4j. It uses Google Generative AI for text processing.

### Image Processing Service
- **Path:** `./image_processing_service`
- **Port:** `5002`
- **Description:** This service processes image input to extract relevant information from diagrams and populate the knowledge graph. It uses Google Generative AI to interpret images.

### Audio Processing Service
- **Path:** `./audio_processing_service`
- **Port:** `5003`
- **Description:** This service processes audio input, converting speech to text using the Whisper model and then populates the knowledge graph with the extracted information.

### Query Processing Service
- **Path:** `./query_processing_service`
- **Port:** `5004`
- **Description:** This service handles user queries to the knowledge graph. It refines the query, generates Cypher queries, executes them against Neo4j, and returns the results in a user-friendly format.

### Query Data Processing Service
- **Path:** `./query_data_processing_service`
- **Port:** `5005`
- **Description:** This service retrieves related keyterms from Neo4j based on user queries and searches for relevant data objects in an AWS S3 bucket.

### Frontend Service
- **Path:** `./frontend`
- **Port:** `8501`
- **Description:** This service provides a web-based user interface using Streamlit for interacting with the multimodal knowledge graph. Users can input text, image, or audio data to populate the graph and query it.

### Neo4j Database
- **Image:** `neo4j:5.20.0`
- **Ports:** `7474` (HTTP), `7687` (Bolt)
- **Description:** This is the graph database where all the knowledge graph data is stored. It is accessed by all other services to store and retrieve data.

## Setup and Running

1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-username/knowledge-graph-app.git
   cd knowledge-graph-app

2. **Ensure Docker and Docker Compose are installed:**

  - Docker Installation: https://docs.docker.com/engine/install/
    
  - Docker Compose Installation: https://docs.docker.com/compose/install/

3. **Build and run the services:**
  ```
  docker-compose build
  docker-compose up 
  ```
This will build the Docker images for each service and start the containers.

4. **Access the frontend:**
Open your web browser and navigate to http://localhost:8501.

### Usage
1. **Creating the Knowledge Graph:**

- Navigate to the "Knowledge Graph Creation" tab.
Select an input method (Text, Image, or Audio).
Enter or upload the corresponding input and provide a table name.
Click the "Push" button to process the input and populate the knowledge graph.

2. **Querying the Knowledge Graph:**

- Navigate to the "Knowledge Graph Querying" tab.
Enter the knowledge graph ID and your query.
Click the "Ask" button to execute the query and display the results.

3. **Data Retrieval with the Knowledge Graph:**

- Navigate to the "Data Retrieval with Knowledge Graph" tab.
Enter the knowledge graph ID and your query.

- Click the "Retrieve" button to search for relevant data objects in the AWS S3 bucket and display the results.
