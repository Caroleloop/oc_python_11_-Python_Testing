import pytest
from datetime import datetime
from server import app, clubs, competitions


@pytest.fixture
def client():
    """
    Fixture Pytest qui fournit un client de test Flask.

    Cette fixture configure l'application Flask en mode TESTING,
    ce qui permet de faire des requêtes HTTP simulées sans démarrer
    le serveur réel.

    Yields:
        - client Flask prêt à être utilisé pour envoyer des requêtes de test.
    """
    app.config["TESTING"] = True
    # Création d'un client de test qui sera utilisé dans les tests
    with app.test_client() as client:
        yield client


def test_cannot_redeem_more_points_than_available(client):
    """
    Teste que le club ne peut pas réserver plus de places que ses points disponibles.

    Arrange:
        - Modifie directement les données du premier club et de la première compétition
          pour définir un scénario de test connu.
          - Club : 5 points disponibles
          - Compétition : 10 places disponibles

    Act:
        - Le club tente de réserver 10 places via un POST sur la route /purchasePlaces.

    Assert:
        - Vérifie que le message d'erreur attendu apparaît dans la réponse :
          "You do not have enough points to book these places."
        - Vérifie que le message de succès n'apparaît pas :
          "Great-booking complete!"

    Args:
        client: Le client de test Flask fourni par la fixture `client`.
    """
    # Arrange : préparation des données pour le test
    clubs[0]["points"] = 5
    competitions[0]["numberOfPlaces"] = 10
    for comp in competitions:
        comp_date = datetime.strptime(comp["date"], "%Y-%m-%d %H:%M:%S")
        if comp_date > datetime.now() and int(comp["numberOfPlaces"]) > 0:
            competition = comp
            break

    club = clubs[0]

    # Act : envoi d'une requête POST simulant la réservation de 10 places
    response = client.post(
        "/purchasePlaces",
        data={"competition": competition["name"], "club": club["name"], "places": 10},
        follow_redirects=True,
    )

    # Assert : vérifie que le message d'erreur est présent
    assert b"You do not have enough points to book these places." in response.data
    # Assert : vérifie que le message de succès n'est pas présent
    assert b"Great-booking complete!" not in response.data
