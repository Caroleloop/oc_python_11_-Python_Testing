import pytest
from datetime import datetime, timedelta
from server import app


@pytest.fixture
def client():
    """
    Fixture qui fournit un client Flask configuré pour les tests.

    - active le mode TESTING pour éviter les effets de bord (sessions, flash, fichiers JSON)
    - yield un client de test utilisable pour envoyer des requêtes HTTP simulées
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_data_past(mocker):
    """
    Mocke les données globales `clubs` et `competitions` pour créer une compétition passée.

    Crée :
        - un club avec 10 points
        - une compétition dont la date est passée

    Patch les variables globales pour éviter de modifier les fichiers JSON réels.

    Returns:
        tuple: (club, competition) pour les tests
    """
    club = {"name": "Iron Temple", "points": "10", "email": "iron@club.com"}
    competition = {
        "name": "Spring Festival",
        "numberOfPlaces": "5",
        # Date dans le passé pour tester le blocage
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Remplace les listes globales par nos mocks
    mocker.patch("server.clubs", [club])
    mocker.patch("server.competitions", [competition])
    return club, competition


def test_booking_past_competition_blocked(client, sample_data_past):
    """
    Test d'intégration Flask :

    Vérifie qu'une réservation pour une compétition passée est correctement bloquée.

    Étapes :
        1. Récupère le club et la compétition passée mockés.
        2. Tente de réserver 1 place via POST sur '/purchasePlaces'.
        3. Vérifie que le flash message d'erreur approprié est présent.
        4. Vérifie que les points du club et les places de la compétition restent inchangés.
    """
    club, competition = sample_data_past

    # Tentative de réservation
    response = client.post(
        "/purchasePlaces",
        data={
            "club": club["name"],
            "competition": competition["name"],
            "places": 1,
        },
        follow_redirects=True,  # Suivre les redirections pour récupérer le flash message
    )

    # Vérifie la présence du message d'erreur
    assert b"You cannot book a place on a past competition." in response.data

    # Vérifie que les données du club et de la compétition n'ont pas été modifiées
    assert competition["numberOfPlaces"] == "5"
    assert club["points"] == "10"
