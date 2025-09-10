import pytest
from server import app, competitions, clubs
from datetime import datetime


@pytest.fixture
def client():
    """
    Crée un client de test Flask pour exécuter les requêtes HTTP
    dans un environnement de test.

    Configuration :
        - Active le mode TESTING pour Flask.
        - Utilise un client de test contextuel afin d'exécuter les appels
          aux routes sans démarrer le serveur.

    Yields:
        client (FlaskClient) : instance du client de test.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def get_past_competition():
    """
    Retourne la première compétition dont la date est passée.

    Parcourt la liste `competitions` et compare la date de chaque compétition
    avec la date actuelle (`datetime.now()`).

    Comportement :
        - Si une compétition passée est trouvée, elle est retournée.
        - Si aucune compétition passée n’est trouvée :
            - Le test est ignoré via `pytest.skip`.

    Returns:
        dict : données de la première compétition passée trouvée.

    Raises:
        pytest.skip : si aucune compétition passée n’est disponible.
    """
    now = datetime.now()
    for comp in competitions:
        comp_date = datetime.strptime(comp["date"], "%Y-%m-%d %H:%M:%S")
        if comp_date < now:
            return comp
    pytest.skip("Pas de compétition passée trouvée dans competitions.json")


def get_any_club():
    """
    Retourne un club valide depuis le fichier clubs.json.

    Actuellement, la fonction renvoie le premier club de la liste.

    Returns:
        dict : données d’un club valide.
    """
    return clubs[0]


def test_booking_past_competition_blocked(client):
    """
    Vérifie que la réservation est impossible pour une compétition passée.

    Scénario testé :
        Given : Une compétition dont la date est passée.
        When : Un secrétaire tente de réserver une place via la route "/purchasePlaces".
        Then : Le système doit bloquer la réservation et afficher un message
               d'erreur explicite.

    Étapes :
        1. Récupère une compétition passée avec `get_past_competition()`.
        2. Récupère un club valide avec `get_any_club()`.
        3. Envoie une requête POST au serveur avec 1 place réservée.
        4. Vérifie dans la réponse HTML que :
            - Le message d'erreur "You cannot book a place on a past competition." est affiché.
            - Le message de succès "Great-booking complete!" n’est pas affiché.

    Args:
        client (FlaskClient): client de test Flask.
    """
    past_competition = get_past_competition()
    club = get_any_club()

    # Envoi de la requête POST simulant la réservation d’une place
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
