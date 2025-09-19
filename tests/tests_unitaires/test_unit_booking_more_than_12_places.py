import pytest
from datetime import datetime, timedelta
from server import app


@pytest.fixture
def client():
    """
    Fixture qui fournit un client Flask pour les tests.

    - Configure Flask en mode TESTING pour éviter les effets de bord (sessions, flash, fichiers JSON)
    - Permet d'envoyer des requêtes HTTP simulées vers l'application
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_data_future(mocker):
    """
    Mocke les données globales `clubs` et `competitions` avec une compétition future.

    Crée :
        - un club avec 20 points
        - une compétition avec 15 places et une date dans le futur

    Patch les variables globales pour que les tests n'affectent pas les fichiers JSON.

    Returns:
        tuple: (club, competition) pour les tests
    """
    club = {"name": "Iron Temple", "email": "iron@club.com", "points": "20"}
    competition = {
        "name": "Spring Festival",
        "numberOfPlaces": "15",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Remplace les listes globales par nos mocks
    mocker.patch("server.clubs", [club])
    mocker.patch("server.competitions", [competition])

    return club, competition


def test_booking_more_than_12_places(client, sample_data_future):
    """
    Test d'intégration Flask :

    Vérifie qu'un club ne peut pas réserver plus de 12 places pour une compétition via /purchasePlaces.

    Étapes :
        1. Récupère le club et la compétition mockés.
        2. Tente de réserver 13 places (plus que la limite autorisée de 12).
        3. Vérifie que le flash message d'erreur est affiché.
        4. Vérifie que les points du club et le nombre de places restent inchangés.
    """
    club, competition = sample_data_future
    initial_places = int(competition["numberOfPlaces"])
    initial_points = int(club["points"])

    # Tentative de réservation excessive
    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": competition["name"], "places": 13},
        follow_redirects=True,  # Suivre les redirections pour récupérer le flash message
    )

    # Vérifie la présence du message d'erreur
    assert b"Cannot book more than 12 places per competition." in response.data

    # Vérifie que les données du club et de la compétition n'ont pas été modifiées
    assert int(competition["numberOfPlaces"]) == initial_places
    assert int(club["points"]) == initial_points
