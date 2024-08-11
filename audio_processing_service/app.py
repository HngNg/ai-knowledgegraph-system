from flask import Flask, request, jsonify
import requests 
import whisper 

app = Flask(__name__)

# --- Your speech2text_ function --- 
def speech2text_(audio_file_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file_path, fp16=False, language='English')
    return result["text"]

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'status': 'error', 'message': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    try: 
        # Save the uploaded audio file temporarily 
        audio_file_path = "temp_audio.wav"  # Consider a more robust naming scheme
        audio_file.save(audio_file_path)

        # Perform Speech-to-Text
        text_data = speech2text_(audio_file_path)
        print("checkpoint")
        print(text_data)
        # Send data to text-processing service 
        response = requests.post("http://text_processing_service:5001/process_text",
                                 json={'text': text_data, 'table_name': request.form.get('table_name')})
        # response = requests.post("http://localhost:5001/process_text",
        #                          json={'text': text_data, 'table_name': request.form.get('table_name')})

        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': 'Audio processed and sent for KG population'})
        else:
            return jsonify({'status': 'error', 'message': 'Error sending data to text-processing service'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # app.run(debug=True, host='audio_processing_service', port=5003)  # Use a different port 
    # app.run(debug=True, host='localhost', port=5003)
    app.run(debug=True, host='0.0.0.0', port=5003)