from abc import ABC, abstractmethod


class TestManagementBackend(ABC):
    """Interface commune : FileBackend (référence) et XrayBackend (Jira + Xray Cloud)."""

    __test__ = False  # évite la collecte par pytest

    @abstractmethod
    def find_by_external_id(self, external_id: str) -> str | None:
        """Retourne la clé du test si elle existe déjà, sinon None."""

    @abstractmethod
    def create_test(self, case: dict) -> str:
        """Crée le test et retourne sa clé."""

    @abstractmethod
    def update_test(self, key: str, case: dict) -> None:
        """Met à jour un test existant."""

    @abstractmethod
    def import_results(self, results: list[dict]) -> str:
        """Importe les résultats d'exécution, retourne un identifiant d'exécution."""

    def ensure_requirement(
        self, req_id: str, title: str, text: str, known_key: str | None = None
    ) -> str | None:
        """Crée ou retrouve l'exigence (Story) et renvoie sa clé. Sans objet par défaut."""
        return None

    def link_to_requirement(self, test_key: str, requirement_key: str) -> None:
        """Relie un test à son exigence. Sans objet par défaut."""
        return
