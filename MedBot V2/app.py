from flask import Flask, request, jsonify, render_template
import google.generativeai as genai  # Import the Gemini library
import time  # For simulating delays
import csv  # For reading the CSV file
from flask_cors import CORS  # Enable CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini API
genai.configure(api_key="AIzaSyDZKcpO0SBr87s_sTBOjOJoEQzsvOZp0Hs")

# Load medical keywords from CSV
def load_medical_keywords():
    medical_keywords = []
    with open('medical_keywords.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            medical_keywords.append(row[0].strip().lower())  # Add each keyword to the list
    return medical_keywords

# Load the medical keywords
medical_keywords = load_medical_keywords()

# Specific commands for the chatbot
specific_commands = {
    # Greetings and General Questions
    "hello": "Hi! How can I assist you with your health concerns today?",
    "hi": "Hello! I'm here to help with any medical questions you have.",
    "what can you do?": "I can provide information on health and medical topics. Just ask me anything!",
    "what is your name?": "I am MediBot, your virtual medical assistant.",
    "who created you?": "I was developed by a team of healthcare and technology professionals to assist with medical queries.",
    "how are you?": "I'm just a bot, but I'm here and ready to help you with your health questions!",
    "thank you": "You're welcome! If you have more questions, feel free to ask.",
    "thanks": "You're welcome! Let me know if there's anything else I can assist you with.",
    "bye": "Goodbye! Take care and stay healthy!",
    "goodbye": "Goodbye! Wishing you good health!",

    # Common Medical Queries
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

    # General Health Tips
    "how can I improve my sleep?": "To improve sleep, maintain a regular sleep schedule, avoid caffeine before bed, create a comfortable sleep environment, and limit screen time before bed.",
    "what are the benefits of exercise?": "Exercise improves cardiovascular health, strengthens muscles, boosts mental health, and helps maintain a healthy weight.",
    "how often should I exercise?": "It is recommended to exercise for at least 30 minutes most days of the week.",
    "what is a healthy weight?": "A healthy weight varies based on factors like age, height, and gender. You can use tools like BMI to get an estimate.",
    "how can I quit smoking?": "To quit smoking, consider using nicotine replacement therapy, seeking support from a counselor, or joining a support group.",
    "what are the benefits of meditation?": "Meditation can reduce stress, improve focus, enhance emotional health, and promote better sleep.",

    # Emergency Responses
    "i feel dizzy": "Dizziness can be caused by dehydration, low blood sugar, or other medical conditions. Sit down, drink water, and seek medical attention if it persists.",
    "i have chest pain": "Chest pain can be serious. If it is severe or accompanied by shortness of breath, seek emergency medical help immediately.",
    "i can't breathe": "Difficulty breathing is a medical emergency. Call emergency services or go to the nearest hospital right away.",
    "i have a high fever": "A high fever can be a sign of infection. Stay hydrated, take fever-reducing medication, and consult a doctor if it persists.",
    "i feel very sick": "If you feel very sick, it's important to rest, stay hydrated, and seek medical attention if symptoms worsen or persist.",

    # Miscellaneous
    "tell me a health tip": "A simple health tip is to drink a glass of water first thing in the morning to kickstart your metabolism and stay hydrated.",
    "what is mindfulness?": "Mindfulness is the practice of being fully present and engaged in the moment, which can help reduce stress and improve mental health.",
    "how do I stay healthy?": "To stay healthy, eat a balanced diet, exercise regularly, get enough sleep, avoid smoking, and manage stress.",
    "what is mental health?": "Mental health refers to your emotional, psychological, and social well-being. It affects how you think, feel, and act.",
    "how can I improve my mental health?": "To improve mental health, practice self-care, stay connected with loved ones, seek professional help if needed, and engage in activities you enjoy.",
}

# Check if the query is medical-related
def is_medical_query(query):
    return any(keyword in query.lower() for keyword in medical_keywords)

# Chatbot function
def medical_chatbot(query):
    query_lower = query.lower()

    # Check for specific commands
    if query_lower in specific_commands:
        return specific_commands[query_lower]
    
    # Check if the query is medical-related
    if not is_medical_query(query_lower):
        return "Sorry, I can only answer health or medical-related questions."
    
    # Generate a response using Gemini API
    try:
        model = genai.GenerativeModel('gemini-pro') 
        response = model.generate_content(
            f"Provide a point-wise answer to the following medical query.. User query: {query}"
        )
        # Extract the bot's response
        bot_response = response.text

        # Format the response as point-wise
        if "\n" in bot_response:
            bot_response = bot_response.replace("\n", "<br>")  # Convert newlines to HTML line breaks
        else:
            bot_response = f"- {bot_response}"  # Add a bullet point if no newlines

        # Add a closing message
        bot_response += "<br><br>Let me know if you have more questions!"

        return bot_response
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Route for the home page
@app.route("/")
def home():
    return render_template("index.html")

# Route for handling chatbot queries
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"response": "Please provide a valid query."})
    
    # Simulate a delay to mimic thinking
    time.sleep(1)  # 1-second delay
    
    # Get the bot's response
    bot_response = medical_chatbot(user_input)
    return jsonify({"response": bot_response})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)