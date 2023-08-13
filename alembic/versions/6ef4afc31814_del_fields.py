"""del fields

Revision ID: 6ef4afc31814
Revises: 9a511cd914ae
Create Date: 2023-08-13 08:26:13.329042

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = '6ef4afc31814'
down_revision = '9a511cd914ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_table('spatial_ref_sys')
    op.drop_column('user_history', 'favourited')
    op.drop_column('user_history', 'opened')
    op.drop_column('user_history', 'showed')
    op.drop_column('user_history', 'liked')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_history', sa.Column('liked', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('user_history', sa.Column('showed', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('user_history', sa.Column('opened', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('user_history', sa.Column('favourited', sa.BOOLEAN(), autoincrement=False, nullable=False))
    # op.create_table('spatial_ref_sys',
    # sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    # sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    # sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    # sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    # sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    # sa.CheckConstraint('(srid > 0) AND (srid <= 998999)', name='spatial_ref_sys_srid_check'),
    # sa.PrimaryKeyConstraint('srid', name='spatial_ref_sys_pkey')
    # )
    # ### end Alembic commands ###