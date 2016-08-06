------ trigger for ani-------
CREATE OR REPLACE FUNCTION public.ani_stat_insert_trigger()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    table_master    varchar(255)        := 'ani_stat';
    table_part      varchar(255)        := '';
BEGIN
    -- set partition name ---------------------------------------
    table_part := table_master
                    || '_' || DATE_PART( 'year', NEW.DATE )::TEXT
                    || '_' || DATE_PART( 'month', NEW.DATE )::TEXT
                    || '_' || DATE_PART( 'day', NEW.DATE )::TEXT;

    -- check partition exists --------------------------------
    PERFORM
        1
    FROM
        pg_class
    WHERE
        relname = table_part
    LIMIT
        1;

    -- create partiotion if not exists ----------------------
    IF NOT FOUND
    THEN
        -- create_partitionу --------------------------------
        EXECUTE '
            CREATE TABLE ' || table_part || ' ( )
            INHERITS ( ' || table_master || ' )
            WITH ( OIDS=FALSE )';

        -- create indexes -----------------------------------
        EXECUTE '
            CREATE INDEX ' || table_part || 'ani_ip_date_index
            ON ' || table_part || '
            USING btree
            (date, ani, ip)';
    END IF;

    -- insert data -------------------------------------------
    EXECUTE '
        INSERT INTO ' || table_part || '
        SELECT ( (' || QUOTE_LITERAL(NEW) || ')::' || TG_RELNAME || ' ).*';

    RETURN NULL;
END;
$function$;


CREATE TRIGGER ani_stat_insert_trigger
  BEFORE INSERT
  ON ani_stat
  FOR EACH ROW
  EXECUTE PROCEDURE ani_stat_insert_trigger();



----trigger for dnis------
CREATE OR REPLACE FUNCTION public.dnis_stat_insert_trigger()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    table_master    varchar(255)        := 'dnis_stat';
    table_part      varchar(255)        := '';
BEGIN
    -- set partition name ---------------------------------------
    table_part := table_master
                    || '_' || DATE_PART( 'year', NEW.DATE )::TEXT
                    || '_' || DATE_PART( 'month', NEW.DATE )::TEXT
                    || '_' || DATE_PART( 'day', NEW.DATE )::TEXT;

    -- check partition exists --------------------------------
    PERFORM
        1
    FROM
        pg_class
    WHERE
        relname = table_part
    LIMIT
        1;

    -- create partiotion if not exists ----------------------
    IF NOT FOUND
    THEN
        -- create_partitionу --------------------------------
        EXECUTE '
            CREATE TABLE ' || table_part || ' ( )
            INHERITS ( ' || table_master || ' )
            WITH ( OIDS=FALSE )';

        -- create indexes -----------------------------------
        EXECUTE '
            CREATE INDEX ' || table_part || 'dnis_ip_date_index
            ON ' || table_part || '
            USING btree
            (date, dnis, ip)';
    END IF;

    -- insert data -------------------------------------------
    EXECUTE '
        INSERT INTO ' || table_part || '
        SELECT ( (' || QUOTE_LITERAL(NEW) || ')::' || TG_RELNAME || ' ).*';

    RETURN NULL;
END;
$function$;


CREATE TRIGGER dnis_stat_insert_trigger
  BEFORE INSERT
  ON dnis_stat
  FOR EACH ROW
  EXECUTE PROCEDURE dnis_stat_insert_trigger();
