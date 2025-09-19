from locust import HttpUser, TaskSet, task, between

# Email et nom d'un club existant dans clubs.json
CLUB_EMAIL = "john@simplylift.co"
CLUB_NAME = "Simply Lift"
COMPETITION_NAME = "Spring Festival"


class SecretaryScenario(TaskSet):
    """
    Scénario de test pour un secrétaire de club utilisant Locust.

    Ce scénario simule le parcours suivant :
    1. Connexion avec l'email du secrétaire
    2. Sélection d'une compétition
    3. Achat de places
    4. Consultation des points du club
    """

    @task
    def secretary_journey(self):
        """Simule le parcours complet du secrétaire sur le site."""

        # 1. Connexion avec l'email du secrétaire
        with self.client.post("/showSummary", {"email": CLUB_EMAIL}, catch_response=True) as response:
            if response.elapsed.total_seconds() > 5:
                response.failure("Connexion took too long (>5s)")
            elif response.status_code != 200:
                response.failure(f"Unexpected status {response.status_code}")
            else:
                response.success()

        # 2. Sélection de la compétition
        with self.client.get(f"/book/{COMPETITION_NAME}/{CLUB_NAME}", catch_response=True) as response:
            if response.elapsed.total_seconds() > 5:
                response.failure("Loading competition took too long (>5s)")
            elif response.status_code != 200:
                response.failure(f"Unexpected status {response.status_code}")
            else:
                response.success()

        # 3. Achat de places
        # Ici, on simule l'achat de 2 places pour la compétition sélectionnée
        with self.client.post(
            "/purchasePlaces", {"club": CLUB_NAME, "competition": COMPETITION_NAME, "places": "2"}, catch_response=True
        ) as response:
            if response.elapsed.total_seconds() > 2:
                response.failure("Purchase took too long (>2s)")
            elif response.status_code != 200:
                response.failure(f"Unexpected status {response.status_code}")
            else:
                response.success()

        # 4. Consultation des points (page publique)
        with self.client.get("/points", catch_response=True) as response:
            if response.elapsed.total_seconds() > 5:
                response.failure("Points page took too long (>5s)")
            elif response.status_code != 200:
                response.failure(f"Unexpected status {response.status_code}")
            else:
                response.success()


class WebsiteUser(HttpUser):
    """
    Classe représentant un utilisateur simulé du site web.

    Elle exécute les tâches définies dans SecretaryScenario avec des pauses
    aléatoires entre les actions pour simuler un comportement humain.
    """

    tasks = [SecretaryScenario]
    wait_time = between(1, 5)  # Pause aléatoire entre 1 et 5 secondes entre les scénarios
