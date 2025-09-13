import pytest
from datetime import datetime, timedelta


@pytest.fixture
def sample_data_future():
    """
    Fournit des données de test pour un club et une compétition future.

    Comportement :
        1. Crée un club fictif avec un nom et un nombre de points.
        2. Crée une compétition fictive avec un nom, un nombre de places,
           et une date future (pour éviter les erreurs liées aux compétitions passées).

    Returns:
        tuple: (club, competition)
            - club (dict) : contient "name" et "points".
            - competition (dict) : contient "name", "numberOfPlaces" et "date".
    """
    # Club fictif pour le test
    club = {"name": "Iron Temple", "points": "20"}

    # Compétition fictive avec date future
    competition = {
        "name": "Spring Festival",
        "numberOfPlaces": "15",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
    }

    return club, competition


def purchase_places_simulated(club, competition, places_required):
    """
    Simule la logique de réservation de places pour un test unitaire.

    Cette fonction reproduit la logique métier de `purchasePlaces` afin
    de vérifier différents cas de réservation.

    Paramètres :
        club (dict) : dictionnaire représentant un club avec ses points.
        competition (dict) : dictionnaire représentant une compétition avec ses places.
        places_required (int) : nombre de places à réserver.

    Returns:
        str : message simulé retourné après la tentative de réservation.

    Messages possibles :
        - "You cannot book a place on a past competition."
        - "Number of places must be greater than zero."
        - "Not enough places left in this competition."
        - "You do not have enough points to book these places."
        - "Cannot book more than 12 places per competition."
        - "Great-booking complete!" : réservation réussie.
    """
    # Conversion de la date de la compétition en objet datetime
    competition_date = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")

    # Vérifie si la compétition est passée
    if competition_date < datetime.now():
        return "You cannot book a place on a past competition."

    # Vérifie que le nombre de places demandées est supérieur à 0
    if places_required <= 0:
        return "Number of places must be greater than zero."

    # Vérifie que le nombre de places demandées ne dépasse pas les places disponibles
    if places_required > int(competition["numberOfPlaces"]):
        return "Not enough places left in this competition."

    # Vérifie que le club dispose de points suffisants
    if places_required > int(club["points"]):
        return "You do not have enough points to book these places."

    # Limite de réservation par club
    if places_required > 12:
        return "Cannot book more than 12 places per competition."

    # Mise à jour des points du club et des places de la compétition
    competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - places_required
    club["points"] = int(club["points"]) - places_required

    return "Great-booking complete!"


def test_booking_more_than_12_places_unit(sample_data_future):
    """
    Test unitaire : un club ne peut pas réserver plus de 12 places.

    Comportement testé :
        1. Récupère le club et la compétition fictifs.
        2. Stocke les valeurs initiales des places et points.
        3. Tente de réserver 13 places (au-dessus de la limite autorisée).
        4. Vérifie que le message retourné correspond à l'erreur attendue.
        5. Vérifie que le nombre de places et les points du club n'ont pas été modifiés.

    Assertions :
        - message == "Cannot book more than 12 places per competition."
        - les données restent inchangées
    """
    club, competition = sample_data_future
    initial_places = int(competition["numberOfPlaces"])
    initial_points = int(club["points"])

    # Tentative de réservation de 13 places
    message = purchase_places_simulated(club, competition, 13)

    # Vérification du message d'erreur
    assert message == "Cannot book more than 12 places per competition."

    # Vérifie que le club et la compétition n'ont pas été modifiés
    assert int(competition["numberOfPlaces"]) == initial_places
    assert int(club["points"]) == initial_points
