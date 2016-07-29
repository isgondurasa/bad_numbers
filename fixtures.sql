--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.1
-- Dumped by pg_dump version 9.5.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner:
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: calls; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE calls (
    id integer NOT NULL,
    call_id character varying(128),
    dnis character varying(128),
    ani text,
    "time" text,
    non_zero boolean DEFAULT false,
    num_valid_egress integer,
    duration integer DEFAULT 0,
    busy boolean,
    ring_time integer,
    failed boolean
);


ALTER TABLE calls OWNER TO postgres;

--
-- Name: calls_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE calls_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE calls_id_seq OWNER TO postgres;

--
-- Name: calls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE calls_id_seq OWNED BY calls.id;


--
-- Name: dnis; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE dnis (
    id integer NOT NULL,
    lrn integer,
    is_mobile boolean,
    carrier text,
    dnis character varying(128)
);


ALTER TABLE dnis OWNER TO postgres;

--
-- Name: dnis_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE dnis_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dnis_id_seq OWNER TO postgres;

--
-- Name: dnis_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE dnis_id_seq OWNED BY dnis.id;


--
-- Name: statistics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE statistics (
    id integer NOT NULL,
    ip character varying(16),
    dnis character varying(128),
    code_200 integer,
    code_404 integer,
    code_503 integer,
    code_486 integer,
    code_487 integer,
    code_402 integer,
    code_480 integer,
    code_other_4xx integer,
    code_other_5xx integer,
    date timestamp without time zone,
    last_block_on timestamp without time zone,
    last_unblock_on timestamp without time zone
);


ALTER TABLE statistics OWNER TO postgres;

--
-- Name: statistics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE statistics_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE statistics_id_seq OWNER TO postgres;

--
-- Name: statistics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE statistics_id_seq OWNED BY statistics.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY calls ALTER COLUMN id SET DEFAULT nextval('calls_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY dnis ALTER COLUMN id SET DEFAULT nextval('dnis_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY statistics ALTER COLUMN id SET DEFAULT nextval('statistics_id_seq'::regclass);


--
-- Data for Name: calls; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY calls (id, call_id, dnis, ani, "time", non_zero, num_valid_egress, duration, busy, ring_time, failed) FROM stdin;
\.


--
-- Name: calls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('calls_id_seq', 1, true);


--
-- Data for Name: dnis; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY dnis (id, lrn, is_mobile, carrier, dnis) FROM stdin;
\.


--
-- Name: dnis_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('dnis_id_seq', 1, false);


--
-- Data for Name: statistics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY statistics (id, dnis, code_200, code_404, code_503, code_486, code_487, code_402, code_480, code_other_4xx, code_other_5xx, last_connect_on, last_block_on, last_unblock_on) FROM stdin;
\.


--
-- Name: statistics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('statistics_id_seq', 1, true);


--
-- Name: calls_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY calls
    ADD CONSTRAINT calls_pkey PRIMARY KEY (id);


--
-- Name: dnis_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY dnis
    ADD CONSTRAINT dnis_pkey PRIMARY KEY (id);


--
-- Name: statistics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY statistics
    ADD CONSTRAINT statistics_pkey PRIMARY KEY (id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

