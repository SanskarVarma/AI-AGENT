import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from queries import handle_query, get_all_documents

load_dotenv()

app = Flask(__name__)

# Routes
app.route('/query', methods=['POST'])(handle_query)
app.route('/all', methods=['GET'])(get_all_documents)

if __name__ == '__main__':
    app.run(debug=True)