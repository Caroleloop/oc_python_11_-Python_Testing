import pytest
from bs4 import BeautifulSoup
from server import app


@pytest.fixture
def client():
    """Fixture qui fournit un client de test Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_clubs(mocker):
    """
    Remplace la variable globale `clubs` de server.py par des données simulées.
    """
    clubs_mock = [
        {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "15"},
        {"name": "Power Gym", "email": "power@gym.com", "points": "20"},
    ]
    mocker.patch("server.clubs", clubs_mock)
    return clubs_mock


def test_email_found_flask(client, sample_clubs):
    """
    Test d'intégration Flask : un email existant retourne le bon club.
    """
    response = client.post(
        "/showSummary",
        data={"email": "admin@irontemple.com"},
        follow_redirects=True,
    )

    # Parse le HTML avec BeautifulSoup pour éviter les problèmes d'encodage/commentaires
    soup = BeautifulSoup(response.data, "html.parser")
    page_text = soup.get_text()

    # Vérifie que la page de résumé contient le nom du club
    assert "admin@irontemple.com" in page_text
    # Vérifie que le flash message "email non trouvé" n'est pas présent
    assert "Sorry, that email wasn't found." not in page_text


def test_email_not_found_flask(client, sample_clubs):
    """
    Test d'intégration Flask : un email inexistant déclenche le flash message.
    """
    response = client.post(
        "/showSummary",
        data={"email": "inconnu@example.com"},
        follow_redirects=True,
    )

    # Parse le HTML avec BeautifulSoup pour vérifier le flash message
    soup = BeautifulSoup(response.data, "html.parser")
    page_text = soup.get_text()

    # Vérifie que le flash message est présent
    assert "Sorry, that email wasn't found." in page_text
