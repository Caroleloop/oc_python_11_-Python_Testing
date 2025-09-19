import pytest
from bs4 import BeautifulSoup
from server import app


@pytest.fixture
def client():
    """
    Fixture qui fournit un client Flask pour les tests.

    - Configure Flask en mode TESTING pour éviter les effets de bord.
    - Permet d'envoyer des requêtes HTTP simulées vers l'application.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_clubs(mocker):
    """
    Mock des clubs pour les tests Flask.

    - Remplace la variable globale `clubs` dans server.py par des données simulées.
    - Permet de tester l'accès à la page de résumé et les flash messages.

    Returns:
        list: Liste des clubs simulés.
    """
    clubs_mock = [
        {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "15"},
        {"name": "Power Gym", "email": "power@gym.com", "points": "20"},
    ]
    mocker.patch("server.clubs", clubs_mock)
    return clubs_mock


def test_email_found_flask(client, sample_clubs):
    """
    Test d'intégration Flask : vérifie qu'un email existant retourne le club correct.

    Étapes :
        1. Envoie un POST sur '/showSummary' avec un email valide.
        2. Parse le HTML de la réponse avec BeautifulSoup.
        3. Vérifie que le nom du club est présent dans la page.
        4. Vérifie que le flash message "email non trouvé" n'apparaît pas.
    """
    response = client.post(
        "/showSummary",
        data={"email": "admin@irontemple.com"},
        follow_redirects=True,
    )

    # Parse le HTML pour récupérer le texte visible
    soup = BeautifulSoup(response.data, "html.parser")
    page_text = soup.get_text()

    # Vérifie que l'email du club est affiché
    assert "admin@irontemple.com" in page_text
    # Vérifie qu'aucun message d'erreur n'est présent
    assert "Sorry, that email wasn't found." not in page_text


def test_email_not_found_flask(client, sample_clubs):
    """
    Test d'intégration Flask : vérifie qu'un email inexistant déclenche un flash message.

    Étapes :
        1. Envoie un POST sur '/showSummary' avec un email invalide.
        2. Parse le HTML avec BeautifulSoup.
        3. Vérifie que le flash message "Sorry, that email wasn't found." est présent.
    """
    response = client.post(
        "/showSummary",
        data={"email": "inconnu@example.com"},
        follow_redirects=True,
    )

    # Parse le HTML pour récupérer le texte
    soup = BeautifulSoup(response.data, "html.parser")
    page_text = soup.get_text()

    # Vérifie que le flash message est affiché
    assert "Sorry, that email wasn't found." in page_text
