from dataclasses import dataclass


@dataclass(frozen=True)
class ListPatientsQuery:
    page: int = 1
    page_size: int = 20
    search: str | None = None
    is_active: bool | None = None
