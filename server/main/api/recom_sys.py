# -*- coding: utf-8 -*-
"""User Route for Demo application."""

import pickle
from flask import Blueprint, jsonify
from server.main.services.demographic_service import DemographicService
from server.models.prep.preprocess import Process
from server.models.content.content_based_rec import ContentRecommender

route = Blueprint('demographic', __name__)

BASE_PATH = 'https://raw.githubusercontent.com/ml-heroes/ml-dataset/master/movies/'
LARGE_BASE_PATH = 'https://dl.dropboxusercontent.com/s/toir5bjqhl463q4/'
MOVIE_DB_URL = 'https://api.themoviedb.org/3/movie/{}?api_key=2085f970b90ca4a5b5047991206ede55'
BASE_POSTER_URL = 'http://image.tmdb.org/t/p/w185/'

processed_data = Process(BASE_PATH, LARGE_BASE_PATH, BASE_POSTER_URL)
demographic_rec = DemographicService(processed_data.metadata)
content_rec = ContentRecommender(processed_data.metadata, processed_data.links_small,
                                 processed_data.keywords, processed_data.credits)


svd = pickle.load(open("server/models/collab/svd.data", "rb" ))
top_n = pickle.load(open("server/models/collab/top_n.data", "rb" ))

@route.route("/api/collabs/<int:user_id>/<int:movie_id>")
def get_collaborative(user_id, movie_id):
    return jsonify(svd.predict(user_id, movie_id))

@route.route("/api/collabs/<int:user_id>")
def get_top_n(user_id):
    return jsonify(top_n[user_id])


@route.route("/api/movies/<movie_id>")
def get_movie_detail(movie_id):
    return demographic_rec.find_movie_by_id(movie_id).to_json(orient='records')


@route.route("/api/trending")
def get_demographics():
    return demographic_rec.trending().to_json(orient='records')


@route.route("/api/popular")
def get_popular():
    return demographic_rec.popular().to_json(orient='records')


@route.route("/api/likeable")
def get_likeable():
    return demographic_rec.likeable().to_json(orient='records')


@route.route("/api/genres/<genre>")
def get_genres(genre):
    return demographic_rec.trending_genre(genre).to_json(orient='records')


@route.route("/api/content/<title>")
def content_based(title):
    mvs = content_rec.recommend(title, 3)
    results = dict()
    for mv in mvs:
        mv_ids = metadata[metadata['title'] == mv]['id']
        for mv_id in mv_ids:
            mv_ovw = metadata[metadata['id'] == mv_id]['overview'].values[0]
            resp = requests.get(POSTER_API_URL.format(mv_id))
            resp_json = resp.json()
            results[mv_id] = {"title": mv, "poster_path": resp_json.get('poster_path'), "overview": mv_ovw}
    return results