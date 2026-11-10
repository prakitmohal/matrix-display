import requests

def get_joke():
    try:
        reply = requests.get(
            "https://icanhazdadjoke.com/",
            headers={"Accept": "text/plain",
                     "User-Agent": "github.com/prakitmohal/matrix-display"},
            timeout=10,
        )
        return reply.text.strip()
    
    except Exception:
        return "API UNAVAILABLE"
