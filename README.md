# Email Scraper Prowebline

A tool that automatically scrapes business emails from websites using Google Maps search.

## What Does It Do?

This script finds companies in different cities, extracts their websites, and scrapes business email addresses from those websites. Results are saved in a CSV file.

## Requirements

- **Python 3.7+**
- **Chrome Browser** (installed on your computer)
- **ChromeDriver** (automatic driver management)

## Installation - Step by Step

### Step 1: Install Python

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **IMPORTANT**: Check the box "Add Python to PATH"
4. Click "Install Now"

### Step 2: Install Required Packages

1. Open a terminal (Command Prompt or PowerShell)
2. Navigate to the folder where you saved this script:
   ```
   cd c:\Users\YourUsername\Desktop\Roblox
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
   This will install:
   - Selenium (browser automation)
   - BeautifulSoup4 (web scraping)
   - Requests (HTTP requests)

## How to Use - Step by Step

### Step 1: Open Terminal

1. Go to the folder with the script
2. Right-click and select "Open in Terminal" (or use PowerShell/Command Prompt)

### Step 2: Run the Script

Type this command and press Enter:
```
python email_scraper_prowebline.py
```

### Step 3: Answer the Questions

The script will ask you:

1. **What would you like to search for?**
   - Example: `Cleaning Service`, `Restaurant`, `Hotel`, `Lawyer`, `Plumber`
   - Type what you want and press Enter

2. **Which region/country?**
   - Choose a number 1-9 for predefined cities
   - Or choose 9 to enter your own cities
   - Press Enter

3. **How many companies per search?**
   - Enter a number between 5-30 (default: 10)
   - More = longer runtime

4. **Should the browser be visible?**
   - Type `y` for yes (you can see what it's doing)
   - Type `n` for no (runs in background)
   - Default: `n`

5. **Use multi-threading?**
   - Type `y` for faster speed (uses more computer resources)
   - Type `n` for slower but more stable
   - Default: `n`

### Step 4: Wait for Results

The script will:
- Search Google Maps for companies
- Visit their websites
- Extract email addresses
- Save everything to `recipients.csv`

**This takes 5-15 minutes** depending on your settings.

### Step 5: Check Results

When done, a file called `recipients.csv` will be created in the same folder.
Open it with Excel, Google Sheets, or any text editor to see the emails.

## What's in the CSV File?

| Column | Meaning |
|--------|---------|
| Name | Contact person name |
| Email | Email address (main result) |
| Company | Company name |
| Phone | Phone number (if found) |
| Website | Company website |

## Troubleshooting

### Problem: "Chrome not found"
- **Solution**: Make sure Google Chrome is installed on your computer

### Problem: "Module not found" error
- **Solution**: Run `pip install -r requirements.txt` again

### Problem: Script is very slow
- **Solution**: 
  - Use `n` for browser visibility (faster)
  - Use `y` for multi-threading (faster)
  - Search fewer companies (5-10 instead of 30)

### Problem: No emails found
- **Solution**: 
  - Try different search terms
  - Try different regions
  - Some websites don't have visible email addresses

### Problem: Browser keeps crashing
- **Solution**:
  - Use single-threaded mode (`n` for multi-threading)
  - Reduce the number of companies per search
  - Close other applications to free up memory

## Performance Tips

- **For speed**: Use multi-threading + headless browser + more companies
- **For stability**: Use single-threaded + visible browser + fewer companies
- **Start small**: Test with 5-10 companies first before scaling up

## Privacy & Legal

⚠️ **Important**: Make sure you follow local laws and website terms of service before scraping.
- Check if websites allow scraping
- Don't overload servers with too many requests
- Some regions have data protection laws (GDPR, etc.)

## Common Search Terms to Try

- Cleaning Service
- Restaurant
- Hotel
- Law Firm
- Plumber
- Electrician
- Marketing Agency
- IT Services
- Construction Company
- Car Rental

## Need Help?

If you encounter issues:
1. Check that all packages are installed: `pip install -r requirements.txt`
2. Make sure Chrome is up to date
3. Try with fewer companies and single-threaded mode first
4. Close other applications to free memory
