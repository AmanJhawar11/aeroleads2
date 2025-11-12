import os
import argparse
import pandas as pd
import time
import requests
from twilio.rest import Client
import phonenumbers
import re


TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_PHONE_NUMBER = '' 
NGROK_URL = 'https://armando-clawless-unclannishly.ngrok-free.dev' # LIVE ngrok URL
CSV_FILE = 'Book 2(sheet1) (1).csv'

CSV_FILE = 'right.csv'              
OUTPUT_FILE = 'status_file.csv'      


client = None


def normalize_phone(original_phone_number: str) -> str:
    """
    Normalize and return an E.164 phone number string or raise ValueError.
    This version assumes "US" for 1800 numbers.
    """
    
    parsed_number = phonenumbers.parse(original_phone_number, "US")
    
    if not phonenumbers.is_valid_number(parsed_number):
        #
        raise ValueError(f"Number '{original_phone_number}' is not valid.")
        
    # This will return numbers in the correct +1800444445 format
    return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)


def make_calls(csv_path: str = CSV_FILE):
    try:
        # We READ from the original csv_path (number.csv)
        df = pd.read_csv(csv_path, sep=',')
        if df.empty:
            print('CSV is empty or parsing produced no rows.')
            return
    except FileNotFoundError:
        print(f"ERROR: '{csv_path}' not found. Please create it.")
        return
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    
    def _normalize_phone(original_phone_number: str) -> str:
        return normalize_phone(original_phone_number)

    
    for index, row in df.iterrows():
        original_phone_number = str(row.get('PhoneNumber', '')).strip()
        name = str(row.get('Name', ''))

        
        if not original_phone_number:
            continue
        

        
        status = row.get('Status', '')
        if pd.notna(status) and status != '':
            print(f"Skipping {name} (already has status: {status})")
            continue

        try:
            e164_phone_number = _normalize_phone(original_phone_number)
            print(f"Formatting {original_phone_number} -> {e164_phone_number}")
        except Exception as e:
            print(f"SKIPPING {name}: Could not format phone number '{original_phone_number}'. Error: {e}")
            df.at[index, 'Status'] = 'Invalid Number Format'
            
            df.to_csv(OUTPUT_FILE, index=False)
            continue

        print(f"Calling {name} at {e164_phone_number}...")

        if getattr(make_calls, 'dry_run', False):
            print(f"[DRY-RUN] Would call {e164_phone_number} from {TWILIO_PHONE_NUMBER}")
            df.at[index, 'Status'] = 'dry-run'
            
            df.to_csv(OUTPUT_FILE, index=False)
            continue

        global client
        if client is None:
            if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER):
                print("ERROR: Missing Twilio credentials. Check the top of the script.")
                df.at[index, 'Status'] = 'Missing Credentials'
                
                df.to_csv(OUTPUT_FILE, index=False)
                continue
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        try:
            call = client.calls.create(
                to=e164_phone_number,
                from_=TWILIO_PHONE_NUMBER,
                url=f"{NGROK_URL}/voice",
                machine_detection='Enable'
            )

            print(f"Call initiated with SID: {call.sid}")

            call_status = call.status
            while call_status not in ['completed', 'busy', 'no-answer', 'failed', 'canceled']:
                time.sleep(5)
                call = client.calls.get(call.sid).fetch()
                call_status = call.status
                print(f"Call status: {call_status}")

            df.at[index, 'Status'] = call_status

            if call_status == 'completed':
                answered_by = call.answered_by
                print(f"Call answered by: {answered_by}")

                if answered_by == 'human' or answered_by == 'unknown':
                    response = requests.get(f"{NGROK_URL}/get_response/{call.sid}")
                    feedback_text = response.text
                    if feedback_text != "NO_RESPONSE":
                        df.at[index, 'Feedback'] = feedback_text
                        print(f"Feedback received: {feedback_text}")
                    else:
                        df.at[index, 'Feedback'] = "No speech detected"
                else:
                    df.at[index, 'Feedback'] = "Voicemail detected"
            else:
                df.at[index, 'Feedback'] = "Call did not complete"

            
            df.to_csv(OUTPUT_FILE, index=False)
            print("Waiting 10 seconds before next call...\n")
            time.sleep(10)

        except Exception as e:
            print(f"Error calling {e164_phone_number}: {e}")
            df.at[index, 'Status'] = 'Error'
            df.at[index, 'Feedback'] = str(e)
            
            df.to_csv(OUTPUT_FILE, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Autodialer')
    parser.add_argument('--csv', default=CSV_FILE, help='Path to CSV file')
    parser.add_argument('--dry-run', action='store_true', help='Do not place real calls; just simulate')
    args = parser.parse_args()

    
    setattr(make_calls, 'dry_run', args.dry_run)

    
    if args.csv != CSV_FILE:
        CSV_FILE = args.csv
    make_calls(CSV_FILE)