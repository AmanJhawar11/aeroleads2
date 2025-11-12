# Python & Twilio Autodialer with Call Status Tracking

This project is a simple autodialer built with Python. It reads a list of phone numbers from a CSV file, calls each number using the Twilio API, and records the status of each call (e.g., "completed," "no-answer," "failed") into a new output CSV file.

The project uses **Flask** and **ngrok** to create a live webhook. This webhook is essential for Twilio to send back real-time information about the call's status.

## ⚙️ How It Works

This project requires two terminals to run simultaneously:

1.  **Terminal 1: ngrok:** This tool creates a secure, public URL that connects to your local computer. Twilio needs a public URL to send call status updates. `ngrok` provides this "tunnel."
2.  **Terminal 2: Flask App:** This is a small web server (`flask_app.py`) that "listens" for the status updates from Twilio. When a call's status changes (e.g., the person picks up), Twilio sends a message to your `ngrok` URL, which forwards it to this Flask app.
3.  **Main Script (`phones.py`):** This is the script you run to *start* the whole process. It reads your CSV, tells Twilio to start calling, and provides the `ngrok` URL for Twilio to use as its "status webhook."

**The flow is:**
`phones.py` (start calls) → **Twilio API** → (calls phone) → **Twilio** (sends status) → **ngrok URL** → **Flask App** (receives status) → `phones.py` (gets status) → `call_results.csv`

---

## 📂 Project Files

* **`input_numbers.csv`**: This is your input file. It **must** have a column named `PhoneNumber` containing the numbers to call (in E.164 format, e.g., `+15551234567`).
* **`flask_app.py`**: The web server that listens for Twilio's webhooks. **You don't need to run this file directly**; it is run by `phones.py`.
* **`phones.py`**: The main script you run to launch the autodialer.
* **`call_results.csv`**: This file is **created** by the script after it runs. It contains your original numbers and a new `Status` column.

---

## 🚀 Setup & How to Run (Step-by-Step)

### Step 1: Prerequisites

1.  **Python 3:** Ensure you have Python 3 installed.
2.  **Twilio Account:**
    * Sign up for a [Twilio Account](https://www.twilio.com/try-twilio).
    * Buy a Twilio Phone Number (this is what you will call *from*).
    * Find your **Account SID** and **Auth Token** on your Twilio console dashboard. You will need these.
3.  **ngrok Account:**
    * Sign up for a free [ngrok Account](https://dashboard.ngrok.com/signup).
    * Follow their instructions to [install ngrok and add your auth token](https://ngrok.com/docs/getting-started/) to your machine.



### Step 2: Install Python Libraries

Open your terminal and install the necessary libraries:

bash
```pip install twilio flask pandas```

### Step 3: Prepare Your Input File
Name	      PhoneNumber	   Status	Feedback
Adrenalin	1800 444 445
AMD	      1800 425 6664	

### Step 4: Configure the phones.py Script
Open your phones.py file and find these variables at the top. This is the most important step.

# 1. ENTER YOUR TWILIO CREDENTIALS HERE

TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # <-- PASTE YOUR SID HERE
TWILIO_AUTH_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"    # <-- PASTE YOUR TOKEN HERE
TWILIO_PHONE_NUMBER = "+1xxxxxxxxxx"                     # <-- PASTE YOUR TWILIO NUMBER HERE


# 2. THIS WILL BE FILLED BY NGROK IN A LATER STEP

NGROK_BASE_URL = ""                                      # <-- LEAVE THIS EMPTY FOR NOW

INPUT_CSV_FILE = "input_numbers.csv"
OUTPUT_CSV_FILE = "call_results.csv"

### Step 5: Run ngrok (Terminal 1)
Open your first terminal.

The Flask app runs on port 5000 (by default). Start ngrok to create a tunnel to that port by typing:

Bash
```ngrok http 5000```

ngrok will start and show you a "Forwarding" URL. Copy the https.s URL. It will look something like this:

https://1a2b-3c4d-5e6f.ngrok-free.app

### Step 6: Add ngrok URL to Script
Go back to your phones.py script.

Paste the ngrok URL you just copied into the NGROK_BASE_URL variable. Make sure it's in quotes.

``NGROK_BASE_URL = "[https://1a2b-3c4d-5e6f.ngrok-free.app](https://1a2b-3c4d-5e6f.ngrok-free.app)"  # <-- PASTE YOUR NGROK URL HERE``
### Step 7: Run the Autodialer (Terminal 2)
Open a second terminal. (Leave your first ngrok terminal running!)

Make sure you are in the same project directory.

Run the main script:
	`python phones.py`

### Step 9: Get Your Results
When the script is finished, it will close everything down. You can now open the call_results.csv file. It will contain your original numbers plus the final status of each call.


