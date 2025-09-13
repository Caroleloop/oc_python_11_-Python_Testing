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
    """
    Permet à un club de réserver des places pour une compétition.

    Cette route traite le formulaire envoyé depuis la page `welcome.html`,
    contenant le nom du club, le nom de la compétition et le nombre de places
    à réserver.

    Comportement :
        1. Récupère la compétition et le club correspondants aux champs du formulaire.
        2. Convertit le nombre de places demandées en entier.
        3. Vérifie plusieurs conditions de validité avant d'accepter la réservation :
            - La compétition ne doit pas être passée.
            - Le nombre de places doit être supérieur à 0.
            - Le nombre de places restantes dans la compétition doit être suffisant.
            - Le club doit disposer d'assez de points.
            - Un club ne peut réserver plus de 12 places par compétition.
        4. Si une condition échoue :
            - Envoie un message flash approprié.
            - Réaffiche la page `welcome.html` avec les infos du club et des compétitions.
        5. Si toutes les conditions sont respectées :
            - Décrémente le nombre de places disponibles pour la compétition.
            - Décrémente les points du club en fonction du nombre de places réservées.
            - Envoie un message flash de confirmation.
            - Retourne la page `welcome.html`.

    Flash messages :
        - "You cannot book a place on a past competition."
        - "Number of places must be greater than zero."
        - "Not enough places left in this competition."
        - "You do not have enough points to book these places."
        - "Cannot book more than 12 places per competition."
        - "Great-booking complete!"

    Returns:
        - render_template("welcome.html") avec le club et les compétitions mises à jour.
    """
    # Récupération de la compétition et du club via les données du formulaire
    competition = [c for c in competitions if c["name"] == request.form["competition"]][0]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    placesRequired = int(request.form["places"])

    # Vérification que la compétition n'est pas déjà passée
    competition_date = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")
    if competition_date < datetime.now():
        flash("You cannot book a place on a past competition.")
        return render_template("welcome.html", club=club, competitions=competitions)

    # Vérification que le nombre de places demandé est valide (> 0)
    if placesRequired <= 0:
        flash("Number of places must be greater than zero.")
        return render_template("welcome.html", club=club, competitions=competitions)

    # Vérification qu'il reste assez de places dans la compétition
    if placesRequired > int(competition["numberOfPlaces"]):
        flash("Not enough places left in this competition.")
        return render_template("welcome.html", club=club, competitions=competitions)

    # Vérification que le club dispose de suffisamment de points
    if placesRequired > int(club["points"]):
        flash("You do not have enough points to book these places.")
        return render_template("welcome.html", club=club, competitions=competitions)

    # Limitation à 12 places maximum par club et par compétition
    if placesRequired > 12:
        flash("Cannot book more than 12 places per competition.")
        return render_template("welcome.html", club=club, competitions=competitions)

    # Mise à jour des données : décrémentation des places et des points du club
    competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - placesRequired
    club["points"] = int(club["points"]) - placesRequired

    # Confirmation de la réservation
    flash("Great-booking complete!")
    return render_template("welcome.html", club=club, competitions=competitions)


# TODO: Add route for points display
@app.route("/points")
def points():
    """
    Affiche un tableau public en lecture seule des clubs et de leurs points.
    Accessible sans connexion.
    """
    return render_template("points.html", clubs=clubs)


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
