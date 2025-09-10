import pytest
from server import app
import html


@pytest.fixture
def client():
    """
    Fixture pour fournir un client de test Flask.

    Cette fixture configure l'application Flask en mode TESTING, ce qui permet :
        - De simuler des requêtes HTTP sans lancer le serveur.
        - D'accéder aux réponses et aux données de l'application pour les assertions.

    Yields:
        client: instance de Flask test client pour les tests.
    """
    app.config["TESTING"] = True  # Active le mode test pour l'application Flask
    with app.test_client() as client:
        # Fournit le client pour l'utilisation dans les tests
        yield client


def test_email_not_found(client):
    """
    Test du comportement lorsque l'email soumis n'existe pas.

    Ce test simule l'envoi d'un email non présent dans `clubs.json` via la route /showSummary.
    Il vérifie :
        1. Que la page renvoyée contient le titre de l'index.
        2. Que le message flash "Sorry, that email wasn't found." est affiché.

    Args:
        client: fixture pytest, client de test Flask.
    """
    # Envoie d'une requête POST avec un email inconnu
    response = client.post("/showSummary", data={"email": "inconnu@example.com"}, follow_redirects=True)

    # Décodage du HTML en texte brut pour gérer les entités HTML
    response_text = html.unescape(response.data.decode())

    # Vérifie que le titre de l'index est présent dans la réponse
    assert "Welcome to the GUDLFT Registration Portal" in response_text

    # Vérifie que le message flash d'erreur est présent
    assert "Sorry, that email wasn't found." in response_text


def test_email_found(client):
    """
    Test du comportement lorsque l'email soumis existe.

    Ce test simule l'envoi d'un email valide présent dans `clubs.json` via la route /showSummary.
    Il vérifie :
        1. Que le résumé du club est affiché (texte "Welcome" dans welcome.html).
        2. Qu'aucun message d'erreur n'est présent.

    Args:
        client: fixture pytest, client de test Flask.
    """
    valid_email = "admin@irontemple.com"  # Email réel présent dans clubs.json

    # Envoie d'une requête POST avec un email valide
    response = client.post("/showSummary", data={"email": valid_email}, follow_redirects=True)

    # Décodage du HTML en texte brut
    response_text = html.unescape(response.data.decode())

    # Vérifie que la page affiche le résumé du club
    assert "Welcome" in response_text

    # Vérifie qu'aucun message d'erreur n'est présent
    assert "Sorry, that email wasn't found." not in response_text
