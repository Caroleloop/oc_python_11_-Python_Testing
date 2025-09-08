import pytest
from server import app, clubs, competitions


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_cannot_redeem_more_points_than_available(client):
    # Arrange : on modifie directement le club et la compétition dans les globals
    clubs[0]["points"] = "5"
    competitions[0]["numberOfPlaces"] = "10"

    club = clubs[0]
    competition = competitions[0]

    # Act : le club essaie de réserver 10 places (donc plus que ses points)
    response = client.post(
        "/purchasePlaces",
        data={"competition": competition["name"], "club": club["name"], "places": 10},
        follow_redirects=True,
    )

    # Assert : le message d'erreur attendu apparaît
    assert b"You do not have enough points to book these places." in response.data
    # et surtout, pas de succès
    assert b"Great-booking complete!" not in response.data
