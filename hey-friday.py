import speech_recognition as sr
import pyttsx3
import requests
import json

# Initialize the speech engine
engine = pyttsx3.init()

# Set speech rate and volume (optional adjustments)
engine.setProperty('rate', 160)    # Increased speed of speech
engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)

# Function to capture microphone input and process speech after a short pause
def listen_and_recognize():
    recognizer = sr.Recognizer()
    
    # Lower energy threshold to make the mic more sensitive to quieter sounds
    recognizer.energy_threshold = 150  # Adjust sensitivity (lower means more sensitive)
    recognizer.pause_threshold = 0.8  # Shorten pause detection to make it more responsive
    
    with sr.Microphone() as source:
        print("Listening... (Pause to indicate you're done speaking)")
        
        # Optional: Comment this out if the environment is quiet enough
        # recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)  # Set timeout to improve speed
        try:
            # Use Google Speech Recognition to transcribe the speech
            text = recognizer.recognize_google(audio)
            print(f"Transcribed speech: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand the audio.")
            return None
        except sr.RequestError:
            print("Sorry, there was an issue with the speech recognition service.")
            return None

# Function to send the recognized text to the Friday instance and get a response
def query_friday(text):
    url = "http://localhost:11434/api/chat"  # Updated API endpoint for chat
    payload = {
        "model": "technobyte/arliai-rpmax-12b-v1.1:q4_k_m",  # Adjust to the correct model
         "messages": [
            { "role": "system", "content": "Respond in a short, friendly, and comforting way." },  # System prompt
            { "role": "user", "content": text }
        ]
    }
    try:
        response = requests.post(url, json=payload, stream=True)
        response_text = ""
        if response.status_code == 200:
            # Stream the response and build it up
            for line in response.iter_lines():
                if line:
                    try:
                        # Decode each line as a JSON object
                        json_data = json.loads(line.decode('utf-8'))
                        assistant_message = json_data.get("message", {}).get("content", "")
                        response_text += assistant_message  # Accumulate the message chunks
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
            return response_text
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to convert text to speech
def speak_text(text):
    engine.say(text)
    engine.runAndWait()

# Main function to handle conversational speech-to-text, query Friday, and text-to-speech
def main():
    while True:
        # Capture speech from the microphone
        user_input = listen_and_recognize()
        if user_input:
            # Send the transcribed input to Friday and get the model's response
            response = query_friday(user_input)
            if response:
                print(f"Friday: {response}")
                # Convert Friday's response to speech
                speak_text(response)
            else:
                print("No response from Friday.")
        else:
            print("Please try speaking again.")
        print("Listening again... (Press Ctrl+C to exit)")

if __name__ == "__main__":
    main()