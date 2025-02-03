# app.py
import os
import datetime
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env (upewnij się, że plik .env znajduje się w tym samym katalogu co app.py)
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# Ustawienie kluczy i haseł – pobierane z .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APP_PASSWORD = os.getenv("APP_PASSWORD")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
# Możesz dodać również zmienną NOTIFY_EMAIL, na którą mają trafiać powiadomienia
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", MAIL_USERNAME)

# Treści prezentujące ofertę, cennik i usługi – z odstępami dla lepszej czytelności
services_info = (
    "Naszą misją jest wsparcie Twojej firmy za pomocą nowoczesnych chatbotów, które pomogą:\n\n"
    "- Zautomatyzować obsługę klienta\n"
    "- Usprawnić sprzedaż\n"
    "- Poprawić komunikację z odbiorcami\n\n"
    "Dlaczego warto współpracować z BiznesBot.pl?\n\n"
    "- Profesjonalizm: 20 lat doświadczenia w technologii komputerowej\n"
    "- Nowoczesność: Modne i skuteczne rozwiązania technologiczne\n"
    "- Indywidualne podejście: Dopasowujemy projekty do potrzeb każdego klienta\n"
    "- Oszczędność czasu: Chatboty Twoi klienci zawsze mają wsparcie – 24/7\n\n"
    "Oferta chatbotów AI:\n\n"
    "1. Gabinety Lekarskie:\n"
    "   - Subskrypcja: 299 zł/mies.\n"
    "   - Jednorazowo: 2999 zł + wsparcie 150 zł/mies.\n"
    "   Bot odpowiada na FAQ, podaje godziny otwarcia i dostępność lekarzy; zaleca kontakt telefoniczny w celu rezerwacji.\n\n"
    "2. Fryzjerzy:\n"
    "   - Subskrypcja: 199 zł/mies.\n"
    "   - Jednorazowo: 1999 zł + wsparcie 100 zł/mies.\n"
    "   Bot odpowiada na FAQ, podaje godziny otwarcia i cennik; rekomenduje kontakt telefoniczny w celu umówienia wizyty.\n\n"
    "3. Kosmetyczki:\n"
    "   - Subskrypcja: 249 zł/mies.\n"
    "   - Jednorazowo: 2499 zł + wsparcie 120 zł/mies.\n"
    "   Bot odpowiada na FAQ, prezentuje cennik i dostępne terminy; poleca kontakt telefoniczny do rezerwacji.\n\n"
    "4. Firmy budowlane:\n"
    "   - Subskrypcja: 299 zł/mies.\n"
    "   - Jednorazowo: 2999 zł + wsparcie 150 zł/mies.\n"
    "   Bot odpowiada na FAQ, podaje godziny pracy i ofertę; sugeruje kontakt telefoniczny dla szczegółowych informacji.\n\n"
    "5. Instalatorzy klimatyzacji i pomp ciepła:\n"
    "   - Subskrypcja: 299 zł/mies.\n"
    "   - Jednorazowo: 2999 zł + wsparcie 150 zł/mies.\n"
    "   Bot odpowiada na FAQ, informuje o ofercie i dostępności usług; zaleca telefoniczne umówienie wizyty technika.\n\n"
    "6. Mechanicy samochodowi:\n"
    "   - Subskrypcja: 199 zł/mies.\n"
    "   - Jednorazowo: 1999 zł + wsparcie 100 zł/mies.\n"
    "   Bot odpowiada na FAQ, podaje godziny otwarcia i informacje o usługach; zachęca do kontaktu telefonicznego."
)

pricing_info = (
    "Oferty Chatbotów AI:\n\n"
    "1. Gabinety Lekarskie:\n"
    "   - Subskrypcja: 299 zł/mies.\n"
    "   - Jednorazowo: 2999 zł + wsparcie 150 zł/mies.\n\n"
    "2. Fryzjerzy:\n"
    "   - Subskrypcja: 199 zł/mies.\n"
    "   - Jednorazowo: 1999 zł + wsparcie 100 zł/mies.\n\n"
    "3. Kosmetyczki:\n"
    "   - Subskrypcja: 249 zł/mies.\n"
    "   - Jednorazowo: 2499 zł + wsparcie 120 zł/mies.\n\n"
    "4. Firmy budowlane:\n"
    "   - Subskrypcja: 299 zł/mies.\n"
    "   - Jednorazowo: 2999 zł + wsparcie 150 zł/mies.\n\n"
    "5. Instalatorzy klimatyzacji i pomp ciepła:\n"
    "   - Subskrypcja: 299 zł/mies.\n"
    "   - Jednorazowo: 2999 zł + wsparcie 150 zł/mies.\n\n"
    "6. Mechanicy samochodowi:\n"
    "   - Subskrypcja: 199 zł/mies.\n"
    "   - Jednorazowo: 1999 zł + wsparcie 100 zł/mies."
)

website_services_pricing = (
    "Cennik usług BiznesBot.pl:\n\n"
    "1. Tworzenie stron internetowych:\n"
    "   • Strona wizytówka (1-3 podstrony, kontakt, proste informacje) – 800 - 1200 zł\n"
    "   • Rozbudowana strona firmowa (4-6 podstrony, formularz kontaktowy, podstawowe SEO) – 1500 - 2500 zł\n"
    "   • Strona z blogiem lub aktualnościami – 2000 - 3000 zł\n"
    "   • Obsługa i aktualizacja strony (miesięcznie) – od 100 zł\n"
    "   • Hosting i domena (roczny koszt, opcjonalnie) – od 100 zł\n\n"
    "2. Tworzenie grafiki na strony internetowe:\n"
    "   • Baner na stronę internetową – 150 - 400 zł\n"
    "   • Logo dla firmy – 300 - 800 zł\n"
    "   • Kompletny branding (logo, kolorystyka, 3-5 grafik do strony) – 1000 - 2000 zł\n\n"
    "3. Szkolenia IT:\n"
    "   • Szkolenie dla seniorów (obsługa komputera, internetu, bezpieczeństwo online, poczta e-mail, podstawy social media)\n"
    "       ◦ 1h – 100 zł\n"
    "       ◦ Pakiet 5h – 450 zł\n"
    "       ◦ Pakiet 10h – 800 zł\n\n"
    "   • Szkolenie dla młodych (programowanie, AI, obsługa narzędzi cyfrowych, strony internetowe, podstawy grafiki komputerowej)\n"
    "       ◦ 1h – 120 zł\n"
    "       ◦ Pakiet 5h – 550 zł\n"
    "       ◦ Pakiet 10h – 1000 zł"
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
    
    # Odpowiedzi na pytania o kontakt – priorytetowe sprawdzenie:
    if "podaj" in lower_input and "email" in lower_input:
        return "Nasz email to: kontakt@biznesbot.pl"
    if "podaj" in lower_input and ("telefon" in lower_input or "numer" in lower_input):
        return "Nasz numer to: 725 777 393"
    if "jaki macie email" in lower_input:
        return "Nasz email to: kontakt@biznesbot.pl"
    if "jaki jest wasz numer" in lower_input:
        return "Nasz numer to: 725 777 393"
    
    # Proste powitania
    greetings = ["witaj", "hej", "cześć", "czesc", "dzień dobry", "mam pytanie"]
    if any(word in lower_input for word in greetings):
        return ("Witam! Jak mogę Ci pomóc?\n\n"
                "Nasze rozwiązania oparte na AI poprawiają efektywność obsługi klienta, zwiększają sprzedaż i budują pozytywny wizerunek marki.")
    
    # Sprawdzenie, czy zapytanie dotyczy oferty – wychwytujemy "ofert" (bez względu na końcówkę)
    if "ofert" in lower_input:
        return services_info
    elif "cennik" in lower_input:
        return pricing_info + "\n\n" + website_services_pricing
    elif any(kw in lower_input for kw in ["kontakt", "działacie", "skontaktować"]):
        if is_business_hours():
            return "Działamy od 8:00 do 16:00. Proszę dzwonić: 725 777 393."
        else:
            subject = "Zapytanie poza godzinami pracy"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            email_message = f"Zapytanie: {user_input}\nCzas: {timestamp}"
            send_email_notification(subject, email_message, "kacperskiszymon@gmail.com")
            return ("Jesteśmy poza godzinami pracy.\n\n"
                    "Proszę podać swój adres email lub numer telefonu, abyśmy mogli się z Tobą skontaktować.")
    else:
        return ("Dziękujemy za Twoją wiadomość!\n\n"
                "Nasze zaawansowane rozwiązania AI pomagają zoptymalizować obsługę klienta, zwiększyć sprzedaż oraz budować silną markę.\n\n"
                "Zachęcam do zadawania pytań o naszą ofertę lub cennik, albo do uzyskania dodatkowych informacji.")

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
