import pytest
from datetime import datetime, timedelta


@pytest.fixture
def sample_data_future():
    """
    Fixture Pytest : fournit un club et une compétition dont la date est future.

    Cette fixture est utilisée pour tester la réservation de places dans le futur,
    afin de ne pas déclencher l'erreur "past competition".

    Returns:
        tuple:
            - club (dict) : dictionnaire contenant le nom et les points du club.
            - competition (dict) : dictionnaire contenant le nom, le nombre de places
              et la date de la compétition (format "%Y-%m-%d %H:%M:%S").
    """
    club = {"name": "Iron Temple", "points": "10"}
    competition = {
        "name": "Spring Festival",
        "numberOfPlaces": "5",
        # Date future pour éviter l'erreur liée aux compétitions passées
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
    }
    return club, competition


def purchase_places_simulated(club, competition, places_required):
    """
    Simule la fonction purchasePlaces pour les tests unitaires.

    Cette fonction reproduit la logique de réservation de places et retourne
    directement le message flash qui serait affiché à l'utilisateur.

    Logique :
        1. Vérifie si la compétition est passée.
        2. Vérifie que le nombre de places demandé est > 0.
        3. Vérifie que le club ne demande pas plus de places que disponibles.
        4. Vérifie que le club a suffisamment de points.
        5. Vérifie que le club ne réserve pas plus de 12 places.
        6. Si tout est correct, met à jour le nombre de places de la compétition
           et les points du club, puis retourne un message de succès.

    Args:
        club (dict) : dictionnaire du club avec "name" et "points".
        competition (dict) : dictionnaire de la compétition avec "name",
                             "numberOfPlaces" et "date".
        places_required (int) : nombre de places que le club souhaite réserver.

    Returns:
        str: message simulé correspondant au résultat de la réservation.
    """
    competition_date = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")

    if competition_date < datetime.now():
        return "You cannot book a place on a past competition."
    if places_required <= 0:
        return "Number of places must be greater than zero."
    if places_required > int(competition["numberOfPlaces"]):
        return "Not enough places left in this competition."
    if places_required > int(club["points"]):
        return "You do not have enough points to book these places."
    if places_required > 12:
        return "Cannot book more than 12 places per competition."

    # Mise à jour des données si toutes les conditions sont remplies
    competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - places_required
    club["points"] = int(club["points"]) - places_required
    return "Great-booking complete!"


def test_cannot_book_more_places_than_available_unit(sample_data_future):
    """
    Test unitaire : un club ne peut pas réserver plus de places que disponibles.

    Scénario :
        1. Récupère un club et une compétition future via la fixture.
        2. Tente de réserver un nombre de places supérieur à celui disponible.
        3. Vérifie que le message retourné est correct.
        4. Vérifie que les données originales du club et de la compétition
           n'ont pas été modifiées.

    Args:
        sample_data_future (tuple) : tuple contenant le club et la compétition
                                     fourni par la fixture.
    """
    club, competition = sample_data_future
    initial_places = int(competition["numberOfPlaces"])
    initial_points = int(club["points"])

    # Tentative de réservation supérieure au nombre de places disponibles
    too_many = initial_places + 5
    message = purchase_places_simulated(club, competition, too_many)

    # Vérifie que le message d'erreur est correct
    assert message == "Not enough places left in this competition."
    # Vérifie que les données du club et de la compétition n'ont pas changé
    assert int(competition["numberOfPlaces"]) == initial_places
    assert int(club["points"]) == initial_points
