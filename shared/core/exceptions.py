class DatabaseException(Exception):
    def __init__(self, operation:str, detail:str):
        self.operation = operation
        self.detail = detail
        self.message = f"Database error occured in: {self.operation}"
        super().__init__(self.message)
        

class InputError(Exception):
    def __init__(self, operation, detail):
        self.operation = operation
        self.detail = detail
        self.message = f"Input validation error occured in: {self.operation}"
        super().__init__(self.message)


class NotFoundException(Exception):
    def __init__(self, ressource:str):
        self.ressource = ressource
        self.message = f"{ressource} not found"
        super().__init__(self.message)


# Client-Exceptions (API und Worker nutzen sie)
class StorageException(Exception):
    def __init__(self, operation: str):
        self.operation = operation
        self.message = f"Storage error in: {self.operation}"
        super().__init__(self.message)


class QdrantException(Exception):
    def __init__(self, operation: str, detail: str):
        self.operation = operation
        self.detail = detail
        self.message = f"Qdrant error in {self.operation}: {detail}"
        super().__init__(self.message)


class OllamaException(Exception):
    def __init__(self, operation: str, detail: str = ""):
        self.operation = operation
        self.detail = detail
        self.message = f"Ollama error in {self.operation}: {detail}"
        super().__init__(self.message)