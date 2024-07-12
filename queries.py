import os
from flask import jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
from query_utils import convert_to_mongo_query, convert_to_natural_language
import json

load_dotenv()

# Initialize MongoDB client
mongo_client = MongoClient(os.getenv('MONGO_URI'))
db = mongo_client[os.getenv('MONGO_DB_NAME')]

def handle_query():
    data = request.json
    user_query = data.get('query')

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Convert the natural language query to a MongoDB query
        mongo_query = convert_to_mongo_query(user_query)

        # Debugging: Print the MongoDB query
        print(f"MongoDB Query: {mongo_query}")

        # Search both collections
        result_mycollection = db.mycollection.find(mongo_query)
        if isinstance(mongo_query, dict):  # Simple find query
            result_mycollection = db.mycollection.find(mongo_query)
        elif isinstance(mongo_query, list):  # Aggregation pipeline
            result_mycollection = db.mycollection.aggregate(mongo_query)

        if isinstance(mongo_query, dict):  # Simple find query
            result_menuDetails = db.menuDetails.find(mongo_query)
        elif isinstance(mongo_query, list):  # Aggregation pipeline
            result_menuDetails = db.menuDetails.aggregate(mongo_query)

        # Convert the cursor to a list of documents for both collections
        output_mycollection = [doc for doc in result_mycollection]
        output_menuDetails = [doc for doc in result_menuDetails]

        # Convert ObjectId to string for JSON serialization
        for doc in output_mycollection:
            doc['_id'] = str(doc['_id'])
        for doc in output_menuDetails:
            doc['_id'] = str(doc['_id'])

        # Merge results if needed or handle separately
        combined_output = {
            "mycollection_results": output_mycollection,
            "menuDetails_results": output_menuDetails
        }

        # Convert the MongoDB query result to natural language
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
