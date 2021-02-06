from pathlib import Path


def get_project_root() -> Path:
    """Restituisce il percorso assoluto della cartella prima di 65527_65549_65227_43779_65068"""
    return Path(__file__).parent.parent.parent
