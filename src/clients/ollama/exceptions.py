class OllamaException(Exception):
    """Custom Exception für Ollama Errors"""
    def __init__(self, operation: str, detail: str):
        self.operation = operation
        self.detail = detail
        super().__init__(f"Ollama {operation} failed: {detail}")
