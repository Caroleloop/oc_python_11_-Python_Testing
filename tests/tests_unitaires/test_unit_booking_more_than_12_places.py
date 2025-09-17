import pytest
from datetime import datetime, timedelta
from server import app


@pytest.fixture
def client():
    """Crée un client de test Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_data_future(mocker):
    """
    Mocke les données de clubs et compétitions avec une compétition future.
    """
    club = {"name": "Iron Temple", "email": "iron@club.com", "points": "20"}
    competition = {
        "name": "Spring Festival",
        "numberOfPlaces": "15",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Patch les variables globales du serveur
    mocker.patch("server.clubs", [club])
    mocker.patch("server.competitions", [competition])

    return club, competition


def test_booking_more_than_12_places(client, sample_data_future):
    """
    Vérifie qu'un club ne peut pas réserver plus de 12 places via /purchasePlaces.
    """
    club, competition = sample_data_future
    initial_places = int(competition["numberOfPlaces"])
    initial_points = int(club["points"])

    # Appel direct de la route Flask
    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": competition["name"], "places": 13},
        follow_redirects=True,
    )

    # Vérifie que le message flash est bien présent
    assert b"Cannot book more than 12 places per competition." in response.data

    # Vérifie que les données n'ont pas changé
    assert int(competition["numberOfPlaces"]) == initial_places
    assert int(club["points"]) == initial_points
