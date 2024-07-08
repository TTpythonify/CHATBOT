import customtkinter as ctk
import threading
import requests
from database import *
import datetime
from speech_to_text import speech
from text_to_speech import Text_to_speech

create_table() # Creates tables in database

class CHATBOT(ctk.CTk):
    def __init__(self, convo_name):
        super().__init__()
        self.convo_name = convo_name
        self.title("Chatbot")
        self.geometry("600x450")

        self.is_recording = False
        self.conversation_started = False
        self.current_conversation_name = None

        self.setup_ui()


    # This deals with display
    def setup_ui(self):
        # Fetch conversations from the database
        rows, button_names = view_all_conversation()

        # Create left frame for conversations list
        left_frame = ctk.CTkFrame(master=self, width=150, height=400)
        left_frame.pack(side='left', fill='y')

        # Label for conversations
        conv_label = ctk.CTkLabel(master=left_frame, text="Conversations", font=("Arial", 20))
        conv_label.pack(pady=10)

        # Scrollable frame for conversation buttons
        button_scroll_frame = ctk.CTkScrollableFrame(master=left_frame, width=150, height=350)
        button_scroll_frame.pack(fill='y', expand=True)

        # Pack buttons into the scrollable frame
        for i in range(rows):
            button = ctk.CTkButton(master=button_scroll_frame, text=button_names[i][1], command=lambda i=i: self.button_clicked(button_names[i][1]))
            button.pack(pady=5, padx=5)

        # Main chat container frame
        main_frame = ctk.CTkFrame(master=self, width=450, height=400)  
        main_frame.pack(side='right', fill='both', expand=True)

        # Label for conversation name
        self.conversation_label = ctk.CTkLabel(master=main_frame, text=self.convo_name, font=("Arial", 20))
        self.conversation_label.pack()

        # Button to start new conversation
        conversation_button = ctk.CTkButton(master=main_frame, width=12, text="New Conversation", command=self.new_conversation)
        conversation_button.pack(side='top', anchor='ne', padx=10, pady=10)

        # Text box for displaying messages
        self.display_text = ctk.CTkTextbox(master=main_frame, width=300, height=280, font=("Arial", 15))
        self.display_text.pack(pady=20)

        # Frame for entry and buttons
        entry_frame = ctk.CTkFrame(main_frame)
        entry_frame.pack(pady=10)

        # Record button
        self.record_button = ctk.CTkButton(master=entry_frame, text="Record", command=self.record_text, width=10, fg_color="blue")
        self.record_button.pack(side='left', padx=5)

        # Entry widget
        self.entry = ctk.CTkEntry(master=entry_frame, width=280, height=280, placeholder_text="Enter or record text")
        self.entry.pack(side='left', padx=5)

        # Send button
        self.send_button = ctk.CTkButton(master=entry_frame, text="Send", command=self.send_text, width=10, fg_color="blue")
        self.send_button.pack(side='left', padx=5)

        self.warning_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        self.warning_label.pack(pady=5)




    # This deals with user sending messages
    def send_text(self):

        user_text = self.entry.get().strip()

        if user_text:

            label_text = self.conversation_label.cget("text")
            convo_id=get_convo_id(label_text.lower())

            # Display the sent message in the textbox
            self.display_text.insert(ctk.END, f"YOU: {user_text}\n\n")
            self.display_text.see(ctk.END) 
            time_sent=datetime.datetime.now() # Get the time the message was sent

            store_conversations(convo_id,user_text,"YOU: ",time_sent) # Store convo in database

            # Clear the entry widget
            self.entry.delete(0, ctk.END)

            voice = False  # Text input, not voice
            threading.Thread(target=self.bot_response, args=(user_text, voice)).start() 


    # Deals with bot response
    def bot_response(self, text, voice):
        
        label_text = self.conversation_label.cget("text")
        convo_id=get_convo_id(label_text.lower())
        chat_bot_response = self.chat_bot(text)

        # Display the sent message in the textbox
        self.display_text.insert(ctk.END, f"BOT: {chat_bot_response}\n\n")
        self.display_text.see(ctk.END)
        time_sent=datetime.datetime.now()# Get time of response

        store_conversations(convo_id,chat_bot_response,"BOT: ",time_sent) # Store convo in database

        if voice:
            threading.Thread(target=Text_to_speech, args=(chat_bot_response,)).start()

    # Records message
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


    # Records Message pt2
    def record_voice(self):

        users_voice = speech() # Import from a different file
        label_text = self.conversation_label.cget("text")
        convo_id=get_convo_id(label_text.lower())
        self.record_button.configure(text="Record", fg_color="blue")
        self.is_recording = False

        # IF user sends a message verbally
        if users_voice:
            voice = True

            # Display the sent message in the textbox
            self.display_text.insert(ctk.END, f"You: {users_voice}\n\n")
            self.display_text.see(ctk.END)
            time_sent=datetime.datetime.now() # Get time message was sent

            threading.Thread(target=self.bot_response, args=(users_voice, voice)).start()

            store_conversations(convo_id,users_voice,"YOU: ",time_sent) # Store convo in the database


    # Stars a new conversation
    def new_conversation(self):

        self.conversation_started = False

        # Create a new dialog window
        self.dialog = ctk.CTkToplevel(self)
        self.dialog.title("New Conversation")
        self.dialog.geometry("300x150")

        dialog_label = ctk.CTkLabel(master=self.dialog, text="Enter conversation name:", font=("Arial", 15))
        dialog_label.pack(pady=10)

        self.dialog_entry = ctk.CTkEntry(master=self.dialog)
        self.dialog_entry.pack(pady=10)

        dialog_button = ctk.CTkButton(master=self.dialog, text="Start", command=self.start_conversation)
        dialog_button.pack(pady=10)


    # Stars a new conversation pt2
    def start_conversation(self):

        conversation_name = self.dialog_entry.get().strip().lower()

        if conversation_name:
            add_convo_to_database(conversation_name)
            self.display_text.see(ctk.END)
            self.conversation_started = True
            self.dialog.destroy()  # Destroy the current dialog window
            self.destroy()  # Destroy the main app window

            # Create a new instance of CHATBOT with the conversation name
            new_app = CHATBOT(convo_name=conversation_name.upper())
            new_app.mainloop() 


    # Go into the conversations
    def button_clicked(self, button_name):

        self.display_text.delete("1.0", ctk.END)
        current_room = button_name
        convo_id=get_convo_id(current_room.lower())
        self.conversation_label.configure(text=current_room.upper())
        convo=get_conversation(convo_id)

        for i in convo:
            # Get the message and the sender
            sender=i[1]
            message=i[0]
            self.display_text.insert(ctk.END,f"{sender}{message}\n\n")
            self.display_text.see(ctk.END)


    # Interacts with the API
    def chat_bot(self, query):

        url = "https://chatgpt-ai-chat-bot.p.rapidapi.com/ask"

        payload = { "query": query }
        headers = {
            "x-rapidapi-key": "41d19352eemsh2976be87ec33502p182569jsn7d5bf59dc367",
            "x-rapidapi-host": "chatgpt-ai-chat-bot.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        # Get response
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            answer = data.get("response", "I don't know")
            return answer
        except Exception as e:
            return "Sorry, I couldn't get a response."


if __name__ == "__main__":
    app = CHATBOT(convo_name="-- Join or Start a Conversation--")
    app.mainloop()
