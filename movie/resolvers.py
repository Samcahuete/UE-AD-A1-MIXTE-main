import json


def movie_with_id(_,info,_id):
    """
    Resolver for the movie_with_id query
    Retrieves the movie associated with the given movie id
    :param _:
    :param info:
    :param _id: string
    :return: Movie
    """
    with open('{}/data/movies.json'.format("."), "r") as file:
        # load movies
        movies = json.load(file)
        for movie in movies['movies']:
            # if the id matches, return the movie
            if movie['id'] == _id:
                return movie

def update_movie_rate(_,info,_id,_rate):
    """
    Resolver for the update_movie_rate mutation
    Updates the rating of a movie given its id
    :param _:
    :param info:
    :param _id: string
    :param _rate: float
    :return: Movie
    """
    # copies used to update the database
    newmovies = {}
    newmovie = {}
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        # goes through all the movies
        for movie in movies['movies']:
            # if the id matches updates the rating
            if movie['id'] == _id:
                movie['rating'] = _rate
                newmovie = movie
                newmovies = movies
    # saves the changes in the database
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(newmovies, wfile)
    return newmovie

def all_movies(_, info):
    """
    Resolver for the all_movies query
    Retrieves all movies
    :param _:
    :param info:
    :return:
    """
    # load the data
    with open('{}/data/movies.json'.format("."), "r") as jsf:
        movies = json.load(jsf)["movies"]
    return movies

def create_movie(_, info, _movie):
    """
    Resolver for the create_movie mutation
    Adds a movie to the database
    :param _:
    :param info:
    :param _movie: Movie
    :return: Movie
    """
    # copy used to update the database
    new_movies = {}
    # loads movies
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)["movies"]
    new_movies["movies"] = movies
    #goes through all the movies to verify if the movie already exists
    for movie in movies:
        if str(movie["id"]) == str(_movie["id"]):
            print("the movie already exists")
            # stops the process
            return movie
    # adds the movie and updates the database
    new_movies["movies"].append(_movie)
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(new_movies, wfile)
    return _movie

def delete_movie_by_id(_, info, _id):
    """
    Resolver for the delete_movie_by_id mutation
    Deletes a movie given its id
    :param _:
    :param info:
    :param _id: string
    :return: Movie
    """
    # copy used to update the database
    new_movies = {}
    # loads movies
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)["movies"]
    new_movies["movies"] = movies
    # Looks for the requested movie
    for movie in movies:
        if str(movie["id"]) == _id:
            print("movie found")
            # removes the movie and updates the database
            new_movies["movies"].remove(movie)
            with open('{}/data/movies.json'.format("."), "w") as wfile:
                json.dump(new_movies, wfile)
            print("movie deleted")
            return movie
    print("movie not found")
    # stops the process
    return None


def resolve_actors_in_movie(movie, info):
    """
    Resolver for the actor field of Movie
    :param movie: Movie
    :param info:
    :return: Actor
    """
    # loads actors
    with open('{}/data/actors.json'.format("."), "r") as file:
        data = json.load(file)
        # retrieves actors whose saved movies includes the parent movie id
        actors = [actor for actor in data['actors'] if movie['id'] in actor['films']]
        return actors
