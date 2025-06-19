import requests
import os

def generate_voice(roast_text, voice_id="21m00Tcm4TlvDq8ikWAM"):
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": roast_text,
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        return response.content
    else:
        print("TTS Generation Failed", response.text)
        return None