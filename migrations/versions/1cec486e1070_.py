"""empty message

Revision ID: 1cec486e1070
Revises: 702c4be2fdb5
Create Date: 2025-02-27 00:26:06.789404

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cec486e1070'
down_revision = '702c4be2fdb5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=10),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.String(length=10),
               type_=sa.INTEGER(),
               existing_nullable=False)

    # ### end Alembic commands ###
