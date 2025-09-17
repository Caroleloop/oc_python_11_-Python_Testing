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
def sample_data_past(mocker):
    """
    Mocke les données globales pour créer un club et une compétition passée.
    """
    club = {"name": "Iron Temple", "points": "10", "email": "iron@club.com"}
    competition = {
        "name": "Spring Festival",
        "numberOfPlaces": "5",
        # Compétition passée
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
    }

    mocker.patch("server.clubs", [club])
    mocker.patch("server.competitions", [competition])
    return club, competition


def test_booking_past_competition_blocked(client, sample_data_past):
    """
    Test d'intégration Flask :
    Vérifie qu'une réservation pour une compétition passée est bloquée.
    """
    club, competition = sample_data_past

    response = client.post(
        "/purchasePlaces",
        data={
            "club": club["name"],
            "competition": competition["name"],
            "places": 1,
        },
        follow_redirects=True,
    )

    # Vérifie que le message flash est dans la réponse
    assert b"You cannot book a place on a past competition." in response.data

    # Vérifie que les données du club et de la compétition n'ont pas été modifiées
    assert competition["numberOfPlaces"] == "5"
    assert club["points"] == "10"
