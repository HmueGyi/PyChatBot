# PyChatBot

![PyChatBot](https://pychatbot.com)  
_A smart chatbot powered by NLP and AI_

## 🚀 Features
- 🌐 **Weather Updates** (Integrated with AccuWeather API)
- 🌐 **Global Time Updates** (Integrated with Timezonedb API)
- 🤖 **Supports General Knowledge Queries** (Openai API)
- 📅 **Meeting & Reminder System** (Stores in Database)
- 🗣️ **Speech-to-Text** 
- 🎭 **Emotional Responses** (Happy, Sad, etc.)
- 🎙️ **Voice-Based Responses** (Male Voice, 20-30 Age)

---

## 📦 Installation

### **1. Clone the Repository**
```bash
git clone https://github.com/HmueGyi/PyChatBot.git
cd PyChatBot
```

### **2. Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate    # Windows
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Set Up API Keys**
- Create a `.env` file in the project root and add:
  ```
  ACCUWEATHER_API_KEY=your_accuweather_api_key
  timezonedb_API_KEY=your_timezonedb_api_key
  OPENAI_API_KEY=your_openai_api_key

  ```

---

## 🎮 Usage

### **Run the Chatbot**
```bash
python Services.py
```

### **Example Queries**
- "What’s the weather in Pathein?"
- "Remind me to call John at 3:30 PM."
- "Who is the president of USA?"
- "Tell me a joke!"
- "I am happy today"
- "Tell me the time in japan"
- "I want to play game"
- "Do i have meetings" that (need to be insert data on database) eg.plan meeting.first you need to add meeting name and then you need to add meeting date and time.

---

## 🛠️ Technologies Used
- **Python** (Core Language)
- **Flask** (Backend)
- **OpenAI API**
- **timezonedb API**
- **AccuWeather API**
- **SQLite** (Database)

---

## 🤝 Contributing
Feel free to fork this repository and submit pull requests! If you find any bugs or have feature requests, please open an issue.

---

## 📜 License
This project is licensed under the MIT License.

---

## 📧 Contact
- Developer: **Hmue Gyi and Yaachay**
- Email: hmuesett2002@gmail.com
- GitHub: [Hmue_Gyi](https://github.com/HmueGyi)

---

_💡 Built with ❤️ by PyChatBot Team. my friend :(https://github.com/yaachay)_


