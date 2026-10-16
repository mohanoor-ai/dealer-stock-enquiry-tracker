"""Shared quotas and private API tables on PostgreSQL."""
from alembic import op
import sqlalchemy as sa
revision = 'd2b001'
down_revision = 'c738f767d239'
branch_labels = None
depends_on = None
TABLES = ['vehicles_v2', 'enquiries_v2', 'tasks_v2', 'audit_events_v2', 'rate_buckets_v2']


def upgrade():
    op.create_table('rate_buckets_v2', sa.Column('key', sa.String(64), primary_key=True),
                    sa.Column('window', sa.Integer(), nullable=False), sa.Column('count', sa.Integer(), nullable=False))
    if op.get_bind().dialect.name == 'postgresql':
        for table in TABLES:
            op.execute(sa.text(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY'))
            # Browser-facing Supabase Data API roles have no policies and no grants.
            for role in ['anon', 'authenticated']:
                exists = op.get_bind().execute(sa.text('SELECT 1 FROM pg_roles WHERE rolname=:role'), {'role': role}).first()
                if exists:
                    op.execute(sa.text(f'REVOKE ALL ON TABLE {table} FROM {role}'))


def downgrade():
    op.drop_table('rate_buckets_v2')
