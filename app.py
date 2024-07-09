import os
from flask import Flask, request, jsonify
import openai
from pymongo import MongoClient
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize MongoDB client
mongo_client = MongoClient(os.getenv('MONGO_URI'))
db = mongo_client[os.getenv('MONGO_DB_NAME')]

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    user_query = data.get('query')

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        mongo_query = convert_to_mongo_query(user_query)

        # Debugging: Print the MongoDB query
        print(f"MongoDB Query: {mongo_query}")

        result = db.collection_name.find(mongo_query)

        # Convert the cursor to a list of documents
        output = [doc for doc in result]

        # Convert ObjectId to string for JSON serialization
        for doc in output:
            doc['_id'] = str(doc['_id'])

        # Return the MongoDB query and the results
        response = {
            "query": mongo_query,
            "results": output
        }

        return jsonify(response)
    except Exception as e:
        # Log the error
        print(f"Error processing query: {str(e)}")
        return jsonify({"error": str(e)}), 400
    
@app.route('/all', methods=['GET'])
def get_all_documents():
    print("'/all' endpoint was accessed")
    try:
        result = db.collection_name.find()
        output = [doc for doc in result]
        for doc in output:
            doc['_id'] = str(doc['_id'])
        return jsonify(output)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def convert_to_mongo_query(user_query):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that converts natural language queries to MongoDB queries. Respond only with the MongoDB query in JSON format."},
            {"role": "user", "content": user_query}
        ]
    )

    # Debugging: Print the raw response from OpenAI
    print(response.choices[0].message['content'].strip())
    
    mongo_query_str = response.choices[0].message['content'].strip()
    
    try:
        # Debugging: Print the query string before evaluation
        print(f"MongoDB query string: {mongo_query_str}")
        
        mongo_query = json.loads(mongo_query_str)
        if not isinstance(mongo_query, dict):
            raise ValueError("Mongo query is not a dictionary")
    except Exception as e:
        raise ValueError(f"Invalid MongoDB query format: {e}")
    
    return mongo_query

if __name__ == '__main__':
    app.run(debug=True)
