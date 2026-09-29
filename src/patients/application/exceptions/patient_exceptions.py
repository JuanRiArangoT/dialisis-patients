class PatientApplicationError(Exception):
    """Base exception for patient application errors."""


class PatientNotFoundApplicationError(PatientApplicationError):
    """Raised when a patient does not exist."""


class PatientConflictApplicationError(PatientApplicationError):
    """Raised when a patient conflicts with existing data."""
