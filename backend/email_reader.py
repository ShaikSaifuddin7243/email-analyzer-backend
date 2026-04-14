import os
import imaplib
from dotenv import load_dotenv
import email
from email.utils import parseaddr
from pymongo import MongoClient
from email.header import decode_header
load_dotenv()


def setup_connections():
    #MongoDB connection
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client['email_analyzer']
    collection = db['emails']

    #IMAP 
    IMAP_SERVER = "imap.gmail.com"
    EMAIL = os.getenv("EMAIL_USER")
    PASSWORD = os.getenv("EMAIL_PASS")
    print("Connecting to the email server...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    print("Successfully connected to the email server.")

    return mail, collection

def is_newsletter(body_text):
    body_text = body_text.lower()
    if "unsubscribe" in body_text:
        return True
    return False

def parse_single_email(msg_data,eid):
    raw_email = msg_data[0][1]

    parsed_email = email.message_from_bytes(raw_email)


    raw_from = parsed_email["From"]
    parsed_from = parseaddr(raw_from)


    sender_name, sender_address = parsed_from

    sender_address = clean_header(sender_address)
    sender_name = clean_header(sender_name)


    timestamp = parsed_email["Date"]


    email_subject = clean_header(parsed_email["Subject"])


    email_body_plain = ""

    if parsed_email.is_multipart():

        for part in parsed_email.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload is not None:  # Make sure it isn't empty!
                    email_body_plain = payload.decode("utf-8", errors="ignore")
                    break # We found our text, so stop searching!
    else:
        payload = parsed_email.get_payload(decode=True)
        if payload is not None:
            email_body_plain = payload.decode("utf-8", errors="ignore")


    no_of_chars = len(email_body_plain)


    email_body_plain = email_body_plain.lower()


    newsletter_status = is_newsletter(email_body_plain)


    print(f"Sender: {sender_name} <{sender_address}>")
    print(f"Timestamp: {timestamp}")
    print(f"Subject: {email_subject}")
    print(f"Email body: {email_body_plain}")  
    print(f"Number of characters in email body: {no_of_chars}")


    my_email_data = {
        "email_id": eid.decode(),
        "sender_name": sender_name,
        "sender_email": sender_address,
        "subject": email_subject,
        "timestamp": timestamp,
        "stats": {
            "char_count": no_of_chars,
            "is_newsletter": newsletter_status
            }
        }
    
    return my_email_data

def save_to_db(collection, email_data):
    already_exists = collection.find_one({"email_id": email_data["email_id"]})
    if not already_exists:
        collection.insert_one(email_data)
    else:       
        print(f"Email with ID {email_data['email_id']} already exists in the database. Skipping insertion.")

def clean_header(raw_header):
    if not raw_header:
        return ""
    decoded_parts = decode_header(raw_header)
    final_text = ""
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            final_text += part.decode(charset or "utf-8", errors="ignore")
        else:
            final_text += part  
    return final_text
def main():
    mail, collection = setup_connections()

    mail.select("INBOX")
    status, messages = mail.search(None,"ALL")
    email_ids = messages[0].split()
    last_10_ids = email_ids[-10:]

    for eid in last_10_ids:
        status, msg_data = mail.fetch(eid,"(RFC822)")
        clean_email_data = parse_single_email(msg_data,eid)
        save_to_db(collection, clean_email_data)
    print("Finished processing the last 10 emails.")


if __name__ == "__main__":

    try:
        main()
    except imaplib.IMAP4.error as e:
        print(f"Failed to connect to the email server: {e}")
        exit(1)