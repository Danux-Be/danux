def compute_backoff(attempt: int, base_seconds: float, max_seconds: float) -> float:
    if attempt < 1:
        raise ValueError('attempt must be >= 1')
    delay = base_seconds * (2 ** (attempt - 1))
    return min(delay, max_seconds)
