"""Compatibility Streamlit entrypoint for the project UI.

This keeps the main interface in ``app.py`` while also allowing
``streamlit run _ui.py`` for users who expect a dedicated UI module.
"""

from app import *  # noqa: F401,F403
