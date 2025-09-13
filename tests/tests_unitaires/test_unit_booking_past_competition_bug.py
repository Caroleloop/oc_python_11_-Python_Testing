import pytest
from datetime import datetime, timedelta


@pytest.fixture
def sample_data_past():
    """
    Fournit des données de test pour une compétition passée.

    Cette fixture crée :
        - un club avec un certain nombre de points,
        - une compétition dont la date est dans le passé.

    Returns:
        tuple: (club, competition)
            - club (dict) : dictionnaire contenant le nom et les points du club.
            - competition (dict) : dictionnaire contenant le nom, le nombre de places
              disponibles et la date de la compétition.
    """
    club = {"name": "Iron Temple", "points": "10"}
    competition = {
        "name": "Winter Festival",
        "numberOfPlaces": "5",
        # Date passée pour simuler une réservation interdite
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
    }
    return club, competition


def purchase_places_simulated(club, competition, places_required):
    """
    Simule l'achat de places pour une compétition, en reproduisant la logique
    de la fonction `purchasePlaces` de l'application.

    Cette fonction effectue plusieurs vérifications :
        1. Vérifie que la compétition n'est pas passée.
        2. Vérifie que le nombre de places demandées est supérieur à zéro.
        3. Vérifie qu'il y a suffisamment de places disponibles dans la compétition.
        4. Vérifie que le club possède suffisamment de points pour réserver.
        5. Limite la réservation à un maximum de 12 places par compétition.

    Si toutes les conditions sont respectées, elle met à jour :
        - le nombre de places disponibles de la compétition,
        - les points du club.

    Args:
        club (dict): Informations sur le club (nom, points).
        competition (dict): Informations sur la compétition (nom, nombre de places, date).
        places_required (int): Nombre de places que le club souhaite réserver.

    Returns:
        str: Message simulé qui serait affiché à l'utilisateur via flash.
    """
    competition_date = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")

    # Vérification si la compétition est passée
    if competition_date < datetime.now():
        return "You cannot book a place on a past competition."

    # Vérification du nombre de places demandées
    if places_required <= 0:
        return "Number of places must be greater than zero."

    # Vérification des places disponibles
    if places_required > int(competition["numberOfPlaces"]):
        return "Not enough places left in this competition."

    # Vérification des points du club
    if places_required > int(club["points"]):
        return "You do not have enough points to book these places."

    # Limite maximale par réservation
    if places_required > 12:
        return "Cannot book more than 12 places per competition."

    # Mise à jour des données si toutes les conditions sont respectées
    competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - places_required
    club["points"] = int(club["points"]) - places_required
    return "Great-booking complete!"


def test_booking_past_competition_blocked_unit(sample_data_past):
    """
    Test unitaire : vérifie qu'une réservation pour une compétition passée est bloquée.

    Cette fonction :
        1. Récupère les données de test fournies par la fixture `sample_data_past`.
        2. Tente de réserver 1 place pour la compétition passée.
        3. Vérifie que le message retourné correspond bien à l'interdiction
           de réservation pour une compétition passée.

    Args:
        sample_data_past (fixture): Tuple contenant le club et la compétition passée.

    Asserts:
        - Le message renvoyé doit être : "You cannot book a place on a past competition."
    """
    club, competition = sample_data_past

    # Simulation de la réservation
    message = purchase_places_simulated(club, competition, 1)

    # Vérification du résultat
    assert message == "You cannot book a place on a past competition."
