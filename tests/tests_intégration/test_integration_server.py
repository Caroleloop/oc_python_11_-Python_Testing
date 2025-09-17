import pytest
from bs4 import BeautifulSoup
from datetime import datetime
from server import app, clubs, competitions


@pytest.fixture
def client():
    """
    Fixture Pytest pour créer un client de test Flask.

    Configure l'application en mode TESTING, ce qui permet de simuler
    des requêtes HTTP sans lancer le serveur.

    Yields:
        client Flask configuré pour les tests.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def get_flash_messages(response):
    """
    Extrait les messages flash depuis la réponse HTML d'une requête.

    Args:
        response: réponse Flask après un POST ou GET.

    Returns:
        list[str]: liste des messages flash présents dans la page.
    """
    # Parse le HTML de la réponse avec BeautifulSoup
    soup = BeautifulSoup(response.data, "html.parser")
    # Retourne tous les textes des éléments <li> (messages flash)
    return [li.get_text(strip=True) for li in soup.find_all("li")]


def test_showSummary_invalid_email(client):
    """
    Teste la route /showSummary avec un email invalide.

    Vérifie que le message d'erreur approprié est affiché lorsque
    l'email n'existe pas dans la liste des clubs.
    """
    response = client.post("/showSummary", data={"email": "wrong@email.com"}, follow_redirects=True)
    flashes = get_flash_messages(response)
    assert "Sorry, that email wasn't found." in flashes


def test_showSummary_valid_email(client):
    """
    Teste la route /showSummary avec un email valide.

    Vérifie que :
        - Aucun message d'erreur n'apparaît.
        - La réponse HTTP est 200 (OK).
    """
    valid_email = clubs[0]["email"]
    response = client.post("/showSummary", data={"email": valid_email}, follow_redirects=True)
    flashes = get_flash_messages(response)
    # Vérifie qu'il n'y a pas de message d'erreur
    assert "Sorry, that email wasn't found." not in flashes
    # Vérifie que la réponse est bien OK
    assert response.status_code == 200


def get_future_competition():
    """
    Retourne la première compétition dont la date est dans le futur.

    Parcourt la liste `competitions` et compare la date de chaque
    compétition à la date actuelle.

    Returns:
        dict: dictionnaire représentant la compétition future.

    Raises:
        ValueError: si aucune compétition future n'est trouvée.
    """
    for comp in competitions:
        comp_date = datetime.strptime(comp["date"], "%Y-%m-%d %H:%M:%S")
        if comp_date > datetime.now():
            return comp
    raise ValueError("No future competition found!")


def test_purchasePlaces_success(client):
    """
    Teste l'achat de places avec succès pour une compétition future.

    Vérifie que :
        - Le message de succès est affiché.
        - Les points du club sont correctement décrémentés.
        - Le nombre de places disponibles dans la compétition est décrémenté.
    """
    club = clubs[0]
    competition = get_future_competition()  # compétition future
    initial_points = int(club["points"])
    initial_places = int(competition["numberOfPlaces"])

    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": competition["name"], "places": 1},
        follow_redirects=True,
    )

    flashes = get_flash_messages(response)
    # Vérifie le message de succès
    assert "Great-booking complete!" in flashes
    # Vérifie la décrémentation des points et des places
    assert int(club["points"]) == initial_points - 1
    assert int(competition["numberOfPlaces"]) == initial_places - 1


def test_purchasePlaces_overbooking(client):
    """
    Teste l'achat de places supérieur au nombre disponible.

    Vérifie que le message d'erreur approprié est affiché lorsque
    le club essaie de réserver plus de places qu'il n'en reste.
    """
    club = clubs[0]
    competition = get_future_competition()  # compétition future

    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": competition["name"], "places": 100},
        follow_redirects=True,
    )

    flashes = get_flash_messages(response)
    # Vérifie le message d'erreur d'overbooking
    assert "Not enough places left in this competition." in flashes
