import pytest
from datetime import datetime, timedelta
from server import app


@pytest.fixture
def client():
    """
    Fixture qui fournit un client Flask pour les tests.

    Configure l'application en mode TESTING afin que :
        - Les sessions et flash messages fonctionnent sans side effects.
        - Les fichiers JSON ne soient pas modifiés.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_data(mocker):
    """
    Mock des variables globales `clubs` et `competitions` pour les tests.

    Crée un club et une compétition valides avec une date future,
    puis patch les variables globales du module `server` avec ces objets.

    Returns:
        tuple: (club, competition) à utiliser dans les tests.
    """
    club = {"name": "Iron Temple", "points": "5", "email": "iron@club.com"}
    competition = {
        "name": "Spring Festival",
        "numberOfPlaces": "10",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Patch des variables globales pour éviter les modifications réelles des fichiers JSON
    mocker.patch("server.clubs", [club])
    mocker.patch("server.competitions", [competition])
    return club, competition


def test_cannot_redeem_more_points_than_available(client, sample_data):
    """
    Test d'intégration Flask :

    Vérifie qu'un club ne peut pas réserver plus de places que ses points disponibles.

    Étapes :
        1. Récupère les données mockées du club et de la compétition.
        2. Tente de réserver 10 places alors que le club n'a que 5 points.
        3. Vérifie que le message d'erreur flash est affiché.
        4. Vérifie que les points du club et les places de la compétition n'ont pas été modifiés.
    """
    club, competition = sample_data
    initial_places = int(competition["numberOfPlaces"])
    initial_points = int(club["points"])

    # Le club tente de réserver plus de places que ses points
    response = client.post(
        "/purchasePlaces",
        data={
            "club": club["name"],
            "competition": competition["name"],
            "places": 10,  # > points disponibles
        },
        follow_redirects=True,  # Suivi automatique des redirections pour capturer le flash message
    )

    # Vérifie que le flash message correspondant apparaît
    assert b"You do not have enough points to book these places." in response.data

    # Vérifie que les données du club et de la compétition n'ont pas été modifiées
    assert int(competition["numberOfPlaces"]) == initial_places
    assert int(club["points"]) == initial_points
