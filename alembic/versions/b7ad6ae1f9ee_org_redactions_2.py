"""org redactions 2

Revision ID: b7ad6ae1f9ee
Revises: 9644c40c26cb
Create Date: 2023-08-12 21:00:10.184754

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = 'b7ad6ae1f9ee'
down_revision = '9644c40c26cb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_table('spatial_ref_sys')
    op.add_column('organizations', sa.Column('image_url', sa.String(), nullable=True))
    op.add_column('organizations', sa.Column('url', sa.String(), nullable=True))
    op.add_column('organizations', sa.Column('subdomain', sa.String(), nullable=True))
    op.alter_column('organizations', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('organizations', 'phone',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.add_column('users', sa.Column('image_url', sa.String(), nullable=True))
    op.drop_column('users', 'icon_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('icon_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('users', 'image_url')
    op.alter_column('organizations', 'phone',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('organizations', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('organizations', 'subdomain')
    op.drop_column('organizations', 'url')
    op.drop_column('organizations', 'image_url')
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
