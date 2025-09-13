import pytest
from datetime import datetime
from server import app, clubs, competitions


@pytest.fixture
def client():
    """
    Crée et configure un client Flask de test en mode TESTING.

    Cette fixture permet de simuler des requêtes HTTP
    (GET, POST, etc.) vers l'application Flask sans
    avoir besoin de lancer le serveur.

    Yields:
        client (FlaskClient): une instance du client de test Flask.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_cannot_book_more_places_than_available(client):
    """
    Vérifie qu'un club ne peut pas réserver plus de places que disponibles
    dans une compétition FUTURE.

    Scénario de test :
        1. Recherche une compétition FUTURE avec au moins une place disponible.
        2. Sélectionne un club (le premier de la liste).
        3. Tente de réserver un nombre de places supérieur à la capacité de la compétition.
        4. Vérifie que :
            - Un message d'erreur s'affiche dans la réponse.
            - Les données (places de la compétition et points du club) ne sont pas modifiées.

    Préconditions :
        - Le fichier `competitions.json` doit contenir au moins une compétition future
          avec des places disponibles.
    """
    # --- Given ---
    # Recherche d'une compétition FUTURE avec au moins 1 place disponible
    competition = None
    now = datetime.now()
    for comp in competitions:
        comp_date = datetime.strptime(comp["date"], "%Y-%m-%d %H:%M:%S")
        if comp_date > now and int(comp["numberOfPlaces"]) > 0:
            competition = comp
            break

    # Vérifie qu'une compétition valide a été trouvée
    assert competition is not None, "Pas de compétition future valide trouvée dans competitions.json"

    # Sélection du premier club disponible
    club = clubs[0]

    # Sauvegarde de l'état initial pour comparaison après la requête
    initial_places = int(competition["numberOfPlaces"])
    initial_points = int(club["points"])

    # --- When ---
    # Tentative de réservation supérieure aux places disponibles
    too_many = initial_places + 5
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": competition["name"],
            "club": club["name"],
            "places": str(too_many),
        },
        follow_redirects=True,
    )
    html = response.data.decode()

    # --- Then ---
    # Vérifie que le message d'erreur attendu est affiché
    assert "Not enough places left in this competition." in html

    # Vérifie que les données n'ont pas changé
    assert int(competition["numberOfPlaces"]) == initial_places
    assert int(club["points"]) == initial_points
