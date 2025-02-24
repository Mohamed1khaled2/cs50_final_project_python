from fastapi import FastAPI, Request
import requests
from dotenv import load_dotenv
import os
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import redis
import base64



# Load .env variables
load_dotenv("app\.env")

# Setup FastAPI
app = FastAPI()

# set redis

redis_client = redis.Redis.from_url("redis://127.0.0.1:6379/", decode_responses=True)
redis_client = redis.Redis(
    host='redis-18430.c259.us-central1-2.gce.redns.redis-cloud.com',
    port=18430,
    decode_responses=True,
    username="default",
    password="D2pz2nnRM5ivIPXoPwuAU0fGu171wKNJ",
)

# Spotify API details
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"


CLIENT_ID = os.getenv("ClientID")
CLIENT_SECRET = os.getenv("ClientSecret")
REDIRECT_URI = "http://127.0.0.1:8000/callback"
ACCESS_TOKEN = ''

auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

@app.get("/login")
def login():
    """Redirect user to Spotify for authentication"""
    scope = "user-read-private user-read-email playlist-read-private playlist-read-collaborative"
    
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
    }
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"
    print(auth_url)
    return RedirectResponse(auth_url)


@app.get("/callback")
def callback(code: str):
    """Handle Spotify callback and get access token"""
 
    headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {auth_header}"
}
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    response = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
    token_info = response.json()

    print(token_info)
    
    if "access_token" in token_info:
        redis_client.set("spotify_token", token_info["access_token"])
        ACCESS_TOKEN = redis_client.get('spotify_token')
        return {"message" : "Login Susseful", "token":f"From redis {ACCESS_TOKEN}"}
    else:
        return {"error": "Authentication failed", "details": token_info}

