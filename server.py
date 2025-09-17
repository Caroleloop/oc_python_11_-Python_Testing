import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime


def loadClubs():
    with open("clubs.json") as c:
        listOfClubs = json.load(c)["clubs"]
        return listOfClubs


def loadCompetitions():
    with open("competitions.json") as comps:
        listOfCompetitions = json.load(comps)["competitions"]
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = "something_special"

competitions = loadCompetitions()
clubs = loadClubs()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def showSummary():
    """
    Affiche le résumé d'un club après saisie de l'email du secrétaire.

    Cette route traite le formulaire envoyé depuis la page d'accueil (index.html)
    contenant l'email du club.

    Comportement :
        1. Récupère l'email depuis le formulaire POST.
        2. Cherche le club correspondant dans la liste `clubs`.
        3. Si aucun club n'est trouvé :
            - Envoie un message flash : "Sorry, that email wasn't found."
            - Redirige vers la page d'accueil (index.html).
        4. Si un club est trouvé :
            - Récupère le premier club correspondant.
            - Affiche la page `welcome.html` avec les informations du club
              et la liste des compétitions disponibles.

    Flash messages :
        - "Sorry, that email wasn't found." : affiché si l'email n'existe pas.

    Returns:
        - redirect vers "index" si email non trouvé.
        - render_template("welcome.html") si email valide.
    """
    email = request.form["email"]
    matching_clubs = [club for club in clubs if club["email"] == email]

    if not matching_clubs:
        flash("Sorry, that email wasn't found.")
        return redirect(url_for("index"))

    club = matching_clubs[0]
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    foundClub = [c for c in clubs if c["name"] == club][0]
    foundCompetition = [c for c in competitions if c["name"] == competition][0]
    if foundClub and foundCompetition:
        return render_template("booking.html", club=foundClub, competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    competition = [c for c in competitions if c["name"] == request.form["competition"]][0]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    placesRequired = int(request.form["places"])

    # Vérification que le club dispose de suffisamment de points
    if placesRequired > int(club["points"]):
        flash("You do not have enough points to book these places.")
        return render_template("welcome.html", club=club, competitions=competitions)

    competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - placesRequired
    flash("Great-booking complete!")
    return render_template("welcome.html", club=club, competitions=competitions)


# TODO: Add route for points display


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
