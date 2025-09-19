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
def sample_data_future(mocker):
    """
    Mocke les données globales `clubs` et `competitions` de server.py pour créer une compétition future.

    Crée :
        - un club avec 10 points
        - une compétition future avec 15 places

    Patch les variables globales pour que les tests n'affectent pas les fichiers JSON.

    Returns:
        tuple: (club, competition) pour les tests
    """
    club = {"name": "Iron Temple", "points": "10", "email": "iron@club.com"}
    competition = {
        "name": "Spring Festival",
        "numberOfPlaces": "15",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Remplace les listes globales par nos mocks
    mocker.patch("server.clubs", [club])
    mocker.patch("server.competitions", [competition])
    return club, competition


def test_cannot_book_more_places_than_available(client, sample_data_future):
    """
    Test d'intégration Flask :

    Vérifie qu'un club ne peut pas réserver plus de places qu'il n'en reste dans la compétition.

    Étapes :
        1. Récupère le club et la compétition mockés.
        2. Tente de réserver un nombre de places supérieur au nombre disponible.
        3. Vérifie que le flash message d'erreur est présent.
        4. Vérifie que les points du club et le nombre de places restent inchangés.
    """
    club, competition = sample_data_future
    initial_places = int(competition["numberOfPlaces"])
    initial_points = int(club["points"])

    # Tentative de réservation excessive
    response = client.post(
        "/purchasePlaces",
        data={
            "club": club["name"],
            "competition": competition["name"],
            "places": initial_places + 5,  # demande supérieure au nombre de places disponibles
        },
        follow_redirects=True,  # Suivre les redirections pour capturer le flash message
    )

    # Vérifie la présence du message d'erreur
    assert b"Not enough places left in this competition." in response.data

    # Vérifie que les données du club et de la compétition n'ont pas été modifiées
    assert int(competition["numberOfPlaces"]) == initial_places
    assert int(club["points"]) == initial_points
