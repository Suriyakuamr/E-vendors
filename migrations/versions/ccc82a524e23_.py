from alembic import op
import sqlalchemy as sa

revision = 'ccc82a524e23'
down_revision = 'previous_revision'
def upgrade():
    op.create_table('temp_purchase_history',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('product_id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('purchase_date', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.execute('INSERT INTO temp_purchase_history SELECT * FROM purchase_history')

    op.drop_table('purchase_history')

    op.rename_table('temp_purchase_history', 'purchase_history')

    op.create_unique_constraint(None, 'user', ['email'])


def downgrade():
    op.create_table('temp_purchase_history',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('product_id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('purchase_date', sa.DateTime(), nullable=False),
                    sa.Column('quantity', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.execute('INSERT INTO temp_purchase_history SELECT * FROM purchase_history')

    op.drop_table('purchase_history')

    op.rename_table('temp_purchase_history', 'purchase_history')

    op.drop_constraint(None, 'user', type_='unique')
 