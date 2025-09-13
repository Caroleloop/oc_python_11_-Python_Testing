import pytest
from server import clubs


@pytest.fixture
def sample_clubs():
    """
    Fixture Pytest qui fournit une liste simulée de clubs.

    Cette fixture remplace l'accès direct à `clubs.json` en renvoyant
    la liste `clubs` importée depuis `server.py`. Elle est utilisée
    pour les tests unitaires afin de garantir des données constantes.

    Returns:
        list: Liste de dictionnaires représentant des clubs.
    """
    return clubs


def find_club_by_email(email, clubs):
    """
    Cherche un club par son email dans une liste de clubs.

    Cette fonction reproduit la logique de recherche utilisée dans
    `showSummary` pour isoler et tester le comportement indépendamment
    de Flask.

    Args:
        email (str): L'email du club à rechercher.
        clubs (list): Liste de dictionnaires représentant les clubs.

    Returns:
        dict or None: Le dictionnaire du club si trouvé, sinon None.
    """
    # Crée une liste de tous les clubs dont l'email correspond
    matching_clubs = [club for club in clubs if club["email"] == email]

    # Retourne le premier club trouvé ou None si aucun club ne correspond
    return matching_clubs[0] if matching_clubs else None


def test_email_found_unit(sample_clubs):
    """
    Test unitaire : vérifie qu'un email existant retourne le club correspondant.

    Ce test utilise la fixture `sample_clubs` pour récupérer les clubs
    et s'assure que `find_club_by_email` retourne bien un club existant.

    Assertions:
        - Le club n'est pas None.
        - L'email du club correspond à l'email recherché.
    """
    club = find_club_by_email("admin@irontemple.com", sample_clubs)
    assert club is not None
    assert club["email"] == "admin@irontemple.com"


def test_email_not_found_unit(sample_clubs):
    """
    Test unitaire : vérifie qu'un email inexistant retourne None.

    Ce test utilise la fixture `sample_clubs` et s'assure que
    `find_club_by_email` renvoie None lorsque l'email n'existe pas.

    Assertions:
        - Le résultat est None.
    """
    club = find_club_by_email("inconnu@example.com", sample_clubs)
    assert club is None
