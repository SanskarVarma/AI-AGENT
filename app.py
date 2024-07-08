import logging
from flask import Flask, request, jsonify
from pymongo import MongoClient
import openai
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()  

logging.basicConfig(level=logging.DEBUG)

client = MongoClient(os.getenv('MONGO_URI'))
db = client['mydatabase']
collection = db['mycollection']

openai.api_key = os.getenv('OPENAI_API_KEY') 

def convert_to_mongo_query(user_query):
    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=f"Convert the following user query into a MongoDB query: {user_query}",
        max_tokens=50
    )
    return eval(response.choices[0].text.strip())

def execute_mongo_query(query):
    result = collection.find(query)
    return list(result)

@app.route('/query', methods=['POST'])
def handle_query():
    user_query = request.json.get('query')
    app.logger.debug(f"Received user query: {user_query}")
    mongo_query = convert_to_mongo_query(user_query)
    app.logger.debug(f"Generated Mongo query: {mongo_query}")
    result = execute_mongo_query(mongo_query)
    app.logger.debug(f"Query result: {result}")
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
