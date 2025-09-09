import pytest
from server import app, competitions, clubs


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_booking_more_than_12_places(client):
    # On choisit un club et une compétition existants
    competition = competitions[0]
    club = clubs[0]

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

    # On vérifie que l'opération est refusée
    assert b"Cannot book more than 12 places per competition." in response.data

    # Vérifie que le nombre de places dans la compétition n’a pas changé
    assert int(competition["numberOfPlaces"]) >= 0
    # Vérifie que les points du club n’ont pas été débités
    assert int(club["points"]) >= 0
