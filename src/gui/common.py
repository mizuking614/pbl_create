import streamlit as st
from pathlib import Path
import src.core.models as models

def root_path() -> Path:
    return models.root_path()

def refresh_state() -> tuple[list[models.Course], list[models.MaterialRecord]]:
    return models.load_state(root_path())

def args(**kwargs):
    # Mimics simple Namespace for compatibility
    from types import SimpleNamespace
    return SimpleNamespace(**kwargs)
