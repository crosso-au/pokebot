![](https://cdn.crossboxlabs.com/cbl-logo.png)

------------

# POKEBOT

This project is a Python-based web scraper designed to monitor Pokemon card prices and stock availability on TrollAndToad. It supports two types of scrapes:

- **Search-based**: Iterates through a search URL (with pagination) to extract details for multiple products.
- **Item-based**: Scrapes details from a specific product page.

The scraper compares current data with previously stored data (in `scraped_data.json`) and sends notifications via a Discord webhook when:
- A product is added for the first time.
- A price drop is detected.
- Stock availability changes.

## Features

- **Data Extraction**: Retrieves product name, URL, price, and stock status.
- **Dual Mode Scraping**: Supports both search-based (multiple items) and item-based (single item) scraping.
- **Data Comparison**: Saves scraped data to `scraped_data.json` and compares it to detect changes.
- **Discord Notifications**: Sends formatted alerts via a Discord webhook.
- **Automated Installation**: An installer script (`installer.py`) is provided to set up required dependencies.

## Requirements

- Python 3.x

Required Python packages:
- `requests`
- `beautifulsoup4`

## Installation

### Step 1. Verify Python Installation

- **Windows**: Open Command Prompt and run:
 
     python --version

or

   	 py --version
	
	
### Linux/Mac: Open Terminal and run:
    python3 --version
	
If Python is not installed or not found in PATH, please install it first. (See the optional platform‑specific installer scripts below.)

### Step 2. Install Python Dependencies
An automated installer script is provided. In the project directory, run:

    python installer.py

This script will:

1. Create a requirements.txt file (if it doesnt exist).
2. Install the required packages.

### (Optional) Step 3. Automate Python Installation
If you need to automate Python installation itself, you can use the following platform‑specific scripts.

#### Windows
Create and run a PowerShell script (e.g., install_python.ps1) as administrator:

##### # install_python.ps1
```
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    Write-Host "Python is already installed."
    exit
}
$pythonUrl = "https://www.python.org/ftp/python/3.10.8/python-3.10.8-amd64.exe"
$output = "python-installer.exe"
Write-Host "Downloading Python from $pythonUrl..."
Invoke-WebRequest -Uri $pythonUrl -OutFile $output
Write-Host "Installing Python..."
Start-Process -FilePath $output -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
Remove-Item $output
Write-Host "Python installation complete."
```
Run the script with administrator privileges.

#### Linux
Create a Bash script (e.g., install_python.sh) for Debian‑based systems:

```bash
#!/bin/bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip
echo "Python and pip have been installed."
```
Make the script executable:

```bash
chmod +x install_python.sh
```

Then run it:

    ./install_python.sh

## Configuration
### items.json
This file specifies the URLs to scrape. Its structure is:


```json
{
  "search": [
    "https://www.trollandtoad.com/category.php?...",
    "..."
  ],
  "item": [
    "https://www.trollandtoad.com/pokemon/...",
    "..."
  ]
}
```

- search: List of search URLs for scraping multiple products.
- item: List of individual product URLs.

### scraped_data.json
This file stores the previous scrapes data and is used to detect changes in price or stock.

### Discord Webhook
Update the DISCORD_WEBHOOK_URL in the script with your Discord webhook URL to receive notifications.

## Running the Scraper
Once the dependencies are installed and configuration is set up, run:

    python PokeBot.py

The script will:
1. Scrape data from the URLs specified in items.json.
2. Compare it with data in scraped_data.json.
3. Send Discord notifications for updates or new products.
4. Save the new data to scraped_data.json.

## Troubleshooting
- No output or errors: Verify that your URLs in items.json are correct and that your internet connection is active.
- Python not found: Ensure Python is installed and available in your system's PATH.
- Discord notifications not appearing: Double-check that the webhook URL is correct and that your network permits outgoing connections to Discord.

# License
This project is provided "as is" without warranty. Feel free to modify it for your own use.
