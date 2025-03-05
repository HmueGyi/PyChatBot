import speech_recognition
import pyttsx3
from flask import Flask, request, jsonify
import re
import requests
import json
from datetime import datetime
import sqlite3
import pytz
from flask_cors import CORS
from threading import Timer
from datetime import timedelta
import webbrowser
# import ollama
import queue
import threading
from threading import Timer
from sympy import sympify
from sympy.core.sympify import SympifyError
import openai
import pyttsx3 

from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

recognizer = speech_recognition.Recognizer()

time_cache = {}

WEATHER_API_KEY = "KEe0z5e5I3ZPg7RtBMkMpbbtlTf6ehPY"
TIME_API_KEY = "NRAAR8CPW8DV"
DEFAULT_CITY ="pathein"
openai.api_key = "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" 



# Load timezone data
try:
    with open("cities_timezones.json", "r") as file:
        city_timezone_map = json.load(file)
except FileNotFoundError:
    city_timezone_map = {}
    print("Error: 'cities_timezones.json' file not found.")

# Initialize database
conn = sqlite3.connect("meetings.db", check_same_thread=False)
cursor = conn.cursor()

waiting_for_meeting_info = {}
meeting_details = {}

def initialize_database():
    cursor.execute('''CREATE TABLE IF NOT EXISTS meetings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL)''')
    conn.commit()


def initialize_reminder_table():
    cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        reminder_time TEXT NOT NULL
    )''')
    conn.commit()

initialize_database()
initialize_reminder_table()


# def ask_ai(question):
#     isLongAns = re.search(r'tell more|tell me more|long answer|completely', question)
#     prompt = question if isLongAns else "Please explain briefly in short: '"+question+"'."
#     response = ollama.generate(model="llama3.2",prompt=prompt)
#     isProgramPrompt = re.search(r'code in|write a|write a|program in',question)
#     mode = "shortText" if (len(response['response'])<300) else "longText"
#     return response['response'], mode


def ask_openai(question):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Use the latest model available to you
        messages=[
            {"role": "user", "content": question}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

def chatbot_response(user_input, user_id="default"):
    user_input = user_input.lower().strip()

    mode = "neutral"  # Default mode

    # Define patterns
    greeting_pattern = re.compile(
    r'.*?^\b(?:hi|hello|hey|hiya|howdy|what\'s up|good (morning|afternoon|evening))\b$',
    re.IGNORECASE
    )

    name_pattern = re.compile(
    r'.*?\b(?:what(?:\'s| is) your name|how can I call you|who are you|tell me your name|your name please|may I know your name)\b',
    re.IGNORECASE
)
    
    feel_pattern = re.compile(
        r'\b(?:how are you|your name please|may I know your name)\b',
        re.IGNORECASE
    )

    # Compliments (Bot Responds Happily)
    compliment_pattern = re.compile(
    r'.*?\b(?:'
    r'(?:you\s*look|you\s*are|you\'re)\s*'
    r'(?:pretty|beautiful|gorgeous|amazing|wonderful|cute|adorable|stunning|lovely|charming|radiant|attractive|smart|intelligent|kind|sweet|thoughtful|awesome|perfect)'
    r'|i like you|i love you|(you\'re|you are) the best'
    r')\b',
    re.IGNORECASE
)

    # Insults (Bot Sulks or Gets Sad)
    insult_pattern = re.compile(
    r'.*?\b(?:'
    r'(?:you\s*look|you\s*are|you\'re)\s*'
    r'(?:ugly|stupid|dumb|annoying|boring|horrible|terrible|gross|weird|disgusting|creepy|lame|useless|pathetic|idiot|awful)'
    r'|i hate you|shut up bot'
    r')\b',
    re.IGNORECASE
)

    # Emotional Patterns
    happiness_pattern = re.compile(r'.*?\b(?:I am happy|I feel happy|happy|joyful|excited|fantastic|awesome|wonderful|great|ecstatic|elated|thrilled|cheerful|delighted|overjoyed)\b', re.IGNORECASE)
    sadness_pattern = re.compile(r'.*?\b(?:I am sad|I feel sad|sad|depressed|unhappy|miserable|crying|lonely|hopeless|heartbroken|downcast|melancholy|blue|despondent)\b', re.IGNORECASE)
    fear_pattern = re.compile(r'.*?\b(?:I am scared|I feel scared|scared|afraid|terrified|fearful|worried|anxious|nervous|panicked|petrified|uneasy|apprehensive)\b', re.IGNORECASE)
    anger_pattern = re.compile(r'.*?\b(?:I am angry|I feel angry|angry|mad|furious|frustrated|annoyed|irritated|outraged|resentful|fuming|infuriated|enraged)\b', re.IGNORECASE)
    surprise_pattern = re.compile(r'.*?\b(?:I am surprised|I feel surprised|shocked|surprised|amazed|incredible|unbelievable|stunned|astonished|dumbfounded|flabbergasted|astounded)\b', re.IGNORECASE)
    disgust_pattern = re.compile(r'.*?\b(?:I am disgusted|I feel disgusted|disgusting|gross|revolting|sickening|repulsive|vile|nauseating|abhorrent|horrid)\b', re.IGNORECASE)
    thanks_pattern = re.compile(r'.*?\b(?:thank you|thanks|appreciate it|grateful)\b', re.IGNORECASE)


    # Responses Based on Detected Emotion
    if greeting_pattern.search(user_input):
        return "Hello! How can I assist you today?", mode
    if name_pattern.search(user_input):
        return "Hello! I'm PyChat. What is your day?", mode
    if feel_pattern.search(user_input):
        return "I'm good! How about you?", mode
    if compliment_pattern.search(user_input):
        mode = "happiness"
        return "Aww, thank you! That made my day!", mode
    if insult_pattern.search(user_input):
        mode = "sadness"
        return "That hurts... Why would you say that?", mode
    if happiness_pattern.search(user_input):
        return "That sounds great! Keep up the positive vibes!", mode
    if sadness_pattern.search(user_input):
        return "I'm sorry to hear that. I'm here for you.", mode
    if fear_pattern.search(user_input):
        return "That sounds scary. Stay strong, you're not alone.", mode
    if anger_pattern.search(user_input):
        mode = "angry"
        return "I understand your frustration. Take a deep breath, let's talk.", mode
    if surprise_pattern.search(user_input):
        return "Wow! That sounds shocking! Tell me more.", mode
    if disgust_pattern.search(user_input):
        return "That sounds awful. I hope things get better.", mode
    if thanks_pattern.search(user_input):
        return "You're very welcome! I'm happy to help. 😊", mode


    # Check for specific commands
    if re.search(r'.*?\b(open|visit)\b', user_input, re.IGNORECASE):
        website = user_input.split("open ")[-1].strip()  # Extract website name
        webbrowser.open(f"https://www.{website}.com")
        return f"Here is {website}, and {website} is open!", mode

    if re.search(r'.*?\b(?:open|visit|launch|access|navigate\s*to)?\s*(lms\.pathein\.edu\.mm)\b',
    user_input, 
    re.IGNORECASE):
        webbrowser.open("http://lms.ucspathein.edu.mm")
        return "Here is lms.ucspathein.edu.mm", mode
    
    search_query = None  # Default to None

    # Case 1: "search [query] on google"
    match_google = re.search(
    r'.*?\b(?:search|find|look\s*up|google)\s+(?:for\s+)?(.+?)(?:\s*\b(?:on\s+google)?)?\b',
    user_input, 
    re.IGNORECASE
)
    if match_google:
        search_query = match_google.group(1)

    # Case 2: "search [query]" (without 'on google')
    elif re.search(r'.*?\b(?:search|find)\s+(.+)', user_input, re.IGNORECASE):
        search_query = re.search(r'\b(?:search|find)\s+(.+)', user_input, re.IGNORECASE).group(1)

    # Only proceed if a valid search query was found
    if search_query:
        search_query = re.sub(r'(\w)([A-Z])', r'\1 \2', search_query)
        
        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"Here are the search results for '{search_query}'!",mode

    # Weather and time inquiries
    if re.search(r'.*?\b(weather\s\'?s?\s+weather|current\s+weather)\b', user_input, re.IGNORECASE):
        return get_weather_today(DEFAULT_CITY), mode

    if re.search(r'.*?\b(time\s+now|what\s+time\s+is\s+it)\b', user_input, re.IGNORECASE):
        return get_time_today(DEFAULT_CITY), mode

    # Meeting scheduling logic
    


    if user_id in meeting_details and "name" in meeting_details[user_id] and "datetime" not in meeting_details[user_id]:
        match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4}) (\d{1,2}):(\d{2}) (AM|PM|am|pm)', user_input)
        if match:
            day, month, year, hour, minute, am_pm = match.groups()
            meeting_datetime = datetime.strptime(f"{day}/{month}/{year} {hour}:{minute} {am_pm.upper()}", "%d/%m/%Y %I:%M %p")
            save_meeting(meeting_details[user_id]["name"], meeting_datetime.strftime("%d/%m/%Y"), meeting_datetime.strftime("%I:%M %p"))
            response_message = f"Meeting '{meeting_details[user_id]['name']}' saved successfully!"
            del meeting_details[user_id]
            return response_message, mode
        else:
            return "Please provide the meeting date and time in the correct format.", mode

    if user_id in waiting_for_meeting_info and waiting_for_meeting_info[user_id]:
        meeting_details[user_id] = {"name": user_input}
        waiting_for_meeting_info[user_id] = False
        return f"Got it! Meeting name is '{user_input}'. Now provide the date and time (e.g., 10/10/2025 10:00 AM).", mode

    if re.search(r'.*?\bmeetings?\s+(today|tomorrow|yesterday)\b', user_input, re.IGNORECASE):
        day = re.search(r'\bmeetings?\s+(today|tomorrow|yesterday)\b', user_input, re.IGNORECASE).group(1)
        mode="table"
        return get_meetings(specific_day=day), mode

    if re.search(r'.*?\b(?:have|any|my|scheduled|upcoming|existing|next)\s+(?:meetings?|appointments?)\b', user_input, re.IGNORECASE):
        mode="table"
        return get_meetings(show_all=False), mode

    if re.search(r'.*?\b(?:show\s+all\s+meetings?)\b', user_input, re.IGNORECASE):
        mode="table"
        return get_meetings(show_all=True), mode

    if re.search(r'.*?\b(?:schedule|set up|create|plan|arrange|make|organize|book|fix|reserve|I need to plan|i want to add|i wanna add)\s+(?:a|an)?\s*(?:meeting|appointment|event|call)\b', user_input, re.IGNORECASE):
        waiting_for_meeting_info[user_id] = True
        return "Let's schedule a meeting! First, tell me the meeting name.", mode

    if re.search(r'.*?\bplay\s*:? ?(?:game|games|a game|the game)\b',user_input,re.IGNORECASE):
        mode="game"
        return "Let's play",mode

    # Reminder functionality
    match = re.search(r'remind me (.*?) at (\d{1,2}:\d{2}\s?(?:am|pm))', user_input, re.IGNORECASE)
    if match:
        task = match.group(1)
        time_str = match.group(2)
        
        today = datetime.now().strftime("%d/%m/%Y")
        reminder_time = f"{today} {time_str.upper()}"
        save_reminder(task, reminder_time)
        return f"Reminder set for '{task}' at {time_str} today.", mode

    match = re.search(r'remind me to (.*?) tomorrow at (\d{1,2}:\d{2}\s?(?:am|pm))', user_input, re.IGNORECASE)
    if match:
        task = match.group(1)
        time_str = match.group(2)
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
        reminder_time = f"{tomorrow} {time_str.upper()}"
        save_reminder(task, reminder_time)
        return f"Reminder set for '{task}' at {time_str} tomorrow.", mode

    # Weather inquiries
    weather_patterns = [
    r'(?:.*?\b(?:what(?:\'?s|\s*is)?\s+the\s+weather\s+like\s+in\s+([\w\s]+))\b.*)',
    r'(?:.*?\b(?:weather\s+in\s+([\w\s]+))\b.*)',
    r'(?:.*?\b(?:tell\s+me\s+the\s+weather\s+for\s+([\w\s]+))\b.*)',
    r'(?:.*?\b(?:current\s+weather\s+in\s+([\w\s]+))\b.*)'
]
    for pattern in weather_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            return get_weather(city), mode

    # Time inquiries
    time_patterns = [
    r'.*?\b(?:what(?:\'?s|\s*is)?\s+the\s+time\s+in\s+([\w\s]+))\b',
    r'.*?\b(?:current\s+time\s+in\s+([\w\s]+))\b',
    r'.*?\b(?:tell\s+me\s+the\s+time\s+in\s+([\w\s]+))\b',
    r'.*?\b(?:time\s+in\s+([\w\s]+))\b'
    ]
    for pattern in time_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            return get_time(city), mode
    
   # Calculation inquiries
    calc_patterns = [
        r'\b(?:what(?:\'?s|\s+is)?|calculate|solve|compute|evaluate|find|the\s+result\s+of|can\s+you\s+calculate)?\s*([\d\+\-\*/\^eE\(\)\.\s]+)\??'
    ]
    # Calculation inquiries
    calc_patterns = [
    r'^\s*(?:what(?:\'?s|\s+is)?|calculate|solve|compute|evaluate|find|the\s+result\s+of|can\s+you\s+calculate)?\s*'
    r'(\(?\s*-?\d+(\.\d+)?\s*([-+*/^]\s*-?\d+(\.\d+)?\s*)*\)?'
    r'|\(?\s*(?:sqrt|sin|cos|tan|log|ln|exp)\s*\(\s*-?\d+(\.\d+)?\s*\)\s*\)?)\s*\??\s*$'
]
    for pattern in calc_patterns:
        match = re.fullmatch(pattern, user_input, re.IGNORECASE)
        if match:
            expression = match.group(1).strip().replace('=', '')
            return calculate_expression(expression), mode  # Handle calculations properly

    other_response = ask_openai(user_input)
    return other_response, mode

def save_meeting(title, date, time):
    cursor.execute("INSERT INTO meetings (title, date, time) VALUES (?, ?, ?)", (title, date, time))
    conn.commit()


def get_meetings(show_all=False, today_only=False, specific_day=None):
    cursor.execute("SELECT title, date, time FROM meetings ORDER BY date, time")
    meetings = cursor.fetchall()

    if not meetings:
        return "You have no meetings scheduled."

    today_date = datetime.now().strftime("%d/%m/%Y")  # Ensure today_date is calculated
    
    # Handle specific days
    if specific_day == "today":
        date_to_check = today_date
    elif specific_day == "tomorrow":
        date_to_check = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
    elif specific_day == "yesterday":
        date_to_check = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    elif specific_day == "this week":
        # Calculate the start of the week (Monday) and end of the week (Sunday)
        start_of_week = datetime.now() - timedelta(days=datetime.now().weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday

        start_of_week_str = start_of_week.strftime("%d/%m/%Y")
        end_of_week_str = end_of_week.strftime("%d/%m/%Y")
    else:
        date_to_check = None

    response = ""
    meetings_found = False  # Flag to track if any meetings are found

    for title, date, time in meetings:
        if specific_day == "this week":
            # Check if the meeting falls within this week range
            if start_of_week_str <= date <= end_of_week_str:
                meeting_datetime = datetime.strptime(f"{date} {time}", "%d/%m/%Y %I:%M %p")
                day_of_week = meeting_datetime.strftime("%A")  # Get day of the week
                response += f"- {title} {date} {time} on {day_of_week}\n"
                meetings_found = True
        elif specific_day in ["today", "tomorrow", "yesterday"]:
            # Handle today, tomorrow, yesterday for specific day checks
            if date == date_to_check:
                meeting_datetime = datetime.strptime(f"{date} {time}", "%d/%m/%Y %I:%M %p")
                day_of_week = meeting_datetime.strftime("%A")  # Get day of the week
                response += f"- {title} {date} {time} on {day_of_week}\n"
                meetings_found = True
        elif today_only:
            # Only show today's meetings
            if date == today_date:
                meeting_datetime = datetime.strptime(f"{date} {time}", "%d/%m/%Y %I:%M %p")
                day_of_week = meeting_datetime.strftime("%A")  # Get day of the week
                response += f"- {title} {date} {time} on {day_of_week}\n"
                meetings_found = True
        elif show_all or datetime.strptime(date, "%d/%m/%Y") >= datetime.strptime(today_date, "%d/%m/%Y"):
            # Show all or future meetings
            meeting_datetime = datetime.strptime(f"{date} {time}", "%d/%m/%Y %I:%M %p")
            day_of_week = meeting_datetime.strftime("%A")  # Get day of the week
            response += f"- {title} {date} {time} on {day_of_week}\n"
            meetings_found = True

    if not meetings_found:
        if today_only:
            return "You don't have any meetings today."  # If no meetings today
        elif specific_day == "tomorrow":
            return "You don't have any meetings tomorrow."  # If no meetings tomorrow
        elif specific_day == "yesterday":
            return "You don't have any meetings yesterday."  # If no meetings yesterday
        else:
            return "You have no upcoming meetings."  # For other cases

    # Singular/Plural Adjustment for Response
    if response.strip():
        if response.count('\n') == 1:
            return f"You have 1 meeting :\n{response.strip()}"
        else:
            return f"You have the following meetings :\n{response.strip()}"

    # Handle responses when no meetings are found
    if specific_day == "today" and not response:
        return "You don't have any meeting today."  # If no meetings today
    elif specific_day == "yesterday" and not response:
        return "You don't have any meeting yesterday."  # If no meetings yesterday
    elif specific_day == "tomorrow" and not response:
        return "You don't have any meeting tomorrow."  # If no meetings tomorrow
    elif today_only and not response:
        return "You don't have any meeting today."  # If no meetings today
    elif not response:
        if show_all:
            return "You have no upcoming meetings."
        return "You have no meetings scheduled."
    
    return response.strip()



def save_reminder(task, reminder_time):
    try:
        cursor.execute("INSERT INTO reminders (task, reminder_time) VALUES (?, ?)", (task, reminder_time))
        conn.commit()
        schedule_reminder(task, reminder_time)
    except Exception as e:
        print(f"Error saving reminder: {e}")
# Initialize the speech engine
engine = pyttsx3.init()
speak_queue = queue.Queue()

def speak_worker():
    """ Continuously process speech requests from the queue. """
    while True:
        text = speak_queue.get()
        if text is None:
            break  # Stop the thread if None is received
        try:
            engine.say(text)
            engine.runAndWait()  # This is blocking
        except Exception as e:
            print(f"Error during speech: {e}")
        finally:
            speak_queue.task_done()

# Start the speech thread
speech_thread = threading.Thread(target=speak_worker, daemon=True)
speech_thread.start()

def speak(text):
    """ Add text to the speech queue. """
    speak_queue.put(text)

def notify_user(task, reminder_datetime):
    reminder_time_str = reminder_datetime.strftime("%I:%M %p")  # Format the time
    message = f"Don't forget {task} at {reminder_time_str} today."
    print(message)
    speak(message)  # Speak the reminder

def schedule_reminder(task, reminder_time):
    reminder_datetime = datetime.strptime(reminder_time, "%d/%m/%Y %I:%M %p")
    now = datetime.now()
    
    if reminder_datetime < now:
        print(f"Error: The reminder time '{reminder_time}' is in the past.")
        return

    time_until_reminder = (reminder_datetime - now).total_seconds()
    
    if time_until_reminder > 0:  # Schedule the reminder
        print(f"Scheduling reminder for '{task}' at {reminder_time}.")
        Timer(time_until_reminder, notify_user, [task, reminder_datetime]).start()  # Pass both arguments


def get_weather(city):
    try:
        location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={WEATHER_API_KEY}&q={city}"
        location_response = requests.get(location_url)
        location_data = location_response.json()

        if location_response.status_code == 200 and location_data:
            location_key = location_data[0]['Key']
            weather_url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={WEATHER_API_KEY}"
            weather_response = requests.get(weather_url)
            weather_data = weather_response.json()

            if weather_response.status_code == 200 and weather_data:
                temp = weather_data[0]['Temperature']['Metric']['Value']
                weather_text = weather_data[0]['WeatherText']
                return f"The current temperature in {city} is {temp}°C with {weather_text}."
        return "Sorry, I couldn't fetch the weather data."
    except Exception as e:
        return f"An error occurred while fetching weather info: {e}"

def get_time(city):
    global time_cache
    city = city.lower()
    if city in time_cache:
        return time_cache[city]

    try:
        timezone = city_timezone_map.get(city)
        if not timezone:
            return "Sorry, I couldn't find the timezone for the specified city."

        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        formatted_time = now.strftime("%d/%m/%Y %I:%M %p")

        time_cache[city] = f"The current time in {city.title()} is {formatted_time}."
        return time_cache[city]
    except Exception as e:
        return f"An error occurred while fetching the time: {e}"
    

def get_weather_today(city):
    try:
        location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={WEATHER_API_KEY}&q={city}"
        location_response = requests.get(location_url)
        location_data = location_response.json()

        if location_response.status_code == 200 and location_data:
            location_key = location_data[0]['Key']
            weather_url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={WEATHER_API_KEY}"
            weather_response = requests.get(weather_url)
            weather_data = weather_response.json()

            if weather_response.status_code == 200 and weather_data:
                temp = weather_data[0]['Temperature']['Metric']['Value']
                weather_text = weather_data[0]['WeatherText']
                return f"Today's current temperature is {temp}°C with {weather_text}."
        return "Sorry, I couldn't fetch the weather data."
    except Exception as e:
        return f"An error occurred while fetching weather info: {e}"

def get_time_today(city):
    global time_cache
    city = city.lower()
    if city in time_cache:
        return time_cache[city]

    try:
        timezone = city_timezone_map.get(city)
        if not timezone:
            return "Sorry, I couldn't find the timezone for the specified city."

        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        formatted_time = now.strftime("%d/%m/%Y %I:%M %p")

        time_cache[city] = f"Today's current time is {formatted_time}."
        return time_cache[city]
    except Exception as e:
        return f"An error occurred while fetching the time: {e}"

def calculate_expression(expression):
    try:
        result = sympify(expression, evaluate=True)

        # Convert to float if it's a fraction but keep integers as integers
        if result.is_number and result.is_rational:
            if not result.is_integer:
                result = float(result)
                return f"The result of {expression} is {result:.3f}"  # Removes unnecessary trailing zeros
            else:
                result = int(result)

        return f"The result of {expression} is {result}."
    
    except SympifyError:
        return "I couldn't understand the mathematical expression. Please try again with a valid format."
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")
    user_id = data.get("user_id", "default")
    
    # Ensure the function returns a tuple
    response, mode = chatbot_response(user_message, user_id)

    return jsonify({"response": response, "mode": mode})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
