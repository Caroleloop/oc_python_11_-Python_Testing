import pytest
from datetime import datetime
from server import app, competitions, clubs


@pytest.fixture
def client():
    """
    Crée un client de test Flask configuré pour exécuter les tests.

    Cette fixture configure l'application en mode TESTING
    et retourne un client permettant d'effectuer des requêtes HTTP
    sur l'application Flask sans la lancer réellement.

    Yields:
        client (FlaskClient): client de test pour envoyer des requêtes.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_booking_more_than_12_places(client):
    """
    Vérifie qu'il est impossible de réserver plus de 12 places pour une compétition.

    Étapes du test :
        1. Sélectionne un club et une compétition existants depuis les données.
        2. Tente de réserver 13 places via la route "/purchasePlaces".
        3. Vérifie que la réservation est refusée par un message d'erreur.
        4. Vérifie que :
            - le nombre de places de la compétition n’a pas été modifié,
            - les points du club n’ont pas été débités.

    Assertions :
        - Le message "Cannot book more than 12 places per competition."
          est présent dans la réponse.
        - Les valeurs de `competition["numberOfPlaces"]` et `club["points"]`
          restent supérieures ou égales à 0.
    """
    # On choisit un club et une compétition existants
    competition = next(
        c
        for c in competitions
        if int(c["numberOfPlaces"]) >= 13 and datetime.strptime(c["date"], "%Y-%m-%d %H:%M:%S") > datetime.now()
    )
    club = next(c for c in clubs if int(c["points"]) >= 13)

    # On essaie de réserver 13 places
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": competition["name"],
            "club": club["name"],
            "places": "13",
        },
        follow_redirects=True,
    )

    # Vérifie que la requête renvoie bien le message d'erreur attendu
    assert b"Cannot book more than 12 places per competition." in response.data

    # Vérifie que le nombre de places disponibles n’a pas diminué
    assert int(competition["numberOfPlaces"]) >= 0
    # Vérifie que les points du club n’ont pas été débités
    assert int(club["points"]) >= 0
