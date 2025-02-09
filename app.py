import os
import datetime
import smtplib
import logging
import json
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai

# Konfiguracja logowania
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Obsługa CORS

# Pobranie zmiennych środowiskowych
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", MAIL_USERNAME)

# Sprawdzenie konfiguracji API OpenAI
if not OPENAI_API_KEY:
    logging.error("Brak klucza API OpenAI! Ustaw OPENAI_API_KEY w pliku .env.")
    raise ValueError("Brak klucza API OpenAI!")

# Ustawienie klucza API dla OpenAI
openai.api_key = OPENAI_API_KEY

# Funkcja do ładowania FAQ
def load_faq():
    try:
        with open("faq.json", "r", encoding="utf-8") as f:
            faq_data = json.load(f)
        logging.info("FAQ załadowane pomyślnie.")
        return faq_data
    except Exception as e:
        logging.error(f"Błąd podczas ładowania FAQ: {e}")
        return {}

FAQ = load_faq()

# Wyszukiwanie odpowiedzi w FAQ
def get_faq_response(user_input):
    for key, answer in FAQ.items():
        if key.lower() in user_input.lower():
            return answer
    return None

# Sprawdzenie godzin pracy (8:00-16:00)
def is_business_hours():
    now = datetime.datetime.now().time()
    return datetime.time(8, 0) <= now <= datetime.time(16, 0)

# Logowanie interakcji do pliku CSV
def log_interaction(user_input, bot_response):
    try:
        with open("chat_logs.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["Data i godzina", "Pytanie użytkownika", "Odpowiedź bota"])
            writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_input, bot_response])
    except Exception as e:
        logging.error(f"Błąd zapisu logów: {e}")

# Wysyłanie e-maila
def send_email_notification(subject, message, recipient):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = MAIL_USERNAME
    sender_password = MAIL_PASSWORD

    if not sender_email or not sender_password:
        logging.warning("Brak danych logowania do e-maila. Powiadomienie nie zostało wysłane.")
        return False

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient
    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [recipient], msg.as_string())
        server.quit()
        logging.info("Wiadomość e-mail wysłana pomyślnie.")
        return True
    except Exception as e:
        logging.error(f"Błąd przy wysyłaniu e-maila: {e}")
        return False

# Generowanie odpowiedzi chatbota
def get_bot_response(user_input):
    lower_input = user_input.lower().strip()

    # Proste odpowiedzi
    if lower_input in ["witaj", "hej", "cześć", "dzień dobry"]:
        return "Cześć! Jak mogę Ci pomóc? 😊"

    if "email" in lower_input:
        return f"Nasz e-mail: {MAIL_USERNAME}"
    
    if "telefon" in lower_input or "numer" in lower_input:
        return "Nasz numer telefonu: 725 777 393"

    if "oferta" in lower_input:
        return "Oferujemy chatboty AI, strony internetowe i szkolenia IT. Więcej szczegółów na BiznesBot.pl."

    # Odpowiedzi na podstawie FAQ
    faq_answer = get_faq_response(user_input)
    if faq_answer:
        return faq_answer

    # Sprawdzenie godzin pracy
    if any(word in lower_input for word in ["kontakt", "skontaktować", "działacie"]):
        if is_business_hours():
            return "Działamy od 8:00 do 16:00. Możesz dzwonić: 725 777 393."
        else:
            subject = "Zapytanie poza godzinami pracy"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            email_message = f"Zapytanie: {user_input}\nCzas: {timestamp}"
            send_email_notification(subject, email_message, NOTIFY_EMAIL)
            return "Obecnie jesteśmy poza godzinami pracy. Proszę zostawić kontakt, a oddzwonimy."

    # Generowanie odpowiedzi z OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Jesteś chatbotem BiznesBot. Oferujemy chatboty, strony internetowe i szkolenia IT."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Błąd OpenAI: {e}")
        return "Przepraszam, wystąpił błąd. Spróbuj ponownie później."

# Endpoint API - obsługa żądań chatbota
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "Brak wiadomości"}), 400

    bot_response = get_bot_response(user_input)
    log_interaction(user_input, bot_response)

    return jsonify({"response": bot_response})

# Strona główna - UI chatbota
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
