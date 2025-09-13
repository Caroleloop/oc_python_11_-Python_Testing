import pytest
from datetime import datetime, timedelta


@pytest.fixture
def sample_data():
    """
    Fournit des données simulées pour les tests unitaires.

    Cette fixture retourne un club et une compétition simulés avec des valeurs
    prédéfinies pour tester la réservation de places.

    Structure des données :
        club : dict
            - name : str -> nom du club
            - points : str -> nombre de points disponibles
        competition : dict
            - name : str -> nom de la compétition
            - numberOfPlaces : str -> nombre de places disponibles
            - date : str -> date de la compétition au format "%Y-%m-%d %H:%M:%S", toujours future pour les tests

    Returns:
        tuple : (club, competition)
    """
    club = {"name": "Iron Temple", "points": "5"}
    competition = {
        "name": "Spring Festival",
        "numberOfPlaces": "10",
        # Date future pour éviter l'erreur de compétition passée
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
    }
    return club, competition


def purchase_places_simulated(club, competition, places_required):
    """
    Simule la réservation de places pour un club dans une compétition.

    Cette fonction reproduit la logique de la fonction réelle `purchasePlaces`
    en vérifiant toutes les conditions possibles avant la réservation.

    Conditions vérifiées :
        1. La compétition est-elle passée ?
        2. Le nombre de places demandé est-il positif ?
        3. Le nombre de places demandé dépasse-t-il les places disponibles ?
        4. Le club a-t-il assez de points ?
        5. Le nombre de places demandé dépasse-t-il 12 ?

    Si toutes les conditions sont validées :
        - Les points du club sont décrémentés
        - Le nombre de places de la compétition est mis à jour
        - Retourne un message de succès

    Args:
        club (dict) : dictionnaire représentant le club
        competition (dict) : dictionnaire représentant la compétition
        places_required (int) : nombre de places à réserver

    Returns:
        str : message de résultat de la réservation
    """
    competition_date = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")

    # Vérification si la compétition est passée
    if competition_date < datetime.now():
        return "You cannot book a place on a past competition."

    # Vérification si le nombre de places est positif
    if places_required <= 0:
        return "Number of places must be greater than zero."

    # Vérification du nombre de places disponibles
    if places_required > int(competition["numberOfPlaces"]):
        return "Not enough places left in this competition."

    # Vérification du nombre de points du club
    if places_required > int(club["points"]):
        return "You do not have enough points to book these places."

    # Vérification du nombre maximum de places par réservation
    if places_required > 12:
        return "Cannot book more than 12 places per competition."

    # Mise à jour des données si toutes les vérifications sont OK
    competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - places_required
    club["points"] = int(club["points"]) - places_required

    return "Great-booking complete!"


def test_purchase_places_deducts_points_unit(sample_data):
    """
    Test unitaire pour vérifier que la réservation décrémente correctement
    les points du club et le nombre de places de la compétition.

    Scénario testé :
        - Réserver 1 place pour un club avec suffisamment de points et
          une compétition ayant des places disponibles.

    Vérifications :
        1. Le message de succès est correct
        2. Les points du club sont décrémentés de 1
        3. Le nombre de places de la compétition est décrémenté de 1

    Args:
        sample_data (tuple) : fixture fournissant un club et une compétition simulés
    """
    club, competition = sample_data
    initial_points = int(club["points"])
    initial_places = int(competition["numberOfPlaces"])

    # Simulation de la réservation d'une place
    message = purchase_places_simulated(club, competition, 1)

    # Assertions pour vérifier le comportement attendu
    assert message == "Great-booking complete!"
    assert int(club["points"]) == initial_points - 1
    assert int(competition["numberOfPlaces"]) == initial_places - 1
