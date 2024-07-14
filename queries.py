import os
from flask import jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
from query_utils import convert_to_mongo_query, convert_to_natural_language
import json

load_dotenv()

mongo_client = MongoClient(os.getenv('MONGO_URI'))
db = mongo_client[os.getenv('MONGO_DB_NAME')]

def handle_query():
    data = request.json
    user_query = data.get('query')

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        mongo_query = convert_to_mongo_query(user_query)

        print(f"MongoDB Query: {mongo_query}")

        result_mycollection = db.mycollection.find(mongo_query)
        if isinstance(mongo_query, dict):  
            result_mycollection = db.mycollection.find(mongo_query)
        elif isinstance(mongo_query, list):  
            result_mycollection = db.mycollection.aggregate(mongo_query)

        if isinstance(mongo_query, dict):  
            result_menuDetails = db.menuDetails.find(mongo_query)
        elif isinstance(mongo_query, list):  
            result_menuDetails = db.menuDetails.aggregate(mongo_query)

        output_mycollection = [doc for doc in result_mycollection]
        output_menuDetails = [doc for doc in result_menuDetails]

        for doc in output_mycollection:
            doc['_id'] = str(doc['_id'])
        for doc in output_menuDetails:
            doc['_id'] = str(doc['_id'])

        combined_output = {
            "mycollection_results": output_mycollection,
            "menuDetails_results": output_menuDetails
        }

        natural_language_response = convert_to_natural_language(combined_output)

        response = {
            "query": mongo_query,
            "results": combined_output,
            "natural_language_response": natural_language_response
        }

        return jsonify(response)
    except Exception as e:
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
