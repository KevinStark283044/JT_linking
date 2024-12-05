from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from collections import defaultdict
from openai import OpenAI
import GPTUtils.prompts as prompts

# Initialize the Flask app and CORS
app = Flask(__name__)
CORS(app)

dirname = os.path.dirname(__file__)
relative_path = lambda filename: os.path.join(dirname, filename)
client = OpenAI(api_key=open("api_key").read(), timeout=10)

# @app.route("/test/")
# def test():
#     return "Hello Delta"


@app.route("/codes/overview/")
def get_codes_overview():
    # Load data from JSON file
    data = json.load(open(relative_path("data/interview_codes_and_summary.json"), "r"))

    # reverse index by Demographics, Values, Drivers, Governance, and Strategy
    example_questions = []
    for question_data in data:
        category_codes = list(
            set([code_name.split("\\")[0] for code_name in question_data["code_names"]])
        )
        assert len(category_codes) == 1
        category_code = category_codes[0]
        example_questions.append(
            {
                "category": category_code,
                "question": question_data["question"][:-1],
                "summaries": question_data["summaries"],
            }
        )

    return {
        "questions": example_questions,
    }


@app.route("/codes/question/", methods=["POST"])
def find_answers():
    user_question = request.json["question"]
    print("User question: ", user_question)
    category_rqs = json.load(open("data/category_rqs.json"))
    applicable_categories = prompts.gpt_applicable_categories(
        client, user_question, category_rqs
    )
    print("Applicable categories: ", applicable_categories)
    all_summaries = json.load(open("data/all_summaries.json"))
    filtered_summaries = [
        s
        for s in all_summaries
        if s["code_name"].split("\\")[0] in applicable_categories
    ]
    direct_answer_indices = prompts.gpt_filter_direct_answers(
        client, user_question, filtered_summaries
    )
    direct_answers = [filtered_summaries[i] for i in direct_answer_indices]
    print(direct_answers)
    return json.dumps(direct_answers)


@app.route("/codes/content/", methods=["POST"])
def find_content():
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({"error": "Invalid request: No data provided"}), 400

        selected_category = request_data.get("selectedCategory")
        selected_scenario = request_data.get("selectedScenario")

        if not selected_category or not selected_scenario:
            return jsonify({"error": "Invalid request: Missing category or scenario"}), 400

        data_file_path = relative_path("data/workbook_mappings.json")
        with open(data_file_path, "r") as file:
            data = json.load(file)

        results = []
        category_data = data.get(selected_category, [])
        for entry in category_data:
            if len(entry) > 2 and entry[2] == selected_scenario:
                results.append({"value1": entry[0], "value2": entry[1]})

        return jsonify({"results": results})
    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode JSON data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# def get_summaries():
#     # Load data from JSON file
#     with open(relative_path("data/interview_codes_and_summary.json"), "r") as f:
#         data = json.load(f)

#     # Retrieve the question from the request data
#     question = request.json["question"]
#     summaries = []

#     # Find summaries for the provided question
#     for entry in data:
#         if question in entry.get("question", []):
#             summaries.extend(entry.get("summaries", []))
#             break

#     return {"question": question, "summaries": summaries}


# @app.route("/")
# def index():
#     return render_template('front-end_test.html')  # Serve the HTML file

if __name__ == "__main__":
    app.run(debug=True)
