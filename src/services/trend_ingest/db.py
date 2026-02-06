"""Database helpers (placeholders).

Real SQLAlchemy engine and session helpers should be implemented in
`models_sqlalchemy.py` and imported here in production.
"""

def get_db_session():
    """Placeholder function for getting a DB session.

    Raises NotImplementedError in scaffold until SQLAlchemy setup is added.
    """
    raise NotImplementedError("DB session not configured in scaffold. See plan/data-model.md")
