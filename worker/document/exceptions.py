# Nur vom Worker genutzte Exceptions (PDF/Split-Logik)


class PDFProcessingException(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        self.message = f"PDF processing failed: {detail}"
        super().__init__(self.message)


class TextSplittingException(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        self.message = f"Splitting text failed: {detail}"
        super().__init__(self.message)
