import pygame
import webbrowser
import speech_recognition as sr
from jokeapi import Jokes 
import asyncio
import requests
import json


with open("speech_assistant/passwords.json", mode='r') as file:
    data = json.load(file)
    newsApi = data['news_api_key']
    weatherApi = data['weather_api_key']


def get_news(key = newsApi):
    url = f"https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey={newsApi}"
    response = requests.get(url)
    data = json.loads(response.text)
    if response.status_code == 200:
        c = 0
        URLs = []
        for article in data['articles']:
            if c < 5:
                description = article['description']
                url = article['url']
                speak(f"{c+1}: {description}")
                URLs.append(url)
                c += 1
        speak("Here are the URLs of the news articles")
        print("Here are the URLs of the news articles:", URLs)
    else:
        print("Error fetching news data")


# Function to get tempreture, feels like and condition
def get_weather(city, key = weatherApi):
    url =f"https://api.weatherapi.com/v1/current.json?q={city}&lang=en&key={key}"
    response = requests.get(url)
    data = json.loads(response.text)
    if response.status_code == 200:
        location = data['location']['name']
        country = data['location']['country']
        temp_c = data['current']['temp_c']
        condition = data['current']['condition']['text']

        speak(f"Tempreture in {location} {country} is {temp_c} degree celsius and Condition is {condition}")
    else:
        speak("Error fetching weather data")

#function to get jokes
async def speak_joke():
    j = await Jokes()  # Initialise the class
    joke = await j.get_joke()  # Retrieve a random joke
    if joke["type"] == "single": # Print the joke
        speak(joke["joke"])
    else:
        speak(joke["setup"])
        speak(joke["delivery"])

#function to get quotes
def get_quotes():
    url ="https://zenquotes.io/api/random"
    response = requests.get(url)
    data = json.loads(response.text)
    if response.status_code == 200:
        quote = data[0]['q']
        speak(quote)
    else:
        speak("Error fetching quotes")

def audio_search():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            speak("How can I help you....!")
            audio_file_raw = recognizer.listen(source)
            audio_file = recognizer.recognize_google(audio_file_raw)
            if audio_file == "how can you help me":
                speak("1. I can search for you on the web/" \
                "2. I can tell you the time/" \
                "3. I can tell you the date/" \
                "4. I can tell you the weather/" \
                "5. I can tell you the news/" \
                "6. I can tell you the jokes/" \
                "7. I can tell you the quotes/")

            if audio_file == "search":
                speak("What do you want to search for?")
                audio_file_raw = recognizer.listen(source)
                audio_file = recognizer.recognize_google(audio_file_raw)
                speak(f"Searching for {audio_file}, Here is your search result")
                url = f"https://www.google.com/search?q={audio_file}"
                webbrowser.open(url)

            if audio_file == "tell me the time":
                from datetime import datetime
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                speak(f"The current time is {current_time}")

            if audio_file == "tell me the date":    
                from datetime import datetime
                now = datetime.now()
                current_date = now.strftime("%Y-%m-%d")
                speak(f"The current date is {current_date}")

            if audio_file == "tell me the weather":
                speak("Please tell me the city name")
                audio_file_raw = recognizer.listen(source)
                city_name = recognizer.recognize_google(audio_file_raw)
                get_weather(city_name)

            if audio_file == "tell me the news":
                get_news()

            if audio_file == "tell me the jokes":
                asyncio.run(speak_joke())   

            if audio_file == "tell me the quotes":
                get_quotes()

    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
    except Exception as e:
        speak(f"An error occurred: {e}")
    finally:
        speak("Audio search completed.")
            
        # print(audio_file)
        
#this speak anything passeed to it
def speak(text):
    from gtts import gTTS
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue


while True:
    audio_search()