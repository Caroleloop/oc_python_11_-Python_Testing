import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime


def loadClubs():
    """
    Charge la liste des clubs depuis le fichier JSON 'clubs.json'.

    Returns:
        list: Liste des clubs sous forme de dictionnaires.
    """
    with open("clubs.json") as c:
        listOfClubs = json.load(c)["clubs"]
        return listOfClubs


def loadCompetitions():
    """
    Charge la liste des compétitions depuis le fichier JSON 'competitions.json'.

    Returns:
        list: Liste des compétitions sous forme de dictionnaires.
    """
    with open("competitions.json") as comps:
        listOfCompetitions = json.load(comps)["competitions"]
        return listOfCompetitions


def updateData():
    """
    Sauvegarde les données de clubs et compétitions dans leurs fichiers JSON.

    Cette fonction :
        - Convertit les points des clubs et le nombre de places des compétitions
          en entiers pour garantir la cohérence.
        - Écrit les données normalisées dans leurs fichiers JSON respectifs.

    Note:
        Si l'application est en mode TESTING (app.config["TESTING"] == True),
        les fichiers JSON ne sont pas modifiés.
    """
    if app.config.get("TESTING"):
        return

    # Normalisation des points des clubs
    for club in clubs:
        club["points"] = int(club["points"])

    # Normalisation du nombre de places des compétitions
    for competition in competitions:
        competition["numberOfPlaces"] = int(competition["numberOfPlaces"])

    # Écriture dans les fichiers JSON
    with open("clubs.json", "w") as c:
        json.dump({"clubs": clubs}, c, indent=4)

    with open("competitions.json", "w") as comps:
        json.dump({"competitions": competitions}, comps, indent=4)


# Création de l'application Flask
app = Flask(__name__)
app.secret_key = "something_special"  # Clé secrète pour les sessions et flash messages

# Chargement initial des données
competitions = loadCompetitions()
clubs = loadClubs()


@app.route("/")
def index():
    """
    Page d'accueil du site.

    Affiche le formulaire de connexion par email pour le secrétaire.
    """
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def showSummary():
    """
    Affiche le résumé d'un club après saisie de l'email du secrétaire.

    Processus :
        1. Récupère l'email depuis le formulaire POST.
        2. Cherche le club correspondant dans la liste `clubs`.
        3. Si aucun club n'est trouvé, redirige vers la page d'accueil avec un message flash.
        4. Sinon, affiche la page 'welcome.html' avec les informations du club et les compétitions.

    Flash messages :
        - "Sorry, that email wasn't found." si email non reconnu.
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
    """
    Page de réservation pour un club et une compétition donnés.

    Args:
        competition (str): Nom de la compétition
        club (str): Nom du club

    Returns:
        render_template: Page 'booking.html' si club et compétition trouvés,
                         sinon retour à 'welcome.html' avec un message flash.
    """
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
    Traite l'achat de places pour une compétition par un club.

    Vérifie plusieurs règles :
        - La compétition n'est pas passée.
        - Le nombre de places demandées est > 0.
        - Suffisamment de places disponibles.
        - Le club a assez de points.
        - Limite de 12 places par compétition.

    Si toutes les validations passent :
        - Décrémente les places disponibles et les points du club.
        - Met à jour les fichiers JSON.
        - Affiche un message de succès.
    """
    competition = next(c for c in competitions if c["name"] == request.form["competition"])
    club = next(c for c in clubs if c["name"] == request.form["club"])
    places_required = int(request.form["places"])

    competition_date = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")

    # Liste de validations avec message et condition
    validations = [
        ("You cannot book a place on a past competition.", competition_date < datetime.now()),
        ("Number of places must be greater than zero.", places_required <= 0),
        ("Not enough places left in this competition.", places_required > int(competition["numberOfPlaces"])),
        ("You do not have enough points to book these places.", places_required > int(club["points"])),
        ("Cannot book more than 12 places per competition.", places_required > 12),
    ]

    # Vérification de chaque condition
    for message, condition in validations:
        if condition:
            flash(message)
            return render_template("welcome.html", club=club, competitions=competitions)

    # Mise à jour des données si validation réussie
    competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - places_required
    club["points"] = int(club["points"]) - places_required

    updateData()
    flash("Great-booking complete!")
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/points")
def points():
    """
    Affiche un tableau public des clubs et de leurs points.

    Accessible sans connexion.
    """
    return render_template("points.html", clubs=clubs)


@app.route("/logout")
def logout():
    """
    Déconnecte le club et redirige vers la page d'accueil.
    """
    return redirect(url_for("index"))
