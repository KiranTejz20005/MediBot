from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import time
import csv
from flask_cors import CORS
from gtts import gTTS
from io import BytesIO
import os
import re
from PIL import Image
import io
from PyPDF2 import PdfReader

app = Flask(__name__)
CORS(app)

genai.configure(api_key="AIzaSyD0GZYHouCSeOPTbdC_zXZ2_QhwDytK0DQ")

specific_commands = {
    "hello": "Hi! How can I assist you with your health concerns today?",
    "hi": "Hello! I'm here to help with any medical questions you have.",
    "what can you do?": "I can provide information on health and medical topics. Just ask me anything!",
    "what is your name?": "I am MediBot, your virtual medical assistant.",
    "who created you?": "I was developed by a team of St.Peter's College Students to assist with medical queries.",
    "how are you?": "I'm just a bot, but I'm here and ready to help you with your health questions!",
    "thank you": "You're welcome! If you have more questions, feel free to ask.",
    "thanks": "You're welcome! Let me know if there's anything else I can assist you with.",
    "bye": "Goodbye! Take care and stay healthy!",
    "goodbye": "Goodbye! Wishing you good health!",
    

    "what are the symptoms of COVID-19?": "Common symptoms of COVID-19 include fever, cough, fatigue, loss of taste or smell, sore throat, and difficulty breathing.",
    "what is a healthy diet?": "A healthy diet includes a variety of fruits, vegetables, whole grains, lean proteins, and healthy fats. Avoid processed foods and excessive sugar.",
    "how can I boost my immune system?": "To boost your immune system, eat a balanced diet, exercise regularly, get enough sleep, stay hydrated, and manage stress.",
    "what is the normal blood pressure range?": "The normal blood pressure range is typically around 120/80 mmHg.",
    "how do I manage stress?": "You can manage stress by practicing mindfulness, exercising regularly, getting enough sleep, and talking to a therapist if needed.",
    "what are the signs of a heart attack?": "Signs of a heart attack include chest pain, shortness of breath, nausea, lightheadedness, and pain in the arm, neck, or jaw.",
    "how much water should I drink daily?": "It is generally recommended to drink about 8 glasses (2 liters) of water per day, but this can vary based on your activity level and climate.",
    "what is diabetes?": "Diabetes is a chronic condition where the body cannot properly regulate blood sugar levels due to insufficient insulin production or insulin resistance.",
    "how can I lower my cholesterol?": "To lower cholesterol, eat a diet low in saturated fats, exercise regularly, avoid smoking, and consider medication if prescribed by your doctor.",
    "what is the flu?": "The flu is a contagious respiratory illness caused by influenza viruses. Symptoms include fever, cough, sore throat, body aches, and fatigue.",


    "how can I improve my sleep?": "To improve sleep, maintain a regular sleep schedule, avoid caffeine before bed, create a comfortable sleep environment, and limit screen time before bed.",
    "what are the benefits of exercise?": "Exercise improves cardiovascular health, strengthens muscles, boosts mental health, and helps maintain a healthy weight.",
    "how often should I exercise?": "It is recommended to exercise for at least 30 minutes most days of the week.",
    "what is a healthy weight?": "A healthy weight varies based on factors like age, height, and gender. You can use tools like BMI to get an estimate.",
    "how can I quit smoking?": "To quit smoking, consider using nicotine replacement therapy, seeking support from a counselor, or joining a support group.",
    "what are the benefits of meditation?": "Meditation can reduce stress, improve focus, enhance emotional health, and promote better sleep.",

    "i feel dizzy": "Dizziness can be caused by dehydration, low blood sugar, or other medical conditions. Sit down, drink water, and seek medical attention if it persists.",
    "i have chest pain": "Chest pain can be serious. If it is severe or accompanied by shortness of breath, seek emergency medical help immediately.",
    "i can't breathe": "Difficulty breathing is a medical emergency. Call emergency services or go to the nearest hospital right away.",
    "i have a high fever": "A high fever can be a sign of infection. Stay hydrated, take fever-reducing medication, and consult a doctor if it persists.",
    "i feel very sick": "If you feel very sick, it's important to rest, stay hydrated, and seek medical attention if symptoms worsen or persist.",

    "tell me a health tip": "A simple health tip is to drink a glass of water first thing in the morning to kickstart your metabolism and stay hydrated.",
    "what is mindfulness?": "Mindfulness is the practice of being fully present and engaged in the moment, which can help reduce stress and improve mental health.",
    "how do I stay healthy?": "To stay healthy, eat a balanced diet, exercise regularly, get enough sleep, avoid smoking, and manage stress.",
    "what is mental health?": "Mental health refers to your emotional, psychological, and social well-being. It affects how you think, feel, and act.",
    "how can I improve my mental health?": "To improve mental health, practice self-care, stay connected with loved ones, seek professional help if needed, and engage in activities you enjoy.",
}
def load_medical_keywords():
    default_keywords = [
        'headache', 'fever', 'cough', 'pain', 'covid', 'vaccine',
        'blood pressure', 'cholesterol', 'diabetes', 'asthma', 'rash',
        'infection', 'antibiotic', 'x-ray', 'mri', 'surgery', 'mental health',
        'anxiety', 'depression', 'heart', 'lung', 'liver', 'kidney', 'fracture',
        'virus', 'prescription', 'symptom', 'diagnosis', 'treatment', 'clinic',
        'hospital', 'emergency', 'doctor', 'pregnancy', 'injury', 'chest pain',
        'shortness of breath', 'fatigue', 'vomit', 'diarrhea', 'cancer',
        'chemotherapy', 'physical therapy', 'diet', 'nutrition', 'insomnia',
        'stroke', 'heart attack', 'migraine', 'dehydration', 'hypothermia',
        'bleeding', 'immune system', 'thyroid', 'insulin', 'obesity', 'uti',
        'kidney stone', 'transplant', 'rehabilitation', 'palliative', 'hospice',
        'medical history', 'genetic', 'pediatric', 'menopause', 'mammogram',
        'blood test', 'ct scan', 'ecg', 'anemia', 'leukemia', 'arrhythmia',
        'vaccination', 'cpr', 'first aid', 'insulin pump', 'bmi', 'calorie',
        'physical therapy', 'cognitive therapy', 'meditation', 'clinical trial',
        'pharmacy', 'dosage', 'side effects', 'pregnancy', 'lactation',
        'rehabilitation', 'telemedicine', 'genomics', 'clinical trial',
        'patient rights', 'epidemic', 'quarantine', 'medical research'
    ]
    
    try:
        with open(r'MediBot-main\chatbot\medical_keywords.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0].strip().lower() not in default_keywords:
                    default_keywords.append(row[0].strip().lower())
        print("Loaded medical keywords from CSV with default fallback.")
    except Exception as e:
        print(f"Error loading CSV: {e}. Using default keywords.")
    
    return default_keywords

medical_keywords = load_medical_keywords()

specific_commands = {
    # ... (keep your existing specific commands here)
}

def is_medical_query(query):
    query = query.lower()
    return any(keyword in query for keyword in medical_keywords)

def clean_response(response):
    response = re.sub(r"\*{2,}", "", response)
    return re.sub(r"\*", "", response)

def generate_text_response(prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return clean_response(response.text)
    except Exception as e:
        return f"Error generating response: {str(e)}"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_input = ""
    file = None

    if request.content_type.startswith('multipart/form-data'):
        user_input = request.form.get("message", "")
        file = request.files.get("file")
    else:
        data = request.get_json()
        user_input = data.get("message", "")

    if not user_input and not file:
        return jsonify({"response": "Please provide a message or file."})

    # Medical query validation
    if not file and not is_medical_query(user_input):
        return jsonify({"response": "I specialize in medical queries. Please ask health-related questions."})

    try:
        if file:
            filename = file.filename.lower()
            file_bytes = file.read()

            if filename.endswith(('.png', '.jpg', '.jpeg')):
                img = Image.open(io.BytesIO(file_bytes))
                model = genai.GenerativeModel('gemini-pro-vision')
                response = model.generate_content([
                    user_input or "Please analyze this medical image",
                    img
                ])
                return jsonify({"response": clean_response(response.text)})

            elif filename.endswith('.csv'):
                csv_content = file_bytes.decode('utf-8')
                prompt = f"Analyze this medical data:\n{csv_content}\n{user_input or 'Provide insights:'}"
                return jsonify({"response": generate_text_response(prompt)})

            elif filename.endswith('.txt'):
                text_content = file_bytes.decode('utf-8')
                prompt = f"Review this medical text:\n{text_content}\n{user_input or 'Summarize key points:'}"
                return jsonify({"response": generate_text_response(prompt)})

            elif filename.endswith('.pdf'):
                pdf_text = "\n".join([page.extract_text() for page in PdfReader(io.BytesIO(file_bytes)).pages])
                prompt = f"Analyze this medical document:\n{pdf_text}\n{user_input or 'Provide summary:'}"
                return jsonify({"response": generate_text_response(prompt)})

            return jsonify({"response": "Unsupported file type. Please upload PDF, image, CSV, or TXT."})

        else:
            # Handle text queries
            if user_input.lower() in specific_commands:
                return jsonify({"response": specific_commands[user_input.lower()]})
            
            prompt = f"Provide a concise medical answer to: {user_input}"
            return jsonify({"response": generate_text_response(prompt)})

    except Exception as e:
        return jsonify({"response": f"Error processing request: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)

