import os
import re
import openai
import json

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def convert_to_mongo_query(user_query):
    prompt = f"""
    You are building a restaurant menu search system that uses MongoDB to retrieve information.
    Your task is to convert natural language queries into MongoDB queries that can accurately retrieve menu items based on user specifications. Respond only with the MongoDB query in valid JSON format.Ensure that the JSON format is correct with property names in double quotes.

    Ensure the output adheres to MongoDB query syntax and handles both collections correctly. Avoid using invalid operators or incorrect JSON formats.

    - `mycollection`: Contains entries for various menu items with fields like item name (`item`), price (`price`), and daily orders received (`orders`).

    Example queries you should handle:
    - Retrieve menu items priced under $10 and located in "Fast Food Heaven".
    - Find items with more than 200 orders per day and preparation time less than 20 minutes.
    - Get details of a specific menu item like 'Burger' including its locations.

    User Query: "{user_query}"
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a MongoDB query assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0
    )

    mongo_query = response.choices[0].message['content'].strip()

    try:
        # Check and fix JSON syntax errors like trailing commas
        mongo_query_fixed = fix_json_syntax(mongo_query)
        parsed_query = json.loads(mongo_query_fixed)
        
        # If the parsed query is a dict with $lookup at the top level, convert it to an aggregation pipeline
        if isinstance(parsed_query, dict) and '$lookup' in parsed_query:
            parsed_query = [parsed_query]

        return parsed_query

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"OpenAI response: {mongo_query}")
        raise

def fix_json_syntax(mongo_query):
    # Remove trailing commas after '}' to fix JSON syntax
    fixed_query = re.sub(r',\s*}', '}', mongo_query)
    return fixed_query

def convert_to_natural_language(result):
    prompt = f"""
    You are a helpful assistant that converts MongoDB query results into natural language. Below is the MongoDB query result:

    {json.dumps(result, indent=2)}

    Please convert this result into a natural language response.give answer that looks like you are a waiter or a restaurant manager. dont write anything related to the collection or code just as as you a restaurang manager
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a natural language generation assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0
    )

    natural_language_response = response.choices[0].message['content'].strip()
    return natural_language_response
