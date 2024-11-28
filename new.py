import speech_recognition as sr
import pyttsx3
import requests

# Initialize the speech engine
engine = pyttsx3.init()

# Function to capture microphone input and convert to text
def listen_and_recognize():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand the audio.")
            return None
        except sr.RequestError:
            print("Sorry, there was an issue with the speech recognition service.")
            return None

# Function to send the recognized text to the Friday instance and get a response
def query_friday(text):
    url = "http://localhost:11434/v1/chat" 
    payload = {
        "model": "llama2",
        "prompt": text
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            print("Error with Friday API")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to convert text to speech
def speak_text(text):
    engine.say(text)
    engine.runAndWait()

# Main function to handle the speech-to-text, query Friday, and text-to-speech workflow
def main():
    while True:
        print("\nSay something...")
        user_input = listen_and_recognize()
        if user_input:
            # Send the input to the Friday instance
            response = query_friday(user_input)
            if response:
                print(f"Ollama: {response}")
                # Convert Friday's response to speech
                speak_text(response)
            else:
                print("No response from Friday")
        else:
            print("Please try speaking again.")
        print("Listening again... (Press Ctrl+C to exit)")

if __name__ == "__main__":
    main()
