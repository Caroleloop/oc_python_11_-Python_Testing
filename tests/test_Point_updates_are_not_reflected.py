import pytest
from datetime import datetime
from server import app, clubs, competitions


@pytest.fixture
def client():
    """
    Crée un client de test Flask configuré en mode TESTING.

    Cette fixture permet de simuler des requêtes HTTP sur l'application Flask
    sans la lancer réellement, en utilisant `app.test_client()`.

    Yields:
        client (FlaskClient): client permettant d'envoyer des requêtes à l'application.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_purchase_places_deducts_points_with_fixture_data(client):
    """
    Teste le processus d'achat d'une place dans une compétition.

    Scénario testé :
        1. Sélectionner un club et une compétition FUTURE avec des places disponibles.
        2. Envoyer une requête POST à la route `/purchasePlaces` pour réserver 1 place.
        3. Vérifier que :
            - la réponse est valide (code HTTP 200).
            - un message de confirmation est présent dans la réponse.
            - les points du club sont décrémentés de 1.
            - le nombre de places disponibles dans la compétition est décrémenté de 1.

    Préconditions :
        - Le fichier `clubs.json` contient au moins un club avec des points disponibles.
        - Le fichier `competitions.json` contient au moins une compétition future avec
          au moins une place disponible.
    """
    # --- Given ---
    club = clubs[0]  # Sélection du premier club disponible
    competition = None

    # Recherche d'une compétition future (date > maintenant) avec au moins 1 place
    for comp in competitions:
        comp_date = datetime.strptime(comp["date"], "%Y-%m-%d %H:%M:%S")
        if comp_date > datetime.now() and int(comp["numberOfPlaces"]) > 0:
            competition = comp
            break

    # Vérifie qu'une compétition valide a bien été trouvée
    assert competition is not None, "Pas de compétition future valide trouvée dans competitions.json"

    # Sauvegarde des valeurs initiales pour comparaison après l'achat
    initial_points = int(club["points"])
    initial_places = int(competition["numberOfPlaces"])

    # --- When ---
    # Envoi d'une requête POST pour acheter 1 place
    response = client.post(
        "/purchasePlaces",
        data={"competition": competition["name"], "club": club["name"], "places": 1},
        follow_redirects=True,
    )

    # --- Then ---
    # Vérification du statut de la réponse
    assert response.status_code == 200
    # Vérifie que le message de confirmation est bien présent
    assert b"Great-booking complete!" in response.data

    # --- Expected ---
    # Vérifie que les points du club ont diminué de 1
    assert int(club["points"]) == initial_points - 1
    # Vérifie que le nombre de places de la compétition a diminué de 1
    assert int(competition["numberOfPlaces"]) == initial_places - 1
