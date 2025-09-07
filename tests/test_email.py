import pytest
from server import app
import html


@pytest.fixture
def client():
    """
    Fixture Flask test client.

    Configure l'application Flask en mode TESTING et fournit un client de test
    pour simuler des requêtes HTTP dans les tests.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_email_not_found(client):
    """
    Teste le comportement de l'application lorsqu'un email non existant est soumis.

    Envoie un email qui n'est pas présent dans clubs.json via la route /showSummary.
    Vérifie que :
        1. La page renvoyée contient le titre de l'index.
        2. Le message flash d'erreur "Sorry, that email wasn't found." est affiché.
    """
    response = client.post("/showSummary", data={"email": "inconnu@example.com"}, follow_redirects=True)

    # Décoder le HTML en texte brut pour gérer les entités HTML
    response_text = html.unescape(response.data.decode())

    # Vérifie que le titre de l'index est présent
    assert "Welcome to the GUDLFT Registration Portal" in response_text

    # Vérifie que le message flash est présent
    assert "Sorry, that email wasn't found." in response_text


def test_email_found(client):
    """
    Teste le comportement de l'application lorsqu'un email existant est soumis.

    Envoie un email valide présent dans clubs.json via la route /showSummary.
    Vérifie que :
        1. Le résumé du club est affiché (texte "Welcome" dans welcome.html).
        2. Aucun message d'erreur n'est présent.
    """
    valid_email = "admin@irontemple.com"  # mettre un email réel de clubs.json
    response = client.post("/showSummary", data={"email": valid_email}, follow_redirects=True)

    # Décoder le HTML en texte brut
    response_text = html.unescape(response.data.decode())

    # Vérifie que le résumé est affiché
    assert "Welcome" in response_text

    # Vérifie qu'aucun message d'erreur n'est présent
    assert "Sorry, that email wasn't found." not in response_text
