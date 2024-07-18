import os
import logging
from flask import jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
from query_utils import convert_to_mongo_query, convert_to_natural_language
import json

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the JSON file
with open('data.json') as f:
    data = json.load(f)

mongo_client = MongoClient(os.getenv('MONGO_URI'))
db = mongo_client[os.getenv('MONGO_DB_NAME')]


# Insert the data into separate collections
def insert_data(db, data):
    for collection_name, documents in data.items():
        collection = db[collection_name]

        if isinstance(documents, list):
            for document in documents:
                # Check if the document already exists in the collection
                if not collection.find_one(document):
                    collection.insert_one(document)
        else:
            # Check if the document already exists in the collection
            if not collection.find_one(documents):
                collection.insert_one(documents)

try:
    insert_data(db, data)
    logger.info("Data inserted successfully")
except Exception as e:
    logger.error(f"Error inserting data: {e}")
    raise


def handle_query():
    data = request.json
    user_query = data.get('query')

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Convert the natural language query to a MongoDB query using OpenAI
        mongo_query = convert_to_mongo_query(user_query)

        # Debugging: Print the MongoDB query
        print(f"MongoDB Query: {mongo_query}")

        # Execute the MongoDB query
        result_mycollection = []
        result_menuDetails = []

        if isinstance(mongo_query, dict):  # Simple find query
            result_mycollection = list(db.mycollection.find(mongo_query))
            result_menuDetails = list(db.menuDetails.find(mongo_query))
        elif isinstance(mongo_query, list):  # Aggregation pipeline
            result_mycollection = list(db.mycollection.aggregate(mongo_query))
            result_menuDetails = list(db.menuDetails.aggregate(mongo_query))

        # Convert ObjectId to string for JSON serialization
        for doc in result_mycollection:
            doc['_id'] = str(doc['_id'])
        for doc in result_menuDetails:
            doc['_id'] = str(doc['_id'])

        # Merge results if needed or handle separately
        combined_output = {
            "mycollection_results": result_mycollection,
            "menuDetails_results": result_menuDetails
        }

        # Convert the MongoDB query result to natural language using OpenAI
        natural_language_response = convert_to_natural_language(combined_output)

        # Return the natural language response and the raw MongoDB query results
        response = {
            "query": mongo_query,
            "results": combined_output,
            "natural_language_response": natural_language_response
        }

        return jsonify(response)
    except Exception as e:
        # Log the error
        print(f"Error processing query: {str(e)}")
        return jsonify({"error": str(e)}), 400

def get_all_documents():
    print("'/all' endpoint was accessed")
    try:
        result = db.mycollection.find()
        output = [doc for doc in result]
        for doc in output:
            doc['_id'] = str(doc['_id'])
        return jsonify(output)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
