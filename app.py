from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
from flask import Flask, render_template, request, jsonify
import csv

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer "  + token}

def search_for_album(token, album_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={album_name}&type=album&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["albums"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    return json_result[0]

def get_album(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def get_genre(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    genres = ["hip hop", "rap", "pop", "rock","electro", "contemporary country", "country"]
    if (len(json_result["genres"]) == 0):
        return "Alternative"
    else:
        for genre in genres:
            if genre in json_result["genres"]:
                return genre
        # return json_result["genres"][0] # return alternative here
        return "Alternative"


@app.route('/album', methods=["POST"])
def POST_album():
    token = get_token()
    album = request.form["course"]
    result = search_for_album(token, album)
    album_id = result["id"]
    album_info = get_album(token, album_id)
    returnAlbum = {"albumname": album_info["name"]}
    returnAlbum["numoftracks"] = album_info["total_tracks"]
    returnAlbum["artist"] = album_info["artists"][0]["name"]
    artistid = album_info["artists"][0]["uri"][15:]
    returnAlbum["genre"] = get_genre(token, artistid)
    # if (len(album_info["genres"]) == 0):
    #     returnAlbum["genre"] = "Alternative"
    # else:
    #     returnAlbum["genre"] = f"{album_info["genres"][0]}"
    returnAlbum["releasedate"] = album_info["release_date"][:4] # only getting year # also is string atm
    returnAlbum["popularity"] = album_info["popularity"]
    # print(album_info)
    return returnAlbum, 200

@app.route('/getAOD', methods=["POST"])
def POST_aod():
    day = int(request.form["day"])
    
    with open('data.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        count = 0
        for row in csv_reader:
            if count == day:
                return {"nameAOD": row[0]}
            count+=1
            
    return "ERROR", 500

    

# token = get_token()
# result = search_for_album(token, "The New Abnormal")
# album_id = result["id"]
# album_info = get_album(token, album_id)

# print(album_info)