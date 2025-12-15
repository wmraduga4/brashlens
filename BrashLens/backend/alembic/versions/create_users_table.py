"""create users table

Revision ID: a1b2c3d4e5f6
Revises: 0440c300230e
Create Date: 2025-12-12 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '0440c300230e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создание enum типа для ролей пользователей (с проверкой существования)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE user_role AS ENUM ('photographer', 'client', 'admin');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Создание таблицы users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=False),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('role', postgresql.ENUM('photographer', 'client', 'admin', name='user_role', create_type=False), nullable=False),
        sa.Column('language', sa.String(length=5), nullable=False, server_default='ru'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # Создание индексов
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_role', 'users', ['role'])
    op.create_index('ix_users_role_is_active', 'users', ['role', 'is_active'])


def downgrade() -> None:
    # Удаление индексов
    op.drop_index('ix_users_role_is_active', table_name='users')
    op.drop_index('ix_users_role', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_telegram_id', table_name='users')

    # Удаление таблицы
    op.drop_table('users')

    # Удаление enum типа (с проверкой существования)
    op.execute("DROP TYPE IF EXISTS user_role")
