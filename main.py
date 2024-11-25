from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import pickle
import pandas as pd
import requests
import os

import gdown
new_df = pickle.load(open('movies.pkl','rb'))

file_id = '1BWTpaIBrpK-o8IUYi9Q0oElai6FDYflM'
url = f"https://drive.google.com/file/d/1BWTpaIBrpK-o8IUYi9Q0oElai6FDYflM/view?usp=sharing={file_id}"

output_file = "similarity.pkl"

gdown.download(url, output_file, quiet=False, fuzzy=True)

print("Download complete!")
import pickle

file_path = 'similarity.pkl'

try:
    with open(file_path, 'rb') as f:
        similarity = pickle.load(f)
except pickle.UnpicklingError as e:
    print(f"Error unpickling file: {e}")

API_KEY = os.getenv("TMDB_ID")  
BASE_URL = "https://api.themoviedb.org/3/movie/"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

app = FastAPI(title="Movie Recommendation API")

def fetch_movie_poster(movie_id):
    url = f"{BASE_URL}{movie_id}?api_key={API_KEY}"
    response = requests.get(url)

    if response.status_code == 200: 
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"{POSTER_BASE_URL}{poster_path}"  # Complete poster URL
        else:
            return None
    else:
        print(f"Error: Unable to fetch details for movie ID {movie_id}.")
        return None


def recommend(movie: str):
    try:
        movie_index = new_df[new_df['title'] == movie].index[0]
        distances = similarity[movie_index]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:10]
        recommendations = []

        for i in movie_list:
            movie_id = new_df.iloc[i[0]].movie_id
            recommendations.append({
                "title": new_df.iloc[i[0]].title,
                "poster_url": fetch_movie_poster(movie_id)
            })

        return recommendations
    except IndexError:
        raise HTTPException(status_code=404, detail=f"Movie '{movie}' not found in the dataset.")

@app.get("/")
def root():
    return {"message": "Welcome to the Movie Recommendation API. Use the /recommend endpoint."}

@app.get("/recommend", summary="Get movie recommendations")
def get_recommendations(movie: str = Query(..., description="The name of the movie for getting recommendations")):
    """
    It provide movie recommendations based on the given movie title.

    Arguments:
        movie (str): The title of the movie for recommendation.

    Returns:
        tuple: A tuple containing a list of recommended movie titles and their poster URL.
    """
    return recommend(movie)



