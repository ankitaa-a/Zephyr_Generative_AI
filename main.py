import win32com.client
import speech_recognition as sr
import webbrowser
import os
import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext, messagebox
from threading import Thread
import random
from googletrans import Translator

chat_history = ""
listening = False
stop_listening = True


def configure_genai():
    genai.configure(api_key="your api key")

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )


def chat(query):
    global chat_history
    chat_history += f"\nUser: {query}\nZephyr: "

    model = configure_genai()
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(query)
    response_text = response.text

    chat_history += response_text
    display_message("Zephyr: " + response_text)


    os.makedirs("ai_files", exist_ok=True)
    with open(f"ai_files/prompt_{random.randint(1, 787687688)}.txt", "w", encoding='utf-8') as f:
        f.write(chat_history)
    #speaker.Speak(response_text)

    return response_text


def ai(prompt):
    model = configure_genai()
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(prompt)
    response_text = response.text

    display_message("AI: " + response_text)
    return response_text


def take_command():
    global stop_listening,listening
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        #print("Listening...")
        display_message("Listening (Press STOP once you complete your sentence)...")
        display_message("     ")
        #speaker.Speak("Listening (Press STOP once you complete your sentence)")
        audio = r.listen(source)

        #if stop_listening:
         #   stop_listening = False
          #  return ""
        """        try:
            query = r.recognize_google(audio, language="en-in")
            display_message(f"User (Said): {query}")
            if stop_listening:
                stop_listening = False
                display_message("Stopped Listening...")
                return ""
            return query"""

        try:
            if stop_listening:
                query = r.recognize_google(audio, language="en-in")
                display_message(f"User (Said): {query}")

                stop_listening=False
                listening=False
                #display_message("Stopped Listening...")
                return query
            #return query

        except Exception as e:
            #print("Some error occurred:", e)
            display_message(f"Some Error Occurred {e}")
            return ""



def display_message(message):

    chat_window.config(state=tk.NORMAL)
    chat_window.insert(tk.END, message + '\n')
    chat_window.config(state=tk.DISABLED)
    chat_window.yview(tk.END)



def process_command():

    global translator
    query = take_command()
    if not query:
        return

    # Create a translator object
    translator = Translator()

    # Check if the query contains "in hindi"
    if "in hindi" in query.lower():
        # Remove the phrase from the query to get the main query
        query = query.lower().replace("in hindi", "").strip()
        language = "hi"

        # Translate the query to Hindi
        display_message("In Hindi")
        translated_query = translator.translate(query, src='en', dest='hi').text
        response_text = chat(translated_query)
        #speaker.Speak(response_text)

    if "open youtube" in query.lower():
        display_message("Opening YouTube")
        webbrowser.open("https://www.youtube.com/")
    elif "open google" in query.lower():
        display_message("Opening Google")
        webbrowser.open("https://www.google.com/")
    elif "open wikipedia" in query.lower():
        display_message("Opening Wikipedia")
        webbrowser.open("https://www.wikipedia.com/")
    elif "open chrome" in query.lower():
        display_message("Opening Chrome")
        os.system(r'"C:\Program Files\Google\Chrome\Application\chrome.exe"')
    elif "exit" in query.lower():
        root.quit()
    elif "using artificial intelligence" in query.lower():
        response_text=ai(query)
        speaker.Speak(response_text)
    elif "stop listening" in query.lower():
        stop_listening_func()
    else:
        display_message("In English")
        response_text=chat(query)
        speaker.Speak(response_text)


def start_listening():
    global listening,stop_listening
    stop_listening = False
    listening = True
    speaker.Speak("Listening (Press STOP once you complete your sentence)")
    while listening:
        process_command()


def stop_listening_func():
    global listening, stop_listening
    stop_listening = True
    listening = False


def start_listening_thread():
    thread = Thread(target=start_listening)
    thread.start()


def on_stop():
    stop_listening_func()
    messagebox.showinfo("Stopped", "Listening stopped.")


def submit_query():
    query = typing_area.get()
    if not query:
        messagebox.showwarning("Input Error", "Please enter a query.")
        return

    display_message(f"User (Typed): {query}")
    speaker.Speak(f"User (Typed): {query}")
    if "using artificial intelligence" in query.lower():
        response_text = ai(query)
    else:
        response_text = chat(query)

    speaker.Speak(response_text)
    typing_area.delete(0, tk.END)  # Clear the typing area after submission


root = tk.Tk()
root.title("Zephyr Generative AI")

# Chat Window
chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED)
chat_window.pack(expand=True, fill='both')

# Typing Area
typing_area = tk.Entry(root, width=50)
typing_area.pack(pady=5)

# Buttons
start_button = tk.Button(root, text="Start Listening", command=start_listening_thread)
start_button.pack(side=tk.LEFT, padx=10, pady=10)

stop_button = tk.Button(root, text="Stop Listening", command=on_stop)
stop_button.pack(side=tk.LEFT, padx=10, pady=10)

submit_button = tk.Button(root, text="Submit", command=submit_query)
submit_button.pack(side=tk.LEFT, padx=10, pady=10)

speaker = win32com.client.Dispatch("SAPI.SpVoice")
speaker.Speak("Zephyr Generative AI How can I assist you?")

root.mainloop()

