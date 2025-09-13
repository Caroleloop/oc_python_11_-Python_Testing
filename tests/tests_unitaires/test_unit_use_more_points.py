import pytest
from datetime import datetime, timedelta


@pytest.fixture
def sample_data():
    """
    Fournit des données simulées pour les tests unitaires.

    Cette fixture retourne un club et une compétition fictifs :
        - club : dictionnaire contenant le nom du club et le nombre de points.
        - competition : dictionnaire contenant le nom, le nombre de places
          disponibles et la date de la compétition.

    La date de la compétition est fixée dans le futur pour éviter les erreurs
    liées à une compétition passée lors des tests.

    Returns:
        tuple: (club, competition)
    """
    club = {"name": "Iron Temple", "points": "5"}  # Club simulé avec 5 points
    competition = {
        "name": "Spring Festival",
        "numberOfPlaces": "10",  # Nombre total de places disponibles
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),  # Date future
    }
    return club, competition


def can_book_places_simulated(club, competition, places_required):
    """
    Simule la vérification des conditions pour réserver des places.

    Cette fonction reproduit la logique de `purchasePlaces` pour les tests :
        1. Vérifie si la compétition est passée.
        2. Vérifie que le nombre de places demandé est positif.
        3. Vérifie que le nombre de places demandé ne dépasse pas
           le nombre de places restantes.
        4. Vérifie que le club dispose de suffisamment de points.
        5. Vérifie que le club ne réserve pas plus de 12 places maximum.

    Args:
        club (dict): Dictionnaire contenant les informations du club.
        competition (dict): Dictionnaire contenant les informations de la compétition.
        places_required (int): Nombre de places que le club souhaite réserver.

    Returns:
        tuple: (bool, str)
            - bool : True si la réservation est possible, False sinon.
            - str : Message d'erreur si la réservation est impossible, chaîne vide sinon.
    """
    competition_date = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")

    # Vérifie si la compétition est déjà passée
    if competition_date < datetime.now():
        return False, "You cannot book a place on a past competition."

    # Vérifie que le nombre de places demandées est positif
    if places_required <= 0:
        return False, "Number of places must be greater than zero."

    # Vérifie qu'il reste assez de places dans la compétition
    if places_required > int(competition["numberOfPlaces"]):
        return False, "Not enough places left in this competition."

    # Vérifie que le club dispose de suffisamment de points
    if places_required > int(club["points"]):
        return False, "You do not have enough points to book these places."

    # Limite de réservation par club
    if places_required > 12:
        return False, "Cannot book more than 12 places per competition."

    # Si toutes les conditions sont respectées, la réservation est possible
    return True, ""


def test_cannot_redeem_more_points_than_available_unit(sample_data):
    """
    Test unitaire pour vérifier qu'un club ne peut pas réserver plus de places
    qu'il n'a de points disponibles.

    Scénario testé :
        - Le club a 5 points.
        - Il tente de réserver 10 places.

    Comportement attendu :
        - La réservation échoue.
        - Le message d'erreur indique que le club n'a pas assez de points.

    Args:
        sample_data (fixture): Fixture Pytest fournissant un club et une compétition simulés.
    """
    club, competition = sample_data
    places_required = 10  # Nombre de places demandé supérieur aux points du club

    # Appel de la fonction simulée de réservation
    can_book, message = can_book_places_simulated(club, competition, places_required)

    # Vérifie que la réservation est refusée et que le message correspond
    assert can_book is False
    assert message == "You do not have enough points to book these places."
