"""empty message

Revision ID: 8f5167ac7dd1
Revises: 135e4241f9a1
Create Date: 2025-02-27 15:12:26.879180

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f5167ac7dd1'
down_revision = '135e4241f9a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('address',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('address_line', sa.String(length=255), nullable=False),
    sa.Column('city', sa.String(length=50), nullable=False),
    sa.Column('state', sa.String(length=50), nullable=False),
    sa.Column('zip_code', sa.String(length=20), nullable=False),
    sa.Column('is_preferred', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], name=op.f('fk_address_customer_id_customer')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_address'))
    )
    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.drop_column('address')

    with op.batch_alter_table('delivery_agent', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id_proof', sa.String(length=12), server_default='', nullable=False))
        batch_op.add_column(sa.Column('is_approved', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('delivery_agent', schema=None) as batch_op:
        batch_op.drop_column('is_approved')
        batch_op.drop_column('id_proof')

    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('address', sa.VARCHAR(length=100), nullable=False))

    op.drop_table('address')
    # ### end Alembic commands ###
