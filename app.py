from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv  # Import dotenv
import json

# Initialize Flask app
app = Flask(__name__)

load_dotenv()

# OpenAI API key setup
api_key = os.getenv("OPENAI_API_KEY")
print(api_key)
client = OpenAI(api_key=api_key)


def generate_mcq_from_llm(subject, chapter):
    """
    Generates an MCQ question with options using OpenAI LLM.
    :param subject: The subject for the question.
    :param chapter: The chapter/topic for the question.
    :return: A dictionary with the question and options.
    """
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that generates educational content related to CBSE boards 10th standard subjects like multiple-choice questions."
        },
        {
            "role": "user",
            "content": f"Generate a multiple-choice question (MCQ) with four options based on the CBSE 10th class subject '{subject}' and chapter '{chapter}'. " \
                       "Include the question, four options (A-D), and indicate the correct option. Return response as a json with 'question', 'options', and 'correct_option'. dont include any text to indicate its json or any other header data in the response"
        }
    ]
    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # Use "gpt-4" if available and necessary
        messages=messages,
        max_tokens=300,
        temperature=0.7
    )
    #print('**LLM RESEPONSE****  ',response)
    #print("extracting response")
    #print('**LLM RESEPONSE****  ',completion)
    response_text = completion.choices[0].message.content.strip()
    #print('**LLM RESEPONSE****  ',response_text)
    data = json.loads(response_text)


    try:
        lines = ""
        question = data['question']
        options =  data['options']
        correct_option = data['correct_option']
        return {
            "question": question,
            "options": options,
            "correct_option": correct_option
        }
    except Exception as e:
        return {"error": "Error parsing response from LLM", "details": str(e)}


def validate_answer_with_llm(question, answer):
    """
    Validates the given answer for a question using OpenAI LLM.
    :param question: The MCQ question to validate against.
    :param answer: The user's answer.
    :return: A validation result with feedback.
    """
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that evaluates answers to multiple-choice questions."
        },
        {
            "role": "user",
            "content": f"Validate the answer '{answer}' for the following question:\n\n'{question}'\n\n" \
                       "Provide feedback indicating if the answer is correct or incorrect and explain why."
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=300,
        temperature=0.7
    )
    response_text = response['choices'][0]['message']['content'].strip()
    return {"validation_result": response_text}


@app.route('/generate_mcq', methods=['POST'])
def generate_mcq():
    """
    API endpoint to generate an MCQ question.
    Expects JSON payload with 'subject' and 'chapter'.
    """
    data = request.json
    subject = data.get("subject")
    chapter = data.get("chapter")
    print('***Data received***:',subject, chapter)
    if not subject or not chapter:
        return jsonify({"error": "Both 'subject' and 'chapter' are required fields."}), 400
    
    result = generate_mcq_from_llm(subject, chapter)
    return jsonify(result)


@app.route('/validate_answer', methods=['POST'])
def validate_answer():
    """
    API endpoint to validate a given answer for an MCQ question.
    Expects JSON payload with 'question' and 'answer'.
    """
    data = request.json
    question = data.get("question")
    answer = data.get("answer")
    
    if not question or not answer:
        return jsonify({"error": "Both 'question' and 'answer' are required fields."}), 400
    
    result = validate_answer_with_llm(question, answer)
    return jsonify(result)


# Entry point for Flask app
if __name__ == '__main__':
    # Run the app
    app.run(debug=True, port=5001)
