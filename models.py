import sqlalchemy as sa
from sqlalchemy import Table, Column, MetaData

metadata = MetaData()


__all__ = ("Dnis", "DnisStatistics", "Calls", "AniStatistics")

Dnis = Table('dnis',
             metadata,
             Column('id', sa.Integer, primary_key=True),
             Column('dnis', sa.String(128)),
             Column('lrm', sa.SmallInteger),
             Column("is_mobile", sa.Boolean),
             Column("carrier", sa.Text))


"""DDL"""
"""

CREATE TABLE public.dnis_stat (
  id int4 NOT NULL DEFAULT nextval('dnis_stat_id_seq'::regclass),
  ip varchar(16) NULL,
  "date" date NULL,
  dnis varchar(128) NULL,
  code_200 int4 NULL,
  code_404 int4 NULL,
  code_503 int4 NULL,
  code_486 int4 NULL,
  code_487 int4 NULL,
  code_402 int4 NULL,
  code_480 int4 NULL,
  code_other_4xx int4 NULL,
  code_other_5xx int4 NULL,
  total_ingress int4 NULL,
  valid_ingress int4 NULL,
  non_zero_call varchar(128) NULL,
  num_calls_ringtone varchar(128) NULL,
  duration int4 NULL,
  last_block_on date NULL,
  last_unblock_on date NULL,
  CONSTRAINT dnis_stat_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

"""

DnisStatistics = Table("dnis_stat",
                   metadata,
                   Column('id', sa.Integer, primary_key=True),
                   Column('ip', sa.String(16)),
                   Column('date', sa.DateTime(timezone=False)),
                   Column('time', sa.Time(timezone=False)),
                   Column('dnis', sa.String(128)),
                   Column('code_200', sa.Integer),
                   Column('code_404', sa.Integer),
                   Column('code_503', sa.Integer),
                   Column('code_486', sa.Integer),
                   Column('code_487', sa.Integer),
                   Column('code_402', sa.Integer),
                   Column('code_480', sa.Integer),
                   Column('code_other_4xx', sa.Integer),
                   Column('code_other_5xx', sa.Integer),
                   Column("total_ingress", sa.Integer),
                   Column("valid_ingress", sa.Integer),
                   Column("duration", sa.Integer),
                   Column("non_zero_call", sa.String(128)),
                   Column("num_call_ringtone", sa.Integer),
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


"""DDL"""
"""
CREATE TABLE public.ani_stat (
  id int4 NOT NULL DEFAULT nextval('ani_stat_id_seq'::regclass),
  ip varchar(16) NULL,
  "date" date NULL,
  ani varchar(128) NULL,
  code_200 int4 NULL,
  code_404 int4 NULL,
  code_503 int4 NULL,
  code_486 int4 NULL,
  code_487 int4 NULL,
  code_402 int4 NULL,
  code_480 int4 NULL,
  code_other_4xx int4 NULL,
  code_other_5xx int4 NULL,
  total_ingress int4 NULL,
  valid_ingress int4 NULL,
  non_zero_call varchar(128) NULL,
  num_call_ringtone varchar(128) NULL,
  duration int4 NULL,
  last_block_on date NULL,
  last_unblock_on date NULL,
  CONSTRAINT ani_stat_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
"""

AniStatistics = Table("ani_stat",
                      metadata,
                      Column('id', sa.Integer, primary_key=True),
                      Column('ip', sa.String(16)),
                      Column('date', sa.DateTime(timezone=False)),
                      Column('time', sa.Time(timezone=False)),
                      Column('ani', sa.String(128)),
                      Column('code_200', sa.Integer),
                      Column('code_404', sa.Integer),
                      Column('code_503', sa.Integer),
                      Column('code_486', sa.Integer),
                      Column('code_487', sa.Integer),
                      Column('code_402', sa.Integer),
                      Column('code_480', sa.Integer),
                      Column('code_other_4xx', sa.Integer),
                      Column('code_other_5xx', sa.Integer),
                      Column("total_ingress", sa.Integer),
                      Column("valid_ingress", sa.Integer),
                      Column("non_zero_call", sa.String(128)),
                      Column("duration", sa.Integer),
                      Column("num_call_ringtone", sa.Integer),
                      Column('last_block_on', sa.DateTime(timezone=False)),
                      Column('last_unblock_on', sa.DateTime(timezone=False)))
