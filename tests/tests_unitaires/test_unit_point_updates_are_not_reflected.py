import pytest
from datetime import datetime, timedelta
from server import app


@pytest.fixture
def client():
    """
    Fixture qui fournit un client Flask configuré pour les tests.

    - active le mode TESTING pour éviter les effets de bord (sessions, flash, fichiers JSON)
    - yield un client de test utilisable pour envoyer des requêtes
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_data(mocker):
    """
    Mocke les données globales `clubs` et `competitions` de server.py.

    Crée :
        - un club avec 5 points
        - une compétition future avec 10 places

    Patch les variables globales pour que les tests n'affectent pas les fichiers JSON.
    Returns:
        tuple: (club, competition)
    """
    club = {"name": "Iron Temple", "points": "5", "email": "iron@club.com"}
    competition = {
        "name": "Spring Festival",
        "numberOfPlaces": "10",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Remplace les listes originales par les mocks
    mocker.patch("server.clubs", [club])
    mocker.patch("server.competitions", [competition])
    return club, competition


def test_purchase_places_deducts_points_integration(client, sample_data):
    """
    Test d'intégration Flask : vérifie qu'une réservation valide :

        1. Décrémente les points du club.
        2. Décrémente le nombre de places de la compétition.
        3. Affiche le message de succès attendu.

    Étapes :
        - Récupère le club et la compétition mockés.
        - Effectue une réservation de 1 place via POST sur '/purchasePlaces'.
        - Vérifie que le flash message "Great-booking complete!" est présent.
        - Vérifie la mise à jour correcte des points et des places.
    """
    club, competition = sample_data
    initial_points = int(club["points"])
    initial_places = int(competition["numberOfPlaces"])

    # Réservation d'une place
    response = client.post(
        "/purchasePlaces",
        data={
            "club": club["name"],
            "competition": competition["name"],
            "places": 1,
        },
        follow_redirects=True,  # Suivre les redirections pour récupérer le flash message
    )

    # Vérifie le message de succès
    assert b"Great-booking complete!" in response.data

    # Vérifie que les points du club ont été décrémentés
    assert int(club["points"]) == initial_points - 1

    # Vérifie que le nombre de places de la compétition a été décrémenté
    assert int(competition["numberOfPlaces"]) == initial_places - 1
