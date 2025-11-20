from google_auth_oauthlib.flow import InstalledAppFlow

# * Scopes needed for Gmail and Calendar
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar"
]

# * Get refresh token (run once)
def get_refresh_token():
    print("Starting OAuth flow...")
    print("A browser window will open. Please sign in and authorize the app.")
    
    # * Open browser 
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    
    # * Run a local server to handle OAuth flow
    creds = flow.run_local_server(port=0)
    
    # * Print refresh token
    print("\n" + "="*50)
    print("SUCCESS! Here is your refresh token:")
    print("="*50)
    print(f"\n{creds.refresh_token}\n")
    print("="*50)
    print("\nCopy this refresh token and add it to your .env file:")
    print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}\n")
    
    # * Save to token.json file
    with open("token.json", "w") as token:
        token.write(creds.to_json())
        
    print("Saved to token.json!")
    return creds

if __name__ == "__main__":
    get_refresh_token()