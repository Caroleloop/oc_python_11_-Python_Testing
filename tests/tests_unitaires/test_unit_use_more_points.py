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
    Mock des variables globales `clubs` et `competitions` avec des données futures
    pour les tests d'intégration Flask.
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


def test_cannot_redeem_more_points_than_available(client, sample_data):
    """
    Test d'intégration Flask pour vérifier qu'un club ne peut pas réserver plus de places
    que ses points disponibles.
    """
    club, competition = sample_data
    initial_places = int(competition["numberOfPlaces"])
    initial_points = int(club["points"])

    # Le club tente de réserver plus de places que ses points (5 points, demande 10)
    response = client.post(
        "/purchasePlaces",
        data={
            "club": club["name"],
            "competition": competition["name"],
            "places": 10,
        },
        follow_redirects=True,
    )

    # Vérifie que le flash message correspondant apparaît
    assert b"You do not have enough points to book these places." in response.data

    # Vérifie que les données n'ont pas été modifiées
    assert int(competition["numberOfPlaces"]) == initial_places
    assert int(club["points"]) == initial_points
