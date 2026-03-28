import os
import webbrowser
import pyttsx3
import speech_recognition as sr
from groq import Groq
import pyautogui
import time
from datetime import datetime
import requests
import sys
from dotenv import load_dotenv  

# .env file se API key load karne ke liye
load_dotenv()                  

# --- SETUP ---
# Groq client setup
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def speak(text):
    """Jarvis ko bulwane ke liye function"""
    if not text or text == "none": return
    print(f"Jarvis: {text}")
    engine = pyttsx3.init('sapi5')
    engine.setProperty('rate', 150) 
    engine.say(text)
    engine.runAndWait()

def get_weather():
    """Delhi ka weather fetch karne ke liye"""
    try:
        url = "https://wttr.in/Delhi?format=%C+%t"
        response = requests.get(url, timeout=5)
        return response.text
    except:
        return "not available"

def take_command():
    """User ki awaaz sunne ke liye function"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1.0  
        r.adjust_for_ambient_noise(source, duration=0.8) 
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=8)
            query = r.recognize_google(audio, language='en-IN')
            print(f"User: {query}")
            return query.lower()
        except:
            return "none"

def execute_task(query):
    """Commands ko execute karne ka logic"""
    
    # 1. SHUTDOWN
    if "shutdown" in query or "power off" in query:
        speak("Shutting down the system. Goodbye, Sir.")
        os.system("shutdown /s /f /t 5")
        sys.exit() 

    # 2. WEB OPENING (Direct Link Fix)
    elif "youtube" in query and "open" in query:
        speak("Opening YouTube, Sir.")
        webbrowser.open("https://www.youtube.com")
        return

    elif "google" in query and "open" in query:
        speak("Opening Google, Sir.")
        webbrowser.open("https://www.google.com")
        return

    # 3. TAB CONTROLS 
    elif "close tab" in query:
        speak("Closing tab.")
        pyautogui.keyDown('ctrl')
        pyautogui.press('w')
        pyautogui.keyUp('ctrl')
        return 

    elif "close all tab" in query:
        speak("Closing all browser windows.")
        os.system("taskkill /f /im chrome.exe /im msedge.exe /im brave.exe")
        return

    # 4. TIME & WEATHER 
    elif "time" in query:
        now = datetime.now().strftime("%I:%M %p")
        speak(f"Sir, it is {now}.")
        return

    elif "weather" in query:
        info = get_weather()
        speak(f"The weather in Delhi is {info}, Sir.")
        return

    # 5. VOLUME & MUSIC 
    elif "volume up" in query:
        pyautogui.press("volumeup", presses=10)
        return
    elif "volume down" in query:
        pyautogui.press("volumedown", presses=10)
        return
    
    elif "play" in query:
        song = query.replace("play", "").replace("jarvis", "").strip()
        speak(f"Playing {song} on YouTube.")
        webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
        time.sleep(8) 
        pyautogui.click(x=600, y=400) 
        pyautogui.press("enter")
        return

    # 6. OPEN APPS
    elif "open" in query:
        app = query.replace("open", "").replace("jarvis", "").strip()
        if "whatsapp" in app:
            os.system("start whatsapp:")
        else:
            os.system(f"start {app}")
        return

    # 7. AI CHAT
    elif query != "none":
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are Jarvis. ALWAYS reply in English. Max 10 words. Use 'Sir' once."},
                    {"role": "user", "content": query}
                ],
                model="llama-3.1-8b-instant",
                timeout=10.0
            )
            speak(chat_completion.choices[0].message.content)
        except:
            speak("Network error, Sir.")

# --- MAIN LOOP ---
if __name__ == "__main__":
    is_awake = False
    print("Jarvis Standby. Say 'Jarvis On' to start.")
    
    while True:
        query = take_command()
        
        if query == "none":
            continue

        # 1. WAKE UP LOGIC (Fixed to stop double speaking)
        if "jarvis on" in query:
            if not is_awake:
                is_awake = True
                speak("I am online. Ready, Sir.")
            else:
                speak("I am already online, Sir.")
            continue  
        
        # 2. SLEEP LOGIC
        elif "jarvis off" in query:
            is_awake = False
            speak("Going to standby.")
            continue
            
        # 3. COMMAND EXECUTION
        elif is_awake and "jarvis" in query:
            clean_query = query.replace("jarvis", "").strip()
            if clean_query != "":
                execute_task(clean_query)