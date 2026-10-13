import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from backend_v2.models import Base
from backend_v2.database import build_engine
config = context.config
url = os.environ.get('DATABASE_URL', config.get_main_option('sqlalchemy.url'))

def run_offline():
    context.configure(url=url,target_metadata=Base.metadata,literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_online():
    engine=build_engine(url)
    with engine.connect() as connection:
        context.configure(connection=connection,target_metadata=Base.metadata,render_as_batch=engine.dialect.name=='sqlite')
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()

if context.is_offline_mode():run_offline()
else:run_online()
