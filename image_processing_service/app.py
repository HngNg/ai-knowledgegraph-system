from flask import Flask, request, jsonify
from PIL import Image
import google.generativeai as genai
from transformers import CLIPProcessor, CLIPModel
import requests
# from ..shared.config import google_api_key

app = Flask(__name__)

google_api_key ='___'
genai.configure(api_key=google_api_key)

input= """
Describe the whole flow from starting to finish. Scan everything present in the image: figures, nodes, boxes, text, arrow, etc. Identify what components the flow/architecture diagram includeTry to describe one flow from one node to another through one arrow at a time using three words. The first and third word could be node and the second word could be relation. Always maintain heirarchical flow and describe the flow in steps. Do not try to skip any step in the flow. Give step-wise output without summarising. Remeber to not add anything that is not present in the picture originally.

Follow these steps:-

Step 1: Identify Overall Architecture
1.1 Start: Briefly describe the type of architecture.
1.2 Components: List the main components present in the diagram (deeply scan every box, circle, dotted box, figures and everything present in the picture.).

Step 2: Follow the Flow
2.1 Start Node: Identify the starting point of the flow (e.g., user, any external system). There can be multiple start nodes.
2.2 Action: Describe the action or event that triggers the flow (consider and analyze each and every arrow, dotted aarow, what is present in what box, what the name of a box is, etc.).
2.3 Intermediate / Destination Node: Identify the component where the data or action goes next (consider every figure, box, text, node, etc whereever any arrow or flow leads to). There can be multiple intermediate / destination nodes.

Repeat Steps 2.2  - 2.3 for each arrow in the diagram, maintaining this format:
    a. Action: Describe the data transformation or action happening at the current node (e.g., data validation, processing).
    b. Relation: Describe the type of connection between nodes (e.g., sends data to, receives response from).
    c. Destination: Identify the next component in the flow (e.g., database, application logic).

Step 3: Ending Point
3.1 Final Node: Identify the ending point of the flow (consider each and every arrow, box, dotted box, figures, nodes, etc). There can be multiple end / final nodes.
3.2 Output/Result: Describe the final outcome or action taken at the end (e.g., display results, data saved).

Additional Notes:
Mention any decision points or conditional branches in the flow.
Briefly describe any loops or repetitions in the process.
Include any text labels or annotations present in the diagram for clarity.

Remember:
Instructions for output format: 
Maintain a three-word format for each step (Node -> Relation -> Node). 
Do not miss any steps or anything at all.
Describe the flow in a hierarchical manner, following each arrow's direction.
Avoid summarizing the entire process at once; provide a step-by-step breakdown.

"""
def get_gemini_response(input,image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    if input!="":
       response = model.generate_content([input,image])
    else:
       response = model.generate_content(image)
    print("***Image Data***")
    print(response)
    print("*resEnd*")
    return response.text


@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400
    image_file = request.files['image']
    try:
        image = Image.open(image_file)
        text_data = get_gemini_response(input, image)  # Assuming 'input' is defined appropriately
        
        # Send data to text-processing service
        response = requests.post("http://text_processing_service:5001/process_text", 
                                json={'text': text_data, 'table_name': request.form.get('table_name')})
        
        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': 'Image processed and sent for KG population'})
        else:
            return jsonify({'status': 'error', 'message': 'Error sending data to text-processing service'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='image_processing_service', port=5002) 