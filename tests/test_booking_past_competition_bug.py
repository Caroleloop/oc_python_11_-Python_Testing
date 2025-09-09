import pytest
from server import app, competitions, clubs
from datetime import datetime


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def get_past_competition():
    """Retourne la première compétition dont la date est passée."""
    now = datetime.now()
    for comp in competitions:
        comp_date = datetime.strptime(comp["date"], "%Y-%m-%d %H:%M:%S")
        if comp_date < now:
            return comp
    pytest.skip("Pas de compétition passée trouvée dans competitions.json")


def get_any_club():
    """Retourne un club valide depuis clubs.json."""
    return clubs[0]


def test_booking_past_competition_blocked(client):
    """
    Given a past competition (from competitions.json)
    When a secretary tries to book a place
    Then the system should reject it
    """
    past_competition = get_past_competition()
    club = get_any_club()

    response = client.post(
        "/purchasePlaces",
        data={"competition": past_competition["name"], "club": club["name"], "places": "1"},
        follow_redirects=True,
    )

    html = response.data.decode()

    # -------- ATTENDU MÉTIER --------
    # Le système doit bloquer la réservation pour une compétition passée
    assert "You cannot book a place on a past competition." in html
    assert "Great-booking complete!" not in html
