import sqlalchemy as sa
from sqlalchemy import Table, Column, MetaData

metadata = MetaData()


__all__ = ("Dnis", "Statistics", "Calls")

Dnis = Table('dnis',
             metadata,
             Column('id', sa.Integer, primary_key=True),
             Column('lrm', sa.SmallInteger),
             Column("is_mobile", sa.Boolean),
             Column("carrier", sa.Text))

Statistics = Table("statistics",
                   metadata,
                   Column('id', sa.Integer, primary_key=True),
                   Column('dnis', sa.String(128)),
                   Column('code_200', sa.Boolean),
                   Column('code_503', sa.Boolean),
                   Column('code_486', sa.Boolean),
                   Column('code_487', sa.Boolean),
                   Column('code_402', sa.Boolean),
                   Column('code_480', sa.Boolean),
                   Column('code_other_4xx', sa.Boolean),
                   Column('code_other_5xx', sa.Boolean),
                   Column('last_connect_on', sa.DateTime(timezone=False)),
                   Column('last_block_on', sa.DateTime(timezone=False)),
                   Column('last_unblock_on', sa.DateTime(timezone=False)))

Calls = Table("calls",
              metadata,
              Column('id', sa.Integer, primary_key=True),
              Column('call_id', sa.String(128)),
              Column('dnis', sa.Integer),
              Column('ani', sa.Integer),
              Column('time', sa.Integer),
              Column('non_zero', sa.Boolean),
              Column('num_valid_egress', sa.Integer),
              Column("duration", sa.Integer),
              Column("busy", sa.Boolean),
              Column("ring_time", sa.Integer))


#await conn.execute(tbl.insert().values(val='abc'))
