import pytest
from datetime import datetime, timedelta
from server import app


@pytest.fixture
def client():
    """Fixture qui fournit un client de test Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_data_future(mocker):
    """
    Remplace les données globales `clubs` et `competitions` de server.py
    par un club et une compétition future, grâce à mocker.
    """
    club = {"name": "Iron Temple", "points": "10", "email": "iron@club.com"}
    competition = {
        "name": "Spring Festival",
        "numberOfPlaces": "15",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
    }

    mocker.patch("server.clubs", [club])
    mocker.patch("server.competitions", [competition])
    return club, competition


def test_cannot_book_more_places_than_available(client, sample_data_future):
    """
    Test d'intégration Flask : un club ne peut pas réserver plus de places que disponibles.
    """
    club, competition = sample_data_future
    initial_places = int(competition["numberOfPlaces"])
    initial_points = int(club["points"])

    # Envoi d'une requête POST vers la route /purchasePlaces
    response = client.post(
        "/purchasePlaces",
        data={
            "club": club["name"],
            "competition": competition["name"],
            "places": initial_places + 5,  # demande trop élevée
        },
        follow_redirects=True,
    )

    # Vérifie que le message d'erreur est présent dans la réponse
    assert b"Not enough places left in this competition." in response.data

    # Vérifie que les données n'ont pas été modifiées
    assert int(competition["numberOfPlaces"]) == initial_places
    assert int(club["points"]) == initial_points
