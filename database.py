import psycopg2

# CONNECT TO THE DATABASE
def connect():
    return psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='12345',
        host='localhost',
        port='5432'
    )

# CREATE TABLE IF IT DOESN'T EXIST
def create_table():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS store_chatbot_conversations (
                    convo_id SERIAL PRIMARY KEY,
                    convo_name VARCHAR(50) UNIQUE NOT NULL
                )
            """)
            conn.commit()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS chatbot_conversation (
                    id SERIAL PRIMARY KEY,
                    convo_id INTEGER NOT NULL REFERENCES store_chatbot_conversations(convo_id),
                    message_text TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sender_type VARCHAR(50)
                )
            """)
            conn.commit()

# Add the newly made conversation to the database
def add_convo_to_database(name):
    with connect() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("INSERT INTO store_chatbot_conversations (convo_name) VALUES (%s)", (name,))
                conn.commit()
            except psycopg2.IntegrityError as e:
                print(f"Error: {e}")
                conn.rollback()

# View all the conversations that the users has
def view_all_conversation():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * from store_chatbot_conversations""")
            rows=cur.fetchall()
            return len(rows), rows
        
# Get conversation / room id
def get_convo_id(convo_name):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT convo_id FROM store_chatbot_conversations WHERE convo_name = %s", (convo_name,))
            result = cur.fetchone()
            if result is not None:
                return result[0]
            else:
                raise ValueError("User with username '{}' not found.".format(convo_name))


# Store the contents of the conversation in the database       
def store_conversations(convo_id, message_text, sender_type, timestamp):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chatbot_conversation (convo_id, message_text, sender_type, timestamp)
                VALUES (%s, %s, %s, %s)
            """, (convo_id, message_text, sender_type, timestamp))
            conn.commit()

# Retrieve the conversations that was had in that room
def get_conversation(convo_id):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT message_text, sender_type, timestamp FROM chatbot_conversation 
                        WHERE convo_id = %s ORDER BY timestamp ASC""", 
                        (convo_id,))
            items = cur.fetchall()
            return items
