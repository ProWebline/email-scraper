# email-scraper Tutorial

# Email Scraper Prowebline# Gebäudereinigung E-Mail Scraper



A powerful Google Maps email scraper that extracts business contact information from companies worldwide.Ein ethisches Python-Programm zum Sammeln öffentlich zugänglicher E-Mail-Adressen von Gebäudereinigungsfirmen.



## 🚀 Quick Start Guide## ⚠️ Wichtige Hinweise



### Step 1: Install Requirements- **Nur öffentlich zugängliche Daten**: Sammelt nur E-Mails von öffentlichen Webseiten

- **Respektiert robots.txt**: Prüft automatisch robots.txt vor dem Scraping

First, install Python (if you don't have it):- **Rate Limiting**: Wartet zwischen Anfragen (1.5-3 Sekunden)

- Download from: https://www.python.org/downloads/- **DSGVO-konform**: Für geschäftliche, öffentlich verfügbare Kontaktdaten

- During installation, check "Add Python to PATH"

## 🚀 Installation

### Step 2: Install Dependencies

1. Python 3.8+ installieren (falls nicht vorhanden)

Open a terminal/command prompt in the project folder and run:2. Abhängigkeiten installieren:



```bash```bash

pip install selenium beautifulsoup4 requestspip install -r requirements.txt

``````



### Step 3: Install Chrome Browser## 📖 Verwendung



Make sure you have Google Chrome installed on your computer.### Programm starten:



### Step 4: Run the Script```bash

python gebaeude_email_scraper.py

Open a terminal in the project folder and run:```



```bash### Optionen:

python email_scraper_prowebline.py

```1. **URLs manuell eingeben**: Gib URLs von Gebäudereinigungsfirmen direkt ein

2. **URLs aus Datei laden**: Lade URLs aus einer Textdatei (eine URL pro Zeile)

## 📋 How to Use3. **Beispiel-Demo**: Demonstriert die Funktionalität



### 1. **Enter Search Term**## 📝 URLs-Datei erstellen

   - Example: "Restaurant", "Hotel", "Cleaning Service", "Law Firm"

   - Can be any business type you want to findErstelle eine Textdatei (z.B. `urls.txt`) mit URLs:



### 2. **Select Region**```

   Choose from:https://www.gebäudereinigung-beispiel.de

   - USAhttps://www.cleaning-service.de

   - UKhttps://www.facility-management.de

   - Germany```

   - France

   - Spain## 📊 Ausgabe

   - Italy

   - CanadaDas Programm erstellt eine CSV-Datei mit:

   - Australia- Gefundenen E-Mail-Adressen

   - Or enter custom cities- Zeitstempel



### 3. **Set Number of Companies**Dateiname: `gebaeude_emails_YYYYMMDD_HHMMSS.csv`

   - Choose how many companies to scrape per city (5-30)

   - Recommended: 10-15 for faster results## 🔍 Funktionen



### 4. **Choose Browser Visibility**- ✅ Respektiert robots.txt

   - `n` = Browser runs hidden (faster)- ✅ Rate Limiting (1.5-3 Sek. zwischen Anfragen)

   - `y` = See the browser working (good for testing)- ✅ Folgt Kontakt/Impressum-Links automatisch

- ✅ Filtert ungültige E-Mails

### 5. **Enable Multi-Threading (Optional)**- ✅ Entfernt Duplikate

   - `n` = Single-threaded (slower, more stable)- ✅ CSV Export

   - `y` = Multi-threaded (3x faster, uses more resources)

## 🛡️ Ethische Verwendung

### 6. **Wait for Results**

   - The script will automatically:Dieses Tool ist für **legale geschäftliche Zwecke** gedacht:

     - Search Google Maps- B2B-Kontaktaufnahme

     - Visit company websites- Marktforschung

     - Extract emails and phone numbers- Öffentlich zugängliche Firmendaten

     - Save everything to `recipients.csv`

**Nicht verwenden für:**

## 📊 Output File- Spam

- Belästigung

Results are saved in: **`recipients.csv`**- Verletzung der Privatsphäre



Contains:## 💡 Tipps

- **Name**: Contact name (usually "Contact")

- **Email**: Business email address- Starte mit wenigen URLs zum Testen

- **Company**: Company name- Prüfe robots.txt manuell bei wichtigen Seiten

- **Phone**: Phone number (if found)- Verwende für große Projekte die Google Custom Search API

- **Website**: Company website URL- Respektiere Opt-Out-Wünsche



## 🎯 Features## 🔧 Anpassungen



✅ International search (8+ countries pre-configured)  Du kannst das Programm anpassen:

✅ Multi-language support (English, German, French, Spanish, Italian)  - Rate Limiting: Zeile 69 (time.sleep)

✅ Phone number extraction  - Max Depth: Parameter in scrape_page()

✅ Duplicate email prevention  - Filter: extract_emails() Methode

✅ Multi-threading for faster scraping  
✅ Automatic retry on errors  
✅ Cookie handling  
✅ Progress tracking  

## ⚙️ Configuration Tips

### For Best Results:
- Use **10-15 companies per city**
- Start with **single-threading** first
- Use **headless mode** (browser hidden) for speed
- Search specific business types (e.g., "Italian Restaurant" instead of just "Restaurant")

### For Faster Scraping:
- Enable **multi-threading** (y)
- Increase companies per city to **20-30**
- Use **headless mode** (n for browser visibility)

## 🔧 Troubleshooting

### "ChromeDriver not found"
**Solution:** The script will download it automatically. If not:
```bash
pip install webdriver-manager
```

### "No emails found"
**Solution:** 
- Try different search terms
- Increase number of companies per city
- Some businesses don't list emails publicly

### Script runs too slow
**Solution:**
- Enable multi-threading
- Reduce companies per city
- Use headless mode

### Browser keeps crashing
**Solution:**
- Disable multi-threading
- Close other programs
- Update Chrome browser

## 📝 Example Usage

```
Search term: Hotel
Region: 1 (USA)
Companies per query: 10
Browser visible: n
Multi-threading: n

Result: 60+ hotel emails from 6 US cities in ~10 minutes
```

## ⚠️ Legal Notice

This tool is for educational and business research purposes only. Always:
- Respect website terms of service
- Follow GDPR and data protection laws
- Don't spam or misuse collected emails
- Use responsibly and ethically

## 💡 Tips

1. **Specific searches work better**: "Pizza Restaurant NYC" > "Restaurant"
2. **Check CSV file**: Open with Excel or Google Sheets
3. **Save results**: The CSV file is overwritten each run
4. **Be patient**: Quality data takes time (10-15 minutes is normal)
5. **Start small**: Test with 5 companies first, then scale up

## 🆘 Support

If you encounter issues:
1. Check your internet connection
2. Update Google Chrome
3. Reinstall dependencies: `pip install --upgrade selenium beautifulsoup4`
4. Try without multi-threading first

---

**Happy Scraping! 🎉**
