from urllib.parse import urlparse


_GITHUB_HOSTS = {"github.com", "www.github.com"}


def normalize_repository_url(raw: str) -> str:
    """Normalize user-provided repository references into cloneable targets.

    Supports passthrough for local paths and non-HTTP git remotes.
    For GitHub web URLs, trims non-clone path segments like /tree/<ref>/...,
    /blob/<ref>/..., /commit/<sha>, etc. and returns canonical .git URL.
    """
    value = (raw or "").strip()
    if not value:
        return value

    lowered = value.lower()
    if not (lowered.startswith("http://") or lowered.startswith("https://")):
        return value

    parsed = urlparse(value)
    host = (parsed.netloc or "").lower()
    if host not in _GITHUB_HOSTS:
        return value

    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        return value

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]

    return f"https://github.com/{owner}/{repo}.git"
