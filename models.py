import sqlalchemy as sa
from sqlalchemy import Table, Column, MetaData

metadata = MetaData()


__all__ = ("Dnis", "Statistics", "Calls")

Dnis = Table('dnis',
             metadata,
             Column('id', sa.Integer, primary_key=True),
             Column('dnis', sa.String(128)),
             Column('lrm', sa.SmallInteger),
             Column("is_mobile", sa.Boolean),
             Column("carrier", sa.Text))

Statistics = Table("statistics",
                   metadata,
                   Column('id', sa.Integer, primary_key=True),
                   Column('ip', sa.String(16)),
                   Column('date', sa.DateTime(timezone=False)),
                   Column('dnis', sa.String(128)),
                   Column('code_200', sa.Integer),
                   Column('code_503', sa.Integer),
                   Column('code_486', sa.Integer),
                   Column('code_487', sa.Integer),
                   Column('code_402', sa.Integer),
                   Column('code_480', sa.Integer),
                   Column('code_other_4xx', sa.Integer),
                   Column('code_other_5xx', sa.Integer),
                   Column('last_block_on', sa.DateTime(timezone=False)),
                   Column('last_unblock_on', sa.DateTime(timezone=False)))

Calls = Table("calls",
              metadata,
              Column('id', sa.Integer, primary_key=True),
              Column('call_id', sa.String(128)),
              Column('dnis', sa.String(128)),
              Column('ani', sa.String(128)),
              Column('time', sa.Integer),
              Column('non_zero', sa.Boolean),
              Column('num_valid_egress', sa.Integer),
              Column("duration", sa.Integer),
              Column("busy", sa.Boolean),
              Column("ring_time", sa.Integer),
              Column("failed", sa.Boolean))

