from __future__ import annotations


class DataHubError(Exception):
    def __init__(self, error_code: str, message: str, *, http_status: int = 422):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.http_status = http_status

    def as_dict(self) -> dict[str, str]:
        return {"error_code": self.error_code, "message": self.message}
