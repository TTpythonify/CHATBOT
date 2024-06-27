import customtkinter as ctk
import requests
import threading
from speech_to_text import speech
from text_to_speech import Text_to_speech

class CHATBOT(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Chatbot")
        self.geometry("450x400")

        self.is_recording = False

        label = ctk.CTkLabel(master=self, text="Mini-Chatbot", font=("Arial", 20))
        label.pack()

        # Create text box to display messages
        self.display_text = ctk.CTkTextbox(master=self, width=300, height=280, font=("Arial", 15))
        self.display_text.pack(pady=20)

        # Create frame for entry and buttons
        entry_frame = ctk.CTkFrame(self)
        entry_frame.pack(pady=10)

        # Create record button
        self.record_button = ctk.CTkButton(master=entry_frame, text="Record", command=self.record_text, width=10, fg_color="blue")
        self.record_button.pack(side='left', padx=5)

        # Create entry widget
        self.entry = ctk.CTkEntry(master=entry_frame, width=280, height=280, placeholder_text="Enter or record text")
        self.entry.pack(side='left', padx=5)

        # Create send button
        self.send_button = ctk.CTkButton(master=entry_frame, text="Send", command=self.send_text, width=10, fg_color="blue")
        self.send_button.pack(side='left', padx=5)

        self.warning_label = ctk.CTkLabel(self, text="", text_color="red")
        self.warning_label.pack(pady=5)

    def send_text(self):
        text = self.entry.get().strip()
        if text:
            # Display the sent message in the textbox
            self.display_text.insert(ctk.END, f"You: {text}\n\n")
            self.display_text.see(ctk.END)

            # Clear the entry widget
            self.entry.delete(0, ctk.END)

            voice = False  # Text input, not voice
            threading.Thread(target=self.bot_response, args=(text, voice)).start()

    def bot_response(self, text, voice):
        chat_bot_response = self.chat_bot(text)
        self.display_text.insert(ctk.END, f"BOT: {chat_bot_response}\n\n")
        self.display_text.see(ctk.END)
        
        if voice:
            threading.Thread(target=Text_to_speech, args=(chat_bot_response,)).start()

    def record_text(self):
        if not self.is_recording:
            # Start recording
            self.record_button.configure(text="Stop", fg_color="red")
            self.is_recording = True
            threading.Thread(target=self.record_voice).start()
        else:
            # Stop recording
            self.record_button.configure(text="Record", fg_color="blue")
            self.is_recording = False

    def record_voice(self):
        users_voice = speech()
        self.record_button.configure(text="Record", fg_color="blue")
        self.is_recording = False
        if users_voice:
            voice = True
            self.display_text.insert(ctk.END, f"You: {users_voice}\n\n")
            self.display_text.see(ctk.END)
            threading.Thread(target=self.bot_response, args=(users_voice, voice)).start()

    def chat_bot(self, query):
        url = "https://chatgpt-ai-chat-bot.p.rapidapi.com/ask"
        payload = {"query": query}
        headers = {
            "x-rapidapi-key": "1ae4654528msh82cf9d56f299a41p175eb1jsnebd34a46be13",
            "x-rapidapi-host": "chatgpt-ai-chat-bot.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            answer = data.get("response", "I don't know")
            return answer
        except Exception as e:
            return "Sorry, I couldn't get a response."

if __name__ == "__main__":
    app = CHATBOT()
    app.mainloop()
