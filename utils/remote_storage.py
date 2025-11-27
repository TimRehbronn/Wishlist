import os
import json
import base64
import requests


def _get_secrets():
    """Fetch required secrets from environment variables (Streamlit Cloud uses env from st.secrets)."""
    token = os.environ.get("GH_TOKEN")
    repo = os.environ.get("GH_REPO")  # e.g., "TimRehbronn/Wishlist"
    path_prefix = os.environ.get("GH_PATH", "cloud-data")  # folder in repo to store files
    return token, repo, path_prefix


def _gh_headers(token: str):
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }


def _repo_api(repo: str):
    return f"https://api.github.com/repos/{repo}"


def remote_available() -> bool:
    token, repo, _ = _get_secrets()
    return bool(token and repo)


def _get_file_sha(token: str, repo: str, path: str):
    url = f"{_repo_api(repo)}/contents/{path}"
    r = requests.get(url, headers=_gh_headers(token))
    if r.status_code == 200:
        return r.json().get("sha")
    return None


def _put_file(token: str, repo: str, path: str, content: bytes, message: str):
    url = f"{_repo_api(repo)}/contents/{path}"
    sha = _get_file_sha(token, repo, path)
    data = {
        "message": message,
        "content": base64.b64encode(content).decode("utf-8"),
        "branch": "main",
    }
    if sha:
        data["sha"] = sha
    r = requests.put(url, headers=_gh_headers(token), json=data)
    r.raise_for_status()
    return r.json()


def _get_file(token: str, repo: str, path: str):
    url = f"{_repo_api(repo)}/contents/{path}"
    r = requests.get(url, headers=_gh_headers(token))
    if r.status_code == 200:
        j = r.json()
        content_b64 = j.get("content", "")
        if content_b64:
            return base64.b64decode(content_b64).decode("utf-8")
    return None


def list_index_path(prefix: str) -> str:
    return f"{prefix}/wishlists_index.json"


def wishlist_path(prefix: str, wishlist_id: str) -> str:
    return f"{prefix}/wishlist_{wishlist_id}.json"


def get_all_wishlists_remote():
    token, repo, prefix = _get_secrets()
    if not remote_available():
        return []
    content = _get_file(token, repo, list_index_path(prefix))
    if not content:
        return []
    try:
        return json.loads(content)
    except Exception:
        return []


def save_wishlists_index_remote(wishlists):
    token, repo, prefix = _get_secrets()
    if not remote_available():
        return
    payload = json.dumps(wishlists, indent=4, ensure_ascii=False).encode("utf-8")
    _put_file(token, repo, list_index_path(prefix), payload, "chore: update wishlists index")


def load_wishlist_remote(wishlist_id: str):
    token, repo, prefix = _get_secrets()
    if not remote_available():
        return None
    content = _get_file(token, repo, wishlist_path(prefix, wishlist_id))
    if not content:
        return None
    try:
        return json.loads(content)
    except Exception:
        return None


def save_wishlist_remote(wishlist_id: str, data: dict):
    token, repo, prefix = _get_secrets()
    if not remote_available():
        return
    payload = json.dumps(data, indent=4, ensure_ascii=False).encode("utf-8")
    _put_file(token, repo, wishlist_path(prefix, wishlist_id), payload, f"feat: update wishlist {wishlist_id}")

