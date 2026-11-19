import os
import sqlite3
import webbrowser
import cv2
import eel
import pyttsx3
import speech_recognition as sr
from google import genai

# Initialize pyttsx3 engine for Windows Text-to-Speech
engine = pyttsx3.init()
engine.setProperty("rate", 175)  # Adjust speech speed if needed
is_speaking = False  # Global flag to track and interrupt active speech

# Initialize Gemini Client (Replace with your API key if not using environment variable)
API_KEY = os.environ.get("GEMINI_API_KEY", "your api key here")
client = genai.Client(api_key=API_KEY)

# Initialize SQLite Database connection
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# Initialize Eel (Point to your frontend folder)
eel.init("www")


def speak(text):
    """Speaks text using a non-blocking loop so stop_speaking() can interrupt immediately."""
    global is_speaking
    print(f"Jarvis: {text}")
    try:
        eel.receiverText(text)()
        eel.sleep(0.1)
    except Exception as e:
        print(f"UI Text Push Error: {e}")

    is_speaking = True
    engine.say(text)
    engine.startLoop(False)

    while is_speaking and engine.isBusy():
        engine.iterate()
        eel.sleep(0.05)  # Yields to Eel so #stopBtn clicks are processed instantly

    if not is_speaking:
        engine.stop()

    engine.endLoop()
    is_speaking = False


@eel.expose
def stop_speaking():
    """Instantly interrupts active speech when #stopBtn is clicked."""
    global is_speaking
    is_speaking = False
    try:
        engine.stop()
        print("Speech interrupted by user.")
    except Exception as e:
        print(f"Stop speaking error: {e}")


@eel.expose
def face_auth():
    """Performs face authentication using OpenCV and trainer.yml."""
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    try:
        recognizer.read("trainer.yml")
    except Exception as e:
        print(f"Error loading trainer.yml: {e}")
        return False

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # Check primary camera (0), fallback to secondary (1) if needed on Windows
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)

    authenticated = False
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            _, confidence = recognizer.predict(gray[y : y + h, x : x + w])
            if confidence < 70:  # Threshold for successful match
                authenticated = True
                break

        if authenticated:
            break

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return authenticated


@eel.expose
def process_command(command_text):
    """Routes commands to system apps, web shortcuts, or Gemini AI."""
    command_text = command_text.lower().strip()
    print(f"Received command: {command_text}")

    # Strip "open " so "open youtube" matches "youtube"
    clean_query = command_text.replace("open ", "").strip()

    # 1. Check SQLite database for system applications (Windows paths)
    try:
        cursor.execute(
            "SELECT path FROM sys_command WHERE LOWER(name) LIKE ?",
            ("%" + clean_query + "%",),
        )
        sys_res = cursor.fetchone()
        if sys_res:
            app_path = sys_res[0]
            speak(f"Opening {clean_query}")
            os.system(f'start "" "{app_path}"')
            return
    except Exception as e:
        print(f"sys_command DB error: {e}")

    # 2. Check SQLite database for web shortcuts
    try:
        cursor.execute(
            "SELECT url FROM web_command WHERE LOWER(name) LIKE ?",
            ("%" + clean_query + "%",),
        )
        web_res = cursor.fetchone()
        if web_res:
            url = web_res[0]
            speak(f"Opening {clean_query}")
            webbrowser.open(url)
            return
    except Exception as e:
        print(f"web_command DB error: {e}")

    # 3. Built-in fallback for common websites if not in database.db
    common_sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "whatsapp": "https://web.whatsapp.com",
        "instagram": "https://www.instagram.com",
    }
    if command_text.startswith("open ") and clean_query in common_sites:
        speak(f"Opening {clean_query}")
        webbrowser.open(common_sites[clean_query])
        return

    # 4. Fallback to Gemini AI for general conversational queries
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=command_text,
        )
        answer = response.text
        speak(answer)
    except Exception as e:
        speak("I encountered an error communicating with Gemini.")
        print(e)


@eel.expose
def take_command():
    """Listens to microphone input and converts speech to text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            eel.DisplayMessage("Listening...")()
            eel.sleep(0.1)
        except Exception:
            pass
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        try:
            eel.DisplayMessage("Recognizing...")()
            eel.sleep(0.1)
        except Exception:
            pass
        query = r.recognize_google(audio, language="en-in")
        print(f"User said: {query}")
        try:
            eel.senderText(query)()
            eel.sleep(0.1)
        except Exception:
            pass
        process_command(query)
    except Exception as e:
        print(e)
        speak("Say that again please...")


if __name__ == "__main__":
    try:
        # Starts the Eel GUI window on Windows
        eel.start("index.html", size=(800, 600), port=8080)
    except Exception as e:
        print(f"Error starting Eel: {e}")