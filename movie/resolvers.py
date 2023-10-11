import json


def movie_with_id(_,info,_id):
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)
        for movie in movies['movies']:
            if movie['id'] == _id:
                return movie

def update_movie_rate(_,info,_id,_rate):
    newmovies = {}
    newmovie = {}
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies['movies']:
            if movie['id'] == _id:
                movie['rating'] = _rate
                newmovie = movie
                newmovies = movies
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(newmovies, wfile)
    return newmovie

def all_movies(_, info):
    with open('{}/data/movies.json'.format("."), "r") as jsf:
        movies = json.load(jsf)["movies"]
    return movies

def create_movie(_, info, _movie):
    new_movies = {}
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)["movies"]
    new_movies["movies"] = movies
    for movie in movies:
        if str(movie["id"]) == str(_movie["id"]):
            print("the movie already exists")
            return movie
    new_movies["movies"].append(_movie)
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(new_movies, wfile)
    return _movie

def delete_movie_by_id(_, info, _id):
    new_movies = {}
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)["movies"]
    new_movies["movies"] = movies
    for movie in movies:
        if str(movie["id"]) == _id:
            print("movie found")
            new_movies["movies"].remove(movie)
            with open('{}/data/movies.json'.format("."), "w") as wfile:
                json.dump(new_movies, wfile)
            print("movie deleted")
            return movie
    print("movie not found")
    return None
def resolve_actors_in_movie(movie, info):
    with open('{}/data/actors.json'.format("."), "r") as file:
        data = json.load(file)
        actors = [actor for actor in data['actors'] if movie['id'] in actor['films']]
        return actors