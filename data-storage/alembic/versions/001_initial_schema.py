"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-01-27

"""
from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Read and execute the schema.sql file
    from pathlib import Path
    
    schema_file = Path(__file__).parent.parent.parent / 'schema.sql'
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Split by semicolons and execute each statement
    # Filter out empty statements and comments
    statements = [
        stmt.strip() 
        for stmt in schema_sql.split(';') 
        if stmt.strip() and not stmt.strip().startswith('--')
    ]
    
    for statement in statements:
        if statement:
            op.execute(statement + ';')


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('betting_odds')
    op.drop_table('ai_predictions')
    op.drop_table('matches')
    op.drop_table('tournaments')
    op.drop_table('teams')
    op.drop_table('data_sources')

