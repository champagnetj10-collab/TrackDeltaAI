"""Row Level Security policies

The FastAPI backend connects directly to Postgres (not through Supabase's
PostgREST layer) as the table-owning role, which bypasses RLS by default —
these policies are NOT what authorizes the backend's own queries (that's
still enforced in application code, e.g. sessions.py's _get_session_or_404
filtering by current_user.id). This is defense-in-depth: it guarantees data
isolation for any other access path to this database (Supabase's REST/
GraphQL API, the SQL editor with a non-owner role, a future feature that
queries Supabase directly from the frontend, etc).

Deliberately NOT using FORCE ROW LEVEL SECURITY, since that would also
restrict the owning role the backend connects as, breaking the app.

Revision ID: 002
Revises: 001
Create Date: 2026-07-09
"""
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

# Tables with a direct user_id column - straightforward "own rows only" policy.
_USER_SCOPED_TABLES = [
    "sessions",
    "driver_dna",
    "debriefs",
    "conversations",
    "subscription_events",
]


def upgrade() -> None:
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY users_select_own ON users FOR SELECT USING (id = auth.uid())"
    )
    op.execute(
        "CREATE POLICY users_update_own ON users FOR UPDATE USING (id = auth.uid())"
    )

    for table in _USER_SCOPED_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY {table}_select_own ON {table} "
            f"FOR SELECT USING (user_id = auth.uid())"
        )

    # sessions and conversations are the two tables users directly create/
    # modify themselves (uploading a session, starting a Delta conversation);
    # everything else (driver_dna, debriefs, subscription_events) is written
    # only by the backend pipeline/webhooks, so read-only policies are enough.
    op.execute(
        "CREATE POLICY sessions_insert_own ON sessions "
        "FOR INSERT WITH CHECK (user_id = auth.uid())"
    )
    op.execute(
        "CREATE POLICY sessions_update_own ON sessions "
        "FOR UPDATE USING (user_id = auth.uid())"
    )
    op.execute(
        "CREATE POLICY sessions_delete_own ON sessions "
        "FOR DELETE USING (user_id = auth.uid())"
    )
    op.execute(
        "CREATE POLICY conversations_insert_own ON conversations "
        "FOR INSERT WITH CHECK (user_id = auth.uid())"
    )

    # conversation_messages has no user_id column - scope through its parent
    # conversation instead.
    op.execute("ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY conversation_messages_select_own ON conversation_messages "
        "FOR SELECT USING ("
        "  conversation_id IN (SELECT id FROM conversations WHERE user_id = auth.uid())"
        ")"
    )
    op.execute(
        "CREATE POLICY conversation_messages_insert_own ON conversation_messages "
        "FOR INSERT WITH CHECK ("
        "  conversation_id IN (SELECT id FROM conversations WHERE user_id = auth.uid())"
        ")"
    )

    # tracks / track_corners are shared reference data, not user-owned -
    # readable by anyone signed in, writable only by the backend's direct
    # (RLS-bypassing) connection.
    op.execute("ALTER TABLE tracks ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY tracks_select_all ON tracks FOR SELECT USING (true)")
    op.execute("ALTER TABLE track_corners ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY track_corners_select_all ON track_corners FOR SELECT USING (true)")


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS track_corners_select_all ON track_corners")
    op.execute("ALTER TABLE track_corners DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS tracks_select_all ON tracks")
    op.execute("ALTER TABLE tracks DISABLE ROW LEVEL SECURITY")

    op.execute("DROP POLICY IF EXISTS conversation_messages_insert_own ON conversation_messages")
    op.execute("DROP POLICY IF EXISTS conversation_messages_select_own ON conversation_messages")
    op.execute("ALTER TABLE conversation_messages DISABLE ROW LEVEL SECURITY")

    op.execute("DROP POLICY IF EXISTS conversations_insert_own ON conversations")
    op.execute("DROP POLICY IF EXISTS sessions_delete_own ON sessions")
    op.execute("DROP POLICY IF EXISTS sessions_update_own ON sessions")
    op.execute("DROP POLICY IF EXISTS sessions_insert_own ON sessions")

    for table in _USER_SCOPED_TABLES:
        op.execute(f"DROP POLICY IF EXISTS {table}_select_own ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    op.execute("DROP POLICY IF EXISTS users_update_own ON users")
    op.execute("DROP POLICY IF EXISTS users_select_own ON users")
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY")
