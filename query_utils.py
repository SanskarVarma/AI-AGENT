import os
import openai
import json
import re

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def convert_to_mongo_query(user_query):
    prompt = f"""
    You are building a restaurant menu search system that uses MongoDB to retrieve information. The database contains two collections:
        - `mycollection`: Contains entries for various menu items with fields like item name (`item`), price (`price`), and daily orders received (`order`).
        - `menuDetails`: Contains additional details for menu items including locations (`locations`) and preparation time (`prep_time`).

        PLEASE TAKE CARE THAT THE FEILD WRITTEN BY THE USER CAN BE IN BOLD LETTERS OR NORMAL LETTERS take care if a user wite Burger or burger or burGer all should be considers like same.

        Your task is to convert natural language queries into MongoDB queries that can accurately retrieve menu items based on user specifications. Respond only with the MongoDB query in valid JSON format.

        Here are the fields you can use:
        - From `mycollection`: `item`, `price`, `order`
        - From `menuDetails`: `locations`, `prep_time`

        Example queries you should handle:
        - Retrieve menu items priced under $10 and located in "Fast Food Heaven".
        - Find items with more than 200 orders per day and preparation time less than 20 minutes.
        - Get details of a specific menu item like 'Burger' including its locations.


    Natural language query: "{user_query}"
    MongoDB query:
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
        ]
    )

    mongo_query_str = response.choices[0].message['content'].strip()

    try:
        # Parse the JSON string into a dictionary
        mongo_query = json.loads(mongo_query_str)
        if isinstance(mongo_query, list):
            # Ensure it's a list of dictionaries (aggregation pipeline)
            for stage in mongo_query:
                if not isinstance(stage, dict):
                    raise ValueError("Invalid MongoDB query format: stages must be dictionaries")
        elif not isinstance(mongo_query, dict):
            raise ValueError("Invalid MongoDB query format: must be a dictionary or list")
    except Exception as e:
        raise ValueError(f"Invalid MongoDB query format: {e}")

    return mongo_query

def convert_to_natural_language(mongo_results):
    result_str = json.dumps(mongo_results, indent=2)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant at a restaurant that provides information about the menu and restaurant details to customers. Use the given MongoDB query result to create a friendly and helpful response. Respond only with the natural language summary. Do not include any additional text."},
            {"role": "user", "content": f"Convert the following MongoDB query result to natural language and only include the important information the user asks for: {result_str}"}
        ]
    )

    natural_language_response = response.choices[0].message['content'].strip()
    
    return natural_language_response
