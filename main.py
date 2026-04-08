from dotenv import load_dotenv
import os

load_dotenv()

def main():
    api_key = os.getenv("ANTROPIC_API_KEY")

    if not api_key:
        print("ERROR: No API key found. Check your .env file.")
        return
    
    print("QUARK AI is initialised")
    print(f"API key loaded:{api_key[:8]}...{api_key[-4:]}")

if __name__ == "__main__":
    main()