SENSITIVE_HEADERS = {'authorization', 'proxy-authorization', 'x-api-key', 'cookie', 'set-cookie'}


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    redacted: dict[str, str] = {}
    for key, value in headers.items():
        if key.lower() in SENSITIVE_HEADERS:
            redacted[key] = '[REDACTED]'
        else:
            redacted[key] = value
    return redacted
