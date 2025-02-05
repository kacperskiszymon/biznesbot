import os
import datetime
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import openai  # Dodajemy import biblioteki OpenAI

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# Ustawienie kluczy i haseł – pobierane z .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APP_PASSWORD = os.getenv("APP_PASSWORD")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", MAIL_USERNAME)

# Ustawienie klucza API OpenAI
openai.api_key = OPENAI_API_KEY

# Nowe informacje o ofercie
services_info = (
    "Asystenci AI czyli Chatboty\n\n"
    "🚀 Pakiet Podstawowy – 990 zł / rok (jednorazowa płatność)\n"
    "✅ Chatbot odpowiadający na 10-15 pytań FAQ.\n"
    "✅ Powiadomienia e-mail o pytaniach klientów.\n"
    "✅ Hosting na stabilnym serwerze (Render bez usypiania) w cenie.\n"
    "✅ Podstawowe wsparcie techniczne.\n\n"
    "📌 Pakiet Podstawowy – 500 zł jednorazowo + 50 zł/miesiąc\n"
    "✅ Chatbot odpowiadający na 10-15 pytań FAQ.\n"
    "✅ Powiadomienia e-mail o pytaniach klientów.\n"
    "✅ Hosting na stabilnym serwerze (Render bez usypiania).\n"
    "✅ Podstawowe wsparcie techniczne.\n\n"
    "💼 Pakiet Rozszerzony – 1490 zł / rok (jednorazowa płatność)\n"
    "✅ Wszystko z Pakietu Podstawowego + więcej funkcji:\n"
    "✅ Chatbot odpowiada na 20-30 pytań FAQ.\n"
    "✅ Możliwość edycji odpowiedzi na życzenie (2 zmiany rocznie).\n"
    "✅ Statystyki i analiza zapytań klientów.\n"
    "✅ Priorytetowa pomoc techniczna.\n\n"
    "📌 Pakiet Rozszerzony – 800 zł jednorazowo + 100 zł/miesiąc\n"
    "✅ Wszystko z Pakietu Podstawowego + więcej funkcji:\n"
    "✅ Chatbot odpowiada na 20-30 pytań FAQ.\n"
    "✅ Możliwość edycji odpowiedzi na życzenie (2 zmiany rocznie).\n"
    "✅ Statystyki i analiza zapytań klientów.\n"
    "✅ Priorytetowa pomoc techniczna.\n\n"
    "Wybierz opcję wygodną dla siebie – miesięczna subskrypcja lub jednorazowa opłata za rok!\n\n"
    "--------------------------------------\n\n"
    "Strony Internetowe\n\n"
    "📌 Pakiet Podstawowy – 990 zł / rok\n"
    "✅ Rejestracja domeny i konfiguracja hostingu.\n"
    "✅ Instalacja WordPressa i podstawowych wtyczek.\n"
    "✅ Szablon dostosowany do branży klienta.\n"
    "✅ 3-5 podstron (np. Strona główna, O nas, Oferta, Kontakt, Galeria).\n"
    "✅ Podstawowa optymalizacja SEO.\n"
    "✅ Responsywność (strona dobrze wygląda na telefonach).\n"
    "✅ Hosting + domena w cenie.\n\n"
    "📌 Pakiet Rozszerzony – 1490 zł / rok\n"
    "✅ Rozbudowany szablon i personalizacja.\n"
    "✅ Do 10 podstron, blog lub sekcja aktualności.\n"
    "✅ Formularz kontaktowy + integracja z Google Maps.\n"
    "✅ Dodatkowa optymalizacja SEO (meta tagi, sitemap).\n"
    "✅ Możliwość wprowadzenia 2 zmian rocznie na stronie.\n"
    "✅ Hosting + domena w cenie.\n\n"
    "--------------------------------------\n\n"
    "🎨 Logo i Banery\n"
    "✅ Projektowanie logo – od 300 zł.\n"
    "✅ Banery na strony internetowe – od 150 zł.\n\n"
    "🎓 Szkolenia IT\n"
    "✅ Szkolenia dla seniorów (obsługa komputera, internet, bezpieczeństwo online, poczta e-mail, podstawy social media).\n"
    "✅ Szkolenia dla młodych (programowanie, AI, obsługa narzędzi cyfrowych).\n"
    "✅ Cena: od 100 zł za godzinę.\n"
)

pricing_info = (
    "Oferty Chatbotów AI:\n\n"
    "Pakiet Podstawowy – 990 zł / rok lub 500 zł jednorazowo + 50 zł/miesiąc.\n\n"
    "Pakiet Rozszerzony – 1490 zł / rok lub 800 zł jednorazowo + 100 zł/miesiąc.\n\n"
)

website_services_pricing = (
    "Cennik Stron Internetowych:\n\n"
    "Pakiet Podstawowy – 990 zł / rok\n"
    "✅ Rejestracja domeny i konfiguracja hostingu.\n"
    "✅ Instalacja WordPressa i podstawowych wtyczek.\n"
    "✅ Szablon dostosowany do branży klienta (3-5 podstron).\n"
    "✅ Podstawowa optymalizacja SEO.\n"
    "✅ Responsywność.\n"
    "✅ Hosting + domena w cenie.\n\n"
    "Pakiet Rozszerzony – 1490 zł / rok\n"
    "✅ Rozbudowany szablon i personalizacja.\n"
    "✅ Do 10 podstron, blog lub sekcja aktualności.\n"
    "✅ Formularz kontaktowy + integracja z Google Maps.\n"
    "✅ Dodatkowa optymalizacja SEO (meta tagi, sitemap).\n"
    "✅ Możliwość wprowadzenia 2 zmian rocznie.\n"
    "✅ Hosting + domena w cenie.\n"
)

def is_business_hours():
    """Sprawdza, czy aktualny czas mieści się w godzinach pracy (8:00-16:00)."""
    now = datetime.datetime.now().time()
    start = datetime.time(8, 0)
    end = datetime.time(16, 0)
    return start <= now <= end

def get_bot_response(user_input):
    """Generuje odpowiedź chatbota na podstawie wpisanego tekstu."""
    lower_input = user_input.lower().strip()

    # Odpowiedzi na pytania o kontakt
    if "podaj" in lower_input and "email" in lower_input:
        return "Nasz email to: kontakt@biznesbot.pl"
    if "podaj" in lower_input and ("telefon" in lower_input or "numer" in lower_input):
        return "Nasz numer to: 725 777 393"
    if "jaki macie email" in lower_input:
        return "Nasz email to: kontakt@biznesbot.pl"
    if "jaki jest wasz numer" in lower_input:
        return "Nasz numer to: 725 777 393"
    
    # Powitania
    greetings = ["witaj", "hej", "cześć", "czesc", "dzień dobry", "mam pytanie"]
    if any(word in lower_input for word in greetings):
        return ("Witam! Jak mogę Ci pomóc?\n\n"
                "Zapytaj o nasze chatboty, strony internetowe, szkolenia IT, logo lub banery.")
    
    # Informacje o usługach – wybieramy tylko wybrane kategorie
    if "chatbot" in lower_input or "asystent" in lower_input or "ai" in lower_input:
        return services_info
    if "strona" in lower_input or "wordp" in lower_input:
        return website_services_pricing
    if "szkolenie" in lower_input:
        return "Oferujemy szkolenia IT od 100 zł za godzinę. Więcej informacji na BiznesBot.pl."
    if "logo" in lower_input or "baner" in lower_input:
        return "Projektujemy logo od 300 zł i banery od 150 zł. Skontaktuj się z nami!"
    if "cennik" in lower_input:
        return pricing_info

    # Kontakt – jeśli zapytanie dotyczy kontaktu
    if any(kw in lower_input for kw in ["kontakt", "działacie", "skontaktować"]):
        if is_business_hours():
            return "Działamy od 8:00 do 16:00. Proszę dzwonić: 725 777 393."
        else:
            subject = "Zapytanie poza godzinami pracy"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            email_message = f"Zapytanie: {user_input}\nCzas: {timestamp}"
            send_email_notification(subject, email_message, "kacperskiszymon@gmail.com")
            return ("Jesteśmy poza godzinami pracy.\n\n"
                    "Proszę podać swój adres email lub numer telefonu, abyśmy mogli się z Tobą skontaktować.")
    
    # Domyślna odpowiedź – użyjemy OpenAI dla bardziej "inteligentnej" odpowiedzi
    try:
        # Wywołanie OpenAI Chat API dla dynamicznej odpowiedzi
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    "Jesteś chatbotem BiznesBot. Twoim zadaniem jest profesjonalne i przekonujące prezentowanie oferty firmy, "
                    "która oferuje chatboty, strony internetowe, szkolenia IT oraz projektowanie logo i banerów. "
                    "Twoje odpowiedzi powinny być pomocne, nakierowywać klienta do skorzystania z usług i budować pozytywny wizerunek firmy."
                )},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Błąd przy generowaniu odpowiedzi z OpenAI:", e)
        return "Przepraszam, wystąpił błąd. Spróbuj ponownie później."

def send_email_notification(subject, message, recipient):
    """
    Wysyła e-mail za pomocą serwera SMTP Gmail.
    Upewnij się, że zmienne MAIL_USERNAME oraz MAIL_PASSWORD są ustawione.
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = MAIL_USERNAME
    sender_password = MAIL_PASSWORD

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [recipient], msg.as_string())
        server.quit()
        print("Wiadomość e-mail wysłana pomyślnie.")
        return True
    except Exception as e:
        print("Błąd przy wysyłaniu e-maila:", e)
        return False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.form.get("message")
    bot_response = get_bot_response(user_input)
    # Wysyłaj powiadomienie e-mail dla KAŻDEGO zapytania
    subject = "Nowe zapytanie z chatbox"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    email_message = f"Zapytanie: {user_input}\nCzas: {timestamp}"
    send_email_notification(subject, email_message, "kacperskiszymon@gmail.com")
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
