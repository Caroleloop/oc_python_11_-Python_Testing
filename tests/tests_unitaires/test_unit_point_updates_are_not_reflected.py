import pytest
from datetime import datetime, timedelta
from server import app


@pytest.fixture
def client():
    """Fixture qui fournit un client Flask pour les tests."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_data(mocker):
    """
    Mocke les données globales de server.py avec un club et une compétition future.
    """
    club = {"name": "Iron Temple", "points": "5", "email": "iron@club.com"}
    competition = {
        "name": "Spring Festival",
        "numberOfPlaces": "10",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
    }

    mocker.patch("server.clubs", [club])
    mocker.patch("server.competitions", [competition])
    return club, competition


def test_purchase_places_deducts_points_integration(client, sample_data):
    """
    Test d'intégration Flask : vérifie qu'une réservation valide décrémente
    les points du club et les places de la compétition.
    """
    club, competition = sample_data
    initial_points = int(club["points"])
    initial_places = int(competition["numberOfPlaces"])

    # On simule une réservation de 1 place
    response = client.post(
        "/purchasePlaces",
        data={
            "club": club["name"],
            "competition": competition["name"],
            "places": 1,
        },
        follow_redirects=True,
    )

    # Vérifie que le message de succès apparaît
    assert b"Great-booking complete!" in response.data

    # Vérifie que les données sont mises à jour
    assert int(club["points"]) == initial_points - 1
    assert int(competition["numberOfPlaces"]) == initial_places - 1
