--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

ALTER TABLE ONLY public.trainee_allocations DROP CONSTRAINT "trainee_allocations_FK_3";
ALTER TABLE ONLY public.trainee_allocations DROP CONSTRAINT "trainee_allocations_FK_2";
ALTER TABLE ONLY public.trainee_allocations DROP CONSTRAINT "trainee_allocations_FK_1";
ALTER TABLE ONLY public.teams DROP CONSTRAINT "teams_FK_1";
ALTER TABLE ONLY public.team_scores DROP CONSTRAINT "team_scores_FK_1";
ALTER TABLE ONLY public.team_score_sheets DROP CONSTRAINT "team_score_sheets_FK_2";
ALTER TABLE ONLY public.team_score_sheets DROP CONSTRAINT "team_score_sheets_FK_1";
ALTER TABLE ONLY public.speaker_scores DROP CONSTRAINT "speaker_scores_FK_1";
ALTER TABLE ONLY public.speaker_score_sheets DROP CONSTRAINT "speaker_score_sheets_FK_3";
ALTER TABLE ONLY public.speaker_score_sheets DROP CONSTRAINT "speaker_score_sheets_FK_2";
ALTER TABLE ONLY public.speaker_score_sheets DROP CONSTRAINT "speaker_score_sheets_FK_1";
ALTER TABLE ONLY public.rounds DROP CONSTRAINT "rounds_FK_1";
ALTER TABLE ONLY public.debates_teams_xrefs DROP CONSTRAINT "debates_teams_xrefs_FK_2";
ALTER TABLE ONLY public.debates_teams_xrefs DROP CONSTRAINT "debates_teams_xrefs_FK_1";
ALTER TABLE ONLY public.debates DROP CONSTRAINT "debates_FK_2";
ALTER TABLE ONLY public.debates DROP CONSTRAINT "debates_FK_1";
ALTER TABLE ONLY public.debaters DROP CONSTRAINT "debaters_FK_1";
ALTER TABLE ONLY public.adjudicators DROP CONSTRAINT "adjudicators_FK_1";
ALTER TABLE ONLY public.adjudicator_feedback_sheets DROP CONSTRAINT "adjudicator_feedback_sheets_FK_3";
ALTER TABLE ONLY public.adjudicator_feedback_sheets DROP CONSTRAINT "adjudicator_feedback_sheets_FK_2";
ALTER TABLE ONLY public.adjudicator_feedback_sheets DROP CONSTRAINT "adjudicator_feedback_sheets_FK_1";
ALTER TABLE ONLY public.adjudicator_conflicts DROP CONSTRAINT "adjudicator_conflicts_FK_2";
ALTER TABLE ONLY public.adjudicator_conflicts DROP CONSTRAINT "adjudicator_conflicts_FK_1";
ALTER TABLE ONLY public.adjudicator_allocations DROP CONSTRAINT "adjudicator_allocations_FK_2";
ALTER TABLE ONLY public.adjudicator_allocations DROP CONSTRAINT "adjudicator_allocations_FK_1";
ALTER TABLE ONLY public.venues DROP CONSTRAINT venues_pkey;
ALTER TABLE ONLY public.venues DROP CONSTRAINT venues_name;
ALTER TABLE ONLY public.trainee_allocations DROP CONSTRAINT trainee_allocations_trainee_id_chair_id_round_id;
ALTER TABLE ONLY public.trainee_allocations DROP CONSTRAINT trainee_allocations_pkey;
ALTER TABLE ONLY public.teams DROP CONSTRAINT teams_pkey;
ALTER TABLE ONLY public.teams DROP CONSTRAINT teams_name;
ALTER TABLE ONLY public.team_scores DROP CONSTRAINT team_scores_team_id;
ALTER TABLE ONLY public.team_scores DROP CONSTRAINT team_scores_pkey;
ALTER TABLE ONLY public.team_score_sheets DROP CONSTRAINT team_score_sheets_pkey;
ALTER TABLE ONLY public.speaker_scores DROP CONSTRAINT speaker_scores_pkey;
ALTER TABLE ONLY public.speaker_scores DROP CONSTRAINT speaker_scores_debater_id;
ALTER TABLE ONLY public.speaker_score_sheets DROP CONSTRAINT speaker_score_sheets_pkey;
ALTER TABLE ONLY public.rounds DROP CONSTRAINT rounds_pkey;
ALTER TABLE ONLY public.rounds DROP CONSTRAINT rounds_name;
ALTER TABLE ONLY public.institutions DROP CONSTRAINT institutions_pkey;
ALTER TABLE ONLY public.institutions DROP CONSTRAINT institutions_code;
ALTER TABLE ONLY public.debates_teams_xrefs DROP CONSTRAINT debates_teams_xrefs_pkey;
ALTER TABLE ONLY public.debates_teams_xrefs DROP CONSTRAINT debates_teams_xrefs_debate_id_team_id;
ALTER TABLE ONLY public.debates DROP CONSTRAINT debates_round_id_venue_id;
ALTER TABLE ONLY public.debates DROP CONSTRAINT debates_pkey;
ALTER TABLE ONLY public.debaters DROP CONSTRAINT debaters_pkey;
ALTER TABLE ONLY public.debaters DROP CONSTRAINT debaters_name;
ALTER TABLE ONLY public.adjudicators DROP CONSTRAINT adjudicators_pkey;
ALTER TABLE ONLY public.adjudicators DROP CONSTRAINT adjudicators_name;
ALTER TABLE ONLY public.adjudicator_feedback_sheets DROP CONSTRAINT adjudicator_feedback_sheets_pkey;
ALTER TABLE ONLY public.adjudicator_conflicts DROP CONSTRAINT adjudicator_conflicts_pkey;
ALTER TABLE ONLY public.adjudicator_allocations DROP CONSTRAINT adjudicator_allocations_pkey;
ALTER TABLE ONLY public.adjudicator_allocations DROP CONSTRAINT adjudicator_allocations_debate_id_adjudicator_id;
DROP SEQUENCE public.venues_seq;
DROP SEQUENCE public.trainee_allocations_seq;
DROP SEQUENCE public.teams_seq;
DROP SEQUENCE public.team_scores_seq;
DROP SEQUENCE public.team_score_sheets_seq;
DROP SEQUENCE public.speaker_scores_seq;
DROP SEQUENCE public.speaker_score_sheets_seq;
DROP SEQUENCE public.rounds_seq;
DROP SEQUENCE public.institutions_seq;
DROP SEQUENCE public.debates_teams_xrefs_seq;
DROP SEQUENCE public.debates_seq;
DROP SEQUENCE public.debaters_seq;
DROP SEQUENCE public.adjudicators_seq;
DROP SEQUENCE public.adjudicator_feedback_sheets_seq;
DROP SEQUENCE public.adjudicator_conflicts_seq;
DROP SEQUENCE public.adjudicator_allocations_seq;
DROP TABLE public.venues;
DROP TABLE public.trainee_allocations;
DROP TABLE public.teams;
DROP TABLE public.team_scores;
DROP TABLE public.team_score_sheets;
DROP TABLE public.speaker_scores;
DROP TABLE public.speaker_score_sheets;
DROP TABLE public.rounds;
DROP TABLE public.institutions;
DROP TABLE public.debates_teams_xrefs;
DROP TABLE public.debates;
DROP TABLE public.debaters;
DROP TABLE public.adjudicators;
DROP TABLE public.adjudicator_feedback_sheets;
DROP TABLE public.adjudicator_conflicts;
DROP TABLE public.adjudicator_allocations;
DROP SCHEMA public;
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: adjudicator_allocations; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE adjudicator_allocations (
    id integer NOT NULL,
    debate_id integer NOT NULL,
    adjudicator_id integer NOT NULL,
    type integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.adjudicator_allocations OWNER TO postgres;

--
-- Name: adjudicator_conflicts; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE adjudicator_conflicts (
    id integer NOT NULL,
    team_id integer NOT NULL,
    adjudicator_id integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.adjudicator_conflicts OWNER TO postgres;

--
-- Name: adjudicator_feedback_sheets; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE adjudicator_feedback_sheets (
    id integer NOT NULL,
    adjudicator_id integer NOT NULL,
    adjudicator_allocation_id integer,
    debate_team_xref_id integer,
    comments character varying(500),
    score double precision NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.adjudicator_feedback_sheets OWNER TO postgres;

--
-- Name: adjudicators; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE adjudicators (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    test_score double precision NOT NULL,
    institution_id integer NOT NULL,
    active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.adjudicators OWNER TO postgres;

--
-- Name: debaters; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE debaters (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    team_id integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.debaters OWNER TO postgres;

--
-- Name: debates; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE debates (
    id integer NOT NULL,
    round_id integer NOT NULL,
    venue_id integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.debates OWNER TO postgres;

--
-- Name: debates_teams_xrefs; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE debates_teams_xrefs (
    id integer NOT NULL,
    debate_id integer NOT NULL,
    team_id integer NOT NULL,
    "position" integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.debates_teams_xrefs OWNER TO postgres;

--
-- Name: institutions; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE institutions (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.institutions OWNER TO postgres;

--
-- Name: rounds; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE rounds (
    id integer NOT NULL,
    name character varying NOT NULL,
    type integer NOT NULL,
    status integer DEFAULT 1 NOT NULL,
    preceded_by_round_id integer,
    feedback_weightage double precision DEFAULT 0 NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.rounds OWNER TO postgres;

--
-- Name: speaker_score_sheets; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE speaker_score_sheets (
    id integer NOT NULL,
    adjudicator_allocation_id integer NOT NULL,
    debate_team_xref_id integer NOT NULL,
    debater_id integer NOT NULL,
    score double precision NOT NULL,
    speaking_position integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.speaker_score_sheets OWNER TO postgres;

--
-- Name: speaker_scores; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE speaker_scores (
    id integer NOT NULL,
    debater_id integer NOT NULL,
    total_speaker_score double precision DEFAULT 0 NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.speaker_scores OWNER TO postgres;

--
-- Name: team_score_sheets; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE team_score_sheets (
    id integer NOT NULL,
    adjudicator_allocation_id integer NOT NULL,
    debate_team_xref_id integer NOT NULL,
    score integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.team_score_sheets OWNER TO postgres;

--
-- Name: team_scores; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE team_scores (
    id integer NOT NULL,
    team_id integer NOT NULL,
    total_team_score integer DEFAULT 0 NOT NULL,
    total_speaker_score double precision DEFAULT 0 NOT NULL,
    total_margin double precision DEFAULT 0 NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.team_scores OWNER TO postgres;

--
-- Name: teams; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE teams (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    institution_id integer NOT NULL,
    swing boolean DEFAULT false NOT NULL,
    active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.teams OWNER TO postgres;

--
-- Name: trainee_allocations; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE trainee_allocations (
    id integer NOT NULL,
    trainee_id integer NOT NULL,
    chair_id integer NOT NULL,
    round_id integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.trainee_allocations OWNER TO postgres;

--
-- Name: venues; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE venues (
    id integer NOT NULL,
    name character varying NOT NULL,
    active boolean DEFAULT true NOT NULL,
    priority integer DEFAULT 1 NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.venues OWNER TO postgres;

--
-- Name: adjudicator_allocations_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE adjudicator_allocations_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.adjudicator_allocations_seq OWNER TO postgres;

--
-- Name: adjudicator_allocations_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('adjudicator_allocations_seq', 573, true);


--
-- Name: adjudicator_conflicts_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE adjudicator_conflicts_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.adjudicator_conflicts_seq OWNER TO postgres;

--
-- Name: adjudicator_conflicts_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('adjudicator_conflicts_seq', 292, true);


--
-- Name: adjudicator_feedback_sheets_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE adjudicator_feedback_sheets_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.adjudicator_feedback_sheets_seq OWNER TO postgres;

--
-- Name: adjudicator_feedback_sheets_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('adjudicator_feedback_sheets_seq', 908, true);


--
-- Name: adjudicators_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE adjudicators_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.adjudicators_seq OWNER TO postgres;

--
-- Name: adjudicators_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('adjudicators_seq', 108, true);


--
-- Name: debaters_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE debaters_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.debaters_seq OWNER TO postgres;

--
-- Name: debaters_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('debaters_seq', 225, true);


--
-- Name: debates_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE debates_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.debates_seq OWNER TO postgres;

--
-- Name: debates_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('debates_seq', 354, true);


--
-- Name: debates_teams_xrefs_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE debates_teams_xrefs_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.debates_teams_xrefs_seq OWNER TO postgres;

--
-- Name: debates_teams_xrefs_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('debates_teams_xrefs_seq', 642, true);


--
-- Name: institutions_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE institutions_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.institutions_seq OWNER TO postgres;

--
-- Name: institutions_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('institutions_seq', 42, true);


--
-- Name: rounds_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE rounds_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.rounds_seq OWNER TO postgres;

--
-- Name: rounds_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('rounds_seq', 9, true);


--
-- Name: speaker_score_sheets_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE speaker_score_sheets_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.speaker_score_sheets_seq OWNER TO postgres;

--
-- Name: speaker_score_sheets_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('speaker_score_sheets_seq', 4219, true);


--
-- Name: speaker_scores_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE speaker_scores_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.speaker_scores_seq OWNER TO postgres;

--
-- Name: speaker_scores_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('speaker_scores_seq', 225, true);


--
-- Name: team_score_sheets_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE team_score_sheets_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.team_score_sheets_seq OWNER TO postgres;

--
-- Name: team_score_sheets_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('team_score_sheets_seq', 1063, true);


--
-- Name: team_scores_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE team_scores_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.team_scores_seq OWNER TO postgres;

--
-- Name: team_scores_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('team_scores_seq', 75, true);


--
-- Name: teams_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE teams_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.teams_seq OWNER TO postgres;

--
-- Name: teams_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('teams_seq', 75, true);


--
-- Name: trainee_allocations_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE trainee_allocations_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.trainee_allocations_seq OWNER TO postgres;

--
-- Name: trainee_allocations_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('trainee_allocations_seq', 63, true);


--
-- Name: venues_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE venues_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.venues_seq OWNER TO postgres;

--
-- Name: venues_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('venues_seq', 77, true);


--
-- Data for Name: adjudicator_allocations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY adjudicator_allocations (id, debate_id, adjudicator_id, type, created_at, updated_at) FROM stdin;
1	1	8	1	2008-07-04 18:44:01	2008-07-04 18:44:01
3	3	52	1	2008-07-04 18:44:01	2008-07-04 18:44:01
4	4	32	1	2008-07-04 18:44:01	2008-07-04 18:44:01
5	5	26	1	2008-07-04 18:44:01	2008-07-04 18:44:01
6	6	35	1	2008-07-04 18:44:01	2008-07-04 18:44:01
8	8	30	1	2008-07-04 18:44:01	2008-07-04 18:44:01
12	12	58	1	2008-07-04 18:44:01	2008-07-04 18:44:01
13	13	71	1	2008-07-04 18:44:01	2008-07-04 18:44:01
14	14	5	1	2008-07-04 18:44:02	2008-07-04 18:44:02
15	15	36	1	2008-07-04 18:44:02	2008-07-04 18:44:02
16	16	34	1	2008-07-04 18:44:02	2008-07-04 18:44:02
17	17	17	1	2008-07-04 18:44:02	2008-07-04 18:44:02
18	18	3	1	2008-07-04 18:44:02	2008-07-04 18:44:02
19	19	55	1	2008-07-04 18:44:02	2008-07-04 18:44:02
21	21	39	1	2008-07-04 18:44:02	2008-07-04 18:44:02
22	22	62	1	2008-07-04 18:44:02	2008-07-04 18:44:02
23	23	24	1	2008-07-04 18:44:02	2008-07-04 18:44:02
24	24	31	1	2008-07-04 18:44:02	2008-07-04 18:44:02
25	25	38	1	2008-07-04 18:44:02	2008-07-04 18:44:02
26	26	4	1	2008-07-04 18:44:02	2008-07-04 18:44:02
27	27	40	1	2008-07-04 18:44:02	2008-07-04 18:44:02
28	27	9	2	2008-07-04 18:44:02	2008-07-04 18:44:02
29	27	41	2	2008-07-04 18:44:02	2008-07-04 18:44:02
30	28	44	1	2008-07-04 18:44:02	2008-07-04 18:44:02
31	28	10	2	2008-07-04 18:44:02	2008-07-04 18:44:02
32	28	47	2	2008-07-04 18:44:02	2008-07-04 18:44:02
34	29	70	2	2008-07-04 18:44:02	2008-07-04 18:44:02
35	29	19	2	2008-07-04 18:44:02	2008-07-04 18:44:02
36	30	56	1	2008-07-04 18:44:02	2008-07-04 18:44:02
38	30	18	2	2008-07-04 18:44:02	2008-07-04 18:44:02
40	31	64	2	2008-07-04 18:44:02	2008-07-04 18:44:02
41	31	60	2	2008-07-04 18:44:02	2008-07-04 18:44:02
42	32	48	1	2008-07-04 18:44:02	2008-07-04 18:44:02
43	32	67	2	2008-07-04 18:44:02	2008-07-04 18:44:02
44	32	29	2	2008-07-04 18:44:02	2008-07-04 18:44:02
45	33	16	1	2008-07-04 18:44:02	2008-07-04 18:44:02
46	33	57	2	2008-07-04 18:44:02	2008-07-04 18:44:02
47	33	13	2	2008-07-04 18:44:02	2008-07-04 18:44:02
48	34	51	1	2008-07-04 18:44:02	2008-07-04 18:44:02
49	34	28	2	2008-07-04 18:44:02	2008-07-04 18:44:02
50	34	1	2	2008-07-04 18:44:02	2008-07-04 18:44:02
51	35	50	1	2008-07-04 18:44:02	2008-07-04 18:44:02
52	35	14	2	2008-07-04 18:44:02	2008-07-04 18:44:02
53	35	23	2	2008-07-04 18:44:02	2008-07-04 18:44:02
54	36	49	1	2008-07-04 18:44:02	2008-07-04 18:44:02
55	36	69	2	2008-07-04 18:44:02	2008-07-04 18:44:02
56	36	61	2	2008-07-04 18:44:02	2008-07-04 18:44:02
57	37	6	1	2008-07-04 18:44:02	2008-07-04 18:44:02
58	37	54	2	2008-07-04 18:44:02	2008-07-04 18:44:02
59	37	15	2	2008-07-04 18:44:02	2008-07-04 18:44:02
9	9	59	1	2008-07-04 18:44:01	2008-07-04 18:44:01
37	30	20	2	2008-07-04 18:44:02	2008-07-04 18:44:02
33	29	21	1	2008-07-04 18:44:02	2008-07-04 18:44:02
39	31	33	1	2008-07-04 18:44:02	2008-07-04 18:44:02
20	20	73	1	2008-07-04 18:44:02	2008-07-04 18:44:02
2	2	74	1	2008-07-04 18:44:01	2008-07-04 18:44:01
7	7	37	1	2008-07-04 18:44:01	2008-07-04 18:44:01
11	11	7	1	2008-07-04 18:44:01	2008-07-04 18:44:01
10	10	75	1	2008-07-04 18:44:01	2008-07-04 18:44:01
60	38	8	1	2008-07-29 13:17:51	2008-07-29 13:17:51
61	39	32	1	2008-07-29 13:17:51	2008-07-29 13:17:51
62	40	26	1	2008-07-29 13:17:51	2008-07-29 13:17:51
64	54	36	1	2008-07-29 13:17:51	2008-07-29 13:17:51
65	48	35	1	2008-07-29 13:17:51	2008-07-29 13:17:51
66	42	7	1	2008-07-29 13:17:51	2008-07-29 13:17:51
67	49	30	1	2008-07-29 13:17:51	2008-07-29 13:17:51
68	46	55	1	2008-07-29 13:17:51	2008-07-29 13:17:51
69	47	24	1	2008-07-29 13:17:51	2008-07-29 13:17:51
70	50	3	1	2008-07-29 13:17:51	2008-07-29 13:17:51
71	52	59	1	2008-07-29 13:17:51	2008-07-29 13:17:51
72	44	4	1	2008-07-29 13:17:51	2008-07-29 13:17:51
73	51	12	1	2008-07-29 13:17:51	2008-07-29 13:17:51
74	55	71	1	2008-07-29 13:17:51	2008-07-29 13:17:51
75	45	17	1	2008-07-29 13:17:51	2008-07-29 13:17:51
76	53	39	1	2008-07-29 13:17:51	2008-07-29 13:17:51
78	56	58	1	2008-07-29 13:17:51	2008-07-29 13:17:51
79	57	37	1	2008-07-29 13:17:51	2008-07-29 13:17:51
80	60	38	1	2008-07-29 13:17:51	2008-07-29 13:17:51
81	59	62	1	2008-07-29 13:17:51	2008-07-29 13:17:51
82	63	11	1	2008-07-29 13:17:51	2008-07-29 13:17:51
83	65	31	1	2008-07-29 13:17:51	2008-07-29 13:17:51
84	69	9	1	2008-07-29 13:17:51	2008-07-29 13:17:51
85	69	16	2	2008-07-29 13:17:51	2008-07-29 13:17:51
86	69	18	2	2008-07-29 13:17:51	2008-07-29 13:17:51
87	64	21	1	2008-07-29 13:17:51	2008-07-29 13:17:51
89	64	23	2	2008-07-29 13:17:51	2008-07-29 13:17:51
90	58	70	1	2008-07-29 13:17:51	2008-07-29 13:17:51
91	58	6	2	2008-07-29 13:17:51	2008-07-29 13:17:51
92	58	20	2	2008-07-29 13:17:51	2008-07-29 13:17:51
93	72	57	1	2008-07-29 13:17:51	2008-07-29 13:17:51
94	72	40	2	2008-07-29 13:17:51	2008-07-29 13:17:51
95	72	13	2	2008-07-29 13:17:51	2008-07-29 13:17:51
96	66	64	1	2008-07-29 13:17:51	2008-07-29 13:17:51
97	66	45	2	2008-07-29 13:17:51	2008-07-29 13:17:51
98	66	15	2	2008-07-29 13:17:51	2008-07-29 13:17:51
99	67	54	1	2008-07-29 13:17:51	2008-07-29 13:17:51
101	67	41	2	2008-07-29 13:17:51	2008-07-29 13:17:51
102	68	10	1	2008-07-29 13:17:51	2008-07-29 13:17:51
103	68	44	2	2008-07-29 13:17:51	2008-07-29 13:17:51
104	68	14	2	2008-07-29 13:17:51	2008-07-29 13:17:51
105	71	47	1	2008-07-29 13:17:51	2008-07-29 13:17:51
106	71	51	2	2008-07-29 13:17:51	2008-07-29 13:17:51
107	71	61	2	2008-07-29 13:17:51	2008-07-29 13:17:51
108	70	1	1	2008-07-29 13:17:51	2008-07-29 13:17:51
109	70	50	2	2008-07-29 13:17:51	2008-07-29 13:17:51
110	70	19	2	2008-07-29 13:17:51	2008-07-29 13:17:51
111	62	53	1	2008-07-29 13:17:51	2008-07-29 13:17:51
112	62	29	2	2008-07-29 13:17:51	2008-07-29 13:17:51
113	62	69	2	2008-07-29 13:17:51	2008-07-29 13:17:51
114	61	60	1	2008-07-29 13:17:51	2008-07-29 13:17:51
115	61	2	2	2008-07-29 13:17:51	2008-07-29 13:17:51
116	61	25	2	2008-07-29 13:17:51	2008-07-29 13:17:51
117	73	28	1	2008-07-29 13:17:51	2008-07-29 13:17:51
118	73	48	2	2008-07-29 13:17:51	2008-07-29 13:17:51
119	73	67	2	2008-07-29 13:17:51	2008-07-29 13:17:51
120	74	49	1	2008-07-29 13:17:51	2008-07-29 13:17:51
77	43	52	1	2008-07-29 13:17:51	2008-07-29 13:17:51
63	41	34	1	2008-07-29 13:17:51	2008-07-29 13:17:51
88	64	33	2	2008-07-29 13:17:51	2008-07-29 13:17:51
100	67	56	2	2008-07-29 13:17:51	2008-07-29 13:17:51
121	75	7	1	2008-07-29 16:35:20	2008-07-29 16:35:20
122	76	5	1	2008-07-29 16:35:20	2008-07-29 16:35:20
123	77	52	1	2008-07-29 16:35:20	2008-07-29 16:35:20
124	79	26	1	2008-07-29 16:35:20	2008-07-29 16:35:20
125	78	8	1	2008-07-29 16:35:20	2008-07-29 16:35:20
126	81	24	1	2008-07-29 16:35:20	2008-07-29 16:35:20
127	80	32	1	2008-07-29 16:35:20	2008-07-29 16:35:20
128	82	37	1	2008-07-29 16:35:20	2008-07-29 16:35:20
129	83	71	1	2008-07-29 16:35:20	2008-07-29 16:35:20
130	84	34	1	2008-07-29 16:35:20	2008-07-29 16:35:20
131	89	59	1	2008-07-29 16:35:20	2008-07-29 16:35:20
132	85	58	1	2008-07-29 16:35:20	2008-07-29 16:35:20
133	97	35	1	2008-07-29 16:35:20	2008-07-29 16:35:20
134	87	36	1	2008-07-29 16:35:20	2008-07-29 16:35:20
135	86	55	1	2008-07-29 16:35:20	2008-07-29 16:35:20
136	91	38	1	2008-07-29 16:35:20	2008-07-29 16:35:20
137	94	11	1	2008-07-29 16:35:20	2008-07-29 16:35:20
138	96	12	1	2008-07-29 16:35:21	2008-07-29 16:35:21
139	98	17	1	2008-07-29 16:35:21	2008-07-29 16:35:21
140	90	31	1	2008-07-29 16:35:21	2008-07-29 16:35:21
141	95	4	1	2008-07-29 16:35:21	2008-07-29 16:35:21
142	92	39	1	2008-07-29 16:35:21	2008-07-29 16:35:21
143	88	3	1	2008-07-29 16:35:21	2008-07-29 16:35:21
144	93	6	1	2008-07-29 16:35:21	2008-07-29 16:35:21
145	93	9	2	2008-07-29 16:35:21	2008-07-29 16:35:21
146	93	18	2	2008-07-29 16:35:21	2008-07-29 16:35:21
147	101	62	1	2008-07-29 16:35:21	2008-07-29 16:35:21
148	99	70	1	2008-07-29 16:35:21	2008-07-29 16:35:21
149	99	60	2	2008-07-29 16:35:21	2008-07-29 16:35:21
150	99	20	2	2008-07-29 16:35:21	2008-07-29 16:35:21
151	100	15	1	2008-07-29 16:35:21	2008-07-29 16:35:21
152	100	16	2	2008-07-29 16:35:21	2008-07-29 16:35:21
153	100	64	2	2008-07-29 16:35:21	2008-07-29 16:35:21
154	102	33	1	2008-07-29 16:35:21	2008-07-29 16:35:21
155	102	56	2	2008-07-29 16:35:21	2008-07-29 16:35:21
156	102	23	2	2008-07-29 16:35:21	2008-07-29 16:35:21
157	103	57	1	2008-07-29 16:35:21	2008-07-29 16:35:21
158	103	44	2	2008-07-29 16:35:21	2008-07-29 16:35:21
159	103	13	2	2008-07-29 16:35:21	2008-07-29 16:35:21
160	105	45	1	2008-07-29 16:35:21	2008-07-29 16:35:21
161	105	10	2	2008-07-29 16:35:21	2008-07-29 16:35:21
162	105	14	2	2008-07-29 16:35:21	2008-07-29 16:35:21
163	106	41	1	2008-07-29 16:35:21	2008-07-29 16:35:21
164	106	40	2	2008-07-29 16:35:21	2008-07-29 16:35:21
165	106	54	2	2008-07-29 16:35:21	2008-07-29 16:35:21
166	104	67	1	2008-07-29 16:35:21	2008-07-29 16:35:21
167	104	48	2	2008-07-29 16:35:21	2008-07-29 16:35:21
168	104	28	2	2008-07-29 16:35:21	2008-07-29 16:35:21
169	107	1	1	2008-07-29 16:35:21	2008-07-29 16:35:21
170	107	50	2	2008-07-29 16:35:21	2008-07-29 16:35:21
171	107	19	2	2008-07-29 16:35:21	2008-07-29 16:35:21
172	108	29	1	2008-07-29 16:35:21	2008-07-29 16:35:21
173	108	49	2	2008-07-29 16:35:21	2008-07-29 16:35:21
174	108	69	2	2008-07-29 16:35:21	2008-07-29 16:35:21
175	109	47	1	2008-07-29 16:35:21	2008-07-29 16:35:21
176	109	51	2	2008-07-29 16:35:21	2008-07-29 16:35:21
177	109	61	2	2008-07-29 16:35:21	2008-07-29 16:35:21
178	110	21	1	2008-07-29 16:35:21	2008-07-29 16:35:21
179	110	2	2	2008-07-29 16:35:21	2008-07-29 16:35:21
180	110	25	2	2008-07-29 16:35:21	2008-07-29 16:35:21
181	111	30	1	2008-07-29 16:35:21	2008-07-29 16:35:21
182	112	4	1	2008-07-29 20:46:37	2008-07-29 20:46:37
184	114	37	1	2008-07-29 20:46:37	2008-07-29 20:46:37
185	115	7	1	2008-07-29 20:46:37	2008-07-29 20:46:37
186	116	8	1	2008-07-29 20:46:37	2008-07-29 20:46:37
187	117	35	1	2008-07-29 20:46:37	2008-07-29 20:46:37
188	120	52	1	2008-07-29 20:46:37	2008-07-29 20:46:37
189	119	59	1	2008-07-29 20:46:37	2008-07-29 20:46:37
190	121	38	1	2008-07-29 20:46:37	2008-07-29 20:46:37
191	121	30	2	2008-07-29 20:46:37	2008-07-29 20:46:37
192	121	58	2	2008-07-29 20:46:37	2008-07-29 20:46:37
194	127	34	1	2008-07-29 20:46:37	2008-07-29 20:46:37
195	127	3	2	2008-07-29 20:46:37	2008-07-29 20:46:37
196	127	39	2	2008-07-29 20:46:37	2008-07-29 20:46:37
198	125	11	1	2008-07-29 20:46:37	2008-07-29 20:46:37
199	124	26	1	2008-07-29 20:46:37	2008-07-29 20:46:37
203	123	17	1	2008-07-29 20:46:37	2008-07-29 20:46:37
205	131	15	1	2008-07-29 20:46:37	2008-07-29 20:46:37
206	133	41	1	2008-07-29 20:46:37	2008-07-29 20:46:37
207	137	47	1	2008-07-29 20:46:37	2008-07-29 20:46:37
208	140	24	1	2008-07-29 20:46:37	2008-07-29 20:46:37
209	134	53	1	2008-07-29 20:46:37	2008-07-29 20:46:37
210	139	50	1	2008-07-29 20:46:37	2008-07-29 20:46:37
211	132	62	1	2008-07-29 20:46:37	2008-07-29 20:46:37
212	138	54	1	2008-07-29 20:46:37	2008-07-29 20:46:37
213	138	9	2	2008-07-29 20:46:37	2008-07-29 20:46:37
214	138	44	2	2008-07-29 20:46:37	2008-07-29 20:46:37
215	135	45	1	2008-07-29 20:46:37	2008-07-29 20:46:37
216	135	57	2	2008-07-29 20:46:37	2008-07-29 20:46:37
217	135	61	2	2008-07-29 20:46:37	2008-07-29 20:46:37
218	136	21	1	2008-07-29 20:46:37	2008-07-29 20:46:37
219	136	64	2	2008-07-29 20:46:37	2008-07-29 20:46:37
220	136	13	2	2008-07-29 20:46:37	2008-07-29 20:46:37
221	141	10	1	2008-07-29 20:46:37	2008-07-29 20:46:37
222	141	51	2	2008-07-29 20:46:37	2008-07-29 20:46:37
223	141	14	2	2008-07-29 20:46:37	2008-07-29 20:46:37
224	142	56	1	2008-07-29 20:46:37	2008-07-29 20:46:37
225	142	40	2	2008-07-29 20:46:37	2008-07-29 20:46:37
226	142	20	2	2008-07-29 20:46:37	2008-07-29 20:46:37
227	143	33	1	2008-07-29 20:46:37	2008-07-29 20:46:37
228	143	60	2	2008-07-29 20:46:37	2008-07-29 20:46:37
229	143	28	2	2008-07-29 20:46:37	2008-07-29 20:46:37
230	144	16	1	2008-07-29 20:46:37	2008-07-29 20:46:37
231	144	29	2	2008-07-29 20:46:37	2008-07-29 20:46:37
232	144	18	2	2008-07-29 20:46:37	2008-07-29 20:46:37
233	145	49	1	2008-07-29 20:46:37	2008-07-29 20:46:37
234	145	67	2	2008-07-29 20:46:37	2008-07-29 20:46:37
235	145	19	2	2008-07-29 20:46:37	2008-07-29 20:46:37
236	146	6	1	2008-07-29 20:46:38	2008-07-29 20:46:38
237	146	69	2	2008-07-29 20:46:38	2008-07-29 20:46:38
239	147	70	1	2008-07-29 20:46:38	2008-07-29 20:46:38
240	147	25	2	2008-07-29 20:46:38	2008-07-29 20:46:38
241	147	2	2	2008-07-29 20:46:38	2008-07-29 20:46:38
242	148	48	1	2008-07-29 20:46:38	2008-07-29 20:46:38
243	148	1	2	2008-07-29 20:46:38	2008-07-29 20:46:38
244	148	66	2	2008-07-29 20:46:38	2008-07-29 20:46:38
238	146	65	2	2008-07-29 20:46:38	2008-07-29 20:46:38
197	129	76	1	2008-07-29 20:46:37	2008-07-29 20:46:37
204	130	36	1	2008-07-29 20:46:37	2008-07-29 20:46:37
201	122	31	1	2008-07-29 20:46:37	2008-07-29 20:46:37
200	128	55	1	2008-07-29 20:46:37	2008-07-29 20:46:37
202	126	12	1	2008-07-29 20:46:37	2008-07-29 20:46:37
193	118	71	1	2008-07-29 20:46:37	2008-07-29 20:46:37
183	113	32	1	2008-07-29 20:46:37	2008-07-29 20:46:37
245	149	34	1	2008-07-06 13:14:05	2008-07-06 13:14:05
246	150	71	1	2008-07-06 13:14:05	2008-07-06 13:14:05
247	151	35	1	2008-07-06 13:14:05	2008-07-06 13:14:05
248	158	26	1	2008-07-06 13:14:05	2008-07-06 13:14:05
249	155	8	1	2008-07-06 13:14:05	2008-07-06 13:14:05
250	152	52	1	2008-07-06 13:14:05	2008-07-06 13:14:05
251	159	59	1	2008-07-06 13:14:05	2008-07-06 13:14:05
252	153	32	1	2008-07-06 13:14:05	2008-07-06 13:14:05
253	154	37	1	2008-07-06 13:14:05	2008-07-06 13:14:05
254	157	24	1	2008-07-06 13:14:05	2008-07-06 13:14:05
255	156	7	1	2008-07-06 13:14:05	2008-07-06 13:14:05
256	160	12	1	2008-07-06 13:14:05	2008-07-06 13:14:05
257	161	38	1	2008-07-06 13:14:05	2008-07-06 13:14:05
258	163	4	1	2008-07-06 13:14:05	2008-07-06 13:14:05
259	164	36	1	2008-07-06 13:14:05	2008-07-06 13:14:05
260	162	11	1	2008-07-06 13:14:05	2008-07-06 13:14:05
261	165	17	1	2008-07-06 13:14:05	2008-07-06 13:14:05
262	166	55	1	2008-07-06 13:14:05	2008-07-06 13:14:05
263	167	31	1	2008-07-06 13:14:05	2008-07-06 13:14:05
264	170	41	1	2008-07-06 13:14:05	2008-07-06 13:14:05
265	168	39	1	2008-07-06 13:14:05	2008-07-06 13:14:05
266	169	30	1	2008-07-06 13:14:05	2008-07-06 13:14:05
268	169	57	2	2008-07-06 13:14:05	2008-07-06 13:14:05
269	171	67	1	2008-07-06 13:14:05	2008-07-06 13:14:05
270	171	14	2	2008-07-06 13:14:05	2008-07-06 13:14:05
271	171	61	2	2008-07-06 13:14:05	2008-07-06 13:14:05
272	172	3	1	2008-07-06 13:14:05	2008-07-06 13:14:05
273	172	60	2	2008-07-06 13:14:05	2008-07-06 13:14:05
274	172	2	2	2008-07-06 13:14:05	2008-07-06 13:14:05
275	173	58	1	2008-07-06 13:14:05	2008-07-06 13:14:05
276	174	53	1	2008-07-06 13:14:05	2008-07-06 13:14:05
277	175	33	1	2008-07-06 13:14:05	2008-07-06 13:14:05
278	181	16	1	2008-07-06 13:14:05	2008-07-06 13:14:05
279	181	56	2	2008-07-06 13:14:05	2008-07-06 13:14:05
280	181	21	2	2008-07-06 13:14:05	2008-07-06 13:14:05
282	177	45	2	2008-07-06 13:14:05	2008-07-06 13:14:05
283	177	70	2	2008-07-06 13:14:05	2008-07-06 13:14:05
284	178	40	1	2008-07-06 13:14:05	2008-07-06 13:14:05
285	178	64	2	2008-07-06 13:14:06	2008-07-06 13:14:06
286	178	1	2	2008-07-06 13:14:06	2008-07-06 13:14:06
287	180	62	1	2008-07-06 13:14:06	2008-07-06 13:14:06
288	180	20	2	2008-07-06 13:14:06	2008-07-06 13:14:06
289	180	10	2	2008-07-06 13:14:06	2008-07-06 13:14:06
292	179	9	2	2008-07-06 13:14:06	2008-07-06 13:14:06
293	176	50	1	2008-07-06 13:14:06	2008-07-06 13:14:06
294	176	47	2	2008-07-06 13:14:06	2008-07-06 13:14:06
295	176	69	2	2008-07-06 13:14:06	2008-07-06 13:14:06
296	182	49	1	2008-07-06 13:14:06	2008-07-06 13:14:06
297	182	28	2	2008-07-06 13:14:06	2008-07-06 13:14:06
298	182	48	2	2008-07-06 13:14:06	2008-07-06 13:14:06
299	183	51	1	2008-07-06 13:14:06	2008-07-06 13:14:06
300	183	29	2	2008-07-06 13:14:06	2008-07-06 13:14:06
301	183	18	2	2008-07-06 13:14:06	2008-07-06 13:14:06
302	184	19	1	2008-07-06 13:14:06	2008-07-06 13:14:06
303	184	66	2	2008-07-06 13:14:06	2008-07-06 13:14:06
304	184	25	2	2008-07-06 13:14:06	2008-07-06 13:14:06
305	185	13	1	2008-07-06 13:14:06	2008-07-06 13:14:06
306	185	22	2	2008-07-06 13:14:06	2008-07-06 13:14:06
307	185	63	2	2008-07-06 13:14:06	2008-07-06 13:14:06
267	169	54	2	2008-07-06 13:14:05	2008-07-06 13:14:05
291	179	15	2	2008-07-06 13:14:06	2008-07-06 13:14:06
290	179	44	1	2008-07-06 13:14:06	2008-07-06 13:14:06
281	177	6	1	2008-07-06 13:14:05	2008-07-06 13:14:05
437	149	5	2	2008-07-06 14:36:29.641106	2008-07-06 14:36:29.641106
438	149	76	2	2008-07-06 14:36:54.399551	2008-07-06 14:36:54.399551
311	215	38	1	2008-07-06 18:58:16	2008-07-06 18:58:16
312	216	11	1	2008-07-06 18:58:16	2008-07-06 18:58:16
313	216	3	2	2008-07-06 18:58:16	2008-07-06 18:58:16
314	216	33	2	2008-07-06 18:58:16	2008-07-06 18:58:16
315	217	17	1	2008-07-06 18:58:16	2008-07-06 18:58:16
316	218	71	1	2008-07-06 18:58:16	2008-07-06 18:58:16
317	219	34	1	2008-07-06 18:58:16	2008-07-06 18:58:16
318	220	4	1	2008-07-06 18:58:16	2008-07-06 18:58:16
319	221	59	1	2008-07-06 18:58:16	2008-07-06 18:58:16
320	222	37	1	2008-07-06 18:58:16	2008-07-06 18:58:16
321	223	35	1	2008-07-06 18:58:16	2008-07-06 18:58:16
322	224	55	1	2008-07-06 18:58:16	2008-07-06 18:58:16
323	225	24	1	2008-07-06 18:58:16	2008-07-06 18:58:16
324	225	30	2	2008-07-06 18:58:16	2008-07-06 18:58:16
325	225	62	2	2008-07-06 18:58:16	2008-07-06 18:58:16
330	229	8	1	2008-07-06 18:58:16	2008-07-06 18:58:16
331	229	39	2	2008-07-06 18:58:16	2008-07-06 18:58:16
332	229	44	2	2008-07-06 18:58:16	2008-07-06 18:58:16
335	231	52	1	2008-07-06 18:58:17	2008-07-06 18:58:17
336	232	12	1	2008-07-06 18:58:17	2008-07-06 18:58:17
337	232	54	2	2008-07-06 18:58:17	2008-07-06 18:58:17
338	232	56	2	2008-07-06 18:58:17	2008-07-06 18:58:17
339	235	76	1	2008-07-06 18:58:17	2008-07-06 18:58:17
340	236	31	1	2008-07-06 18:58:17	2008-07-06 18:58:17
341	237	36	1	2008-07-06 18:58:17	2008-07-06 18:58:17
342	233	70	1	2008-07-06 18:58:17	2008-07-06 18:58:17
343	234	6	1	2008-07-06 18:58:17	2008-07-06 18:58:17
344	238	15	1	2008-07-06 18:58:17	2008-07-06 18:58:17
345	239	67	1	2008-07-06 18:58:17	2008-07-06 18:58:17
346	240	49	1	2008-07-06 18:58:17	2008-07-06 18:58:17
347	241	21	1	2008-07-06 18:58:17	2008-07-06 18:58:17
348	242	40	1	2008-07-06 18:58:17	2008-07-06 18:58:17
349	243	41	1	2008-07-06 18:58:17	2008-07-06 18:58:17
350	243	47	2	2008-07-06 18:58:17	2008-07-06 18:58:17
351	243	13	2	2008-07-06 18:58:17	2008-07-06 18:58:17
353	244	64	2	2008-07-06 18:58:17	2008-07-06 18:58:17
354	244	50	2	2008-07-06 18:58:17	2008-07-06 18:58:17
356	245	9	2	2008-07-06 18:58:17	2008-07-06 18:58:17
357	245	20	2	2008-07-06 18:58:17	2008-07-06 18:58:17
358	246	16	1	2008-07-06 18:58:17	2008-07-06 18:58:17
359	246	63	2	2008-07-06 18:58:17	2008-07-06 18:58:17
360	246	22	2	2008-07-06 18:58:17	2008-07-06 18:58:17
361	247	57	1	2008-07-06 18:58:17	2008-07-06 18:58:17
362	247	48	2	2008-07-06 18:58:17	2008-07-06 18:58:17
363	247	18	2	2008-07-06 18:58:17	2008-07-06 18:58:17
364	248	1	1	2008-07-06 18:58:17	2008-07-06 18:58:17
365	248	10	2	2008-07-06 18:58:17	2008-07-06 18:58:17
366	248	28	2	2008-07-06 18:58:17	2008-07-06 18:58:17
367	249	19	1	2008-07-06 18:58:17	2008-07-06 18:58:17
368	249	65	2	2008-07-06 18:58:17	2008-07-06 18:58:17
369	249	68	2	2008-07-06 18:58:17	2008-07-06 18:58:17
370	250	60	1	2008-07-06 18:58:17	2008-07-06 18:58:17
371	250	66	2	2008-07-06 18:58:17	2008-07-06 18:58:17
372	250	2	2	2008-07-06 18:58:17	2008-07-06 18:58:17
373	251	14	1	2008-07-06 18:58:17	2008-07-06 18:58:17
374	251	69	2	2008-07-06 18:58:17	2008-07-06 18:58:17
375	251	29	2	2008-07-06 18:58:17	2008-07-06 18:58:17
355	245	45	1	2008-07-06 18:58:17	2008-07-06 18:58:17
352	244	51	1	2008-07-06 18:58:17	2008-07-06 18:58:17
439	241	25	2	2008-07-07 10:08:01.95536	2008-07-07 10:08:01.95536
440	241	61	2	2008-07-07 10:08:10.954253	2008-07-07 10:08:10.954253
326	228	5	1	2008-07-06 18:58:16	2008-07-06 18:58:16
327	228	53	2	2008-07-06 18:58:16	2008-07-06 18:58:16
328	228	58	2	2008-07-06 18:58:16	2008-07-06 18:58:16
329	226	7	1	2008-07-06 18:58:16	2008-07-06 18:58:16
334	227	26	1	2008-07-06 18:58:17	2008-07-06 18:58:17
333	230	32	1	2008-07-06 18:58:16	2008-07-06 18:58:16
441	284	34	1	2008-07-07 12:50:28	2008-07-07 12:50:28
442	282	59	1	2008-07-07 12:50:28	2008-07-07 12:50:28
443	283	8	1	2008-07-07 12:50:28	2008-07-07 12:50:28
445	285	38	1	2008-07-07 12:50:28	2008-07-07 12:50:28
446	289	37	1	2008-07-07 12:50:28	2008-07-07 12:50:28
447	288	52	1	2008-07-07 12:50:28	2008-07-07 12:50:28
448	287	11	1	2008-07-07 12:50:28	2008-07-07 12:50:28
449	293	32	1	2008-07-07 12:50:28	2008-07-07 12:50:28
451	290	26	1	2008-07-07 12:50:28	2008-07-07 12:50:28
453	281	33	1	2008-07-07 12:50:28	2008-07-07 12:50:28
454	281	3	2	2008-07-07 12:50:28	2008-07-07 12:50:28
455	281	70	2	2008-07-07 12:50:28	2008-07-07 12:50:28
456	295	5	1	2008-07-07 12:50:28	2008-07-07 12:50:28
457	298	12	1	2008-07-07 12:50:28	2008-07-07 12:50:28
458	300	39	1	2008-07-07 12:50:28	2008-07-07 12:50:28
460	294	55	1	2008-07-07 12:50:28	2008-07-07 12:50:28
461	297	17	1	2008-07-07 12:50:28	2008-07-07 12:50:28
462	297	15	2	2008-07-07 12:50:28	2008-07-07 12:50:28
463	297	14	2	2008-07-07 12:50:28	2008-07-07 12:50:28
464	296	31	1	2008-07-07 12:50:28	2008-07-07 12:50:28
465	296	56	2	2008-07-07 12:50:28	2008-07-07 12:50:28
466	296	40	2	2008-07-07 12:50:28	2008-07-07 12:50:28
467	301	24	1	2008-07-07 12:50:28	2008-07-07 12:50:28
468	301	47	2	2008-07-07 12:50:28	2008-07-07 12:50:28
469	301	45	2	2008-07-07 12:50:28	2008-07-07 12:50:28
470	302	36	1	2008-07-07 12:50:28	2008-07-07 12:50:28
471	302	30	2	2008-07-07 12:50:28	2008-07-07 12:50:28
472	302	57	2	2008-07-07 12:50:28	2008-07-07 12:50:28
473	303	58	1	2008-07-07 12:50:28	2008-07-07 12:50:28
474	303	6	2	2008-07-07 12:50:28	2008-07-07 12:50:28
475	303	21	2	2008-07-07 12:50:28	2008-07-07 12:50:28
476	304	62	1	2008-07-07 12:50:28	2008-07-07 12:50:28
477	304	54	2	2008-07-07 12:50:28	2008-07-07 12:50:28
478	304	44	2	2008-07-07 12:50:29	2008-07-07 12:50:29
479	305	53	1	2008-07-07 12:50:29	2008-07-07 12:50:29
480	305	67	2	2008-07-07 12:50:29	2008-07-07 12:50:29
481	305	49	2	2008-07-07 12:50:29	2008-07-07 12:50:29
482	306	48	1	2008-07-07 12:50:29	2008-07-07 12:50:29
483	306	63	2	2008-07-07 12:50:29	2008-07-07 12:50:29
484	306	65	2	2008-07-07 12:50:29	2008-07-07 12:50:29
485	307	41	1	2008-07-07 12:50:29	2008-07-07 12:50:29
486	307	28	2	2008-07-07 12:50:29	2008-07-07 12:50:29
487	307	29	2	2008-07-07 12:50:29	2008-07-07 12:50:29
488	308	9	1	2008-07-07 12:50:29	2008-07-07 12:50:29
489	308	25	2	2008-07-07 12:50:29	2008-07-07 12:50:29
490	308	22	2	2008-07-07 12:50:29	2008-07-07 12:50:29
492	309	10	2	2008-07-07 12:50:29	2008-07-07 12:50:29
493	309	19	2	2008-07-07 12:50:29	2008-07-07 12:50:29
494	310	20	1	2008-07-07 12:50:29	2008-07-07 12:50:29
495	310	66	2	2008-07-07 12:50:29	2008-07-07 12:50:29
496	310	60	2	2008-07-07 12:50:29	2008-07-07 12:50:29
498	312	43	2	2008-07-07 12:50:29	2008-07-07 12:50:29
499	312	61	2	2008-07-07 12:50:29	2008-07-07 12:50:29
500	311	50	1	2008-07-07 12:50:29	2008-07-07 12:50:29
501	311	68	2	2008-07-07 12:50:29	2008-07-07 12:50:29
502	311	2	2	2008-07-07 12:50:29	2008-07-07 12:50:29
503	313	51	1	2008-07-07 12:50:29	2008-07-07 12:50:29
504	314	16	1	2008-07-07 12:50:29	2008-07-07 12:50:29
505	315	69	1	2008-07-07 12:50:29	2008-07-07 12:50:29
506	316	1	1	2008-07-07 12:50:29	2008-07-07 12:50:29
507	317	64	1	2008-07-07 12:50:29	2008-07-07 12:50:29
444	286	71	1	2008-07-07 12:50:28	2008-07-07 12:50:28
459	299	35	1	2008-07-07 12:50:28	2008-07-07 12:50:28
452	291	7	1	2008-07-07 12:50:28	2008-07-07 12:50:28
450	292	4	1	2008-07-07 12:50:28	2008-07-07 12:50:28
491	309	13	1	2008-07-07 12:50:29	2008-07-07 12:50:29
497	312	18	1	2008-07-07 12:50:29	2008-07-07 12:50:29
508	320	26	1	2008-07-07 16:18:38	2008-07-07 16:18:38
509	322	52	1	2008-07-07 16:18:38	2008-07-07 16:18:38
510	321	11	1	2008-07-07 16:18:38	2008-07-07 16:18:38
511	323	71	1	2008-07-07 16:18:38	2008-07-07 16:18:38
512	324	32	1	2008-07-07 16:18:38	2008-07-07 16:18:38
513	326	7	1	2008-07-07 16:18:38	2008-07-07 16:18:38
514	325	37	1	2008-07-07 16:18:38	2008-07-07 16:18:38
515	331	36	1	2008-07-07 16:18:38	2008-07-07 16:18:38
516	328	59	1	2008-07-07 16:18:38	2008-07-07 16:18:38
517	327	55	1	2008-07-07 16:18:38	2008-07-07 16:18:38
518	327	58	2	2008-07-07 16:18:38	2008-07-07 16:18:38
519	327	53	2	2008-07-07 16:18:38	2008-07-07 16:18:38
520	330	38	1	2008-07-07 16:18:38	2008-07-07 16:18:38
521	333	70	1	2008-07-07 16:18:38	2008-07-07 16:18:38
522	333	20	2	2008-07-07 16:18:38	2008-07-07 16:18:38
523	333	51	2	2008-07-07 16:18:38	2008-07-07 16:18:38
524	335	33	1	2008-07-07 16:18:38	2008-07-07 16:18:38
525	335	13	2	2008-07-07 16:18:38	2008-07-07 16:18:38
526	335	28	2	2008-07-07 16:18:38	2008-07-07 16:18:38
527	329	34	1	2008-07-07 16:18:38	2008-07-07 16:18:38
528	329	8	2	2008-07-07 16:18:38	2008-07-07 16:18:38
529	329	31	2	2008-07-07 16:18:38	2008-07-07 16:18:38
530	318	4	1	2008-07-07 16:18:38	2008-07-07 16:18:38
531	318	39	2	2008-07-07 16:18:38	2008-07-07 16:18:38
532	318	17	2	2008-07-07 16:18:38	2008-07-07 16:18:38
533	332	56	1	2008-07-07 16:18:38	2008-07-07 16:18:38
534	332	64	2	2008-07-07 16:18:38	2008-07-07 16:18:38
535	332	14	2	2008-07-07 16:18:38	2008-07-07 16:18:38
536	334	62	1	2008-07-07 16:18:38	2008-07-07 16:18:38
537	334	19	2	2008-07-07 16:18:38	2008-07-07 16:18:38
538	334	61	2	2008-07-07 16:18:38	2008-07-07 16:18:38
539	336	3	1	2008-07-07 16:18:38	2008-07-07 16:18:38
540	336	69	2	2008-07-07 16:18:38	2008-07-07 16:18:38
541	336	10	2	2008-07-07 16:18:38	2008-07-07 16:18:38
542	319	35	1	2008-07-07 16:18:38	2008-07-07 16:18:38
543	319	24	2	2008-07-07 16:18:38	2008-07-07 16:18:38
544	319	12	2	2008-07-07 16:18:38	2008-07-07 16:18:38
545	337	44	1	2008-07-07 16:18:38	2008-07-07 16:18:38
546	337	18	2	2008-07-07 16:18:38	2008-07-07 16:18:38
547	337	2	2	2008-07-07 16:18:38	2008-07-07 16:18:38
548	338	45	1	2008-07-07 16:18:38	2008-07-07 16:18:38
549	338	48	2	2008-07-07 16:18:38	2008-07-07 16:18:38
550	338	66	2	2008-07-07 16:18:38	2008-07-07 16:18:38
551	339	54	1	2008-07-07 16:18:38	2008-07-07 16:18:38
552	339	25	2	2008-07-07 16:18:38	2008-07-07 16:18:38
553	339	68	2	2008-07-07 16:18:38	2008-07-07 16:18:38
554	342	57	1	2008-07-07 16:18:38	2008-07-07 16:18:38
555	342	29	2	2008-07-07 16:18:38	2008-07-07 16:18:38
556	342	63	2	2008-07-07 16:18:38	2008-07-07 16:18:38
557	341	30	1	2008-07-07 16:18:38	2008-07-07 16:18:38
558	341	22	2	2008-07-07 16:18:38	2008-07-07 16:18:38
559	341	43	2	2008-07-07 16:18:38	2008-07-07 16:18:38
560	343	65	1	2008-07-07 16:18:38	2008-07-07 16:18:38
561	340	6	1	2008-07-07 16:18:38	2008-07-07 16:18:38
562	344	40	1	2008-07-07 16:18:38	2008-07-07 16:18:38
563	345	16	1	2008-07-07 16:18:38	2008-07-07 16:18:38
564	346	21	1	2008-07-07 16:18:38	2008-07-07 16:18:38
565	347	67	1	2008-07-07 16:18:38	2008-07-07 16:18:38
566	348	50	1	2008-07-07 16:18:38	2008-07-07 16:18:38
567	349	1	1	2008-07-07 16:18:38	2008-07-07 16:18:38
568	350	41	1	2008-07-07 16:18:38	2008-07-07 16:18:38
569	351	15	1	2008-07-07 16:18:38	2008-07-07 16:18:38
570	352	49	1	2008-07-07 16:18:38	2008-07-07 16:18:38
571	353	9	1	2008-07-07 16:18:39	2008-07-07 16:18:39
572	354	60	1	2008-07-07 16:18:39	2008-07-07 16:18:39
\.


--
-- Data for Name: adjudicator_conflicts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY adjudicator_conflicts (id, team_id, adjudicator_id, created_at, updated_at) FROM stdin;
1	1	1	2008-07-04 17:20:52	2008-07-04 17:20:52
2	2	1	2008-07-04 17:20:52	2008-07-04 17:20:52
3	1	2	2008-07-04 17:20:53	2008-07-04 17:20:53
4	2	2	2008-07-04 17:20:53	2008-07-04 17:20:53
5	3	3	2008-07-04 17:20:53	2008-07-04 17:20:53
6	4	3	2008-07-04 17:20:53	2008-07-04 17:20:53
7	5	3	2008-07-04 17:20:53	2008-07-04 17:20:53
8	6	3	2008-07-04 17:20:53	2008-07-04 17:20:53
9	7	3	2008-07-04 17:20:53	2008-07-04 17:20:53
10	3	4	2008-07-04 17:20:53	2008-07-04 17:20:53
11	4	4	2008-07-04 17:20:53	2008-07-04 17:20:53
12	5	4	2008-07-04 17:20:53	2008-07-04 17:20:53
13	6	4	2008-07-04 17:20:53	2008-07-04 17:20:53
14	7	4	2008-07-04 17:20:53	2008-07-04 17:20:53
15	3	5	2008-07-04 17:20:53	2008-07-04 17:20:53
16	4	5	2008-07-04 17:20:53	2008-07-04 17:20:53
17	5	5	2008-07-04 17:20:53	2008-07-04 17:20:53
18	6	5	2008-07-04 17:20:53	2008-07-04 17:20:53
19	7	5	2008-07-04 17:20:53	2008-07-04 17:20:53
20	3	6	2008-07-04 17:20:53	2008-07-04 17:20:53
21	4	6	2008-07-04 17:20:53	2008-07-04 17:20:53
22	5	6	2008-07-04 17:20:53	2008-07-04 17:20:53
23	6	6	2008-07-04 17:20:53	2008-07-04 17:20:53
24	7	6	2008-07-04 17:20:53	2008-07-04 17:20:53
25	3	7	2008-07-04 17:20:53	2008-07-04 17:20:53
26	4	7	2008-07-04 17:20:53	2008-07-04 17:20:53
27	5	7	2008-07-04 17:20:53	2008-07-04 17:20:53
28	6	7	2008-07-04 17:20:53	2008-07-04 17:20:53
29	7	7	2008-07-04 17:20:53	2008-07-04 17:20:53
30	3	8	2008-07-04 17:20:53	2008-07-04 17:20:53
31	4	8	2008-07-04 17:20:53	2008-07-04 17:20:53
32	5	8	2008-07-04 17:20:53	2008-07-04 17:20:53
33	6	8	2008-07-04 17:20:53	2008-07-04 17:20:53
34	7	8	2008-07-04 17:20:53	2008-07-04 17:20:53
35	9	9	2008-07-04 17:20:54	2008-07-04 17:20:54
36	10	9	2008-07-04 17:20:54	2008-07-04 17:20:54
37	11	9	2008-07-04 17:20:54	2008-07-04 17:20:54
38	9	10	2008-07-04 17:20:54	2008-07-04 17:20:54
39	10	10	2008-07-04 17:20:54	2008-07-04 17:20:54
40	11	10	2008-07-04 17:20:54	2008-07-04 17:20:54
41	12	11	2008-07-04 17:20:54	2008-07-04 17:20:54
42	13	11	2008-07-04 17:20:54	2008-07-04 17:20:54
43	14	11	2008-07-04 17:20:54	2008-07-04 17:20:54
44	12	12	2008-07-04 17:20:54	2008-07-04 17:20:54
45	13	12	2008-07-04 17:20:54	2008-07-04 17:20:54
46	14	12	2008-07-04 17:20:54	2008-07-04 17:20:54
47	15	13	2008-07-04 17:20:55	2008-07-04 17:20:55
48	16	13	2008-07-04 17:20:55	2008-07-04 17:20:55
49	15	14	2008-07-04 17:20:55	2008-07-04 17:20:55
50	16	14	2008-07-04 17:20:55	2008-07-04 17:20:55
51	18	15	2008-07-04 17:20:55	2008-07-04 17:20:55
52	18	16	2008-07-04 17:20:55	2008-07-04 17:20:55
53	20	17	2008-07-04 17:20:56	2008-07-04 17:20:56
54	21	17	2008-07-04 17:20:56	2008-07-04 17:20:56
55	22	17	2008-07-04 17:20:56	2008-07-04 17:20:56
56	20	18	2008-07-04 17:20:56	2008-07-04 17:20:56
57	21	18	2008-07-04 17:20:56	2008-07-04 17:20:56
58	22	18	2008-07-04 17:20:56	2008-07-04 17:20:56
59	24	24	2008-07-04 17:20:56	2008-07-04 17:20:56
60	25	24	2008-07-04 17:20:56	2008-07-04 17:20:56
61	26	24	2008-07-04 17:20:56	2008-07-04 17:20:56
62	24	25	2008-07-04 17:20:56	2008-07-04 17:20:56
63	25	25	2008-07-04 17:20:56	2008-07-04 17:20:56
64	26	25	2008-07-04 17:20:56	2008-07-04 17:20:56
65	24	26	2008-07-04 17:20:56	2008-07-04 17:20:56
66	25	26	2008-07-04 17:20:56	2008-07-04 17:20:56
67	26	26	2008-07-04 17:20:56	2008-07-04 17:20:56
71	27	28	2008-07-04 17:20:57	2008-07-04 17:20:57
72	28	29	2008-07-04 17:20:57	2008-07-04 17:20:57
73	29	29	2008-07-04 17:20:57	2008-07-04 17:20:57
74	30	30	2008-07-04 17:20:57	2008-07-04 17:20:57
75	31	30	2008-07-04 17:20:57	2008-07-04 17:20:57
76	32	30	2008-07-04 17:20:57	2008-07-04 17:20:57
77	30	31	2008-07-04 17:20:57	2008-07-04 17:20:57
78	31	31	2008-07-04 17:20:57	2008-07-04 17:20:57
79	32	31	2008-07-04 17:20:57	2008-07-04 17:20:57
80	30	32	2008-07-04 17:20:57	2008-07-04 17:20:57
81	31	32	2008-07-04 17:20:57	2008-07-04 17:20:57
82	32	32	2008-07-04 17:20:57	2008-07-04 17:20:57
83	33	33	2008-07-04 17:20:58	2008-07-04 17:20:58
84	34	33	2008-07-04 17:20:58	2008-07-04 17:20:58
85	35	33	2008-07-04 17:20:58	2008-07-04 17:20:58
86	36	33	2008-07-04 17:20:58	2008-07-04 17:20:58
87	37	33	2008-07-04 17:20:58	2008-07-04 17:20:58
88	33	34	2008-07-04 17:20:58	2008-07-04 17:20:58
89	34	34	2008-07-04 17:20:58	2008-07-04 17:20:58
90	35	34	2008-07-04 17:20:58	2008-07-04 17:20:58
91	36	34	2008-07-04 17:20:58	2008-07-04 17:20:58
92	37	34	2008-07-04 17:20:58	2008-07-04 17:20:58
93	33	35	2008-07-04 17:20:58	2008-07-04 17:20:58
94	34	35	2008-07-04 17:20:58	2008-07-04 17:20:58
95	35	35	2008-07-04 17:20:58	2008-07-04 17:20:58
96	36	35	2008-07-04 17:20:58	2008-07-04 17:20:58
97	37	35	2008-07-04 17:20:58	2008-07-04 17:20:58
98	33	36	2008-07-04 17:20:58	2008-07-04 17:20:58
99	34	36	2008-07-04 17:20:58	2008-07-04 17:20:58
100	35	36	2008-07-04 17:20:58	2008-07-04 17:20:58
101	36	36	2008-07-04 17:20:58	2008-07-04 17:20:58
102	37	36	2008-07-04 17:20:58	2008-07-04 17:20:58
103	33	37	2008-07-04 17:20:58	2008-07-04 17:20:58
104	34	37	2008-07-04 17:20:58	2008-07-04 17:20:58
105	35	37	2008-07-04 17:20:58	2008-07-04 17:20:58
106	36	37	2008-07-04 17:20:58	2008-07-04 17:20:58
107	37	37	2008-07-04 17:20:58	2008-07-04 17:20:58
108	33	38	2008-07-04 17:20:58	2008-07-04 17:20:58
109	34	38	2008-07-04 17:20:58	2008-07-04 17:20:58
110	35	38	2008-07-04 17:20:58	2008-07-04 17:20:58
111	36	38	2008-07-04 17:20:58	2008-07-04 17:20:58
112	37	38	2008-07-04 17:20:58	2008-07-04 17:20:58
113	33	39	2008-07-04 17:20:58	2008-07-04 17:20:58
114	34	39	2008-07-04 17:20:58	2008-07-04 17:20:58
115	35	39	2008-07-04 17:20:58	2008-07-04 17:20:58
116	36	39	2008-07-04 17:20:58	2008-07-04 17:20:58
117	37	39	2008-07-04 17:20:58	2008-07-04 17:20:58
118	39	40	2008-07-04 17:20:59	2008-07-04 17:20:59
119	40	40	2008-07-04 17:20:59	2008-07-04 17:20:59
120	41	40	2008-07-04 17:20:59	2008-07-04 17:20:59
121	39	41	2008-07-04 17:20:59	2008-07-04 17:20:59
122	40	41	2008-07-04 17:20:59	2008-07-04 17:20:59
123	41	41	2008-07-04 17:20:59	2008-07-04 17:20:59
127	43	43	2008-07-04 17:20:59	2008-07-04 17:20:59
128	44	43	2008-07-04 17:20:59	2008-07-04 17:20:59
129	43	44	2008-07-04 17:20:59	2008-07-04 17:20:59
130	44	44	2008-07-04 17:20:59	2008-07-04 17:20:59
131	46	46	2008-07-04 17:21:00	2008-07-04 17:21:00
132	47	47	2008-07-04 17:21:00	2008-07-04 17:21:00
133	50	48	2008-07-04 17:21:01	2008-07-04 17:21:01
134	51	48	2008-07-04 17:21:01	2008-07-04 17:21:01
135	53	49	2008-07-04 17:21:01	2008-07-04 17:21:01
136	54	49	2008-07-04 17:21:01	2008-07-04 17:21:01
137	53	50	2008-07-04 17:21:01	2008-07-04 17:21:01
138	54	50	2008-07-04 17:21:01	2008-07-04 17:21:01
139	53	51	2008-07-04 17:21:01	2008-07-04 17:21:01
140	54	51	2008-07-04 17:21:01	2008-07-04 17:21:01
141	53	52	2008-07-04 17:21:01	2008-07-04 17:21:01
142	54	52	2008-07-04 17:21:01	2008-07-04 17:21:01
143	55	53	2008-07-04 17:21:02	2008-07-04 17:21:02
144	56	53	2008-07-04 17:21:02	2008-07-04 17:21:02
145	57	54	2008-07-04 17:21:02	2008-07-04 17:21:02
146	58	54	2008-07-04 17:21:02	2008-07-04 17:21:02
147	59	54	2008-07-04 17:21:02	2008-07-04 17:21:02
148	60	54	2008-07-04 17:21:02	2008-07-04 17:21:02
149	61	54	2008-07-04 17:21:02	2008-07-04 17:21:02
150	62	54	2008-07-04 17:21:02	2008-07-04 17:21:02
151	57	55	2008-07-04 17:21:02	2008-07-04 17:21:02
152	58	55	2008-07-04 17:21:02	2008-07-04 17:21:02
153	59	55	2008-07-04 17:21:02	2008-07-04 17:21:02
154	60	55	2008-07-04 17:21:02	2008-07-04 17:21:02
155	61	55	2008-07-04 17:21:02	2008-07-04 17:21:02
156	62	55	2008-07-04 17:21:02	2008-07-04 17:21:02
157	57	56	2008-07-04 17:21:02	2008-07-04 17:21:02
158	58	56	2008-07-04 17:21:02	2008-07-04 17:21:02
159	59	56	2008-07-04 17:21:02	2008-07-04 17:21:02
160	60	56	2008-07-04 17:21:02	2008-07-04 17:21:02
161	61	56	2008-07-04 17:21:02	2008-07-04 17:21:02
162	62	56	2008-07-04 17:21:02	2008-07-04 17:21:02
163	57	57	2008-07-04 17:21:02	2008-07-04 17:21:02
164	58	57	2008-07-04 17:21:02	2008-07-04 17:21:02
165	59	57	2008-07-04 17:21:02	2008-07-04 17:21:02
166	60	57	2008-07-04 17:21:02	2008-07-04 17:21:02
167	61	57	2008-07-04 17:21:02	2008-07-04 17:21:02
168	62	57	2008-07-04 17:21:02	2008-07-04 17:21:02
169	57	58	2008-07-04 17:21:02	2008-07-04 17:21:02
170	58	58	2008-07-04 17:21:02	2008-07-04 17:21:02
171	59	58	2008-07-04 17:21:02	2008-07-04 17:21:02
172	60	58	2008-07-04 17:21:02	2008-07-04 17:21:02
173	61	58	2008-07-04 17:21:02	2008-07-04 17:21:02
174	62	58	2008-07-04 17:21:02	2008-07-04 17:21:02
175	57	59	2008-07-04 17:21:02	2008-07-04 17:21:02
176	58	59	2008-07-04 17:21:02	2008-07-04 17:21:02
177	59	59	2008-07-04 17:21:02	2008-07-04 17:21:02
178	60	59	2008-07-04 17:21:03	2008-07-04 17:21:03
179	61	59	2008-07-04 17:21:03	2008-07-04 17:21:03
180	62	59	2008-07-04 17:21:03	2008-07-04 17:21:03
181	63	60	2008-07-04 17:21:03	2008-07-04 17:21:03
182	64	60	2008-07-04 17:21:03	2008-07-04 17:21:03
183	65	60	2008-07-04 17:21:03	2008-07-04 17:21:03
184	66	60	2008-07-04 17:21:03	2008-07-04 17:21:03
185	63	61	2008-07-04 17:21:03	2008-07-04 17:21:03
186	64	61	2008-07-04 17:21:03	2008-07-04 17:21:03
187	65	61	2008-07-04 17:21:03	2008-07-04 17:21:03
188	66	61	2008-07-04 17:21:03	2008-07-04 17:21:03
189	63	62	2008-07-04 17:21:03	2008-07-04 17:21:03
190	64	62	2008-07-04 17:21:03	2008-07-04 17:21:03
191	65	62	2008-07-04 17:21:03	2008-07-04 17:21:03
192	66	62	2008-07-04 17:21:03	2008-07-04 17:21:03
193	67	65	2008-07-04 17:21:03	2008-07-04 17:21:03
194	68	65	2008-07-04 17:21:03	2008-07-04 17:21:03
195	67	66	2008-07-04 17:21:03	2008-07-04 17:21:03
196	68	66	2008-07-04 17:21:03	2008-07-04 17:21:03
197	70	68	2008-07-04 17:21:04	2008-07-04 17:21:04
198	71	69	2008-07-04 17:21:04	2008-07-04 17:21:04
199	72	69	2008-07-04 17:21:04	2008-07-04 17:21:04
200	73	69	2008-07-04 17:21:04	2008-07-04 17:21:04
201	71	70	2008-07-04 17:21:04	2008-07-04 17:21:04
202	72	70	2008-07-04 17:21:04	2008-07-04 17:21:04
203	73	70	2008-07-04 17:21:04	2008-07-04 17:21:04
204	71	71	2008-07-04 17:21:04	2008-07-04 17:21:04
205	72	71	2008-07-04 17:21:04	2008-07-04 17:21:04
206	73	71	2008-07-04 17:21:04	2008-07-04 17:21:04
207	74	72	2008-07-04 17:21:05	2008-07-04 17:21:05
208	24	11	2008-07-04 17:27:09	2008-07-04 17:27:09
209	25	11	2008-07-04 17:27:16	2008-07-04 17:27:16
210	26	11	2008-07-04 17:27:24	2008-07-04 17:27:24
211	57	38	2008-07-04 17:28:05	2008-07-04 17:28:05
212	58	38	2008-07-04 17:28:12	2008-07-04 17:28:12
213	59	38	2008-07-04 17:28:20	2008-07-04 17:28:20
214	60	38	2008-07-04 17:28:28	2008-07-04 17:28:28
215	61	38	2008-07-04 17:28:36	2008-07-04 17:28:36
216	62	38	2008-07-04 17:28:46	2008-07-04 17:28:46
217	33	31	2008-07-04 17:29:19	2008-07-04 17:29:19
218	34	31	2008-07-04 17:29:26	2008-07-04 17:29:26
219	35	31	2008-07-04 17:29:33	2008-07-04 17:29:33
220	36	31	2008-07-04 17:29:40	2008-07-04 17:29:40
221	37	31	2008-07-04 17:29:47	2008-07-04 17:29:47
222	69	62	2008-07-04 17:30:21	2008-07-04 17:30:21
223	70	62	2008-07-04 17:30:29	2008-07-04 17:30:29
224	30	37	2008-07-04 17:31:05	2008-07-04 17:31:05
225	30	34	2008-07-04 17:31:53	2008-07-04 17:31:53
226	30	55	2008-07-04 17:32:20	2008-07-04 17:32:20
227	31	55	2008-07-04 17:32:27	2008-07-04 17:32:27
228	32	55	2008-07-04 17:32:35	2008-07-04 17:32:35
229	47	9	2008-07-04 17:33:44	2008-07-04 17:33:44
230	47	10	2008-07-04 17:34:59	2008-07-04 17:34:59
231	19	19	2008-07-04 17:35:37	2008-07-04 17:35:37
232	69	61	2008-07-04 17:36:09	2008-07-04 17:36:09
233	70	61	2008-07-04 17:36:15	2008-07-04 17:36:15
234	69	60	2008-07-04 17:36:52	2008-07-04 17:36:52
235	70	60	2008-07-04 17:36:58	2008-07-04 17:36:58
236	69	68	2008-07-04 17:37:37	2008-07-04 17:37:37
237	63	68	2008-07-04 17:37:45	2008-07-04 17:37:45
238	64	68	2008-07-04 17:37:51	2008-07-04 17:37:51
239	65	68	2008-07-04 17:37:59	2008-07-04 17:37:59
240	66	68	2008-07-04 17:38:07	2008-07-04 17:38:07
241	33	7	2008-07-04 18:37:12	2008-07-04 18:37:12
242	6	26	2008-07-04 18:37:33	2008-07-04 18:37:33
243	34	32	2008-07-04 18:38:16	2008-07-04 18:38:16
244	63	37	2008-07-29 10:17:54	2008-07-29 10:17:54
245	64	37	2008-07-29 10:18:04	2008-07-29 10:18:04
246	30	21	2008-07-29 10:22:18	2008-07-29 10:22:18
249	52	73	2008-07-29 10:28:41	2008-07-29 10:28:41
250	3	74	2008-07-29 10:33:25	2008-07-29 10:33:25
251	4	74	2008-07-29 10:33:25	2008-07-29 10:33:25
252	5	74	2008-07-29 10:33:25	2008-07-29 10:33:25
253	6	74	2008-07-29 10:33:25	2008-07-29 10:33:25
254	7	74	2008-07-29 10:33:25	2008-07-29 10:33:25
255	3	75	2008-07-29 11:50:15	2008-07-29 11:50:15
256	4	75	2008-07-29 11:50:15	2008-07-29 11:50:15
257	5	75	2008-07-29 11:50:15	2008-07-29 11:50:15
258	6	75	2008-07-29 11:50:15	2008-07-29 11:50:15
259	7	75	2008-07-29 11:50:15	2008-07-29 11:50:15
260	3	76	2008-07-06 10:33:07	2008-07-06 10:33:07
261	4	76	2008-07-06 10:33:07	2008-07-06 10:33:07
262	5	76	2008-07-06 10:33:07	2008-07-06 10:33:07
263	6	76	2008-07-06 10:33:07	2008-07-06 10:33:07
264	7	76	2008-07-06 10:33:07	2008-07-06 10:33:07
\.


--
-- Data for Name: adjudicator_feedback_sheets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY adjudicator_feedback_sheets (id, adjudicator_id, adjudicator_allocation_id, debate_team_xref_id, comments, score, created_at, updated_at) FROM stdin;
1	24	\N	45	No Comment	4	2008-07-29 13:30:24	2008-07-29 13:30:24
2	44	\N	55	No Comment	3	2008-07-29 13:32:57	2008-07-29 13:32:57
3	71	\N	25	No Comment	4	2008-07-29 13:33:14	2008-07-29 13:33:14
4	71	\N	26	No Comment	5	2008-07-29 13:33:49	2008-07-29 13:33:49
5	44	\N	56	No Comment	3	2008-07-29 13:34:09	2008-07-29 13:34:09
6	16	\N	65	No Comment	3	2008-07-29 13:34:27	2008-07-29 13:34:27
8	16	\N	66	No Comment	4	2008-07-29 13:35:00	2008-07-29 13:35:00
9	40	\N	53	No Comment	4	2008-07-29 13:35:01	2008-07-29 13:35:01
11	51	\N	68	No Comment	3	2008-07-29 13:35:46	2008-07-29 13:35:46
12	40	\N	54	No Comment	3	2008-07-29 13:36:00	2008-07-29 13:36:00
13	3	\N	35	No Comment	4	2008-07-29 13:36:07	2008-07-29 13:36:07
14	51	\N	67	No Comment	4	2008-07-29 13:36:23	2008-07-29 13:36:23
15	38	\N	49	No Comment	4	2008-07-29 13:37:01	2008-07-29 13:37:01
16	38	\N	50	No Comment	4	2008-07-29 13:37:27	2008-07-29 13:37:27
17	55	\N	37	No Comment	4	2008-07-29 13:37:40	2008-07-29 13:37:40
18	17	\N	33	No Comment	4	2008-07-29 13:37:55	2008-07-29 13:37:55
19	55	\N	38	No Comment	4	2008-07-29 13:38:09	2008-07-29 13:38:09
20	17	\N	34	No Comment	4	2008-07-29 13:38:34	2008-07-29 13:38:34
21	24	\N	46	No Comment	5	2008-07-29 13:38:52	2008-07-29 13:38:52
22	6	\N	73	No Comment	4	2008-07-29 13:39:02	2008-07-29 13:39:02
23	6	\N	74	No Comment	4	2008-07-29 13:39:20	2008-07-29 13:39:20
24	34	\N	32	No Comment	5	2008-07-29 13:40:19	2008-07-29 13:40:19
25	34	\N	31	No Comment	4	2008-07-29 13:40:50	2008-07-29 13:40:50
26	39	\N	41	No Comment	3	2008-07-29 13:42:11	2008-07-29 13:42:11
27	39	\N	42	No Comment	4	2008-07-29 13:42:39	2008-07-29 13:42:39
29	21	\N	58	No Comment	3	2008-07-29 13:43:33	2008-07-29 13:43:33
31	21	\N	57	No Comment	4	2008-07-29 13:44:07	2008-07-29 13:44:07
32	37	\N	14	No Comment	5	2008-07-29 13:44:11	2008-07-29 13:44:11
33	37	\N	13	No Comment	5	2008-07-29 13:44:33	2008-07-29 13:44:33
34	49	\N	71	No Comment	3	2008-07-29 13:44:41	2008-07-29 13:44:41
36	49	\N	72	No Comment	3	2008-07-29 13:45:13	2008-07-29 13:45:13
38	30	\N	16	No Comment	5	2008-07-29 13:46:08	2008-07-29 13:46:08
39	30	\N	15	No Comment	3	2008-07-29 13:46:31	2008-07-29 13:46:31
42	62	\N	43	No Comment	2	2008-07-29 13:47:53	2008-07-29 13:47:53
43	62	\N	44	No Comment	4	2008-07-29 13:48:14	2008-07-29 13:48:14
44	33	\N	61	No Comment	5	2008-07-29 13:48:39	2008-07-29 13:48:39
45	31	\N	47	No Comment	4	2008-07-29 13:49:16	2008-07-29 13:49:16
46	31	\N	48	No Comment	4	2008-07-29 13:49:52	2008-07-29 13:49:52
47	33	\N	62	No Comment	3	2008-07-29 13:50:42	2008-07-29 13:50:42
48	36	\N	30	No Comment	5	2008-07-29 13:51:25	2008-07-29 13:51:25
49	35	\N	12	No Comment	4	2008-07-29 13:51:31	2008-07-29 13:51:31
50	36	\N	29	No Comment	4	2008-07-29 13:51:48	2008-07-29 13:51:48
51	35	\N	11	No Comment	4	2008-07-29 13:51:51	2008-07-29 13:51:51
52	50	\N	69	No Comment	4	2008-07-29 13:52:23	2008-07-29 13:52:23
53	50	\N	70	No Comment	4	2008-07-29 13:52:45	2008-07-29 13:52:45
54	56	\N	59	No Comment	3	2008-07-29 13:52:59	2008-07-29 13:52:59
55	56	\N	60	No Comment	4	2008-07-29 13:53:48	2008-07-29 13:53:48
56	59	\N	17	No Comment	4	2008-07-29 13:56:14	2008-07-29 13:56:14
57	59	\N	18	No Comment	5	2008-07-29 13:56:40	2008-07-29 13:56:40
58	48	\N	63	No Comment	3	2008-07-29 13:58:24	2008-07-29 13:58:24
59	48	\N	64	No Comment	2	2008-07-29 13:58:47	2008-07-29 13:58:47
60	50	53	\N	No Comment	5	2008-07-29 14:01:54	2008-07-29 14:01:54
61	4	\N	52	No Comment	5	2008-07-29 14:02:14	2008-07-29 14:02:14
62	14	53	\N	No Comment	4	2008-07-29 14:02:22	2008-07-29 14:02:22
63	50	52	\N	No Comment	4	2008-07-29 14:02:52	2008-07-29 14:02:52
64	23	52	\N	No Comment	2	2008-07-29 14:03:14	2008-07-29 14:03:14
65	21	34	\N	No Comment	3	2008-07-29 14:03:28	2008-07-29 14:03:28
66	14	51	\N	No Comment	3	2008-07-29 14:03:39	2008-07-29 14:03:39
67	19	34	\N	No Comment	2	2008-07-29 14:03:58	2008-07-29 14:03:58
68	23	51	\N	No Comment	3	2008-07-29 14:04:18	2008-07-29 14:04:18
69	70	33	\N	No Comment	4	2008-07-29 14:04:32	2008-07-29 14:04:32
70	49	55	\N	No Comment	5	2008-07-29 14:04:42	2008-07-29 14:04:42
71	19	33	\N	No Comment	4	2008-07-29 14:05:00	2008-07-29 14:05:00
72	21	35	\N	No Comment	4	2008-07-29 14:05:28	2008-07-29 14:05:28
73	61	55	\N	No Comment	3	2008-07-29 14:05:34	2008-07-29 14:05:34
74	70	35	\N	No Comment	4	2008-07-29 14:05:51	2008-07-29 14:05:51
75	33	40	\N	No Comment	4	2008-07-29 14:06:28	2008-07-29 14:06:28
76	49	56	\N	No Comment	4	2008-07-29 14:07:29	2008-07-29 14:07:29
77	60	40	\N	No Comment	4	2008-07-29 14:07:33	2008-07-29 14:07:33
78	69	56	\N	No Comment	2	2008-07-29 14:07:52	2008-07-29 14:07:52
79	33	41	\N	No Comment	5	2008-07-29 14:07:58	2008-07-29 14:07:58
80	69	54	\N	No Comment	3	2008-07-29 14:08:14	2008-07-29 14:08:14
81	64	41	\N	No Comment	3	2008-07-29 14:08:15	2008-07-29 14:08:15
82	61	54	\N	No Comment	3	2008-07-29 14:08:41	2008-07-29 14:08:41
83	15	58	\N	No Comment	4	2008-07-29 14:09:05	2008-07-29 14:09:05
84	18	36	\N	No Comment	4	2008-07-29 14:09:15	2008-07-29 14:09:15
85	6	58	\N	No Comment	5	2008-07-29 14:09:26	2008-07-29 14:09:26
86	20	36	\N	No Comment	4	2008-07-29 14:09:44	2008-07-29 14:09:44
87	54	59	\N	No Comment	3	2008-07-29 14:09:54	2008-07-29 14:09:54
88	6	59	\N	No Comment	5	2008-07-29 14:10:15	2008-07-29 14:10:15
89	56	37	\N	No Comment	4	2008-07-29 14:10:21	2008-07-29 14:10:21
90	54	57	\N	No Comment	4	2008-07-29 14:10:44	2008-07-29 14:10:44
91	15	57	\N	No Comment	4	2008-07-29 14:11:05	2008-07-29 14:11:05
92	16	46	\N	No Comment	4	2008-07-29 14:11:43	2008-07-29 14:11:43
93	13	46	\N	No Comment	3	2008-07-29 14:12:07	2008-07-29 14:12:07
94	57	45	\N	No Comment	3	2008-07-29 14:12:32	2008-07-29 14:12:32
95	13	45	\N	No Comment	3	2008-07-29 14:12:53	2008-07-29 14:12:53
96	56	38	\N	No Comment	4	2008-07-29 14:12:54	2008-07-29 14:12:54
97	16	47	\N	No Comment	3	2008-07-29 14:13:17	2008-07-29 14:13:17
98	20	38	\N	No Comment	4	2008-07-29 14:13:20	2008-07-29 14:13:20
99	57	47	\N	No Comment	3	2008-07-29 14:13:42	2008-07-29 14:13:42
100	18	37	\N	No Comment	4	2008-07-29 14:13:52	2008-07-29 14:13:52
101	3	\N	36	No Comment	3	2008-07-29 14:15:07	2008-07-29 14:15:07
102	51	50	\N	No Comment	3	2008-07-29 14:15:37	2008-07-29 14:15:37
103	28	50	\N	No Comment	3	2008-07-29 14:16:11	2008-07-29 14:16:11
104	51	49	\N	No Comment	3	2008-07-29 14:16:50	2008-07-29 14:16:50
105	64	39	\N	No Comment	3	2008-07-29 14:16:51	2008-07-29 14:16:51
106	1	49	\N	No Comment	4	2008-07-29 14:17:11	2008-07-29 14:17:11
107	28	48	\N	No Comment	4	2008-07-29 14:17:30	2008-07-29 14:17:30
108	60	39	\N	No Comment	3	2008-07-29 14:17:31	2008-07-29 14:17:31
109	1	48	\N	No Comment	4	2008-07-29 14:17:46	2008-07-29 14:17:46
110	48	43	\N	No Comment	3	2008-07-29 14:18:08	2008-07-29 14:18:08
111	29	43	\N	No Comment	3	2008-07-29 14:18:41	2008-07-29 14:18:41
112	67	42	\N	No Comment	3	2008-07-29 14:19:41	2008-07-29 14:19:41
113	29	42	\N	No Comment	2	2008-07-29 14:19:58	2008-07-29 14:19:58
114	48	44	\N	No Comment	3	2008-07-29 14:20:16	2008-07-29 14:20:16
115	67	44	\N	No Comment	4	2008-07-29 14:20:53	2008-07-29 14:20:53
116	74	\N	4	No Comment	3	2008-07-29 14:40:45	2008-07-29 14:40:45
117	74	\N	3	No Comment	4	2008-07-29 14:41:02	2008-07-29 14:41:02
118	5	\N	28	No Comment	3	2008-07-29 14:41:55	2008-07-29 14:41:55
119	5	\N	27	No Comment	5	2008-07-29 14:42:14	2008-07-29 14:42:14
120	73	\N	39	=)	5	2008-07-29 14:43:53	2008-07-29 14:43:53
121	73	\N	40	No Comment	3	2008-07-29 14:44:39	2008-07-29 14:44:39
122	75	\N	20	No Comment	3	2008-07-29 14:45:06	2008-07-29 14:45:06
123	75	\N	19	No Comment	4	2008-07-29 14:45:28	2008-07-29 14:45:28
125	22	16	\N	No Comment	1	2008-07-29 14:58:51	2008-07-29 14:58:51
126	68	18	\N	No Comment	1	2008-07-29 14:59:08	2008-07-29 14:59:08
127	65	23	\N	No Comment	1	2008-07-29 14:59:27	2008-07-29 14:59:27
128	2	7	\N	No Comment	4	2008-07-29 15:01:29	2008-07-29 15:01:29
129	4	\N	51	Neg debated topic right to protest not china's right to prosecute but adj gave them win	2	2008-07-29 15:48:41	2008-07-29 15:48:41
130	15	97	\N	No Comment	3	2008-07-29 16:44:17	2008-07-29 16:44:17
131	64	97	\N	No Comment	2	2008-07-29 16:44:46	2008-07-29 16:44:46
132	64	\N	131	No Comment	2	2008-07-29 16:45:26	2008-07-29 16:45:26
133	64	\N	132	No Comment	1	2008-07-29 16:45:55	2008-07-29 16:45:55
134	54	101	\N	No Comment	3	2008-07-29 16:46:29	2008-07-29 16:46:29
135	56	101	\N	No Comment	3	2008-07-29 16:47:56	2008-07-29 16:47:56
136	60	115	\N	No Comment	4	2008-07-29 16:48:17	2008-07-29 16:48:17
137	56	99	\N	No Comment	5	2008-07-29 16:48:19	2008-07-29 16:48:19
138	41	99	\N	No Comment	5	2008-07-29 16:48:49	2008-07-29 16:48:49
139	25	115	\N	No Comment	3	2008-07-29 16:48:55	2008-07-29 16:48:55
140	54	100	\N	No Comment	4	2008-07-29 16:49:10	2008-07-29 16:49:10
141	60	116	\N	No Comment	4	2008-07-29 16:49:18	2008-07-29 16:49:18
142	41	100	\N	No Comment	3	2008-07-29 16:49:34	2008-07-29 16:49:34
143	2	116	\N	No Comment	3	2008-07-29 16:49:49	2008-07-29 16:49:49
144	11	\N	126	No Comment	4	2008-07-29 16:50:00	2008-07-29 16:50:00
145	45	96	\N	No Comment	3	2008-07-29 16:50:12	2008-07-29 16:50:12
146	11	\N	125	No Comment	4	2008-07-29 16:50:28	2008-07-29 16:50:28
147	15	96	\N	No Comment	4	2008-07-29 16:50:53	2008-07-29 16:50:53
148	70	\N	115	No Comment	4	2008-07-29 16:50:55	2008-07-29 16:50:55
149	70	\N	116	No Comment	4	2008-07-29 16:51:20	2008-07-29 16:51:20
150	14	103	\N	No Comment	4	2008-07-29 16:51:21	2008-07-29 16:51:21
151	20	90	\N	No Comment	3	2008-07-29 16:51:48	2008-07-29 16:51:48
152	10	103	\N	No Comment	2	2008-07-29 16:51:55	2008-07-29 16:51:55
153	6	90	\N	No Comment	3	2008-07-29 16:52:10	2008-07-29 16:52:10
154	14	102	\N	No Comment	3	2008-07-29 16:52:16	2008-07-29 16:52:16
155	70	91	\N	No Comment	4	2008-07-29 16:52:35	2008-07-29 16:52:35
156	44	102	\N	No Comment	5	2008-07-29 16:52:43	2008-07-29 16:52:43
157	20	91	\N	No Comment	2	2008-07-29 16:52:56	2008-07-29 16:52:56
158	2	114	\N	No Comment	4	2008-07-29 16:53:13	2008-07-29 16:53:13
159	70	92	\N	No Comment	4	2008-07-29 16:53:17	2008-07-29 16:53:17
160	25	114	\N	No Comment	2	2008-07-29 16:53:37	2008-07-29 16:53:37
161	6	92	\N	No Comment	3	2008-07-29 16:53:42	2008-07-29 16:53:42
162	10	104	\N	No Comment	3	2008-07-29 16:54:00	2008-07-29 16:54:00
163	29	111	\N	No Comment	2	2008-07-29 16:54:06	2008-07-29 16:54:06
164	44	104	\N	No Comment	3	2008-07-29 16:54:17	2008-07-29 16:54:17
165	69	111	\N	No Comment	3	2008-07-29 16:54:34	2008-07-29 16:54:34
166	53	112	\N	No Comment	4	2008-07-29 16:55:16	2008-07-29 16:55:16
167	64	98	\N	No Comment	3	2008-07-29 16:55:26	2008-07-29 16:55:26
168	69	112	\N	No Comment	3	2008-07-29 16:55:47	2008-07-29 16:55:47
169	45	98	\N	No Comment	1	2008-07-29 16:55:51	2008-07-29 16:55:51
170	53	113	\N	No Comment	3	2008-07-29 16:56:38	2008-07-29 16:56:38
171	29	113	\N	No Comment	1	2008-07-29 16:57:05	2008-07-29 16:57:05
172	53	\N	123	No Comment	3	2008-07-29 16:57:36	2008-07-29 16:57:36
173	1	110	\N	No Comment	2	2008-07-29 16:57:37	2008-07-29 16:57:37
174	9	86	\N	No Comment	4	2008-07-29 16:58:13	2008-07-29 16:58:13
175	16	86	\N	No Comment	4	2008-07-29 16:58:39	2008-07-29 16:58:39
176	50	110	\N	No Comment	3	2008-07-29 16:58:49	2008-07-29 16:58:49
177	18	84	\N	No Comment	3	2008-07-29 16:59:03	2008-07-29 16:59:03
178	50	108	\N	No Comment	3	2008-07-29 16:59:23	2008-07-29 16:59:23
179	16	84	\N	No Comment	3	2008-07-29 16:59:26	2008-07-29 16:59:26
180	19	108	\N	No Comment	4	2008-07-29 16:59:46	2008-07-29 16:59:46
181	9	85	\N	No Comment	2	2008-07-29 16:59:47	2008-07-29 16:59:47
182	18	85	\N	No Comment	2	2008-07-29 17:00:13	2008-07-29 17:00:13
183	47	106	\N	No Comment	4	2008-07-29 17:00:20	2008-07-29 17:00:20
184	9	\N	138	No Comment	3	2008-07-29 17:00:36	2008-07-29 17:00:36
185	61	106	\N	No Comment	4	2008-07-29 17:00:47	2008-07-29 17:00:47
186	9	\N	137	No Comment	2	2008-07-29 17:00:59	2008-07-29 17:00:59
187	61	105	\N	No Comment	2	2008-07-29 17:01:04	2008-07-29 17:01:04
188	51	105	\N	No Comment	4	2008-07-29 17:01:26	2008-07-29 17:01:26
189	57	\N	144	No Comment	4	2008-07-29 17:01:34	2008-07-29 17:01:34
190	47	107	\N	No Comment	4	2008-07-29 17:01:51	2008-07-29 17:01:51
191	28	\N	145	No Comment	2	2008-07-29 17:02:05	2008-07-29 17:02:05
192	51	107	\N	No Comment	4	2008-07-29 17:02:09	2008-07-29 17:02:09
193	28	\N	146	No Comment	3	2008-07-29 17:02:29	2008-07-29 17:02:29
194	28	119	\N	No Comment	2	2008-07-29 17:02:53	2008-07-29 17:02:53
195	48	119	\N	No Comment	3	2008-07-29 17:03:25	2008-07-29 17:03:25
196	28	118	\N	No Comment	3	2008-07-29 17:03:50	2008-07-29 17:03:50
197	49	\N	148	No Comment	3	2008-07-29 17:04:06	2008-07-29 17:04:06
198	67	118	\N	No Comment	3	2008-07-29 17:04:11	2008-07-29 17:04:11
199	54	\N	133	No Comment	3	2008-07-29 17:04:26	2008-07-29 17:04:26
200	35	\N	96	No Comment	4	2008-07-29 17:04:33	2008-07-29 17:04:33
201	67	117	\N	No Comment	3	2008-07-29 17:04:33	2008-07-29 17:04:33
202	54	\N	134	No Comment	4	2008-07-29 17:04:53	2008-07-29 17:04:53
203	48	117	\N	No Comment	3	2008-07-29 17:05:02	2008-07-29 17:05:02
204	4	\N	88	No Comment	5	2008-07-29 17:05:11	2008-07-29 17:05:11
205	24	\N	93	No Comment	4	2008-07-29 17:05:13	2008-07-29 17:05:13
206	3	\N	100	No Comment	4	2008-07-29 17:05:31	2008-07-29 17:05:31
207	24	\N	94	No Comment	3	2008-07-29 17:05:33	2008-07-29 17:05:33
208	4	\N	87	No Comment	4	2008-07-29 17:05:35	2008-07-29 17:05:35
209	17	\N	90	No Comment	4	2008-07-29 17:06:01	2008-07-29 17:06:01
210	47	\N	142	No Comment	3	2008-07-29 17:06:10	2008-07-29 17:06:10
211	17	\N	89	No Comment	3	2008-07-29 17:06:23	2008-07-29 17:06:23
212	30	\N	98	No Comment	3	2008-07-29 17:06:25	2008-07-29 17:06:25
213	47	\N	141	No Comment	4	2008-07-29 17:06:37	2008-07-29 17:06:37
214	30	\N	97	No Comment	4	2008-07-29 17:07:01	2008-07-29 17:07:01
215	12	\N	102	No Comment	4	2008-07-29 17:07:04	2008-07-29 17:07:04
216	37	\N	113	No Comment	5	2008-07-29 17:07:14	2008-07-29 17:07:14
217	12	\N	101	No Comment	3	2008-07-29 17:07:24	2008-07-29 17:07:24
218	39	\N	105	No Comment	3	2008-07-29 17:07:58	2008-07-29 17:07:58
219	59	\N	104	No Comment	5	2008-07-29 17:08:22	2008-07-29 17:08:22
220	39	\N	106	No Comment	4	2008-07-29 17:08:23	2008-07-29 17:08:23
221	37	\N	114	No Comment	4	2008-07-29 17:08:46	2008-07-29 17:08:46
222	58	\N	111	No Comment	4	2008-07-29 17:08:48	2008-07-29 17:08:48
223	58	\N	112	No Comment	1	2008-07-29 17:09:12	2008-07-29 17:09:12
224	36	\N	107	No Comment	5	2008-07-29 17:09:38	2008-07-29 17:09:38
225	71	\N	110	No Comment	4	2008-07-29 17:10:11	2008-07-29 17:10:11
226	59	\N	103	No Comment	5	2008-07-29 17:10:14	2008-07-29 17:10:14
227	36	\N	108	No Comment	3	2008-07-29 17:10:38	2008-07-29 17:10:38
228	34	\N	82	No Comment	5	2008-07-29 17:10:58	2008-07-29 17:10:58
229	71	\N	109	No Comment	4	2008-07-29 17:11:16	2008-07-29 17:11:16
230	62	\N	118	No Comment	3	2008-07-29 17:11:36	2008-07-29 17:11:36
231	1	\N	139	No Comment	3	2008-07-29 17:11:50	2008-07-29 17:11:50
232	62	\N	117	No Comment	2	2008-07-29 17:12:17	2008-07-29 17:12:17
233	10	\N	135	No Comment	3	2008-07-29 17:12:18	2008-07-29 17:12:18
234	60	\N	122	No Comment	4	2008-07-29 17:12:44	2008-07-29 17:12:44
235	40	93	\N	No Comment	4	2008-07-29 17:12:56	2008-07-29 17:12:56
236	13	93	\N	No Comment	3	2008-07-29 17:13:19	2008-07-29 17:13:19
237	10	\N	136	No Comment	3	2008-07-29 17:13:22	2008-07-29 17:13:22
238	60	\N	121	No Comment	4	2008-07-29 17:13:42	2008-07-29 17:13:42
239	57	95	\N	No Comment	4	2008-07-29 17:13:44	2008-07-29 17:13:44
240	40	95	\N	No Comment	4	2008-07-29 17:14:12	2008-07-29 17:14:12
241	49	\N	147	No Comment	3	2008-07-29 17:14:12	2008-07-29 17:14:12
242	57	94	\N	No Comment	4	2008-07-29 17:14:47	2008-07-29 17:14:47
243	13	94	\N	No Comment	4	2008-07-29 17:15:09	2008-07-29 17:15:09
244	38	\N	120	No Comment	5	2008-07-29 17:15:19	2008-07-29 17:15:19
245	21	\N	128	No Comment	2	2008-07-29 17:15:31	2008-07-29 17:15:31
246	38	\N	119	No Comment	4	2008-07-29 17:15:42	2008-07-29 17:15:42
247	21	\N	127	No Comment	3	2008-07-29 17:15:58	2008-07-29 17:15:58
249	21	88	\N	No Comment	4	2008-07-29 17:16:24	2008-07-29 17:16:24
252	23	88	\N	No Comment	2	2008-07-29 17:16:57	2008-07-29 17:16:57
254	33	87	\N	No Comment	4	2008-07-29 17:17:43	2008-07-29 17:17:43
255	23	87	\N	No Comment	3	2008-07-29 17:18:10	2008-07-29 17:18:10
256	55	\N	91	No Comment	5	2008-07-29 17:18:28	2008-07-29 17:18:28
257	21	89	\N	No Comment	5	2008-07-29 17:18:35	2008-07-29 17:18:35
258	55	\N	92	No Comment	3	2008-07-29 17:18:56	2008-07-29 17:18:56
259	33	89	\N	No Comment	4	2008-07-29 17:18:58	2008-07-29 17:18:58
260	31	\N	130	No Comment	4	2008-07-29 17:19:30	2008-07-29 17:19:30
261	34	\N	81	No Comment	4	2008-07-29 17:19:32	2008-07-29 17:19:32
262	31	\N	129	No Comment	3	2008-07-29 17:19:59	2008-07-29 17:19:59
263	63	129	\N	Right Result, Scores are off	2	2008-07-29 17:20:26	2008-07-29 17:20:26
264	1	\N	140	No Comment	5	2008-07-29 17:22:16	2008-07-29 17:22:16
265	65	69	\N	No Comment	3	2008-07-29 17:22:38	2008-07-29 17:22:38
266	22	63	\N	got decision right but very inexperienced	3	2008-07-29 17:26:24	2008-07-29 17:26:24
267	35	\N	95	No Comment	5	2008-07-29 17:26:51	2008-07-29 17:26:51
269	53	\N	124	No Comment	3	2008-07-29 17:29:20	2008-07-29 17:29:20
270	1	109	\N	No Comment	2	2008-07-29 17:29:56	2008-07-29 17:29:56
271	6	\N	185	No Comment	2	2008-07-29 19:50:16	2008-07-29 19:50:16
272	6	\N	186	No Comment	4	2008-07-29 19:50:45	2008-07-29 19:50:45
273	5	\N	152	No Comment	5	2008-07-29 19:51:27	2008-07-29 19:51:27
274	67	168	\N	No Comment	3	2008-07-29 19:51:50	2008-07-29 19:51:50
275	5	\N	151	No Comment	4	2008-07-29 19:51:56	2008-07-29 19:51:56
276	48	168	\N	No Comment	3	2008-07-29 19:52:19	2008-07-29 19:52:19
277	4	\N	190	No Comment	5	2008-07-29 19:52:23	2008-07-29 19:52:23
278	4	\N	189	No Comment	4	2008-07-29 19:52:46	2008-07-29 19:52:46
279	45	162	\N	No Comment	4	2008-07-29 19:52:48	2008-07-29 19:52:48
280	10	162	\N	No Comment	3	2008-07-29 19:53:15	2008-07-29 19:53:15
281	12	\N	191	No Comment	5	2008-07-29 19:53:20	2008-07-29 19:53:20
282	12	\N	192	No Comment	5	2008-07-29 19:53:44	2008-07-29 19:53:44
283	11	\N	188	No Comment	4	2008-07-29 19:54:16	2008-07-29 19:54:16
284	64	151	\N	No Comment	4	2008-07-29 19:54:26	2008-07-29 19:54:26
285	11	\N	187	No Comment	5	2008-07-29 19:54:42	2008-07-29 19:54:42
286	16	151	\N	No Comment	4	2008-07-29 19:54:53	2008-07-29 19:54:53
287	15	152	\N	No Comment	5	2008-07-29 19:55:14	2008-07-29 19:55:14
288	34	\N	167	No Comment	5	2008-07-29 19:55:32	2008-07-29 19:55:32
289	64	152	\N	No Comment	3	2008-07-29 19:55:48	2008-07-29 19:55:48
290	15	153	\N	No Comment	4	2008-07-29 19:56:16	2008-07-29 19:56:16
291	16	153	\N	No Comment	4	2008-07-29 19:56:33	2008-07-29 19:56:33
292	70	\N	197	No Comment	4	2008-07-29 19:56:35	2008-07-29 19:56:35
293	17	\N	196	No Comment	4	2008-07-29 19:56:45	2008-07-29 19:56:45
294	62	\N	201	No Comment	4	2008-07-29 19:57:11	2008-07-29 19:57:11
295	62	\N	202	No Comment	4	2008-07-29 19:57:31	2008-07-29 19:57:31
296	41	164	\N	No Comment	5	2008-07-29 19:57:37	2008-07-29 19:57:37
297	1	\N	213	No Comment	4	2008-07-29 19:57:53	2008-07-29 19:57:53
299	54	164	\N	No Comment	4	2008-07-29 19:58:14	2008-07-29 19:58:14
301	54	163	\N	No Comment	5	2008-07-29 19:58:38	2008-07-29 19:58:38
304	40	163	\N	No Comment	5	2008-07-29 19:59:13	2008-07-29 19:59:13
306	41	165	\N	No Comment	5	2008-07-29 19:59:39	2008-07-29 19:59:39
308	70	150	\N	No Comment	4	2008-07-29 19:59:57	2008-07-29 19:59:57
309	40	165	\N	No Comment	3	2008-07-29 20:00:12	2008-07-29 20:00:12
310	33	\N	203	No Comment	4	2008-07-29 20:00:24	2008-07-29 20:00:24
311	33	\N	204	No Comment	3	2008-07-29 20:00:47	2008-07-29 20:00:47
312	41	\N	212	No Comment	3	2008-07-29 20:00:50	2008-07-29 20:00:50
313	15	\N	199	No Comment	4	2008-07-29 20:01:15	2008-07-29 20:01:15
314	41	\N	211	No Comment	3	2008-07-29 20:01:20	2008-07-29 20:01:20
315	60	150	\N	No Comment	4	2008-07-29 20:01:37	2008-07-29 20:01:37
316	15	\N	200	No Comment	4	2008-07-29 20:01:49	2008-07-29 20:01:49
317	57	\N	205	No Comment	4	2008-07-29 20:02:16	2008-07-29 20:02:16
318	24	\N	162	No Comment	3	2008-07-29 20:02:17	2008-07-29 20:02:17
319	57	\N	206	No Comment	4	2008-07-29 20:02:42	2008-07-29 20:02:42
320	34	\N	168	No Comment	2	2008-07-29 20:02:46	2008-07-29 20:02:46
321	45	\N	209	No Comment	3	2008-07-29 20:03:37	2008-07-29 20:03:37
322	51	177	\N	No Comment	2	2008-07-29 20:03:39	2008-07-29 20:03:39
323	20	149	\N	No Comment	4	2008-07-29 20:03:41	2008-07-29 20:03:41
324	45	\N	210	No Comment	3	2008-07-29 20:04:03	2008-07-29 20:04:03
325	47	177	\N	No Comment	3	2008-07-29 20:04:19	2008-07-29 20:04:19
326	70	149	\N	No Comment	5	2008-07-29 20:04:48	2008-07-29 20:04:48
327	47	176	\N	No Comment	4	2008-07-29 20:04:53	2008-07-29 20:04:53
328	67	167	\N	No Comment	3	2008-07-29 20:05:06	2008-07-29 20:05:06
329	61	176	\N	No Comment	4	2008-07-29 20:05:23	2008-07-29 20:05:23
330	28	167	\N	No Comment	3	2008-07-29 20:05:26	2008-07-29 20:05:26
331	60	148	\N	No Comment	3	2008-07-29 20:05:42	2008-07-29 20:05:42
332	51	175	\N	No Comment	3	2008-07-29 20:05:53	2008-07-29 20:05:53
333	48	166	\N	No Comment	3	2008-07-29 20:05:54	2008-07-29 20:05:54
334	28	166	\N	No Comment	3	2008-07-29 20:06:19	2008-07-29 20:06:19
335	20	148	\N	No Comment	3	2008-07-29 20:06:21	2008-07-29 20:06:21
336	61	175	\N	No Comment	3	2008-07-29 20:06:23	2008-07-29 20:06:23
337	1	170	\N	No Comment	3	2008-07-29 20:06:51	2008-07-29 20:06:51
338	30	\N	222	No Comment	4	2008-07-29 20:07:01	2008-07-29 20:07:01
339	19	170	\N	No Comment	3	2008-07-29 20:07:22	2008-07-29 20:07:22
340	35	\N	194	No Comment	5	2008-07-29 20:07:40	2008-07-29 20:07:40
341	37	\N	163	No Comment	5	2008-07-29 20:07:51	2008-07-29 20:07:51
342	59	\N	178	No Comment	4	2008-07-29 20:08:03	2008-07-29 20:08:03
343	37	\N	164	No Comment	5	2008-07-29 20:08:14	2008-07-29 20:08:14
344	35	\N	193	No Comment	5	2008-07-29 20:08:27	2008-07-29 20:08:27
345	2	178	\N	No Comment	2	2008-07-29 20:08:34	2008-07-29 20:08:34
346	59	\N	177	No Comment	5	2008-07-29 20:08:50	2008-07-29 20:08:50
347	25	178	\N	No Comment	3	2008-07-29 20:08:57	2008-07-29 20:08:57
348	47	\N	217	No Comment	4	2008-07-29 20:09:17	2008-07-29 20:09:17
349	21	179	\N	No Comment	4	2008-07-29 20:09:21	2008-07-29 20:09:21
350	38	\N	182	No Comment	4	2008-07-29 20:09:37	2008-07-29 20:09:37
351	25	179	\N	No Comment	4	2008-07-29 20:09:45	2008-07-29 20:09:45
352	21	180	\N	No Comment	4	2008-07-29 20:10:09	2008-07-29 20:10:09
353	47	\N	218	No Comment	5	2008-07-29 20:10:17	2008-07-29 20:10:17
354	31	\N	179	No Comment	4	2008-07-29 20:10:28	2008-07-29 20:10:28
355	38	\N	181	No Comment	5	2008-07-29 20:10:28	2008-07-29 20:10:28
356	2	180	\N	No Comment	4	2008-07-29 20:10:30	2008-07-29 20:10:30
357	31	\N	180	No Comment	4	2008-07-29 20:11:07	2008-07-29 20:11:07
358	21	\N	219	No Comment	5	2008-07-29 20:11:08	2008-07-29 20:11:08
359	71	\N	165	No Comment	5	2008-07-29 20:11:27	2008-07-29 20:11:27
360	39	\N	183	No Comment	5	2008-07-29 20:11:28	2008-07-29 20:11:28
361	21	\N	220	No Comment	5	2008-07-29 20:11:32	2008-07-29 20:11:32
362	36	\N	174	No Comment	5	2008-07-29 20:11:49	2008-07-29 20:11:49
363	3	\N	175	No Comment	3	2008-07-29 20:12:04	2008-07-29 20:12:04
364	36	\N	173	No Comment	3	2008-07-29 20:12:16	2008-07-29 20:12:16
365	3	\N	176	No Comment	5	2008-07-29 20:12:23	2008-07-29 20:12:23
366	17	\N	195	No Comment	4	2008-07-29 20:12:24	2008-07-29 20:12:24
367	63	129	\N	No Comment	3	2008-07-29 20:12:40	2008-07-29 20:12:40
368	58	\N	169	No Comment	4	2008-07-29 20:12:50	2008-07-29 20:12:50
369	29	173	\N	didn't offer any adjudication	1	2008-07-29 20:13:03	2008-07-29 20:13:03
370	55	\N	171	No Comment	3	2008-07-29 20:13:20	2008-07-29 20:13:20
371	57	158	\N	No Comment	3	2008-07-29 20:13:27	2008-07-29 20:13:27
372	58	\N	170	No Comment	4	2008-07-29 20:13:30	2008-07-29 20:13:30
373	69	173	\N	No Comment	3	2008-07-29 20:13:30	2008-07-29 20:13:30
374	55	\N	172	No Comment	5	2008-07-29 20:13:51	2008-07-29 20:13:51
375	49	172	\N	No Comment	4	2008-07-29 20:14:06	2008-07-29 20:14:06
376	6	146	\N	No Comment	4	2008-07-29 20:14:19	2008-07-29 20:14:19
377	13	158	\N	No Comment	4	2008-07-29 20:14:32	2008-07-29 20:14:32
378	69	172	\N	No Comment	4	2008-07-29 20:14:41	2008-07-29 20:14:41
379	13	157	\N	No Comment	3	2008-07-29 20:15:02	2008-07-29 20:15:02
380	6	145	\N	No Comment	4	2008-07-29 20:15:03	2008-07-29 20:15:03
381	29	174	\N	No Comment	2	2008-07-29 20:15:07	2008-07-29 20:15:07
382	56	154	\N	No Comment	3	2008-07-29 20:15:23	2008-07-29 20:15:23
383	49	174	\N	No Comment	4	2008-07-29 20:15:51	2008-07-29 20:15:51
384	29	\N	215	No Comment	5	2008-07-29 20:16:16	2008-07-29 20:16:16
385	9	146	\N	No Comment	4	2008-07-29 20:16:25	2008-07-29 20:16:25
386	44	157	\N	No Comment	4	2008-07-29 20:16:36	2008-07-29 20:16:36
387	29	\N	216	No Comment	3	2008-07-29 20:16:37	2008-07-29 20:16:37
388	23	154	\N	No Comment	1	2008-07-29 20:16:39	2008-07-29 20:16:39
389	57	159	\N	No Comment	3	2008-07-29 20:17:02	2008-07-29 20:17:02
390	10	160	\N	No Comment	1	2008-07-29 20:17:12	2008-07-29 20:17:12
391	33	155	\N	No Comment	4	2008-07-29 20:17:21	2008-07-29 20:17:21
392	44	159	\N	No Comment	3	2008-07-29 20:17:29	2008-07-29 20:17:29
393	14	160	\N	No Comment	2	2008-07-29 20:17:38	2008-07-29 20:17:38
394	23	155	\N	No Comment	2	2008-07-29 20:17:49	2008-07-29 20:17:49
395	45	161	\N	No Comment	5	2008-07-29 20:18:07	2008-07-29 20:18:07
396	33	156	\N	No Comment	5	2008-07-29 20:18:15	2008-07-29 20:18:15
397	18	145	\N	No Comment	3	2008-07-29 20:18:28	2008-07-29 20:18:28
398	14	161	\N	No Comment	3	2008-07-29 20:18:29	2008-07-29 20:18:29
399	56	156	\N	No Comment	4	2008-07-29 20:18:48	2008-07-29 20:18:48
400	71	\N	166	No Comment	5	2008-07-29 20:19:04	2008-07-29 20:19:04
401	66	132	\N	No Comment	3	2008-07-29 20:19:55	2008-07-29 20:19:55
402	1	\N	214	No Comment	5	2008-07-29 20:20:32	2008-07-29 20:20:32
403	18	144	\N	No Comment	2	2008-07-29 20:20:39	2008-07-29 20:20:39
404	9	144	\N	No Comment	3	2008-07-29 20:21:40	2008-07-29 20:21:40
405	53	\N	268	No Comment	4	2008-07-06 22:13:18	2008-07-06 22:13:18
406	53	\N	267	No Comment	3	2008-07-06 22:13:48	2008-07-06 22:13:48
407	17	\N	245	No Comment	5	2008-07-06 22:14:26	2008-07-06 22:14:26
409	17	\N	246	No Comment	4	2008-07-06 22:15:15	2008-07-06 22:15:15
411	21	\N	271	No Comment	2	2008-07-06 22:15:54	2008-07-06 22:15:54
412	15	\N	261	No Comment	4	2008-07-06 22:16:14	2008-07-06 22:16:14
413	15	\N	262	No Comment	3	2008-07-06 22:16:51	2008-07-06 22:16:51
414	21	\N	272	The adjudicator did not seem to know that there should not be new matter/rebuttals in the reply speech. The team who won gave a rebuttal speech!! Which was really important in a split decision.	3	2008-07-06 22:17:10	2008-07-06 22:17:10
415	62	\N	264	No Comment	5	2008-07-06 22:17:38	2008-07-06 22:17:38
416	11	\N	249	No Comment	4	2008-07-06 22:18:05	2008-07-06 22:18:05
417	35	\N	233	No Comment	5	2008-07-06 22:18:06	2008-07-06 22:18:06
418	45	\N	269	No Comment	4	2008-07-06 22:18:49	2008-07-06 22:18:49
419	11	\N	250	No Comment	5	2008-07-06 22:18:53	2008-07-06 22:18:53
420	35	\N	234	No Comment	5	2008-07-06 22:19:17	2008-07-06 22:19:17
421	38	\N	241	No Comment	4	2008-07-06 22:19:40	2008-07-06 22:19:40
422	70	\N	293	No Comment	4	2008-07-06 22:20:04	2008-07-06 22:20:04
423	70	\N	294	No Comment	5	2008-07-06 22:20:38	2008-07-06 22:20:38
424	50	\N	278	No Comment	5	2008-07-06 22:21:01	2008-07-06 22:21:01
425	6	\N	291	No Comment	4	2008-07-06 22:21:28	2008-07-06 22:21:28
426	33	\N	285	No Comment	4	2008-07-06 22:21:38	2008-07-06 22:21:38
427	6	\N	292	No Comment	4	2008-07-06 22:21:51	2008-07-06 22:21:51
428	10	\N	282	No Comment	1	2008-07-06 22:22:22	2008-07-06 22:22:22
429	33	\N	286	No Comment	5	2008-07-06 22:22:25	2008-07-06 22:22:25
430	10	\N	281	No Comment	2	2008-07-06 22:23:00	2008-07-06 22:23:00
431	37	\N	227	No Comment	4	2008-07-06 22:23:23	2008-07-06 22:23:23
432	71	\N	235	No Comment	5	2008-07-06 22:23:31	2008-07-06 22:23:31
433	37	\N	228	No Comment	5	2008-07-06 22:23:48	2008-07-06 22:23:48
434	71	\N	236	No Comment	5	2008-07-06 22:24:14	2008-07-06 22:24:14
435	38	\N	242	No Comment	4	2008-07-06 22:24:24	2008-07-06 22:24:24
436	50	\N	277	No Comment	4	2008-07-06 22:24:49	2008-07-06 22:24:49
438	47	\N	274	No Comment	4	2008-07-06 22:25:13	2008-07-06 22:25:13
439	47	\N	273	No Comment	3	2008-07-06 22:25:41	2008-07-06 22:25:41
440	16	\N	287	No Comment	2	2008-07-06 22:26:32	2008-07-06 22:26:32
441	31	\N	243	No Comment	3	2008-07-06 22:27:03	2008-07-06 22:27:03
442	16	\N	288	No Comment	3	2008-07-06 22:27:07	2008-07-06 22:27:07
443	49	\N	289	No Comment	4	2008-07-06 22:27:42	2008-07-06 22:27:42
444	31	\N	244	No Comment	4	2008-07-06 22:27:52	2008-07-06 22:27:52
445	49	\N	290	No Comment	3	2008-07-06 22:28:05	2008-07-06 22:28:05
446	76	\N	257	No Comment	3	2008-07-06 22:28:29	2008-07-06 22:28:29
447	55	\N	255	No Comment	4	2008-07-06 22:28:44	2008-07-06 22:28:44
448	76	\N	258	No Comment	4	2008-07-06 22:28:54	2008-07-06 22:28:54
449	55	\N	256	No Comment	4	2008-07-06 22:29:23	2008-07-06 22:29:23
450	48	\N	295	No Comment	3	2008-07-06 22:29:38	2008-07-06 22:29:38
451	48	\N	296	No Comment	4	2008-07-06 22:29:59	2008-07-06 22:29:59
452	34	\N	254	No Comment	5	2008-07-06 22:30:39	2008-07-06 22:30:39
453	34	\N	253	comments were very useful to take away for the next round	4	2008-07-06 22:31:55	2008-07-06 22:31:55
454	12	\N	252	While the team agrees that they should have lost, they disagree with the reasons why the lost.	3	2008-07-06 22:32:20	2008-07-06 22:32:20
455	69	236	\N	No Comment	2	2008-07-06 22:33:04	2008-07-06 22:33:04
456	12	\N	251	No Comment	4	2008-07-06 22:33:10	2008-07-06 22:33:10
457	65	236	\N	No Comment	3	2008-07-06 22:33:44	2008-07-06 22:33:44
458	6	238	\N	No Comment	3	2008-07-06 22:34:09	2008-07-06 22:34:09
459	41	\N	265	No Comment	3	2008-07-06 22:34:23	2008-07-06 22:34:23
460	69	238	\N	No Comment	5	2008-07-06 22:34:35	2008-07-06 22:34:35
461	6	237	\N	No Comment	4	2008-07-06 22:34:58	2008-07-06 22:34:58
462	41	\N	266	No Comment	4	2008-07-06 22:35:00	2008-07-06 22:35:00
463	65	237	\N	No Comment	2	2008-07-06 22:35:29	2008-07-06 22:35:29
464	49	234	\N	No Comment	4	2008-07-06 22:36:00	2008-07-06 22:36:00
465	56	\N	283	No Comment	4	2008-07-06 14:36:44	2008-07-06 14:36:44
466	19	234	\N	No Comment	3	2008-07-06 14:36:52	2008-07-06 14:36:52
467	67	233	\N	No Comment	4	2008-07-06 14:37:22	2008-07-06 14:37:22
468	56	\N	284	No Comment	5	2008-07-06 14:37:49	2008-07-06 14:37:49
470	19	233	\N	No Comment	2	2008-07-06 14:37:56	2008-07-06 14:37:56
471	59	\N	237	No Comment	4	2008-07-06 14:38:37	2008-07-06 14:38:37
472	59	\N	238	No Comment	5	2008-07-06 14:39:08	2008-07-06 14:39:08
473	59	\N	238	No Comment	5	2008-07-06 14:39:27	2008-07-06 14:39:27
474	49	235	\N	while judging EFL speakers didn't check to see if debaters could understand them before giving feedback quickly	4	2008-07-06 14:39:45	2008-07-06 14:39:45
475	67	235	\N	while judging EFL speakers didn't check to see if debaters could understand them before giving feedback quickly	4	2008-07-06 14:40:14	2008-07-06 14:40:14
476	38	191	\N	No Comment	5	2008-07-06 14:40:21	2008-07-06 14:40:21
477	48	243	\N	No Comment	2	2008-07-06 14:40:54	2008-07-06 14:40:54
478	58	191	\N	No Comment	4	2008-07-06 14:41:17	2008-07-06 14:41:17
479	66	243	\N	No Comment	1	2008-07-06 14:41:29	2008-07-06 14:41:29
480	1	242	\N	No Comment	4	2008-07-06 14:41:54	2008-07-06 14:41:54
481	33	228	\N	No Comment	5	2008-07-06 14:41:58	2008-07-06 14:41:58
482	66	242	\N	No Comment	3	2008-07-06 14:42:36	2008-07-06 14:42:36
483	28	228	\N	No Comment	4	2008-07-06 14:42:56	2008-07-06 14:42:56
484	1	244	\N	No Comment	4	2008-07-06 14:43:02	2008-07-06 14:43:02
485	36	\N	259	No Comment	4	2008-07-06 14:43:04	2008-07-06 14:43:04
486	28	228	\N	No Comment	4	2008-07-06 14:43:23	2008-07-06 14:43:23
487	48	244	\N	No Comment	4	2008-07-06 14:43:56	2008-07-06 14:43:56
488	36	\N	260	No Comment	3	2008-07-06 14:44:14	2008-07-06 14:44:14
489	60	229	\N	No Comment	3	2008-07-06 14:44:29	2008-07-06 14:44:29
490	13	219	\N	No Comment	3	2008-07-06 14:44:42	2008-07-06 14:44:42
491	33	229	\N	No Comment	4	2008-07-06 14:45:02	2008-07-06 14:45:02
492	24	\N	279	No Comment	4	2008-07-06 14:45:10	2008-07-06 14:45:10
493	21	219	\N	No Comment	3	2008-07-06 14:45:27	2008-07-06 14:45:27
494	56	225	\N	No Comment	4	2008-07-06 14:45:36	2008-07-06 14:45:36
495	20	225	\N	No Comment	3	2008-07-06 14:46:13	2008-07-06 14:46:13
496	40	224	\N	No Comment	4	2008-07-06 14:46:39	2008-07-06 14:46:39
497	29	230	\N	No Comment	1	2008-07-06 14:46:46	2008-07-06 14:46:46
498	20	224	\N	No Comment	3	2008-07-06 14:47:12	2008-07-06 14:47:12
499	18	230	\N	No Comment	2	2008-07-06 14:47:21	2008-07-06 14:47:21
500	40	226	\N	No Comment	4	2008-07-06 14:47:40	2008-07-06 14:47:40
501	56	226	\N	No Comment	4	2008-07-06 14:48:05	2008-07-06 14:48:05
502	51	221	\N	No Comment	4	2008-07-06 14:48:57	2008-07-06 14:48:57
503	16	232	\N	No Comment	4	2008-07-06 14:49:03	2008-07-06 14:49:03
504	14	221	\N	No Comment	3	2008-07-06 14:49:30	2008-07-06 14:49:30
505	29	232	\N	No Comment	2	2008-07-06 14:49:42	2008-07-06 14:49:42
506	29	232	\N	No Comment	2	2008-07-06 14:49:53	2008-07-06 14:49:53
507	51	223	\N	No Comment	3	2008-07-06 14:49:55	2008-07-06 14:49:55
508	10	223	\N	No Comment	3	2008-07-06 14:50:28	2008-07-06 14:50:28
509	10	222	\N	No Comment	4	2008-07-06 14:50:50	2008-07-06 14:50:50
510	16	231	\N	No Comment	3	2008-07-06 14:50:59	2008-07-06 14:50:59
511	14	222	\N	No Comment	4	2008-07-06 14:51:16	2008-07-06 14:51:16
512	45	217	\N	No Comment	5	2008-07-06 14:51:45	2008-07-06 14:51:45
513	18	231	\N	No Comment	3	2008-07-06 14:51:51	2008-07-06 14:51:51
514	57	217	\N	No Comment	4	2008-07-06 14:52:38	2008-07-06 14:52:38
515	3	194	\N	No Comment	3	2008-07-06 14:52:44	2008-07-06 14:52:44
516	57	215	\N	No Comment	4	2008-07-06 14:53:07	2008-07-06 14:53:07
517	39	194	\N	No Comment	4	2008-07-06 14:53:22	2008-07-06 14:53:22
518	61	215	\N	No Comment	2	2008-07-06 14:53:42	2008-07-06 14:53:42
519	45	216	\N	No Comment	5	2008-07-06 14:54:06	2008-07-06 14:54:06
520	3	196	\N	No Comment	4	2008-07-06 14:54:14	2008-07-06 14:54:14
521	61	216	\N	No Comment	3	2008-07-06 14:54:32	2008-07-06 14:54:32
522	54	213	\N	No Comment	4	2008-07-06 14:55:00	2008-07-06 14:55:00
523	34	195	\N	No Comment	4	2008-07-06 14:55:22	2008-07-06 14:55:22
524	44	213	\N	No Comment	4	2008-07-06 14:55:27	2008-07-06 14:55:27
525	9	212	\N	No Comment	5	2008-07-06 14:55:56	2008-07-06 14:55:56
526	34	196	\N	No Comment	5	2008-07-06 14:56:07	2008-07-06 14:56:07
527	44	212	\N	No Comment	5	2008-07-06 14:56:26	2008-07-06 14:56:26
528	39	195	\N	No Comment	3	2008-07-06 14:56:47	2008-07-06 14:56:47
529	54	214	\N	No Comment	4	2008-07-06 14:56:55	2008-07-06 14:56:55
530	9	214	\N	No Comment	3	2008-07-06 14:57:28	2008-07-06 14:57:28
531	25	239	\N	No Comment	2	2008-07-06 14:57:53	2008-07-06 14:57:53
532	21	220	\N	No Comment	3	2008-07-06 14:58:42	2008-07-06 14:58:42
533	25	241	\N	No Comment	4	2008-07-06 14:58:47	2008-07-06 14:58:47
534	64	220	\N	No Comment	3	2008-07-06 14:59:19	2008-07-06 14:59:19
535	2	239	\N	No Comment	2	2008-07-06 14:59:29	2008-07-06 14:59:29
536	13	218	\N	No Comment	4	2008-07-06 14:59:46	2008-07-06 14:59:46
537	2	240	\N	No Comment	4	2008-07-06 15:00:17	2008-07-06 15:00:17
538	64	218	\N	No Comment	4	2008-07-06 15:00:20	2008-07-06 15:00:20
539	4	\N	224	No Comment	4	2008-07-06 15:01:24	2008-07-06 15:01:24
540	70	240	\N	No Comment	4	2008-07-06 15:01:34	2008-07-06 15:01:34
541	70	241	\N	No Comment	4	2008-07-06 15:02:17	2008-07-06 15:02:17
542	22	182	\N	No Comment	3	2008-07-06 15:03:24	2008-07-06 15:03:24
469	68	187	\N	Jake says to upgrade her	5	2008-07-06 14:37:50	2008-07-06 14:37:50
544	62	\N	263	No Comment	5	2008-07-06 15:55:32	2008-07-06 15:55:32
545	6	\N	353	No Comment	3	2008-07-06 16:55:48	2008-07-06 16:55:48
546	4	\N	325	No Comment	4	2008-07-06 16:55:58	2008-07-06 16:55:58
547	6	\N	354	No Comment	4	2008-07-06 16:56:33	2008-07-06 16:56:33
548	40	\N	355	No Comment	5	2008-07-06 16:57:26	2008-07-06 16:57:26
549	4	\N	326	No Comment	4	2008-07-06 16:58:10	2008-07-06 16:58:10
550	40	\N	356	No Comment	2	2008-07-06 16:58:25	2008-07-06 16:58:25
553	50	\N	351	No Comment	4	2008-07-06 17:02:05	2008-07-06 17:02:05
555	50	\N	352	did not take the effort to even listen to our speech, ie wasting time staring out the window for 2 minutes. did not write our points, even if did, not everything. she looks back to her very few notes to give adj as if forgot what happened - not really forgot we think but she took very few notes at the first place. she said their argument "sort of that" , "sort of this" your rebuttal "sort of" this or that, the debate "sort of" that. what a "sort of" adjudication	1	2008-07-06 17:03:17	2008-07-06 17:03:17
557	3	\N	343	No Comment	3	2008-07-06 17:04:00	2008-07-06 17:04:00
558	3	\N	344	No Comment	4	2008-07-06 17:04:28	2008-07-06 17:04:28
559	12	\N	319	Very thorough and very careful not to enter the debate.	4	2008-07-06 17:04:51	2008-07-06 17:04:51
560	35	\N	302	Jake had good, well-explained reasons for his decisions, but ultimately we're convinced he misunderstood the importance of the issues of clash between teams. That being said, he's still pretty good	4	2008-07-06 17:06:08	2008-07-06 17:06:08
561	12	\N	320	Agree with the decision. However feel that some arguments were not considered because of personal knowledge of the situation. Feedback and oral adjudication still good.	3	2008-07-06 17:06:14	2008-07-06 17:06:14
562	35	\N	301	tell decision at the start	4	2008-07-06 17:06:57	2008-07-06 17:06:57
563	39	\N	336	No Comment	5	2008-07-06 17:07:05	2008-07-06 17:07:05
564	34	\N	297	cursary adjudication	3	2008-07-06 17:07:38	2008-07-06 17:07:38
565	39	\N	335	No Comment	5	2008-07-06 17:07:43	2008-07-06 17:07:43
566	31	\N	334	No Comment	4	2008-07-06 17:08:35	2008-07-06 17:08:35
567	31	\N	333	No Comment	3	2008-07-06 17:09:06	2008-07-06 17:09:06
568	38	\N	321	No Comment	5	2008-07-06 17:09:32	2008-07-06 17:09:32
569	38	\N	322	No Comment	4	2008-07-06 17:10:11	2008-07-06 17:10:11
570	11	\N	323	No Comment	5	2008-07-06 17:10:55	2008-07-06 17:10:55
571	11	\N	324	No Comment	5	2008-07-06 17:11:19	2008-07-06 17:11:19
572	37	\N	307	No Comment	5	2008-07-06 17:11:49	2008-07-06 17:11:49
573	37	\N	308	No Comment	4	2008-07-06 17:12:17	2008-07-06 17:12:17
574	13	\N	369	No Comment	4	2008-07-06 17:12:47	2008-07-06 17:12:47
575	13	\N	370	No Comment	4	2008-07-06 17:13:27	2008-07-06 17:13:27
576	62	\N	359	No Comment	2	2008-07-06 17:13:47	2008-07-06 17:13:47
577	33	\N	349	No Comment	4	2008-07-06 17:14:10	2008-07-06 17:14:10
578	33	\N	350	No Comment	1	2008-07-06 17:14:39	2008-07-06 17:14:39
579	62	\N	360	No Comment	2	2008-07-06 17:15:43	2008-07-06 17:15:43
580	53	\N	347	No Comment	3	2008-07-06 17:16:32	2008-07-06 17:16:32
581	19	\N	367	No Comment	4	2008-07-06 17:16:53	2008-07-06 17:16:53
582	53	\N	348	No Comment	4	2008-07-06 17:16:59	2008-07-06 17:16:59
583	44	\N	358	No Comment	4	2008-07-06 17:18:40	2008-07-06 17:18:40
584	59	\N	317	- The emphasis placed on how an issue ought to be proven seemed to be slightly unreasonable	3	2008-07-06 17:19:02	2008-07-06 17:19:02
585	44	\N	357	No Comment	3	2008-07-06 17:19:05	2008-07-06 17:19:05
586	67	\N	341	No Comment	3	2008-07-06 17:20:13	2008-07-06 17:20:13
587	67	\N	342	No Comment	5	2008-07-06 17:20:41	2008-07-06 17:20:41
588	36	\N	328	No Comment	3	2008-07-06 17:21:10	2008-07-06 17:21:10
589	59	\N	318	really good identification and discussion of issues|| made us think "wow"- excellent	5	2008-07-06 17:21:51	2008-07-06 17:21:51
590	55	\N	332	No Comment	1	2008-07-06 17:22:15	2008-07-06 17:22:15
591	41	\N	339	No Comment	4	2008-07-06 17:22:42	2008-07-06 17:22:42
592	55	\N	331	No Comment	4	2008-07-06 17:22:51	2008-07-06 17:22:51
593	17	\N	329	No Comment	5	2008-07-06 17:23:31	2008-07-06 17:23:31
594	41	\N	340	No Comment	2	2008-07-06 17:23:44	2008-07-06 17:23:44
595	17	\N	330	No Comment	5	2008-07-06 17:23:58	2008-07-06 17:23:58
596	58	\N	346	No Comment	3	2008-07-06 17:24:45	2008-07-06 17:24:45
597	71	\N	300	No Comment	4	2008-07-06 17:25:03	2008-07-06 17:25:03
598	58	\N	345	No Comment	3	2008-07-06 17:25:16	2008-07-06 17:25:16
599	51	\N	366	No Comment	3	2008-07-06 17:25:57	2008-07-06 17:25:57
600	71	\N	299	No Comment	4	2008-07-06 17:25:59	2008-07-06 17:25:59
601	71	\N	299	No Comment	4	2008-07-06 17:26:26	2008-07-06 17:26:26
602	51	\N	365	No Comment	4	2008-07-06 17:27:11	2008-07-06 17:27:11
603	24	\N	313	No Comment	1	2008-07-06 17:27:53	2008-07-06 17:27:53
604	16	\N	361	No Comment	3	2008-07-06 17:28:11	2008-07-06 17:28:11
605	16	\N	362	No Comment	2	2008-07-06 17:28:40	2008-07-06 17:28:40
606	3	274	\N	No Comment	4	2008-07-06 17:29:49	2008-07-06 17:29:49
607	24	\N	314	This was a very messy debate and Angie was excellent at picking out and explaining the key issues that each team won, lost, and could improve on	5	2008-07-06 17:29:58	2008-07-06 17:29:58
608	60	274	\N	No Comment	3	2008-07-06 17:30:25	2008-07-06 17:30:25
609	2	272	\N	No Comment	3	2008-07-06 17:30:59	2008-07-06 17:30:59
610	49	\N	363	No Comment	4	2008-07-06 17:31:01	2008-07-06 17:31:01
611	60	272	\N	No Comment	2	2008-07-06 17:31:59	2008-07-06 17:31:59
612	49	\N	364	No Comment	1	2008-07-06 17:32:14	2008-07-06 17:32:14
613	64	284	\N	No Comment	3	2008-07-06 17:33:15	2008-07-06 17:33:15
614	51	300	\N	No Comment	4	2008-07-06 17:33:32	2008-07-06 17:33:32
615	1	284	\N	No Comment	3	2008-07-06 17:34:07	2008-07-06 17:34:07
616	64	286	\N	No Comment	3	2008-07-06 17:34:34	2008-07-06 17:34:34
617	18	300	\N	No Comment	3	2008-07-06 17:34:42	2008-07-06 17:34:42
618	18	299	\N	No Comment	3	2008-07-06 17:35:36	2008-07-06 17:35:36
619	40	286	\N	No Comment	3	2008-07-06 17:35:40	2008-07-06 17:35:40
620	1	285	\N	No Comment	2	2008-07-06 17:36:12	2008-07-06 17:36:12
621	40	285	\N	No Comment	2	2008-07-06 17:37:10	2008-07-06 17:37:10
622	29	299	\N	No Comment	2	2008-07-06 17:37:14	2008-07-06 17:37:14
623	45	281	\N	No Comment	4	2008-07-06 17:38:00	2008-07-06 17:38:00
624	51	301	\N	No Comment	4	2008-07-06 17:38:16	2008-07-06 17:38:16
625	70	281	\N	No Comment	3	2008-07-06 17:38:27	2008-07-06 17:38:27
626	70	282	\N	No Comment	4	2008-07-06 17:38:56	2008-07-06 17:38:56
627	29	301	\N	No Comment	3	2008-07-06 17:39:03	2008-07-06 17:39:03
628	6	282	\N	No Comment	4	2008-07-06 17:39:44	2008-07-06 17:39:44
629	15	290	\N	No Comment	3	2008-07-06 17:40:09	2008-07-06 17:40:09
630	6	283	\N	good analysis but well over 10 minutes	3	2008-07-06 17:40:31	2008-07-06 17:40:31
631	45	283	\N	No Comment	3	2008-07-06 17:41:11	2008-07-06 17:41:11
632	9	290	\N	No Comment	3	2008-07-06 17:41:14	2008-07-06 17:41:14
633	13	307	\N	No Comment	2	2008-07-06 17:42:15	2008-07-06 17:42:15
634	22	307	\N	No Comment	3	2008-07-06 17:42:52	2008-07-06 17:42:52
635	13	306	\N	No Comment	3	2008-07-06 17:44:26	2008-07-06 17:44:26
636	15	292	\N	No Comment	4	2008-07-06 17:44:31	2008-07-06 17:44:31
637	63	306	\N	No Comment	2	2008-07-06 17:45:16	2008-07-06 17:45:16
638	44	292	\N	No Comment	5	2008-07-06 17:45:36	2008-07-06 17:45:36
639	22	305	\N	No Comment	2	2008-07-06 17:45:57	2008-07-06 17:45:57
640	9	291	\N	No Comment	3	2008-07-06 17:46:31	2008-07-06 17:46:31
641	63	305	\N	No Comment	2	2008-07-06 17:46:38	2008-07-06 17:46:38
642	44	291	\N	No Comment	4	2008-07-06 17:47:46	2008-07-06 17:47:46
643	20	287	\N	No Comment	3	2008-07-06 17:47:49	2008-07-06 17:47:49
644	10	287	\N	No Comment	3	2008-07-06 17:48:34	2008-07-06 17:48:34
645	21	279	\N	No Comment	3	2008-07-06 17:48:47	2008-07-06 17:48:47
646	21	279	\N	No Comment	3	2008-07-06 17:49:04	2008-07-06 17:49:04
647	20	289	\N	No Comment	4	2008-07-06 17:49:11	2008-07-06 17:49:11
648	21	279	\N	No Comment	3	2008-07-06 17:49:27	2008-07-06 17:49:27
649	62	289	\N	No Comment	4	2008-07-06 17:50:00	2008-07-06 17:50:00
650	10	288	\N	No Comment	2	2008-07-06 17:50:42	2008-07-06 17:50:42
651	16	279	\N	No Comment	3	2008-07-06 17:50:49	2008-07-06 17:50:49
652	62	288	\N	No Comment	4	2008-07-06 17:51:19	2008-07-06 17:51:19
653	56	278	\N	No Comment	3	2008-07-06 17:51:39	2008-07-06 17:51:39
654	21	278	\N	No Comment	2	2008-07-06 17:52:29	2008-07-06 17:52:29
655	25	303	\N	No Comment	3	2008-07-06 17:52:52	2008-07-06 17:52:52
656	19	303	\N	No Comment	5	2008-07-06 17:53:20	2008-07-06 17:53:20
657	56	280	\N	No Comment	5	2008-07-06 17:53:37	2008-07-06 17:53:37
658	66	304	\N	No Comment	4	2008-07-06 17:53:51	2008-07-06 17:53:51
659	16	280	\N	No Comment	5	2008-07-06 17:54:24	2008-07-06 17:54:24
660	19	304	\N	No Comment	4	2008-07-06 17:54:26	2008-07-06 17:54:26
661	66	302	\N	No Comment	3	2008-07-06 17:55:03	2008-07-06 17:55:03
662	25	302	\N	No Comment	2	2008-07-06 17:55:28	2008-07-06 17:55:28
663	28	298	\N	No Comment	3	2008-07-06 17:55:30	2008-07-06 17:55:30
664	30	267	\N	No Comment	2	2008-07-06 17:56:35	2008-07-06 17:56:35
665	57	267	\N	No Comment	5	2008-07-06 17:57:18	2008-07-06 17:57:18
666	30	268	\N	No Comment	2	2008-07-06 17:57:53	2008-07-06 17:57:53
667	54	268	\N	No Comment	5	2008-07-06 17:58:29	2008-07-06 17:58:29
668	67	270	\N	No Comment	5	2008-07-06 17:59:18	2008-07-06 17:59:18
669	61	270	\N	No Comment	3	2008-07-06 18:00:00	2008-07-06 18:00:00
670	67	271	\N	No Comment	4	2008-07-06 18:00:31	2008-07-06 18:00:31
671	14	271	\N	No Comment	2	2008-07-06 18:01:05	2008-07-06 18:01:05
672	14	269	\N	No Comment	3	2008-07-06 18:01:37	2008-07-06 18:01:37
673	61	269	\N	No Comment	3	2008-07-06 18:02:07	2008-07-06 18:02:07
674	50	294	\N	No Comment	4	2008-07-06 18:02:39	2008-07-06 18:02:39
675	69	294	\N	No Comment	3	2008-07-06 18:03:14	2008-07-06 18:03:14
676	47	293	\N	No Comment	3	2008-07-06 18:03:53	2008-07-06 18:03:53
677	69	293	\N	No Comment	3	2008-07-06 18:04:30	2008-07-06 18:04:30
678	28	296	\N	No Comment	3	2008-07-06 18:05:19	2008-07-06 18:05:19
679	48	296	\N	No Comment	3	2008-07-06 18:06:01	2008-07-06 18:06:01
680	48	297	\N	No Comment	2	2008-07-06 18:06:36	2008-07-06 18:06:36
681	49	297	\N	No Comment	4	2008-07-06 18:07:26	2008-07-06 18:07:26
682	49	298	\N	No Comment	4	2008-07-06 18:08:02	2008-07-06 18:08:02
685	14	\N	469	No Comment	3	2008-07-07 14:21:39	2008-07-07 14:21:39
686	14	\N	469	No Comment	3	2008-07-07 14:21:44	2008-07-07 14:21:44
687	57	\N	460	No Comment	3	2008-07-07 14:22:32	2008-07-07 14:22:32
688	1	\N	463	No Comment	4	2008-07-07 14:22:53	2008-07-07 14:22:53
689	6	\N	434	No Comment	3	2008-07-07 14:23:10	2008-07-07 14:23:10
690	6	\N	435	No Comment	4	2008-07-07 14:23:26	2008-07-07 14:23:26
691	56	336	\N	No Comment	5	2008-07-07 14:26:09	2008-07-07 14:26:09
692	56	337	\N	No Comment	4	2008-07-07 14:26:52	2008-07-07 14:26:52
693	38	\N	396	Excellent	5	2008-07-07 14:26:55	2008-07-07 14:26:55
694	54	338	\N	No Comment	4	2008-07-07 14:27:21	2008-07-07 14:27:21
695	38	\N	397	No Comment	5	2008-07-07 14:27:33	2008-07-07 14:27:33
696	12	338	\N	No Comment	3	2008-07-07 14:27:53	2008-07-07 14:27:53
697	12	337	\N	No Comment	5	2008-07-07 14:28:09	2008-07-07 14:28:09
698	57	\N	461	No Comment	5	2008-07-07 14:28:13	2008-07-07 14:28:13
699	54	336	\N	No Comment	3	2008-07-07 14:28:37	2008-07-07 14:28:37
700	1	\N	462	No Comment	5	2008-07-07 14:29:00	2008-07-07 14:29:00
701	12	\N	431	No Comment	4	2008-07-07 14:29:00	2008-07-07 14:29:00
702	12	\N	430	No Comment	4	2008-07-07 14:29:30	2008-07-07 14:29:30
703	1	365	\N	No Comment	5	2008-07-07 14:29:34	2008-07-07 14:29:34
704	45	\N	456	No Comment	4	2008-07-07 14:30:01	2008-07-07 14:30:01
705	1	366	\N	No Comment	3	2008-07-07 14:30:19	2008-07-07 14:30:19
706	45	\N	457	No Comment	5	2008-07-07 14:30:22	2008-07-07 14:30:22
707	16	\N	459	No Comment	4	2008-07-07 14:30:38	2008-07-07 14:30:38
708	16	\N	458	No Comment	4	2008-07-07 14:30:49	2008-07-07 14:30:49
709	50	353	\N	No Comment	3	2008-07-07 14:31:09	2008-07-07 14:31:09
710	28	364	\N	No Comment	5	2008-07-07 14:31:10	2008-07-07 14:31:10
711	51	353	\N	No Comment	3	2008-07-07 14:31:24	2008-07-07 14:31:24
712	51	\N	454	No Comment	3	2008-07-07 14:31:52	2008-07-07 14:31:52
713	51	\N	455	No Comment	4	2008-07-07 14:32:05	2008-07-07 14:32:05
714	50	352	\N	No Comment	5	2008-07-07 14:32:21	2008-07-07 14:32:21
715	28	365	\N	No Comment	4	2008-07-07 14:32:32	2008-07-07 14:32:32
716	64	352	\N	No Comment	3	2008-07-07 14:32:39	2008-07-07 14:32:39
717	60	\N	466	No Comment	3	2008-07-07 14:32:54	2008-07-07 14:32:54
718	66	372	\N	No Comment	3	2008-07-07 14:33:09	2008-07-07 14:33:09
719	60	372	\N	No Comment	3	2008-07-07 14:33:21	2008-07-07 14:33:21
720	10	364	\N	No Comment	3	2008-07-07 14:33:24	2008-07-07 14:33:24
721	2	371	\N	No Comment	4	2008-07-07 14:33:39	2008-07-07 14:33:39
722	60	371	\N	No Comment	5	2008-07-07 14:33:50	2008-07-07 14:33:50
723	11	313	\N	No Comment	5	2008-07-07 14:34:26	2008-07-07 14:34:26
724	33	313	\N	No Comment	4	2008-07-07 14:34:33	2008-07-07 14:34:33
725	10	366	\N	No Comment	3	2008-07-07 14:34:53	2008-07-07 14:34:53
726	11	314	\N	No Comment	5	2008-07-07 14:34:59	2008-07-07 14:34:59
727	3	314	\N	No Comment	2	2008-07-07 14:35:15	2008-07-07 14:35:15
728	11	\N	398	No Comment	4	2008-07-07 14:35:32	2008-07-07 14:35:32
729	69	373	\N	No Comment	3	2008-07-07 14:35:36	2008-07-07 14:35:36
730	33	312	\N	No Comment	5	2008-07-07 14:36:03	2008-07-07 14:36:03
731	3	312	\N	No Comment	3	2008-07-07 14:36:06	2008-07-07 14:36:06
732	29	373	\N	No Comment	2	2008-07-07 14:36:16	2008-07-07 14:36:16
733	11	\N	399	No Comment	4	2008-07-07 14:36:56	2008-07-07 14:36:56
734	29	374	\N	No Comment	2	2008-07-07 14:37:05	2008-07-07 14:37:05
735	15	\N	442	No Comment	1	2008-07-07 14:37:09	2008-07-07 14:37:09
736	55	\N	415	No Comment	5	2008-07-07 14:37:43	2008-07-07 14:37:43
737	53	326	\N	No Comment	5	2008-07-07 14:37:44	2008-07-07 14:37:44
738	15	\N	443	No Comment	4	2008-07-07 14:37:51	2008-07-07 14:37:51
739	24	\N	416	No Comment	5	2008-07-07 14:38:14	2008-07-07 14:38:14
740	24	\N	417	No Comment	4	2008-07-07 14:38:27	2008-07-07 14:38:27
741	58	326	\N	No Comment	5	2008-07-07 14:38:38	2008-07-07 14:38:38
742	67	\N	444	No Comment	5	2008-07-07 14:38:53	2008-07-07 14:38:53
743	41	\N	453	No Comment	2	2008-07-07 14:38:59	2008-07-07 14:38:59
744	14	374	\N	No Comment	4	2008-07-07 14:39:12	2008-07-07 14:39:12
745	67	\N	445	No Comment	4	2008-07-07 14:39:21	2008-07-07 14:39:21
746	5	327	\N	No Comment	5	2008-07-07 14:39:31	2008-07-07 14:39:31
747	36	\N	440	No Comment	5	2008-07-07 14:39:39	2008-07-07 14:39:39
748	36	\N	441	No Comment	4	2008-07-07 14:39:50	2008-07-07 14:39:50
749	70	\N	432	No Comment	3	2008-07-07 14:40:03	2008-07-07 14:40:03
750	58	327	\N	No Comment	5	2008-07-07 14:40:06	2008-07-07 14:40:06
751	70	\N	433	No Comment	5	2008-07-07 14:40:38	2008-07-07 14:40:38
752	76	\N	437	No Comment	4	2008-07-07 14:40:42	2008-07-07 14:40:42
753	5	328	\N	No Comment	5	2008-07-07 14:41:03	2008-07-07 14:41:03
754	76	\N	436	No Comment	3	2008-07-07 14:41:05	2008-07-07 14:41:05
755	45	357	\N	No Comment	4	2008-07-07 14:41:08	2008-07-07 14:41:08
756	34	\N	404	No Comment	5	2008-07-07 14:41:21	2008-07-07 14:41:21
757	53	328	\N	No Comment	5	2008-07-07 14:41:45	2008-07-07 14:41:45
758	34	\N	405	No Comment	3	2008-07-07 14:41:47	2008-07-07 14:41:47
759	17	\N	401	No Comment	4	2008-07-07 14:42:04	2008-07-07 14:42:04
760	17	\N	400	No Comment	4	2008-07-07 14:42:16	2008-07-07 14:42:16
761	71	\N	403	No Comment	5	2008-07-07 14:42:30	2008-07-07 14:42:30
762	9	357	\N	No Comment	2	2008-07-07 14:42:32	2008-07-07 14:42:32
763	71	\N	402	No Comment	5	2008-07-07 14:42:53	2008-07-07 14:42:53
764	35	\N	412	No Comment	5	2008-07-07 14:43:04	2008-07-07 14:43:04
765	35	\N	413	No Comment	5	2008-07-07 14:43:16	2008-07-07 14:43:16
766	20	356	\N	No Comment	4	2008-07-07 14:43:26	2008-07-07 14:43:26
767	41	350	\N	Sid analyzes excellently during discussion - straight to the point. But during oral adjudication he spends too much time re-capping. Kinda long-winded, haha. Its a "4-" :)	4	2008-07-07 14:43:31	2008-07-07 14:43:31
768	62	324	\N	No Comment	5	2008-07-07 14:43:49	2008-07-07 14:43:49
769	24	324	\N	No Comment	5	2008-07-07 14:43:54	2008-07-07 14:43:54
770	13	350	\N	No Comment	4	2008-07-07 14:43:58	2008-07-07 14:43:58
771	45	356	\N	No Comment	5	2008-07-07 14:44:13	2008-07-07 14:44:13
772	62	323	\N	No Comment	4	2008-07-07 14:44:21	2008-07-07 14:44:21
773	30	323	\N	No Comment	4	2008-07-07 14:44:31	2008-07-07 14:44:31
774	24	325	\N	No Comment	5	2008-07-07 14:44:47	2008-07-07 14:44:47
775	30	325	\N	No Comment	3	2008-07-07 14:44:56	2008-07-07 14:44:56
776	21	\N	449	No Comment	1	2008-07-07 14:45:03	2008-07-07 14:45:03
777	25	347	\N	No Comment	2	2008-07-07 14:45:12	2008-07-07 14:45:12
778	20	355	\N	No Comment	3	2008-07-07 14:45:13	2008-07-07 14:45:13
779	25	347	\N	No Comment	3	2008-07-07 14:45:33	2008-07-07 14:45:33
780	21	\N	448	No Comment	4	2008-07-07 14:45:47	2008-07-07 14:45:47
781	61	347	\N	No Comment	3	2008-07-07 14:46:04	2008-07-07 14:46:04
782	39	330	\N	No Comment	5	2008-07-07 14:46:17	2008-07-07 14:46:17
783	9	355	\N	No Comment	3	2008-07-07 14:46:21	2008-07-07 14:46:21
784	44	330	\N	No Comment	5	2008-07-07 14:46:32	2008-07-07 14:46:32
785	16	359	\N	No Comment	3	2008-07-07 14:46:38	2008-07-07 14:46:38
786	44	331	\N	No Comment	3	2008-07-07 14:46:49	2008-07-07 14:46:49
788	39	332	\N	No Comment	3	2008-07-07 14:47:14	2008-07-07 14:47:14
789	22	359	\N	No Comment	2	2008-07-07 14:47:15	2008-07-07 14:47:15
791	63	360	\N	No Comment	3	2008-07-07 14:47:43	2008-07-07 14:47:43
792	21	440	\N	No Comment	4	2008-07-07 14:47:46	2008-07-07 14:47:46
793	25	440	\N	No Comment	2	2008-07-07 14:47:57	2008-07-07 14:47:57
794	49	\N	446	No Comment	4	2008-07-07 14:47:57	2008-07-07 14:47:57
795	16	360	\N	No Comment	3	2008-07-07 14:48:14	2008-07-07 14:48:14
796	61	439	\N	No Comment	4	2008-07-07 14:48:29	2008-07-07 14:48:29
797	21	439	\N	No Comment	4	2008-07-07 14:48:34	2008-07-07 14:48:34
798	63	358	\N	No Comment	3	2008-07-07 14:48:40	2008-07-07 14:48:40
799	49	\N	447	No Comment	4	2008-07-07 14:48:50	2008-07-07 14:48:50
800	37	\N	410	No Comment	5	2008-07-07 14:49:04	2008-07-07 14:49:04
801	22	358	\N	No Comment	2	2008-07-07 14:49:09	2008-07-07 14:49:09
802	37	\N	411	No Comment	5	2008-07-07 14:49:17	2008-07-07 14:49:17
803	14	\N	468	No Comment	4	2008-07-07 14:49:36	2008-07-07 14:49:36
804	59	\N	408	No Comment	5	2008-07-07 14:49:43	2008-07-07 14:49:43
805	14	375	\N	No Comment	3	2008-07-07 14:49:49	2008-07-07 14:49:49
806	51	354	\N	No Comment	4	2008-07-07 14:50:04	2008-07-07 14:50:04
807	69	375	\N	No Comment	3	2008-07-07 14:50:12	2008-07-07 14:50:12
808	47	349	\N	No Comment	3	2008-07-07 14:50:26	2008-07-07 14:50:26
809	41	351	\N	No Comment	4	2008-07-07 14:50:47	2008-07-07 14:50:47
810	13	349	\N	No Comment	3	2008-07-07 14:50:52	2008-07-07 14:50:52
811	59	\N	409	No Comment	4	2008-07-07 14:51:03	2008-07-07 14:51:03
812	47	351	\N	No Comment	3	2008-07-07 14:51:13	2008-07-07 14:51:13
813	57	363	\N	No Comment	4	2008-07-07 14:51:18	2008-07-07 14:51:18
814	48	363	\N	No Comment	2	2008-07-07 14:51:40	2008-07-07 14:51:40
815	18	361	\N	No Comment	3	2008-07-07 14:51:51	2008-07-07 14:51:51
816	48	361	\N	No Comment	2	2008-07-07 14:52:00	2008-07-07 14:52:00
817	57	362	\N	No Comment	4	2008-07-07 14:52:03	2008-07-07 14:52:03
818	4	\N	406	No Comment	4	2008-07-07 14:52:04	2008-07-07 14:52:04
819	18	362	\N	No Comment	3	2008-07-07 14:52:34	2008-07-07 14:52:34
820	19	\N	465	No Comment	3	2008-07-07 14:52:51	2008-07-07 14:52:51
821	19	\N	464	No Comment	2	2008-07-07 14:53:09	2008-07-07 14:53:09
822	4	\N	407	No Comment	5	2008-07-07 14:53:27	2008-07-07 14:53:27
823	65	367	\N	No Comment	2	2008-07-07 14:53:28	2008-07-07 14:53:28
824	68	367	\N	No Comment	2	2008-07-07 14:53:53	2008-07-07 14:53:53
825	19	368	\N	No Comment	3	2008-07-07 14:54:11	2008-07-07 14:54:11
826	31	\N	438	No Comment	4	2008-07-07 14:54:30	2008-07-07 14:54:30
827	5	\N	423	No Comment	5	2008-07-07 14:54:53	2008-07-07 14:54:53
828	5	\N	422	No Comment	4	2008-07-07 14:55:18	2008-07-07 14:55:18
829	31	\N	439	No Comment	4	2008-07-07 14:55:29	2008-07-07 14:55:29
830	40	\N	451	No Comment	4	2008-07-07 14:57:19	2008-07-07 14:57:19
831	33	455	\N	No Comment	5	2008-07-07 17:14:30	2008-07-07 17:14:30
832	3	455	\N	No Comment	4	2008-07-07 17:14:48	2008-07-07 17:14:48
833	33	454	\N	No Comment	4	2008-07-07 17:15:07	2008-07-07 17:15:07
834	70	454	\N	No Comment	3	2008-07-07 17:15:30	2008-07-07 17:15:30
835	3	453	\N	No Comment	2	2008-07-07 17:15:48	2008-07-07 17:15:48
836	70	453	\N	No Comment	3	2008-07-07 17:16:05	2008-07-07 17:16:05
837	67	479	\N	No Comment	4	2008-07-07 17:16:25	2008-07-07 17:16:25
838	49	479	\N	No Comment	4	2008-07-07 17:16:47	2008-07-07 17:16:47
839	53	481	\N	No Comment	3	2008-07-07 17:17:15	2008-07-07 17:17:15
840	67	481	\N	No Comment	4	2008-07-07 17:17:38	2008-07-07 17:17:38
841	49	480	\N	No Comment	4	2008-07-07 17:17:54	2008-07-07 17:17:54
842	53	480	\N	No Comment	4	2008-07-07 17:18:10	2008-07-07 17:18:10
843	61	497	\N	No Comment	3	2008-07-07 17:18:32	2008-07-07 17:18:32
844	43	497	\N	No Comment	2	2008-07-07 17:18:55	2008-07-07 17:18:55
845	18	499	\N	No Comment	3	2008-07-07 17:19:24	2008-07-07 17:19:24
846	43	499	\N	No Comment	3	2008-07-07 17:19:45	2008-07-07 17:19:45
847	18	498	\N	No Comment	2	2008-07-07 17:20:04	2008-07-07 17:20:04
848	61	498	\N	No Comment	2	2008-07-07 17:20:27	2008-07-07 17:20:27
849	60	495	\N	No Comment	5	2008-07-07 17:21:09	2008-07-07 17:21:09
850	20	495	\N	No Comment	5	2008-07-07 17:21:35	2008-07-07 17:21:35
851	66	496	\N	No Comment	5	2008-07-07 17:21:53	2008-07-07 17:21:53
852	20	496	\N	No Comment	5	2008-07-07 17:22:13	2008-07-07 17:22:13
853	66	494	\N	No Comment	3	2008-07-07 17:22:36	2008-07-07 17:22:36
854	60	494	\N	No Comment	4	2008-07-07 17:22:56	2008-07-07 17:22:56
855	19	491	\N	No Comment	2	2008-07-07 17:23:18	2008-07-07 17:23:18
856	10	491	\N	No Comment	2	2008-07-07 17:23:40	2008-07-07 17:23:40
857	19	492	\N	No Comment	4	2008-07-07 17:24:00	2008-07-07 17:24:00
858	13	492	\N	No Comment	4	2008-07-07 17:24:21	2008-07-07 17:24:21
859	13	493	\N	No Comment	2	2008-07-07 17:24:39	2008-07-07 17:24:39
860	10	493	\N	No Comment	3	2008-07-07 17:25:00	2008-07-07 17:25:00
861	65	482	\N	No Comment	4	2008-07-07 17:25:19	2008-07-07 17:25:19
862	63	482	\N	No Comment	4	2008-07-07 17:25:50	2008-07-07 17:25:50
863	48	484	\N	No Comment	4	2008-07-07 17:26:10	2008-07-07 17:26:10
864	63	484	\N	No Comment	3	2008-07-07 17:26:28	2008-07-07 17:26:28
865	48	483	\N	No Comment	3	2008-07-07 17:26:47	2008-07-07 17:26:47
866	65	483	\N	No Comment	3	2008-07-07 17:27:04	2008-07-07 17:27:04
867	62	478	\N	No Comment	3	2008-07-07 17:27:22	2008-07-07 17:27:22
868	54	478	\N	No Comment	4	2008-07-07 17:27:41	2008-07-07 17:27:41
869	44	477	\N	No Comment	5	2008-07-07 17:27:57	2008-07-07 17:27:57
870	62	477	\N	No Comment	5	2008-07-07 17:28:14	2008-07-07 17:28:14
871	47	467	\N	No Comment	3	2008-07-07 17:28:22	2008-07-07 17:28:22
872	44	476	\N	No Comment	3	2008-07-07 17:28:31	2008-07-07 17:28:31
873	54	476	\N	No Comment	3	2008-07-07 17:28:50	2008-07-07 17:28:50
874	45	467	\N	No Comment	3	2008-07-07 17:29:02	2008-07-07 17:29:02
875	24	469	\N	No Comment	5	2008-07-07 17:29:49	2008-07-07 17:29:49
876	56	464	\N	saw big issues in a close and messy debate same as me. We just had slightly different preferences for particular argumentation. Debate should have been a split and that's fine	4	2008-07-07 17:30:11	2008-07-07 17:30:11
877	40	464	\N	had a very different scoring range to me and pat. saw it as a smacking and not close and neg won no issues, which was garbage	2	2008-07-07 17:31:19	2008-07-07 17:31:19
878	47	469	\N	No Comment	4	2008-07-07 17:31:34	2008-07-07 17:31:34
879	56	466	\N	No Comment	3	2008-07-07 17:31:35	2008-07-07 17:31:35
880	31	466	\N	No Comment	2	2008-07-07 17:32:00	2008-07-07 17:32:00
881	31	465	\N	No Comment	5	2008-07-07 17:32:21	2008-07-07 17:32:21
882	40	465	\N	No Comment	2	2008-07-07 17:32:35	2008-07-07 17:32:35
883	17	462	\N	No Comment	5	2008-07-07 17:33:02	2008-07-07 17:33:02
884	14	462	\N	No Comment	4	2008-07-07 17:33:18	2008-07-07 17:33:18
885	17	463	\N	No Comment	5	2008-07-07 17:33:40	2008-07-07 17:33:40
886	15	463	\N	No Comment	4	2008-07-07 17:33:56	2008-07-07 17:33:56
887	14	461	\N	No Comment	4	2008-07-07 17:34:15	2008-07-07 17:34:15
888	15	461	\N	No Comment	3	2008-07-07 17:34:32	2008-07-07 17:34:32
889	58	475	\N	No Comment	5	2008-07-07 17:35:08	2008-07-07 17:35:08
890	6	475	\N	No Comment	4	2008-07-07 17:35:28	2008-07-07 17:35:28
891	21	474	\N	No Comment	2	2008-07-07 17:35:49	2008-07-07 17:35:49
892	58	474	\N	No Comment	4	2008-07-07 17:36:06	2008-07-07 17:36:06
893	6	473	\N	No Comment	4	2008-07-07 17:36:22	2008-07-07 17:36:22
894	21	473	\N	No Comment	4	2008-07-07 17:36:38	2008-07-07 17:36:38
895	22	489	\N	No Comment	3	2008-07-07 17:36:58	2008-07-07 17:36:58
896	9	489	\N	No Comment	4	2008-07-07 17:37:17	2008-07-07 17:37:17
897	9	490	\N	No Comment	3	2008-07-07 17:37:37	2008-07-07 17:37:37
898	25	490	\N	No Comment	2	2008-07-07 17:37:58	2008-07-07 17:37:58
899	22	488	\N	No Comment	3	2008-07-07 17:38:18	2008-07-07 17:38:18
900	25	488	\N	No Comment	2	2008-07-07 17:38:36	2008-07-07 17:38:36
901	30	470	\N	No Comment	2	2008-07-07 17:38:53	2008-07-07 17:38:53
902	57	470	\N	No Comment	4	2008-07-07 17:39:10	2008-07-07 17:39:10
903	36	472	\N	No Comment	4	2008-07-07 17:39:27	2008-07-07 17:39:27
904	30	472	\N	No Comment	2	2008-07-07 17:39:44	2008-07-07 17:39:44
905	36	471	\N	No Comment	4	2008-07-07 17:40:26	2008-07-07 17:40:26
906	57	471	\N	No Comment	3	2008-07-07 17:40:42	2008-07-07 17:40:42
907	24	468	\N	No Comment	4	2008-07-07 17:41:28	2008-07-07 17:41:28
908	45	468	\N	No Comment	4	2008-07-07 17:41:53	2008-07-07 17:41:53
\.


--
-- Data for Name: adjudicators; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY adjudicators (id, name, test_score, institution_id, active, created_at, updated_at) FROM stdin;
1	Peter Isaac Simon	2	1	t	2008-07-04 17:20:52	2008-07-04 17:20:52
2	Suttichart Denpruektam	1	1	t	2008-07-04 17:20:53	2008-07-04 17:20:53
3	Bernadette Angangco	4	2	t	2008-07-04 17:20:53	2008-07-04 17:20:53
4	Eleanor Uy	4	2	t	2008-07-04 17:20:53	2008-07-04 17:20:53
6	Wyndale Wong	3	2	t	2008-07-04 17:20:53	2008-07-04 17:20:53
8	Leloy Claudio	5	2	t	2008-07-04 17:20:53	2008-07-04 17:20:53
12	Jason Jarvis	4	5	t	2008-07-04 17:20:54	2008-07-04 17:20:54
13	Princess Parenas	2	6	t	2008-07-04 17:20:55	2008-07-04 17:20:55
14	Robin Garcia	2	6	t	2008-07-04 17:20:55	2008-07-04 17:20:55
15	Joeven Castro	2	8	t	2008-07-04 17:20:55	2008-07-04 17:20:55
16	Mark Ysla	3	8	t	2008-07-04 17:20:55	2008-07-04 17:20:55
17	Mohd Sani Mohd Ismail	4	10	t	2008-07-04 17:20:55	2008-07-04 17:20:55
18	Ami Rozaidi Chik Ros	2	10	t	2008-07-04 17:20:56	2008-07-04 17:20:56
20	Emi Yasukawa	2	13	t	2008-07-04 17:20:56	2008-07-04 17:20:56
22	Miku Hagihara	1	13	t	2008-07-04 17:20:56	2008-07-04 17:20:56
24	Angie	4	14	t	2008-07-04 17:20:56	2008-07-04 17:20:56
25	Julian	1	14	t	2008-07-04 17:20:56	2008-07-04 17:20:56
28	Daniel Moremong	2	15	t	2008-07-04 17:20:57	2008-07-04 17:20:57
29	Mo Chen	2	16	t	2008-07-04 17:20:57	2008-07-04 17:20:57
30	Christopher Lum	4	17	t	2008-07-04 17:20:57	2008-07-04 17:20:57
33	Collette Mintz	3	18	t	2008-07-04 17:20:58	2008-07-04 17:20:58
35	Jake Clifton	4	18	t	2008-07-04 17:20:58	2008-07-04 17:20:58
36	Julian Campbell	4	18	t	2008-07-04 17:20:58	2008-07-04 17:20:58
39	Melissa Matteo	4	18	t	2008-07-04 17:20:58	2008-07-04 17:20:58
40	Anindita Pal	3	20	t	2008-07-04 17:20:59	2008-07-04 17:20:59
41	Siddharth Trivedi	2	20	t	2008-07-04 17:20:59	2008-07-04 17:20:59
43	Gordon Ho	1	22	t	2008-07-04 17:20:59	2008-07-04 17:20:59
44	Romita Das	3	22	t	2008-07-04 17:20:59	2008-07-04 17:20:59
45	Loke Wing Fatt	3	23	t	2008-07-04 17:20:59	2008-07-04 17:20:59
46	Chang Mei Yee	1	25	t	2008-07-04 17:21:00	2008-07-04 17:21:00
47	Genevieve Antono	2	26	t	2008-07-04 17:21:00	2008-07-04 17:21:00
48	Brandy Tsang	2	29	t	2008-07-04 17:21:01	2008-07-04 17:21:01
49	Catherine Richardson	2	31	t	2008-07-04 17:21:01	2008-07-04 17:21:01
50	Helen Miller	2	31	t	2008-07-04 17:21:01	2008-07-04 17:21:01
51	Jonathan Humphrey	2	31	t	2008-07-04 17:21:01	2008-07-04 17:21:01
52	Rob Leeds	5	31	t	2008-07-04 17:21:01	2008-07-04 17:21:01
54	Eliza Forsyth	3	33	t	2008-07-04 17:21:02	2008-07-04 17:21:02
56	Patrick Wall	3	33	t	2008-07-04 17:21:02	2008-07-04 17:21:02
57	Paul Karp	3	33	t	2008-07-04 17:21:02	2008-07-04 17:21:02
58	Rohan Grey	4	33	t	2008-07-04 17:21:02	2008-07-04 17:21:02
59	Ivan Ah Sam	4	33	t	2008-07-04 17:21:02	2008-07-04 17:21:02
63	Eng Shueu Ni	1	35	t	2008-07-04 17:21:03	2008-07-04 17:21:03
64	Narendran Ramasenderan	3	35	t	2008-07-04 17:21:03	2008-07-04 17:21:03
65	Nicholas Smith	1	36	t	2008-07-04 17:21:03	2008-07-04 17:21:03
66	Rebecca Jenkins	1	36	t	2008-07-04 17:21:03	2008-07-04 17:21:03
67	Jeremy Rich	2	37	t	2008-07-04 17:21:04	2008-07-04 17:21:04
69	Brent Perry	2	40	t	2008-07-04 17:21:04	2008-07-04 17:21:04
70	Nigel Smith	3	40	t	2008-07-04 17:21:04	2008-07-04 17:21:04
71	Sayeqa Islam	4	40	t	2008-07-04 17:21:04	2008-07-04 17:21:04
72	Izham Ibrahim	1	41	t	2008-07-04 17:21:05	2008-07-04 17:21:05
11	Logandran Balavijendran	4	5	t	2008-07-04 17:20:54	2008-07-04 17:27:36
38	Tom Chapman	4	18	t	2008-07-04 17:20:58	2008-07-04 17:28:51
31	Stephen Worcester	4	17	t	2008-07-04 17:20:57	2008-07-04 17:29:51
62	Adiba Shareen	4	34	t	2008-07-04 17:21:03	2008-07-04 17:30:37
34	Fiona Prowse	4	18	t	2008-07-04 17:20:58	2008-07-04 17:31:56
55	Elizabeth Ames	4	33	t	2008-07-04 17:21:02	2008-07-04 17:33:12
9	Jessie Chuen	3	4	t	2008-07-04 17:20:54	2008-07-04 17:33:49
19	Jonathan Borock	2	12	t	2008-07-04 17:20:56	2008-07-04 17:35:40
61	Nurul Rafeeza Hamdan	2	34	t	2008-07-04 17:21:03	2008-07-04 17:36:24
60	Faiz Arshad(Masai)	2	34	t	2008-07-04 17:21:03	2008-07-04 17:37:01
68	Nor Ashikin Mohammad Yusof	1	39	t	2008-07-04 17:21:04	2008-07-04 17:38:11
7	Bobby Benedicto	5	2	t	2008-07-04 17:20:53	2008-07-04 18:37:15
26	Tate	5	14	t	2008-07-04 17:20:56	2008-07-04 18:37:35
37	Tim Sonnreich	4	18	t	2008-07-04 17:20:58	2008-07-29 10:18:25
21	Masako Suzuki	3	13	t	2008-07-04 17:20:56	2008-07-29 10:22:22
73	Ser Martin	4	30	f	2008-07-29 10:28:22	2008-07-29 10:29:25
74	Ray Aguas	4	2	f	2008-07-29 10:33:25	2008-07-29 10:33:25
75	Darren	2	2	f	2008-07-29 11:50:15	2008-07-29 11:52:21
32	Elizabeth Sheargold	5	17	t	2008-07-04 17:20:57	2008-07-29 15:21:45
10	Lui Lok Hang Lorraine	3	4	t	2008-07-04 17:20:54	2008-07-29 17:12:39
53	Arlene Maneja	4	32	t	2008-07-04 17:21:02	2008-07-29 17:13:45
5	Jess Lopez	4	2	t	2008-07-04 17:20:53	2008-07-29 17:14:52
76	Wilfred	4	2	t	2008-07-06 10:33:07	2008-07-06 10:33:07
23	Ryo Takikawa	2	13	f	2008-07-04 17:20:56	2008-07-08 11:01:28
\.


--
-- Data for Name: debaters; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY debaters (id, name, team_id, created_at, updated_at) FROM stdin;
1	Aishwarya Nair	1	2008-07-04 17:20:52	2008-07-04 17:20:52
2	Farai Ngoni Bhima	1	2008-07-04 17:20:52	2008-07-04 17:20:52
3	Yutian Cynthia Luo	1	2008-07-04 17:20:52	2008-07-04 17:20:52
4	Karnnadda Senarak	2	2008-07-04 17:20:52	2008-07-04 17:20:52
5	Supanida Sripumbang	2	2008-07-04 17:20:52	2008-07-04 17:20:52
6	Tanyanan Songprasit	2	2008-07-04 17:20:52	2008-07-04 17:20:52
7	Charisse Borromeo	3	2008-07-04 17:20:53	2008-07-04 17:20:53
8	Kip Oebanda	3	2008-07-04 17:20:53	2008-07-04 17:20:53
9	Sharmila Parmanand	3	2008-07-04 17:20:53	2008-07-04 17:20:53
10	Angelica Simone Mangahas	4	2008-07-04 17:20:53	2008-07-04 17:20:53
11	Miko Biscocho	4	2008-07-04 17:20:53	2008-07-04 17:20:53
12	Stephanie Co	4	2008-07-04 17:20:53	2008-07-04 17:20:53
13	Ely Zosa	5	2008-07-04 17:20:53	2008-07-04 17:20:53
14	Pauline Gairanod	5	2008-07-04 17:20:53	2008-07-04 17:20:53
15	Vincenzo Tagle	5	2008-07-04 17:20:53	2008-07-04 17:20:53
16	Danielle De Castro	6	2008-07-04 17:20:53	2008-07-04 17:20:53
17	Peterson Poon	6	2008-07-04 17:20:53	2008-07-04 17:20:53
18	Shiveena Parmanand	6	2008-07-04 17:20:53	2008-07-04 17:20:53
19	Cecile Danica Gotamco	7	2008-07-04 17:20:53	2008-07-04 17:20:53
20	Jasmine Cruz	7	2008-07-04 17:20:53	2008-07-04 17:20:53
21	Jonathan David Chu	7	2008-07-04 17:20:53	2008-07-04 17:20:53
22	Katrina Gonzalez	8	2008-07-04 17:20:53	2008-07-04 17:20:53
23	Nathaniel Oducado	8	2008-07-04 17:20:53	2008-07-04 17:20:53
24	Paulyn Quiza	8	2008-07-04 17:20:53	2008-07-04 17:20:53
27	Kwan Yeng Chan Arnold	9	2008-07-04 17:20:54	2008-07-04 17:20:54
28	Joyce Lam	10	2008-07-04 17:20:54	2008-07-04 17:20:54
29	Dorianne Lau	10	2008-07-04 17:20:54	2008-07-04 17:20:54
30	Tsz Kwan Chu	10	2008-07-04 17:20:54	2008-07-04 17:20:54
31	Ernesto Carella	11	2008-07-04 17:20:54	2008-07-04 17:20:54
32	Hoi Ling Mak	11	2008-07-04 17:20:54	2008-07-04 17:20:54
33	Chong Tanna	11	2008-07-04 17:20:54	2008-07-04 17:20:54
34	Gina Kim	12	2008-07-04 17:20:54	2008-07-04 17:20:54
35	Stella Roh	12	2008-07-04 17:20:54	2008-07-04 17:20:54
36	Sohye Yoon	12	2008-07-04 17:20:54	2008-07-04 17:20:54
37	Sujin Sim	13	2008-07-04 17:20:54	2008-07-04 17:20:54
38	Jimin Cha	13	2008-07-04 17:20:54	2008-07-04 17:20:54
39	Jeong Min Jeh	13	2008-07-04 17:20:54	2008-07-04 17:20:54
40	Eun Joo Jun	14	2008-07-04 17:20:54	2008-07-04 17:20:54
41	Hye Jin Huh	14	2008-07-04 17:20:54	2008-07-04 17:20:54
42	Hyo Sun Joo	14	2008-07-04 17:20:54	2008-07-04 17:20:54
43	Dino de Leon	15	2008-07-04 17:20:54	2008-07-04 17:20:54
44	Bianca Lagdameo	15	2008-07-04 17:20:54	2008-07-04 17:20:54
45	Robin Sebolino	15	2008-07-04 17:20:54	2008-07-04 17:20:54
46	Carlito Reyes	16	2008-07-04 17:20:54	2008-07-04 17:20:54
47	Enrique Yap	16	2008-07-04 17:20:54	2008-07-04 17:20:54
48	Angela Vargas	16	2008-07-04 17:20:55	2008-07-04 17:20:55
49	Bo Eun Kin	17	2008-07-04 17:20:55	2008-07-04 17:20:55
50	Heejin An	17	2008-07-04 17:20:55	2008-07-04 17:20:55
51	Moon Young Park	17	2008-07-04 17:20:55	2008-07-04 17:20:55
52	Jesus Falcis	18	2008-07-04 17:20:55	2008-07-04 17:20:55
53	Rizen Salonga	18	2008-07-04 17:20:55	2008-07-04 17:20:55
54	Stephanie Santos	18	2008-07-04 17:20:55	2008-07-04 17:20:55
55	Keigo Okada	19	2008-07-04 17:20:55	2008-07-04 17:20:55
56	Naoko Hattori	19	2008-07-04 17:20:55	2008-07-04 17:20:55
57	Toshiaki Ikehara	19	2008-07-04 17:20:55	2008-07-04 17:20:55
58	Khalidah Nazihah	20	2008-07-04 17:20:55	2008-07-04 17:20:55
59	Meor Alif	20	2008-07-04 17:20:55	2008-07-04 17:20:55
60	Zamir Hamdy Hamdan	20	2008-07-04 17:20:55	2008-07-04 17:20:55
61	Ahmad Faiz Yahaya	21	2008-07-04 17:20:55	2008-07-04 17:20:55
62	Nur Afifah Muhammadiah	21	2008-07-04 17:20:55	2008-07-04 17:20:55
63	Lutfi Torla	21	2008-07-04 17:20:55	2008-07-04 17:20:55
64	Nabilah Lokmal	22	2008-07-04 17:20:55	2008-07-04 17:20:55
65	Nabilah Ulfah Bagarib	22	2008-07-04 17:20:55	2008-07-04 17:20:55
66	Zaimah Zaim	22	2008-07-04 17:20:55	2008-07-04 17:20:55
67	Aino Auerkari	23	2008-07-04 17:20:56	2008-07-04 17:20:56
68	Luthfi Abdurrahman	23	2008-07-04 17:20:56	2008-07-04 17:20:56
69	Masyhur Hilmy	23	2008-07-04 17:20:56	2008-07-04 17:20:56
70	Ips	24	2008-07-04 17:20:56	2008-07-04 17:20:56
71	B-squared	24	2008-07-04 17:20:56	2008-07-04 17:20:56
72	Fangz	24	2008-07-04 17:20:56	2008-07-04 17:20:56
73	Bubu	25	2008-07-04 17:20:56	2008-07-04 17:20:56
74	Twinkles	25	2008-07-04 17:20:56	2008-07-04 17:20:56
75	Gluteus	25	2008-07-04 17:20:56	2008-07-04 17:20:56
76	Baby G	26	2008-07-04 17:20:56	2008-07-04 17:20:56
77	Shalani	26	2008-07-04 17:20:56	2008-07-04 17:20:56
78	Eunice	26	2008-07-04 17:20:56	2008-07-04 17:20:56
79	Alexander Loh	27	2008-07-04 17:20:56	2008-07-04 17:20:56
80	Tlotolo Galiemelwe	27	2008-07-04 17:20:57	2008-07-04 17:20:57
81	Yong Yi Ling	27	2008-07-04 17:20:57	2008-07-04 17:20:57
82	Wang Pei	28	2008-07-04 17:20:57	2008-07-04 17:20:57
83	Zhang Jing	28	2008-07-04 17:20:57	2008-07-04 17:20:57
84	Ya Juan Duan	28	2008-07-04 17:20:57	2008-07-04 17:20:57
85	Ying Luo	29	2008-07-04 17:20:57	2008-07-04 17:20:57
86	Ka Pou Ieong	29	2008-07-04 17:20:57	2008-07-04 17:20:57
87	Wei Xian Song	29	2008-07-04 17:20:57	2008-07-04 17:20:57
88	Lucia Pietropaoli	30	2008-07-04 17:20:57	2008-07-04 17:20:57
89	Nicole Lynch	30	2008-07-04 17:20:57	2008-07-04 17:20:57
90	Seamus Coleman	30	2008-07-04 17:20:57	2008-07-04 17:20:57
91	Alex Finkel	31	2008-07-04 17:20:57	2008-07-04 17:20:57
92	Duncan Campell	31	2008-07-04 17:20:57	2008-07-04 17:20:57
93	Erica Leaney	31	2008-07-04 17:20:57	2008-07-04 17:20:57
94	Alexander Chapman	32	2008-07-04 17:20:57	2008-07-04 17:20:57
95	Sam Naparstek	32	2008-07-04 17:20:57	2008-07-04 17:20:57
96	Simin Ngan	32	2008-07-04 17:20:57	2008-07-04 17:20:57
97	Kiran Iyer	33	2008-07-04 17:20:58	2008-07-04 17:20:58
98	Sashi Balaraman	33	2008-07-04 17:20:58	2008-07-04 17:20:58
99	Victor Finkel	33	2008-07-04 17:20:58	2008-07-04 17:20:58
100	Damien Bruckard	34	2008-07-04 17:20:58	2008-07-04 17:20:58
101	Nita Rao	34	2008-07-04 17:20:58	2008-07-04 17:20:58
102	Ravi  Dutta	34	2008-07-04 17:20:58	2008-07-04 17:20:58
103	Jing Leong	35	2008-07-04 17:20:58	2008-07-04 17:20:58
104	Madeleine Schultz	35	2008-07-04 17:20:58	2008-07-04 17:20:58
105	Melissa Birch	35	2008-07-04 17:20:58	2008-07-04 17:20:58
106	Jeffrey Largier	36	2008-07-04 17:20:58	2008-07-04 17:20:58
107	Katerina Pshenichner	36	2008-07-04 17:20:58	2008-07-04 17:20:58
108	Rhys Campbell	36	2008-07-04 17:20:58	2008-07-04 17:20:58
109	Alexandra Kotova	37	2008-07-04 17:20:58	2008-07-04 17:20:58
110	David Barda	37	2008-07-04 17:20:58	2008-07-04 17:20:58
111	Meredith Prior	37	2008-07-04 17:20:58	2008-07-04 17:20:58
115	Parvathy Prem	39	2008-07-04 17:20:59	2008-07-04 17:20:59
116	Prabakharan Vasudevan	39	2008-07-04 17:20:59	2008-07-04 17:20:59
117	Satyanarayana Venugopal	39	2008-07-04 17:20:59	2008-07-04 17:20:59
118	Divya Swaminathan	40	2008-07-04 17:20:59	2008-07-04 17:20:59
119	Rahul Bhasker	40	2008-07-04 17:20:59	2008-07-04 17:20:59
120	Raslyn Rasiah	40	2008-07-04 17:20:59	2008-07-04 17:20:59
121	Ashwin Nagarajan	41	2008-07-04 17:20:59	2008-07-04 17:20:59
122	Jayesh Kannan	41	2008-07-04 17:20:59	2008-07-04 17:20:59
123	Stephanie Yap	41	2008-07-04 17:20:59	2008-07-04 17:20:59
124	Mayank Mukherjee	42	2008-07-04 17:20:59	2008-07-04 17:20:59
125	Vibhu Sharma	42	2008-07-04 17:20:59	2008-07-04 17:20:59
126	Uday Joshi	42	2008-07-04 17:20:59	2008-07-04 17:20:59
127	Mark Cordiner	43	2008-07-04 17:20:59	2008-07-04 17:20:59
128	Sadhana Rai	43	2008-07-04 17:20:59	2008-07-04 17:20:59
129	Tan Li Feng	43	2008-07-04 17:20:59	2008-07-04 17:20:59
130	Ashok Kumar Rai	44	2008-07-04 17:20:59	2008-07-04 17:20:59
131	Leong Chi Hoong	44	2008-07-04 17:20:59	2008-07-04 17:20:59
132	Raymund Vitorio	44	2008-07-04 17:20:59	2008-07-04 17:20:59
133	Marlon Bosantog	45	2008-07-04 17:21:00	2008-07-04 17:21:00
134	Parable Dizon	45	2008-07-04 17:21:00	2008-07-04 17:21:00
135	Iris Hamada	45	2008-07-04 17:21:00	2008-07-04 17:21:00
136	Cheryl Cheong	46	2008-07-04 17:21:00	2008-07-04 17:21:00
137	Goh Marie	46	2008-07-04 17:21:00	2008-07-04 17:21:00
138	Gopakumar Vihasini	46	2008-07-04 17:21:00	2008-07-04 17:21:00
139	Addiped Cheng	47	2008-07-04 17:21:00	2008-07-04 17:21:00
140	Alex Chee Yu Yeung	47	2008-07-04 17:21:00	2008-07-04 17:21:00
141	Yvonne Ngai	47	2008-07-04 17:21:00	2008-07-04 17:21:00
142	Freida Siregar	48	2008-07-04 17:21:00	2008-07-04 17:21:00
143	Miranda Anwar	48	2008-07-04 17:21:00	2008-07-04 17:21:00
144	Astari Damia	48	2008-07-04 17:21:00	2008-07-04 17:21:00
145	Zhe Wei Lau	49	2008-07-04 17:21:00	2008-07-04 17:21:00
146	Darryl Jie Wei Tan	49	2008-07-04 17:21:00	2008-07-04 17:21:00
147	Ganeshsree Selvachandran	49	2008-07-04 17:21:00	2008-07-04 17:21:00
148	Bart Cummings	50	2008-07-04 17:21:01	2008-07-04 17:21:01
149	Su-Min Lim	50	2008-07-04 17:21:01	2008-07-04 17:21:01
150	Tom Bowes	50	2008-07-04 17:21:01	2008-07-04 17:21:01
151	David Maher	51	2008-07-04 17:21:01	2008-07-04 17:21:01
152	Krystin Glanville	51	2008-07-04 17:21:01	2008-07-04 17:21:01
153	Mariel Barnes	51	2008-07-04 17:21:01	2008-07-04 17:21:01
154	Melissa Sayoc	52	2008-07-04 17:21:01	2008-07-04 17:21:01
155	Alvin Camba	52	2008-07-04 17:21:01	2008-07-04 17:21:01
156	Aaron Francis Chan	52	2008-07-04 17:21:01	2008-07-04 17:21:01
157	Lauren Humphrey	53	2008-07-04 17:21:01	2008-07-04 17:21:01
158	Tom Gole	53	2008-07-04 17:21:01	2008-07-04 17:21:01
159	Evan Goldman	53	2008-07-04 17:21:01	2008-07-04 17:21:01
160	Kavita Paw	54	2008-07-04 17:21:01	2008-07-04 17:21:01
161	Nihal Kumta	54	2008-07-04 17:21:01	2008-07-04 17:21:01
162	Robert Forsaith	54	2008-07-04 17:21:01	2008-07-04 17:21:01
163	Joan Zaldivar	55	2008-07-04 17:21:01	2008-07-04 17:21:01
164	Kayleen Ortiz	55	2008-07-04 17:21:01	2008-07-04 17:21:01
165	Elaine Tiu	55	2008-07-04 17:21:01	2008-07-04 17:21:01
166	Buena Bernal	56	2008-07-04 17:21:01	2008-07-04 17:21:01
167	Hilary Mercado	56	2008-07-04 17:21:01	2008-07-04 17:21:01
168	Kristine Fernandez	56	2008-07-04 17:21:01	2008-07-04 17:21:01
169	Julia Bowes	57	2008-07-04 17:21:02	2008-07-04 17:21:02
170	Naomi Oreb	57	2008-07-04 17:21:02	2008-07-04 17:21:02
171	Steven Hind	57	2008-07-04 17:21:02	2008-07-04 17:21:02
172	Bronwyn Cowell	58	2008-07-04 17:21:02	2008-07-04 17:21:02
173	Jack Wright	58	2008-07-04 17:21:02	2008-07-04 17:21:02
174	Tim Mooney	58	2008-07-04 17:21:02	2008-07-04 17:21:02
175	Giselle Kenny	59	2008-07-04 17:21:02	2008-07-04 17:21:02
176	Katherine Connolly	59	2008-07-04 17:21:02	2008-07-04 17:21:02
177	Sam Greenland	59	2008-07-04 17:21:02	2008-07-04 17:21:02
178	Michael Falk	60	2008-07-04 17:21:02	2008-07-04 17:21:02
179	Naomi Hart	60	2008-07-04 17:21:02	2008-07-04 17:21:02
180	Sriram Srikumar	60	2008-07-04 17:21:02	2008-07-04 17:21:02
181	Andrew Garrett	61	2008-07-04 17:21:02	2008-07-04 17:21:02
182	Kathleen Heath	61	2008-07-04 17:21:02	2008-07-04 17:21:02
183	Steph Paton	61	2008-07-04 17:21:02	2008-07-04 17:21:02
184	James Johnston	62	2008-07-04 17:21:02	2008-07-04 17:21:02
185	Kelvin Yu	62	2008-07-04 17:21:02	2008-07-04 17:21:02
186	Stephanie D'Souza	62	2008-07-04 17:21:02	2008-07-04 17:21:02
187	Aina Syazwani Salleh	63	2008-07-04 17:21:03	2008-07-04 17:21:03
188	Siti Jasmine	63	2008-07-04 17:21:03	2008-07-04 17:21:03
190	Ahmed Ilyas Adam	64	2008-07-04 17:21:03	2008-07-04 17:21:03
191	Mohd Rafa'ei Mohd Tahir	64	2008-07-04 17:21:03	2008-07-04 17:21:03
192	Mohammad Shaqib	64	2008-07-04 17:21:03	2008-07-04 17:21:03
193	Nur Asilah Mod Nor	65	2008-07-04 17:21:03	2008-07-04 17:21:03
194	Nurul Jannah Mohd Noor	65	2008-07-04 17:21:03	2008-07-04 17:21:03
195	Muhammad Qayser Mohd Shahrin	65	2008-07-04 17:21:03	2008-07-04 17:21:03
196	Izwan Zakaria	66	2008-07-04 17:21:03	2008-07-04 17:21:03
197	Mohd Aerie Rahman	66	2008-07-04 17:21:03	2008-07-04 17:21:03
198	Nur Atiqah Mohd Zaki	66	2008-07-04 17:21:03	2008-07-04 17:21:03
199	Esther Kwiet	67	2008-07-04 17:21:03	2008-07-04 17:21:03
200	Stephanie Stojanovic	67	2008-07-04 17:21:03	2008-07-04 17:21:03
201	Zoya Shaftalovich	67	2008-07-04 17:21:03	2008-07-04 17:21:03
202	Patrick Will	68	2008-07-04 17:21:03	2008-07-04 17:21:03
203	Vanessa Duffy	68	2008-07-04 17:21:03	2008-07-04 17:21:03
204	Wing Shum	68	2008-07-04 17:21:03	2008-07-04 17:21:03
205	Elina Raihana Shamsudin	69	2008-07-04 17:21:04	2008-07-04 17:21:04
206	Joanna Ghazali	69	2008-07-04 17:21:04	2008-07-04 17:21:04
207	Nur Sharizad Mohd Shahimi	69	2008-07-04 17:21:04	2008-07-04 17:21:04
208	Siti Suhaila Kamaruddin	70	2008-07-04 17:21:04	2008-07-04 17:21:04
209	Suffian As Saury Shamsudin	70	2008-07-04 17:21:04	2008-07-04 17:21:04
210	Syarir Zakwan Zainol	70	2008-07-04 17:21:04	2008-07-04 17:21:04
211	Chris Bishop	71	2008-07-04 17:21:04	2008-07-04 17:21:04
212	Polly Higbee	71	2008-07-04 17:21:04	2008-07-04 17:21:04
213	Stephen Whittington	71	2008-07-04 17:21:04	2008-07-04 17:21:04
214	Katherine Errington	72	2008-07-04 17:21:04	2008-07-04 17:21:04
215	Kathy Scott Dowell	72	2008-07-04 17:21:04	2008-07-04 17:21:04
216	Richard D'Ath	72	2008-07-04 17:21:04	2008-07-04 17:21:04
217	Emily Bruce	73	2008-07-04 17:21:04	2008-07-04 17:21:04
218	Jenna Raeburn	73	2008-07-04 17:21:04	2008-07-04 17:21:04
219	Seb Templeton	73	2008-07-04 17:21:04	2008-07-04 17:21:04
220	Cala Binamira	74	2008-07-04 17:21:04	2008-07-04 17:21:04
221	Cha Santos	74	2008-07-04 17:21:05	2008-07-04 17:21:05
222	Muhammad Yunus	74	2008-07-04 17:21:05	2008-07-04 17:21:05
224	Rudrajyoti Nath Ray	75	2008-07-29 10:40:29	2008-07-29 15:23:39
225	Kalrav Mishra	75	2008-07-29 10:40:29	2008-07-29 15:23:39
223	Sushila Rao	75	2008-07-29 10:40:28	2008-07-29 15:23:55
189	Nor Hazwani Zainal	63	2008-07-04 17:21:03	2008-07-29 16:09:51
25	Angel Shan Shan Lee	9	2008-07-04 17:20:54	2008-07-06 12:05:11
26	Bambi Yen Chin Chen	9	2008-07-04 17:20:54	2008-07-06 12:05:11
\.


--
-- Data for Name: debates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY debates (id, round_id, venue_id, created_at, updated_at) FROM stdin;
1	1	41	2008-07-04 18:34:47	2008-07-04 18:34:47
2	1	42	2008-07-04 18:34:47	2008-07-04 18:34:47
3	1	43	2008-07-04 18:34:47	2008-07-04 18:34:47
4	1	44	2008-07-04 18:34:47	2008-07-04 18:34:47
5	1	45	2008-07-04 18:34:47	2008-07-04 18:34:47
6	1	46	2008-07-04 18:34:47	2008-07-04 18:34:47
7	1	47	2008-07-04 18:34:47	2008-07-04 18:34:47
8	1	48	2008-07-04 18:34:47	2008-07-04 18:34:47
9	1	49	2008-07-04 18:34:47	2008-07-04 18:34:47
10	1	50	2008-07-04 18:34:47	2008-07-04 18:34:47
11	1	51	2008-07-04 18:34:47	2008-07-04 18:34:47
12	1	52	2008-07-04 18:34:47	2008-07-04 18:34:47
13	1	53	2008-07-04 18:34:47	2008-07-04 18:34:47
14	1	54	2008-07-04 18:34:47	2008-07-04 18:34:47
15	1	55	2008-07-04 18:34:47	2008-07-04 18:34:47
16	1	56	2008-07-04 18:34:48	2008-07-04 18:34:48
17	1	57	2008-07-04 18:34:48	2008-07-04 18:34:48
18	1	58	2008-07-04 18:34:48	2008-07-04 18:34:48
19	1	59	2008-07-04 18:34:48	2008-07-04 18:34:48
20	1	60	2008-07-04 18:34:48	2008-07-04 18:34:48
21	1	61	2008-07-04 18:34:48	2008-07-04 18:34:48
22	1	62	2008-07-04 18:34:48	2008-07-04 18:34:48
23	1	63	2008-07-04 18:34:48	2008-07-04 18:34:48
24	1	64	2008-07-04 18:34:48	2008-07-04 18:34:48
25	1	65	2008-07-04 18:34:48	2008-07-04 18:34:48
26	1	66	2008-07-04 18:34:48	2008-07-04 18:34:48
27	1	67	2008-07-04 18:34:48	2008-07-04 18:34:48
28	1	68	2008-07-04 18:34:48	2008-07-04 18:34:48
29	1	69	2008-07-04 18:34:48	2008-07-04 18:34:48
30	1	70	2008-07-04 18:34:48	2008-07-04 18:34:48
31	1	71	2008-07-04 18:34:48	2008-07-04 18:34:48
32	1	72	2008-07-04 18:34:48	2008-07-04 18:34:48
33	1	73	2008-07-04 18:34:48	2008-07-04 18:34:48
34	1	74	2008-07-04 18:34:48	2008-07-04 18:34:48
35	1	75	2008-07-04 18:34:48	2008-07-04 18:34:48
36	1	76	2008-07-04 18:34:48	2008-07-04 18:34:48
37	1	77	2008-07-04 18:34:48	2008-07-04 18:34:48
38	2	41	2008-07-29 13:07:52	2008-07-29 13:07:52
39	2	42	2008-07-29 13:07:52	2008-07-29 13:07:52
40	2	43	2008-07-29 13:07:52	2008-07-29 13:07:52
41	2	44	2008-07-29 13:07:52	2008-07-29 13:07:52
42	2	45	2008-07-29 13:07:52	2008-07-29 13:07:52
43	2	46	2008-07-29 13:07:52	2008-07-29 13:07:52
44	2	47	2008-07-29 13:07:52	2008-07-29 13:07:52
45	2	48	2008-07-29 13:07:52	2008-07-29 13:07:52
46	2	49	2008-07-29 13:07:52	2008-07-29 13:07:52
47	2	50	2008-07-29 13:07:52	2008-07-29 13:07:52
48	2	51	2008-07-29 13:07:52	2008-07-29 13:07:52
49	2	52	2008-07-29 13:07:52	2008-07-29 13:07:52
50	2	53	2008-07-29 13:07:52	2008-07-29 13:07:52
51	2	54	2008-07-29 13:07:52	2008-07-29 13:07:52
52	2	55	2008-07-29 13:07:52	2008-07-29 13:07:52
53	2	56	2008-07-29 13:07:52	2008-07-29 13:07:52
54	2	57	2008-07-29 13:07:52	2008-07-29 13:07:52
55	2	58	2008-07-29 13:07:52	2008-07-29 13:07:52
56	2	59	2008-07-29 13:07:52	2008-07-29 13:07:52
57	2	60	2008-07-29 13:07:52	2008-07-29 13:07:52
58	2	61	2008-07-29 13:07:53	2008-07-29 13:07:53
59	2	62	2008-07-29 13:07:53	2008-07-29 13:07:53
60	2	63	2008-07-29 13:07:53	2008-07-29 13:07:53
61	2	64	2008-07-29 13:07:53	2008-07-29 13:07:53
62	2	65	2008-07-29 13:07:53	2008-07-29 13:07:53
63	2	66	2008-07-29 13:07:53	2008-07-29 13:07:53
64	2	67	2008-07-29 13:07:53	2008-07-29 13:07:53
65	2	68	2008-07-29 13:07:53	2008-07-29 13:07:53
66	2	69	2008-07-29 13:07:53	2008-07-29 13:07:53
67	2	70	2008-07-29 13:07:53	2008-07-29 13:07:53
68	2	71	2008-07-29 13:07:53	2008-07-29 13:07:53
69	2	72	2008-07-29 13:07:53	2008-07-29 13:07:53
70	2	73	2008-07-29 13:07:53	2008-07-29 13:07:53
71	2	74	2008-07-29 13:07:53	2008-07-29 13:07:53
72	2	75	2008-07-29 13:07:53	2008-07-29 13:07:53
73	2	76	2008-07-29 13:07:53	2008-07-29 13:07:53
74	2	77	2008-07-29 13:07:53	2008-07-29 13:07:53
75	3	41	2008-07-29 16:25:08	2008-07-29 16:25:08
76	3	44	2008-07-29 16:25:08	2008-07-29 16:25:08
77	3	45	2008-07-29 16:25:08	2008-07-29 16:25:08
78	3	46	2008-07-29 16:25:08	2008-07-29 16:25:08
79	3	47	2008-07-29 16:25:08	2008-07-29 16:25:08
80	3	48	2008-07-29 16:25:08	2008-07-29 16:25:08
81	3	49	2008-07-29 16:25:08	2008-07-29 16:25:08
82	3	50	2008-07-29 16:25:08	2008-07-29 16:25:08
83	3	51	2008-07-29 16:25:08	2008-07-29 16:25:08
84	3	52	2008-07-29 16:25:08	2008-07-29 16:25:08
85	3	53	2008-07-29 16:25:08	2008-07-29 16:25:08
86	3	54	2008-07-29 16:25:08	2008-07-29 16:25:08
87	3	55	2008-07-29 16:25:08	2008-07-29 16:25:08
88	3	56	2008-07-29 16:25:08	2008-07-29 16:25:08
89	3	57	2008-07-29 16:25:08	2008-07-29 16:25:08
90	3	58	2008-07-29 16:25:08	2008-07-29 16:25:08
91	3	59	2008-07-29 16:25:08	2008-07-29 16:25:08
92	3	60	2008-07-29 16:25:08	2008-07-29 16:25:08
93	3	42	2008-07-29 16:25:09	2008-07-29 16:25:09
94	3	43	2008-07-29 16:25:09	2008-07-29 16:25:09
95	3	61	2008-07-29 16:25:09	2008-07-29 16:25:09
96	3	62	2008-07-29 16:25:09	2008-07-29 16:25:09
97	3	63	2008-07-29 16:25:09	2008-07-29 16:25:09
98	3	64	2008-07-29 16:25:09	2008-07-29 16:25:09
99	3	65	2008-07-29 16:25:09	2008-07-29 16:25:09
100	3	66	2008-07-29 16:25:09	2008-07-29 16:25:09
101	3	67	2008-07-29 16:25:09	2008-07-29 16:25:09
102	3	68	2008-07-29 16:25:09	2008-07-29 16:25:09
103	3	69	2008-07-29 16:25:09	2008-07-29 16:25:09
104	3	70	2008-07-29 16:25:09	2008-07-29 16:25:09
105	3	71	2008-07-29 16:25:09	2008-07-29 16:25:09
106	3	72	2008-07-29 16:25:09	2008-07-29 16:25:09
107	3	73	2008-07-29 16:25:09	2008-07-29 16:25:09
108	3	74	2008-07-29 16:25:09	2008-07-29 16:25:09
109	3	76	2008-07-29 16:25:09	2008-07-29 16:25:09
110	3	75	2008-07-29 16:25:09	2008-07-29 16:25:09
111	3	77	2008-07-29 16:25:09	2008-07-29 16:25:09
112	4	51	2008-07-29 20:10:37	2008-07-29 20:10:37
113	4	53	2008-07-29 20:10:37	2008-07-29 20:10:37
114	4	52	2008-07-29 20:10:37	2008-07-29 20:10:37
115	4	54	2008-07-29 20:10:37	2008-07-29 20:10:37
116	4	55	2008-07-29 20:10:38	2008-07-29 20:10:38
117	4	56	2008-07-29 20:10:38	2008-07-29 20:10:38
118	4	57	2008-07-29 20:10:38	2008-07-29 20:10:38
119	4	58	2008-07-29 20:10:38	2008-07-29 20:10:38
120	4	59	2008-07-29 20:10:38	2008-07-29 20:10:38
121	4	60	2008-07-29 20:10:38	2008-07-29 20:10:38
122	4	43	2008-07-29 20:10:38	2008-07-29 20:10:38
123	4	41	2008-07-29 20:10:38	2008-07-29 20:10:38
124	4	44	2008-07-29 20:10:38	2008-07-29 20:10:38
125	4	45	2008-07-29 20:10:38	2008-07-29 20:10:38
126	4	46	2008-07-29 20:10:39	2008-07-29 20:10:39
127	4	47	2008-07-29 20:10:39	2008-07-29 20:10:39
128	4	48	2008-07-29 20:10:39	2008-07-29 20:10:39
129	4	49	2008-07-29 20:10:39	2008-07-29 20:10:39
130	4	50	2008-07-29 20:10:39	2008-07-29 20:10:39
131	4	42	2008-07-29 20:10:39	2008-07-29 20:10:39
132	4	61	2008-07-29 20:10:39	2008-07-29 20:10:39
133	4	62	2008-07-29 20:10:39	2008-07-29 20:10:39
134	4	63	2008-07-29 20:10:39	2008-07-29 20:10:39
135	4	64	2008-07-29 20:10:39	2008-07-29 20:10:39
136	4	65	2008-07-29 20:10:39	2008-07-29 20:10:39
137	4	66	2008-07-29 20:10:40	2008-07-29 20:10:40
138	4	67	2008-07-29 20:10:40	2008-07-29 20:10:40
139	4	68	2008-07-29 20:10:40	2008-07-29 20:10:40
140	4	69	2008-07-29 20:10:40	2008-07-29 20:10:40
141	4	70	2008-07-29 20:10:40	2008-07-29 20:10:40
142	4	71	2008-07-29 20:10:40	2008-07-29 20:10:40
143	4	72	2008-07-29 20:10:40	2008-07-29 20:10:40
144	4	73	2008-07-29 20:10:40	2008-07-29 20:10:40
145	4	74	2008-07-29 20:10:40	2008-07-29 20:10:40
146	4	76	2008-07-29 20:10:40	2008-07-29 20:10:40
147	4	75	2008-07-29 20:10:41	2008-07-29 20:10:41
148	4	77	2008-07-29 20:10:41	2008-07-29 20:10:41
149	5	51	2008-07-06 12:39:49	2008-07-06 12:39:49
150	5	53	2008-07-06 12:39:49	2008-07-06 12:39:49
151	5	52	2008-07-06 12:39:49	2008-07-06 12:39:49
152	5	54	2008-07-06 12:39:49	2008-07-06 12:39:49
153	5	55	2008-07-06 12:39:49	2008-07-06 12:39:49
154	5	56	2008-07-06 12:39:49	2008-07-06 12:39:49
155	5	57	2008-07-06 12:39:49	2008-07-06 12:39:49
156	5	58	2008-07-06 12:39:49	2008-07-06 12:39:49
157	5	59	2008-07-06 12:39:49	2008-07-06 12:39:49
158	5	60	2008-07-06 12:39:49	2008-07-06 12:39:49
159	5	43	2008-07-06 12:39:49	2008-07-06 12:39:49
160	5	41	2008-07-06 12:39:49	2008-07-06 12:39:49
161	5	44	2008-07-06 12:39:49	2008-07-06 12:39:49
162	5	45	2008-07-06 12:39:49	2008-07-06 12:39:49
163	5	46	2008-07-06 12:39:49	2008-07-06 12:39:49
164	5	47	2008-07-06 12:39:49	2008-07-06 12:39:49
165	5	48	2008-07-06 12:39:49	2008-07-06 12:39:49
166	5	49	2008-07-06 12:39:49	2008-07-06 12:39:49
167	5	50	2008-07-06 12:39:49	2008-07-06 12:39:49
168	5	42	2008-07-06 12:39:49	2008-07-06 12:39:49
169	5	61	2008-07-06 12:39:49	2008-07-06 12:39:49
170	5	62	2008-07-06 12:39:49	2008-07-06 12:39:49
171	5	63	2008-07-06 12:39:49	2008-07-06 12:39:49
172	5	64	2008-07-06 12:39:49	2008-07-06 12:39:49
173	5	65	2008-07-06 12:39:49	2008-07-06 12:39:49
174	5	66	2008-07-06 12:39:50	2008-07-06 12:39:50
175	5	67	2008-07-06 12:39:50	2008-07-06 12:39:50
176	5	68	2008-07-06 12:39:50	2008-07-06 12:39:50
177	5	69	2008-07-06 12:39:50	2008-07-06 12:39:50
178	5	70	2008-07-06 12:39:50	2008-07-06 12:39:50
179	5	71	2008-07-06 12:39:50	2008-07-06 12:39:50
180	5	72	2008-07-06 12:39:50	2008-07-06 12:39:50
181	5	73	2008-07-06 12:39:50	2008-07-06 12:39:50
182	5	74	2008-07-06 12:39:50	2008-07-06 12:39:50
183	5	76	2008-07-06 12:39:50	2008-07-06 12:39:50
184	5	75	2008-07-06 12:39:50	2008-07-06 12:39:50
185	5	77	2008-07-06 12:39:50	2008-07-06 12:39:50
215	6	51	2008-07-06 17:22:21	2008-07-06 17:22:21
216	6	53	2008-07-06 17:22:21	2008-07-06 17:22:21
217	6	52	2008-07-06 17:22:21	2008-07-06 17:22:21
218	6	54	2008-07-06 17:22:21	2008-07-06 17:22:21
219	6	55	2008-07-06 17:22:21	2008-07-06 17:22:21
220	6	56	2008-07-06 17:22:21	2008-07-06 17:22:21
221	6	57	2008-07-06 17:22:21	2008-07-06 17:22:21
222	6	58	2008-07-06 17:22:21	2008-07-06 17:22:21
223	6	59	2008-07-06 17:22:21	2008-07-06 17:22:21
224	6	60	2008-07-06 17:22:21	2008-07-06 17:22:21
225	6	43	2008-07-06 17:22:22	2008-07-06 17:22:22
226	6	41	2008-07-06 17:22:22	2008-07-06 17:22:22
227	6	44	2008-07-06 17:22:22	2008-07-06 17:22:22
228	6	45	2008-07-06 17:22:22	2008-07-06 17:22:22
229	6	46	2008-07-06 17:22:22	2008-07-06 17:22:22
230	6	47	2008-07-06 17:22:22	2008-07-06 17:22:22
231	6	48	2008-07-06 17:22:22	2008-07-06 17:22:22
232	6	49	2008-07-06 17:22:22	2008-07-06 17:22:22
233	6	50	2008-07-06 17:22:22	2008-07-06 17:22:22
234	6	42	2008-07-06 17:22:22	2008-07-06 17:22:22
235	6	61	2008-07-06 17:22:22	2008-07-06 17:22:22
236	6	62	2008-07-06 17:22:22	2008-07-06 17:22:22
237	6	63	2008-07-06 17:22:22	2008-07-06 17:22:22
238	6	64	2008-07-06 17:22:23	2008-07-06 17:22:23
239	6	65	2008-07-06 17:22:23	2008-07-06 17:22:23
240	6	66	2008-07-06 17:22:23	2008-07-06 17:22:23
241	6	67	2008-07-06 17:22:23	2008-07-06 17:22:23
242	6	68	2008-07-06 17:22:23	2008-07-06 17:22:23
243	6	69	2008-07-06 17:22:23	2008-07-06 17:22:23
244	6	70	2008-07-06 17:22:23	2008-07-06 17:22:23
245	6	71	2008-07-06 17:22:23	2008-07-06 17:22:23
246	6	72	2008-07-06 17:22:23	2008-07-06 17:22:23
247	6	73	2008-07-06 17:22:23	2008-07-06 17:22:23
248	6	74	2008-07-06 17:22:23	2008-07-06 17:22:23
249	6	76	2008-07-06 17:22:23	2008-07-06 17:22:23
250	6	75	2008-07-06 17:22:23	2008-07-06 17:22:23
251	6	77	2008-07-06 17:22:23	2008-07-06 17:22:23
281	7	41	2008-07-07 12:21:42	2008-07-07 12:21:42
282	7	56	2008-07-07 12:21:42	2008-07-07 12:21:42
283	7	57	2008-07-07 12:21:42	2008-07-07 12:21:42
284	7	50	2008-07-07 12:21:42	2008-07-07 12:21:42
285	7	58	2008-07-07 12:21:42	2008-07-07 12:21:42
286	7	59	2008-07-07 12:21:42	2008-07-07 12:21:42
287	7	45	2008-07-07 12:21:42	2008-07-07 12:21:42
288	7	46	2008-07-07 12:21:42	2008-07-07 12:21:42
289	7	51	2008-07-07 12:21:42	2008-07-07 12:21:42
290	7	52	2008-07-07 12:21:42	2008-07-07 12:21:42
291	7	54	2008-07-07 12:21:42	2008-07-07 12:21:42
292	7	43	2008-07-07 12:21:42	2008-07-07 12:21:42
293	7	42	2008-07-07 12:21:42	2008-07-07 12:21:42
294	7	61	2008-07-07 12:21:42	2008-07-07 12:21:42
295	7	62	2008-07-07 12:21:42	2008-07-07 12:21:42
296	7	63	2008-07-07 12:21:42	2008-07-07 12:21:42
297	7	64	2008-07-07 12:21:42	2008-07-07 12:21:42
298	7	65	2008-07-07 12:21:42	2008-07-07 12:21:42
299	7	66	2008-07-07 12:21:42	2008-07-07 12:21:42
300	7	67	2008-07-07 12:21:42	2008-07-07 12:21:42
301	7	68	2008-07-07 12:21:42	2008-07-07 12:21:42
302	7	44	2008-07-07 12:21:42	2008-07-07 12:21:42
303	7	71	2008-07-07 12:21:42	2008-07-07 12:21:42
304	7	72	2008-07-07 12:21:42	2008-07-07 12:21:42
305	7	73	2008-07-07 12:21:42	2008-07-07 12:21:42
306	7	74	2008-07-07 12:21:42	2008-07-07 12:21:42
307	7	76	2008-07-07 12:21:42	2008-07-07 12:21:42
308	7	75	2008-07-07 12:21:42	2008-07-07 12:21:42
309	7	77	2008-07-07 12:21:42	2008-07-07 12:21:42
310	7	53	2008-07-07 12:21:42	2008-07-07 12:21:42
311	7	55	2008-07-07 12:21:42	2008-07-07 12:21:42
312	7	60	2008-07-07 12:21:43	2008-07-07 12:21:43
313	7	70	2008-07-07 12:21:43	2008-07-07 12:21:43
314	7	69	2008-07-07 12:21:43	2008-07-07 12:21:43
315	7	49	2008-07-07 12:21:43	2008-07-07 12:21:43
316	7	48	2008-07-07 12:21:43	2008-07-07 12:21:43
317	7	47	2008-07-07 12:21:43	2008-07-07 12:21:43
318	8	41	2008-07-07 15:58:48	2008-07-07 15:58:48
319	8	56	2008-07-07 15:58:48	2008-07-07 15:58:48
320	8	57	2008-07-07 15:58:48	2008-07-07 15:58:48
321	8	50	2008-07-07 15:58:48	2008-07-07 15:58:48
322	8	58	2008-07-07 15:58:48	2008-07-07 15:58:48
323	8	45	2008-07-07 15:58:48	2008-07-07 15:58:48
324	8	46	2008-07-07 15:58:48	2008-07-07 15:58:48
325	8	51	2008-07-07 15:58:48	2008-07-07 15:58:48
326	8	52	2008-07-07 15:58:48	2008-07-07 15:58:48
327	8	54	2008-07-07 15:58:48	2008-07-07 15:58:48
328	8	43	2008-07-07 15:58:48	2008-07-07 15:58:48
329	8	42	2008-07-07 15:58:48	2008-07-07 15:58:48
330	8	61	2008-07-07 15:58:48	2008-07-07 15:58:48
331	8	62	2008-07-07 15:58:48	2008-07-07 15:58:48
332	8	63	2008-07-07 15:58:48	2008-07-07 15:58:48
333	8	64	2008-07-07 15:58:48	2008-07-07 15:58:48
334	8	65	2008-07-07 15:58:48	2008-07-07 15:58:48
335	8	66	2008-07-07 15:58:48	2008-07-07 15:58:48
336	8	67	2008-07-07 15:58:48	2008-07-07 15:58:48
337	8	68	2008-07-07 15:58:48	2008-07-07 15:58:48
338	8	59	2008-07-07 15:58:48	2008-07-07 15:58:48
339	8	70	2008-07-07 15:58:48	2008-07-07 15:58:48
340	8	71	2008-07-07 15:58:48	2008-07-07 15:58:48
341	8	72	2008-07-07 15:58:48	2008-07-07 15:58:48
342	8	73	2008-07-07 15:58:49	2008-07-07 15:58:49
343	8	74	2008-07-07 15:58:49	2008-07-07 15:58:49
344	8	76	2008-07-07 15:58:49	2008-07-07 15:58:49
345	8	75	2008-07-07 15:58:49	2008-07-07 15:58:49
346	8	77	2008-07-07 15:58:49	2008-07-07 15:58:49
347	8	53	2008-07-07 15:58:49	2008-07-07 15:58:49
348	8	55	2008-07-07 15:58:49	2008-07-07 15:58:49
349	8	60	2008-07-07 15:58:49	2008-07-07 15:58:49
350	8	69	2008-07-07 15:58:49	2008-07-07 15:58:49
351	8	49	2008-07-07 15:58:49	2008-07-07 15:58:49
352	8	48	2008-07-07 15:58:49	2008-07-07 15:58:49
353	8	47	2008-07-07 15:58:49	2008-07-07 15:58:49
354	8	44	2008-07-07 15:58:49	2008-07-07 15:58:49
\.


--
-- Data for Name: debates_teams_xrefs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY debates_teams_xrefs (id, debate_id, team_id, "position", created_at, updated_at) FROM stdin;
1	1	74	1	2008-07-04 18:34:47	2008-07-04 18:34:47
2	1	18	2	2008-07-04 18:34:47	2008-07-04 18:34:47
3	2	12	1	2008-07-04 18:34:47	2008-07-04 18:34:47
4	2	46	2	2008-07-04 18:34:47	2008-07-04 18:34:47
5	3	49	1	2008-07-04 18:34:47	2008-07-04 18:34:47
6	3	9	2	2008-07-04 18:34:47	2008-07-04 18:34:47
7	4	5	1	2008-07-04 18:34:47	2008-07-04 18:34:47
8	4	21	2	2008-07-04 18:34:47	2008-07-04 18:34:47
9	5	20	1	2008-07-04 18:34:47	2008-07-04 18:34:47
10	5	7	2	2008-07-04 18:34:47	2008-07-04 18:34:47
11	6	69	1	2008-07-04 18:34:47	2008-07-04 18:34:47
12	6	28	2	2008-07-04 18:34:47	2008-07-04 18:34:47
13	7	41	1	2008-07-04 18:34:47	2008-07-04 18:34:47
14	7	52	2	2008-07-04 18:34:47	2008-07-04 18:34:47
15	8	13	1	2008-07-04 18:34:47	2008-07-04 18:34:47
16	8	11	2	2008-07-04 18:34:47	2008-07-04 18:34:47
17	9	63	1	2008-07-04 18:34:47	2008-07-04 18:34:47
18	9	3	2	2008-07-04 18:34:47	2008-07-04 18:34:47
19	10	14	1	2008-07-04 18:34:47	2008-07-04 18:34:47
20	10	61	2	2008-07-04 18:34:47	2008-07-04 18:34:47
21	11	53	1	2008-07-04 18:34:47	2008-07-04 18:34:47
22	11	72	2	2008-07-04 18:34:47	2008-07-04 18:34:47
23	12	16	1	2008-07-04 18:34:47	2008-07-04 18:34:47
24	12	54	2	2008-07-04 18:34:47	2008-07-04 18:34:47
25	13	44	1	2008-07-04 18:34:47	2008-07-04 18:34:47
26	13	35	2	2008-07-04 18:34:47	2008-07-04 18:34:47
27	14	37	1	2008-07-04 18:34:47	2008-07-04 18:34:47
28	14	39	2	2008-07-04 18:34:47	2008-07-04 18:34:47
29	15	26	1	2008-07-04 18:34:48	2008-07-04 18:34:48
30	15	71	2	2008-07-04 18:34:48	2008-07-04 18:34:48
31	16	58	1	2008-07-04 18:34:48	2008-07-04 18:34:48
32	16	25	2	2008-07-04 18:34:48	2008-07-04 18:34:48
33	17	6	1	2008-07-04 18:34:48	2008-07-04 18:34:48
34	17	40	2	2008-07-04 18:34:48	2008-07-04 18:34:48
35	18	15	1	2008-07-04 18:34:48	2008-07-04 18:34:48
36	18	32	2	2008-07-04 18:34:48	2008-07-04 18:34:48
37	19	27	1	2008-07-04 18:34:48	2008-07-04 18:34:48
38	19	67	2	2008-07-04 18:34:48	2008-07-04 18:34:48
39	20	43	1	2008-07-04 18:34:48	2008-07-04 18:34:48
41	21	48	1	2008-07-04 18:34:48	2008-07-04 18:34:48
42	21	65	2	2008-07-04 18:34:48	2008-07-04 18:34:48
43	22	50	1	2008-07-04 18:34:48	2008-07-04 18:34:48
44	22	73	2	2008-07-04 18:34:48	2008-07-04 18:34:48
45	23	33	1	2008-07-04 18:34:48	2008-07-04 18:34:48
46	23	66	2	2008-07-04 18:34:48	2008-07-04 18:34:48
47	24	10	1	2008-07-04 18:34:48	2008-07-04 18:34:48
48	24	62	2	2008-07-04 18:34:48	2008-07-04 18:34:48
49	25	42	1	2008-07-04 18:34:48	2008-07-04 18:34:48
50	25	1	2	2008-07-04 18:34:48	2008-07-04 18:34:48
51	26	51	1	2008-07-04 18:34:48	2008-07-04 18:34:48
52	26	17	2	2008-07-04 18:34:48	2008-07-04 18:34:48
53	27	60	1	2008-07-04 18:34:48	2008-07-04 18:34:48
54	27	23	2	2008-07-04 18:34:48	2008-07-04 18:34:48
55	28	8	1	2008-07-04 18:34:48	2008-07-04 18:34:48
56	28	36	2	2008-07-04 18:34:48	2008-07-04 18:34:48
57	29	31	1	2008-07-04 18:34:48	2008-07-04 18:34:48
58	29	22	2	2008-07-04 18:34:48	2008-07-04 18:34:48
59	30	24	1	2008-07-04 18:34:48	2008-07-04 18:34:48
60	30	56	2	2008-07-04 18:34:48	2008-07-04 18:34:48
61	31	47	1	2008-07-04 18:34:48	2008-07-04 18:34:48
62	31	30	2	2008-07-04 18:34:48	2008-07-04 18:34:48
63	32	57	1	2008-07-04 18:34:48	2008-07-04 18:34:48
64	32	19	2	2008-07-04 18:34:48	2008-07-04 18:34:48
65	33	2	1	2008-07-04 18:34:48	2008-07-04 18:34:48
66	33	64	2	2008-07-04 18:34:48	2008-07-04 18:34:48
67	34	4	1	2008-07-04 18:34:48	2008-07-04 18:34:48
68	34	45	2	2008-07-04 18:34:48	2008-07-04 18:34:48
69	35	29	1	2008-07-04 18:34:48	2008-07-04 18:34:48
70	35	59	2	2008-07-04 18:34:48	2008-07-04 18:34:48
71	36	55	1	2008-07-04 18:34:48	2008-07-04 18:34:48
72	36	34	2	2008-07-04 18:34:48	2008-07-04 18:34:48
73	37	70	1	2008-07-04 18:34:48	2008-07-04 18:34:48
74	37	68	2	2008-07-04 18:34:48	2008-07-04 18:34:48
40	20	75	2	2008-07-04 18:34:48	2008-07-04 18:34:48
75	38	52	1	2008-07-29 13:07:52	2008-07-29 13:07:52
76	38	57	2	2008-07-29 13:07:52	2008-07-29 13:07:52
77	39	71	1	2008-07-29 13:07:52	2008-07-29 13:07:52
78	39	61	2	2008-07-29 13:07:52	2008-07-29 13:07:52
79	40	54	1	2008-07-29 13:07:52	2008-07-29 13:07:52
80	40	3	2	2008-07-29 13:07:52	2008-07-29 13:07:52
81	41	5	1	2008-07-29 13:07:52	2008-07-29 13:07:52
82	41	43	2	2008-07-29 13:07:52	2008-07-29 13:07:52
83	42	30	1	2008-07-29 13:07:52	2008-07-29 13:07:52
84	42	73	2	2008-07-29 13:07:52	2008-07-29 13:07:52
85	43	31	1	2008-07-29 13:07:52	2008-07-29 13:07:52
86	43	58	2	2008-07-29 13:07:52	2008-07-29 13:07:52
87	44	40	1	2008-07-29 13:07:52	2008-07-29 13:07:52
88	44	33	2	2008-07-29 13:07:52	2008-07-29 13:07:52
89	45	42	1	2008-07-29 13:07:52	2008-07-29 13:07:52
90	45	37	2	2008-07-29 13:07:52	2008-07-29 13:07:52
91	46	34	1	2008-07-29 13:07:52	2008-07-29 13:07:52
92	46	69	2	2008-07-29 13:07:52	2008-07-29 13:07:52
93	47	35	1	2008-07-29 13:07:52	2008-07-29 13:07:52
94	47	4	2	2008-07-29 13:07:52	2008-07-29 13:07:52
95	48	62	1	2008-07-29 13:07:52	2008-07-29 13:07:52
96	48	64	2	2008-07-29 13:07:52	2008-07-29 13:07:52
97	49	17	1	2008-07-29 13:07:52	2008-07-29 13:07:52
98	49	60	2	2008-07-29 13:07:52	2008-07-29 13:07:52
99	50	59	1	2008-07-29 13:07:52	2008-07-29 13:07:52
100	50	49	2	2008-07-29 13:07:52	2008-07-29 13:07:52
101	51	7	1	2008-07-29 13:07:52	2008-07-29 13:07:52
102	51	48	2	2008-07-29 13:07:52	2008-07-29 13:07:52
103	52	68	1	2008-07-29 13:07:52	2008-07-29 13:07:52
104	52	53	2	2008-07-29 13:07:52	2008-07-29 13:07:52
105	53	67	1	2008-07-29 13:07:52	2008-07-29 13:07:52
106	53	74	2	2008-07-29 13:07:52	2008-07-29 13:07:52
107	54	11	1	2008-07-29 13:07:52	2008-07-29 13:07:52
108	54	24	2	2008-07-29 13:07:52	2008-07-29 13:07:52
109	55	36	1	2008-07-29 13:07:52	2008-07-29 13:07:52
110	55	46	2	2008-07-29 13:07:52	2008-07-29 13:07:52
111	56	39	1	2008-07-29 13:07:52	2008-07-29 13:07:52
112	56	15	2	2008-07-29 13:07:52	2008-07-29 13:07:52
113	57	66	1	2008-07-29 13:07:53	2008-07-29 13:07:53
114	57	45	2	2008-07-29 13:07:53	2008-07-29 13:07:53
115	58	25	1	2008-07-29 13:07:53	2008-07-29 13:07:53
116	58	47	2	2008-07-29 13:07:53	2008-07-29 13:07:53
117	59	75	1	2008-07-29 13:07:53	2008-07-29 13:07:53
118	59	9	2	2008-07-29 13:07:53	2008-07-29 13:07:53
119	60	21	1	2008-07-29 13:07:53	2008-07-29 13:07:53
120	60	63	2	2008-07-29 13:07:53	2008-07-29 13:07:53
121	61	19	1	2008-07-29 13:07:53	2008-07-29 13:07:53
122	61	27	2	2008-07-29 13:07:53	2008-07-29 13:07:53
123	62	41	1	2008-07-29 13:07:53	2008-07-29 13:07:53
124	62	8	2	2008-07-29 13:07:53	2008-07-29 13:07:53
125	63	32	1	2008-07-29 13:07:53	2008-07-29 13:07:53
126	63	70	2	2008-07-29 13:07:53	2008-07-29 13:07:53
127	64	72	1	2008-07-29 13:07:53	2008-07-29 13:07:53
128	64	56	2	2008-07-29 13:07:53	2008-07-29 13:07:53
129	65	55	1	2008-07-29 13:07:53	2008-07-29 13:07:53
130	65	51	2	2008-07-29 13:07:53	2008-07-29 13:07:53
131	66	23	1	2008-07-29 13:07:53	2008-07-29 13:07:53
132	66	28	2	2008-07-29 13:07:53	2008-07-29 13:07:53
133	67	44	1	2008-07-29 13:07:53	2008-07-29 13:07:53
134	67	10	2	2008-07-29 13:07:53	2008-07-29 13:07:53
135	68	22	1	2008-07-29 13:07:53	2008-07-29 13:07:53
136	68	1	2	2008-07-29 13:07:53	2008-07-29 13:07:53
137	69	2	1	2008-07-29 13:07:53	2008-07-29 13:07:53
138	69	6	2	2008-07-29 13:07:53	2008-07-29 13:07:53
139	70	26	1	2008-07-29 13:07:53	2008-07-29 13:07:53
140	70	14	2	2008-07-29 13:07:53	2008-07-29 13:07:53
141	71	29	1	2008-07-29 13:07:53	2008-07-29 13:07:53
142	71	20	2	2008-07-29 13:07:53	2008-07-29 13:07:53
143	72	50	1	2008-07-29 13:07:53	2008-07-29 13:07:53
144	72	13	2	2008-07-29 13:07:53	2008-07-29 13:07:53
145	73	18	1	2008-07-29 13:07:53	2008-07-29 13:07:53
146	73	16	2	2008-07-29 13:07:53	2008-07-29 13:07:53
147	74	65	1	2008-07-29 13:07:53	2008-07-29 13:07:53
148	74	12	2	2008-07-29 13:07:53	2008-07-29 13:07:53
149	75	57	1	2008-07-29 16:25:08	2008-07-29 16:25:08
150	75	34	2	2008-07-29 16:25:08	2008-07-29 16:25:08
151	76	60	1	2008-07-29 16:25:08	2008-07-29 16:25:08
152	76	71	2	2008-07-29 16:25:08	2008-07-29 16:25:08
153	77	3	1	2008-07-29 16:25:08	2008-07-29 16:25:08
154	77	67	2	2008-07-29 16:25:08	2008-07-29 16:25:08
155	78	58	1	2008-07-29 16:25:08	2008-07-29 16:25:08
156	78	37	2	2008-07-29 16:25:08	2008-07-29 16:25:08
157	79	48	1	2008-07-29 16:25:08	2008-07-29 16:25:08
158	79	33	2	2008-07-29 16:25:08	2008-07-29 16:25:08
159	80	62	1	2008-07-29 16:25:08	2008-07-29 16:25:08
160	80	36	2	2008-07-29 16:25:08	2008-07-29 16:25:08
161	81	30	1	2008-07-29 16:25:08	2008-07-29 16:25:08
162	81	59	2	2008-07-29 16:25:08	2008-07-29 16:25:08
163	82	43	1	2008-07-29 16:25:08	2008-07-29 16:25:08
164	82	24	2	2008-07-29 16:25:08	2008-07-29 16:25:08
165	83	35	1	2008-07-29 16:25:08	2008-07-29 16:25:08
166	83	53	2	2008-07-29 16:25:08	2008-07-29 16:25:08
167	84	61	1	2008-07-29 16:25:08	2008-07-29 16:25:08
168	84	16	2	2008-07-29 16:25:08	2008-07-29 16:25:08
169	85	7	1	2008-07-29 16:25:08	2008-07-29 16:25:08
170	85	39	2	2008-07-29 16:25:08	2008-07-29 16:25:08
171	86	25	1	2008-07-29 16:25:08	2008-07-29 16:25:08
172	86	44	2	2008-07-29 16:25:08	2008-07-29 16:25:08
173	87	15	1	2008-07-29 16:25:08	2008-07-29 16:25:08
174	87	41	2	2008-07-29 16:25:08	2008-07-29 16:25:08
175	88	23	1	2008-07-29 16:25:08	2008-07-29 16:25:08
176	88	66	2	2008-07-29 16:25:08	2008-07-29 16:25:08
177	89	51	1	2008-07-29 16:25:08	2008-07-29 16:25:08
178	89	52	2	2008-07-29 16:25:08	2008-07-29 16:25:08
179	90	17	1	2008-07-29 16:25:08	2008-07-29 16:25:08
180	90	4	2	2008-07-29 16:25:08	2008-07-29 16:25:08
181	91	72	1	2008-07-29 16:25:08	2008-07-29 16:25:08
182	91	49	2	2008-07-29 16:25:08	2008-07-29 16:25:08
183	92	69	1	2008-07-29 16:25:09	2008-07-29 16:25:09
184	92	5	2	2008-07-29 16:25:09	2008-07-29 16:25:09
185	93	64	1	2008-07-29 16:25:09	2008-07-29 16:25:09
186	93	26	2	2008-07-29 16:25:09	2008-07-29 16:25:09
187	94	73	1	2008-07-29 16:25:09	2008-07-29 16:25:09
188	94	20	2	2008-07-29 16:25:09	2008-07-29 16:25:09
189	95	46	1	2008-07-29 16:25:09	2008-07-29 16:25:09
190	95	54	2	2008-07-29 16:25:09	2008-07-29 16:25:09
191	96	22	1	2008-07-29 16:25:09	2008-07-29 16:25:09
192	96	27	2	2008-07-29 16:25:09	2008-07-29 16:25:09
193	97	11	1	2008-07-29 16:25:09	2008-07-29 16:25:09
194	97	50	2	2008-07-29 16:25:09	2008-07-29 16:25:09
195	98	9	1	2008-07-29 16:25:09	2008-07-29 16:25:09
196	98	31	2	2008-07-29 16:25:09	2008-07-29 16:25:09
197	99	40	1	2008-07-29 16:25:09	2008-07-29 16:25:09
198	99	68	2	2008-07-29 16:25:09	2008-07-29 16:25:09
199	100	70	1	2008-07-29 16:25:09	2008-07-29 16:25:09
200	100	42	2	2008-07-29 16:25:09	2008-07-29 16:25:09
201	101	74	1	2008-07-29 16:25:09	2008-07-29 16:25:09
202	101	6	2	2008-07-29 16:25:09	2008-07-29 16:25:09
203	102	63	1	2008-07-29 16:25:09	2008-07-29 16:25:09
204	102	12	2	2008-07-29 16:25:09	2008-07-29 16:25:09
205	103	10	1	2008-07-29 16:25:09	2008-07-29 16:25:09
206	103	55	2	2008-07-29 16:25:09	2008-07-29 16:25:09
207	104	47	1	2008-07-29 16:25:09	2008-07-29 16:25:09
208	104	2	2	2008-07-29 16:25:09	2008-07-29 16:25:09
209	105	45	1	2008-07-29 16:25:09	2008-07-29 16:25:09
210	105	75	2	2008-07-29 16:25:09	2008-07-29 16:25:09
211	106	28	1	2008-07-29 16:25:09	2008-07-29 16:25:09
212	106	32	2	2008-07-29 16:25:09	2008-07-29 16:25:09
213	107	56	1	2008-07-29 16:25:09	2008-07-29 16:25:09
214	107	18	2	2008-07-29 16:25:09	2008-07-29 16:25:09
215	108	14	1	2008-07-29 16:25:09	2008-07-29 16:25:09
216	108	19	2	2008-07-29 16:25:09	2008-07-29 16:25:09
217	109	1	1	2008-07-29 16:25:09	2008-07-29 16:25:09
218	109	13	2	2008-07-29 16:25:09	2008-07-29 16:25:09
219	110	65	1	2008-07-29 16:25:09	2008-07-29 16:25:09
220	110	21	2	2008-07-29 16:25:09	2008-07-29 16:25:09
221	111	8	1	2008-07-29 16:25:09	2008-07-29 16:25:09
222	111	29	2	2008-07-29 16:25:09	2008-07-29 16:25:09
223	112	33	1	2008-07-29 20:10:37	2008-07-29 20:10:37
224	112	71	2	2008-07-29 20:10:37	2008-07-29 20:10:37
225	113	53	1	2008-07-29 20:10:37	2008-07-29 20:10:37
226	113	57	2	2008-07-29 20:10:37	2008-07-29 20:10:37
227	114	3	1	2008-07-29 20:10:37	2008-07-29 20:10:37
228	114	62	2	2008-07-29 20:10:37	2008-07-29 20:10:37
229	115	24	1	2008-07-29 20:10:37	2008-07-29 20:10:37
230	115	58	2	2008-07-29 20:10:38	2008-07-29 20:10:38
231	116	30	1	2008-07-29 20:10:38	2008-07-29 20:10:38
232	116	60	2	2008-07-29 20:10:38	2008-07-29 20:10:38
233	117	67	1	2008-07-29 20:10:38	2008-07-29 20:10:38
234	117	42	2	2008-07-29 20:10:38	2008-07-29 20:10:38
235	118	6	1	2008-07-29 20:10:38	2008-07-29 20:10:38
236	118	43	2	2008-07-29 20:10:38	2008-07-29 20:10:38
237	119	4	1	2008-07-29 20:10:38	2008-07-29 20:10:38
238	119	54	2	2008-07-29 20:10:38	2008-07-29 20:10:38
239	120	61	1	2008-07-29 20:10:38	2008-07-29 20:10:38
240	120	7	2	2008-07-29 20:10:38	2008-07-29 20:10:38
241	121	50	1	2008-07-29 20:10:38	2008-07-29 20:10:38
242	121	5	2	2008-07-29 20:10:38	2008-07-29 20:10:38
243	122	48	1	2008-07-29 20:10:38	2008-07-29 20:10:38
244	122	15	2	2008-07-29 20:10:38	2008-07-29 20:10:38
245	123	34	1	2008-07-29 20:10:38	2008-07-29 20:10:38
246	123	52	2	2008-07-29 20:10:38	2008-07-29 20:10:38
247	124	59	1	2008-07-29 20:10:38	2008-07-29 20:10:38
248	124	31	2	2008-07-29 20:10:38	2008-07-29 20:10:38
249	125	66	1	2008-07-29 20:10:38	2008-07-29 20:10:38
250	125	35	2	2008-07-29 20:10:38	2008-07-29 20:10:38
251	126	37	1	2008-07-29 20:10:39	2008-07-29 20:10:39
252	126	44	2	2008-07-29 20:10:39	2008-07-29 20:10:39
253	127	72	1	2008-07-29 20:10:39	2008-07-29 20:10:39
254	127	63	2	2008-07-29 20:10:39	2008-07-29 20:10:39
255	128	36	1	2008-07-29 20:10:39	2008-07-29 20:10:39
256	128	20	2	2008-07-29 20:10:39	2008-07-29 20:10:39
257	129	26	1	2008-07-29 20:10:39	2008-07-29 20:10:39
258	129	40	2	2008-07-29 20:10:39	2008-07-29 20:10:39
259	130	27	1	2008-07-29 20:10:39	2008-07-29 20:10:39
260	130	39	2	2008-07-29 20:10:39	2008-07-29 20:10:39
261	131	25	1	2008-07-29 20:10:39	2008-07-29 20:10:39
262	131	23	2	2008-07-29 20:10:39	2008-07-29 20:10:39
263	132	73	1	2008-07-29 20:10:39	2008-07-29 20:10:39
264	132	49	2	2008-07-29 20:10:39	2008-07-29 20:10:39
265	133	68	1	2008-07-29 20:10:39	2008-07-29 20:10:39
266	133	55	2	2008-07-29 20:10:39	2008-07-29 20:10:39
267	134	64	1	2008-07-29 20:10:39	2008-07-29 20:10:39
268	134	51	2	2008-07-29 20:10:39	2008-07-29 20:10:39
269	135	41	1	2008-07-29 20:10:39	2008-07-29 20:10:39
270	135	17	2	2008-07-29 20:10:39	2008-07-29 20:10:39
271	136	9	1	2008-07-29 20:10:40	2008-07-29 20:10:40
272	136	47	2	2008-07-29 20:10:40	2008-07-29 20:10:40
273	137	46	1	2008-07-29 20:10:40	2008-07-29 20:10:40
274	137	21	2	2008-07-29 20:10:40	2008-07-29 20:10:40
275	138	18	1	2008-07-29 20:10:40	2008-07-29 20:10:40
276	138	22	2	2008-07-29 20:10:40	2008-07-29 20:10:40
277	139	32	1	2008-07-29 20:10:40	2008-07-29 20:10:40
278	139	1	2	2008-07-29 20:10:40	2008-07-29 20:10:40
279	140	16	1	2008-07-29 20:10:40	2008-07-29 20:10:40
280	140	70	2	2008-07-29 20:10:40	2008-07-29 20:10:40
281	141	74	1	2008-07-29 20:10:40	2008-07-29 20:10:40
282	141	8	2	2008-07-29 20:10:40	2008-07-29 20:10:40
283	142	45	1	2008-07-29 20:10:40	2008-07-29 20:10:40
284	142	69	2	2008-07-29 20:10:40	2008-07-29 20:10:40
285	143	12	1	2008-07-29 20:10:40	2008-07-29 20:10:40
286	143	11	2	2008-07-29 20:10:40	2008-07-29 20:10:40
287	144	19	1	2008-07-29 20:10:40	2008-07-29 20:10:40
288	144	56	2	2008-07-29 20:10:40	2008-07-29 20:10:40
289	145	29	1	2008-07-29 20:10:40	2008-07-29 20:10:40
290	145	10	2	2008-07-29 20:10:40	2008-07-29 20:10:40
291	146	65	1	2008-07-29 20:10:40	2008-07-29 20:10:40
292	146	2	2	2008-07-29 20:10:40	2008-07-29 20:10:40
293	147	75	1	2008-07-29 20:10:41	2008-07-29 20:10:41
294	147	13	2	2008-07-29 20:10:41	2008-07-29 20:10:41
295	148	28	1	2008-07-29 20:10:41	2008-07-29 20:10:41
296	148	14	2	2008-07-29 20:10:41	2008-07-29 20:10:41
297	149	71	1	2008-07-06 12:39:49	2008-07-06 12:39:49
298	149	57	2	2008-07-06 12:39:49	2008-07-06 12:39:49
299	150	3	1	2008-07-06 12:39:49	2008-07-06 12:39:49
300	150	30	2	2008-07-06 12:39:49	2008-07-06 12:39:49
301	151	58	1	2008-07-06 12:39:49	2008-07-06 12:39:49
302	151	53	2	2008-07-06 12:39:49	2008-07-06 12:39:49
303	152	62	1	2008-07-06 12:39:49	2008-07-06 12:39:49
304	152	34	2	2008-07-06 12:39:49	2008-07-06 12:39:49
305	153	15	1	2008-07-06 12:39:49	2008-07-06 12:39:49
306	153	43	2	2008-07-06 12:39:49	2008-07-06 12:39:49
307	154	24	1	2008-07-06 12:39:49	2008-07-06 12:39:49
308	154	67	2	2008-07-06 12:39:49	2008-07-06 12:39:49
309	155	59	1	2008-07-06 12:39:49	2008-07-06 12:39:49
310	155	33	2	2008-07-06 12:39:49	2008-07-06 12:39:49
311	156	61	1	2008-07-06 12:39:49	2008-07-06 12:39:49
312	156	35	2	2008-07-06 12:39:49	2008-07-06 12:39:49
313	157	54	1	2008-07-06 12:39:49	2008-07-06 12:39:49
314	157	37	2	2008-07-06 12:39:49	2008-07-06 12:39:49
315	158	36	1	2008-07-06 12:39:49	2008-07-06 12:39:49
316	158	50	2	2008-07-06 12:39:49	2008-07-06 12:39:49
317	159	40	1	2008-07-06 12:39:49	2008-07-06 12:39:49
318	159	72	2	2008-07-06 12:39:49	2008-07-06 12:39:49
319	160	60	1	2008-07-06 12:39:49	2008-07-06 12:39:49
320	160	41	2	2008-07-06 12:39:49	2008-07-06 12:39:49
321	161	4	1	2008-07-06 12:39:49	2008-07-06 12:39:49
322	161	63	2	2008-07-06 12:39:49	2008-07-06 12:39:49
323	162	32	1	2008-07-06 12:39:49	2008-07-06 12:39:49
324	162	7	2	2008-07-06 12:39:49	2008-07-06 12:39:49
325	163	42	1	2008-07-06 12:39:49	2008-07-06 12:39:49
326	163	31	2	2008-07-06 12:39:49	2008-07-06 12:39:49
327	164	21	1	2008-07-06 12:39:49	2008-07-06 12:39:49
328	164	6	2	2008-07-06 12:39:49	2008-07-06 12:39:49
329	165	44	1	2008-07-06 12:39:49	2008-07-06 12:39:49
330	165	16	2	2008-07-06 12:39:49	2008-07-06 12:39:49
331	166	20	1	2008-07-06 12:39:49	2008-07-06 12:39:49
332	166	25	2	2008-07-06 12:39:49	2008-07-06 12:39:49
333	167	66	1	2008-07-06 12:39:49	2008-07-06 12:39:49
334	167	5	2	2008-07-06 12:39:49	2008-07-06 12:39:49
335	168	39	1	2008-07-06 12:39:49	2008-07-06 12:39:49
336	168	51	2	2008-07-06 12:39:49	2008-07-06 12:39:49
337	169	11	1	2008-07-06 12:39:49	2008-07-06 12:39:49
338	169	27	2	2008-07-06 12:39:49	2008-07-06 12:39:49
339	170	9	1	2008-07-06 12:39:49	2008-07-06 12:39:49
340	170	48	2	2008-07-06 12:39:49	2008-07-06 12:39:49
341	171	52	1	2008-07-06 12:39:49	2008-07-06 12:39:49
342	171	18	2	2008-07-06 12:39:49	2008-07-06 12:39:49
343	172	55	1	2008-07-06 12:39:49	2008-07-06 12:39:49
344	172	26	2	2008-07-06 12:39:49	2008-07-06 12:39:49
345	173	73	1	2008-07-06 12:39:49	2008-07-06 12:39:49
346	173	74	2	2008-07-06 12:39:49	2008-07-06 12:39:49
347	174	45	1	2008-07-06 12:39:50	2008-07-06 12:39:50
348	174	64	2	2008-07-06 12:39:50	2008-07-06 12:39:50
349	175	1	1	2008-07-06 12:39:50	2008-07-06 12:39:50
350	175	47	2	2008-07-06 12:39:50	2008-07-06 12:39:50
351	176	56	1	2008-07-06 12:39:50	2008-07-06 12:39:50
352	176	70	2	2008-07-06 12:39:50	2008-07-06 12:39:50
353	177	22	1	2008-07-06 12:39:50	2008-07-06 12:39:50
354	177	75	2	2008-07-06 12:39:50	2008-07-06 12:39:50
355	178	10	1	2008-07-06 12:39:50	2008-07-06 12:39:50
356	178	19	2	2008-07-06 12:39:50	2008-07-06 12:39:50
357	179	68	1	2008-07-06 12:39:50	2008-07-06 12:39:50
358	179	69	2	2008-07-06 12:39:50	2008-07-06 12:39:50
359	180	23	1	2008-07-06 12:39:50	2008-07-06 12:39:50
360	180	46	2	2008-07-06 12:39:50	2008-07-06 12:39:50
361	181	49	1	2008-07-06 12:39:50	2008-07-06 12:39:50
362	181	28	2	2008-07-06 12:39:50	2008-07-06 12:39:50
363	182	17	1	2008-07-06 12:39:50	2008-07-06 12:39:50
364	182	65	2	2008-07-06 12:39:50	2008-07-06 12:39:50
365	183	8	1	2008-07-06 12:39:50	2008-07-06 12:39:50
366	183	12	2	2008-07-06 12:39:50	2008-07-06 12:39:50
367	184	13	1	2008-07-06 12:39:50	2008-07-06 12:39:50
368	184	2	2	2008-07-06 12:39:50	2008-07-06 12:39:50
369	185	14	1	2008-07-06 12:39:50	2008-07-06 12:39:50
370	185	29	2	2008-07-06 12:39:50	2008-07-06 12:39:50
396	215	57	1	2008-07-06 17:22:21	2008-07-06 17:22:21
397	215	3	2	2008-07-06 17:22:21	2008-07-06 17:22:21
398	216	71	1	2008-07-06 17:22:21	2008-07-06 17:22:21
399	216	58	2	2008-07-06 17:22:21	2008-07-06 17:22:21
400	217	37	1	2008-07-06 17:22:21	2008-07-06 17:22:21
401	217	30	2	2008-07-06 17:22:21	2008-07-06 17:22:21
402	218	43	1	2008-07-06 17:22:21	2008-07-06 17:22:21
405	219	72	2	2008-07-06 17:22:21	2008-07-06 17:22:21
406	220	36	1	2008-07-06 17:22:21	2008-07-06 17:22:21
407	220	59	2	2008-07-06 17:22:21	2008-07-06 17:22:21
408	221	53	1	2008-07-06 17:22:21	2008-07-06 17:22:21
409	221	34	2	2008-07-06 17:22:21	2008-07-06 17:22:21
410	222	54	1	2008-07-06 17:22:21	2008-07-06 17:22:21
411	222	60	2	2008-07-06 17:22:21	2008-07-06 17:22:21
412	223	5	1	2008-07-06 17:22:21	2008-07-06 17:22:21
413	223	62	2	2008-07-06 17:22:21	2008-07-06 17:22:21
415	224	33	2	2008-07-06 17:22:21	2008-07-06 17:22:21
417	225	4	2	2008-07-06 17:22:22	2008-07-06 17:22:22
418	226	67	1	2008-07-06 17:22:22	2008-07-06 17:22:22
421	227	7	2	2008-07-06 17:22:22	2008-07-06 17:22:22
423	228	44	2	2008-07-06 17:22:22	2008-07-06 17:22:22
428	231	11	1	2008-07-06 17:22:22	2008-07-06 17:22:22
429	231	15	2	2008-07-06 17:22:22	2008-07-06 17:22:22
430	232	26	1	2008-07-06 17:22:22	2008-07-06 17:22:22
431	232	48	2	2008-07-06 17:22:22	2008-07-06 17:22:22
432	233	56	1	2008-07-06 17:22:22	2008-07-06 17:22:22
433	233	25	2	2008-07-06 17:22:22	2008-07-06 17:22:22
404	219	24	1	2008-07-06 17:22:21	2008-07-06 17:22:21
420	227	31	1	2008-07-06 17:22:22	2008-07-06 17:22:22
422	228	20	1	2008-07-06 17:22:22	2008-07-06 17:22:22
424	229	50	2	2008-07-06 17:22:22	2008-07-06 17:22:22
425	229	21	1	2008-07-06 17:22:22	2008-07-06 17:22:22
427	230	52	1	2008-07-06 17:22:22	2008-07-06 17:22:22
426	230	73	2	2008-07-06 17:22:22	2008-07-06 17:22:22
434	234	23	1	2008-07-06 17:22:22	2008-07-06 17:22:22
435	234	42	2	2008-07-06 17:22:22	2008-07-06 17:22:22
419	226	40	2	2008-07-06 17:22:22	2008-07-06 17:22:22
436	235	32	1	2008-07-06 17:22:22	2008-07-06 17:22:22
437	235	66	2	2008-07-06 17:22:22	2008-07-06 17:22:22
438	236	18	1	2008-07-06 17:22:22	2008-07-06 17:22:22
439	236	6	2	2008-07-06 17:22:22	2008-07-06 17:22:22
440	237	41	1	2008-07-06 17:22:23	2008-07-06 17:22:23
441	237	9	2	2008-07-06 17:22:23	2008-07-06 17:22:23
442	238	63	1	2008-07-06 17:22:23	2008-07-06 17:22:23
443	238	51	2	2008-07-06 17:22:23	2008-07-06 17:22:23
444	239	27	1	2008-07-06 17:22:23	2008-07-06 17:22:23
445	239	10	2	2008-07-06 17:22:23	2008-07-06 17:22:23
446	240	64	1	2008-07-06 17:22:23	2008-07-06 17:22:23
447	240	17	2	2008-07-06 17:22:23	2008-07-06 17:22:23
448	241	49	1	2008-07-06 17:22:23	2008-07-06 17:22:23
449	241	55	2	2008-07-06 17:22:23	2008-07-06 17:22:23
450	242	75	1	2008-07-06 17:22:23	2008-07-06 17:22:23
451	242	16	2	2008-07-06 17:22:23	2008-07-06 17:22:23
452	243	74	1	2008-07-06 17:22:23	2008-07-06 17:22:23
453	243	45	2	2008-07-06 17:22:23	2008-07-06 17:22:23
454	244	47	1	2008-07-06 17:22:23	2008-07-06 17:22:23
455	244	12	2	2008-07-06 17:22:23	2008-07-06 17:22:23
456	245	19	1	2008-07-06 17:22:23	2008-07-06 17:22:23
457	245	68	2	2008-07-06 17:22:23	2008-07-06 17:22:23
458	246	70	1	2008-07-06 17:22:23	2008-07-06 17:22:23
459	246	22	2	2008-07-06 17:22:23	2008-07-06 17:22:23
460	247	2	1	2008-07-06 17:22:23	2008-07-06 17:22:23
463	248	8	2	2008-07-06 17:22:23	2008-07-06 17:22:23
464	249	28	1	2008-07-06 17:22:23	2008-07-06 17:22:23
465	249	1	2	2008-07-06 17:22:23	2008-07-06 17:22:23
466	250	46	1	2008-07-06 17:22:23	2008-07-06 17:22:23
467	250	29	2	2008-07-06 17:22:23	2008-07-06 17:22:23
468	251	13	1	2008-07-06 17:22:24	2008-07-06 17:22:24
469	251	14	2	2008-07-06 17:22:24	2008-07-06 17:22:24
403	218	61	2	2008-07-06 17:22:21	2008-07-06 17:22:21
461	247	69	2	2008-07-06 17:22:23	2008-07-06 17:22:23
462	248	65	1	2008-07-06 17:22:23	2008-07-06 17:22:23
414	224	35	1	2008-07-06 17:22:21	2008-07-06 17:22:21
416	225	39	1	2008-07-06 17:22:22	2008-07-06 17:22:22
495	281	58	1	2008-07-07 12:21:42	2008-07-07 12:21:42
496	281	57	2	2008-07-07 12:21:42	2008-07-07 12:21:42
497	282	3	1	2008-07-07 12:21:42	2008-07-07 12:21:42
498	282	24	2	2008-07-07 12:21:42	2008-07-07 12:21:42
499	283	30	1	2008-07-07 12:21:42	2008-07-07 12:21:42
500	283	61	2	2008-07-07 12:21:42	2008-07-07 12:21:42
501	284	53	1	2008-07-07 12:21:42	2008-07-07 12:21:42
502	284	59	2	2008-07-07 12:21:42	2008-07-07 12:21:42
503	285	71	1	2008-07-07 12:21:42	2008-07-07 12:21:42
504	285	52	2	2008-07-07 12:21:42	2008-07-07 12:21:42
505	286	60	1	2008-07-07 12:21:42	2008-07-07 12:21:42
506	286	5	2	2008-07-07 12:21:42	2008-07-07 12:21:42
507	287	33	1	2008-07-07 12:21:42	2008-07-07 12:21:42
508	287	44	2	2008-07-07 12:21:42	2008-07-07 12:21:42
509	288	4	1	2008-07-07 12:21:42	2008-07-07 12:21:42
510	288	50	2	2008-07-07 12:21:42	2008-07-07 12:21:42
511	289	48	1	2008-07-07 12:21:42	2008-07-07 12:21:42
512	289	43	2	2008-07-07 12:21:42	2008-07-07 12:21:42
513	290	34	1	2008-07-07 12:21:42	2008-07-07 12:21:42
514	290	15	2	2008-07-07 12:21:42	2008-07-07 12:21:42
515	291	67	1	2008-07-07 12:21:42	2008-07-07 12:21:42
516	291	36	2	2008-07-07 12:21:42	2008-07-07 12:21:42
517	292	31	1	2008-07-07 12:21:42	2008-07-07 12:21:42
518	292	72	2	2008-07-07 12:21:42	2008-07-07 12:21:42
519	293	62	1	2008-07-07 12:21:42	2008-07-07 12:21:42
520	293	37	2	2008-07-07 12:21:42	2008-07-07 12:21:42
521	294	7	1	2008-07-07 12:21:42	2008-07-07 12:21:42
522	294	40	2	2008-07-07 12:21:42	2008-07-07 12:21:42
523	295	45	1	2008-07-07 12:21:42	2008-07-07 12:21:42
524	295	25	2	2008-07-07 12:21:42	2008-07-07 12:21:42
525	296	20	1	2008-07-07 12:21:42	2008-07-07 12:21:42
526	296	54	2	2008-07-07 12:21:42	2008-07-07 12:21:42
527	297	35	1	2008-07-07 12:21:42	2008-07-07 12:21:42
528	297	68	2	2008-07-07 12:21:42	2008-07-07 12:21:42
529	298	42	1	2008-07-07 12:21:42	2008-07-07 12:21:42
530	298	21	2	2008-07-07 12:21:42	2008-07-07 12:21:42
531	299	6	1	2008-07-07 12:21:42	2008-07-07 12:21:42
532	299	64	2	2008-07-07 12:21:42	2008-07-07 12:21:42
533	300	39	1	2008-07-07 12:21:42	2008-07-07 12:21:42
534	300	11	2	2008-07-07 12:21:42	2008-07-07 12:21:42
535	301	51	1	2008-07-07 12:21:42	2008-07-07 12:21:42
536	301	16	2	2008-07-07 12:21:42	2008-07-07 12:21:42
537	302	49	1	2008-07-07 12:21:42	2008-07-07 12:21:42
538	302	27	2	2008-07-07 12:21:42	2008-07-07 12:21:42
539	303	73	1	2008-07-07 12:21:42	2008-07-07 12:21:42
540	303	26	2	2008-07-07 12:21:42	2008-07-07 12:21:42
541	304	12	1	2008-07-07 12:21:42	2008-07-07 12:21:42
542	304	32	2	2008-07-07 12:21:42	2008-07-07 12:21:42
543	305	63	1	2008-07-07 12:21:42	2008-07-07 12:21:42
544	305	41	2	2008-07-07 12:21:42	2008-07-07 12:21:42
545	306	55	1	2008-07-07 12:21:42	2008-07-07 12:21:42
546	306	75	2	2008-07-07 12:21:42	2008-07-07 12:21:42
547	307	66	1	2008-07-07 12:21:42	2008-07-07 12:21:42
548	307	47	2	2008-07-07 12:21:42	2008-07-07 12:21:42
549	308	1	1	2008-07-07 12:21:42	2008-07-07 12:21:42
550	308	56	2	2008-07-07 12:21:42	2008-07-07 12:21:42
551	309	69	1	2008-07-07 12:21:42	2008-07-07 12:21:42
552	309	23	2	2008-07-07 12:21:42	2008-07-07 12:21:42
553	310	46	1	2008-07-07 12:21:42	2008-07-07 12:21:42
554	310	9	2	2008-07-07 12:21:42	2008-07-07 12:21:42
555	311	22	1	2008-07-07 12:21:42	2008-07-07 12:21:42
556	311	17	2	2008-07-07 12:21:43	2008-07-07 12:21:43
557	312	10	1	2008-07-07 12:21:43	2008-07-07 12:21:43
558	312	74	2	2008-07-07 12:21:43	2008-07-07 12:21:43
559	313	18	1	2008-07-07 12:21:43	2008-07-07 12:21:43
560	313	65	2	2008-07-07 12:21:43	2008-07-07 12:21:43
561	314	19	1	2008-07-07 12:21:43	2008-07-07 12:21:43
562	314	28	2	2008-07-07 12:21:43	2008-07-07 12:21:43
563	315	29	1	2008-07-07 12:21:43	2008-07-07 12:21:43
564	315	2	2	2008-07-07 12:21:43	2008-07-07 12:21:43
565	316	8	1	2008-07-07 12:21:43	2008-07-07 12:21:43
566	316	13	2	2008-07-07 12:21:43	2008-07-07 12:21:43
567	317	70	1	2008-07-07 12:21:43	2008-07-07 12:21:43
568	317	14	2	2008-07-07 12:21:43	2008-07-07 12:21:43
569	318	57	1	2008-07-07 15:58:48	2008-07-07 15:58:48
570	318	58	2	2008-07-07 15:58:48	2008-07-07 15:58:48
571	319	3	1	2008-07-07 15:58:48	2008-07-07 15:58:48
572	319	30	2	2008-07-07 15:58:48	2008-07-07 15:58:48
573	320	43	1	2008-07-07 15:58:48	2008-07-07 15:58:48
574	320	53	2	2008-07-07 15:58:48	2008-07-07 15:58:48
575	321	34	1	2008-07-07 15:58:48	2008-07-07 15:58:48
576	321	71	2	2008-07-07 15:58:48	2008-07-07 15:58:48
577	322	72	1	2008-07-07 15:58:48	2008-07-07 15:58:48
578	322	60	2	2008-07-07 15:58:48	2008-07-07 15:58:48
579	323	33	1	2008-07-07 15:58:48	2008-07-07 15:58:48
580	323	24	2	2008-07-07 15:58:48	2008-07-07 15:58:48
581	324	61	1	2008-07-07 15:58:48	2008-07-07 15:58:48
582	324	4	2	2008-07-07 15:58:48	2008-07-07 15:58:48
583	325	59	1	2008-07-07 15:58:48	2008-07-07 15:58:48
584	325	67	2	2008-07-07 15:58:48	2008-07-07 15:58:48
585	326	62	1	2008-07-07 15:58:48	2008-07-07 15:58:48
586	326	41	2	2008-07-07 15:58:48	2008-07-07 15:58:48
587	327	37	1	2008-07-07 15:58:48	2008-07-07 15:58:48
588	327	40	2	2008-07-07 15:58:48	2008-07-07 15:58:48
589	328	5	1	2008-07-07 15:58:48	2008-07-07 15:58:48
590	328	36	2	2008-07-07 15:58:48	2008-07-07 15:58:48
591	329	52	1	2008-07-07 15:58:48	2008-07-07 15:58:48
592	329	20	2	2008-07-07 15:58:48	2008-07-07 15:58:48
593	330	50	1	2008-07-07 15:58:48	2008-07-07 15:58:48
594	330	39	2	2008-07-07 15:58:48	2008-07-07 15:58:48
595	331	42	1	2008-07-07 15:58:48	2008-07-07 15:58:48
596	331	73	2	2008-07-07 15:58:48	2008-07-07 15:58:48
597	332	44	1	2008-07-07 15:58:48	2008-07-07 15:58:48
598	332	32	2	2008-07-07 15:58:48	2008-07-07 15:58:48
599	333	27	1	2008-07-07 15:58:48	2008-07-07 15:58:48
600	333	15	2	2008-07-07 15:58:48	2008-07-07 15:58:48
601	334	48	1	2008-07-07 15:58:48	2008-07-07 15:58:48
602	334	31	2	2008-07-07 15:58:48	2008-07-07 15:58:48
603	335	6	1	2008-07-07 15:58:48	2008-07-07 15:58:48
604	335	45	2	2008-07-07 15:58:48	2008-07-07 15:58:48
605	336	51	1	2008-07-07 15:58:48	2008-07-07 15:58:48
606	336	35	2	2008-07-07 15:58:48	2008-07-07 15:58:48
607	337	7	1	2008-07-07 15:58:48	2008-07-07 15:58:48
608	337	23	2	2008-07-07 15:58:48	2008-07-07 15:58:48
609	338	54	1	2008-07-07 15:58:48	2008-07-07 15:58:48
610	338	22	2	2008-07-07 15:58:48	2008-07-07 15:58:48
611	339	16	1	2008-07-07 15:58:48	2008-07-07 15:58:48
612	339	11	2	2008-07-07 15:58:48	2008-07-07 15:58:48
613	340	75	1	2008-07-07 15:58:48	2008-07-07 15:58:48
614	340	25	2	2008-07-07 15:58:48	2008-07-07 15:58:48
615	341	47	1	2008-07-07 15:58:49	2008-07-07 15:58:49
616	341	49	2	2008-07-07 15:58:49	2008-07-07 15:58:49
617	342	21	1	2008-07-07 15:58:49	2008-07-07 15:58:49
618	342	26	2	2008-07-07 15:58:49	2008-07-07 15:58:49
619	343	1	1	2008-07-07 15:58:49	2008-07-07 15:58:49
620	343	64	2	2008-07-07 15:58:49	2008-07-07 15:58:49
621	344	68	1	2008-07-07 15:58:49	2008-07-07 15:58:49
622	344	74	2	2008-07-07 15:58:49	2008-07-07 15:58:49
623	345	9	1	2008-07-07 15:58:49	2008-07-07 15:58:49
624	345	12	2	2008-07-07 15:58:49	2008-07-07 15:58:49
625	346	63	1	2008-07-07 15:58:49	2008-07-07 15:58:49
626	346	18	2	2008-07-07 15:58:49	2008-07-07 15:58:49
627	347	55	1	2008-07-07 15:58:49	2008-07-07 15:58:49
628	347	66	2	2008-07-07 15:58:49	2008-07-07 15:58:49
629	348	56	1	2008-07-07 15:58:49	2008-07-07 15:58:49
630	348	8	2	2008-07-07 15:58:49	2008-07-07 15:58:49
631	349	17	1	2008-07-07 15:58:49	2008-07-07 15:58:49
632	349	19	2	2008-07-07 15:58:49	2008-07-07 15:58:49
634	350	2	2	2008-07-07 15:58:49	2008-07-07 15:58:49
636	351	10	2	2008-07-07 15:58:49	2008-07-07 15:58:49
637	352	46	1	2008-07-07 15:58:49	2008-07-07 15:58:49
638	352	70	2	2008-07-07 15:58:49	2008-07-07 15:58:49
639	353	28	1	2008-07-07 15:58:49	2008-07-07 15:58:49
640	353	29	2	2008-07-07 15:58:49	2008-07-07 15:58:49
641	354	14	1	2008-07-07 15:58:49	2008-07-07 15:58:49
642	354	13	2	2008-07-07 15:58:49	2008-07-07 15:58:49
635	351	69	1	2008-07-07 15:58:49	2008-07-07 15:58:49
633	350	65	1	2008-07-07 15:58:49	2008-07-07 15:58:49
\.


--
-- Data for Name: institutions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY institutions (id, code, name, created_at, updated_at) FROM stdin;
1	Assumption	Assumption University	2008-07-04 17:20:52	2008-07-04 17:20:52
2	Ateneo	Ateneo de Manila University	2008-07-04 17:20:53	2008-07-04 17:20:53
3	CSB	College of St Benilde	2008-07-04 17:20:53	2008-07-04 17:20:53
4	CUHK	Chinese University of Hong Kong	2008-07-04 17:20:53	2008-07-04 17:20:53
5	DAE	Debate Association of EWHA	2008-07-04 17:20:54	2008-07-04 17:20:54
6	DLSU	De La Salle University	2008-07-04 17:20:54	2008-07-04 17:20:54
7	EDIS	EWHA Debate International Studies	2008-07-04 17:20:55	2008-07-04 17:20:55
8	FEU	Far Eastern University	2008-07-04 17:20:55	2008-07-04 17:20:55
9	ICU	International Christian University	2008-07-04 17:20:55	2008-07-04 17:20:55
10	IIU	International Islamic University	2008-07-04 17:20:55	2008-07-04 17:20:55
11	ITB	Institut Teknologi Bandung	2008-07-04 17:20:56	2008-07-04 17:20:56
12	Independent	Independent	2008-07-04 17:20:56	2008-07-04 17:20:56
13	Keio	Keio University	2008-07-04 17:20:56	2008-07-04 17:20:56
14	MMU	Multimedia University	2008-07-04 17:20:56	2008-07-04 17:20:56
15	MMUM	Multimedia University Malacca	2008-07-04 17:20:56	2008-07-04 17:20:56
16	Macau	University of Macau	2008-07-04 17:20:57	2008-07-04 17:20:57
17	Melbourne	University of Melbourne	2008-07-04 17:20:57	2008-07-04 17:20:57
18	Monash	Monash University	2008-07-04 17:20:57	2008-07-04 17:20:57
19	NLSIU	National Law School of India University	2008-07-04 17:20:58	2008-07-04 17:20:58
20	NTU	Nanyang Technological University	2008-07-04 17:20:59	2008-07-04 17:20:59
21	NUJS	National University of Juridical Sciences	2008-07-04 17:20:59	2008-07-04 17:20:59
22	NUS	National University of Singapore	2008-07-04 17:20:59	2008-07-04 17:20:59
23	SAID	SAID	2008-07-04 17:20:59	2008-07-04 17:20:59
24	SLU	St. Louis University	2008-07-04 17:21:00	2008-07-04 17:21:00
25	Singapore Poly	Singapore Polytechnic	2008-07-04 17:21:00	2008-07-04 17:21:00
26	UHK	University of Hong Kong	2008-07-04 17:21:00	2008-07-04 17:21:00
27	UI	Universitas Indonesia	2008-07-04 17:21:00	2008-07-04 17:21:00
28	UKM	Universiti Kebangsaan Malaysia	2008-07-04 17:21:00	2008-07-04 17:21:00
29	UNSW	University of New South Wales	2008-07-04 17:21:00	2008-07-04 17:21:00
30	UPD	University of the Philippines Diliman	2008-07-04 17:21:01	2008-07-04 17:21:01
31	UQ	University of Queensland	2008-07-04 17:21:01	2008-07-04 17:21:01
32	UST	University of Santo Tomas	2008-07-04 17:21:01	2008-07-04 17:21:01
33	Usyd	University of Sydney	2008-07-04 17:21:02	2008-07-04 17:21:02
34	UT Mara	UT Mara	2008-07-04 17:21:03	2008-07-04 17:21:03
35	UTHM	University Tunn Hussein Om	2008-07-04 17:21:03	2008-07-04 17:21:03
36	UTS	University of Technology Sydney	2008-07-04 17:21:03	2008-07-04 17:21:03
37	UWA	University of Western Australia	2008-07-04 17:21:04	2008-07-04 17:21:04
38	UiTM Johor	UT Mara Johor	2008-07-04 17:21:04	2008-07-04 17:21:04
39	UiTM Terengganu	UT Mara Terengganu	2008-07-04 17:21:04	2008-07-04 17:21:04
40	Vic	Victoria University of Wellington	2008-07-04 17:21:04	2008-07-04 17:21:04
41	WUPID	CIMB WUPID	2008-07-04 17:21:04	2008-07-04 17:21:04
42	Swing	Swing	2008-07-29 10:39:51	2008-07-29 10:39:51
\.


--
-- Data for Name: rounds; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY rounds (id, name, type, status, preceded_by_round_id, feedback_weightage, created_at, updated_at) FROM stdin;
1	Round 1	1	64	\N	0	2008-07-04 17:22:26	2008-07-29 12:25:24
2	Round 2	2	64	1	0.10000000000000001	2008-07-04 17:22:43	2008-07-29 16:12:50
3	Round 3	2	64	2	0.20000000000000001	2008-07-04 17:23:01	2008-07-29 19:44:36
4	Round 4	2	64	3	0.29999999999999999	2008-07-04 17:23:34	2008-07-06 12:17:20
5	Round 5	2	64	4	0.40000000000000002	2008-07-04 17:23:46	2008-07-06 17:00:00
6	Round 6	2	64	5	0.5	2008-07-04 17:23:58	2008-07-07 12:00:12
7	Round 7	8	64	6	0.59999999999999998	2008-07-04 17:24:15	2008-07-07 15:39:43
8	Round 8	8	64	7	0.69999999999999996	2008-07-04 17:24:26	2008-07-07 19:05:57
9	Round 9	4	1	8	0.69999999999999996	2008-07-07 19:18:52	2008-07-07 19:18:52
\.


--
-- Data for Name: speaker_score_sheets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY speaker_score_sheets (id, adjudicator_allocation_id, debate_team_xref_id, debater_id, score, speaking_position, created_at, updated_at) FROM stdin;
1	16	31	173	77	1	2008-07-29 11:27:26	2008-07-29 11:27:26
2	16	31	174	77	2	2008-07-29 11:27:26	2008-07-29 11:27:26
3	16	31	172	76	3	2008-07-29 11:27:26	2008-07-29 11:27:26
4	16	31	173	38.5	4	2008-07-29 11:27:26	2008-07-29 11:27:26
5	16	32	73	75	1	2008-07-29 11:27:26	2008-07-29 11:27:26
6	16	32	74	76	2	2008-07-29 11:27:26	2008-07-29 11:27:26
7	16	32	75	76	3	2008-07-29 11:27:26	2008-07-29 11:27:26
8	16	32	73	38	4	2008-07-29 11:27:26	2008-07-29 11:27:26
9	7	13	122	74	1	2008-07-29 11:32:27	2008-07-29 11:32:27
10	7	13	121	75	2	2008-07-29 11:32:27	2008-07-29 11:32:27
11	7	13	123	76	3	2008-07-29 11:32:27	2008-07-29 11:32:27
12	7	13	121	38	4	2008-07-29 11:32:27	2008-07-29 11:32:27
13	7	14	155	76	1	2008-07-29 11:32:27	2008-07-29 11:32:27
14	7	14	156	76	2	2008-07-29 11:32:27	2008-07-29 11:32:27
15	7	14	154	76	3	2008-07-29 11:32:27	2008-07-29 11:32:27
16	7	14	156	37.5	4	2008-07-29 11:32:27	2008-07-29 11:32:27
17	26	51	152	74	1	2008-07-29 11:34:26	2008-07-29 11:34:26
18	26	51	151	75	2	2008-07-29 11:34:26	2008-07-29 11:34:26
19	26	51	153	74	3	2008-07-29 11:34:27	2008-07-29 11:34:27
20	26	51	151	36	4	2008-07-29 11:34:27	2008-07-29 11:34:27
21	26	52	49	75	1	2008-07-29 11:34:27	2008-07-29 11:34:27
22	26	52	51	75	2	2008-07-29 11:34:27	2008-07-29 11:34:27
23	26	52	50	75	3	2008-07-29 11:34:27	2008-07-29 11:34:27
24	26	52	51	37	4	2008-07-29 11:34:27	2008-07-29 11:34:27
25	4	7	13	76	1	2008-07-29 11:34:43	2008-07-29 11:34:43
26	4	7	14	75	2	2008-07-29 11:34:43	2008-07-29 11:34:43
27	4	7	15	77	3	2008-07-29 11:34:43	2008-07-29 11:34:43
28	4	7	13	37	4	2008-07-29 11:34:43	2008-07-29 11:34:43
29	4	8	63	74	1	2008-07-29 11:34:43	2008-07-29 11:34:43
30	4	8	61	74	2	2008-07-29 11:34:43	2008-07-29 11:34:43
31	4	8	62	75	3	2008-07-29 11:34:43	2008-07-29 11:34:43
32	4	8	61	37	4	2008-07-29 11:34:43	2008-07-29 11:34:43
33	21	41	142	76	1	2008-07-29 11:36:34	2008-07-29 11:36:34
34	21	41	144	76	2	2008-07-29 11:36:34	2008-07-29 11:36:34
35	21	41	143	77	3	2008-07-29 11:36:34	2008-07-29 11:36:34
36	21	41	144	37.5	4	2008-07-29 11:36:34	2008-07-29 11:36:34
37	21	42	193	76	1	2008-07-29 11:36:34	2008-07-29 11:36:34
38	21	42	194	75	2	2008-07-29 11:36:34	2008-07-29 11:36:34
39	21	42	195	74	3	2008-07-29 11:36:34	2008-07-29 11:36:34
40	21	42	194	36	4	2008-07-29 11:36:34	2008-07-29 11:36:34
41	6	11	207	75	1	2008-07-29 11:38:34	2008-07-29 11:38:34
42	6	11	205	74	2	2008-07-29 11:38:34	2008-07-29 11:38:34
43	6	11	206	76	3	2008-07-29 11:38:34	2008-07-29 11:38:34
44	6	11	207	38	4	2008-07-29 11:38:34	2008-07-29 11:38:34
45	6	12	82	75	1	2008-07-29 11:38:34	2008-07-29 11:38:34
46	6	12	84	74	2	2008-07-29 11:38:34	2008-07-29 11:38:34
47	6	12	83	73	3	2008-07-29 11:38:34	2008-07-29 11:38:34
48	6	12	82	37	4	2008-07-29 11:38:34	2008-07-29 11:38:34
49	51	69	86	73	1	2008-07-29 11:39:42	2008-07-29 11:39:42
50	52	69	86	74	1	2008-07-29 11:39:42	2008-07-29 11:39:42
51	53	69	86	72	1	2008-07-29 11:39:42	2008-07-29 11:39:42
52	51	69	85	73	2	2008-07-29 11:39:42	2008-07-29 11:39:42
53	52	69	85	74	2	2008-07-29 11:39:42	2008-07-29 11:39:42
54	53	69	85	72	2	2008-07-29 11:39:42	2008-07-29 11:39:42
55	51	69	87	72	3	2008-07-29 11:39:42	2008-07-29 11:39:42
56	52	69	87	72	3	2008-07-29 11:39:42	2008-07-29 11:39:42
57	53	69	87	72	3	2008-07-29 11:39:42	2008-07-29 11:39:42
58	51	69	86	36.5	4	2008-07-29 11:39:42	2008-07-29 11:39:42
59	52	69	86	37	4	2008-07-29 11:39:42	2008-07-29 11:39:42
60	53	69	86	37	4	2008-07-29 11:39:42	2008-07-29 11:39:42
61	51	70	175	77	1	2008-07-29 11:39:42	2008-07-29 11:39:42
62	52	70	175	76	1	2008-07-29 11:39:42	2008-07-29 11:39:42
63	53	70	175	76	1	2008-07-29 11:39:42	2008-07-29 11:39:42
64	51	70	177	76	2	2008-07-29 11:39:42	2008-07-29 11:39:42
65	52	70	177	75	2	2008-07-29 11:39:42	2008-07-29 11:39:42
66	53	70	177	77	2	2008-07-29 11:39:42	2008-07-29 11:39:42
67	51	70	176	77	3	2008-07-29 11:39:42	2008-07-29 11:39:42
68	52	70	176	75	3	2008-07-29 11:39:42	2008-07-29 11:39:42
69	53	70	176	77	3	2008-07-29 11:39:42	2008-07-29 11:39:42
70	51	70	175	37	4	2008-07-29 11:39:42	2008-07-29 11:39:42
71	52	70	175	38.5	4	2008-07-29 11:39:42	2008-07-29 11:39:42
72	53	70	175	38	4	2008-07-29 11:39:42	2008-07-29 11:39:42
73	3	5	147	75	1	2008-07-29 11:41:35	2008-07-29 11:41:35
74	3	5	146	75	2	2008-07-29 11:41:35	2008-07-29 11:41:35
75	3	5	145	74	3	2008-07-29 11:41:35	2008-07-29 11:41:35
76	3	5	146	38	4	2008-07-29 11:41:35	2008-07-29 11:41:35
77	3	6	27	74	1	2008-07-29 11:41:35	2008-07-29 11:41:35
78	3	6	26	73	2	2008-07-29 11:41:35	2008-07-29 11:41:35
79	3	6	25	76	3	2008-07-29 11:41:35	2008-07-29 11:41:35
80	3	6	26	37.5	4	2008-07-29 11:41:35	2008-07-29 11:41:35
81	15	29	76	76	1	2008-07-29 11:43:03	2008-07-29 11:43:03
82	15	29	77	74	2	2008-07-29 11:43:03	2008-07-29 11:43:03
83	15	29	78	74	3	2008-07-29 11:43:03	2008-07-29 11:43:03
84	15	29	76	37.5	4	2008-07-29 11:43:03	2008-07-29 11:43:03
85	15	30	211	77	1	2008-07-29 11:43:03	2008-07-29 11:43:03
86	15	30	212	77	2	2008-07-29 11:43:03	2008-07-29 11:43:03
87	15	30	213	78	3	2008-07-29 11:43:03	2008-07-29 11:43:03
88	15	30	211	39.5	4	2008-07-29 11:43:03	2008-07-29 11:43:03
89	36	59	70	75	1	2008-07-29 11:43:51	2008-07-29 11:43:51
90	38	59	70	76	1	2008-07-29 11:43:51	2008-07-29 11:43:51
91	37	59	70	79	1	2008-07-29 11:43:51	2008-07-29 11:43:51
92	36	59	71	75	2	2008-07-29 11:43:51	2008-07-29 11:43:51
93	38	59	71	75	2	2008-07-29 11:43:51	2008-07-29 11:43:51
94	37	59	71	75	2	2008-07-29 11:43:51	2008-07-29 11:43:51
95	36	59	72	76	3	2008-07-29 11:43:51	2008-07-29 11:43:51
96	38	59	72	77	3	2008-07-29 11:43:51	2008-07-29 11:43:51
97	37	59	72	77	3	2008-07-29 11:43:51	2008-07-29 11:43:51
98	36	59	70	38	4	2008-07-29 11:43:51	2008-07-29 11:43:51
99	38	59	70	37	4	2008-07-29 11:43:51	2008-07-29 11:43:51
100	37	59	70	38.5	4	2008-07-29 11:43:51	2008-07-29 11:43:51
101	36	60	166	74	1	2008-07-29 11:43:51	2008-07-29 11:43:51
102	38	60	166	75	1	2008-07-29 11:43:51	2008-07-29 11:43:51
103	37	60	166	74	1	2008-07-29 11:43:51	2008-07-29 11:43:51
104	36	60	167	74	2	2008-07-29 11:43:51	2008-07-29 11:43:51
105	38	60	167	74	2	2008-07-29 11:43:51	2008-07-29 11:43:51
106	37	60	167	74	2	2008-07-29 11:43:51	2008-07-29 11:43:51
107	36	60	168	74	3	2008-07-29 11:43:51	2008-07-29 11:43:51
108	38	60	168	74	3	2008-07-29 11:43:51	2008-07-29 11:43:51
109	37	60	168	75	3	2008-07-29 11:43:51	2008-07-29 11:43:51
110	36	60	166	36.5	4	2008-07-29 11:43:51	2008-07-29 11:43:51
111	38	60	166	36.5	4	2008-07-29 11:43:51	2008-07-29 11:43:51
112	37	60	166	37	4	2008-07-29 11:43:51	2008-07-29 11:43:51
113	9	17	187	76	1	2008-07-29 11:45:36	2008-07-29 11:45:36
114	9	17	188	75	2	2008-07-29 11:45:36	2008-07-29 11:45:36
115	9	17	189	76	3	2008-07-29 11:45:36	2008-07-29 11:45:36
116	9	17	187	37	4	2008-07-29 11:45:36	2008-07-29 11:45:36
117	9	18	9	78	1	2008-07-29 11:45:36	2008-07-29 11:45:36
118	9	18	8	77	2	2008-07-29 11:45:36	2008-07-29 11:45:36
119	9	18	7	77	3	2008-07-29 11:45:36	2008-07-29 11:45:36
120	9	18	9	38	4	2008-07-29 11:45:36	2008-07-29 11:45:36
121	2	3	35	71	1	2008-07-29 11:47:04	2008-07-29 11:47:04
122	2	3	36	71	2	2008-07-29 11:47:04	2008-07-29 11:47:04
123	2	3	34	72	3	2008-07-29 11:47:04	2008-07-29 11:47:04
124	2	3	35	36.5	4	2008-07-29 11:47:04	2008-07-29 11:47:04
125	2	4	138	74	1	2008-07-29 11:47:04	2008-07-29 11:47:04
126	2	4	136	72	2	2008-07-29 11:47:04	2008-07-29 11:47:04
127	2	4	137	73	3	2008-07-29 11:47:04	2008-07-29 11:47:04
128	2	4	138	37.5	4	2008-07-29 11:47:04	2008-07-29 11:47:04
129	34	57	93	75	1	2008-07-29 11:47:41	2008-07-29 11:47:41
130	35	57	93	78	1	2008-07-29 11:47:41	2008-07-29 11:47:41
131	33	57	93	74	1	2008-07-29 11:47:41	2008-07-29 11:47:41
132	34	57	92	75	2	2008-07-29 11:47:41	2008-07-29 11:47:41
133	35	57	92	76	2	2008-07-29 11:47:41	2008-07-29 11:47:41
134	33	57	92	77	2	2008-07-29 11:47:41	2008-07-29 11:47:41
135	34	57	91	74	3	2008-07-29 11:47:41	2008-07-29 11:47:41
136	35	57	91	73	3	2008-07-29 11:47:41	2008-07-29 11:47:41
137	33	57	91	74	3	2008-07-29 11:47:41	2008-07-29 11:47:41
138	34	57	93	37.5	4	2008-07-29 11:47:41	2008-07-29 11:47:41
139	35	57	93	39.5	4	2008-07-29 11:47:41	2008-07-29 11:47:41
140	33	57	93	37.5	4	2008-07-29 11:47:41	2008-07-29 11:47:41
141	34	58	64	74	1	2008-07-29 11:47:41	2008-07-29 11:47:41
142	35	58	64	73	1	2008-07-29 11:47:41	2008-07-29 11:47:41
143	33	58	64	72	1	2008-07-29 11:47:41	2008-07-29 11:47:41
144	34	58	65	75	2	2008-07-29 11:47:41	2008-07-29 11:47:41
145	35	58	65	73	2	2008-07-29 11:47:41	2008-07-29 11:47:41
146	33	58	65	75	2	2008-07-29 11:47:41	2008-07-29 11:47:41
147	34	58	66	73	3	2008-07-29 11:47:41	2008-07-29 11:47:41
148	35	58	66	73	3	2008-07-29 11:47:41	2008-07-29 11:47:41
149	33	58	66	74	3	2008-07-29 11:47:41	2008-07-29 11:47:41
150	34	58	64	37	4	2008-07-29 11:47:41	2008-07-29 11:47:41
151	35	58	64	37	4	2008-07-29 11:47:41	2008-07-29 11:47:41
152	33	58	64	36	4	2008-07-29 11:47:41	2008-07-29 11:47:41
153	17	33	16	75	1	2008-07-29 11:49:16	2008-07-29 11:49:16
154	17	33	18	74	2	2008-07-29 11:49:16	2008-07-29 11:49:16
155	17	33	17	75	3	2008-07-29 11:49:16	2008-07-29 11:49:16
156	17	33	16	37.5	4	2008-07-29 11:49:16	2008-07-29 11:49:16
157	17	34	119	75	1	2008-07-29 11:49:16	2008-07-29 11:49:16
158	17	34	120	75	2	2008-07-29 11:49:16	2008-07-29 11:49:16
159	17	34	118	76	3	2008-07-29 11:49:17	2008-07-29 11:49:17
160	17	34	119	37.5	4	2008-07-29 11:49:17	2008-07-29 11:49:17
161	19	37	80	76	1	2008-07-29 11:52:29	2008-07-29 11:52:29
162	19	37	81	75	2	2008-07-29 11:52:29	2008-07-29 11:52:29
163	19	37	79	76	3	2008-07-29 11:52:29	2008-07-29 11:52:29
164	19	37	80	36.5	4	2008-07-29 11:52:29	2008-07-29 11:52:29
165	19	38	201	77	1	2008-07-29 11:52:29	2008-07-29 11:52:29
166	19	38	200	76	2	2008-07-29 11:52:29	2008-07-29 11:52:29
167	19	38	199	76	3	2008-07-29 11:52:29	2008-07-29 11:52:29
168	19	38	201	37.5	4	2008-07-29 11:52:29	2008-07-29 11:52:29
169	8	15	39	73	1	2008-07-29 11:54:24	2008-07-29 11:54:24
170	8	15	37	73	2	2008-07-29 11:54:24	2008-07-29 11:54:24
171	8	15	38	72	3	2008-07-29 11:54:24	2008-07-29 11:54:24
172	8	15	39	36	4	2008-07-29 11:54:24	2008-07-29 11:54:24
173	8	16	33	74	1	2008-07-29 11:54:24	2008-07-29 11:54:24
174	8	16	31	74	2	2008-07-29 11:54:24	2008-07-29 11:54:24
175	8	16	32	75	3	2008-07-29 11:54:24	2008-07-29 11:54:24
176	8	16	31	36	4	2008-07-29 11:54:24	2008-07-29 11:54:24
177	45	65	5	74	1	2008-07-29 11:55:32	2008-07-29 11:55:32
178	46	65	5	73	1	2008-07-29 11:55:32	2008-07-29 11:55:32
179	47	65	5	74	1	2008-07-29 11:55:32	2008-07-29 11:55:32
180	45	65	4	74	2	2008-07-29 11:55:32	2008-07-29 11:55:32
181	46	65	4	74	2	2008-07-29 11:55:32	2008-07-29 11:55:32
182	47	65	4	72	2	2008-07-29 11:55:32	2008-07-29 11:55:32
183	45	65	6	75	3	2008-07-29 11:55:32	2008-07-29 11:55:32
184	46	65	6	75	3	2008-07-29 11:55:32	2008-07-29 11:55:32
185	47	65	6	73	3	2008-07-29 11:55:32	2008-07-29 11:55:32
186	45	65	4	37	4	2008-07-29 11:55:32	2008-07-29 11:55:32
187	46	65	4	36.5	4	2008-07-29 11:55:32	2008-07-29 11:55:32
188	47	65	4	36	4	2008-07-29 11:55:32	2008-07-29 11:55:32
189	45	66	191	75	1	2008-07-29 11:55:32	2008-07-29 11:55:32
190	46	66	191	74	1	2008-07-29 11:55:32	2008-07-29 11:55:32
191	47	66	191	76	1	2008-07-29 11:55:32	2008-07-29 11:55:32
192	45	66	192	74	2	2008-07-29 11:55:32	2008-07-29 11:55:32
193	46	66	192	76	2	2008-07-29 11:55:32	2008-07-29 11:55:32
194	47	66	192	75	2	2008-07-29 11:55:32	2008-07-29 11:55:32
195	45	66	190	76	3	2008-07-29 11:55:32	2008-07-29 11:55:32
196	46	66	190	75	3	2008-07-29 11:55:32	2008-07-29 11:55:32
197	47	66	190	76	3	2008-07-29 11:55:32	2008-07-29 11:55:32
198	45	66	191	37	4	2008-07-29 11:55:32	2008-07-29 11:55:32
199	46	66	191	37.5	4	2008-07-29 11:55:32	2008-07-29 11:55:32
200	47	66	191	37	4	2008-07-29 11:55:32	2008-07-29 11:55:32
201	25	49	126	75	1	2008-07-29 11:56:27	2008-07-29 11:56:27
202	25	49	124	75	2	2008-07-29 11:56:27	2008-07-29 11:56:27
203	25	49	125	76	3	2008-07-29 11:56:27	2008-07-29 11:56:27
204	25	49	126	37.5	4	2008-07-29 11:56:27	2008-07-29 11:56:27
205	25	50	3	76	1	2008-07-29 11:56:27	2008-07-29 11:56:27
206	25	50	2	75	2	2008-07-29 11:56:27	2008-07-29 11:56:27
207	25	50	1	74	3	2008-07-29 11:56:27	2008-07-29 11:56:27
208	25	50	3	37	4	2008-07-29 11:56:27	2008-07-29 11:56:27
209	11	21	158	76	1	2008-07-29 11:58:13	2008-07-29 11:58:13
210	11	21	159	76	2	2008-07-29 11:58:13	2008-07-29 11:58:13
211	11	21	157	77	3	2008-07-29 11:58:13	2008-07-29 11:58:13
212	11	21	159	37.5	4	2008-07-29 11:58:13	2008-07-29 11:58:13
213	11	22	215	76	1	2008-07-29 11:58:13	2008-07-29 11:58:13
214	11	22	214	75	2	2008-07-29 11:58:13	2008-07-29 11:58:13
215	11	22	216	75	3	2008-07-29 11:58:13	2008-07-29 11:58:13
216	11	22	215	37	4	2008-07-29 11:58:13	2008-07-29 11:58:13
217	18	35	44	76	1	2008-07-29 11:59:39	2008-07-29 11:59:39
218	18	35	45	75	2	2008-07-29 11:59:39	2008-07-29 11:59:39
219	18	35	43	77	3	2008-07-29 11:59:39	2008-07-29 11:59:39
220	18	35	45	37.5	4	2008-07-29 11:59:39	2008-07-29 11:59:39
221	18	36	94	76	1	2008-07-29 11:59:39	2008-07-29 11:59:39
222	18	36	95	75	2	2008-07-29 11:59:39	2008-07-29 11:59:39
223	18	36	96	74	3	2008-07-29 11:59:39	2008-07-29 11:59:39
224	18	36	94	38	4	2008-07-29 11:59:39	2008-07-29 11:59:39
225	57	73	209	74	1	2008-07-29 11:59:48	2008-07-29 11:59:48
226	58	73	209	75	1	2008-07-29 11:59:48	2008-07-29 11:59:48
227	59	73	209	74	1	2008-07-29 11:59:48	2008-07-29 11:59:48
228	57	73	208	75	2	2008-07-29 11:59:48	2008-07-29 11:59:48
229	58	73	208	76	2	2008-07-29 11:59:48	2008-07-29 11:59:48
230	59	73	208	73	2	2008-07-29 11:59:48	2008-07-29 11:59:48
231	57	73	210	74	3	2008-07-29 11:59:48	2008-07-29 11:59:48
232	58	73	210	73	3	2008-07-29 11:59:48	2008-07-29 11:59:48
233	59	73	210	72	3	2008-07-29 11:59:48	2008-07-29 11:59:48
234	57	73	209	37.5	4	2008-07-29 11:59:48	2008-07-29 11:59:48
235	58	73	209	37	4	2008-07-29 11:59:48	2008-07-29 11:59:48
236	59	73	209	37.5	4	2008-07-29 11:59:48	2008-07-29 11:59:48
237	57	74	202	75	1	2008-07-29 11:59:48	2008-07-29 11:59:48
238	58	74	202	74	1	2008-07-29 11:59:48	2008-07-29 11:59:48
239	59	74	202	73	1	2008-07-29 11:59:48	2008-07-29 11:59:48
240	57	74	203	76	2	2008-07-29 11:59:48	2008-07-29 11:59:48
241	58	74	203	76	2	2008-07-29 11:59:48	2008-07-29 11:59:48
242	59	74	203	74	2	2008-07-29 11:59:48	2008-07-29 11:59:48
243	57	74	204	75	3	2008-07-29 11:59:48	2008-07-29 11:59:48
244	58	74	204	76	3	2008-07-29 11:59:49	2008-07-29 11:59:49
245	59	74	204	74	3	2008-07-29 11:59:49	2008-07-29 11:59:49
246	57	74	202	37.5	4	2008-07-29 11:59:49	2008-07-29 11:59:49
247	58	74	202	37	4	2008-07-29 11:59:49	2008-07-29 11:59:49
248	59	74	202	37	4	2008-07-29 11:59:49	2008-07-29 11:59:49
249	5	9	58	75	1	2008-07-29 12:01:03	2008-07-29 12:01:03
250	5	9	60	74	2	2008-07-29 12:01:03	2008-07-29 12:01:03
251	5	9	59	75	3	2008-07-29 12:01:03	2008-07-29 12:01:03
252	5	9	58	37	4	2008-07-29 12:01:03	2008-07-29 12:01:03
253	5	10	21	75	1	2008-07-29 12:01:03	2008-07-29 12:01:03
254	5	10	19	75	2	2008-07-29 12:01:03	2008-07-29 12:01:03
255	5	10	20	75	3	2008-07-29 12:01:03	2008-07-29 12:01:03
256	5	10	21	37	4	2008-07-29 12:01:03	2008-07-29 12:01:03
257	13	25	130	75	1	2008-07-29 12:02:30	2008-07-29 12:02:30
258	13	25	132	75	2	2008-07-29 12:02:30	2008-07-29 12:02:30
259	13	25	131	74	3	2008-07-29 12:02:30	2008-07-29 12:02:30
260	13	25	130	38	4	2008-07-29 12:02:30	2008-07-29 12:02:30
261	13	26	105	75	1	2008-07-29 12:02:30	2008-07-29 12:02:30
262	13	26	104	76	2	2008-07-29 12:02:30	2008-07-29 12:02:30
263	13	26	103	75	3	2008-07-29 12:02:30	2008-07-29 12:02:30
264	13	26	105	37.5	4	2008-07-29 12:02:30	2008-07-29 12:02:30
265	23	45	99	77	1	2008-07-29 12:02:42	2008-07-29 12:02:42
266	23	45	97	76	2	2008-07-29 12:02:42	2008-07-29 12:02:42
267	23	45	98	78	3	2008-07-29 12:02:42	2008-07-29 12:02:42
268	23	45	99	37.5	4	2008-07-29 12:02:42	2008-07-29 12:02:42
269	23	46	196	75	1	2008-07-29 12:02:42	2008-07-29 12:02:42
270	23	46	197	76	2	2008-07-29 12:02:42	2008-07-29 12:02:42
271	23	46	198	77	3	2008-07-29 12:02:42	2008-07-29 12:02:42
272	23	46	197	37.5	4	2008-07-29 12:02:42	2008-07-29 12:02:42
273	22	43	148	75	1	2008-07-29 12:03:55	2008-07-29 12:03:55
274	22	43	149	74	2	2008-07-29 12:03:55	2008-07-29 12:03:55
275	22	43	150	75	3	2008-07-29 12:03:55	2008-07-29 12:03:55
276	22	43	149	37	4	2008-07-29 12:03:55	2008-07-29 12:03:55
277	22	44	217	75	1	2008-07-29 12:03:55	2008-07-29 12:03:55
278	22	44	218	75	2	2008-07-29 12:03:55	2008-07-29 12:03:55
279	22	44	219	76	3	2008-07-29 12:03:55	2008-07-29 12:03:55
280	22	44	217	37.5	4	2008-07-29 12:03:55	2008-07-29 12:03:55
281	24	47	28	75	1	2008-07-29 12:05:18	2008-07-29 12:05:18
282	24	47	29	74	2	2008-07-29 12:05:18	2008-07-29 12:05:18
283	24	47	30	73	3	2008-07-29 12:05:18	2008-07-29 12:05:18
284	24	47	29	37	4	2008-07-29 12:05:18	2008-07-29 12:05:18
285	24	48	186	76	1	2008-07-29 12:05:18	2008-07-29 12:05:18
286	24	48	185	77	2	2008-07-29 12:05:18	2008-07-29 12:05:18
287	24	48	184	76	3	2008-07-29 12:05:18	2008-07-29 12:05:18
288	24	48	186	38	4	2008-07-29 12:05:18	2008-07-29 12:05:18
289	14	27	111	78	1	2008-07-29 12:05:22	2008-07-29 12:05:22
290	14	27	109	75	2	2008-07-29 12:05:22	2008-07-29 12:05:22
291	14	27	110	77	3	2008-07-29 12:05:22	2008-07-29 12:05:22
292	14	27	111	37.5	4	2008-07-29 12:05:22	2008-07-29 12:05:22
293	14	28	116	77	1	2008-07-29 12:05:22	2008-07-29 12:05:22
294	14	28	115	74	2	2008-07-29 12:05:22	2008-07-29 12:05:22
295	14	28	117	78	3	2008-07-29 12:05:22	2008-07-29 12:05:22
296	14	28	116	37.5	4	2008-07-29 12:05:22	2008-07-29 12:05:22
297	48	67	11	77	1	2008-07-29 12:05:55	2008-07-29 12:05:55
298	49	67	11	75	1	2008-07-29 12:05:55	2008-07-29 12:05:55
299	50	67	11	76	1	2008-07-29 12:05:55	2008-07-29 12:05:55
300	48	67	10	78	2	2008-07-29 12:05:55	2008-07-29 12:05:55
301	49	67	10	77	2	2008-07-29 12:05:55	2008-07-29 12:05:55
302	50	67	10	77	2	2008-07-29 12:05:55	2008-07-29 12:05:55
303	48	67	12	77	3	2008-07-29 12:05:55	2008-07-29 12:05:55
304	49	67	12	75	3	2008-07-29 12:05:55	2008-07-29 12:05:55
305	50	67	12	75	3	2008-07-29 12:05:55	2008-07-29 12:05:55
306	48	67	11	38.5	4	2008-07-29 12:05:55	2008-07-29 12:05:55
307	49	67	11	38	4	2008-07-29 12:05:55	2008-07-29 12:05:55
308	50	67	11	38	4	2008-07-29 12:05:55	2008-07-29 12:05:55
309	48	68	133	75	1	2008-07-29 12:05:55	2008-07-29 12:05:55
310	49	68	133	74	1	2008-07-29 12:05:55	2008-07-29 12:05:55
311	50	68	133	74	1	2008-07-29 12:05:55	2008-07-29 12:05:55
312	48	68	134	76	2	2008-07-29 12:05:55	2008-07-29 12:05:55
313	49	68	134	74	2	2008-07-29 12:05:55	2008-07-29 12:05:55
314	50	68	134	75	2	2008-07-29 12:05:55	2008-07-29 12:05:55
315	48	68	135	76	3	2008-07-29 12:05:55	2008-07-29 12:05:55
316	49	68	135	75	3	2008-07-29 12:05:55	2008-07-29 12:05:55
317	50	68	135	75	3	2008-07-29 12:05:55	2008-07-29 12:05:55
318	48	68	133	37	4	2008-07-29 12:05:55	2008-07-29 12:05:55
319	49	68	133	35	4	2008-07-29 12:05:55	2008-07-29 12:05:55
320	50	68	133	37	4	2008-07-29 12:05:55	2008-07-29 12:05:55
321	12	23	48	74	1	2008-07-29 12:07:47	2008-07-29 12:07:47
322	12	23	46	75	2	2008-07-29 12:07:47	2008-07-29 12:07:47
323	12	23	47	75	3	2008-07-29 12:07:47	2008-07-29 12:07:47
324	12	23	46	37	4	2008-07-29 12:07:47	2008-07-29 12:07:47
325	12	24	161	75	1	2008-07-29 12:07:47	2008-07-29 12:07:47
326	12	24	160	76	2	2008-07-29 12:07:47	2008-07-29 12:07:47
327	12	24	162	76	3	2008-07-29 12:07:47	2008-07-29 12:07:47
328	12	24	161	37.5	4	2008-07-29 12:07:47	2008-07-29 12:07:47
329	27	53	180	75	1	2008-07-29 12:09:25	2008-07-29 12:09:25
330	28	53	180	75	1	2008-07-29 12:09:25	2008-07-29 12:09:25
331	29	53	180	76	1	2008-07-29 12:09:25	2008-07-29 12:09:25
332	27	53	178	77	2	2008-07-29 12:09:25	2008-07-29 12:09:25
333	28	53	178	76	2	2008-07-29 12:09:25	2008-07-29 12:09:25
334	29	53	178	76	2	2008-07-29 12:09:25	2008-07-29 12:09:25
335	27	53	179	78	3	2008-07-29 12:09:25	2008-07-29 12:09:25
336	28	53	179	77	3	2008-07-29 12:09:25	2008-07-29 12:09:25
337	29	53	179	76	3	2008-07-29 12:09:25	2008-07-29 12:09:25
338	27	53	180	38.5	4	2008-07-29 12:09:25	2008-07-29 12:09:25
339	28	53	180	38	4	2008-07-29 12:09:26	2008-07-29 12:09:26
340	29	53	180	37.5	4	2008-07-29 12:09:26	2008-07-29 12:09:26
341	27	54	68	76	1	2008-07-29 12:09:26	2008-07-29 12:09:26
342	28	54	68	76	1	2008-07-29 12:09:26	2008-07-29 12:09:26
343	29	54	68	75	1	2008-07-29 12:09:26	2008-07-29 12:09:26
344	27	54	67	75	2	2008-07-29 12:09:26	2008-07-29 12:09:26
345	28	54	67	75	2	2008-07-29 12:09:26	2008-07-29 12:09:26
346	29	54	67	76	2	2008-07-29 12:09:26	2008-07-29 12:09:26
347	27	54	69	74	3	2008-07-29 12:09:26	2008-07-29 12:09:26
348	28	54	69	73	3	2008-07-29 12:09:26	2008-07-29 12:09:26
349	29	54	69	75	3	2008-07-29 12:09:26	2008-07-29 12:09:26
350	27	54	68	37.5	4	2008-07-29 12:09:26	2008-07-29 12:09:26
351	28	54	68	37	4	2008-07-29 12:09:26	2008-07-29 12:09:26
352	29	54	68	37.5	4	2008-07-29 12:09:26	2008-07-29 12:09:26
353	10	19	42	74	1	2008-07-29 12:11:35	2008-07-29 12:11:35
354	10	19	40	74	2	2008-07-29 12:11:35	2008-07-29 12:11:35
355	10	19	41	73	3	2008-07-29 12:11:35	2008-07-29 12:11:35
356	10	19	42	36	4	2008-07-29 12:11:35	2008-07-29 12:11:35
357	10	20	181	76	1	2008-07-29 12:11:36	2008-07-29 12:11:36
358	10	20	183	75	2	2008-07-29 12:11:36	2008-07-29 12:11:36
359	10	20	182	76	3	2008-07-29 12:11:36	2008-07-29 12:11:36
360	10	20	181	38	4	2008-07-29 12:11:36	2008-07-29 12:11:36
361	42	63	171	76	1	2008-07-29 12:13:06	2008-07-29 12:13:06
362	43	63	171	78	1	2008-07-29 12:13:06	2008-07-29 12:13:06
363	44	63	171	76	1	2008-07-29 12:13:06	2008-07-29 12:13:06
364	42	63	169	79	2	2008-07-29 12:13:06	2008-07-29 12:13:06
365	43	63	169	80	2	2008-07-29 12:13:06	2008-07-29 12:13:06
366	44	63	169	78	2	2008-07-29 12:13:06	2008-07-29 12:13:06
367	42	63	170	79	3	2008-07-29 12:13:06	2008-07-29 12:13:06
368	43	63	170	81	3	2008-07-29 12:13:06	2008-07-29 12:13:06
369	44	63	170	79	3	2008-07-29 12:13:06	2008-07-29 12:13:06
370	42	63	169	40	4	2008-07-29 12:13:06	2008-07-29 12:13:06
371	43	63	169	39.5	4	2008-07-29 12:13:06	2008-07-29 12:13:06
372	44	63	169	38	4	2008-07-29 12:13:06	2008-07-29 12:13:06
373	42	64	57	73	1	2008-07-29 12:13:06	2008-07-29 12:13:06
374	43	64	57	76	1	2008-07-29 12:13:06	2008-07-29 12:13:06
375	44	64	57	77	1	2008-07-29 12:13:07	2008-07-29 12:13:07
376	42	64	56	73	2	2008-07-29 12:13:07	2008-07-29 12:13:07
377	43	64	56	74	2	2008-07-29 12:13:07	2008-07-29 12:13:07
378	44	64	56	74	2	2008-07-29 12:13:07	2008-07-29 12:13:07
379	42	64	55	73	3	2008-07-29 12:13:07	2008-07-29 12:13:07
380	43	64	55	74	3	2008-07-29 12:13:07	2008-07-29 12:13:07
381	44	64	55	75	3	2008-07-29 12:13:07	2008-07-29 12:13:07
382	42	64	57	37	4	2008-07-29 12:13:07	2008-07-29 12:13:07
383	43	64	57	37.5	4	2008-07-29 12:13:07	2008-07-29 12:13:07
384	44	64	57	36	4	2008-07-29 12:13:07	2008-07-29 12:13:07
385	40	61	139	75	1	2008-07-29 12:14:28	2008-07-29 12:14:28
386	41	61	139	75	1	2008-07-29 12:14:28	2008-07-29 12:14:28
387	39	61	139	75	1	2008-07-29 12:14:28	2008-07-29 12:14:28
388	40	61	141	75	2	2008-07-29 12:14:28	2008-07-29 12:14:28
389	41	61	141	76	2	2008-07-29 12:14:28	2008-07-29 12:14:28
390	39	61	141	75	2	2008-07-29 12:14:28	2008-07-29 12:14:28
391	40	61	140	74	3	2008-07-29 12:14:28	2008-07-29 12:14:28
392	41	61	140	74	3	2008-07-29 12:14:28	2008-07-29 12:14:28
393	39	61	140	74	3	2008-07-29 12:14:28	2008-07-29 12:14:28
394	40	61	139	36	4	2008-07-29 12:14:28	2008-07-29 12:14:28
395	41	61	139	36.5	4	2008-07-29 12:14:28	2008-07-29 12:14:28
396	39	61	139	37.5	4	2008-07-29 12:14:28	2008-07-29 12:14:28
397	40	62	89	76	1	2008-07-29 12:14:28	2008-07-29 12:14:28
398	41	62	89	77	1	2008-07-29 12:14:28	2008-07-29 12:14:28
399	39	62	89	77	1	2008-07-29 12:14:28	2008-07-29 12:14:28
400	40	62	88	76	2	2008-07-29 12:14:28	2008-07-29 12:14:28
401	41	62	88	78	2	2008-07-29 12:14:28	2008-07-29 12:14:28
402	39	62	88	79	2	2008-07-29 12:14:28	2008-07-29 12:14:28
403	40	62	90	77	3	2008-07-29 12:14:28	2008-07-29 12:14:28
404	41	62	90	77	3	2008-07-29 12:14:28	2008-07-29 12:14:28
405	39	62	90	77	3	2008-07-29 12:14:28	2008-07-29 12:14:28
406	40	62	89	37	4	2008-07-29 12:14:28	2008-07-29 12:14:28
407	41	62	89	37.5	4	2008-07-29 12:14:28	2008-07-29 12:14:28
408	39	62	89	38	4	2008-07-29 12:14:28	2008-07-29 12:14:28
409	30	55	24	74	1	2008-07-29 12:15:00	2008-07-29 12:15:00
410	31	55	24	74	1	2008-07-29 12:15:00	2008-07-29 12:15:00
411	32	55	24	73	1	2008-07-29 12:15:00	2008-07-29 12:15:00
412	30	55	22	75	2	2008-07-29 12:15:00	2008-07-29 12:15:00
413	31	55	22	76	2	2008-07-29 12:15:00	2008-07-29 12:15:00
414	32	55	22	73	2	2008-07-29 12:15:00	2008-07-29 12:15:00
415	30	55	23	75	3	2008-07-29 12:15:00	2008-07-29 12:15:00
416	31	55	23	74	3	2008-07-29 12:15:00	2008-07-29 12:15:00
417	32	55	23	75	3	2008-07-29 12:15:00	2008-07-29 12:15:00
418	30	55	24	37	4	2008-07-29 12:15:00	2008-07-29 12:15:00
419	31	55	24	37.5	4	2008-07-29 12:15:00	2008-07-29 12:15:00
420	32	55	24	35	4	2008-07-29 12:15:00	2008-07-29 12:15:00
421	30	56	108	75	1	2008-07-29 12:15:00	2008-07-29 12:15:00
422	31	56	108	77	1	2008-07-29 12:15:00	2008-07-29 12:15:00
423	32	56	108	76	1	2008-07-29 12:15:00	2008-07-29 12:15:00
424	30	56	107	76	2	2008-07-29 12:15:00	2008-07-29 12:15:00
425	31	56	107	77	2	2008-07-29 12:15:00	2008-07-29 12:15:00
426	32	56	107	75	2	2008-07-29 12:15:00	2008-07-29 12:15:00
427	30	56	106	75	3	2008-07-29 12:15:00	2008-07-29 12:15:00
428	31	56	106	77	3	2008-07-29 12:15:00	2008-07-29 12:15:00
429	32	56	106	76	3	2008-07-29 12:15:00	2008-07-29 12:15:00
430	30	56	108	37.5	4	2008-07-29 12:15:00	2008-07-29 12:15:00
431	31	56	108	38	4	2008-07-29 12:15:00	2008-07-29 12:15:00
432	32	56	108	37	4	2008-07-29 12:15:00	2008-07-29 12:15:00
433	1	1	221	73	1	2008-07-29 12:15:43	2008-07-29 12:15:43
434	1	1	222	75	2	2008-07-29 12:15:43	2008-07-29 12:15:43
435	1	1	220	74	3	2008-07-29 12:15:43	2008-07-29 12:15:43
436	1	1	222	37.5	4	2008-07-29 12:15:43	2008-07-29 12:15:43
437	1	2	52	73	1	2008-07-29 12:15:43	2008-07-29 12:15:43
438	1	2	53	72	2	2008-07-29 12:15:43	2008-07-29 12:15:43
439	1	2	54	72	3	2008-07-29 12:15:43	2008-07-29 12:15:43
440	1	2	52	37	4	2008-07-29 12:15:43	2008-07-29 12:15:43
441	20	39	129	77	1	2008-07-29 12:18:55	2008-07-29 12:18:55
442	20	39	128	77	2	2008-07-29 12:18:55	2008-07-29 12:18:55
443	20	39	127	78	3	2008-07-29 12:18:55	2008-07-29 12:18:55
444	20	39	129	37.5	4	2008-07-29 12:18:55	2008-07-29 12:18:55
445	20	40	223	76	1	2008-07-29 12:18:55	2008-07-29 12:18:55
446	20	40	224	75	2	2008-07-29 12:18:55	2008-07-29 12:18:55
447	20	40	225	76	3	2008-07-29 12:18:55	2008-07-29 12:18:55
448	20	40	223	37.5	4	2008-07-29 12:18:55	2008-07-29 12:18:55
449	54	71	163	75	1	2008-07-29 12:19:40	2008-07-29 12:19:40
450	55	71	163	76	1	2008-07-29 12:19:40	2008-07-29 12:19:40
451	56	71	163	76	1	2008-07-29 12:19:40	2008-07-29 12:19:40
452	54	71	164	74	2	2008-07-29 12:19:40	2008-07-29 12:19:40
453	55	71	164	75	2	2008-07-29 12:19:40	2008-07-29 12:19:40
454	56	71	164	75	2	2008-07-29 12:19:40	2008-07-29 12:19:40
455	54	71	165	75	3	2008-07-29 12:19:40	2008-07-29 12:19:40
456	55	71	165	75	3	2008-07-29 12:19:40	2008-07-29 12:19:40
457	56	71	165	75	3	2008-07-29 12:19:40	2008-07-29 12:19:40
458	54	71	163	36.5	4	2008-07-29 12:19:40	2008-07-29 12:19:40
459	55	71	163	37.5	4	2008-07-29 12:19:40	2008-07-29 12:19:40
460	56	71	163	37.5	4	2008-07-29 12:19:40	2008-07-29 12:19:40
461	54	72	101	76	1	2008-07-29 12:19:40	2008-07-29 12:19:40
462	55	72	101	77	1	2008-07-29 12:19:40	2008-07-29 12:19:40
463	56	72	101	77	1	2008-07-29 12:19:40	2008-07-29 12:19:40
464	54	72	102	77	2	2008-07-29 12:19:40	2008-07-29 12:19:40
465	55	72	102	76	2	2008-07-29 12:19:40	2008-07-29 12:19:40
466	56	72	102	77	2	2008-07-29 12:19:40	2008-07-29 12:19:40
467	54	72	100	76	3	2008-07-29 12:19:40	2008-07-29 12:19:40
468	55	72	100	76	3	2008-07-29 12:19:40	2008-07-29 12:19:40
469	56	72	100	76	3	2008-07-29 12:19:40	2008-07-29 12:19:40
470	54	72	101	37.5	4	2008-07-29 12:19:40	2008-07-29 12:19:40
471	55	72	101	38.5	4	2008-07-29 12:19:40	2008-07-29 12:19:40
472	56	72	101	38	4	2008-07-29 12:19:40	2008-07-29 12:19:40
473	61	77	211	78	1	2008-07-29 15:27:32	2008-07-29 15:27:32
474	61	77	212	77	2	2008-07-29 15:27:32	2008-07-29 15:27:32
475	61	77	213	78	3	2008-07-29 15:27:32	2008-07-29 15:27:32
476	61	77	211	39	4	2008-07-29 15:27:32	2008-07-29 15:27:32
477	61	78	181	77	1	2008-07-29 15:27:32	2008-07-29 15:27:32
478	61	78	183	77	2	2008-07-29 15:27:32	2008-07-29 15:27:32
479	61	78	182	77	3	2008-07-29 15:27:32	2008-07-29 15:27:32
480	61	78	181	38.5	4	2008-07-29 15:27:32	2008-07-29 15:27:32
481	60	75	155	75	1	2008-07-29 15:28:15	2008-07-29 15:28:15
482	60	75	156	75	2	2008-07-29 15:28:15	2008-07-29 15:28:15
483	60	75	154	76	3	2008-07-29 15:28:15	2008-07-29 15:28:15
484	60	75	155	38	4	2008-07-29 15:28:15	2008-07-29 15:28:15
485	60	76	171	77	1	2008-07-29 15:28:15	2008-07-29 15:28:15
486	60	76	169	78	2	2008-07-29 15:28:15	2008-07-29 15:28:15
487	60	76	170	78	3	2008-07-29 15:28:15	2008-07-29 15:28:15
488	60	76	169	38.5	4	2008-07-29 15:28:15	2008-07-29 15:28:15
489	62	79	161	76	1	2008-07-29 15:30:15	2008-07-29 15:30:15
490	62	79	160	75	2	2008-07-29 15:30:15	2008-07-29 15:30:15
491	62	79	162	75	3	2008-07-29 15:30:15	2008-07-29 15:30:15
492	62	79	161	37	4	2008-07-29 15:30:15	2008-07-29 15:30:15
493	62	80	9	78	1	2008-07-29 15:30:15	2008-07-29 15:30:15
494	62	80	8	77	2	2008-07-29 15:30:15	2008-07-29 15:30:15
495	62	80	7	78	3	2008-07-29 15:30:15	2008-07-29 15:30:15
496	62	80	9	38	4	2008-07-29 15:30:15	2008-07-29 15:30:15
497	81	117	223	72	1	2008-07-29 15:31:37	2008-07-29 15:31:37
498	81	117	225	71	2	2008-07-29 15:31:37	2008-07-29 15:31:37
499	81	117	224	72	3	2008-07-29 15:31:37	2008-07-29 15:31:37
500	81	117	225	36	4	2008-07-29 15:31:37	2008-07-29 15:31:37
501	81	118	25	74	1	2008-07-29 15:31:37	2008-07-29 15:31:37
502	81	118	26	74	2	2008-07-29 15:31:37	2008-07-29 15:31:37
503	81	118	27	74	3	2008-07-29 15:31:37	2008-07-29 15:31:37
504	81	118	25	37	4	2008-07-29 15:31:37	2008-07-29 15:31:37
505	78	111	115	75	1	2008-07-29 15:32:59	2008-07-29 15:32:59
506	78	111	117	76	2	2008-07-29 15:32:59	2008-07-29 15:32:59
507	78	111	116	76	3	2008-07-29 15:33:00	2008-07-29 15:33:00
508	78	111	115	37.5	4	2008-07-29 15:33:00	2008-07-29 15:33:00
509	78	112	43	76	1	2008-07-29 15:33:00	2008-07-29 15:33:00
510	78	112	45	75	2	2008-07-29 15:33:00	2008-07-29 15:33:00
511	78	112	44	76	3	2008-07-29 15:33:00	2008-07-29 15:33:00
512	78	112	43	37	4	2008-07-29 15:33:00	2008-07-29 15:33:00
513	79	113	196	75	1	2008-07-29 15:33:24	2008-07-29 15:33:24
514	79	113	197	76	2	2008-07-29 15:33:24	2008-07-29 15:33:24
515	79	113	198	76	3	2008-07-29 15:33:24	2008-07-29 15:33:24
516	79	113	197	37	4	2008-07-29 15:33:24	2008-07-29 15:33:24
517	79	114	134	76	1	2008-07-29 15:33:24	2008-07-29 15:33:24
518	79	114	133	75	2	2008-07-29 15:33:24	2008-07-29 15:33:24
519	79	114	135	74	3	2008-07-29 15:33:24	2008-07-29 15:33:24
520	79	114	133	36.5	4	2008-07-29 15:33:24	2008-07-29 15:33:24
521	65	95	185	76	1	2008-07-29 15:35:21	2008-07-29 15:35:21
522	65	95	184	77	2	2008-07-29 15:35:21	2008-07-29 15:35:21
523	65	95	186	78	3	2008-07-29 15:35:21	2008-07-29 15:35:21
524	65	95	185	38	4	2008-07-29 15:35:21	2008-07-29 15:35:21
525	65	96	191	76	1	2008-07-29 15:35:21	2008-07-29 15:35:21
526	65	96	192	76	2	2008-07-29 15:35:21	2008-07-29 15:35:21
527	65	96	190	76	3	2008-07-29 15:35:21	2008-07-29 15:35:21
528	65	96	191	37.5	4	2008-07-29 15:35:21	2008-07-29 15:35:21
529	76	105	201	76	1	2008-07-29 15:35:25	2008-07-29 15:35:25
530	76	105	200	75	2	2008-07-29 15:35:25	2008-07-29 15:35:25
531	76	105	199	76	3	2008-07-29 15:35:25	2008-07-29 15:35:25
532	76	105	201	38	4	2008-07-29 15:35:25	2008-07-29 15:35:25
533	76	106	221	73	1	2008-07-29 15:35:25	2008-07-29 15:35:25
534	76	106	222	72	2	2008-07-29 15:35:25	2008-07-29 15:35:25
535	76	106	220	73	3	2008-07-29 15:35:25	2008-07-29 15:35:25
536	76	106	222	36	4	2008-07-29 15:35:25	2008-07-29 15:35:25
545	71	103	202	73	1	2008-07-29 15:36:18	2008-07-29 15:36:18
546	71	103	203	74	2	2008-07-29 15:36:18	2008-07-29 15:36:18
547	71	103	204	74	3	2008-07-29 15:36:18	2008-07-29 15:36:18
548	71	103	202	37	4	2008-07-29 15:36:18	2008-07-29 15:36:18
549	71	104	159	77	1	2008-07-29 15:36:18	2008-07-29 15:36:18
550	71	104	158	76	2	2008-07-29 15:36:18	2008-07-29 15:36:18
551	71	104	157	76	3	2008-07-29 15:36:18	2008-07-29 15:36:18
552	71	104	159	38.5	4	2008-07-29 15:36:18	2008-07-29 15:36:18
553	63	81	15	75	1	2008-07-29 15:36:45	2008-07-29 15:36:45
554	63	81	14	76	2	2008-07-29 15:36:45	2008-07-29 15:36:45
555	63	81	13	76	3	2008-07-29 15:36:45	2008-07-29 15:36:45
556	63	81	14	36.5	4	2008-07-29 15:36:45	2008-07-29 15:36:45
557	63	82	129	76	1	2008-07-29 15:36:45	2008-07-29 15:36:45
558	63	82	128	76	2	2008-07-29 15:36:45	2008-07-29 15:36:45
559	63	82	127	77	3	2008-07-29 15:36:45	2008-07-29 15:36:45
560	63	82	129	36.5	4	2008-07-29 15:36:45	2008-07-29 15:36:45
561	90	115	73	77	1	2008-07-29 15:39:21	2008-07-29 15:39:21
562	91	115	73	75	1	2008-07-29 15:39:21	2008-07-29 15:39:21
563	92	115	73	77	1	2008-07-29 15:39:21	2008-07-29 15:39:21
564	90	115	74	76	2	2008-07-29 15:39:21	2008-07-29 15:39:21
565	91	115	74	76	2	2008-07-29 15:39:21	2008-07-29 15:39:21
566	92	115	74	77	2	2008-07-29 15:39:21	2008-07-29 15:39:21
567	90	115	75	75	3	2008-07-29 15:39:21	2008-07-29 15:39:21
568	91	115	75	76	3	2008-07-29 15:39:21	2008-07-29 15:39:21
569	92	115	75	76	3	2008-07-29 15:39:21	2008-07-29 15:39:21
570	90	115	73	36.5	4	2008-07-29 15:39:21	2008-07-29 15:39:21
571	91	115	73	38	4	2008-07-29 15:39:21	2008-07-29 15:39:21
572	92	115	73	38	4	2008-07-29 15:39:21	2008-07-29 15:39:21
573	90	116	139	76	1	2008-07-29 15:39:21	2008-07-29 15:39:21
574	91	116	139	75	1	2008-07-29 15:39:21	2008-07-29 15:39:21
575	92	116	139	77	1	2008-07-29 15:39:21	2008-07-29 15:39:21
576	90	116	141	76	2	2008-07-29 15:39:21	2008-07-29 15:39:21
577	91	116	141	75	2	2008-07-29 15:39:21	2008-07-29 15:39:21
578	92	116	141	78	2	2008-07-29 15:39:21	2008-07-29 15:39:21
579	90	116	140	74	3	2008-07-29 15:39:21	2008-07-29 15:39:21
580	91	116	140	74	3	2008-07-29 15:39:21	2008-07-29 15:39:21
581	92	116	140	77	3	2008-07-29 15:39:21	2008-07-29 15:39:21
582	90	116	139	37.5	4	2008-07-29 15:39:21	2008-07-29 15:39:21
583	91	116	139	37.5	4	2008-07-29 15:39:21	2008-07-29 15:39:21
584	92	116	139	38.5	4	2008-07-29 15:39:21	2008-07-29 15:39:21
585	83	129	163	75	1	2008-07-29 15:40:31	2008-07-29 15:40:31
586	83	129	164	74	2	2008-07-29 15:40:31	2008-07-29 15:40:31
587	83	129	165	75	3	2008-07-29 15:40:31	2008-07-29 15:40:31
588	83	129	163	37	4	2008-07-29 15:40:31	2008-07-29 15:40:31
589	83	130	151	75	1	2008-07-29 15:40:31	2008-07-29 15:40:31
590	83	130	152	74	2	2008-07-29 15:40:31	2008-07-29 15:40:31
591	83	130	153	76	3	2008-07-29 15:40:31	2008-07-29 15:40:31
592	83	130	151	38	4	2008-07-29 15:40:31	2008-07-29 15:40:31
593	87	127	215	76	1	2008-07-29 15:42:04	2008-07-29 15:42:04
594	89	127	215	76	1	2008-07-29 15:42:04	2008-07-29 15:42:04
595	88	127	215	76	1	2008-07-29 15:42:04	2008-07-29 15:42:04
596	87	127	214	75	2	2008-07-29 15:42:04	2008-07-29 15:42:04
597	89	127	214	75	2	2008-07-29 15:42:04	2008-07-29 15:42:04
598	88	127	214	75	2	2008-07-29 15:42:04	2008-07-29 15:42:04
599	87	127	216	78	3	2008-07-29 15:42:04	2008-07-29 15:42:04
600	89	127	216	77	3	2008-07-29 15:42:04	2008-07-29 15:42:04
601	88	127	216	76	3	2008-07-29 15:42:04	2008-07-29 15:42:04
602	87	127	214	38	4	2008-07-29 15:42:04	2008-07-29 15:42:04
603	89	127	214	37	4	2008-07-29 15:42:04	2008-07-29 15:42:04
604	88	127	214	38	4	2008-07-29 15:42:04	2008-07-29 15:42:04
605	87	128	166	76	1	2008-07-29 15:42:04	2008-07-29 15:42:04
606	89	128	166	76	1	2008-07-29 15:42:04	2008-07-29 15:42:04
607	88	128	166	76	1	2008-07-29 15:42:04	2008-07-29 15:42:04
608	87	128	167	75	2	2008-07-29 15:42:04	2008-07-29 15:42:04
609	89	128	167	75	2	2008-07-29 15:42:04	2008-07-29 15:42:04
610	88	128	167	74	2	2008-07-29 15:42:04	2008-07-29 15:42:04
611	87	128	168	75	3	2008-07-29 15:42:04	2008-07-29 15:42:04
612	89	128	168	74	3	2008-07-29 15:42:04	2008-07-29 15:42:04
613	88	128	168	73	3	2008-07-29 15:42:04	2008-07-29 15:42:04
614	87	128	166	37.5	4	2008-07-29 15:42:04	2008-07-29 15:42:04
615	89	128	166	38	4	2008-07-29 15:42:04	2008-07-29 15:42:04
616	88	128	166	37	4	2008-07-29 15:42:04	2008-07-29 15:42:04
617	108	139	76	76	1	2008-07-29 15:44:35	2008-07-29 15:44:35
618	109	139	76	75	1	2008-07-29 15:44:35	2008-07-29 15:44:35
619	110	139	76	75	1	2008-07-29 15:44:35	2008-07-29 15:44:35
620	108	139	77	75	2	2008-07-29 15:44:35	2008-07-29 15:44:35
621	109	139	77	74	2	2008-07-29 15:44:35	2008-07-29 15:44:35
622	110	139	77	74	2	2008-07-29 15:44:35	2008-07-29 15:44:35
623	108	139	78	73	3	2008-07-29 15:44:35	2008-07-29 15:44:35
624	109	139	78	74	3	2008-07-29 15:44:35	2008-07-29 15:44:35
625	110	139	78	71	3	2008-07-29 15:44:35	2008-07-29 15:44:35
626	108	139	76	37	4	2008-07-29 15:44:35	2008-07-29 15:44:35
627	109	139	76	37.5	4	2008-07-29 15:44:35	2008-07-29 15:44:35
628	110	139	76	37.5	4	2008-07-29 15:44:35	2008-07-29 15:44:35
629	108	140	42	73	1	2008-07-29 15:44:35	2008-07-29 15:44:35
630	109	140	42	74	1	2008-07-29 15:44:35	2008-07-29 15:44:35
631	110	140	42	72	1	2008-07-29 15:44:35	2008-07-29 15:44:35
632	108	140	40	74	2	2008-07-29 15:44:35	2008-07-29 15:44:35
633	109	140	40	73	2	2008-07-29 15:44:35	2008-07-29 15:44:35
634	110	140	40	72	2	2008-07-29 15:44:35	2008-07-29 15:44:35
635	108	140	41	72	3	2008-07-29 15:44:35	2008-07-29 15:44:35
636	109	140	41	73	3	2008-07-29 15:44:35	2008-07-29 15:44:35
637	110	140	41	71	3	2008-07-29 15:44:35	2008-07-29 15:44:35
638	108	140	42	36	4	2008-07-29 15:44:35	2008-07-29 15:44:35
639	109	140	42	36	4	2008-07-29 15:44:35	2008-07-29 15:44:35
640	110	140	42	36.5	4	2008-07-29 15:44:35	2008-07-29 15:44:35
641	120	147	194	71	1	2008-07-29 15:45:05	2008-07-29 15:45:05
642	120	147	193	71	2	2008-07-29 15:45:05	2008-07-29 15:45:05
643	120	147	195	70	3	2008-07-29 15:45:05	2008-07-29 15:45:05
644	120	147	194	35	4	2008-07-29 15:45:05	2008-07-29 15:45:05
645	120	148	35	72	1	2008-07-29 15:45:05	2008-07-29 15:45:05
646	120	148	36	72	2	2008-07-29 15:45:05	2008-07-29 15:45:05
647	120	148	34	71	3	2008-07-29 15:45:05	2008-07-29 15:45:05
648	120	148	35	35.5	4	2008-07-29 15:45:05	2008-07-29 15:45:05
649	105	141	85	71	1	2008-07-29 15:45:21	2008-07-29 15:45:21
650	106	141	85	73	1	2008-07-29 15:45:21	2008-07-29 15:45:21
651	107	141	85	72	1	2008-07-29 15:45:21	2008-07-29 15:45:21
652	105	141	87	70	2	2008-07-29 15:45:21	2008-07-29 15:45:21
653	106	141	87	73	2	2008-07-29 15:45:21	2008-07-29 15:45:21
654	107	141	87	73	2	2008-07-29 15:45:21	2008-07-29 15:45:21
655	105	141	86	72	3	2008-07-29 15:45:21	2008-07-29 15:45:21
656	106	141	86	74	3	2008-07-29 15:45:21	2008-07-29 15:45:21
657	107	141	86	72	3	2008-07-29 15:45:21	2008-07-29 15:45:21
658	105	141	85	35	4	2008-07-29 15:45:21	2008-07-29 15:45:21
659	106	141	85	36	4	2008-07-29 15:45:21	2008-07-29 15:45:21
660	107	141	85	36	4	2008-07-29 15:45:21	2008-07-29 15:45:21
661	105	142	58	74	1	2008-07-29 15:45:21	2008-07-29 15:45:21
662	106	142	58	75	1	2008-07-29 15:45:21	2008-07-29 15:45:21
663	107	142	58	74	1	2008-07-29 15:45:21	2008-07-29 15:45:21
664	105	142	60	73	2	2008-07-29 15:45:21	2008-07-29 15:45:21
665	106	142	60	75	2	2008-07-29 15:45:21	2008-07-29 15:45:21
666	107	142	60	74	2	2008-07-29 15:45:22	2008-07-29 15:45:22
667	105	142	59	73	3	2008-07-29 15:45:22	2008-07-29 15:45:22
668	106	142	59	76	3	2008-07-29 15:45:22	2008-07-29 15:45:22
669	107	142	59	75	3	2008-07-29 15:45:22	2008-07-29 15:45:22
670	105	142	58	36	4	2008-07-29 15:45:22	2008-07-29 15:45:22
671	106	142	58	37	4	2008-07-29 15:45:22	2008-07-29 15:45:22
672	107	142	58	37	4	2008-07-29 15:45:22	2008-07-29 15:45:22
681	69	93	105	74	1	2008-07-29 15:47:34	2008-07-29 15:47:34
682	69	93	104	76	2	2008-07-29 15:47:34	2008-07-29 15:47:34
683	69	93	103	75	3	2008-07-29 15:47:34	2008-07-29 15:47:34
684	69	93	105	38.5	4	2008-07-29 15:47:34	2008-07-29 15:47:34
685	69	94	10	76	1	2008-07-29 15:47:34	2008-07-29 15:47:34
686	69	94	11	74	2	2008-07-29 15:47:34	2008-07-29 15:47:34
687	69	94	12	75	3	2008-07-29 15:47:34	2008-07-29 15:47:34
688	69	94	11	37	4	2008-07-29 15:47:34	2008-07-29 15:47:34
689	84	137	4	75	1	2008-07-29 15:48:33	2008-07-29 15:48:33
690	85	137	4	75	1	2008-07-29 15:48:33	2008-07-29 15:48:33
691	86	137	4	74	1	2008-07-29 15:48:33	2008-07-29 15:48:33
692	84	137	5	74	2	2008-07-29 15:48:33	2008-07-29 15:48:33
693	85	137	5	74	2	2008-07-29 15:48:33	2008-07-29 15:48:33
694	86	137	5	74	2	2008-07-29 15:48:33	2008-07-29 15:48:33
695	84	137	6	73	3	2008-07-29 15:48:33	2008-07-29 15:48:33
696	85	137	6	75	3	2008-07-29 15:48:33	2008-07-29 15:48:33
697	86	137	6	75	3	2008-07-29 15:48:33	2008-07-29 15:48:33
698	84	137	4	36.5	4	2008-07-29 15:48:33	2008-07-29 15:48:33
699	85	137	4	35	4	2008-07-29 15:48:33	2008-07-29 15:48:33
700	86	137	4	37	4	2008-07-29 15:48:33	2008-07-29 15:48:33
701	84	138	18	76	1	2008-07-29 15:48:33	2008-07-29 15:48:33
702	85	138	18	77	1	2008-07-29 15:48:33	2008-07-29 15:48:33
703	86	138	18	75	1	2008-07-29 15:48:33	2008-07-29 15:48:33
704	84	138	16	76	2	2008-07-29 15:48:33	2008-07-29 15:48:33
705	85	138	16	76	2	2008-07-29 15:48:33	2008-07-29 15:48:33
706	86	138	16	75	2	2008-07-29 15:48:33	2008-07-29 15:48:33
707	84	138	17	75	3	2008-07-29 15:48:34	2008-07-29 15:48:34
708	85	138	17	77	3	2008-07-29 15:48:34	2008-07-29 15:48:34
709	86	138	17	76	3	2008-07-29 15:48:34	2008-07-29 15:48:34
710	84	138	18	37	4	2008-07-29 15:48:34	2008-07-29 15:48:34
711	85	138	18	36	4	2008-07-29 15:48:34	2008-07-29 15:48:34
712	86	138	18	36.5	4	2008-07-29 15:48:34	2008-07-29 15:48:34
713	67	97	49	74	1	2008-07-29 15:50:11	2008-07-29 15:50:11
714	67	97	51	74	2	2008-07-29 15:50:11	2008-07-29 15:50:11
715	67	97	50	75	3	2008-07-29 15:50:11	2008-07-29 15:50:11
716	67	97	51	37	4	2008-07-29 15:50:11	2008-07-29 15:50:11
717	67	98	178	76	1	2008-07-29 15:50:11	2008-07-29 15:50:11
718	67	98	180	76	2	2008-07-29 15:50:11	2008-07-29 15:50:11
719	67	98	179	77	3	2008-07-29 15:50:11	2008-07-29 15:50:11
720	67	98	178	38	4	2008-07-29 15:50:11	2008-07-29 15:50:11
721	117	145	53	74	1	2008-07-29 15:51:32	2008-07-29 15:51:32
722	118	145	53	75	1	2008-07-29 15:51:32	2008-07-29 15:51:32
723	119	145	53	74	1	2008-07-29 15:51:32	2008-07-29 15:51:32
724	117	145	52	74	2	2008-07-29 15:51:32	2008-07-29 15:51:32
725	118	145	52	75	2	2008-07-29 15:51:32	2008-07-29 15:51:32
726	119	145	52	75	2	2008-07-29 15:51:32	2008-07-29 15:51:32
727	117	145	54	74	3	2008-07-29 15:51:32	2008-07-29 15:51:32
728	118	145	54	75	3	2008-07-29 15:51:32	2008-07-29 15:51:32
729	119	145	54	75	3	2008-07-29 15:51:32	2008-07-29 15:51:32
730	117	145	52	36	4	2008-07-29 15:51:32	2008-07-29 15:51:32
731	118	145	52	35.5	4	2008-07-29 15:51:32	2008-07-29 15:51:32
732	119	145	52	35.5	4	2008-07-29 15:51:32	2008-07-29 15:51:32
733	117	146	48	76	1	2008-07-29 15:51:32	2008-07-29 15:51:32
734	118	146	48	75	1	2008-07-29 15:51:32	2008-07-29 15:51:32
735	119	146	48	74	1	2008-07-29 15:51:32	2008-07-29 15:51:32
736	117	146	46	74	2	2008-07-29 15:51:32	2008-07-29 15:51:32
737	118	146	46	77	2	2008-07-29 15:51:32	2008-07-29 15:51:32
738	119	146	46	76	2	2008-07-29 15:51:32	2008-07-29 15:51:32
739	117	146	47	75	3	2008-07-29 15:51:32	2008-07-29 15:51:32
740	118	146	47	76	3	2008-07-29 15:51:32	2008-07-29 15:51:32
741	119	146	47	76	3	2008-07-29 15:51:32	2008-07-29 15:51:32
742	117	146	46	37	4	2008-07-29 15:51:32	2008-07-29 15:51:32
743	118	146	46	40.5	4	2008-07-29 15:51:32	2008-07-29 15:51:32
744	119	146	46	36.5	4	2008-07-29 15:51:32	2008-07-29 15:51:32
745	96	131	68	76	1	2008-07-29 15:52:49	2008-07-29 15:52:49
746	97	131	68	73	1	2008-07-29 15:52:49	2008-07-29 15:52:49
747	98	131	68	75	1	2008-07-29 15:52:49	2008-07-29 15:52:49
748	96	131	67	74	2	2008-07-29 15:52:49	2008-07-29 15:52:49
749	97	131	67	73	2	2008-07-29 15:52:49	2008-07-29 15:52:49
750	98	131	67	74	2	2008-07-29 15:52:49	2008-07-29 15:52:49
751	96	131	69	74	3	2008-07-29 15:52:49	2008-07-29 15:52:49
752	97	131	69	73	3	2008-07-29 15:52:49	2008-07-29 15:52:49
753	98	131	69	74	3	2008-07-29 15:52:49	2008-07-29 15:52:49
754	96	131	68	37	4	2008-07-29 15:52:49	2008-07-29 15:52:49
755	97	131	68	36	4	2008-07-29 15:52:49	2008-07-29 15:52:49
756	98	131	68	38.5	4	2008-07-29 15:52:49	2008-07-29 15:52:49
757	96	132	84	72	1	2008-07-29 15:52:49	2008-07-29 15:52:49
758	97	132	84	72	1	2008-07-29 15:52:49	2008-07-29 15:52:49
759	98	132	84	73	1	2008-07-29 15:52:49	2008-07-29 15:52:49
760	96	132	82	74	2	2008-07-29 15:52:49	2008-07-29 15:52:49
761	97	132	82	74	2	2008-07-29 15:52:49	2008-07-29 15:52:49
762	98	132	82	75	2	2008-07-29 15:52:49	2008-07-29 15:52:49
763	96	132	83	71	3	2008-07-29 15:52:49	2008-07-29 15:52:49
764	97	132	83	73	3	2008-07-29 15:52:49	2008-07-29 15:52:49
765	98	132	83	71	3	2008-07-29 15:52:49	2008-07-29 15:52:49
766	96	132	82	36.5	4	2008-07-29 15:52:49	2008-07-29 15:52:49
767	97	132	82	37	4	2008-07-29 15:52:49	2008-07-29 15:52:49
768	98	132	82	37	4	2008-07-29 15:52:49	2008-07-29 15:52:49
769	93	143	148	77	1	2008-07-29 15:53:39	2008-07-29 15:53:39
770	94	143	148	75	1	2008-07-29 15:53:39	2008-07-29 15:53:39
771	95	143	148	76	1	2008-07-29 15:53:39	2008-07-29 15:53:39
772	93	143	149	77	2	2008-07-29 15:53:39	2008-07-29 15:53:39
773	94	143	149	76	2	2008-07-29 15:53:39	2008-07-29 15:53:39
774	95	143	149	77	2	2008-07-29 15:53:39	2008-07-29 15:53:39
775	93	143	150	76	3	2008-07-29 15:53:39	2008-07-29 15:53:39
776	94	143	150	75	3	2008-07-29 15:53:39	2008-07-29 15:53:39
777	95	143	150	75	3	2008-07-29 15:53:39	2008-07-29 15:53:39
778	93	143	149	38	4	2008-07-29 15:53:39	2008-07-29 15:53:39
779	94	143	149	38	4	2008-07-29 15:53:39	2008-07-29 15:53:39
780	95	143	149	38	4	2008-07-29 15:53:39	2008-07-29 15:53:39
781	93	144	39	71	1	2008-07-29 15:53:39	2008-07-29 15:53:39
782	94	144	39	73	1	2008-07-29 15:53:39	2008-07-29 15:53:39
783	95	144	39	73	1	2008-07-29 15:53:39	2008-07-29 15:53:39
784	93	144	37	73	2	2008-07-29 15:53:39	2008-07-29 15:53:39
785	94	144	37	73	2	2008-07-29 15:53:39	2008-07-29 15:53:39
786	95	144	37	74	2	2008-07-29 15:53:39	2008-07-29 15:53:39
787	93	144	38	73	3	2008-07-29 15:53:39	2008-07-29 15:53:39
788	94	144	38	72	3	2008-07-29 15:53:39	2008-07-29 15:53:39
789	95	144	38	74	3	2008-07-29 15:53:39	2008-07-29 15:53:39
790	93	144	39	36	4	2008-07-29 15:53:39	2008-07-29 15:53:39
791	94	144	39	36.5	4	2008-07-29 15:53:39	2008-07-29 15:53:39
792	95	144	39	36.5	4	2008-07-29 15:53:39	2008-07-29 15:53:39
793	80	119	63	75	1	2008-07-29 15:53:56	2008-07-29 15:53:56
794	80	119	61	74	2	2008-07-29 15:53:56	2008-07-29 15:53:56
795	80	119	62	74	3	2008-07-29 15:53:56	2008-07-29 15:53:56
796	80	119	63	37	4	2008-07-29 15:53:56	2008-07-29 15:53:56
797	80	120	187	74	1	2008-07-29 15:53:56	2008-07-29 15:53:56
798	80	120	188	75	2	2008-07-29 15:53:56	2008-07-29 15:53:56
799	80	120	189	75	3	2008-07-29 15:53:56	2008-07-29 15:53:56
800	80	120	188	37.5	4	2008-07-29 15:53:56	2008-07-29 15:53:56
801	99	133	130	76	1	2008-07-29 15:54:41	2008-07-29 15:54:41
802	101	133	130	74	1	2008-07-29 15:54:41	2008-07-29 15:54:41
803	100	133	130	73	1	2008-07-29 15:54:41	2008-07-29 15:54:41
804	99	133	131	75	2	2008-07-29 15:54:41	2008-07-29 15:54:41
805	101	133	131	74	2	2008-07-29 15:54:41	2008-07-29 15:54:41
806	100	133	131	75	2	2008-07-29 15:54:41	2008-07-29 15:54:41
807	99	133	132	77	3	2008-07-29 15:54:41	2008-07-29 15:54:41
808	101	133	132	75	3	2008-07-29 15:54:41	2008-07-29 15:54:41
809	100	133	132	74	3	2008-07-29 15:54:41	2008-07-29 15:54:41
810	99	133	130	37	4	2008-07-29 15:54:41	2008-07-29 15:54:41
811	101	133	130	37.5	4	2008-07-29 15:54:41	2008-07-29 15:54:41
812	100	133	130	37	4	2008-07-29 15:54:41	2008-07-29 15:54:41
813	99	134	29	76	1	2008-07-29 15:54:41	2008-07-29 15:54:41
814	101	134	29	73	1	2008-07-29 15:54:41	2008-07-29 15:54:41
815	100	134	29	75	1	2008-07-29 15:54:41	2008-07-29 15:54:41
816	99	134	28	75	2	2008-07-29 15:54:41	2008-07-29 15:54:41
817	101	134	28	73	2	2008-07-29 15:54:41	2008-07-29 15:54:41
818	100	134	28	76	2	2008-07-29 15:54:41	2008-07-29 15:54:41
819	99	134	30	74	3	2008-07-29 15:54:41	2008-07-29 15:54:41
820	101	134	30	73	3	2008-07-29 15:54:41	2008-07-29 15:54:41
821	100	134	30	73	3	2008-07-29 15:54:41	2008-07-29 15:54:41
822	99	134	29	37.5	4	2008-07-29 15:54:41	2008-07-29 15:54:41
823	101	134	29	37	4	2008-07-29 15:54:41	2008-07-29 15:54:41
824	100	134	29	37	4	2008-07-29 15:54:41	2008-07-29 15:54:41
825	74	109	107	75	1	2008-07-29 15:55:24	2008-07-29 15:55:24
826	74	109	108	76	2	2008-07-29 15:55:24	2008-07-29 15:55:24
827	74	109	106	77	3	2008-07-29 15:55:24	2008-07-29 15:55:24
828	74	109	108	37	4	2008-07-29 15:55:24	2008-07-29 15:55:24
829	74	110	138	76	1	2008-07-29 15:55:24	2008-07-29 15:55:24
830	74	110	136	76	2	2008-07-29 15:55:24	2008-07-29 15:55:24
831	74	110	137	75	3	2008-07-29 15:55:24	2008-07-29 15:55:24
832	74	110	138	37	4	2008-07-29 15:55:24	2008-07-29 15:55:24
833	70	99	175	75	1	2008-07-29 15:56:23	2008-07-29 15:56:23
834	70	99	177	75	2	2008-07-29 15:56:23	2008-07-29 15:56:23
835	70	99	176	75	3	2008-07-29 15:56:23	2008-07-29 15:56:23
836	70	99	175	37.5	4	2008-07-29 15:56:23	2008-07-29 15:56:23
837	70	100	147	74	1	2008-07-29 15:56:23	2008-07-29 15:56:23
838	70	100	146	75	2	2008-07-29 15:56:23	2008-07-29 15:56:23
839	70	100	145	73	3	2008-07-29 15:56:23	2008-07-29 15:56:23
840	70	100	146	37.5	4	2008-07-29 15:56:23	2008-07-29 15:56:23
849	68	91	101	76	1	2008-07-29 15:57:02	2008-07-29 15:57:02
850	68	91	102	76	2	2008-07-29 15:57:02	2008-07-29 15:57:02
851	68	91	100	75	3	2008-07-29 15:57:02	2008-07-29 15:57:02
852	68	91	101	37.5	4	2008-07-29 15:57:02	2008-07-29 15:57:02
853	68	92	207	74	1	2008-07-29 15:57:02	2008-07-29 15:57:02
854	68	92	205	73	2	2008-07-29 15:57:02	2008-07-29 15:57:02
855	68	92	206	75	3	2008-07-29 15:57:02	2008-07-29 15:57:02
856	68	92	207	36.5	4	2008-07-29 15:57:02	2008-07-29 15:57:02
857	64	107	33	75	1	2008-07-29 15:59:30	2008-07-29 15:59:30
858	64	107	31	74	2	2008-07-29 15:59:30	2008-07-29 15:59:30
859	64	107	32	74	3	2008-07-29 15:59:30	2008-07-29 15:59:30
860	64	107	31	38	4	2008-07-29 15:59:30	2008-07-29 15:59:30
861	64	108	70	75	1	2008-07-29 15:59:30	2008-07-29 15:59:30
862	64	108	71	75	2	2008-07-29 15:59:30	2008-07-29 15:59:30
863	64	108	72	74	3	2008-07-29 15:59:30	2008-07-29 15:59:30
864	64	108	70	38	4	2008-07-29 15:59:30	2008-07-29 15:59:30
865	114	121	57	76	1	2008-07-29 15:59:32	2008-07-29 15:59:32
866	115	121	57	77	1	2008-07-29 15:59:33	2008-07-29 15:59:33
867	116	121	57	75	1	2008-07-29 15:59:33	2008-07-29 15:59:33
868	114	121	56	73	2	2008-07-29 15:59:33	2008-07-29 15:59:33
869	115	121	56	75	2	2008-07-29 15:59:33	2008-07-29 15:59:33
870	116	121	56	74	2	2008-07-29 15:59:33	2008-07-29 15:59:33
871	114	121	55	73	3	2008-07-29 15:59:33	2008-07-29 15:59:33
872	115	121	55	75	3	2008-07-29 15:59:33	2008-07-29 15:59:33
873	116	121	55	74	3	2008-07-29 15:59:33	2008-07-29 15:59:33
874	114	121	57	37.5	4	2008-07-29 15:59:33	2008-07-29 15:59:33
875	115	121	57	36	4	2008-07-29 15:59:33	2008-07-29 15:59:33
876	116	121	57	38	4	2008-07-29 15:59:33	2008-07-29 15:59:33
877	114	122	80	76	1	2008-07-29 15:59:33	2008-07-29 15:59:33
878	115	122	80	75	1	2008-07-29 15:59:33	2008-07-29 15:59:33
879	116	122	80	74	1	2008-07-29 15:59:33	2008-07-29 15:59:33
880	114	122	81	74	2	2008-07-29 15:59:33	2008-07-29 15:59:33
881	115	122	81	78	2	2008-07-29 15:59:33	2008-07-29 15:59:33
882	116	122	81	75	2	2008-07-29 15:59:33	2008-07-29 15:59:33
883	114	122	79	76	3	2008-07-29 15:59:33	2008-07-29 15:59:33
884	115	122	79	76	3	2008-07-29 15:59:33	2008-07-29 15:59:33
885	116	122	79	76	3	2008-07-29 15:59:33	2008-07-29 15:59:33
886	114	122	80	37.5	4	2008-07-29 15:59:33	2008-07-29 15:59:33
887	115	122	80	35	4	2008-07-29 15:59:33	2008-07-29 15:59:33
888	116	122	80	35.5	4	2008-07-29 15:59:33	2008-07-29 15:59:33
889	72	87	118	76	1	2008-07-29 15:59:39	2008-07-29 15:59:39
890	72	87	120	75	2	2008-07-29 15:59:39	2008-07-29 15:59:39
891	72	87	119	75	3	2008-07-29 15:59:39	2008-07-29 15:59:39
892	72	87	118	37	4	2008-07-29 15:59:39	2008-07-29 15:59:39
893	72	88	99	77	1	2008-07-29 15:59:39	2008-07-29 15:59:39
894	72	88	97	76	2	2008-07-29 15:59:39	2008-07-29 15:59:39
895	72	88	98	78	3	2008-07-29 15:59:39	2008-07-29 15:59:39
896	72	88	99	37	4	2008-07-29 15:59:39	2008-07-29 15:59:39
897	111	123	122	75	1	2008-07-29 16:02:17	2008-07-29 16:02:17
898	112	123	122	75	1	2008-07-29 16:02:17	2008-07-29 16:02:17
899	113	123	122	75	1	2008-07-29 16:02:17	2008-07-29 16:02:17
900	111	123	121	74	2	2008-07-29 16:02:17	2008-07-29 16:02:17
901	112	123	121	75	2	2008-07-29 16:02:17	2008-07-29 16:02:17
902	113	123	121	73	2	2008-07-29 16:02:17	2008-07-29 16:02:17
903	111	123	123	76	3	2008-07-29 16:02:17	2008-07-29 16:02:17
904	112	123	123	77	3	2008-07-29 16:02:17	2008-07-29 16:02:17
905	113	123	123	76	3	2008-07-29 16:02:17	2008-07-29 16:02:17
906	111	123	122	37	4	2008-07-29 16:02:17	2008-07-29 16:02:17
907	112	123	122	34	4	2008-07-29 16:02:17	2008-07-29 16:02:17
908	113	123	122	35.5	4	2008-07-29 16:02:17	2008-07-29 16:02:17
909	111	124	23	74	1	2008-07-29 16:02:17	2008-07-29 16:02:17
910	112	124	23	73	1	2008-07-29 16:02:17	2008-07-29 16:02:17
911	113	124	23	75	1	2008-07-29 16:02:17	2008-07-29 16:02:17
912	111	124	24	74	2	2008-07-29 16:02:17	2008-07-29 16:02:17
913	112	124	24	75	2	2008-07-29 16:02:17	2008-07-29 16:02:17
914	113	124	24	75	2	2008-07-29 16:02:17	2008-07-29 16:02:17
915	111	124	22	76	3	2008-07-29 16:02:17	2008-07-29 16:02:17
916	112	124	22	76	3	2008-07-29 16:02:17	2008-07-29 16:02:17
917	113	124	22	74	3	2008-07-29 16:02:17	2008-07-29 16:02:17
918	111	124	23	36	4	2008-07-29 16:02:17	2008-07-29 16:02:17
919	112	124	23	34	4	2008-07-29 16:02:17	2008-07-29 16:02:17
920	113	124	23	37.5	4	2008-07-29 16:02:17	2008-07-29 16:02:17
921	75	89	126	76	1	2008-07-29 16:03:45	2008-07-29 16:03:45
922	75	89	124	75	2	2008-07-29 16:03:45	2008-07-29 16:03:45
923	75	89	125	74	3	2008-07-29 16:03:45	2008-07-29 16:03:45
924	75	89	126	37.5	4	2008-07-29 16:03:45	2008-07-29 16:03:45
925	75	90	111	76	1	2008-07-29 16:03:45	2008-07-29 16:03:45
926	75	90	109	75	2	2008-07-29 16:03:45	2008-07-29 16:03:45
927	75	90	110	75	3	2008-07-29 16:03:45	2008-07-29 16:03:45
928	75	90	111	37.5	4	2008-07-29 16:03:45	2008-07-29 16:03:45
929	102	135	64	76	1	2008-07-29 16:04:37	2008-07-29 16:04:37
930	103	135	64	74	1	2008-07-29 16:04:37	2008-07-29 16:04:37
931	104	135	64	75	1	2008-07-29 16:04:37	2008-07-29 16:04:37
932	102	135	65	75	2	2008-07-29 16:04:37	2008-07-29 16:04:37
933	103	135	65	74	2	2008-07-29 16:04:37	2008-07-29 16:04:37
934	104	135	65	75	2	2008-07-29 16:04:37	2008-07-29 16:04:37
935	102	135	66	76	3	2008-07-29 16:04:37	2008-07-29 16:04:37
936	103	135	66	75	3	2008-07-29 16:04:37	2008-07-29 16:04:37
937	104	135	66	76	3	2008-07-29 16:04:37	2008-07-29 16:04:37
938	102	135	64	38	4	2008-07-29 16:04:37	2008-07-29 16:04:37
939	103	135	64	37	4	2008-07-29 16:04:37	2008-07-29 16:04:37
940	104	135	64	37.5	4	2008-07-29 16:04:37	2008-07-29 16:04:37
941	102	136	3	74	1	2008-07-29 16:04:37	2008-07-29 16:04:37
942	103	136	3	74	1	2008-07-29 16:04:37	2008-07-29 16:04:37
943	104	136	3	75	1	2008-07-29 16:04:37	2008-07-29 16:04:37
944	102	136	2	72	2	2008-07-29 16:04:37	2008-07-29 16:04:37
945	103	136	2	73	2	2008-07-29 16:04:37	2008-07-29 16:04:37
946	104	136	2	74	2	2008-07-29 16:04:37	2008-07-29 16:04:37
947	102	136	1	74	3	2008-07-29 16:04:37	2008-07-29 16:04:37
948	103	136	1	73	3	2008-07-29 16:04:37	2008-07-29 16:04:37
949	104	136	1	75	3	2008-07-29 16:04:37	2008-07-29 16:04:37
950	102	136	3	37	4	2008-07-29 16:04:37	2008-07-29 16:04:37
951	103	136	3	37	4	2008-07-29 16:04:37	2008-07-29 16:04:37
952	104	136	3	37	4	2008-07-29 16:04:37	2008-07-29 16:04:37
953	77	85	93	76	1	2008-07-29 16:06:23	2008-07-29 16:06:23
954	77	85	92	75	2	2008-07-29 16:06:23	2008-07-29 16:06:23
955	77	85	91	74	3	2008-07-29 16:06:23	2008-07-29 16:06:23
956	77	85	93	38	4	2008-07-29 16:06:23	2008-07-29 16:06:23
957	77	86	173	78	1	2008-07-29 16:06:23	2008-07-29 16:06:23
958	77	86	174	77	2	2008-07-29 16:06:23	2008-07-29 16:06:23
959	77	86	172	77	3	2008-07-29 16:06:23	2008-07-29 16:06:23
960	77	86	173	38.5	4	2008-07-29 16:06:23	2008-07-29 16:06:23
961	82	125	95	73	1	2008-07-29 16:07:01	2008-07-29 16:07:01
962	82	125	96	73	2	2008-07-29 16:07:01	2008-07-29 16:07:01
963	82	125	94	76	3	2008-07-29 16:07:01	2008-07-29 16:07:01
964	82	125	95	37	4	2008-07-29 16:07:01	2008-07-29 16:07:01
965	82	126	209	75	1	2008-07-29 16:07:01	2008-07-29 16:07:01
966	82	126	208	74	2	2008-07-29 16:07:01	2008-07-29 16:07:01
967	82	126	210	74	3	2008-07-29 16:07:01	2008-07-29 16:07:01
968	82	126	209	37	4	2008-07-29 16:07:01	2008-07-29 16:07:01
969	66	83	89	76	1	2008-07-29 16:08:23	2008-07-29 16:08:23
970	66	83	88	77	2	2008-07-29 16:08:23	2008-07-29 16:08:23
971	66	83	90	76	3	2008-07-29 16:08:23	2008-07-29 16:08:23
972	66	83	89	38	4	2008-07-29 16:08:23	2008-07-29 16:08:23
973	66	84	217	75	1	2008-07-29 16:08:23	2008-07-29 16:08:23
974	66	84	218	75	2	2008-07-29 16:08:23	2008-07-29 16:08:23
975	66	84	219	76	3	2008-07-29 16:08:23	2008-07-29 16:08:23
976	66	84	217	38	4	2008-07-29 16:08:23	2008-07-29 16:08:23
977	73	101	21	76	1	2008-07-29 16:11:16	2008-07-29 16:11:16
978	73	101	19	75	2	2008-07-29 16:11:16	2008-07-29 16:11:16
979	73	101	20	75	3	2008-07-29 16:11:16	2008-07-29 16:11:16
980	73	101	21	37	4	2008-07-29 16:11:16	2008-07-29 16:11:16
981	73	102	144	76	1	2008-07-29 16:11:16	2008-07-29 16:11:16
982	73	102	142	76	2	2008-07-29 16:11:16	2008-07-29 16:11:16
983	73	102	143	75	3	2008-07-29 16:11:16	2008-07-29 16:11:16
984	73	102	144	37	4	2008-07-29 16:11:16	2008-07-29 16:11:16
985	125	155	173	78	1	2008-07-29 18:46:58	2008-07-29 18:46:58
986	125	155	174	79	2	2008-07-29 18:46:58	2008-07-29 18:46:58
987	125	155	172	77	3	2008-07-29 18:46:58	2008-07-29 18:46:58
988	125	155	173	39.5	4	2008-07-29 18:46:58	2008-07-29 18:46:58
989	125	156	111	75	1	2008-07-29 18:46:58	2008-07-29 18:46:58
990	125	156	109	75	2	2008-07-29 18:46:58	2008-07-29 18:46:58
991	125	156	110	76	3	2008-07-29 18:46:58	2008-07-29 18:46:58
992	125	156	111	38	4	2008-07-29 18:46:58	2008-07-29 18:46:58
993	133	193	33	75	1	2008-07-29 18:50:04	2008-07-29 18:50:04
994	133	193	31	76	2	2008-07-29 18:50:04	2008-07-29 18:50:04
995	133	193	32	74	3	2008-07-29 18:50:04	2008-07-29 18:50:04
996	133	193	31	38	4	2008-07-29 18:50:04	2008-07-29 18:50:04
997	133	194	150	77	1	2008-07-29 18:50:04	2008-07-29 18:50:04
998	133	194	149	78	2	2008-07-29 18:50:04	2008-07-29 18:50:04
999	133	194	148	75	3	2008-07-29 18:50:04	2008-07-29 18:50:04
1000	133	194	149	38.5	4	2008-07-29 18:50:04	2008-07-29 18:50:04
1001	139	195	26	73	1	2008-07-29 18:51:17	2008-07-29 18:51:17
1002	139	195	25	75	2	2008-07-29 18:51:17	2008-07-29 18:51:17
1003	139	195	27	74	3	2008-07-29 18:51:17	2008-07-29 18:51:17
1004	139	195	25	37	4	2008-07-29 18:51:17	2008-07-29 18:51:17
1005	139	196	93	76	1	2008-07-29 18:51:17	2008-07-29 18:51:17
1006	139	196	92	75	2	2008-07-29 18:51:17	2008-07-29 18:51:17
1007	139	196	91	74	3	2008-07-29 18:51:17	2008-07-29 18:51:17
1008	139	196	93	38	4	2008-07-29 18:51:17	2008-07-29 18:51:17
1009	163	211	82	74	1	2008-07-29 18:55:43	2008-07-29 18:55:43
1010	164	211	82	75	1	2008-07-29 18:55:43	2008-07-29 18:55:43
1011	165	211	82	74	1	2008-07-29 18:55:43	2008-07-29 18:55:43
1012	163	211	84	73	2	2008-07-29 18:55:43	2008-07-29 18:55:43
1013	164	211	84	74	2	2008-07-29 18:55:43	2008-07-29 18:55:43
1014	165	211	84	73	2	2008-07-29 18:55:43	2008-07-29 18:55:43
1015	163	211	83	72	3	2008-07-29 18:55:43	2008-07-29 18:55:43
1016	164	211	83	72	3	2008-07-29 18:55:43	2008-07-29 18:55:43
1017	165	211	83	73	3	2008-07-29 18:55:43	2008-07-29 18:55:43
1018	163	211	82	37	4	2008-07-29 18:55:43	2008-07-29 18:55:43
1019	164	211	82	37.5	4	2008-07-29 18:55:43	2008-07-29 18:55:43
1020	165	211	82	37	4	2008-07-29 18:55:43	2008-07-29 18:55:43
1021	163	212	94	76	1	2008-07-29 18:55:43	2008-07-29 18:55:43
1022	164	212	94	76	1	2008-07-29 18:55:43	2008-07-29 18:55:43
1023	165	212	94	76	1	2008-07-29 18:55:43	2008-07-29 18:55:43
1024	163	212	95	76	2	2008-07-29 18:55:43	2008-07-29 18:55:43
1025	164	212	95	75	2	2008-07-29 18:55:43	2008-07-29 18:55:43
1026	165	212	95	75	2	2008-07-29 18:55:43	2008-07-29 18:55:43
1027	163	212	96	74	3	2008-07-29 18:55:43	2008-07-29 18:55:43
1028	164	212	96	74	3	2008-07-29 18:55:43	2008-07-29 18:55:43
1029	165	212	96	75	3	2008-07-29 18:55:43	2008-07-29 18:55:43
1030	163	212	94	38	4	2008-07-29 18:55:43	2008-07-29 18:55:43
1031	164	212	94	37.5	4	2008-07-29 18:55:43	2008-07-29 18:55:43
1032	165	212	94	38	4	2008-07-29 18:55:43	2008-07-29 18:55:43
1033	121	149	169	78	1	2008-07-29 18:56:33	2008-07-29 18:56:33
1034	121	149	171	76	2	2008-07-29 18:56:33	2008-07-29 18:56:33
1035	121	149	170	78	3	2008-07-29 18:56:33	2008-07-29 18:56:33
1036	121	149	169	38	4	2008-07-29 18:56:33	2008-07-29 18:56:33
1037	121	150	102	76	1	2008-07-29 18:56:33	2008-07-29 18:56:33
1038	121	150	101	75	2	2008-07-29 18:56:33	2008-07-29 18:56:33
1039	121	150	100	75	3	2008-07-29 18:56:33	2008-07-29 18:56:33
1040	121	150	102	37.5	4	2008-07-29 18:56:33	2008-07-29 18:56:33
1041	151	199	209	75	1	2008-07-29 18:57:29	2008-07-29 18:57:29
1042	152	199	209	75	1	2008-07-29 18:57:29	2008-07-29 18:57:29
1043	153	199	209	73	1	2008-07-29 18:57:29	2008-07-29 18:57:29
1044	151	199	208	72	2	2008-07-29 18:57:29	2008-07-29 18:57:29
1045	152	199	208	74	2	2008-07-29 18:57:29	2008-07-29 18:57:29
1046	153	199	208	72	2	2008-07-29 18:57:29	2008-07-29 18:57:29
1047	151	199	210	72	3	2008-07-29 18:57:29	2008-07-29 18:57:29
1048	152	199	210	74	3	2008-07-29 18:57:29	2008-07-29 18:57:29
1049	153	199	210	73	3	2008-07-29 18:57:29	2008-07-29 18:57:29
1050	151	199	209	37.5	4	2008-07-29 18:57:30	2008-07-29 18:57:30
1051	152	199	209	36	4	2008-07-29 18:57:30	2008-07-29 18:57:30
1052	153	199	209	36	4	2008-07-29 18:57:30	2008-07-29 18:57:30
1053	151	200	126	78	1	2008-07-29 18:57:30	2008-07-29 18:57:30
1054	152	200	126	78	1	2008-07-29 18:57:30	2008-07-29 18:57:30
1055	153	200	126	75	1	2008-07-29 18:57:30	2008-07-29 18:57:30
1056	151	200	124	76	2	2008-07-29 18:57:30	2008-07-29 18:57:30
1057	152	200	124	76	2	2008-07-29 18:57:30	2008-07-29 18:57:30
1058	153	200	124	76	2	2008-07-29 18:57:30	2008-07-29 18:57:30
1059	151	200	125	76	3	2008-07-29 18:57:30	2008-07-29 18:57:30
1060	152	200	125	77	3	2008-07-29 18:57:30	2008-07-29 18:57:30
1061	153	200	125	74	3	2008-07-29 18:57:30	2008-07-29 18:57:30
1062	151	200	126	38	4	2008-07-29 18:57:30	2008-07-29 18:57:30
1063	152	200	126	38	4	2008-07-29 18:57:30	2008-07-29 18:57:30
1064	153	200	126	37	4	2008-07-29 18:57:30	2008-07-29 18:57:30
1065	122	151	180	77	1	2008-07-29 18:57:51	2008-07-29 18:57:51
1066	122	151	178	76	2	2008-07-29 18:57:51	2008-07-29 18:57:51
1067	122	151	179	79	3	2008-07-29 18:57:51	2008-07-29 18:57:51
1068	122	151	178	39	4	2008-07-29 18:57:51	2008-07-29 18:57:51
1069	122	152	211	79	1	2008-07-29 18:57:51	2008-07-29 18:57:51
1070	122	152	212	79	2	2008-07-29 18:57:51	2008-07-29 18:57:51
1071	122	152	213	79	3	2008-07-29 18:57:51	2008-07-29 18:57:51
1072	122	152	211	38.5	4	2008-07-29 18:57:51	2008-07-29 18:57:51
1073	127	159	185	76	1	2008-07-29 18:58:27	2008-07-29 18:58:27
1074	127	159	184	75	2	2008-07-29 18:58:27	2008-07-29 18:58:27
1075	127	159	186	76	3	2008-07-29 18:58:27	2008-07-29 18:58:27
1076	127	159	185	38	4	2008-07-29 18:58:27	2008-07-29 18:58:27
1077	127	160	108	75	1	2008-07-29 18:58:27	2008-07-29 18:58:27
1078	127	160	107	74	2	2008-07-29 18:58:27	2008-07-29 18:58:27
1079	127	160	106	77	3	2008-07-29 18:58:27	2008-07-29 18:58:27
1080	127	160	108	37.5	4	2008-07-29 18:58:27	2008-07-29 18:58:27
1081	141	189	138	75	1	2008-07-29 18:59:56	2008-07-29 18:59:56
1082	141	189	136	74	2	2008-07-29 18:59:56	2008-07-29 18:59:56
1083	141	189	137	73	3	2008-07-29 18:59:56	2008-07-29 18:59:56
1084	141	189	138	36	4	2008-07-29 18:59:56	2008-07-29 18:59:56
1085	141	190	161	76	1	2008-07-29 18:59:56	2008-07-29 18:59:56
1086	141	190	160	76	2	2008-07-29 18:59:56	2008-07-29 18:59:56
1087	141	190	162	75	3	2008-07-29 18:59:56	2008-07-29 18:59:56
1088	141	190	161	37	4	2008-07-29 18:59:56	2008-07-29 18:59:56
1089	123	153	8	77	1	2008-07-29 19:00:04	2008-07-29 19:00:04
1090	123	153	9	78	2	2008-07-29 19:00:04	2008-07-29 19:00:04
1091	123	153	7	79	3	2008-07-29 19:00:04	2008-07-29 19:00:04
1092	123	153	9	39	4	2008-07-29 19:00:04	2008-07-29 19:00:04
1093	123	154	201	77	1	2008-07-29 19:00:04	2008-07-29 19:00:04
1094	123	154	200	76	2	2008-07-29 19:00:04	2008-07-29 19:00:04
1095	123	154	199	77	3	2008-07-29 19:00:04	2008-07-29 19:00:04
1096	123	154	201	39	4	2008-07-29 19:00:04	2008-07-29 19:00:04
1097	138	191	64	75	1	2008-07-29 19:01:16	2008-07-29 19:01:16
1098	138	191	65	76	2	2008-07-29 19:01:17	2008-07-29 19:01:17
1099	138	191	66	77	3	2008-07-29 19:01:17	2008-07-29 19:01:17
1100	138	191	64	37.5	4	2008-07-29 19:01:17	2008-07-29 19:01:17
1101	138	192	80	74	1	2008-07-29 19:01:17	2008-07-29 19:01:17
1102	138	192	81	78	2	2008-07-29 19:01:17	2008-07-29 19:01:17
1103	138	192	79	76	3	2008-07-29 19:01:17	2008-07-29 19:01:17
1104	138	192	80	38.5	4	2008-07-29 19:01:17	2008-07-29 19:01:17
1105	144	185	191	73	1	2008-07-29 19:03:07	2008-07-29 19:03:07
1106	145	185	191	74	1	2008-07-29 19:03:07	2008-07-29 19:03:07
1107	146	185	191	78	1	2008-07-29 19:03:07	2008-07-29 19:03:07
1108	144	185	192	74	2	2008-07-29 19:03:07	2008-07-29 19:03:07
1109	145	185	192	75	2	2008-07-29 19:03:07	2008-07-29 19:03:07
1110	146	185	192	77	2	2008-07-29 19:03:07	2008-07-29 19:03:07
1111	144	185	190	73	3	2008-07-29 19:03:07	2008-07-29 19:03:07
1112	145	185	190	75	3	2008-07-29 19:03:07	2008-07-29 19:03:07
1113	146	185	190	76	3	2008-07-29 19:03:07	2008-07-29 19:03:07
1114	144	185	191	37	4	2008-07-29 19:03:07	2008-07-29 19:03:07
1115	145	185	191	37.5	4	2008-07-29 19:03:07	2008-07-29 19:03:07
1116	146	185	191	37.5	4	2008-07-29 19:03:07	2008-07-29 19:03:07
1117	144	186	76	76	1	2008-07-29 19:03:07	2008-07-29 19:03:07
1118	145	186	76	75	1	2008-07-29 19:03:07	2008-07-29 19:03:07
1119	146	186	76	77	1	2008-07-29 19:03:07	2008-07-29 19:03:07
1120	144	186	77	76	2	2008-07-29 19:03:07	2008-07-29 19:03:07
1121	145	186	77	76	2	2008-07-29 19:03:07	2008-07-29 19:03:07
1122	146	186	77	77	2	2008-07-29 19:03:07	2008-07-29 19:03:07
1123	144	186	78	74	3	2008-07-29 19:03:07	2008-07-29 19:03:07
1124	145	186	78	75	3	2008-07-29 19:03:07	2008-07-29 19:03:07
1125	146	186	78	75	3	2008-07-29 19:03:07	2008-07-29 19:03:07
1126	144	186	76	38	4	2008-07-29 19:03:07	2008-07-29 19:03:07
1127	145	186	76	38	4	2008-07-29 19:03:07	2008-07-29 19:03:07
1128	146	186	76	37	4	2008-07-29 19:03:07	2008-07-29 19:03:07
1129	126	161	89	77	1	2008-07-29 19:03:38	2008-07-29 19:03:38
1130	126	161	88	79	2	2008-07-29 19:03:38	2008-07-29 19:03:38
1131	126	161	90	77	3	2008-07-29 19:03:38	2008-07-29 19:03:38
1132	126	161	89	38	4	2008-07-29 19:03:38	2008-07-29 19:03:38
1133	126	162	175	76	1	2008-07-29 19:03:38	2008-07-29 19:03:38
1134	126	162	177	76	2	2008-07-29 19:03:38	2008-07-29 19:03:38
1135	126	162	176	76	3	2008-07-29 19:03:38	2008-07-29 19:03:38
1136	126	162	175	38	4	2008-07-29 19:03:38	2008-07-29 19:03:38
1137	181	221	24	76	1	2008-07-29 19:04:31	2008-07-29 19:04:31
1138	181	221	22	76	2	2008-07-29 19:04:31	2008-07-29 19:04:31
1139	181	221	23	77	3	2008-07-29 19:04:31	2008-07-29 19:04:31
1140	181	221	24	37	4	2008-07-29 19:04:31	2008-07-29 19:04:31
1141	181	222	86	75	1	2008-07-29 19:04:31	2008-07-29 19:04:31
1142	181	222	85	74	2	2008-07-29 19:04:31	2008-07-29 19:04:31
1143	181	222	87	73	3	2008-07-29 19:04:31	2008-07-29 19:04:31
1144	181	222	86	38	4	2008-07-29 19:04:31	2008-07-29 19:04:31
1145	135	171	73	76	1	2008-07-29 19:04:49	2008-07-29 19:04:49
1146	135	171	74	74	2	2008-07-29 19:04:49	2008-07-29 19:04:49
1147	135	171	75	76	3	2008-07-29 19:04:49	2008-07-29 19:04:49
1148	135	171	73	36.5	4	2008-07-29 19:04:49	2008-07-29 19:04:49
1149	135	172	130	77	1	2008-07-29 19:04:49	2008-07-29 19:04:49
1150	135	172	131	76	2	2008-07-29 19:04:49	2008-07-29 19:04:49
1151	135	172	132	75	3	2008-07-29 19:04:49	2008-07-29 19:04:49
1152	135	172	130	36.5	4	2008-07-29 19:04:49	2008-07-29 19:04:49
1153	129	165	105	77	1	2008-07-29 19:04:53	2008-07-29 19:04:53
1154	129	165	104	77	2	2008-07-29 19:04:53	2008-07-29 19:04:53
1155	129	165	103	76	3	2008-07-29 19:04:53	2008-07-29 19:04:53
1156	129	165	105	38	4	2008-07-29 19:04:53	2008-07-29 19:04:53
1157	129	166	158	77	1	2008-07-29 19:04:53	2008-07-29 19:04:53
1158	129	166	159	77	2	2008-07-29 19:04:53	2008-07-29 19:04:53
1159	129	166	157	78	3	2008-07-29 19:04:53	2008-07-29 19:04:53
1160	129	166	158	39	4	2008-07-29 19:04:53	2008-07-29 19:04:53
1161	130	167	182	74	1	2008-07-29 19:06:06	2008-07-29 19:06:06
1162	130	167	181	74	2	2008-07-29 19:06:06	2008-07-29 19:06:06
1163	130	167	183	76	3	2008-07-29 19:06:06	2008-07-29 19:06:06
1164	130	167	182	37.5	4	2008-07-29 19:06:06	2008-07-29 19:06:06
1165	130	168	48	74	1	2008-07-29 19:06:06	2008-07-29 19:06:06
1166	130	168	46	76	2	2008-07-29 19:06:06	2008-07-29 19:06:06
1167	130	168	47	73	3	2008-07-29 19:06:06	2008-07-29 19:06:06
1168	130	168	46	36.5	4	2008-07-29 19:06:06	2008-07-29 19:06:06
1169	157	205	28	74	1	2008-07-29 19:06:08	2008-07-29 19:06:08
1170	158	205	28	75	1	2008-07-29 19:06:08	2008-07-29 19:06:08
1171	159	205	28	73	1	2008-07-29 19:06:08	2008-07-29 19:06:08
1172	157	205	29	76	2	2008-07-29 19:06:08	2008-07-29 19:06:08
1173	158	205	29	75	2	2008-07-29 19:06:08	2008-07-29 19:06:08
1174	159	205	29	73	2	2008-07-29 19:06:08	2008-07-29 19:06:08
1175	157	205	30	75	3	2008-07-29 19:06:08	2008-07-29 19:06:08
1176	158	205	30	74	3	2008-07-29 19:06:08	2008-07-29 19:06:08
1177	159	205	30	72	3	2008-07-29 19:06:08	2008-07-29 19:06:08
1178	157	205	28	37	4	2008-07-29 19:06:08	2008-07-29 19:06:08
1179	158	205	28	38	4	2008-07-29 19:06:08	2008-07-29 19:06:08
1180	159	205	28	36	4	2008-07-29 19:06:08	2008-07-29 19:06:08
1181	157	206	163	75	1	2008-07-29 19:06:08	2008-07-29 19:06:08
1182	158	206	163	76	1	2008-07-29 19:06:08	2008-07-29 19:06:08
1183	159	206	163	76	1	2008-07-29 19:06:08	2008-07-29 19:06:08
1184	157	206	164	76	2	2008-07-29 19:06:08	2008-07-29 19:06:08
1185	158	206	164	76	2	2008-07-29 19:06:08	2008-07-29 19:06:08
1186	159	206	164	77	2	2008-07-29 19:06:08	2008-07-29 19:06:08
1187	157	206	165	76	3	2008-07-29 19:06:08	2008-07-29 19:06:08
1188	158	206	165	76	3	2008-07-29 19:06:08	2008-07-29 19:06:08
1189	159	206	165	76	3	2008-07-29 19:06:08	2008-07-29 19:06:08
1190	157	206	163	37	4	2008-07-29 19:06:08	2008-07-29 19:06:08
1191	158	206	163	38	4	2008-07-29 19:06:08	2008-07-29 19:06:08
1192	159	206	163	38	4	2008-07-29 19:06:08	2008-07-29 19:06:08
1193	124	157	142	75	1	2008-07-29 19:06:12	2008-07-29 19:06:12
1194	124	157	144	73	2	2008-07-29 19:06:12	2008-07-29 19:06:12
1195	124	157	143	75	3	2008-07-29 19:06:12	2008-07-29 19:06:12
1196	124	157	144	37	4	2008-07-29 19:06:12	2008-07-29 19:06:12
1197	124	158	99	77	1	2008-07-29 19:06:12	2008-07-29 19:06:12
1198	124	158	97	77	2	2008-07-29 19:06:12	2008-07-29 19:06:12
1199	124	158	98	77	3	2008-07-29 19:06:12	2008-07-29 19:06:12
1200	124	158	97	37.5	4	2008-07-29 19:06:12	2008-07-29 19:06:12
1201	166	207	139	75	1	2008-07-29 19:07:08	2008-07-29 19:07:08
1202	167	207	139	74	1	2008-07-29 19:07:08	2008-07-29 19:07:08
1203	168	207	139	75	1	2008-07-29 19:07:08	2008-07-29 19:07:08
1204	166	207	140	75	2	2008-07-29 19:07:08	2008-07-29 19:07:08
1205	167	207	140	73	2	2008-07-29 19:07:08	2008-07-29 19:07:08
1206	168	207	140	75	2	2008-07-29 19:07:08	2008-07-29 19:07:08
1207	166	207	141	77	3	2008-07-29 19:07:08	2008-07-29 19:07:08
1208	167	207	141	77	3	2008-07-29 19:07:08	2008-07-29 19:07:08
1209	168	207	141	77	3	2008-07-29 19:07:08	2008-07-29 19:07:08
1210	166	207	139	38	4	2008-07-29 19:07:08	2008-07-29 19:07:08
1211	167	207	139	36.5	4	2008-07-29 19:07:08	2008-07-29 19:07:08
1212	168	207	139	37.5	4	2008-07-29 19:07:08	2008-07-29 19:07:08
1213	166	208	4	76	1	2008-07-29 19:07:08	2008-07-29 19:07:08
1214	167	208	4	74	1	2008-07-29 19:07:08	2008-07-29 19:07:08
1215	168	208	4	75	1	2008-07-29 19:07:08	2008-07-29 19:07:08
1216	166	208	5	75	2	2008-07-29 19:07:08	2008-07-29 19:07:08
1217	167	208	5	74	2	2008-07-29 19:07:08	2008-07-29 19:07:08
1218	168	208	5	76	2	2008-07-29 19:07:08	2008-07-29 19:07:08
1219	166	208	6	75	3	2008-07-29 19:07:08	2008-07-29 19:07:08
1220	167	208	6	73	3	2008-07-29 19:07:08	2008-07-29 19:07:08
1221	168	208	6	74	3	2008-07-29 19:07:08	2008-07-29 19:07:08
1222	166	208	4	36.5	4	2008-07-29 19:07:08	2008-07-29 19:07:08
1223	167	208	4	35	4	2008-07-29 19:07:08	2008-07-29 19:07:08
1224	168	208	4	34	4	2008-07-29 19:07:08	2008-07-29 19:07:08
1225	147	201	220	74	1	2008-07-29 19:07:09	2008-07-29 19:07:09
1226	147	201	222	77	2	2008-07-29 19:07:09	2008-07-29 19:07:09
1227	147	201	221	73	3	2008-07-29 19:07:09	2008-07-29 19:07:09
1228	147	201	222	38	4	2008-07-29 19:07:09	2008-07-29 19:07:09
1229	147	202	18	76	1	2008-07-29 19:07:09	2008-07-29 19:07:09
1230	147	202	16	76	2	2008-07-29 19:07:09	2008-07-29 19:07:09
1231	147	202	17	76	3	2008-07-29 19:07:09	2008-07-29 19:07:09
1232	147	202	18	38	4	2008-07-29 19:07:09	2008-07-29 19:07:09
1233	128	163	129	76	1	2008-07-29 19:07:44	2008-07-29 19:07:44
1234	128	163	128	76	2	2008-07-29 19:07:44	2008-07-29 19:07:44
1235	128	163	127	76	3	2008-07-29 19:07:44	2008-07-29 19:07:44
1236	128	163	129	37	4	2008-07-29 19:07:44	2008-07-29 19:07:44
1237	128	164	70	78	1	2008-07-29 19:07:44	2008-07-29 19:07:44
1238	128	164	71	76	2	2008-07-29 19:07:44	2008-07-29 19:07:44
1239	128	164	72	75	3	2008-07-29 19:07:44	2008-07-29 19:07:44
1240	128	164	70	38	4	2008-07-29 19:07:44	2008-07-29 19:07:44
1241	154	203	187	74	1	2008-07-29 19:09:11	2008-07-29 19:09:11
1242	155	203	187	74	1	2008-07-29 19:09:11	2008-07-29 19:09:11
1243	156	203	187	73	1	2008-07-29 19:09:11	2008-07-29 19:09:11
1244	154	203	188	76	2	2008-07-29 19:09:11	2008-07-29 19:09:11
1245	155	203	188	75	2	2008-07-29 19:09:11	2008-07-29 19:09:11
1246	156	203	188	73	2	2008-07-29 19:09:11	2008-07-29 19:09:11
1247	154	203	189	75	3	2008-07-29 19:09:11	2008-07-29 19:09:11
1248	155	203	189	77	3	2008-07-29 19:09:11	2008-07-29 19:09:11
1249	156	203	189	73	3	2008-07-29 19:09:11	2008-07-29 19:09:11
1250	154	203	187	37	4	2008-07-29 19:09:11	2008-07-29 19:09:11
1251	155	203	187	37.5	4	2008-07-29 19:09:11	2008-07-29 19:09:11
1252	156	203	187	36	4	2008-07-29 19:09:11	2008-07-29 19:09:11
1253	154	204	35	71	1	2008-07-29 19:09:11	2008-07-29 19:09:11
1254	155	204	35	71	1	2008-07-29 19:09:11	2008-07-29 19:09:11
1255	156	204	35	73	1	2008-07-29 19:09:11	2008-07-29 19:09:11
1256	154	204	36	75	2	2008-07-29 19:09:11	2008-07-29 19:09:11
1257	155	204	36	74	2	2008-07-29 19:09:11	2008-07-29 19:09:11
1258	156	204	36	73	2	2008-07-29 19:09:11	2008-07-29 19:09:11
1259	154	204	34	73	3	2008-07-29 19:09:11	2008-07-29 19:09:11
1260	155	204	34	73	3	2008-07-29 19:09:11	2008-07-29 19:09:11
1261	156	204	34	73	3	2008-07-29 19:09:11	2008-07-29 19:09:11
1262	154	204	35	36	4	2008-07-29 19:09:11	2008-07-29 19:09:11
1263	155	204	35	36.5	4	2008-07-29 19:09:11	2008-07-29 19:09:11
1264	156	204	35	37	4	2008-07-29 19:09:11	2008-07-29 19:09:11
1265	137	187	217	76	1	2008-07-29 19:14:12	2008-07-29 19:14:12
1266	137	187	218	75	2	2008-07-29 19:14:12	2008-07-29 19:14:12
1267	137	187	219	76	3	2008-07-29 19:14:12	2008-07-29 19:14:12
1268	137	187	217	37.5	4	2008-07-29 19:14:12	2008-07-29 19:14:12
1269	137	188	58	77	1	2008-07-29 19:14:12	2008-07-29 19:14:12
1270	137	188	60	76	2	2008-07-29 19:14:12	2008-07-29 19:14:12
1271	137	188	59	75	3	2008-07-29 19:14:13	2008-07-29 19:14:13
1272	137	188	58	37.5	4	2008-07-29 19:14:13	2008-07-29 19:14:13
1273	172	215	42	70	1	2008-07-29 19:27:05	2008-07-29 19:27:05
1274	173	215	42	70	1	2008-07-29 19:27:05	2008-07-29 19:27:05
1275	174	215	42	73	1	2008-07-29 19:27:06	2008-07-29 19:27:06
1276	172	215	40	72	2	2008-07-29 19:27:06	2008-07-29 19:27:06
1277	173	215	40	70	2	2008-07-29 19:27:06	2008-07-29 19:27:06
1278	174	215	40	74	2	2008-07-29 19:27:06	2008-07-29 19:27:06
1279	172	215	41	72	3	2008-07-29 19:27:06	2008-07-29 19:27:06
1280	173	215	41	69	3	2008-07-29 19:27:06	2008-07-29 19:27:06
1281	174	215	41	73	3	2008-07-29 19:27:06	2008-07-29 19:27:06
1282	172	215	42	35	4	2008-07-29 19:27:06	2008-07-29 19:27:06
1283	173	215	42	35.5	4	2008-07-29 19:27:06	2008-07-29 19:27:06
1284	174	215	42	37	4	2008-07-29 19:27:06	2008-07-29 19:27:06
1285	172	216	57	77	1	2008-07-29 19:27:06	2008-07-29 19:27:06
1286	173	216	57	74	1	2008-07-29 19:27:06	2008-07-29 19:27:06
1287	174	216	57	76	1	2008-07-29 19:27:06	2008-07-29 19:27:06
1288	172	216	56	76	2	2008-07-29 19:27:06	2008-07-29 19:27:06
1289	173	216	56	72	2	2008-07-29 19:27:06	2008-07-29 19:27:06
1290	174	216	56	75	2	2008-07-29 19:27:06	2008-07-29 19:27:06
1291	172	216	55	74	3	2008-07-29 19:27:06	2008-07-29 19:27:06
1292	173	216	55	73	3	2008-07-29 19:27:06	2008-07-29 19:27:06
1293	174	216	55	74	3	2008-07-29 19:27:06	2008-07-29 19:27:06
1294	172	216	57	38	4	2008-07-29 19:27:06	2008-07-29 19:27:06
1295	173	216	57	36.5	4	2008-07-29 19:27:06	2008-07-29 19:27:06
1296	174	216	57	37	4	2008-07-29 19:27:06	2008-07-29 19:27:06
1297	175	217	2	73	1	2008-07-29 19:27:51	2008-07-29 19:27:51
1298	176	217	2	74	1	2008-07-29 19:27:51	2008-07-29 19:27:51
1299	177	217	2	74	1	2008-07-29 19:27:51	2008-07-29 19:27:51
1300	175	217	3	71	2	2008-07-29 19:27:51	2008-07-29 19:27:51
1301	176	217	3	73	2	2008-07-29 19:27:51	2008-07-29 19:27:51
1302	177	217	3	74	2	2008-07-29 19:27:51	2008-07-29 19:27:51
1303	175	217	1	72	3	2008-07-29 19:27:51	2008-07-29 19:27:51
1304	176	217	1	74	3	2008-07-29 19:27:51	2008-07-29 19:27:51
1305	177	217	1	75	3	2008-07-29 19:27:51	2008-07-29 19:27:51
1306	175	217	2	35	4	2008-07-29 19:27:51	2008-07-29 19:27:51
1307	176	217	2	37.5	4	2008-07-29 19:27:51	2008-07-29 19:27:51
1308	177	217	2	36.5	4	2008-07-29 19:27:51	2008-07-29 19:27:51
1309	175	218	39	71	1	2008-07-29 19:27:51	2008-07-29 19:27:51
1310	176	218	39	73	1	2008-07-29 19:27:51	2008-07-29 19:27:51
1311	177	218	39	73	1	2008-07-29 19:27:51	2008-07-29 19:27:51
1312	175	218	37	70	2	2008-07-29 19:27:51	2008-07-29 19:27:51
1313	176	218	37	73	2	2008-07-29 19:27:51	2008-07-29 19:27:51
1314	177	218	37	74	2	2008-07-29 19:27:51	2008-07-29 19:27:51
1315	175	218	38	69	3	2008-07-29 19:27:51	2008-07-29 19:27:51
1316	176	218	38	73	3	2008-07-29 19:27:51	2008-07-29 19:27:51
1317	177	218	38	73	3	2008-07-29 19:27:51	2008-07-29 19:27:51
1318	175	218	39	35	4	2008-07-29 19:27:51	2008-07-29 19:27:51
1319	176	218	39	37	4	2008-07-29 19:27:51	2008-07-29 19:27:51
1320	177	218	39	36	4	2008-07-29 19:27:51	2008-07-29 19:27:51
1321	169	213	166	75	1	2008-07-29 19:28:00	2008-07-29 19:28:00
1322	170	213	166	75	1	2008-07-29 19:28:00	2008-07-29 19:28:00
1323	171	213	166	72	1	2008-07-29 19:28:00	2008-07-29 19:28:00
1324	169	213	167	75	2	2008-07-29 19:28:00	2008-07-29 19:28:00
1325	170	213	167	74	2	2008-07-29 19:28:00	2008-07-29 19:28:00
1326	171	213	167	72	2	2008-07-29 19:28:00	2008-07-29 19:28:00
1327	169	213	168	76	3	2008-07-29 19:28:00	2008-07-29 19:28:00
1328	170	213	168	75	3	2008-07-29 19:28:00	2008-07-29 19:28:00
1329	171	213	168	73	3	2008-07-29 19:28:00	2008-07-29 19:28:00
1330	169	213	166	36	4	2008-07-29 19:28:00	2008-07-29 19:28:00
1331	170	213	166	37.5	4	2008-07-29 19:28:00	2008-07-29 19:28:00
1332	171	213	166	38	4	2008-07-29 19:28:00	2008-07-29 19:28:00
1333	169	214	52	77	1	2008-07-29 19:28:00	2008-07-29 19:28:00
1334	170	214	52	76	1	2008-07-29 19:28:00	2008-07-29 19:28:00
1335	171	214	52	74	1	2008-07-29 19:28:00	2008-07-29 19:28:00
1336	169	214	53	77	2	2008-07-29 19:28:00	2008-07-29 19:28:00
1337	170	214	53	75	2	2008-07-29 19:28:00	2008-07-29 19:28:00
1338	171	214	53	75	2	2008-07-29 19:28:00	2008-07-29 19:28:00
1339	169	214	54	76	3	2008-07-29 19:28:00	2008-07-29 19:28:00
1340	170	214	54	75	3	2008-07-29 19:28:00	2008-07-29 19:28:00
1341	171	214	54	75	3	2008-07-29 19:28:00	2008-07-29 19:28:00
1342	169	214	52	38	4	2008-07-29 19:28:00	2008-07-29 19:28:00
1343	170	214	52	37.5	4	2008-07-29 19:28:00	2008-07-29 19:28:00
1344	171	214	52	37.5	4	2008-07-29 19:28:00	2008-07-29 19:28:00
1345	136	181	215	75	1	2008-07-29 19:29:08	2008-07-29 19:29:08
1346	136	181	214	77	2	2008-07-29 19:29:08	2008-07-29 19:29:08
1347	136	181	216	76	3	2008-07-29 19:29:08	2008-07-29 19:29:08
1348	136	181	215	38	4	2008-07-29 19:29:08	2008-07-29 19:29:08
1349	136	182	147	74	1	2008-07-29 19:29:08	2008-07-29 19:29:08
1350	136	182	146	75	2	2008-07-29 19:29:08	2008-07-29 19:29:08
1351	136	182	145	74	3	2008-07-29 19:29:08	2008-07-29 19:29:08
1352	136	182	146	37	4	2008-07-29 19:29:08	2008-07-29 19:29:08
1353	143	175	67	73	1	2008-07-29 19:29:45	2008-07-29 19:29:45
1354	143	175	69	74	2	2008-07-29 19:29:45	2008-07-29 19:29:45
1355	143	175	68	74	3	2008-07-29 19:29:45	2008-07-29 19:29:45
1356	143	175	69	37	4	2008-07-29 19:29:45	2008-07-29 19:29:45
1357	143	176	196	74	1	2008-07-29 19:29:45	2008-07-29 19:29:45
1358	143	176	197	74	2	2008-07-29 19:29:45	2008-07-29 19:29:45
1359	143	176	198	74	3	2008-07-29 19:29:45	2008-07-29 19:29:45
1360	143	176	197	37	4	2008-07-29 19:29:45	2008-07-29 19:29:45
1385	178	219	193	74	1	2008-07-29 19:30:37	2008-07-29 19:30:37
1386	179	219	193	74	1	2008-07-29 19:30:37	2008-07-29 19:30:37
1387	180	219	193	74	1	2008-07-29 19:30:37	2008-07-29 19:30:37
1388	178	219	195	75	2	2008-07-29 19:30:37	2008-07-29 19:30:37
1389	179	219	195	74	2	2008-07-29 19:30:37	2008-07-29 19:30:37
1390	180	219	195	73	2	2008-07-29 19:30:37	2008-07-29 19:30:37
1391	178	219	194	73	3	2008-07-29 19:30:37	2008-07-29 19:30:37
1392	179	219	194	75	3	2008-07-29 19:30:37	2008-07-29 19:30:37
1393	180	219	194	75	3	2008-07-29 19:30:37	2008-07-29 19:30:37
1394	178	219	193	37.5	4	2008-07-29 19:30:37	2008-07-29 19:30:37
1395	179	219	193	35	4	2008-07-29 19:30:37	2008-07-29 19:30:37
1396	180	219	193	36.5	4	2008-07-29 19:30:37	2008-07-29 19:30:37
1397	178	220	63	78	1	2008-07-29 19:30:37	2008-07-29 19:30:37
1398	179	220	63	73	1	2008-07-29 19:30:37	2008-07-29 19:30:37
1399	180	220	63	75	1	2008-07-29 19:30:37	2008-07-29 19:30:37
1400	178	220	61	76	2	2008-07-29 19:30:37	2008-07-29 19:30:37
1401	179	220	61	74	2	2008-07-29 19:30:37	2008-07-29 19:30:37
1402	180	220	61	77	2	2008-07-29 19:30:37	2008-07-29 19:30:37
1403	178	220	62	76	3	2008-07-29 19:30:37	2008-07-29 19:30:37
1404	179	220	62	74	3	2008-07-29 19:30:37	2008-07-29 19:30:37
1405	180	220	62	75	3	2008-07-29 19:30:37	2008-07-29 19:30:37
1406	178	220	61	38.5	4	2008-07-29 19:30:37	2008-07-29 19:30:37
1407	179	220	61	35	4	2008-07-29 19:30:37	2008-07-29 19:30:37
1408	180	220	61	37.5	4	2008-07-29 19:30:37	2008-07-29 19:30:37
1409	134	173	44	76	1	2008-07-29 19:31:20	2008-07-29 19:31:20
1410	134	173	45	75	2	2008-07-29 19:31:20	2008-07-29 19:31:20
1411	134	173	43	77	3	2008-07-29 19:31:20	2008-07-29 19:31:20
1412	134	173	45	38	4	2008-07-29 19:31:20	2008-07-29 19:31:20
1413	134	174	121	76	1	2008-07-29 19:31:20	2008-07-29 19:31:20
1414	134	174	122	73	2	2008-07-29 19:31:20	2008-07-29 19:31:20
1415	134	174	123	77	3	2008-07-29 19:31:20	2008-07-29 19:31:20
1416	134	174	121	37	4	2008-07-29 19:31:20	2008-07-29 19:31:20
1417	148	197	118	76	1	2008-07-29 19:31:22	2008-07-29 19:31:22
1418	149	197	118	76	1	2008-07-29 19:31:22	2008-07-29 19:31:22
1419	150	197	118	78	1	2008-07-29 19:31:22	2008-07-29 19:31:22
1420	148	197	120	76	2	2008-07-29 19:31:22	2008-07-29 19:31:22
1421	149	197	120	76	2	2008-07-29 19:31:22	2008-07-29 19:31:22
1422	150	197	120	77	2	2008-07-29 19:31:22	2008-07-29 19:31:22
1423	148	197	119	77	3	2008-07-29 19:31:22	2008-07-29 19:31:22
1424	149	197	119	76	3	2008-07-29 19:31:22	2008-07-29 19:31:22
1425	150	197	119	77	3	2008-07-29 19:31:22	2008-07-29 19:31:22
1426	148	197	118	37.5	4	2008-07-29 19:31:22	2008-07-29 19:31:22
1427	149	197	118	37.5	4	2008-07-29 19:31:22	2008-07-29 19:31:22
1428	150	197	118	38.5	4	2008-07-29 19:31:22	2008-07-29 19:31:22
1429	148	198	202	74	1	2008-07-29 19:31:22	2008-07-29 19:31:22
1430	149	198	202	75	1	2008-07-29 19:31:22	2008-07-29 19:31:22
1431	150	198	202	76	1	2008-07-29 19:31:22	2008-07-29 19:31:22
1432	148	198	203	74	2	2008-07-29 19:31:22	2008-07-29 19:31:22
1433	149	198	203	74	2	2008-07-29 19:31:22	2008-07-29 19:31:22
1434	150	198	203	76	2	2008-07-29 19:31:22	2008-07-29 19:31:22
1435	148	198	204	74	3	2008-07-29 19:31:22	2008-07-29 19:31:22
1436	149	198	204	76	3	2008-07-29 19:31:22	2008-07-29 19:31:22
1437	150	198	204	76	3	2008-07-29 19:31:22	2008-07-29 19:31:22
1438	148	198	202	36.5	4	2008-07-29 19:31:22	2008-07-29 19:31:22
1439	149	198	202	36.5	4	2008-07-29 19:31:22	2008-07-29 19:31:22
1440	150	198	202	37	4	2008-07-29 19:31:22	2008-07-29 19:31:22
1465	140	179	49	74	1	2008-07-29 19:32:43	2008-07-29 19:32:43
1466	140	179	51	73	2	2008-07-29 19:32:43	2008-07-29 19:32:43
1467	140	179	50	73	3	2008-07-29 19:32:43	2008-07-29 19:32:43
1468	140	179	51	37	4	2008-07-29 19:32:43	2008-07-29 19:32:43
1469	140	180	10	76	1	2008-07-29 19:32:43	2008-07-29 19:32:43
1470	140	180	11	78	2	2008-07-29 19:32:43	2008-07-29 19:32:43
1471	140	180	12	76	3	2008-07-29 19:32:43	2008-07-29 19:32:43
1472	140	180	10	37.5	4	2008-07-29 19:32:43	2008-07-29 19:32:43
1473	132	169	21	75	1	2008-07-29 19:32:54	2008-07-29 19:32:54
1474	132	169	19	77	2	2008-07-29 19:32:54	2008-07-29 19:32:54
1475	132	169	20	76	3	2008-07-29 19:32:54	2008-07-29 19:32:54
1476	132	169	21	38.5	4	2008-07-29 19:32:54	2008-07-29 19:32:54
1477	132	170	117	75	1	2008-07-29 19:32:54	2008-07-29 19:32:54
1478	132	170	115	75	2	2008-07-29 19:32:54	2008-07-29 19:32:54
1479	132	170	116	75	3	2008-07-29 19:32:54	2008-07-29 19:32:54
1480	132	170	115	37.5	4	2008-07-29 19:32:54	2008-07-29 19:32:54
1481	142	183	207	74	1	2008-07-29 19:33:45	2008-07-29 19:33:45
1482	142	183	205	72	2	2008-07-29 19:33:45	2008-07-29 19:33:45
1483	142	183	206	74	3	2008-07-29 19:33:45	2008-07-29 19:33:45
1484	142	183	207	34	4	2008-07-29 19:33:45	2008-07-29 19:33:45
1485	142	184	13	76	1	2008-07-29 19:33:45	2008-07-29 19:33:45
1486	142	184	14	75	2	2008-07-29 19:33:45	2008-07-29 19:33:45
1487	142	184	15	76	3	2008-07-29 19:33:45	2008-07-29 19:33:45
1488	142	184	14	35	4	2008-07-29 19:33:45	2008-07-29 19:33:45
1497	131	177	152	72	1	2008-07-29 19:36:11	2008-07-29 19:36:11
1498	131	177	151	76	2	2008-07-29 19:36:11	2008-07-29 19:36:11
1499	131	177	153	72	3	2008-07-29 19:36:11	2008-07-29 19:36:11
1500	131	177	151	38.5	4	2008-07-29 19:36:11	2008-07-29 19:36:11
1501	131	178	155	75	1	2008-07-29 19:36:11	2008-07-29 19:36:11
1502	131	178	156	73	2	2008-07-29 19:36:11	2008-07-29 19:36:11
1503	131	178	154	76	3	2008-07-29 19:36:11	2008-07-29 19:36:11
1504	131	178	155	36.5	4	2008-07-29 19:36:11	2008-07-29 19:36:11
1505	160	209	133	75	1	2008-07-29 19:39:18	2008-07-29 19:39:18
1506	161	209	133	75	1	2008-07-29 19:39:18	2008-07-29 19:39:18
1507	162	209	133	75	1	2008-07-29 19:39:18	2008-07-29 19:39:18
1508	160	209	134	75	2	2008-07-29 19:39:18	2008-07-29 19:39:18
1509	161	209	134	76	2	2008-07-29 19:39:18	2008-07-29 19:39:18
1510	162	209	134	75	2	2008-07-29 19:39:18	2008-07-29 19:39:18
1511	160	209	135	75	3	2008-07-29 19:39:18	2008-07-29 19:39:18
1512	161	209	135	75	3	2008-07-29 19:39:18	2008-07-29 19:39:18
1513	162	209	135	75	3	2008-07-29 19:39:18	2008-07-29 19:39:18
1514	160	209	134	36.5	4	2008-07-29 19:39:18	2008-07-29 19:39:18
1515	161	209	134	37.5	4	2008-07-29 19:39:18	2008-07-29 19:39:18
1516	162	209	134	37	4	2008-07-29 19:39:18	2008-07-29 19:39:18
1517	160	210	225	74	1	2008-07-29 19:39:18	2008-07-29 19:39:18
1518	161	210	225	76	1	2008-07-29 19:39:18	2008-07-29 19:39:18
1519	162	210	225	74	1	2008-07-29 19:39:18	2008-07-29 19:39:18
1520	160	210	223	73	2	2008-07-29 19:39:18	2008-07-29 19:39:18
1521	161	210	223	78	2	2008-07-29 19:39:18	2008-07-29 19:39:18
1522	162	210	223	73	2	2008-07-29 19:39:18	2008-07-29 19:39:18
1523	160	210	224	74	3	2008-07-29 19:39:18	2008-07-29 19:39:18
1524	161	210	224	76	3	2008-07-29 19:39:19	2008-07-29 19:39:19
1525	162	210	224	74	3	2008-07-29 19:39:19	2008-07-29 19:39:19
1526	160	210	225	37	4	2008-07-29 19:39:19	2008-07-29 19:39:19
1527	161	210	225	37.5	4	2008-07-29 19:39:19	2008-07-29 19:39:19
1528	162	210	225	37	4	2008-07-29 19:39:19	2008-07-29 19:39:19
1529	200	255	106	74	1	2008-07-06 11:35:46	2008-07-06 11:35:46
1530	200	255	107	75	2	2008-07-06 11:35:46	2008-07-06 11:35:46
1531	200	255	108	76	3	2008-07-06 11:35:46	2008-07-06 11:35:46
1532	200	255	106	38	4	2008-07-06 11:35:46	2008-07-06 11:35:46
1533	200	256	58	75	1	2008-07-06 11:35:46	2008-07-06 11:35:46
1534	200	256	60	74	2	2008-07-06 11:35:46	2008-07-06 11:35:46
1535	200	256	59	75	3	2008-07-06 11:35:46	2008-07-06 11:35:46
1536	200	256	58	37	4	2008-07-06 11:35:46	2008-07-06 11:35:46
1537	207	273	138	73	1	2008-07-06 11:36:04	2008-07-06 11:36:04
1538	207	273	136	73	2	2008-07-06 11:36:04	2008-07-06 11:36:04
1539	207	273	137	72	3	2008-07-06 11:36:04	2008-07-06 11:36:04
1540	207	273	138	36.5	4	2008-07-06 11:36:04	2008-07-06 11:36:04
1541	207	274	63	76	1	2008-07-06 11:36:04	2008-07-06 11:36:04
1542	207	274	61	75	2	2008-07-06 11:36:04	2008-07-06 11:36:04
1543	207	274	62	74	3	2008-07-06 11:36:04	2008-07-06 11:36:04
1544	207	274	63	37.5	4	2008-07-06 11:36:04	2008-07-06 11:36:04
1545	189	237	11	76	1	2008-07-06 11:40:01	2008-07-06 11:40:01
1546	189	237	10	74	2	2008-07-06 11:40:01	2008-07-06 11:40:01
1547	189	237	12	75	3	2008-07-06 11:40:01	2008-07-06 11:40:01
1548	189	237	11	39	4	2008-07-06 11:40:01	2008-07-06 11:40:01
1549	189	238	161	76	1	2008-07-06 11:40:01	2008-07-06 11:40:01
1550	189	238	160	75	2	2008-07-06 11:40:01	2008-07-06 11:40:01
1551	189	238	162	76	3	2008-07-06 11:40:01	2008-07-06 11:40:01
1552	189	238	161	37.5	4	2008-07-06 11:40:01	2008-07-06 11:40:01
1553	224	283	133	74	1	2008-07-06 11:41:53	2008-07-06 11:41:53
1554	225	283	133	75	1	2008-07-06 11:41:54	2008-07-06 11:41:54
1555	226	283	133	77	1	2008-07-06 11:41:54	2008-07-06 11:41:54
1556	224	283	134	76	2	2008-07-06 11:41:54	2008-07-06 11:41:54
1557	225	283	134	77	2	2008-07-06 11:41:54	2008-07-06 11:41:54
1558	226	283	134	78	2	2008-07-06 11:41:54	2008-07-06 11:41:54
1559	224	283	135	75	3	2008-07-06 11:41:54	2008-07-06 11:41:54
1560	225	283	135	77	3	2008-07-06 11:41:54	2008-07-06 11:41:54
1561	226	283	135	77	3	2008-07-06 11:41:54	2008-07-06 11:41:54
1562	224	283	133	37	4	2008-07-06 11:41:54	2008-07-06 11:41:54
1563	225	283	133	38	4	2008-07-06 11:41:54	2008-07-06 11:41:54
1564	226	283	133	38.5	4	2008-07-06 11:41:54	2008-07-06 11:41:54
1565	224	284	207	72	1	2008-07-06 11:41:54	2008-07-06 11:41:54
1566	225	284	207	73	1	2008-07-06 11:41:54	2008-07-06 11:41:54
1567	226	284	207	75	1	2008-07-06 11:41:54	2008-07-06 11:41:54
1568	224	284	205	70	2	2008-07-06 11:41:54	2008-07-06 11:41:54
1569	225	284	205	72	2	2008-07-06 11:41:54	2008-07-06 11:41:54
1570	226	284	205	75	2	2008-07-06 11:41:54	2008-07-06 11:41:54
1571	224	284	206	73	3	2008-07-06 11:41:54	2008-07-06 11:41:54
1572	225	284	206	77	3	2008-07-06 11:41:54	2008-07-06 11:41:54
1573	226	284	206	76	3	2008-07-06 11:41:54	2008-07-06 11:41:54
1574	224	284	207	37	4	2008-07-06 11:41:54	2008-07-06 11:41:54
1575	225	284	207	37.5	4	2008-07-06 11:41:54	2008-07-06 11:41:54
1576	226	284	207	37	4	2008-07-06 11:41:54	2008-07-06 11:41:54
1577	233	289	86	71	1	2008-07-06 11:41:55	2008-07-06 11:41:55
1578	234	289	86	72	1	2008-07-06 11:41:55	2008-07-06 11:41:55
1579	235	289	86	70	1	2008-07-06 11:41:55	2008-07-06 11:41:55
1580	233	289	85	72	2	2008-07-06 11:41:55	2008-07-06 11:41:55
1581	234	289	85	72	2	2008-07-06 11:41:55	2008-07-06 11:41:55
1582	235	289	85	71	2	2008-07-06 11:41:55	2008-07-06 11:41:55
1583	233	289	87	70	3	2008-07-06 11:41:55	2008-07-06 11:41:55
1584	234	289	87	72	3	2008-07-06 11:41:55	2008-07-06 11:41:55
1585	235	289	87	71	3	2008-07-06 11:41:55	2008-07-06 11:41:55
1586	233	289	86	35.5	4	2008-07-06 11:41:55	2008-07-06 11:41:55
1587	234	289	86	35	4	2008-07-06 11:41:55	2008-07-06 11:41:55
1588	235	289	86	37	4	2008-07-06 11:41:55	2008-07-06 11:41:55
1589	233	290	29	72	1	2008-07-06 11:41:55	2008-07-06 11:41:55
1590	234	290	29	74	1	2008-07-06 11:41:55	2008-07-06 11:41:55
1591	235	290	29	72	1	2008-07-06 11:41:55	2008-07-06 11:41:55
1592	233	290	28	73	2	2008-07-06 11:41:55	2008-07-06 11:41:55
1593	234	290	28	74	2	2008-07-06 11:41:55	2008-07-06 11:41:55
1594	235	290	28	72	2	2008-07-06 11:41:56	2008-07-06 11:41:56
1595	233	290	30	73	3	2008-07-06 11:41:56	2008-07-06 11:41:56
1596	234	290	30	75	3	2008-07-06 11:41:56	2008-07-06 11:41:56
1597	235	290	30	74	3	2008-07-06 11:41:56	2008-07-06 11:41:56
1598	233	290	29	36.5	4	2008-07-06 11:41:56	2008-07-06 11:41:56
1599	234	290	29	36.5	4	2008-07-06 11:41:56	2008-07-06 11:41:56
1600	235	290	29	37.5	4	2008-07-06 11:41:56	2008-07-06 11:41:56
1601	201	243	142	75	1	2008-07-06 11:42:50	2008-07-06 11:42:50
1602	201	243	144	74	2	2008-07-06 11:42:50	2008-07-06 11:42:50
1603	201	243	143	76	3	2008-07-06 11:42:50	2008-07-06 11:42:50
1604	201	243	144	37.5	4	2008-07-06 11:42:50	2008-07-06 11:42:50
1605	201	244	43	76	1	2008-07-06 11:42:50	2008-07-06 11:42:50
1606	201	244	45	76	2	2008-07-06 11:42:50	2008-07-06 11:42:50
1607	201	244	44	75	3	2008-07-06 11:42:50	2008-07-06 11:42:50
1608	201	244	43	37	4	2008-07-06 11:42:50	2008-07-06 11:42:50
1609	188	239	181	77	1	2008-07-06 11:43:02	2008-07-06 11:43:02
1610	188	239	182	76	2	2008-07-06 11:43:02	2008-07-06 11:43:02
1611	188	239	183	77	3	2008-07-06 11:43:02	2008-07-06 11:43:02
1612	188	239	181	37.5	4	2008-07-06 11:43:02	2008-07-06 11:43:02
1613	188	240	21	76	1	2008-07-06 11:43:02	2008-07-06 11:43:02
1614	188	240	19	77	2	2008-07-06 11:43:02	2008-07-06 11:43:02
1615	188	240	20	76	3	2008-07-06 11:43:02	2008-07-06 11:43:02
1616	188	240	21	36.5	4	2008-07-06 11:43:02	2008-07-06 11:43:02
1625	209	267	191	75	1	2008-07-06 11:44:34	2008-07-06 11:44:34
1626	209	267	192	75	2	2008-07-06 11:44:34	2008-07-06 11:44:34
1627	209	267	190	74	3	2008-07-06 11:44:34	2008-07-06 11:44:34
1628	209	267	191	36	4	2008-07-06 11:44:34	2008-07-06 11:44:34
1629	209	268	151	77	1	2008-07-06 11:44:34	2008-07-06 11:44:34
1630	209	268	152	76	2	2008-07-06 11:44:34	2008-07-06 11:44:34
1631	209	268	153	74	3	2008-07-06 11:44:34	2008-07-06 11:44:34
1632	209	268	151	36	4	2008-07-06 11:44:34	2008-07-06 11:44:34
1633	194	253	215	76	1	2008-07-06 11:44:38	2008-07-06 11:44:38
1634	195	253	215	76	1	2008-07-06 11:44:38	2008-07-06 11:44:38
1635	196	253	215	76	1	2008-07-06 11:44:38	2008-07-06 11:44:38
1636	194	253	214	77	2	2008-07-06 11:44:38	2008-07-06 11:44:38
1637	195	253	214	75	2	2008-07-06 11:44:38	2008-07-06 11:44:38
1638	196	253	214	75	2	2008-07-06 11:44:38	2008-07-06 11:44:38
1639	194	253	216	76	3	2008-07-06 11:44:38	2008-07-06 11:44:38
1640	195	253	216	76	3	2008-07-06 11:44:38	2008-07-06 11:44:38
1641	196	253	216	76	3	2008-07-06 11:44:38	2008-07-06 11:44:38
1642	194	253	215	38	4	2008-07-06 11:44:38	2008-07-06 11:44:38
1643	195	253	215	38	4	2008-07-06 11:44:38	2008-07-06 11:44:38
1644	196	253	215	38.5	4	2008-07-06 11:44:38	2008-07-06 11:44:38
1645	194	254	187	75	1	2008-07-06 11:44:38	2008-07-06 11:44:38
1646	195	254	187	75	1	2008-07-06 11:44:38	2008-07-06 11:44:38
1647	196	254	187	74	1	2008-07-06 11:44:38	2008-07-06 11:44:38
1648	194	254	188	75	2	2008-07-06 11:44:38	2008-07-06 11:44:38
1649	195	254	188	75	2	2008-07-06 11:44:38	2008-07-06 11:44:38
1650	196	254	188	74	2	2008-07-06 11:44:38	2008-07-06 11:44:38
1651	194	254	189	75	3	2008-07-06 11:44:38	2008-07-06 11:44:38
1652	195	254	189	75	3	2008-07-06 11:44:38	2008-07-06 11:44:38
1653	196	254	189	76	3	2008-07-06 11:44:38	2008-07-06 11:44:38
1654	194	254	187	37	4	2008-07-06 11:44:38	2008-07-06 11:44:38
1655	195	254	187	37	4	2008-07-06 11:44:38	2008-07-06 11:44:38
1656	196	254	187	37	4	2008-07-06 11:44:38	2008-07-06 11:44:38
1657	193	235	16	76	1	2008-07-06 11:45:34	2008-07-06 11:45:34
1658	193	235	18	75	2	2008-07-06 11:45:34	2008-07-06 11:45:34
1659	193	235	17	76	3	2008-07-06 11:45:34	2008-07-06 11:45:34
1660	193	235	16	37	4	2008-07-06 11:45:34	2008-07-06 11:45:34
1661	193	236	129	77	1	2008-07-06 11:45:34	2008-07-06 11:45:34
1662	193	236	128	77	2	2008-07-06 11:45:34	2008-07-06 11:45:34
1663	193	236	127	77	3	2008-07-06 11:45:34	2008-07-06 11:45:34
1664	193	236	129	37	4	2008-07-06 11:45:34	2008-07-06 11:45:34
1665	199	247	175	75	1	2008-07-06 11:46:19	2008-07-06 11:46:19
1666	199	247	177	75	2	2008-07-06 11:46:19	2008-07-06 11:46:19
1667	199	247	176	76	3	2008-07-06 11:46:19	2008-07-06 11:46:19
1668	199	247	175	37	4	2008-07-06 11:46:19	2008-07-06 11:46:19
1669	199	248	93	74	1	2008-07-06 11:46:19	2008-07-06 11:46:19
1670	199	248	92	75	2	2008-07-06 11:46:19	2008-07-06 11:46:19
1671	199	248	91	74	3	2008-07-06 11:46:19	2008-07-06 11:46:19
1672	199	248	93	37	4	2008-07-06 11:46:19	2008-07-06 11:46:19
1673	198	249	196	74	1	2008-07-06 11:47:07	2008-07-06 11:47:07
1674	198	249	197	73	2	2008-07-06 11:47:07	2008-07-06 11:47:07
1675	198	249	198	73	3	2008-07-06 11:47:07	2008-07-06 11:47:07
1676	198	249	196	37	4	2008-07-06 11:47:07	2008-07-06 11:47:07
1677	198	250	105	75	1	2008-07-06 11:47:07	2008-07-06 11:47:07
1678	198	250	103	76	2	2008-07-06 11:47:08	2008-07-06 11:47:08
1679	198	250	104	74	3	2008-07-06 11:47:08	2008-07-06 11:47:08
1680	198	250	105	38	4	2008-07-06 11:47:08	2008-07-06 11:47:08
1681	187	233	201	77	1	2008-07-06 11:47:34	2008-07-06 11:47:34
1682	187	233	200	75	2	2008-07-06 11:47:34	2008-07-06 11:47:34
1683	187	233	199	75	3	2008-07-06 11:47:34	2008-07-06 11:47:34
1684	187	233	201	38	4	2008-07-06 11:47:34	2008-07-06 11:47:34
1685	187	234	126	77	1	2008-07-06 11:47:34	2008-07-06 11:47:34
1686	187	234	124	75	2	2008-07-06 11:47:34	2008-07-06 11:47:34
1687	187	234	125	75	3	2008-07-06 11:47:34	2008-07-06 11:47:34
1688	187	234	126	37	4	2008-07-06 11:47:34	2008-07-06 11:47:34
1689	204	259	80	76	1	2008-07-06 11:50:09	2008-07-06 11:50:09
1690	204	259	81	72	2	2008-07-06 11:50:09	2008-07-06 11:50:09
1691	204	259	79	73	3	2008-07-06 11:50:09	2008-07-06 11:50:09
1692	204	259	80	38.5	4	2008-07-06 11:50:09	2008-07-06 11:50:09
1693	204	260	116	74	1	2008-07-06 11:50:09	2008-07-06 11:50:09
1694	204	260	115	73	2	2008-07-06 11:50:09	2008-07-06 11:50:09
1695	204	260	117	77	3	2008-07-06 11:50:09	2008-07-06 11:50:09
1696	204	260	116	37	4	2008-07-06 11:50:09	2008-07-06 11:50:09
1697	239	293	225	73	1	2008-07-06 11:51:22	2008-07-06 11:51:22
1698	240	293	225	76	1	2008-07-06 11:51:22	2008-07-06 11:51:22
1699	241	293	225	75	1	2008-07-06 11:51:22	2008-07-06 11:51:22
1700	239	293	223	72	2	2008-07-06 11:51:22	2008-07-06 11:51:22
1701	240	293	223	76	2	2008-07-06 11:51:22	2008-07-06 11:51:22
1702	241	293	223	74	2	2008-07-06 11:51:22	2008-07-06 11:51:22
1703	239	293	224	74	3	2008-07-06 11:51:22	2008-07-06 11:51:22
1704	240	293	224	77	3	2008-07-06 11:51:22	2008-07-06 11:51:22
1705	241	293	224	76	3	2008-07-06 11:51:22	2008-07-06 11:51:22
1706	239	293	225	36	4	2008-07-06 11:51:22	2008-07-06 11:51:22
1707	240	293	225	36	4	2008-07-06 11:51:22	2008-07-06 11:51:22
1708	241	293	225	37.5	4	2008-07-06 11:51:22	2008-07-06 11:51:22
1709	239	294	39	71	1	2008-07-06 11:51:22	2008-07-06 11:51:22
1710	240	294	39	74	1	2008-07-06 11:51:22	2008-07-06 11:51:22
1711	241	294	39	75	1	2008-07-06 11:51:22	2008-07-06 11:51:22
1712	239	294	37	71	2	2008-07-06 11:51:22	2008-07-06 11:51:22
1713	240	294	37	74	2	2008-07-06 11:51:22	2008-07-06 11:51:22
1714	241	294	37	74	2	2008-07-06 11:51:22	2008-07-06 11:51:22
1715	239	294	38	72	3	2008-07-06 11:51:22	2008-07-06 11:51:22
1716	240	294	38	75	3	2008-07-06 11:51:22	2008-07-06 11:51:22
1717	241	294	38	74	3	2008-07-06 11:51:22	2008-07-06 11:51:22
1718	239	294	39	36.5	4	2008-07-06 11:51:22	2008-07-06 11:51:22
1719	240	294	39	36	4	2008-07-06 11:51:22	2008-07-06 11:51:22
1720	241	294	39	37.5	4	2008-07-06 11:51:22	2008-07-06 11:51:22
1721	236	291	193	74	1	2008-07-06 11:51:25	2008-07-06 11:51:25
1722	237	291	193	75	1	2008-07-06 11:51:25	2008-07-06 11:51:25
1723	238	291	193	74	1	2008-07-06 11:51:25	2008-07-06 11:51:25
1724	236	291	194	75	2	2008-07-06 11:51:25	2008-07-06 11:51:25
1725	237	291	194	75	2	2008-07-06 11:51:25	2008-07-06 11:51:25
1726	238	291	194	77	2	2008-07-06 11:51:25	2008-07-06 11:51:25
1727	236	291	195	76	3	2008-07-06 11:51:25	2008-07-06 11:51:25
1728	237	291	195	76	3	2008-07-06 11:51:25	2008-07-06 11:51:25
1729	238	291	195	76	3	2008-07-06 11:51:25	2008-07-06 11:51:25
1730	236	291	193	37.5	4	2008-07-06 11:51:25	2008-07-06 11:51:25
1731	237	291	193	37.5	4	2008-07-06 11:51:25	2008-07-06 11:51:25
1732	238	291	193	39	4	2008-07-06 11:51:25	2008-07-06 11:51:25
1733	236	292	4	74	1	2008-07-06 11:51:25	2008-07-06 11:51:25
1734	237	292	4	75	1	2008-07-06 11:51:25	2008-07-06 11:51:25
1735	238	292	4	77	1	2008-07-06 11:51:25	2008-07-06 11:51:25
1736	236	292	5	73	2	2008-07-06 11:51:25	2008-07-06 11:51:25
1737	237	292	5	76	2	2008-07-06 11:51:25	2008-07-06 11:51:25
1738	238	292	5	76	2	2008-07-06 11:51:25	2008-07-06 11:51:25
1739	236	292	6	73	3	2008-07-06 11:51:25	2008-07-06 11:51:25
1740	237	292	6	75	3	2008-07-06 11:51:25	2008-07-06 11:51:25
1741	238	292	6	73	3	2008-07-06 11:51:25	2008-07-06 11:51:25
1742	236	292	4	37	4	2008-07-06 11:51:25	2008-07-06 11:51:25
1743	237	292	4	38.5	4	2008-07-06 11:51:25	2008-07-06 11:51:25
1744	238	292	4	37	4	2008-07-06 11:51:25	2008-07-06 11:51:25
1745	202	251	111	75	1	2008-07-06 11:51:26	2008-07-06 11:51:26
1746	202	251	109	78	2	2008-07-06 11:51:27	2008-07-06 11:51:27
1747	202	251	110	77	3	2008-07-06 11:51:27	2008-07-06 11:51:27
1748	202	251	111	37.5	4	2008-07-06 11:51:27	2008-07-06 11:51:27
1749	202	252	130	76	1	2008-07-06 11:51:27	2008-07-06 11:51:27
1750	202	252	131	76	2	2008-07-06 11:51:27	2008-07-06 11:51:27
1751	202	252	132	76	3	2008-07-06 11:51:27	2008-07-06 11:51:27
1752	202	252	130	37.5	4	2008-07-06 11:51:27	2008-07-06 11:51:27
1753	208	279	48	74	1	2008-07-06 11:52:48	2008-07-06 11:52:48
1754	208	279	46	75	2	2008-07-06 11:52:48	2008-07-06 11:52:48
1755	208	279	47	76	3	2008-07-06 11:52:48	2008-07-06 11:52:48
1756	208	279	46	37.5	4	2008-07-06 11:52:48	2008-07-06 11:52:48
1757	208	280	209	74	1	2008-07-06 11:52:48	2008-07-06 11:52:48
1758	208	280	208	75	2	2008-07-06 11:52:48	2008-07-06 11:52:48
1759	208	280	210	73	3	2008-07-06 11:52:48	2008-07-06 11:52:48
1760	208	280	209	37	4	2008-07-06 11:52:48	2008-07-06 11:52:48
1761	211	263	217	74	1	2008-07-06 11:53:09	2008-07-06 11:53:09
1762	211	263	218	75	2	2008-07-06 11:53:09	2008-07-06 11:53:09
1763	211	263	219	75	3	2008-07-06 11:53:09	2008-07-06 11:53:09
1764	211	263	217	35	4	2008-07-06 11:53:09	2008-07-06 11:53:09
1765	211	264	147	75	1	2008-07-06 11:53:09	2008-07-06 11:53:09
1766	211	264	146	74	2	2008-07-06 11:53:09	2008-07-06 11:53:09
1767	211	264	145	74	3	2008-07-06 11:53:09	2008-07-06 11:53:09
1768	211	264	146	35	4	2008-07-06 11:53:09	2008-07-06 11:53:09
1769	197	257	76	72	1	2008-07-06 11:54:02	2008-07-06 11:54:02
1770	197	257	77	72	2	2008-07-06 11:54:02	2008-07-06 11:54:02
1771	197	257	78	70	3	2008-07-06 11:54:02	2008-07-06 11:54:02
1772	197	257	76	38	4	2008-07-06 11:54:02	2008-07-06 11:54:02
1773	197	258	119	74	1	2008-07-06 11:54:02	2008-07-06 11:54:02
1774	197	258	120	73	2	2008-07-06 11:54:02	2008-07-06 11:54:02
1775	197	258	118	75	3	2008-07-06 11:54:02	2008-07-06 11:54:02
1776	197	258	119	38	4	2008-07-06 11:54:02	2008-07-06 11:54:02
1777	190	241	150	76	1	2008-07-06 11:54:07	2008-07-06 11:54:07
1778	191	241	150	75	1	2008-07-06 11:54:08	2008-07-06 11:54:08
1779	192	241	150	77	1	2008-07-06 11:54:08	2008-07-06 11:54:08
1780	190	241	149	76	2	2008-07-06 11:54:08	2008-07-06 11:54:08
1781	191	241	149	76	2	2008-07-06 11:54:08	2008-07-06 11:54:08
1782	192	241	149	76	2	2008-07-06 11:54:08	2008-07-06 11:54:08
1783	190	241	148	75	3	2008-07-06 11:54:08	2008-07-06 11:54:08
1784	191	241	148	75	3	2008-07-06 11:54:08	2008-07-06 11:54:08
1785	192	241	148	75	3	2008-07-06 11:54:08	2008-07-06 11:54:08
1786	190	241	149	37	4	2008-07-06 11:54:08	2008-07-06 11:54:08
1787	191	241	149	37	4	2008-07-06 11:54:08	2008-07-06 11:54:08
1788	192	241	149	38	4	2008-07-06 11:54:08	2008-07-06 11:54:08
1789	190	242	13	75	1	2008-07-06 11:54:08	2008-07-06 11:54:08
1790	191	242	13	77	1	2008-07-06 11:54:08	2008-07-06 11:54:08
1791	192	242	13	76	1	2008-07-06 11:54:08	2008-07-06 11:54:08
1792	190	242	14	75	2	2008-07-06 11:54:08	2008-07-06 11:54:08
1793	191	242	14	75	2	2008-07-06 11:54:08	2008-07-06 11:54:08
1794	192	242	14	76	2	2008-07-06 11:54:08	2008-07-06 11:54:08
1795	190	242	15	76	3	2008-07-06 11:54:08	2008-07-06 11:54:08
1796	191	242	15	75	3	2008-07-06 11:54:08	2008-07-06 11:54:08
1797	192	242	15	75	3	2008-07-06 11:54:08	2008-07-06 11:54:08
1798	190	242	13	37	4	2008-07-06 11:54:08	2008-07-06 11:54:08
1799	191	242	13	38	4	2008-07-06 11:54:08	2008-07-06 11:54:08
1800	192	242	13	38	4	2008-07-06 11:54:08	2008-07-06 11:54:08
1801	203	245	101	74	1	2008-07-06 11:55:33	2008-07-06 11:55:33
1802	203	245	102	77	2	2008-07-06 11:55:33	2008-07-06 11:55:33
1803	203	245	100	75	3	2008-07-06 11:55:33	2008-07-06 11:55:33
1804	203	245	101	38.5	4	2008-07-06 11:55:33	2008-07-06 11:55:33
1805	203	246	155	75	1	2008-07-06 11:55:33	2008-07-06 11:55:33
1806	203	246	156	75	2	2008-07-06 11:55:33	2008-07-06 11:55:33
1807	203	246	154	75	3	2008-07-06 11:55:33	2008-07-06 11:55:33
1808	203	246	155	38	4	2008-07-06 11:55:33	2008-07-06 11:55:33
1809	205	261	73	75	1	2008-07-06 11:56:43	2008-07-06 11:56:43
1810	205	261	74	75	2	2008-07-06 11:56:43	2008-07-06 11:56:43
1811	205	261	75	75	3	2008-07-06 11:56:43	2008-07-06 11:56:43
1812	205	261	73	37.5	4	2008-07-06 11:56:43	2008-07-06 11:56:43
1813	205	262	67	74	1	2008-07-06 11:56:43	2008-07-06 11:56:43
1814	205	262	69	75	2	2008-07-06 11:56:43	2008-07-06 11:56:43
1815	205	262	68	75	3	2008-07-06 11:56:43	2008-07-06 11:56:43
1816	205	262	69	37	4	2008-07-06 11:56:43	2008-07-06 11:56:43
1817	221	281	221	73	1	2008-07-06 11:56:46	2008-07-06 11:56:46
1818	222	281	221	72	1	2008-07-06 11:56:46	2008-07-06 11:56:46
1819	223	281	221	72	1	2008-07-06 11:56:46	2008-07-06 11:56:46
1820	221	281	220	72	2	2008-07-06 11:56:46	2008-07-06 11:56:46
1821	222	281	220	73	2	2008-07-06 11:56:46	2008-07-06 11:56:46
1822	223	281	220	72	2	2008-07-06 11:56:46	2008-07-06 11:56:46
1823	221	281	222	74	3	2008-07-06 11:56:46	2008-07-06 11:56:46
1824	222	281	222	74	3	2008-07-06 11:56:46	2008-07-06 11:56:46
1825	223	281	222	74	3	2008-07-06 11:56:46	2008-07-06 11:56:46
1826	221	281	220	36	4	2008-07-06 11:56:46	2008-07-06 11:56:46
1827	222	281	220	36	4	2008-07-06 11:56:46	2008-07-06 11:56:46
1828	223	281	220	37	4	2008-07-06 11:56:46	2008-07-06 11:56:46
1829	221	282	24	72	1	2008-07-06 11:56:46	2008-07-06 11:56:46
1830	222	282	24	73	1	2008-07-06 11:56:46	2008-07-06 11:56:46
1831	223	282	24	71	1	2008-07-06 11:56:46	2008-07-06 11:56:46
1832	221	282	22	71	2	2008-07-06 11:56:46	2008-07-06 11:56:46
1833	222	282	22	73	2	2008-07-06 11:56:46	2008-07-06 11:56:46
1834	223	282	22	72	2	2008-07-06 11:56:46	2008-07-06 11:56:46
1835	221	282	23	72	3	2008-07-06 11:56:46	2008-07-06 11:56:46
1836	222	282	23	73	3	2008-07-06 11:56:46	2008-07-06 11:56:46
1837	223	282	23	74	3	2008-07-06 11:56:46	2008-07-06 11:56:46
1838	221	282	24	35.5	4	2008-07-06 11:56:46	2008-07-06 11:56:46
1839	222	282	24	36.5	4	2008-07-06 11:56:46	2008-07-06 11:56:46
1840	223	282	24	37	4	2008-07-06 11:56:46	2008-07-06 11:56:46
1841	230	287	57	76	1	2008-07-06 11:57:09	2008-07-06 11:57:09
1842	231	287	57	76	1	2008-07-06 11:57:09	2008-07-06 11:57:09
1843	232	287	57	76	1	2008-07-06 11:57:09	2008-07-06 11:57:09
1844	230	287	56	74	2	2008-07-06 11:57:09	2008-07-06 11:57:09
1845	231	287	56	74	2	2008-07-06 11:57:09	2008-07-06 11:57:09
1846	232	287	56	75	2	2008-07-06 11:57:09	2008-07-06 11:57:09
1847	230	287	55	75	3	2008-07-06 11:57:09	2008-07-06 11:57:09
1848	231	287	55	75	3	2008-07-06 11:57:09	2008-07-06 11:57:09
1849	232	287	55	75	3	2008-07-06 11:57:09	2008-07-06 11:57:09
1850	230	287	57	36	4	2008-07-06 11:57:09	2008-07-06 11:57:09
1851	231	287	57	38	4	2008-07-06 11:57:09	2008-07-06 11:57:09
1852	232	287	57	37	4	2008-07-06 11:57:09	2008-07-06 11:57:09
1853	230	288	166	77	1	2008-07-06 11:57:09	2008-07-06 11:57:09
1854	231	288	166	77	1	2008-07-06 11:57:09	2008-07-06 11:57:09
1855	232	288	166	76	1	2008-07-06 11:57:09	2008-07-06 11:57:09
1856	230	288	167	76	2	2008-07-06 11:57:09	2008-07-06 11:57:09
1857	231	288	167	75	2	2008-07-06 11:57:09	2008-07-06 11:57:09
1858	232	288	167	76	2	2008-07-06 11:57:09	2008-07-06 11:57:09
1859	230	288	168	74	3	2008-07-06 11:57:09	2008-07-06 11:57:09
1860	231	288	168	76	3	2008-07-06 11:57:09	2008-07-06 11:57:09
1861	232	288	168	77	3	2008-07-06 11:57:09	2008-07-06 11:57:09
1862	230	288	166	37	4	2008-07-06 11:57:09	2008-07-06 11:57:09
1863	231	288	166	36	4	2008-07-06 11:57:09	2008-07-06 11:57:09
1864	232	288	166	37.5	4	2008-07-06 11:57:09	2008-07-06 11:57:09
1865	206	265	202	75	1	2008-07-06 11:58:22	2008-07-06 11:58:22
1866	206	265	203	75	2	2008-07-06 11:58:22	2008-07-06 11:58:22
1867	206	265	204	74	3	2008-07-06 11:58:22	2008-07-06 11:58:22
1868	206	265	202	37.5	4	2008-07-06 11:58:22	2008-07-06 11:58:22
1869	206	266	163	75	1	2008-07-06 11:58:22	2008-07-06 11:58:22
1870	206	266	164	75	2	2008-07-06 11:58:22	2008-07-06 11:58:22
1871	206	266	165	75	3	2008-07-06 11:58:22	2008-07-06 11:58:22
1872	206	266	163	37.5	4	2008-07-06 11:58:22	2008-07-06 11:58:22
1873	186	231	89	77	1	2008-07-06 11:58:39	2008-07-06 11:58:39
1874	186	231	88	76	2	2008-07-06 11:58:39	2008-07-06 11:58:39
1875	186	231	90	77	3	2008-07-06 11:58:39	2008-07-06 11:58:39
1876	186	231	89	38.5	4	2008-07-06 11:58:39	2008-07-06 11:58:39
1877	186	232	178	77	1	2008-07-06 11:58:39	2008-07-06 11:58:39
1878	186	232	180	76	2	2008-07-06 11:58:39	2008-07-06 11:58:39
1879	186	232	179	76	3	2008-07-06 11:58:39	2008-07-06 11:58:39
1880	186	232	178	38	4	2008-07-06 11:58:39	2008-07-06 11:58:39
1881	210	277	94	76	1	2008-07-06 11:58:52	2008-07-06 11:58:52
1882	210	277	95	75	2	2008-07-06 11:58:52	2008-07-06 11:58:52
1883	210	277	96	75	3	2008-07-06 11:58:52	2008-07-06 11:58:52
1884	210	277	94	38	4	2008-07-06 11:58:52	2008-07-06 11:58:52
1885	210	278	3	74	1	2008-07-06 11:58:52	2008-07-06 11:58:52
1886	210	278	2	74	2	2008-07-06 11:58:52	2008-07-06 11:58:52
1887	210	278	1	75	3	2008-07-06 11:58:52	2008-07-06 11:58:52
1888	210	278	3	37	4	2008-07-06 11:58:52	2008-07-06 11:58:52
1889	183	225	158	78	1	2008-07-06 12:00:03	2008-07-06 12:00:03
1890	183	225	159	78	2	2008-07-06 12:00:03	2008-07-06 12:00:03
1891	183	225	157	78	3	2008-07-06 12:00:03	2008-07-06 12:00:03
1892	183	225	158	38.5	4	2008-07-06 12:00:03	2008-07-06 12:00:03
1893	183	226	171	78	1	2008-07-06 12:00:03	2008-07-06 12:00:03
1894	183	226	169	79	2	2008-07-06 12:00:03	2008-07-06 12:00:03
1895	183	226	170	79	3	2008-07-06 12:00:03	2008-07-06 12:00:03
1896	183	226	169	38.5	4	2008-07-06 12:00:03	2008-07-06 12:00:03
1897	185	229	70	76	1	2008-07-06 12:00:38	2008-07-06 12:00:38
1898	185	229	71	75	2	2008-07-06 12:00:38	2008-07-06 12:00:38
1899	185	229	72	75	3	2008-07-06 12:00:38	2008-07-06 12:00:38
1900	185	229	70	37.5	4	2008-07-06 12:00:38	2008-07-06 12:00:38
1901	185	230	173	77	1	2008-07-06 12:00:38	2008-07-06 12:00:38
1902	185	230	174	77	2	2008-07-06 12:00:38	2008-07-06 12:00:38
1903	185	230	172	77	3	2008-07-06 12:00:38	2008-07-06 12:00:38
1904	185	230	173	38	4	2008-07-06 12:00:38	2008-07-06 12:00:38
1905	184	227	8	77	1	2008-07-06 12:01:27	2008-07-06 12:01:27
1906	184	227	9	76	2	2008-07-06 12:01:27	2008-07-06 12:01:27
1907	184	227	7	78	3	2008-07-06 12:01:27	2008-07-06 12:01:27
1908	184	227	9	37	4	2008-07-06 12:01:27	2008-07-06 12:01:27
1909	184	228	186	77	1	2008-07-06 12:01:27	2008-07-06 12:01:27
1910	184	228	185	76	2	2008-07-06 12:01:27	2008-07-06 12:01:27
1911	184	228	184	77	3	2008-07-06 12:01:27	2008-07-06 12:01:27
1912	184	228	186	37.5	4	2008-07-06 12:01:27	2008-07-06 12:01:27
1913	227	285	35	72	1	2008-07-06 12:01:37	2008-07-06 12:01:37
1914	228	285	35	71	1	2008-07-06 12:01:37	2008-07-06 12:01:37
1915	229	285	35	73	1	2008-07-06 12:01:37	2008-07-06 12:01:37
1916	227	285	36	74	2	2008-07-06 12:01:37	2008-07-06 12:01:37
1917	228	285	36	72	2	2008-07-06 12:01:37	2008-07-06 12:01:37
1918	229	285	36	74	2	2008-07-06 12:01:37	2008-07-06 12:01:37
1919	227	285	34	73	3	2008-07-06 12:01:37	2008-07-06 12:01:37
1920	228	285	34	72	3	2008-07-06 12:01:37	2008-07-06 12:01:37
1921	229	285	34	74	3	2008-07-06 12:01:37	2008-07-06 12:01:37
1922	227	285	35	36	4	2008-07-06 12:01:37	2008-07-06 12:01:37
1923	228	285	35	36	4	2008-07-06 12:01:37	2008-07-06 12:01:37
1924	229	285	35	34	4	2008-07-06 12:01:37	2008-07-06 12:01:37
1925	227	286	33	74	1	2008-07-06 12:01:37	2008-07-06 12:01:37
1926	228	286	33	73	1	2008-07-06 12:01:37	2008-07-06 12:01:37
1927	229	286	33	73	1	2008-07-06 12:01:37	2008-07-06 12:01:37
1928	227	286	31	74	2	2008-07-06 12:01:37	2008-07-06 12:01:37
1929	228	286	31	76	2	2008-07-06 12:01:37	2008-07-06 12:01:37
1930	229	286	31	73	2	2008-07-06 12:01:38	2008-07-06 12:01:38
1931	227	286	32	75	3	2008-07-06 12:01:38	2008-07-06 12:01:38
1932	228	286	32	75	3	2008-07-06 12:01:38	2008-07-06 12:01:38
1933	229	286	32	76	3	2008-07-06 12:01:38	2008-07-06 12:01:38
1934	227	286	31	37	4	2008-07-06 12:01:38	2008-07-06 12:01:38
1935	228	286	31	37.5	4	2008-07-06 12:01:38	2008-07-06 12:01:38
1936	229	286	31	37	4	2008-07-06 12:01:38	2008-07-06 12:01:38
1937	182	223	99	75	1	2008-07-06 12:03:56	2008-07-06 12:03:56
1938	182	223	97	74	2	2008-07-06 12:03:56	2008-07-06 12:03:56
1939	182	223	98	75	3	2008-07-06 12:03:56	2008-07-06 12:03:56
1940	182	223	99	36	4	2008-07-06 12:03:56	2008-07-06 12:03:56
1941	182	224	211	75	1	2008-07-06 12:03:56	2008-07-06 12:03:56
1942	182	224	212	74	2	2008-07-06 12:03:56	2008-07-06 12:03:56
1943	182	224	213	74	3	2008-07-06 12:03:56	2008-07-06 12:03:56
1944	182	224	211	38	4	2008-07-06 12:03:56	2008-07-06 12:03:56
1945	218	271	25	76	1	2008-07-06 12:04:19	2008-07-06 12:04:19
1946	219	271	25	74	1	2008-07-06 12:04:19	2008-07-06 12:04:19
1947	220	271	25	75	1	2008-07-06 12:04:19	2008-07-06 12:04:19
1948	218	271	26	75	2	2008-07-06 12:04:19	2008-07-06 12:04:19
1949	219	271	26	74	2	2008-07-06 12:04:19	2008-07-06 12:04:19
1950	220	271	26	75	2	2008-07-06 12:04:19	2008-07-06 12:04:19
1951	218	271	27	75	3	2008-07-06 12:04:19	2008-07-06 12:04:19
1952	219	271	27	74	3	2008-07-06 12:04:19	2008-07-06 12:04:19
1953	220	271	27	74	3	2008-07-06 12:04:19	2008-07-06 12:04:19
1954	218	271	25	38	4	2008-07-06 12:04:19	2008-07-06 12:04:19
1955	219	271	25	35	4	2008-07-06 12:04:19	2008-07-06 12:04:19
1956	220	271	25	37.5	4	2008-07-06 12:04:19	2008-07-06 12:04:19
1957	218	272	139	75	1	2008-07-06 12:04:19	2008-07-06 12:04:19
1958	219	272	139	75	1	2008-07-06 12:04:19	2008-07-06 12:04:19
1959	220	272	139	74	1	2008-07-06 12:04:19	2008-07-06 12:04:19
1960	218	272	140	74	2	2008-07-06 12:04:19	2008-07-06 12:04:19
1961	219	272	140	75	2	2008-07-06 12:04:19	2008-07-06 12:04:19
1962	220	272	140	74	2	2008-07-06 12:04:19	2008-07-06 12:04:19
1963	218	272	141	75	3	2008-07-06 12:04:19	2008-07-06 12:04:19
1964	219	272	141	74	3	2008-07-06 12:04:19	2008-07-06 12:04:19
1965	220	272	141	75	3	2008-07-06 12:04:19	2008-07-06 12:04:19
1966	218	272	139	37.5	4	2008-07-06 12:04:19	2008-07-06 12:04:19
1967	219	272	139	37	4	2008-07-06 12:04:19	2008-07-06 12:04:19
1968	220	272	139	37	4	2008-07-06 12:04:19	2008-07-06 12:04:19
1969	212	275	52	76	1	2008-07-06 12:04:51	2008-07-06 12:04:51
1970	213	275	52	75	1	2008-07-06 12:04:51	2008-07-06 12:04:51
1971	214	275	52	75	1	2008-07-06 12:04:51	2008-07-06 12:04:51
1972	212	275	53	74	2	2008-07-06 12:04:51	2008-07-06 12:04:51
1973	213	275	53	75	2	2008-07-06 12:04:51	2008-07-06 12:04:51
1974	214	275	53	75	2	2008-07-06 12:04:51	2008-07-06 12:04:51
1975	212	275	54	76	3	2008-07-06 12:04:51	2008-07-06 12:04:51
1976	213	275	54	75	3	2008-07-06 12:04:51	2008-07-06 12:04:51
1977	214	275	54	74	3	2008-07-06 12:04:51	2008-07-06 12:04:51
1978	212	275	52	37	4	2008-07-06 12:04:51	2008-07-06 12:04:51
1979	213	275	52	37.5	4	2008-07-06 12:04:51	2008-07-06 12:04:51
1980	214	275	52	38	4	2008-07-06 12:04:51	2008-07-06 12:04:51
1981	212	276	64	75	1	2008-07-06 12:04:51	2008-07-06 12:04:51
1982	213	276	64	74	1	2008-07-06 12:04:51	2008-07-06 12:04:51
1983	214	276	64	73	1	2008-07-06 12:04:51	2008-07-06 12:04:51
1984	212	276	65	75	2	2008-07-06 12:04:51	2008-07-06 12:04:51
1985	213	276	65	75	2	2008-07-06 12:04:51	2008-07-06 12:04:51
1986	214	276	65	73	2	2008-07-06 12:04:51	2008-07-06 12:04:51
1987	212	276	66	76	3	2008-07-06 12:04:51	2008-07-06 12:04:51
1988	213	276	66	75	3	2008-07-06 12:04:51	2008-07-06 12:04:51
1989	214	276	66	75	3	2008-07-06 12:04:51	2008-07-06 12:04:51
1990	212	276	64	38	4	2008-07-06 12:04:51	2008-07-06 12:04:51
1991	213	276	64	37	4	2008-07-06 12:04:51	2008-07-06 12:04:51
1992	214	276	64	37.5	4	2008-07-06 12:04:51	2008-07-06 12:04:51
1993	242	295	82	75	1	2008-07-06 12:08:38	2008-07-06 12:08:38
1994	243	295	82	74	1	2008-07-06 12:08:38	2008-07-06 12:08:38
1995	244	295	82	76	1	2008-07-06 12:08:38	2008-07-06 12:08:38
1996	242	295	84	76	2	2008-07-06 12:08:38	2008-07-06 12:08:38
1997	243	295	84	76	2	2008-07-06 12:08:38	2008-07-06 12:08:38
1998	244	295	84	74	2	2008-07-06 12:08:38	2008-07-06 12:08:38
1999	242	295	83	76	3	2008-07-06 12:08:38	2008-07-06 12:08:38
2000	243	295	83	74	3	2008-07-06 12:08:38	2008-07-06 12:08:38
2001	244	295	83	73	3	2008-07-06 12:08:38	2008-07-06 12:08:38
2002	242	295	82	37.5	4	2008-07-06 12:08:38	2008-07-06 12:08:38
2003	243	295	82	38	4	2008-07-06 12:08:38	2008-07-06 12:08:38
2004	244	295	82	38	4	2008-07-06 12:08:38	2008-07-06 12:08:38
2005	242	296	42	75	1	2008-07-06 12:08:38	2008-07-06 12:08:38
2006	243	296	42	73	1	2008-07-06 12:08:38	2008-07-06 12:08:38
2007	244	296	42	73	1	2008-07-06 12:08:38	2008-07-06 12:08:38
2008	242	296	40	74	2	2008-07-06 12:08:38	2008-07-06 12:08:38
2009	243	296	40	76	2	2008-07-06 12:08:38	2008-07-06 12:08:38
2010	244	296	40	76	2	2008-07-06 12:08:38	2008-07-06 12:08:38
2011	242	296	41	74	3	2008-07-06 12:08:38	2008-07-06 12:08:38
2012	243	296	41	74	3	2008-07-06 12:08:38	2008-07-06 12:08:38
2013	244	296	41	73	3	2008-07-06 12:08:38	2008-07-06 12:08:38
2014	242	296	42	37.5	4	2008-07-06 12:08:38	2008-07-06 12:08:38
2015	243	296	42	37.5	4	2008-07-06 12:08:38	2008-07-06 12:08:38
2016	244	296	42	37	4	2008-07-06 12:08:38	2008-07-06 12:08:38
2017	215	269	122	75	1	2008-07-06 12:08:46	2008-07-06 12:08:46
2018	216	269	122	74	1	2008-07-06 12:08:46	2008-07-06 12:08:46
2019	217	269	122	75	1	2008-07-06 12:08:46	2008-07-06 12:08:46
2020	215	269	121	74	2	2008-07-06 12:08:46	2008-07-06 12:08:46
2021	216	269	121	75	2	2008-07-06 12:08:46	2008-07-06 12:08:46
2022	217	269	121	75	2	2008-07-06 12:08:46	2008-07-06 12:08:46
2023	215	269	123	75	3	2008-07-06 12:08:46	2008-07-06 12:08:46
2024	216	269	123	76	3	2008-07-06 12:08:46	2008-07-06 12:08:46
2025	217	269	123	76	3	2008-07-06 12:08:46	2008-07-06 12:08:46
2026	215	269	122	38	4	2008-07-06 12:08:46	2008-07-06 12:08:46
2027	216	269	122	37.5	4	2008-07-06 12:08:46	2008-07-06 12:08:46
2028	217	269	122	37	4	2008-07-06 12:08:46	2008-07-06 12:08:46
2029	215	270	49	73	1	2008-07-06 12:08:46	2008-07-06 12:08:46
2030	216	270	49	73	1	2008-07-06 12:08:46	2008-07-06 12:08:46
2031	217	270	49	73	1	2008-07-06 12:08:46	2008-07-06 12:08:46
2032	215	270	51	73	2	2008-07-06 12:08:46	2008-07-06 12:08:46
2033	216	270	51	74	2	2008-07-06 12:08:46	2008-07-06 12:08:46
2034	217	270	51	75	2	2008-07-06 12:08:46	2008-07-06 12:08:46
2035	215	270	50	74	3	2008-07-06 12:08:46	2008-07-06 12:08:46
2036	216	270	50	75	3	2008-07-06 12:08:46	2008-07-06 12:08:46
2037	217	270	50	74	3	2008-07-06 12:08:46	2008-07-06 12:08:46
2038	215	270	49	36.5	4	2008-07-06 12:08:46	2008-07-06 12:08:46
2039	216	270	49	36.5	4	2008-07-06 12:08:46	2008-07-06 12:08:46
2040	217	270	49	37	4	2008-07-06 12:08:46	2008-07-06 12:08:46
2057	255	311	181	75	1	2008-07-06 15:44:19	2008-07-06 15:44:19
2058	255	311	182	74	2	2008-07-06 15:44:19	2008-07-06 15:44:19
2059	255	311	183	75	3	2008-07-06 15:44:19	2008-07-06 15:44:19
2060	255	311	181	37.5	4	2008-07-06 15:44:19	2008-07-06 15:44:19
2061	255	312	105	74	1	2008-07-06 15:44:19	2008-07-06 15:44:19
2062	255	312	104	74	2	2008-07-06 15:44:19	2008-07-06 15:44:19
2063	255	312	103	74	3	2008-07-06 15:44:19	2008-07-06 15:44:19
2064	255	312	105	36	4	2008-07-06 15:44:19	2008-07-06 15:44:19
2065	250	303	185	76	1	2008-07-06 15:48:33	2008-07-06 15:48:33
2066	250	303	184	75	2	2008-07-06 15:48:33	2008-07-06 15:48:33
2067	250	303	186	77	3	2008-07-06 15:48:33	2008-07-06 15:48:33
2068	250	303	185	38	4	2008-07-06 15:48:33	2008-07-06 15:48:33
2069	250	304	101	76	1	2008-07-06 15:48:33	2008-07-06 15:48:33
2070	250	304	102	77	2	2008-07-06 15:48:33	2008-07-06 15:48:33
2071	250	304	100	76	3	2008-07-06 15:48:33	2008-07-06 15:48:33
2072	250	304	101	38	4	2008-07-06 15:48:33	2008-07-06 15:48:33
2073	252	305	44	73	1	2008-07-06 15:49:44	2008-07-06 15:49:44
2074	252	305	45	74	2	2008-07-06 15:49:44	2008-07-06 15:49:44
2075	252	305	43	75	3	2008-07-06 15:49:44	2008-07-06 15:49:44
2076	252	305	45	37	4	2008-07-06 15:49:44	2008-07-06 15:49:44
2077	252	306	129	76	1	2008-07-06 15:49:44	2008-07-06 15:49:44
2078	252	306	128	75	2	2008-07-06 15:49:44	2008-07-06 15:49:44
2079	252	306	127	77	3	2008-07-06 15:49:44	2008-07-06 15:49:44
2080	252	306	129	38	4	2008-07-06 15:49:44	2008-07-06 15:49:44
2081	245	297	211	78	1	2008-07-06 15:50:55	2008-07-06 15:50:55
2082	437	297	211	78	1	2008-07-06 15:50:55	2008-07-06 15:50:55
2083	438	297	211	77	1	2008-07-06 15:50:55	2008-07-06 15:50:55
2084	245	297	212	78	2	2008-07-06 15:50:55	2008-07-06 15:50:55
2085	437	297	212	76	2	2008-07-06 15:50:55	2008-07-06 15:50:55
2086	438	297	212	75	2	2008-07-06 15:50:55	2008-07-06 15:50:55
2087	245	297	213	78	3	2008-07-06 15:50:55	2008-07-06 15:50:55
2088	437	297	213	75	3	2008-07-06 15:50:55	2008-07-06 15:50:55
2089	438	297	213	76	3	2008-07-06 15:50:55	2008-07-06 15:50:55
2090	245	297	211	38	4	2008-07-06 15:50:55	2008-07-06 15:50:55
2091	437	297	211	37.5	4	2008-07-06 15:50:55	2008-07-06 15:50:55
2092	438	297	211	38	4	2008-07-06 15:50:55	2008-07-06 15:50:55
2093	245	298	171	79	1	2008-07-06 15:50:55	2008-07-06 15:50:55
2094	437	298	171	78	1	2008-07-06 15:50:55	2008-07-06 15:50:55
2095	438	298	171	76	1	2008-07-06 15:50:55	2008-07-06 15:50:55
2096	245	298	169	79	2	2008-07-06 15:50:55	2008-07-06 15:50:55
2097	437	298	169	77	2	2008-07-06 15:50:55	2008-07-06 15:50:55
2098	438	298	169	77	2	2008-07-06 15:50:55	2008-07-06 15:50:55
2099	245	298	170	77	3	2008-07-06 15:50:55	2008-07-06 15:50:55
2100	437	298	170	76	3	2008-07-06 15:50:55	2008-07-06 15:50:55
2101	438	298	170	77	3	2008-07-06 15:50:55	2008-07-06 15:50:55
2102	245	298	169	39	4	2008-07-06 15:50:55	2008-07-06 15:50:55
2103	437	298	169	38.5	4	2008-07-06 15:50:55	2008-07-06 15:50:55
2104	438	298	169	39	4	2008-07-06 15:50:55	2008-07-06 15:50:55
2105	277	349	2	73	1	2008-07-06 15:51:12	2008-07-06 15:51:12
2106	277	349	3	72	2	2008-07-06 15:51:12	2008-07-06 15:51:12
2107	277	349	1	76	3	2008-07-06 15:51:12	2008-07-06 15:51:12
2108	277	349	3	37	4	2008-07-06 15:51:12	2008-07-06 15:51:12
2109	277	350	139	75	1	2008-07-06 15:51:12	2008-07-06 15:51:12
2110	277	350	141	75	2	2008-07-06 15:51:12	2008-07-06 15:51:12
2111	277	350	140	73	3	2008-07-06 15:51:12	2008-07-06 15:51:12
2112	277	350	139	37.5	4	2008-07-06 15:51:12	2008-07-06 15:51:12
2113	276	347	133	74	1	2008-07-06 15:52:42	2008-07-06 15:52:42
2114	276	347	134	75	2	2008-07-06 15:52:42	2008-07-06 15:52:42
2115	276	347	135	76	3	2008-07-06 15:52:42	2008-07-06 15:52:42
2116	276	347	133	37	4	2008-07-06 15:52:42	2008-07-06 15:52:42
2117	276	348	191	76	1	2008-07-06 15:52:42	2008-07-06 15:52:42
2118	276	348	192	76	2	2008-07-06 15:52:42	2008-07-06 15:52:42
2119	276	348	190	77	3	2008-07-06 15:52:42	2008-07-06 15:52:42
2120	276	348	191	37	4	2008-07-06 15:52:42	2008-07-06 15:52:42
2121	269	341	155	76	1	2008-07-06 15:53:16	2008-07-06 15:53:16
2122	270	341	155	77	1	2008-07-06 15:53:16	2008-07-06 15:53:16
2123	271	341	155	76	1	2008-07-06 15:53:16	2008-07-06 15:53:16
2124	269	341	156	75	2	2008-07-06 15:53:16	2008-07-06 15:53:16
2125	270	341	156	77	2	2008-07-06 15:53:16	2008-07-06 15:53:16
2126	271	341	156	76	2	2008-07-06 15:53:16	2008-07-06 15:53:16
2127	269	341	154	77	3	2008-07-06 15:53:16	2008-07-06 15:53:16
2128	270	341	154	77	3	2008-07-06 15:53:16	2008-07-06 15:53:16
2129	271	341	154	76	3	2008-07-06 15:53:16	2008-07-06 15:53:16
2130	269	341	155	37	4	2008-07-06 15:53:16	2008-07-06 15:53:16
2131	270	341	155	37.5	4	2008-07-06 15:53:16	2008-07-06 15:53:16
2132	271	341	155	38	4	2008-07-06 15:53:16	2008-07-06 15:53:16
2133	269	342	52	76	1	2008-07-06 15:53:16	2008-07-06 15:53:16
2134	270	342	52	75	1	2008-07-06 15:53:16	2008-07-06 15:53:16
2135	271	342	52	76	1	2008-07-06 15:53:16	2008-07-06 15:53:16
2136	269	342	53	75	2	2008-07-06 15:53:16	2008-07-06 15:53:16
2137	270	342	53	74	2	2008-07-06 15:53:16	2008-07-06 15:53:16
2138	271	342	53	76	2	2008-07-06 15:53:16	2008-07-06 15:53:16
2139	269	342	54	75	3	2008-07-06 15:53:16	2008-07-06 15:53:16
2140	270	342	54	75	3	2008-07-06 15:53:16	2008-07-06 15:53:16
2141	271	342	54	75	3	2008-07-06 15:53:16	2008-07-06 15:53:16
2142	269	342	52	37.5	4	2008-07-06 15:53:16	2008-07-06 15:53:16
2143	270	342	52	37	4	2008-07-06 15:53:16	2008-07-06 15:53:16
2144	271	342	52	38	4	2008-07-06 15:53:16	2008-07-06 15:53:16
2145	256	319	180	76	1	2008-07-06 15:53:46	2008-07-06 15:53:46
2146	256	319	178	79	2	2008-07-06 15:53:47	2008-07-06 15:53:47
2147	256	319	179	79	3	2008-07-06 15:53:47	2008-07-06 15:53:47
2148	256	319	180	38	4	2008-07-06 15:53:47	2008-07-06 15:53:47
2149	256	320	121	76	1	2008-07-06 15:53:47	2008-07-06 15:53:47
2150	256	320	122	76	2	2008-07-06 15:53:47	2008-07-06 15:53:47
2151	256	320	123	75	3	2008-07-06 15:53:47	2008-07-06 15:53:47
2152	256	320	121	37.5	4	2008-07-06 15:53:47	2008-07-06 15:53:47
2153	275	345	217	74	1	2008-07-06 15:54:53	2008-07-06 15:54:53
2154	275	345	218	75	2	2008-07-06 15:54:53	2008-07-06 15:54:53
2155	275	345	219	76	3	2008-07-06 15:54:53	2008-07-06 15:54:53
2156	275	345	217	37	4	2008-07-06 15:54:53	2008-07-06 15:54:53
2157	275	346	221	72	1	2008-07-06 15:54:53	2008-07-06 15:54:53
2158	275	346	220	72	2	2008-07-06 15:54:53	2008-07-06 15:54:53
2159	275	346	222	74	3	2008-07-06 15:54:53	2008-07-06 15:54:53
2160	275	346	220	36	4	2008-07-06 15:54:53	2008-07-06 15:54:53
2161	299	365	24	73	1	2008-07-06 15:56:53	2008-07-06 15:56:53
2162	300	365	24	72	1	2008-07-06 15:56:53	2008-07-06 15:56:53
2163	301	365	24	75	1	2008-07-06 15:56:53	2008-07-06 15:56:53
2164	299	365	22	74	2	2008-07-06 15:56:53	2008-07-06 15:56:53
2165	300	365	22	74	2	2008-07-06 15:56:53	2008-07-06 15:56:53
2166	301	365	22	74	2	2008-07-06 15:56:53	2008-07-06 15:56:53
2167	299	365	23	74	3	2008-07-06 15:56:53	2008-07-06 15:56:53
2168	300	365	23	72	3	2008-07-06 15:56:53	2008-07-06 15:56:53
2169	301	365	23	75	3	2008-07-06 15:56:53	2008-07-06 15:56:53
2170	299	365	24	37.5	4	2008-07-06 15:56:53	2008-07-06 15:56:53
2171	300	365	24	38	4	2008-07-06 15:56:53	2008-07-06 15:56:53
2172	301	365	24	37.5	4	2008-07-06 15:56:53	2008-07-06 15:56:53
2173	299	366	35	75	1	2008-07-06 15:56:53	2008-07-06 15:56:53
2174	300	366	35	74	1	2008-07-06 15:56:53	2008-07-06 15:56:53
2175	301	366	35	76	1	2008-07-06 15:56:53	2008-07-06 15:56:53
2176	299	366	36	75	2	2008-07-06 15:56:53	2008-07-06 15:56:53
2177	300	366	36	76	2	2008-07-06 15:56:53	2008-07-06 15:56:53
2178	301	366	36	75	2	2008-07-06 15:56:53	2008-07-06 15:56:53
2179	299	366	34	75	3	2008-07-06 15:56:53	2008-07-06 15:56:53
2180	300	366	34	74	3	2008-07-06 15:56:53	2008-07-06 15:56:53
2181	301	366	34	75	3	2008-07-06 15:56:53	2008-07-06 15:56:53
2182	299	366	35	37.5	4	2008-07-06 15:56:53	2008-07-06 15:56:53
2183	300	366	35	36	4	2008-07-06 15:56:53	2008-07-06 15:56:53
2184	301	366	35	37	4	2008-07-06 15:56:53	2008-07-06 15:56:53
2185	257	321	11	77	1	2008-07-06 15:59:14	2008-07-06 15:59:14
2186	257	321	10	77	2	2008-07-06 15:59:14	2008-07-06 15:59:14
2187	257	321	12	77	3	2008-07-06 15:59:14	2008-07-06 15:59:14
2188	257	321	11	38.5	4	2008-07-06 15:59:14	2008-07-06 15:59:14
2189	257	322	187	76	1	2008-07-06 15:59:14	2008-07-06 15:59:14
2190	257	322	188	76	2	2008-07-06 15:59:14	2008-07-06 15:59:14
2191	257	322	189	75	3	2008-07-06 15:59:14	2008-07-06 15:59:14
2192	257	322	187	37.5	4	2008-07-06 15:59:14	2008-07-06 15:59:14
2193	265	335	115	76	1	2008-07-06 15:59:37	2008-07-06 15:59:37
2194	265	335	116	75	2	2008-07-06 15:59:37	2008-07-06 15:59:37
2195	265	335	117	76	3	2008-07-06 15:59:37	2008-07-06 15:59:37
2196	265	335	116	34	4	2008-07-06 15:59:37	2008-07-06 15:59:37
2197	265	336	151	75	1	2008-07-06 15:59:37	2008-07-06 15:59:37
2198	265	336	152	73	2	2008-07-06 15:59:37	2008-07-06 15:59:37
2199	265	336	153	74	3	2008-07-06 15:59:37	2008-07-06 15:59:37
2200	265	336	151	36	4	2008-07-06 15:59:37	2008-07-06 15:59:37
2201	248	315	107	74	1	2008-07-06 16:01:49	2008-07-06 16:01:49
2202	248	315	106	75	2	2008-07-06 16:01:49	2008-07-06 16:01:49
2203	248	315	108	75	3	2008-07-06 16:01:49	2008-07-06 16:01:49
2204	248	315	106	37	4	2008-07-06 16:01:49	2008-07-06 16:01:49
2205	248	316	150	74	1	2008-07-06 16:01:49	2008-07-06 16:01:49
2206	248	316	149	75	2	2008-07-06 16:01:50	2008-07-06 16:01:50
2207	248	316	148	74	3	2008-07-06 16:01:50	2008-07-06 16:01:50
2208	248	316	149	37	4	2008-07-06 16:01:50	2008-07-06 16:01:50
2209	263	333	196	74	1	2008-07-06 16:02:50	2008-07-06 16:02:50
2210	263	333	197	74	2	2008-07-06 16:02:50	2008-07-06 16:02:50
2211	263	333	198	74	3	2008-07-06 16:02:50	2008-07-06 16:02:50
2212	263	333	197	37	4	2008-07-06 16:02:50	2008-07-06 16:02:50
2213	263	334	13	75	1	2008-07-06 16:02:51	2008-07-06 16:02:51
2214	263	334	14	75	2	2008-07-06 16:02:51	2008-07-06 16:02:51
2215	263	334	15	75	3	2008-07-06 16:02:51	2008-07-06 16:02:51
2216	263	334	13	37	4	2008-07-06 16:02:51	2008-07-06 16:02:51
2217	296	363	49	73	1	2008-07-06 16:03:40	2008-07-06 16:03:40
2218	297	363	49	73	1	2008-07-06 16:03:40	2008-07-06 16:03:40
2219	298	363	49	77	1	2008-07-06 16:03:40	2008-07-06 16:03:40
2220	296	363	51	73	2	2008-07-06 16:03:40	2008-07-06 16:03:40
2221	297	363	51	75	2	2008-07-06 16:03:40	2008-07-06 16:03:40
2222	298	363	51	77	2	2008-07-06 16:03:40	2008-07-06 16:03:40
2223	296	363	50	73	3	2008-07-06 16:03:40	2008-07-06 16:03:40
2224	297	363	50	75	3	2008-07-06 16:03:40	2008-07-06 16:03:40
2225	298	363	50	79	3	2008-07-06 16:03:41	2008-07-06 16:03:41
2226	296	363	51	35.5	4	2008-07-06 16:03:41	2008-07-06 16:03:41
2227	297	363	51	37.5	4	2008-07-06 16:03:41	2008-07-06 16:03:41
2228	298	363	51	37.5	4	2008-07-06 16:03:41	2008-07-06 16:03:41
2229	296	364	193	73	1	2008-07-06 16:03:41	2008-07-06 16:03:41
2230	297	364	193	73	1	2008-07-06 16:03:41	2008-07-06 16:03:41
2231	298	364	193	77	1	2008-07-06 16:03:41	2008-07-06 16:03:41
2232	296	364	194	72	2	2008-07-06 16:03:41	2008-07-06 16:03:41
2233	297	364	194	74	2	2008-07-06 16:03:41	2008-07-06 16:03:41
2234	298	364	194	78	2	2008-07-06 16:03:41	2008-07-06 16:03:41
2235	296	364	195	72	3	2008-07-06 16:03:41	2008-07-06 16:03:41
2236	297	364	195	74	3	2008-07-06 16:03:41	2008-07-06 16:03:41
2237	298	364	195	76	3	2008-07-06 16:03:41	2008-07-06 16:03:41
2238	296	364	193	36	4	2008-07-06 16:03:41	2008-07-06 16:03:41
2239	297	364	193	36.5	4	2008-07-06 16:03:41	2008-07-06 16:03:41
2240	298	364	193	38.5	4	2008-07-06 16:03:41	2008-07-06 16:03:41
2241	292	357	202	77	1	2008-07-06 16:05:20	2008-07-06 16:05:20
2242	291	357	202	76	1	2008-07-06 16:05:20	2008-07-06 16:05:20
2243	290	357	202	75	1	2008-07-06 16:05:20	2008-07-06 16:05:20
2244	292	357	203	76	2	2008-07-06 16:05:20	2008-07-06 16:05:20
2245	291	357	203	76	2	2008-07-06 16:05:20	2008-07-06 16:05:20
2246	290	357	203	75	2	2008-07-06 16:05:20	2008-07-06 16:05:20
2247	292	357	204	76	3	2008-07-06 16:05:20	2008-07-06 16:05:20
2248	291	357	204	75	3	2008-07-06 16:05:20	2008-07-06 16:05:20
2249	290	357	204	74	3	2008-07-06 16:05:20	2008-07-06 16:05:20
2250	292	357	202	38.5	4	2008-07-06 16:05:20	2008-07-06 16:05:20
2251	291	357	202	37.5	4	2008-07-06 16:05:20	2008-07-06 16:05:20
2252	290	357	202	37.5	4	2008-07-06 16:05:20	2008-07-06 16:05:20
2253	292	358	207	73	1	2008-07-06 16:05:20	2008-07-06 16:05:20
2254	291	358	207	73	1	2008-07-06 16:05:20	2008-07-06 16:05:20
2255	290	358	207	73	1	2008-07-06 16:05:20	2008-07-06 16:05:20
2256	292	358	205	73	2	2008-07-06 16:05:20	2008-07-06 16:05:20
2257	291	358	205	71	2	2008-07-06 16:05:20	2008-07-06 16:05:20
2258	290	358	205	73	2	2008-07-06 16:05:20	2008-07-06 16:05:20
2259	292	358	206	74	3	2008-07-06 16:05:20	2008-07-06 16:05:20
2260	291	358	206	75	3	2008-07-06 16:05:20	2008-07-06 16:05:20
2261	290	358	206	74	3	2008-07-06 16:05:20	2008-07-06 16:05:20
2262	292	358	207	36.5	4	2008-07-06 16:05:20	2008-07-06 16:05:20
2263	291	358	207	37	4	2008-07-06 16:05:20	2008-07-06 16:05:20
2264	290	358	207	35	4	2008-07-06 16:05:20	2008-07-06 16:05:20
2265	258	325	126	75	1	2008-07-06 16:06:03	2008-07-06 16:06:03
2266	258	325	124	74	2	2008-07-06 16:06:03	2008-07-06 16:06:03
2267	258	325	125	74	3	2008-07-06 16:06:03	2008-07-06 16:06:03
2268	258	325	126	38	4	2008-07-06 16:06:03	2008-07-06 16:06:03
2269	258	326	93	76	1	2008-07-06 16:06:03	2008-07-06 16:06:03
2270	258	326	92	75	2	2008-07-06 16:06:03	2008-07-06 16:06:03
2271	258	326	91	75	3	2008-07-06 16:06:03	2008-07-06 16:06:03
2272	258	326	93	38	4	2008-07-06 16:06:03	2008-07-06 16:06:03
2273	251	317	118	76	1	2008-07-06 16:06:46	2008-07-06 16:06:46
2274	251	317	120	74	2	2008-07-06 16:06:46	2008-07-06 16:06:46
2275	251	317	119	75	3	2008-07-06 16:06:46	2008-07-06 16:06:46
2276	251	317	120	36	4	2008-07-06 16:06:46	2008-07-06 16:06:46
2277	251	318	215	77	1	2008-07-06 16:06:46	2008-07-06 16:06:46
2278	251	318	214	77	2	2008-07-06 16:06:46	2008-07-06 16:06:46
2279	251	318	216	76	3	2008-07-06 16:06:46	2008-07-06 16:06:46
2280	251	318	215	38.5	4	2008-07-06 16:06:46	2008-07-06 16:06:46
2281	266	337	33	73	1	2008-07-06 16:07:09	2008-07-06 16:07:09
2282	268	337	33	75	1	2008-07-06 16:07:09	2008-07-06 16:07:09
2283	267	337	33	74	1	2008-07-06 16:07:09	2008-07-06 16:07:09
2284	266	337	31	73	2	2008-07-06 16:07:09	2008-07-06 16:07:09
2285	268	337	31	77	2	2008-07-06 16:07:10	2008-07-06 16:07:10
2286	267	337	31	76	2	2008-07-06 16:07:10	2008-07-06 16:07:10
2287	266	337	32	74	3	2008-07-06 16:07:10	2008-07-06 16:07:10
2288	268	337	32	76	3	2008-07-06 16:07:10	2008-07-06 16:07:10
2289	267	337	32	75	3	2008-07-06 16:07:10	2008-07-06 16:07:10
2290	266	337	31	37	4	2008-07-06 16:07:10	2008-07-06 16:07:10
2291	268	337	31	38.5	4	2008-07-06 16:07:10	2008-07-06 16:07:10
2292	267	337	31	38.5	4	2008-07-06 16:07:10	2008-07-06 16:07:10
2293	266	338	80	75	1	2008-07-06 16:07:10	2008-07-06 16:07:10
2294	268	338	80	74	1	2008-07-06 16:07:10	2008-07-06 16:07:10
2295	267	338	80	74	1	2008-07-06 16:07:10	2008-07-06 16:07:10
2296	266	338	81	75	2	2008-07-06 16:07:10	2008-07-06 16:07:10
2297	268	338	81	75	2	2008-07-06 16:07:10	2008-07-06 16:07:10
2298	267	338	81	73	2	2008-07-06 16:07:10	2008-07-06 16:07:10
2299	266	338	79	73	3	2008-07-06 16:07:10	2008-07-06 16:07:10
2300	268	338	79	76	3	2008-07-06 16:07:10	2008-07-06 16:07:10
2301	267	338	79	76	3	2008-07-06 16:07:10	2008-07-06 16:07:10
2302	266	338	80	37.5	4	2008-07-06 16:07:10	2008-07-06 16:07:10
2303	268	338	80	37	4	2008-07-06 16:07:10	2008-07-06 16:07:10
2304	267	338	80	37	4	2008-07-06 16:07:10	2008-07-06 16:07:10
2305	264	339	25	74	1	2008-07-06 16:07:46	2008-07-06 16:07:46
2306	264	339	26	75	2	2008-07-06 16:07:46	2008-07-06 16:07:46
2307	264	339	27	74	3	2008-07-06 16:07:46	2008-07-06 16:07:46
2308	264	339	25	37.5	4	2008-07-06 16:07:46	2008-07-06 16:07:46
2309	264	340	144	75	1	2008-07-06 16:07:46	2008-07-06 16:07:46
2310	264	340	142	76	2	2008-07-06 16:07:46	2008-07-06 16:07:46
2311	264	340	143	76	3	2008-07-06 16:07:46	2008-07-06 16:07:46
2312	264	340	144	37.5	4	2008-07-06 16:07:46	2008-07-06 16:07:46
2313	253	307	70	77	1	2008-07-06 16:11:02	2008-07-06 16:11:02
2314	253	307	71	75	2	2008-07-06 16:11:02	2008-07-06 16:11:02
2315	253	307	72	77	3	2008-07-06 16:11:02	2008-07-06 16:11:02
2316	253	307	70	37.5	4	2008-07-06 16:11:02	2008-07-06 16:11:02
2317	253	308	201	76	1	2008-07-06 16:11:02	2008-07-06 16:11:02
2318	253	308	200	75	2	2008-07-06 16:11:02	2008-07-06 16:11:02
2319	253	308	199	76	3	2008-07-06 16:11:02	2008-07-06 16:11:02
2320	253	308	201	37.5	4	2008-07-06 16:11:02	2008-07-06 16:11:02
2321	302	367	39	74	1	2008-07-06 16:11:14	2008-07-06 16:11:14
2322	303	367	39	76	1	2008-07-06 16:11:14	2008-07-06 16:11:14
2323	304	367	39	74	1	2008-07-06 16:11:14	2008-07-06 16:11:14
2324	302	367	37	73	2	2008-07-06 16:11:14	2008-07-06 16:11:14
2325	303	367	37	74	2	2008-07-06 16:11:14	2008-07-06 16:11:14
2326	304	367	37	72	2	2008-07-06 16:11:14	2008-07-06 16:11:14
2327	302	367	38	70	3	2008-07-06 16:11:14	2008-07-06 16:11:14
2328	303	367	38	75	3	2008-07-06 16:11:14	2008-07-06 16:11:14
2329	304	367	38	74	3	2008-07-06 16:11:14	2008-07-06 16:11:14
2330	302	367	39	36.5	4	2008-07-06 16:11:15	2008-07-06 16:11:15
2331	303	367	39	37	4	2008-07-06 16:11:15	2008-07-06 16:11:15
2332	304	367	39	36.5	4	2008-07-06 16:11:15	2008-07-06 16:11:15
2333	302	368	4	73	1	2008-07-06 16:11:15	2008-07-06 16:11:15
2334	303	368	4	76	1	2008-07-06 16:11:15	2008-07-06 16:11:15
2335	304	368	4	75	1	2008-07-06 16:11:15	2008-07-06 16:11:15
2336	302	368	5	74	2	2008-07-06 16:11:15	2008-07-06 16:11:15
2337	303	368	5	76	2	2008-07-06 16:11:15	2008-07-06 16:11:15
2338	304	368	5	76	2	2008-07-06 16:11:15	2008-07-06 16:11:15
2339	302	368	6	74	3	2008-07-06 16:11:15	2008-07-06 16:11:15
2340	303	368	6	76	3	2008-07-06 16:11:15	2008-07-06 16:11:15
2341	304	368	6	76	3	2008-07-06 16:11:15	2008-07-06 16:11:15
2342	302	368	4	37	4	2008-07-06 16:11:15	2008-07-06 16:11:15
2343	303	368	4	38	4	2008-07-06 16:11:15	2008-07-06 16:11:15
2344	304	368	4	37.5	4	2008-07-06 16:11:15	2008-07-06 16:11:15
2345	305	369	42	72	1	2008-07-06 16:11:28	2008-07-06 16:11:28
2346	306	369	42	75	1	2008-07-06 16:11:28	2008-07-06 16:11:28
2347	307	369	42	71	1	2008-07-06 16:11:28	2008-07-06 16:11:28
2348	305	369	40	71	2	2008-07-06 16:11:28	2008-07-06 16:11:28
2349	306	369	40	75	2	2008-07-06 16:11:28	2008-07-06 16:11:28
2350	307	369	40	73	2	2008-07-06 16:11:28	2008-07-06 16:11:28
2351	305	369	41	71	3	2008-07-06 16:11:28	2008-07-06 16:11:28
2352	306	369	41	75	3	2008-07-06 16:11:28	2008-07-06 16:11:28
2353	307	369	41	73	3	2008-07-06 16:11:29	2008-07-06 16:11:29
2354	305	369	40	35.5	4	2008-07-06 16:11:29	2008-07-06 16:11:29
2355	306	369	40	37.5	4	2008-07-06 16:11:29	2008-07-06 16:11:29
2356	307	369	40	36	4	2008-07-06 16:11:29	2008-07-06 16:11:29
2357	305	370	86	72	1	2008-07-06 16:11:29	2008-07-06 16:11:29
2358	306	370	86	75	1	2008-07-06 16:11:29	2008-07-06 16:11:29
2359	307	370	86	72	1	2008-07-06 16:11:29	2008-07-06 16:11:29
2360	305	370	87	72	2	2008-07-06 16:11:29	2008-07-06 16:11:29
2361	306	370	87	74	2	2008-07-06 16:11:29	2008-07-06 16:11:29
2362	307	370	87	73	2	2008-07-06 16:11:29	2008-07-06 16:11:29
2363	305	370	85	71	3	2008-07-06 16:11:29	2008-07-06 16:11:29
2364	306	370	85	75	3	2008-07-06 16:11:29	2008-07-06 16:11:29
2365	307	370	85	73	3	2008-07-06 16:11:29	2008-07-06 16:11:29
2366	305	370	86	36	4	2008-07-06 16:11:29	2008-07-06 16:11:29
2367	306	370	86	37.5	4	2008-07-06 16:11:29	2008-07-06 16:11:29
2368	307	370	86	36	4	2008-07-06 16:11:29	2008-07-06 16:11:29
2369	249	309	175	76	1	2008-07-06 16:13:19	2008-07-06 16:13:19
2370	249	309	177	78	2	2008-07-06 16:13:19	2008-07-06 16:13:19
2371	249	309	176	77	3	2008-07-06 16:13:19	2008-07-06 16:13:19
2372	249	309	175	38	4	2008-07-06 16:13:19	2008-07-06 16:13:19
2373	249	310	99	77	1	2008-07-06 16:13:19	2008-07-06 16:13:19
2374	249	310	97	75	2	2008-07-06 16:13:19	2008-07-06 16:13:19
2375	249	310	98	76	3	2008-07-06 16:13:19	2008-07-06 16:13:19
2376	249	310	99	38	4	2008-07-06 16:13:19	2008-07-06 16:13:19
2377	259	327	63	74	1	2008-07-06 16:13:26	2008-07-06 16:13:26
2378	259	327	61	75	2	2008-07-06 16:13:26	2008-07-06 16:13:26
2379	259	327	62	75	3	2008-07-06 16:13:26	2008-07-06 16:13:26
2380	259	327	63	37.5	4	2008-07-06 16:13:26	2008-07-06 16:13:26
2381	259	328	18	74	1	2008-07-06 16:13:26	2008-07-06 16:13:26
2382	259	328	16	75	2	2008-07-06 16:13:26	2008-07-06 16:13:26
2383	259	328	17	75	3	2008-07-06 16:13:26	2008-07-06 16:13:26
2384	259	328	18	37	4	2008-07-06 16:13:26	2008-07-06 16:13:26
2385	246	299	8	77	1	2008-07-06 16:13:37	2008-07-06 16:13:37
2386	246	299	9	78	2	2008-07-06 16:13:37	2008-07-06 16:13:37
2387	246	299	7	77	3	2008-07-06 16:13:37	2008-07-06 16:13:37
2388	246	299	9	38	4	2008-07-06 16:13:37	2008-07-06 16:13:37
2389	246	300	89	76	1	2008-07-06 16:13:37	2008-07-06 16:13:37
2390	246	300	88	77	2	2008-07-06 16:13:37	2008-07-06 16:13:37
2391	246	300	90	78	3	2008-07-06 16:13:37	2008-07-06 16:13:37
2392	246	300	89	37	4	2008-07-06 16:13:37	2008-07-06 16:13:37
2393	247	301	173	78	1	2008-07-06 16:15:29	2008-07-06 16:15:29
2394	247	301	174	78	2	2008-07-06 16:15:29	2008-07-06 16:15:29
2395	247	301	172	78	3	2008-07-06 16:15:29	2008-07-06 16:15:29
2396	247	301	173	39	4	2008-07-06 16:15:29	2008-07-06 16:15:29
2397	247	302	159	78	1	2008-07-06 16:15:29	2008-07-06 16:15:29
2398	247	302	158	77	2	2008-07-06 16:15:29	2008-07-06 16:15:29
2399	247	302	157	77	3	2008-07-06 16:15:29	2008-07-06 16:15:29
2400	247	302	159	39	4	2008-07-06 16:15:29	2008-07-06 16:15:29
2401	254	313	160	74	1	2008-07-06 16:19:03	2008-07-06 16:19:03
2402	254	313	161	76	2	2008-07-06 16:19:03	2008-07-06 16:19:03
2403	254	313	162	74	3	2008-07-06 16:19:03	2008-07-06 16:19:03
2404	254	313	160	37.5	4	2008-07-06 16:19:03	2008-07-06 16:19:03
2405	254	314	111	75	1	2008-07-06 16:19:03	2008-07-06 16:19:03
2406	254	314	109	76	2	2008-07-06 16:19:03	2008-07-06 16:19:03
2407	254	314	110	75	3	2008-07-06 16:19:03	2008-07-06 16:19:03
2408	254	314	111	37.5	4	2008-07-06 16:19:03	2008-07-06 16:19:03
2409	287	359	68	74	1	2008-07-06 16:20:21	2008-07-06 16:20:21
2410	288	359	68	77	1	2008-07-06 16:20:21	2008-07-06 16:20:21
2411	289	359	68	71	1	2008-07-06 16:20:21	2008-07-06 16:20:21
2412	287	359	67	74	2	2008-07-06 16:20:21	2008-07-06 16:20:21
2413	288	359	67	75	2	2008-07-06 16:20:21	2008-07-06 16:20:21
2414	289	359	67	72	2	2008-07-06 16:20:21	2008-07-06 16:20:21
2415	287	359	69	75	3	2008-07-06 16:20:21	2008-07-06 16:20:21
2416	288	359	69	75	3	2008-07-06 16:20:21	2008-07-06 16:20:21
2417	289	359	69	71	3	2008-07-06 16:20:21	2008-07-06 16:20:21
2418	287	359	68	37	4	2008-07-06 16:20:21	2008-07-06 16:20:21
2419	288	359	68	38	4	2008-07-06 16:20:21	2008-07-06 16:20:21
2420	289	359	68	37	4	2008-07-06 16:20:21	2008-07-06 16:20:21
2421	287	360	138	74	1	2008-07-06 16:20:21	2008-07-06 16:20:21
2422	288	360	138	74	1	2008-07-06 16:20:21	2008-07-06 16:20:21
2423	289	360	138	72	1	2008-07-06 16:20:21	2008-07-06 16:20:21
2424	287	360	136	74	2	2008-07-06 16:20:21	2008-07-06 16:20:21
2425	288	360	136	74	2	2008-07-06 16:20:21	2008-07-06 16:20:21
2426	289	360	136	72	2	2008-07-06 16:20:21	2008-07-06 16:20:21
2427	287	360	137	74	3	2008-07-06 16:20:21	2008-07-06 16:20:21
2428	288	360	137	75	3	2008-07-06 16:20:21	2008-07-06 16:20:21
2429	289	360	137	72	3	2008-07-06 16:20:21	2008-07-06 16:20:21
2430	287	360	138	36.5	4	2008-07-06 16:20:21	2008-07-06 16:20:21
2431	288	360	138	37	4	2008-07-06 16:20:21	2008-07-06 16:20:21
2432	289	360	138	37	4	2008-07-06 16:20:21	2008-07-06 16:20:21
2433	261	329	130	76	1	2008-07-06 16:20:28	2008-07-06 16:20:28
2434	261	329	131	75	2	2008-07-06 16:20:28	2008-07-06 16:20:28
2435	261	329	132	77	3	2008-07-06 16:20:28	2008-07-06 16:20:28
2436	261	329	130	38	4	2008-07-06 16:20:28	2008-07-06 16:20:28
2437	261	330	48	75	1	2008-07-06 16:20:29	2008-07-06 16:20:29
2438	261	330	46	76	2	2008-07-06 16:20:29	2008-07-06 16:20:29
2439	261	330	47	76	3	2008-07-06 16:20:29	2008-07-06 16:20:29
2440	261	330	46	38.5	4	2008-07-06 16:20:29	2008-07-06 16:20:29
2441	278	361	147	74	1	2008-07-06 16:20:46	2008-07-06 16:20:46
2442	279	361	147	72	1	2008-07-06 16:20:46	2008-07-06 16:20:46
2443	280	361	147	73	1	2008-07-06 16:20:46	2008-07-06 16:20:46
2444	278	361	146	75	2	2008-07-06 16:20:46	2008-07-06 16:20:46
2445	279	361	146	73	2	2008-07-06 16:20:46	2008-07-06 16:20:46
2446	280	361	146	75	2	2008-07-06 16:20:46	2008-07-06 16:20:46
2447	278	361	145	74	3	2008-07-06 16:20:46	2008-07-06 16:20:46
2448	279	361	145	73	3	2008-07-06 16:20:46	2008-07-06 16:20:46
2449	280	361	145	75	3	2008-07-06 16:20:46	2008-07-06 16:20:46
2450	278	361	146	36	4	2008-07-06 16:20:46	2008-07-06 16:20:46
2451	279	361	146	38	4	2008-07-06 16:20:46	2008-07-06 16:20:46
2452	280	361	146	38.5	4	2008-07-06 16:20:46	2008-07-06 16:20:46
2453	278	362	82	74	1	2008-07-06 16:20:46	2008-07-06 16:20:46
2454	279	362	82	73	1	2008-07-06 16:20:46	2008-07-06 16:20:46
2455	280	362	82	74	1	2008-07-06 16:20:47	2008-07-06 16:20:47
2456	278	362	84	72	2	2008-07-06 16:20:47	2008-07-06 16:20:47
2457	279	362	84	72	2	2008-07-06 16:20:47	2008-07-06 16:20:47
2458	280	362	84	76	2	2008-07-06 16:20:47	2008-07-06 16:20:47
2459	278	362	83	71	3	2008-07-06 16:20:47	2008-07-06 16:20:47
2460	279	362	83	72	3	2008-07-06 16:20:47	2008-07-06 16:20:47
2461	280	362	83	73	3	2008-07-06 16:20:47	2008-07-06 16:20:47
2462	278	362	82	34	4	2008-07-06 16:20:47	2008-07-06 16:20:47
2463	279	362	82	37	4	2008-07-06 16:20:47	2008-07-06 16:20:47
2464	280	362	82	37	4	2008-07-06 16:20:47	2008-07-06 16:20:47
2465	260	323	94	78	1	2008-07-06 16:23:32	2008-07-06 16:23:32
2466	260	323	95	76	2	2008-07-06 16:23:32	2008-07-06 16:23:32
2467	260	323	96	75	3	2008-07-06 16:23:32	2008-07-06 16:23:32
2468	260	323	94	38.5	4	2008-07-06 16:23:32	2008-07-06 16:23:32
2469	260	324	21	77	1	2008-07-06 16:23:32	2008-07-06 16:23:32
2470	260	324	19	77	2	2008-07-06 16:23:32	2008-07-06 16:23:32
2471	260	324	20	76	3	2008-07-06 16:23:32	2008-07-06 16:23:32
2472	260	324	19	38.5	4	2008-07-06 16:23:32	2008-07-06 16:23:32
2473	293	351	166	75	1	2008-07-06 16:25:03	2008-07-06 16:25:03
2474	294	351	166	74	1	2008-07-06 16:25:03	2008-07-06 16:25:03
2475	295	351	166	76	1	2008-07-06 16:25:03	2008-07-06 16:25:03
2476	293	351	167	74	2	2008-07-06 16:25:03	2008-07-06 16:25:03
2477	294	351	167	72	2	2008-07-06 16:25:03	2008-07-06 16:25:03
2478	295	351	167	75	2	2008-07-06 16:25:03	2008-07-06 16:25:03
2479	293	351	168	76	3	2008-07-06 16:25:03	2008-07-06 16:25:03
2480	294	351	168	71	3	2008-07-06 16:25:03	2008-07-06 16:25:03
2481	295	351	168	76	3	2008-07-06 16:25:03	2008-07-06 16:25:03
2482	293	351	166	38	4	2008-07-06 16:25:03	2008-07-06 16:25:03
2483	294	351	166	37	4	2008-07-06 16:25:03	2008-07-06 16:25:03
2484	295	351	166	37.5	4	2008-07-06 16:25:03	2008-07-06 16:25:03
2485	293	352	209	74	1	2008-07-06 16:25:03	2008-07-06 16:25:03
2486	294	352	209	72	1	2008-07-06 16:25:03	2008-07-06 16:25:03
2487	295	352	209	75	1	2008-07-06 16:25:03	2008-07-06 16:25:03
2488	293	352	208	75	2	2008-07-06 16:25:03	2008-07-06 16:25:03
2489	294	352	208	71	2	2008-07-06 16:25:03	2008-07-06 16:25:03
2490	295	352	208	74	2	2008-07-06 16:25:03	2008-07-06 16:25:03
2491	293	352	210	74	3	2008-07-06 16:25:03	2008-07-06 16:25:03
2492	294	352	210	72	3	2008-07-06 16:25:03	2008-07-06 16:25:03
2493	295	352	210	74	3	2008-07-06 16:25:03	2008-07-06 16:25:03
2494	293	352	209	37	4	2008-07-06 16:25:03	2008-07-06 16:25:03
2495	294	352	209	36	4	2008-07-06 16:25:03	2008-07-06 16:25:03
2496	295	352	209	37.5	4	2008-07-06 16:25:03	2008-07-06 16:25:03
2497	272	343	163	75	1	2008-07-06 16:25:25	2008-07-06 16:25:25
2498	273	343	163	77	1	2008-07-06 16:25:25	2008-07-06 16:25:25
2499	274	343	163	75	1	2008-07-06 16:25:25	2008-07-06 16:25:25
2500	272	343	164	74	2	2008-07-06 16:25:25	2008-07-06 16:25:25
2501	273	343	164	76	2	2008-07-06 16:25:25	2008-07-06 16:25:25
2502	274	343	164	75	2	2008-07-06 16:25:25	2008-07-06 16:25:25
2503	272	343	165	73	3	2008-07-06 16:25:25	2008-07-06 16:25:25
2504	273	343	165	76	3	2008-07-06 16:25:25	2008-07-06 16:25:25
2505	274	343	165	77	3	2008-07-06 16:25:25	2008-07-06 16:25:25
2506	272	343	163	38.5	4	2008-07-06 16:25:25	2008-07-06 16:25:25
2507	273	343	163	38	4	2008-07-06 16:25:25	2008-07-06 16:25:25
2508	274	343	163	35	4	2008-07-06 16:25:25	2008-07-06 16:25:25
2509	272	344	76	75	1	2008-07-06 16:25:25	2008-07-06 16:25:25
2510	273	344	76	75	1	2008-07-06 16:25:25	2008-07-06 16:25:25
2511	274	344	76	76	1	2008-07-06 16:25:25	2008-07-06 16:25:25
2512	272	344	77	74	2	2008-07-06 16:25:25	2008-07-06 16:25:25
2513	273	344	77	73	2	2008-07-06 16:25:25	2008-07-06 16:25:25
2514	274	344	77	77	2	2008-07-06 16:25:25	2008-07-06 16:25:25
2515	272	344	78	73	3	2008-07-06 16:25:25	2008-07-06 16:25:25
2516	273	344	78	74	3	2008-07-06 16:25:25	2008-07-06 16:25:25
2517	274	344	78	76	3	2008-07-06 16:25:25	2008-07-06 16:25:25
2518	272	344	76	39	4	2008-07-06 16:25:25	2008-07-06 16:25:25
2519	273	344	76	37.5	4	2008-07-06 16:25:26	2008-07-06 16:25:26
2520	274	344	76	35	4	2008-07-06 16:25:26	2008-07-06 16:25:26
2521	282	353	64	73	1	2008-07-06 16:51:04	2008-07-06 16:51:04
2522	283	353	64	75	1	2008-07-06 16:51:04	2008-07-06 16:51:04
2523	281	353	64	73	1	2008-07-06 16:51:04	2008-07-06 16:51:04
2524	282	353	65	73	2	2008-07-06 16:51:04	2008-07-06 16:51:04
2525	283	353	65	75	2	2008-07-06 16:51:04	2008-07-06 16:51:04
2526	281	353	65	76	2	2008-07-06 16:51:04	2008-07-06 16:51:04
2527	282	353	66	74	3	2008-07-06 16:51:04	2008-07-06 16:51:04
2528	283	353	66	75	3	2008-07-06 16:51:04	2008-07-06 16:51:04
2529	281	353	66	75	3	2008-07-06 16:51:04	2008-07-06 16:51:04
2530	282	353	64	36.5	4	2008-07-06 16:51:04	2008-07-06 16:51:04
2531	283	353	64	37.5	4	2008-07-06 16:51:04	2008-07-06 16:51:04
2532	281	353	64	38.5	4	2008-07-06 16:51:04	2008-07-06 16:51:04
2533	282	354	225	74	1	2008-07-06 16:51:04	2008-07-06 16:51:04
2534	283	354	225	75	1	2008-07-06 16:51:04	2008-07-06 16:51:04
2535	281	354	225	76	1	2008-07-06 16:51:04	2008-07-06 16:51:04
2536	282	354	223	73	2	2008-07-06 16:51:04	2008-07-06 16:51:04
2537	283	354	223	75	2	2008-07-06 16:51:04	2008-07-06 16:51:04
2538	281	354	223	74	2	2008-07-06 16:51:04	2008-07-06 16:51:04
2539	282	354	224	75	3	2008-07-06 16:51:04	2008-07-06 16:51:04
2540	283	354	224	77	3	2008-07-06 16:51:04	2008-07-06 16:51:04
2541	281	354	224	77	3	2008-07-06 16:51:04	2008-07-06 16:51:04
2542	282	354	225	37	4	2008-07-06 16:51:04	2008-07-06 16:51:04
2543	283	354	225	37.5	4	2008-07-06 16:51:04	2008-07-06 16:51:04
2544	281	354	225	38	4	2008-07-06 16:51:04	2008-07-06 16:51:04
2545	284	355	29	78	1	2008-07-06 16:51:46	2008-07-06 16:51:46
2546	285	355	29	74	1	2008-07-06 16:51:46	2008-07-06 16:51:46
2547	286	355	29	78	1	2008-07-06 16:51:46	2008-07-06 16:51:46
2548	284	355	28	75	2	2008-07-06 16:51:46	2008-07-06 16:51:46
2549	285	355	28	73	2	2008-07-06 16:51:46	2008-07-06 16:51:46
2550	286	355	28	75	2	2008-07-06 16:51:46	2008-07-06 16:51:46
2551	284	355	30	74	3	2008-07-06 16:51:46	2008-07-06 16:51:46
2552	285	355	30	73	3	2008-07-06 16:51:46	2008-07-06 16:51:46
2553	286	355	30	74	3	2008-07-06 16:51:46	2008-07-06 16:51:46
2554	284	355	29	37.5	4	2008-07-06 16:51:46	2008-07-06 16:51:46
2555	285	355	29	37.5	4	2008-07-06 16:51:46	2008-07-06 16:51:46
2556	286	355	29	38	4	2008-07-06 16:51:46	2008-07-06 16:51:46
2557	284	356	57	77	1	2008-07-06 16:51:46	2008-07-06 16:51:46
2558	285	356	57	75	1	2008-07-06 16:51:46	2008-07-06 16:51:46
2559	286	356	57	76	1	2008-07-06 16:51:46	2008-07-06 16:51:46
2560	284	356	56	74	2	2008-07-06 16:51:46	2008-07-06 16:51:46
2561	285	356	56	73	2	2008-07-06 16:51:46	2008-07-06 16:51:46
2562	286	356	56	73	2	2008-07-06 16:51:46	2008-07-06 16:51:46
2563	284	356	55	74	3	2008-07-06 16:51:46	2008-07-06 16:51:46
2564	285	356	55	73	3	2008-07-06 16:51:46	2008-07-06 16:51:46
2565	286	356	55	75	3	2008-07-06 16:51:46	2008-07-06 16:51:46
2566	284	356	57	37.5	4	2008-07-06 16:51:46	2008-07-06 16:51:46
2567	285	356	57	37.5	4	2008-07-06 16:51:46	2008-07-06 16:51:46
2568	286	356	57	37.5	4	2008-07-06 16:51:46	2008-07-06 16:51:46
2569	262	331	58	77	1	2008-07-06 16:53:33	2008-07-06 16:53:33
2570	262	331	59	76	2	2008-07-06 16:53:33	2008-07-06 16:53:33
2571	262	331	60	76	3	2008-07-06 16:53:33	2008-07-06 16:53:33
2572	262	331	58	37.5	4	2008-07-06 16:53:33	2008-07-06 16:53:33
2573	262	332	73	75	1	2008-07-06 16:53:33	2008-07-06 16:53:33
2574	262	332	74	75	2	2008-07-06 16:53:33	2008-07-06 16:53:33
2575	262	332	75	76	3	2008-07-06 16:53:33	2008-07-06 16:53:33
2576	262	332	73	37	4	2008-07-06 16:53:33	2008-07-06 16:53:33
2585	318	406	107	76	1	2008-07-07 11:36:27	2008-07-07 11:36:27
2586	318	406	108	76	2	2008-07-07 11:36:27	2008-07-07 11:36:27
2587	318	406	106	76	3	2008-07-07 11:36:27	2008-07-07 11:36:27
2588	318	406	108	37	4	2008-07-07 11:36:27	2008-07-07 11:36:27
2589	318	407	175	77	1	2008-07-07 11:36:27	2008-07-07 11:36:27
2590	318	407	177	78	2	2008-07-07 11:36:27	2008-07-07 11:36:27
2591	318	407	176	77	3	2008-07-07 11:36:27	2008-07-07 11:36:27
2592	318	407	175	37	4	2008-07-07 11:36:27	2008-07-07 11:36:27
2593	334	420	93	76	1	2008-07-07 11:36:40	2008-07-07 11:36:40
2594	334	420	92	75	2	2008-07-07 11:36:40	2008-07-07 11:36:40
2595	334	420	91	74	3	2008-07-07 11:36:40	2008-07-07 11:36:40
2596	334	420	93	37.5	4	2008-07-07 11:36:40	2008-07-07 11:36:40
2597	334	421	21	74	1	2008-07-07 11:36:40	2008-07-07 11:36:40
2598	334	421	19	75	2	2008-07-07 11:36:40	2008-07-07 11:36:40
2599	334	421	20	74	3	2008-07-07 11:36:40	2008-07-07 11:36:40
2600	334	421	21	37	4	2008-07-07 11:36:40	2008-07-07 11:36:40
2601	311	396	169	78	1	2008-07-07 11:37:11	2008-07-07 11:37:11
2602	311	396	171	77	2	2008-07-07 11:37:11	2008-07-07 11:37:11
2603	311	396	170	78	3	2008-07-07 11:37:11	2008-07-07 11:37:11
2604	311	396	169	39	4	2008-07-07 11:37:11	2008-07-07 11:37:11
2605	311	397	9	77	1	2008-07-07 11:37:11	2008-07-07 11:37:11
2606	311	397	8	76	2	2008-07-07 11:37:11	2008-07-07 11:37:11
2607	311	397	7	79	3	2008-07-07 11:37:11	2008-07-07 11:37:11
2608	311	397	9	38.5	4	2008-07-07 11:37:11	2008-07-07 11:37:11
2609	346	446	191	73	1	2008-07-07 11:37:33	2008-07-07 11:37:33
2610	346	446	192	75	2	2008-07-07 11:37:33	2008-07-07 11:37:33
2611	346	446	190	74	3	2008-07-07 11:37:33	2008-07-07 11:37:33
2612	346	446	191	36.5	4	2008-07-07 11:37:33	2008-07-07 11:37:33
2613	346	447	49	73	1	2008-07-07 11:37:33	2008-07-07 11:37:33
2614	346	447	51	72	2	2008-07-07 11:37:33	2008-07-07 11:37:33
2615	346	447	50	72	3	2008-07-07 11:37:33	2008-07-07 11:37:33
2616	346	447	51	36	4	2008-07-07 11:37:33	2008-07-07 11:37:33
2617	316	402	129	76	1	2008-07-07 11:37:47	2008-07-07 11:37:47
2618	316	402	128	76	2	2008-07-07 11:37:47	2008-07-07 11:37:47
2619	316	402	127	76	3	2008-07-07 11:37:47	2008-07-07 11:37:47
2620	316	402	129	37	4	2008-07-07 11:37:47	2008-07-07 11:37:47
2621	316	403	181	76	1	2008-07-07 11:37:47	2008-07-07 11:37:47
2622	316	403	183	77	2	2008-07-07 11:37:47	2008-07-07 11:37:47
2623	316	403	182	76	3	2008-07-07 11:37:47	2008-07-07 11:37:47
2624	316	403	181	38.5	4	2008-07-07 11:37:47	2008-07-07 11:37:47
2625	335	428	33	74	1	2008-07-07 11:38:33	2008-07-07 11:38:33
2626	335	428	31	75	2	2008-07-07 11:38:33	2008-07-07 11:38:33
2627	335	428	32	74	3	2008-07-07 11:38:33	2008-07-07 11:38:33
2628	335	428	31	37	4	2008-07-07 11:38:33	2008-07-07 11:38:33
2629	335	429	43	76	1	2008-07-07 11:38:33	2008-07-07 11:38:33
2630	335	429	45	75	2	2008-07-07 11:38:33	2008-07-07 11:38:33
2631	335	429	44	76	3	2008-07-07 11:38:33	2008-07-07 11:38:33
2632	335	429	43	37	4	2008-07-07 11:38:33	2008-07-07 11:38:33
2633	336	430	76	76	1	2008-07-07 11:38:35	2008-07-07 11:38:35
2634	337	430	76	76	1	2008-07-07 11:38:35	2008-07-07 11:38:35
2635	338	430	76	75	1	2008-07-07 11:38:35	2008-07-07 11:38:35
2636	336	430	77	75	2	2008-07-07 11:38:35	2008-07-07 11:38:35
2637	337	430	77	75	2	2008-07-07 11:38:35	2008-07-07 11:38:35
2638	338	430	77	74	2	2008-07-07 11:38:35	2008-07-07 11:38:35
2639	336	430	78	74	3	2008-07-07 11:38:35	2008-07-07 11:38:35
2640	337	430	78	75	3	2008-07-07 11:38:35	2008-07-07 11:38:35
2641	338	430	78	74	3	2008-07-07 11:38:35	2008-07-07 11:38:35
2642	336	430	76	38	4	2008-07-07 11:38:35	2008-07-07 11:38:35
2643	337	430	76	37	4	2008-07-07 11:38:35	2008-07-07 11:38:35
2644	338	430	76	37	4	2008-07-07 11:38:35	2008-07-07 11:38:35
2645	336	431	144	76	1	2008-07-07 11:38:35	2008-07-07 11:38:35
2646	337	431	144	76	1	2008-07-07 11:38:35	2008-07-07 11:38:35
2647	338	431	144	75	1	2008-07-07 11:38:35	2008-07-07 11:38:35
2648	336	431	142	76	2	2008-07-07 11:38:35	2008-07-07 11:38:35
2649	337	431	142	76	2	2008-07-07 11:38:35	2008-07-07 11:38:35
2650	338	431	142	76	2	2008-07-07 11:38:35	2008-07-07 11:38:35
2651	336	431	143	77	3	2008-07-07 11:38:35	2008-07-07 11:38:35
2652	337	431	143	77	3	2008-07-07 11:38:35	2008-07-07 11:38:35
2653	338	431	143	77	3	2008-07-07 11:38:35	2008-07-07 11:38:35
2654	336	431	144	38.5	4	2008-07-07 11:38:35	2008-07-07 11:38:35
2655	337	431	144	38	4	2008-07-07 11:38:35	2008-07-07 11:38:35
2656	338	431	144	38	4	2008-07-07 11:38:35	2008-07-07 11:38:35
2657	315	400	111	76	1	2008-07-07 11:38:43	2008-07-07 11:38:43
2658	315	400	109	76	2	2008-07-07 11:38:43	2008-07-07 11:38:43
2659	315	400	110	75	3	2008-07-07 11:38:43	2008-07-07 11:38:43
2660	315	400	111	37.5	4	2008-07-07 11:38:43	2008-07-07 11:38:43
2661	315	401	89	77	1	2008-07-07 11:38:43	2008-07-07 11:38:43
2662	315	401	88	78	2	2008-07-07 11:38:43	2008-07-07 11:38:43
2663	315	401	90	76	3	2008-07-07 11:38:43	2008-07-07 11:38:43
2664	315	401	89	38	4	2008-07-07 11:38:43	2008-07-07 11:38:43
2665	339	436	94	76	1	2008-07-07 11:39:03	2008-07-07 11:39:03
2666	339	436	95	73	2	2008-07-07 11:39:03	2008-07-07 11:39:03
2667	339	436	96	74	3	2008-07-07 11:39:03	2008-07-07 11:39:03
2668	339	436	94	39	4	2008-07-07 11:39:03	2008-07-07 11:39:03
2669	339	437	196	73	1	2008-07-07 11:39:03	2008-07-07 11:39:03
2670	339	437	197	74	2	2008-07-07 11:39:03	2008-07-07 11:39:03
2671	339	437	198	73	3	2008-07-07 11:39:03	2008-07-07 11:39:03
2672	339	437	197	36	4	2008-07-07 11:39:03	2008-07-07 11:39:03
2673	320	410	161	76	1	2008-07-07 11:39:34	2008-07-07 11:39:34
2674	320	410	160	77	2	2008-07-07 11:39:34	2008-07-07 11:39:34
2675	320	410	162	75	3	2008-07-07 11:39:34	2008-07-07 11:39:34
2676	320	410	161	37	4	2008-07-07 11:39:34	2008-07-07 11:39:34
2677	320	411	178	77	1	2008-07-07 11:39:34	2008-07-07 11:39:34
2678	320	411	180	77	2	2008-07-07 11:39:34	2008-07-07 11:39:34
2679	320	411	179	76	3	2008-07-07 11:39:34	2008-07-07 11:39:34
2680	320	411	178	37.5	4	2008-07-07 11:39:34	2008-07-07 11:39:34
2681	321	412	14	77	1	2008-07-07 11:39:50	2008-07-07 11:39:50
2682	321	412	13	77	2	2008-07-07 11:39:50	2008-07-07 11:39:50
2683	321	412	15	77	3	2008-07-07 11:39:50	2008-07-07 11:39:50
2684	321	412	14	38.5	4	2008-07-07 11:39:50	2008-07-07 11:39:50
2685	321	413	186	77	1	2008-07-07 11:39:50	2008-07-07 11:39:50
2686	321	413	185	76	2	2008-07-07 11:39:50	2008-07-07 11:39:50
2687	321	413	184	76	3	2008-07-07 11:39:50	2008-07-07 11:39:50
2688	321	413	186	38.5	4	2008-07-07 11:39:50	2008-07-07 11:39:50
2689	348	450	223	75	1	2008-07-07 11:40:20	2008-07-07 11:40:20
2690	348	450	225	77	2	2008-07-07 11:40:20	2008-07-07 11:40:20
2691	348	450	224	75	3	2008-07-07 11:40:20	2008-07-07 11:40:20
2692	348	450	225	37.5	4	2008-07-07 11:40:20	2008-07-07 11:40:20
2693	348	451	48	76	1	2008-07-07 11:40:20	2008-07-07 11:40:20
2694	348	451	46	78	2	2008-07-07 11:40:20	2008-07-07 11:40:20
2695	348	451	47	76	3	2008-07-07 11:40:20	2008-07-07 11:40:20
2696	348	451	46	38.5	4	2008-07-07 11:40:20	2008-07-07 11:40:20
2697	342	432	166	76	1	2008-07-07 11:40:25	2008-07-07 11:40:25
2698	342	432	167	74	2	2008-07-07 11:40:25	2008-07-07 11:40:25
2699	342	432	168	77	3	2008-07-07 11:40:26	2008-07-07 11:40:26
2700	342	432	166	37.5	4	2008-07-07 11:40:26	2008-07-07 11:40:26
2701	342	433	73	76	1	2008-07-07 11:40:26	2008-07-07 11:40:26
2702	342	433	74	75	2	2008-07-07 11:40:26	2008-07-07 11:40:26
2703	342	433	75	77	3	2008-07-07 11:40:26	2008-07-07 11:40:26
2704	342	433	73	38	4	2008-07-07 11:40:26	2008-07-07 11:40:26
2705	340	438	52	75	1	2008-07-07 11:41:20	2008-07-07 11:41:20
2706	340	438	53	74	2	2008-07-07 11:41:20	2008-07-07 11:41:20
2707	340	438	54	74	3	2008-07-07 11:41:20	2008-07-07 11:41:20
2708	340	438	52	36.5	4	2008-07-07 11:41:20	2008-07-07 11:41:20
2709	340	439	18	77	1	2008-07-07 11:41:20	2008-07-07 11:41:20
2710	340	439	16	76	2	2008-07-07 11:41:20	2008-07-07 11:41:20
2711	340	439	17	74	3	2008-07-07 11:41:20	2008-07-07 11:41:20
2712	340	439	18	38	4	2008-07-07 11:41:20	2008-07-07 11:41:20
2713	341	440	122	76	1	2008-07-07 11:41:27	2008-07-07 11:41:27
2714	341	440	121	76	2	2008-07-07 11:41:27	2008-07-07 11:41:27
2715	341	440	123	75	3	2008-07-07 11:41:27	2008-07-07 11:41:27
2716	341	440	121	37	4	2008-07-07 11:41:27	2008-07-07 11:41:27
2717	341	441	25	75	1	2008-07-07 11:41:27	2008-07-07 11:41:27
2718	341	441	26	75	2	2008-07-07 11:41:27	2008-07-07 11:41:27
2719	341	441	27	75	3	2008-07-07 11:41:27	2008-07-07 11:41:27
2720	341	441	25	37	4	2008-07-07 11:41:27	2008-07-07 11:41:27
2721	347	448	147	77	1	2008-07-07 11:41:56	2008-07-07 11:41:56
2722	439	448	147	75	1	2008-07-07 11:41:56	2008-07-07 11:41:56
2723	440	448	147	75	1	2008-07-07 11:41:56	2008-07-07 11:41:56
2724	347	448	146	75	2	2008-07-07 11:41:56	2008-07-07 11:41:56
2725	439	448	146	75	2	2008-07-07 11:41:56	2008-07-07 11:41:56
2726	440	448	146	76	2	2008-07-07 11:41:56	2008-07-07 11:41:56
2727	347	448	145	76	3	2008-07-07 11:41:56	2008-07-07 11:41:56
2728	439	448	145	75	3	2008-07-07 11:41:56	2008-07-07 11:41:56
2729	440	448	145	75	3	2008-07-07 11:41:56	2008-07-07 11:41:56
2730	347	448	146	39	4	2008-07-07 11:41:56	2008-07-07 11:41:56
2731	439	448	146	38	4	2008-07-07 11:41:56	2008-07-07 11:41:56
2732	440	448	146	37.5	4	2008-07-07 11:41:56	2008-07-07 11:41:56
2733	347	449	163	75	1	2008-07-07 11:41:56	2008-07-07 11:41:56
2734	439	449	163	76	1	2008-07-07 11:41:56	2008-07-07 11:41:56
2735	440	449	163	75	1	2008-07-07 11:41:56	2008-07-07 11:41:56
2736	347	449	164	75	2	2008-07-07 11:41:56	2008-07-07 11:41:56
2737	439	449	164	76	2	2008-07-07 11:41:56	2008-07-07 11:41:56
2738	440	449	164	76	2	2008-07-07 11:41:56	2008-07-07 11:41:56
2739	347	449	165	74	3	2008-07-07 11:41:56	2008-07-07 11:41:56
2740	439	449	165	75	3	2008-07-07 11:41:56	2008-07-07 11:41:56
2741	440	449	165	74	3	2008-07-07 11:41:56	2008-07-07 11:41:56
2742	347	449	163	36.5	4	2008-07-07 11:41:56	2008-07-07 11:41:56
2743	439	449	163	37.5	4	2008-07-07 11:41:56	2008-07-07 11:41:56
2744	440	449	163	36.5	4	2008-07-07 11:41:56	2008-07-07 11:41:56
2745	329	418	201	76	1	2008-07-07 11:42:11	2008-07-07 11:42:11
2746	329	418	200	75	2	2008-07-07 11:42:11	2008-07-07 11:42:11
2747	329	418	199	75	3	2008-07-07 11:42:11	2008-07-07 11:42:11
2748	329	418	201	38	4	2008-07-07 11:42:11	2008-07-07 11:42:11
2749	329	419	118	76	1	2008-07-07 11:42:11	2008-07-07 11:42:11
2750	329	419	120	75	2	2008-07-07 11:42:11	2008-07-07 11:42:11
2751	329	419	119	74	3	2008-07-07 11:42:11	2008-07-07 11:42:11
2752	329	419	118	37.5	4	2008-07-07 11:42:11	2008-07-07 11:42:11
2753	317	404	70	77	1	2008-07-07 11:42:23	2008-07-07 11:42:23
2754	317	404	71	76	2	2008-07-07 11:42:23	2008-07-07 11:42:23
2755	317	404	72	78	3	2008-07-07 11:42:23	2008-07-07 11:42:23
2756	317	404	70	38.5	4	2008-07-07 11:42:23	2008-07-07 11:42:23
2757	317	405	215	76	1	2008-07-07 11:42:23	2008-07-07 11:42:23
2758	317	405	214	76	2	2008-07-07 11:42:23	2008-07-07 11:42:23
2759	317	405	216	75	3	2008-07-07 11:42:23	2008-07-07 11:42:23
2760	317	405	215	37.5	4	2008-07-07 11:42:23	2008-07-07 11:42:23
2761	322	414	105	76	1	2008-07-07 11:43:28	2008-07-07 11:43:28
2762	322	414	103	75	2	2008-07-07 11:43:28	2008-07-07 11:43:28
2763	322	414	104	78	3	2008-07-07 11:43:28	2008-07-07 11:43:28
2764	322	414	105	37.5	4	2008-07-07 11:43:28	2008-07-07 11:43:28
2765	322	415	99	79	1	2008-07-07 11:43:28	2008-07-07 11:43:28
2766	322	415	97	78	2	2008-07-07 11:43:28	2008-07-07 11:43:28
2767	322	415	98	77	3	2008-07-07 11:43:28	2008-07-07 11:43:28
2768	322	415	99	37.5	4	2008-07-07 11:43:28	2008-07-07 11:43:28
2769	319	408	158	77	1	2008-07-07 11:43:30	2008-07-07 11:43:30
2770	319	408	159	79	2	2008-07-07 11:43:30	2008-07-07 11:43:30
2771	319	408	157	80	3	2008-07-07 11:43:30	2008-07-07 11:43:30
2772	319	408	159	40.5	4	2008-07-07 11:43:30	2008-07-07 11:43:30
2773	319	409	101	77	1	2008-07-07 11:43:30	2008-07-07 11:43:30
2774	319	409	102	79	2	2008-07-07 11:43:30	2008-07-07 11:43:30
2775	319	409	100	76	3	2008-07-07 11:43:30	2008-07-07 11:43:30
2776	319	409	101	39	4	2008-07-07 11:43:30	2008-07-07 11:43:30
2777	344	442	187	75	1	2008-07-07 11:44:22	2008-07-07 11:44:22
2778	344	442	188	74	2	2008-07-07 11:44:22	2008-07-07 11:44:22
2779	344	442	189	76	3	2008-07-07 11:44:22	2008-07-07 11:44:22
2780	344	442	187	38	4	2008-07-07 11:44:22	2008-07-07 11:44:22
2781	344	443	151	76	1	2008-07-07 11:44:22	2008-07-07 11:44:22
2782	344	443	152	75	2	2008-07-07 11:44:22	2008-07-07 11:44:22
2783	344	443	153	75	3	2008-07-07 11:44:22	2008-07-07 11:44:22
2784	344	443	151	38	4	2008-07-07 11:44:22	2008-07-07 11:44:22
2785	343	434	68	76	1	2008-07-07 11:44:42	2008-07-07 11:44:42
2786	343	434	67	74	2	2008-07-07 11:44:42	2008-07-07 11:44:42
2787	343	434	69	75	3	2008-07-07 11:44:42	2008-07-07 11:44:42
2788	343	434	68	38	4	2008-07-07 11:44:42	2008-07-07 11:44:42
2789	343	435	126	75	1	2008-07-07 11:44:42	2008-07-07 11:44:42
2790	343	435	124	76	2	2008-07-07 11:44:42	2008-07-07 11:44:42
2791	343	435	125	76	3	2008-07-07 11:44:42	2008-07-07 11:44:42
2792	343	435	126	37.5	4	2008-07-07 11:44:42	2008-07-07 11:44:42
2793	349	452	221	73	1	2008-07-07 11:44:57	2008-07-07 11:44:57
2794	350	452	221	75	1	2008-07-07 11:44:57	2008-07-07 11:44:57
2795	351	452	221	74	1	2008-07-07 11:44:57	2008-07-07 11:44:57
2796	349	452	222	73	2	2008-07-07 11:44:57	2008-07-07 11:44:57
2797	350	452	222	74	2	2008-07-07 11:44:57	2008-07-07 11:44:57
2798	351	452	222	75	2	2008-07-07 11:44:57	2008-07-07 11:44:57
2799	349	452	220	73	3	2008-07-07 11:44:57	2008-07-07 11:44:57
2800	350	452	220	76	3	2008-07-07 11:44:57	2008-07-07 11:44:57
2801	351	452	220	75	3	2008-07-07 11:44:57	2008-07-07 11:44:57
2802	349	452	222	37.5	4	2008-07-07 11:44:57	2008-07-07 11:44:57
2803	350	452	222	36	4	2008-07-07 11:44:57	2008-07-07 11:44:57
2804	351	452	222	37.5	4	2008-07-07 11:44:57	2008-07-07 11:44:57
2805	349	453	133	74	1	2008-07-07 11:44:57	2008-07-07 11:44:57
2806	350	453	133	76	1	2008-07-07 11:44:57	2008-07-07 11:44:57
2807	351	453	133	75	1	2008-07-07 11:44:57	2008-07-07 11:44:57
2808	349	453	134	74	2	2008-07-07 11:44:57	2008-07-07 11:44:57
2809	350	453	134	74	2	2008-07-07 11:44:57	2008-07-07 11:44:57
2810	351	453	134	76	2	2008-07-07 11:44:57	2008-07-07 11:44:57
2811	349	453	135	74	3	2008-07-07 11:44:57	2008-07-07 11:44:57
2812	350	453	135	76	3	2008-07-07 11:44:57	2008-07-07 11:44:57
2813	351	453	135	76	3	2008-07-07 11:44:57	2008-07-07 11:44:57
2814	349	453	133	37.5	4	2008-07-07 11:44:57	2008-07-07 11:44:57
2815	350	453	133	37	4	2008-07-07 11:44:57	2008-07-07 11:44:57
2816	351	453	133	38	4	2008-07-07 11:44:57	2008-07-07 11:44:57
2817	330	425	63	75	1	2008-07-07 11:45:30	2008-07-07 11:45:30
2818	331	425	63	75	1	2008-07-07 11:45:30	2008-07-07 11:45:30
2819	332	425	63	76	1	2008-07-07 11:45:30	2008-07-07 11:45:30
2820	330	425	61	74	2	2008-07-07 11:45:30	2008-07-07 11:45:30
2821	331	425	61	75	2	2008-07-07 11:45:30	2008-07-07 11:45:30
2822	332	425	61	75	2	2008-07-07 11:45:30	2008-07-07 11:45:30
2823	330	425	62	75	3	2008-07-07 11:45:30	2008-07-07 11:45:30
2824	331	425	62	75	3	2008-07-07 11:45:30	2008-07-07 11:45:30
2825	332	425	62	75	3	2008-07-07 11:45:30	2008-07-07 11:45:30
2826	330	425	63	37.5	4	2008-07-07 11:45:30	2008-07-07 11:45:30
2827	331	425	63	35	4	2008-07-07 11:45:30	2008-07-07 11:45:30
2828	332	425	63	37.5	4	2008-07-07 11:45:30	2008-07-07 11:45:30
2829	330	424	149	76	1	2008-07-07 11:45:30	2008-07-07 11:45:30
2830	331	424	149	76	1	2008-07-07 11:45:30	2008-07-07 11:45:30
2831	332	424	149	77	1	2008-07-07 11:45:30	2008-07-07 11:45:30
2832	330	424	150	75	2	2008-07-07 11:45:30	2008-07-07 11:45:30
2833	331	424	150	75	2	2008-07-07 11:45:30	2008-07-07 11:45:30
2834	332	424	150	76	2	2008-07-07 11:45:30	2008-07-07 11:45:30
2835	330	424	148	76	3	2008-07-07 11:45:30	2008-07-07 11:45:30
2836	331	424	148	76	3	2008-07-07 11:45:30	2008-07-07 11:45:30
2837	332	424	148	76	3	2008-07-07 11:45:30	2008-07-07 11:45:30
2838	330	424	149	38	4	2008-07-07 11:45:30	2008-07-07 11:45:30
2839	331	424	149	36	4	2008-07-07 11:45:30	2008-07-07 11:45:30
2840	332	424	149	38	4	2008-07-07 11:45:30	2008-07-07 11:45:30
2841	345	444	80	76	1	2008-07-07 11:45:45	2008-07-07 11:45:45
2842	345	444	81	76	2	2008-07-07 11:45:45	2008-07-07 11:45:45
2843	345	444	79	76	3	2008-07-07 11:45:45	2008-07-07 11:45:45
2844	345	444	80	37.5	4	2008-07-07 11:45:45	2008-07-07 11:45:45
2845	345	445	29	76	1	2008-07-07 11:45:45	2008-07-07 11:45:45
2846	345	445	28	75	2	2008-07-07 11:45:45	2008-07-07 11:45:45
2847	345	445	30	75	3	2008-07-07 11:45:45	2008-07-07 11:45:45
2848	345	445	29	38	4	2008-07-07 11:45:45	2008-07-07 11:45:45
2849	323	416	115	75	1	2008-07-07 11:46:55	2008-07-07 11:46:55
2850	324	416	115	78	1	2008-07-07 11:46:55	2008-07-07 11:46:55
2851	325	416	115	76	1	2008-07-07 11:46:55	2008-07-07 11:46:55
2852	323	416	116	74	2	2008-07-07 11:46:55	2008-07-07 11:46:55
2853	324	416	116	76	2	2008-07-07 11:46:55	2008-07-07 11:46:55
2854	325	416	116	76	2	2008-07-07 11:46:55	2008-07-07 11:46:55
2855	323	416	117	77	3	2008-07-07 11:46:55	2008-07-07 11:46:55
2856	324	416	117	77	3	2008-07-07 11:46:55	2008-07-07 11:46:55
2857	325	416	117	77	3	2008-07-07 11:46:55	2008-07-07 11:46:55
2858	323	416	115	37	4	2008-07-07 11:46:55	2008-07-07 11:46:55
2859	324	416	115	37.5	4	2008-07-07 11:46:55	2008-07-07 11:46:55
2860	325	416	115	38	4	2008-07-07 11:46:55	2008-07-07 11:46:55
2861	323	417	10	78	1	2008-07-07 11:46:55	2008-07-07 11:46:55
2862	324	417	10	78	1	2008-07-07 11:46:55	2008-07-07 11:46:55
2863	325	417	10	77	1	2008-07-07 11:46:55	2008-07-07 11:46:55
2864	323	417	11	76	2	2008-07-07 11:46:55	2008-07-07 11:46:55
2865	324	417	11	77	2	2008-07-07 11:46:55	2008-07-07 11:46:55
2866	325	417	11	77	2	2008-07-07 11:46:55	2008-07-07 11:46:55
2867	323	417	12	76	3	2008-07-07 11:46:55	2008-07-07 11:46:55
2868	324	417	12	77	3	2008-07-07 11:46:55	2008-07-07 11:46:55
2869	325	417	12	77	3	2008-07-07 11:46:55	2008-07-07 11:46:55
2870	323	417	11	38	4	2008-07-07 11:46:55	2008-07-07 11:46:55
2871	324	417	11	38	4	2008-07-07 11:46:55	2008-07-07 11:46:55
2872	325	417	11	38.5	4	2008-07-07 11:46:55	2008-07-07 11:46:55
2873	333	427	155	76	1	2008-07-07 11:47:07	2008-07-07 11:47:07
2874	333	427	156	76	2	2008-07-07 11:47:07	2008-07-07 11:47:07
2875	333	427	154	77	3	2008-07-07 11:47:07	2008-07-07 11:47:07
2876	333	427	155	39	4	2008-07-07 11:47:07	2008-07-07 11:47:07
2877	333	426	217	75	1	2008-07-07 11:47:07	2008-07-07 11:47:07
2878	333	426	218	76	2	2008-07-07 11:47:07	2008-07-07 11:47:07
2879	333	426	219	77	3	2008-07-07 11:47:07	2008-07-07 11:47:07
2880	333	426	217	38.5	4	2008-07-07 11:47:07	2008-07-07 11:47:07
2881	356	456	57	75	1	2008-07-07 11:47:36	2008-07-07 11:47:36
2882	357	456	57	77	1	2008-07-07 11:47:36	2008-07-07 11:47:36
2883	355	456	57	74	1	2008-07-07 11:47:36	2008-07-07 11:47:36
2884	356	456	56	74	2	2008-07-07 11:47:36	2008-07-07 11:47:36
2885	357	456	56	75	2	2008-07-07 11:47:36	2008-07-07 11:47:36
2886	355	456	56	72	2	2008-07-07 11:47:36	2008-07-07 11:47:36
2887	356	456	55	74	3	2008-07-07 11:47:36	2008-07-07 11:47:36
2888	357	456	55	76	3	2008-07-07 11:47:36	2008-07-07 11:47:36
2889	355	456	55	73	3	2008-07-07 11:47:36	2008-07-07 11:47:36
2890	356	456	57	37	4	2008-07-07 11:47:36	2008-07-07 11:47:36
2891	357	456	57	38	4	2008-07-07 11:47:36	2008-07-07 11:47:36
2892	355	456	57	36.5	4	2008-07-07 11:47:36	2008-07-07 11:47:36
2893	356	457	202	76	1	2008-07-07 11:47:36	2008-07-07 11:47:36
2894	357	457	202	77	1	2008-07-07 11:47:36	2008-07-07 11:47:36
2895	355	457	202	75	1	2008-07-07 11:47:36	2008-07-07 11:47:36
2896	356	457	203	77	2	2008-07-07 11:47:36	2008-07-07 11:47:36
2897	357	457	203	76	2	2008-07-07 11:47:36	2008-07-07 11:47:36
2898	355	457	203	75	2	2008-07-07 11:47:36	2008-07-07 11:47:36
2899	356	457	204	76	3	2008-07-07 11:47:36	2008-07-07 11:47:36
2900	357	457	204	76	3	2008-07-07 11:47:36	2008-07-07 11:47:36
2901	355	457	204	75	3	2008-07-07 11:47:36	2008-07-07 11:47:36
2902	356	457	202	37	4	2008-07-07 11:47:36	2008-07-07 11:47:36
2903	357	457	202	38	4	2008-07-07 11:47:36	2008-07-07 11:47:36
2904	355	457	202	37.5	4	2008-07-07 11:47:36	2008-07-07 11:47:36
2905	361	460	4	74	1	2008-07-07 11:49:32	2008-07-07 11:49:32
2906	362	460	4	75	1	2008-07-07 11:49:32	2008-07-07 11:49:32
2907	363	460	4	75	1	2008-07-07 11:49:32	2008-07-07 11:49:32
2908	361	460	5	73	2	2008-07-07 11:49:32	2008-07-07 11:49:32
2909	362	460	5	76	2	2008-07-07 11:49:32	2008-07-07 11:49:32
2910	363	460	5	74	2	2008-07-07 11:49:32	2008-07-07 11:49:32
2911	361	460	6	73	3	2008-07-07 11:49:32	2008-07-07 11:49:32
2912	362	460	6	77	3	2008-07-07 11:49:32	2008-07-07 11:49:32
2913	363	460	6	76	3	2008-07-07 11:49:32	2008-07-07 11:49:32
2914	361	460	4	37.5	4	2008-07-07 11:49:32	2008-07-07 11:49:32
2915	362	460	4	37	4	2008-07-07 11:49:32	2008-07-07 11:49:32
2916	363	460	4	37.5	4	2008-07-07 11:49:32	2008-07-07 11:49:32
2917	361	461	207	75	1	2008-07-07 11:49:32	2008-07-07 11:49:32
2918	362	461	207	75	1	2008-07-07 11:49:32	2008-07-07 11:49:32
2919	363	461	207	76	1	2008-07-07 11:49:32	2008-07-07 11:49:32
2920	361	461	205	74	2	2008-07-07 11:49:32	2008-07-07 11:49:32
2921	362	461	205	74	2	2008-07-07 11:49:32	2008-07-07 11:49:32
2922	363	461	205	75	2	2008-07-07 11:49:32	2008-07-07 11:49:32
2923	361	461	206	76	3	2008-07-07 11:49:32	2008-07-07 11:49:32
2924	362	461	206	78	3	2008-07-07 11:49:32	2008-07-07 11:49:32
2925	363	461	206	77	3	2008-07-07 11:49:32	2008-07-07 11:49:32
2926	361	461	207	37.5	4	2008-07-07 11:49:32	2008-07-07 11:49:32
2927	362	461	207	37.5	4	2008-07-07 11:49:32	2008-07-07 11:49:32
2928	363	461	207	38.5	4	2008-07-07 11:49:32	2008-07-07 11:49:32
2929	312	398	211	78	1	2008-07-07 11:49:43	2008-07-07 11:49:43
2930	313	398	211	77	1	2008-07-07 11:49:43	2008-07-07 11:49:43
2931	314	398	211	77	1	2008-07-07 11:49:43	2008-07-07 11:49:43
2932	312	398	212	77	2	2008-07-07 11:49:43	2008-07-07 11:49:43
2933	313	398	212	76	2	2008-07-07 11:49:43	2008-07-07 11:49:43
2934	314	398	212	76	2	2008-07-07 11:49:43	2008-07-07 11:49:43
2935	312	398	213	77	3	2008-07-07 11:49:43	2008-07-07 11:49:43
2936	313	398	213	77	3	2008-07-07 11:49:43	2008-07-07 11:49:43
2937	314	398	213	77	3	2008-07-07 11:49:43	2008-07-07 11:49:43
2938	312	398	211	39	4	2008-07-07 11:49:43	2008-07-07 11:49:43
2939	313	398	211	38.5	4	2008-07-07 11:49:43	2008-07-07 11:49:43
2940	314	398	211	38	4	2008-07-07 11:49:43	2008-07-07 11:49:43
2941	312	399	173	79	1	2008-07-07 11:49:43	2008-07-07 11:49:43
2942	313	399	173	77	1	2008-07-07 11:49:43	2008-07-07 11:49:43
2943	314	399	173	78	1	2008-07-07 11:49:43	2008-07-07 11:49:43
2944	312	399	174	79	2	2008-07-07 11:49:43	2008-07-07 11:49:43
2945	313	399	174	76	2	2008-07-07 11:49:43	2008-07-07 11:49:43
2946	314	399	174	77	2	2008-07-07 11:49:43	2008-07-07 11:49:43
2947	312	399	172	77	3	2008-07-07 11:49:43	2008-07-07 11:49:43
2948	313	399	172	76	3	2008-07-07 11:49:43	2008-07-07 11:49:43
2949	314	399	172	78	3	2008-07-07 11:49:43	2008-07-07 11:49:43
2950	312	399	173	39	4	2008-07-07 11:49:43	2008-07-07 11:49:43
2951	313	399	173	38	4	2008-07-07 11:49:43	2008-07-07 11:49:43
2952	314	399	173	38.5	4	2008-07-07 11:49:43	2008-07-07 11:49:43
2953	364	462	193	75	1	2008-07-07 11:49:52	2008-07-07 11:49:52
2954	365	462	193	71	1	2008-07-07 11:49:52	2008-07-07 11:49:52
2955	366	462	193	74	1	2008-07-07 11:49:52	2008-07-07 11:49:52
2956	364	462	194	76	2	2008-07-07 11:49:52	2008-07-07 11:49:52
2957	365	462	194	71	2	2008-07-07 11:49:52	2008-07-07 11:49:52
2958	366	462	194	75	2	2008-07-07 11:49:52	2008-07-07 11:49:52
2959	364	462	195	77	3	2008-07-07 11:49:52	2008-07-07 11:49:52
2960	365	462	195	74	3	2008-07-07 11:49:52	2008-07-07 11:49:52
2961	366	462	195	76	3	2008-07-07 11:49:52	2008-07-07 11:49:52
2962	364	462	194	37	4	2008-07-07 11:49:52	2008-07-07 11:49:52
2963	365	462	194	36	4	2008-07-07 11:49:52	2008-07-07 11:49:52
2964	366	462	194	37.5	4	2008-07-07 11:49:52	2008-07-07 11:49:52
2965	364	463	24	76	1	2008-07-07 11:49:52	2008-07-07 11:49:52
2966	365	463	24	72	1	2008-07-07 11:49:52	2008-07-07 11:49:52
2967	366	463	24	75	1	2008-07-07 11:49:52	2008-07-07 11:49:52
2968	364	463	22	77	2	2008-07-07 11:49:52	2008-07-07 11:49:52
2969	365	463	22	70	2	2008-07-07 11:49:52	2008-07-07 11:49:52
2970	366	463	22	74	2	2008-07-07 11:49:52	2008-07-07 11:49:52
2971	364	463	23	77	3	2008-07-07 11:49:52	2008-07-07 11:49:52
2972	365	463	23	70	3	2008-07-07 11:49:52	2008-07-07 11:49:52
2973	366	463	23	74	3	2008-07-07 11:49:52	2008-07-07 11:49:52
2974	364	463	24	38.5	4	2008-07-07 11:49:52	2008-07-07 11:49:52
2975	365	463	24	35	4	2008-07-07 11:49:52	2008-07-07 11:49:52
2976	366	463	24	37	4	2008-07-07 11:49:52	2008-07-07 11:49:52
2977	353	454	139	75	1	2008-07-07 11:50:46	2008-07-07 11:50:46
2978	354	454	139	75	1	2008-07-07 11:50:46	2008-07-07 11:50:46
2979	352	454	139	77	1	2008-07-07 11:50:46	2008-07-07 11:50:46
2980	353	454	141	74	2	2008-07-07 11:50:46	2008-07-07 11:50:46
2981	354	454	141	76	2	2008-07-07 11:50:46	2008-07-07 11:50:46
2982	352	454	141	76	2	2008-07-07 11:50:46	2008-07-07 11:50:46
2983	353	454	140	74	3	2008-07-07 11:50:46	2008-07-07 11:50:46
2984	354	454	140	75	3	2008-07-07 11:50:46	2008-07-07 11:50:46
2985	352	454	140	76	3	2008-07-07 11:50:46	2008-07-07 11:50:46
2986	353	454	139	37	4	2008-07-07 11:50:46	2008-07-07 11:50:46
2987	354	454	139	37.5	4	2008-07-07 11:50:46	2008-07-07 11:50:46
2988	352	454	139	38.5	4	2008-07-07 11:50:46	2008-07-07 11:50:46
2989	353	455	35	73	1	2008-07-07 11:50:46	2008-07-07 11:50:46
2990	354	455	35	76	1	2008-07-07 11:50:46	2008-07-07 11:50:46
2991	352	455	35	77	1	2008-07-07 11:50:46	2008-07-07 11:50:46
2992	353	455	36	74	2	2008-07-07 11:50:46	2008-07-07 11:50:46
2993	354	455	36	76	2	2008-07-07 11:50:46	2008-07-07 11:50:46
2994	352	455	36	77	2	2008-07-07 11:50:46	2008-07-07 11:50:46
2995	353	455	34	74	3	2008-07-07 11:50:46	2008-07-07 11:50:46
2996	354	455	34	76	3	2008-07-07 11:50:46	2008-07-07 11:50:46
2997	352	455	34	77	3	2008-07-07 11:50:46	2008-07-07 11:50:46
2998	353	455	35	36	4	2008-07-07 11:50:46	2008-07-07 11:50:46
2999	354	455	35	37	4	2008-07-07 11:50:46	2008-07-07 11:50:46
3000	352	455	35	38	4	2008-07-07 11:50:46	2008-07-07 11:50:46
3001	370	466	138	75	1	2008-07-07 11:51:47	2008-07-07 11:51:47
3002	371	466	138	74	1	2008-07-07 11:51:47	2008-07-07 11:51:47
3003	372	466	138	76	1	2008-07-07 11:51:47	2008-07-07 11:51:47
3004	370	466	136	76	2	2008-07-07 11:51:47	2008-07-07 11:51:47
3005	371	466	136	76	2	2008-07-07 11:51:47	2008-07-07 11:51:47
3006	372	466	136	76	2	2008-07-07 11:51:47	2008-07-07 11:51:47
3007	370	466	137	75	3	2008-07-07 11:51:47	2008-07-07 11:51:47
3008	371	466	137	75	3	2008-07-07 11:51:47	2008-07-07 11:51:47
3009	372	466	137	74	3	2008-07-07 11:51:47	2008-07-07 11:51:47
3010	370	466	138	37.5	4	2008-07-07 11:51:47	2008-07-07 11:51:47
3011	371	466	138	38.5	4	2008-07-07 11:51:47	2008-07-07 11:51:47
3012	372	466	138	35	4	2008-07-07 11:51:47	2008-07-07 11:51:47
3013	370	467	87	74	1	2008-07-07 11:51:47	2008-07-07 11:51:47
3014	371	467	87	73	1	2008-07-07 11:51:47	2008-07-07 11:51:47
3015	372	467	87	74	1	2008-07-07 11:51:47	2008-07-07 11:51:47
3016	370	467	86	73	2	2008-07-07 11:51:47	2008-07-07 11:51:47
3017	371	467	86	75	2	2008-07-07 11:51:47	2008-07-07 11:51:47
3018	372	467	86	75	2	2008-07-07 11:51:47	2008-07-07 11:51:47
3019	370	467	85	73	3	2008-07-07 11:51:47	2008-07-07 11:51:47
3020	371	467	85	74	3	2008-07-07 11:51:47	2008-07-07 11:51:47
3021	372	467	85	73	3	2008-07-07 11:51:47	2008-07-07 11:51:47
3022	370	467	86	37.5	4	2008-07-07 11:51:47	2008-07-07 11:51:47
3023	371	467	86	37.5	4	2008-07-07 11:51:47	2008-07-07 11:51:47
3024	372	467	86	35	4	2008-07-07 11:51:47	2008-07-07 11:51:47
3025	373	468	39	73	1	2008-07-07 11:52:04	2008-07-07 11:52:04
3026	374	468	39	74	1	2008-07-07 11:52:04	2008-07-07 11:52:04
3027	375	468	39	71	1	2008-07-07 11:52:04	2008-07-07 11:52:04
3028	373	468	37	72	2	2008-07-07 11:52:04	2008-07-07 11:52:04
3029	374	468	37	74	2	2008-07-07 11:52:04	2008-07-07 11:52:04
3030	375	468	37	72	2	2008-07-07 11:52:04	2008-07-07 11:52:04
3031	373	468	38	72	3	2008-07-07 11:52:04	2008-07-07 11:52:04
3032	374	468	38	74	3	2008-07-07 11:52:04	2008-07-07 11:52:04
3033	375	468	38	71	3	2008-07-07 11:52:04	2008-07-07 11:52:04
3034	373	468	39	36.5	4	2008-07-07 11:52:04	2008-07-07 11:52:04
3035	374	468	39	36.5	4	2008-07-07 11:52:04	2008-07-07 11:52:04
3036	375	468	39	36	4	2008-07-07 11:52:04	2008-07-07 11:52:04
3037	373	469	42	72	1	2008-07-07 11:52:04	2008-07-07 11:52:04
3038	374	469	42	72	1	2008-07-07 11:52:04	2008-07-07 11:52:04
3039	375	469	42	71	1	2008-07-07 11:52:04	2008-07-07 11:52:04
3040	373	469	40	72	2	2008-07-07 11:52:04	2008-07-07 11:52:04
3041	374	469	40	74	2	2008-07-07 11:52:04	2008-07-07 11:52:04
3042	375	469	40	73	2	2008-07-07 11:52:04	2008-07-07 11:52:04
3043	373	469	41	72	3	2008-07-07 11:52:04	2008-07-07 11:52:04
3044	374	469	41	73	3	2008-07-07 11:52:04	2008-07-07 11:52:04
3045	375	469	41	69	3	2008-07-07 11:52:04	2008-07-07 11:52:04
3046	373	469	40	36.5	4	2008-07-07 11:52:04	2008-07-07 11:52:04
3047	374	469	40	36	4	2008-07-07 11:52:04	2008-07-07 11:52:04
3048	375	469	40	35	4	2008-07-07 11:52:04	2008-07-07 11:52:04
3049	367	464	82	74	1	2008-07-07 11:53:15	2008-07-07 11:53:15
3050	368	464	82	71	1	2008-07-07 11:53:15	2008-07-07 11:53:15
3051	369	464	82	75	1	2008-07-07 11:53:15	2008-07-07 11:53:15
3052	367	464	84	72	2	2008-07-07 11:53:15	2008-07-07 11:53:15
3053	368	464	84	72	2	2008-07-07 11:53:15	2008-07-07 11:53:15
3054	369	464	84	76	2	2008-07-07 11:53:15	2008-07-07 11:53:15
3055	367	464	83	73	3	2008-07-07 11:53:15	2008-07-07 11:53:15
3056	368	464	83	72	3	2008-07-07 11:53:15	2008-07-07 11:53:15
3057	369	464	83	74	3	2008-07-07 11:53:15	2008-07-07 11:53:15
3058	367	464	82	36.5	4	2008-07-07 11:53:15	2008-07-07 11:53:15
3059	368	464	82	35	4	2008-07-07 11:53:15	2008-07-07 11:53:15
3060	369	464	82	35	4	2008-07-07 11:53:15	2008-07-07 11:53:15
3061	367	465	3	72	1	2008-07-07 11:53:15	2008-07-07 11:53:15
3062	368	465	3	74	1	2008-07-07 11:53:15	2008-07-07 11:53:15
3063	369	465	3	76	1	2008-07-07 11:53:15	2008-07-07 11:53:15
3064	367	465	2	75	2	2008-07-07 11:53:15	2008-07-07 11:53:15
3065	368	465	2	76	2	2008-07-07 11:53:15	2008-07-07 11:53:15
3066	369	465	2	77	2	2008-07-07 11:53:15	2008-07-07 11:53:15
3067	367	465	1	75	3	2008-07-07 11:53:15	2008-07-07 11:53:15
3068	368	465	1	75	3	2008-07-07 11:53:15	2008-07-07 11:53:15
3069	369	465	1	76	3	2008-07-07 11:53:15	2008-07-07 11:53:15
3070	367	465	3	38.5	4	2008-07-07 11:53:15	2008-07-07 11:53:15
3071	368	465	3	37	4	2008-07-07 11:53:15	2008-07-07 11:53:15
3072	369	465	3	36	4	2008-07-07 11:53:15	2008-07-07 11:53:15
3073	326	422	58	74	1	2008-07-07 11:53:39	2008-07-07 11:53:39
3074	327	422	58	75	1	2008-07-07 11:53:39	2008-07-07 11:53:39
3075	328	422	58	76	1	2008-07-07 11:53:39	2008-07-07 11:53:39
3076	326	422	59	76	2	2008-07-07 11:53:39	2008-07-07 11:53:39
3077	327	422	59	75	2	2008-07-07 11:53:39	2008-07-07 11:53:39
3078	328	422	59	75	2	2008-07-07 11:53:39	2008-07-07 11:53:39
3079	326	422	60	74	3	2008-07-07 11:53:39	2008-07-07 11:53:39
3080	327	422	60	76	3	2008-07-07 11:53:39	2008-07-07 11:53:39
3081	328	422	60	75	3	2008-07-07 11:53:39	2008-07-07 11:53:39
3082	326	422	58	37.5	4	2008-07-07 11:53:39	2008-07-07 11:53:39
3083	327	422	58	37	4	2008-07-07 11:53:39	2008-07-07 11:53:39
3084	328	422	58	37.5	4	2008-07-07 11:53:39	2008-07-07 11:53:39
3085	326	423	130	76	1	2008-07-07 11:53:39	2008-07-07 11:53:39
3086	327	423	130	76	1	2008-07-07 11:53:39	2008-07-07 11:53:39
3087	328	423	130	76	1	2008-07-07 11:53:39	2008-07-07 11:53:39
3088	326	423	131	74	2	2008-07-07 11:53:39	2008-07-07 11:53:39
3089	327	423	131	75	2	2008-07-07 11:53:39	2008-07-07 11:53:39
3090	328	423	131	76	2	2008-07-07 11:53:39	2008-07-07 11:53:39
3091	326	423	132	76	3	2008-07-07 11:53:39	2008-07-07 11:53:39
3092	327	423	132	77	3	2008-07-07 11:53:39	2008-07-07 11:53:39
3093	328	423	132	77	3	2008-07-07 11:53:39	2008-07-07 11:53:39
3094	326	423	130	37.5	4	2008-07-07 11:53:39	2008-07-07 11:53:39
3095	327	423	130	37	4	2008-07-07 11:53:39	2008-07-07 11:53:39
3096	328	423	130	37.5	4	2008-07-07 11:53:39	2008-07-07 11:53:39
3100	358	458	209	75	1	2008-07-07 11:57:28	2008-07-07 11:57:28
3101	359	458	209	73	1	2008-07-07 11:57:28	2008-07-07 11:57:28
3102	360	458	209	72	1	2008-07-07 11:57:28	2008-07-07 11:57:28
3103	358	458	208	73	2	2008-07-07 11:57:28	2008-07-07 11:57:28
3104	359	458	208	74	2	2008-07-07 11:57:28	2008-07-07 11:57:28
3105	360	458	208	72	2	2008-07-07 11:57:28	2008-07-07 11:57:28
3106	358	458	210	72	3	2008-07-07 11:57:28	2008-07-07 11:57:28
3107	359	458	210	72	3	2008-07-07 11:57:28	2008-07-07 11:57:28
3108	360	458	210	71	3	2008-07-07 11:57:28	2008-07-07 11:57:28
3109	358	458	209	34	4	2008-07-07 11:57:28	2008-07-07 11:57:28
3110	359	458	209	37.5	4	2008-07-07 11:57:28	2008-07-07 11:57:28
3111	360	458	209	36	4	2008-07-07 11:57:28	2008-07-07 11:57:28
3112	358	459	64	74	1	2008-07-07 11:57:28	2008-07-07 11:57:28
3113	359	459	64	74	1	2008-07-07 11:57:28	2008-07-07 11:57:28
3114	360	459	64	72	1	2008-07-07 11:57:28	2008-07-07 11:57:28
3115	358	459	65	74	2	2008-07-07 11:57:28	2008-07-07 11:57:28
3116	359	459	65	75	2	2008-07-07 11:57:28	2008-07-07 11:57:28
3117	360	459	65	72	2	2008-07-07 11:57:28	2008-07-07 11:57:28
3118	358	459	66	75	3	2008-07-07 11:57:28	2008-07-07 11:57:28
3119	359	459	66	75	3	2008-07-07 11:57:28	2008-07-07 11:57:28
3120	360	459	66	73	3	2008-07-07 11:57:28	2008-07-07 11:57:28
3121	358	459	64	35	4	2008-07-07 11:57:28	2008-07-07 11:57:28
3122	359	459	64	37.5	4	2008-07-07 11:57:28	2008-07-07 11:57:28
3123	360	459	64	36	4	2008-07-07 11:57:28	2008-07-07 11:57:28
3124	507	567	209	73	1	2008-07-07 14:54:08	2008-07-07 14:54:08
3125	507	567	208	72	2	2008-07-07 14:54:08	2008-07-07 14:54:08
3126	507	567	210	72	3	2008-07-07 14:54:08	2008-07-07 14:54:08
3127	507	567	209	36.5	4	2008-07-07 14:54:08	2008-07-07 14:54:08
3128	507	568	40	74	1	2008-07-07 14:54:08	2008-07-07 14:54:08
3129	507	568	42	72	2	2008-07-07 14:54:08	2008-07-07 14:54:08
3130	507	568	41	72	3	2008-07-07 14:54:08	2008-07-07 14:54:08
3131	507	568	42	36	4	2008-07-07 14:54:08	2008-07-07 14:54:08
3132	452	515	201	76	1	2008-07-07 14:54:59	2008-07-07 14:54:59
3133	452	515	200	74	2	2008-07-07 14:54:59	2008-07-07 14:54:59
3134	452	515	199	75	3	2008-07-07 14:54:59	2008-07-07 14:54:59
3135	452	515	201	38	4	2008-07-07 14:54:59	2008-07-07 14:54:59
3136	452	516	108	75	1	2008-07-07 14:54:59	2008-07-07 14:54:59
3137	452	516	107	74	2	2008-07-07 14:54:59	2008-07-07 14:54:59
3138	452	516	106	74	3	2008-07-07 14:54:59	2008-07-07 14:54:59
3139	452	516	108	37	4	2008-07-07 14:54:59	2008-07-07 14:54:59
3140	449	519	185	76	1	2008-07-07 14:55:50	2008-07-07 14:55:50
3141	449	519	184	75	2	2008-07-07 14:55:50	2008-07-07 14:55:50
3142	449	519	186	77	3	2008-07-07 14:55:50	2008-07-07 14:55:50
3143	449	519	185	37	4	2008-07-07 14:55:50	2008-07-07 14:55:50
3144	449	520	111	76	1	2008-07-07 14:55:50	2008-07-07 14:55:50
3145	449	520	109	75	2	2008-07-07 14:55:50	2008-07-07 14:55:50
3146	449	520	110	76	3	2008-07-07 14:55:50	2008-07-07 14:55:50
3147	449	520	111	37	4	2008-07-07 14:55:50	2008-07-07 14:55:50
3148	506	565	24	76	1	2008-07-07 14:57:44	2008-07-07 14:57:44
3149	506	565	22	77	2	2008-07-07 14:57:44	2008-07-07 14:57:44
3150	506	565	23	76	3	2008-07-07 14:57:44	2008-07-07 14:57:44
3151	506	565	24	38	4	2008-07-07 14:57:44	2008-07-07 14:57:44
3152	506	566	39	74	1	2008-07-07 14:57:44	2008-07-07 14:57:44
3153	506	566	37	76	2	2008-07-07 14:57:44	2008-07-07 14:57:44
3154	506	566	38	76	3	2008-07-07 14:57:44	2008-07-07 14:57:44
3155	506	566	39	37	4	2008-07-07 14:57:44	2008-07-07 14:57:44
3156	446	511	142	74	1	2008-07-07 14:58:40	2008-07-07 14:58:40
3157	446	511	144	76	2	2008-07-07 14:58:40	2008-07-07 14:58:40
3158	446	511	143	77	3	2008-07-07 14:58:40	2008-07-07 14:58:40
3159	446	511	144	37.5	4	2008-07-07 14:58:40	2008-07-07 14:58:40
3160	446	512	129	76	1	2008-07-07 14:58:40	2008-07-07 14:58:40
3161	446	512	128	77	2	2008-07-07 14:58:40	2008-07-07 14:58:40
3162	446	512	127	76	3	2008-07-07 14:58:40	2008-07-07 14:58:40
3163	446	512	129	37.5	4	2008-07-07 14:58:40	2008-07-07 14:58:40
3164	450	517	93	75	1	2008-07-07 14:59:51	2008-07-07 14:59:51
3165	450	517	92	75	2	2008-07-07 14:59:51	2008-07-07 14:59:51
3166	450	517	91	75	3	2008-07-07 14:59:51	2008-07-07 14:59:51
3167	450	517	93	37	4	2008-07-07 14:59:51	2008-07-07 14:59:51
3168	450	518	215	77	1	2008-07-07 14:59:51	2008-07-07 14:59:51
3169	450	518	214	76	2	2008-07-07 14:59:52	2008-07-07 14:59:52
3170	450	518	216	77	3	2008-07-07 14:59:52	2008-07-07 14:59:52
3171	450	518	215	37	4	2008-07-07 14:59:52	2008-07-07 14:59:52
3172	460	521	21	75	1	2008-07-07 15:00:18	2008-07-07 15:00:18
3173	460	521	19	76	2	2008-07-07 15:00:18	2008-07-07 15:00:18
3174	460	521	20	76	3	2008-07-07 15:00:18	2008-07-07 15:00:18
3175	460	521	21	36.5	4	2008-07-07 15:00:18	2008-07-07 15:00:18
3176	460	522	119	77	1	2008-07-07 15:00:18	2008-07-07 15:00:18
3177	460	522	120	75	2	2008-07-07 15:00:18	2008-07-07 15:00:18
3178	460	522	118	76	3	2008-07-07 15:00:18	2008-07-07 15:00:18
3179	460	522	119	37.5	4	2008-07-07 15:00:18	2008-07-07 15:00:18
3180	504	561	57	75	1	2008-07-07 15:00:45	2008-07-07 15:00:45
3181	504	561	56	73	2	2008-07-07 15:00:45	2008-07-07 15:00:45
3182	504	561	55	74	3	2008-07-07 15:00:45	2008-07-07 15:00:45
3183	504	561	57	35	4	2008-07-07 15:00:45	2008-07-07 15:00:45
3184	504	562	82	74	1	2008-07-07 15:00:45	2008-07-07 15:00:45
3185	504	562	84	72	2	2008-07-07 15:00:45	2008-07-07 15:00:45
3186	504	562	83	73	3	2008-07-07 15:00:45	2008-07-07 15:00:45
3187	504	562	82	34	4	2008-07-07 15:00:45	2008-07-07 15:00:45
3188	503	559	52	75	1	2008-07-07 15:01:14	2008-07-07 15:01:14
3189	503	559	53	75	2	2008-07-07 15:01:14	2008-07-07 15:01:14
3190	503	559	54	78	3	2008-07-07 15:01:14	2008-07-07 15:01:14
3191	503	559	52	38.5	4	2008-07-07 15:01:14	2008-07-07 15:01:14
3192	503	560	194	76	1	2008-07-07 15:01:14	2008-07-07 15:01:14
3193	503	560	193	75	2	2008-07-07 15:01:14	2008-07-07 15:01:14
3194	503	560	195	74	3	2008-07-07 15:01:14	2008-07-07 15:01:14
3195	503	560	194	37	4	2008-07-07 15:01:14	2008-07-07 15:01:14
3196	443	499	89	76	1	2008-07-07 15:01:38	2008-07-07 15:01:38
3197	443	499	88	76	2	2008-07-07 15:01:38	2008-07-07 15:01:38
3198	443	499	90	77	3	2008-07-07 15:01:38	2008-07-07 15:01:38
3199	443	499	89	38	4	2008-07-07 15:01:38	2008-07-07 15:01:38
3200	443	500	181	75	1	2008-07-07 15:01:38	2008-07-07 15:01:38
3201	443	500	183	76	2	2008-07-07 15:01:38	2008-07-07 15:01:38
3202	443	500	182	75	3	2008-07-07 15:01:38	2008-07-07 15:01:38
3203	443	500	181	37.5	4	2008-07-07 15:01:38	2008-07-07 15:01:38
3204	456	523	133	74	1	2008-07-07 15:02:10	2008-07-07 15:02:10
3205	456	523	134	76	2	2008-07-07 15:02:10	2008-07-07 15:02:10
3206	456	523	135	73	3	2008-07-07 15:02:10	2008-07-07 15:02:10
3207	456	523	133	37.5	4	2008-07-07 15:02:10	2008-07-07 15:02:10
3208	456	524	73	73	1	2008-07-07 15:02:10	2008-07-07 15:02:10
3209	456	524	74	72	2	2008-07-07 15:02:10	2008-07-07 15:02:10
3210	456	524	75	75	3	2008-07-07 15:02:10	2008-07-07 15:02:10
3211	456	524	73	38.5	4	2008-07-07 15:02:10	2008-07-07 15:02:10
3212	451	513	101	76	1	2008-07-07 15:02:56	2008-07-07 15:02:56
3213	451	513	102	77	2	2008-07-07 15:02:56	2008-07-07 15:02:56
3214	451	513	100	76	3	2008-07-07 15:02:56	2008-07-07 15:02:56
3215	451	513	101	38	4	2008-07-07 15:02:56	2008-07-07 15:02:56
3216	451	514	43	76	1	2008-07-07 15:02:56	2008-07-07 15:02:56
3217	451	514	45	76	2	2008-07-07 15:02:56	2008-07-07 15:02:56
3218	451	514	44	77	3	2008-07-07 15:02:56	2008-07-07 15:02:56
3219	451	514	43	37.5	4	2008-07-07 15:02:56	2008-07-07 15:02:56
3220	441	501	158	79	1	2008-07-07 15:03:04	2008-07-07 15:03:04
3221	441	501	159	77	2	2008-07-07 15:03:04	2008-07-07 15:03:04
3222	441	501	157	77	3	2008-07-07 15:03:04	2008-07-07 15:03:04
3223	441	501	158	38.5	4	2008-07-07 15:03:04	2008-07-07 15:03:04
3224	441	502	175	77	1	2008-07-07 15:03:04	2008-07-07 15:03:04
3225	441	502	177	76	2	2008-07-07 15:03:04	2008-07-07 15:03:04
3226	441	502	176	78	3	2008-07-07 15:03:04	2008-07-07 15:03:04
3227	441	502	175	39	4	2008-07-07 15:03:04	2008-07-07 15:03:04
3228	445	503	211	76	1	2008-07-07 15:03:48	2008-07-07 15:03:48
3229	445	503	212	77	2	2008-07-07 15:03:48	2008-07-07 15:03:48
3230	445	503	213	77	3	2008-07-07 15:03:48	2008-07-07 15:03:48
3231	445	503	211	38.5	4	2008-07-07 15:03:48	2008-07-07 15:03:48
3232	445	504	155	76	1	2008-07-07 15:03:48	2008-07-07 15:03:48
3233	445	504	156	76	2	2008-07-07 15:03:48	2008-07-07 15:03:48
3234	445	504	154	75	3	2008-07-07 15:03:48	2008-07-07 15:03:48
3235	445	504	156	37	4	2008-07-07 15:03:48	2008-07-07 15:03:48
3236	457	529	126	76	1	2008-07-07 15:05:07	2008-07-07 15:05:07
3237	457	529	124	76	2	2008-07-07 15:05:07	2008-07-07 15:05:07
3238	457	529	125	77	3	2008-07-07 15:05:07	2008-07-07 15:05:07
3239	457	529	126	38.5	4	2008-07-07 15:05:07	2008-07-07 15:05:07
3240	457	530	63	75	1	2008-07-07 15:05:07	2008-07-07 15:05:07
3241	457	530	62	77	2	2008-07-07 15:05:07	2008-07-07 15:05:07
3242	457	530	61	74	3	2008-07-07 15:05:07	2008-07-07 15:05:07
3243	457	530	63	37	4	2008-07-07 15:05:07	2008-07-07 15:05:07
3244	459	531	16	75	1	2008-07-07 15:05:51	2008-07-07 15:05:51
3245	459	531	18	76	2	2008-07-07 15:05:51	2008-07-07 15:05:51
3246	459	531	17	76	3	2008-07-07 15:05:51	2008-07-07 15:05:51
3247	459	531	16	38.5	4	2008-07-07 15:05:51	2008-07-07 15:05:51
3248	459	532	191	75	1	2008-07-07 15:05:51	2008-07-07 15:05:51
3249	459	532	192	75	2	2008-07-07 15:05:51	2008-07-07 15:05:51
3250	459	532	190	75	3	2008-07-07 15:05:51	2008-07-07 15:05:51
3251	459	532	191	38	4	2008-07-07 15:05:51	2008-07-07 15:05:51
3252	479	543	187	75	1	2008-07-07 15:10:45	2008-07-07 15:10:45
3253	480	543	187	75	1	2008-07-07 15:10:45	2008-07-07 15:10:45
3254	481	543	187	76	1	2008-07-07 15:10:45	2008-07-07 15:10:45
3255	479	543	188	75	2	2008-07-07 15:10:45	2008-07-07 15:10:45
3256	480	543	188	75	2	2008-07-07 15:10:45	2008-07-07 15:10:45
3257	481	543	188	76	2	2008-07-07 15:10:45	2008-07-07 15:10:45
3258	479	543	189	75	3	2008-07-07 15:10:45	2008-07-07 15:10:45
3259	480	543	189	75	3	2008-07-07 15:10:45	2008-07-07 15:10:45
3260	481	543	189	75	3	2008-07-07 15:10:45	2008-07-07 15:10:45
3261	479	543	187	37	4	2008-07-07 15:10:45	2008-07-07 15:10:45
3262	480	543	187	37.5	4	2008-07-07 15:10:45	2008-07-07 15:10:45
3263	481	543	187	37.5	4	2008-07-07 15:10:45	2008-07-07 15:10:45
3264	479	544	122	76	1	2008-07-07 15:10:45	2008-07-07 15:10:45
3265	480	544	122	75	1	2008-07-07 15:10:45	2008-07-07 15:10:45
3266	481	544	122	77	1	2008-07-07 15:10:45	2008-07-07 15:10:45
3267	479	544	121	76	2	2008-07-07 15:10:45	2008-07-07 15:10:45
3268	480	544	121	76	2	2008-07-07 15:10:45	2008-07-07 15:10:45
3269	481	544	121	76	2	2008-07-07 15:10:45	2008-07-07 15:10:45
3270	479	544	123	76	3	2008-07-07 15:10:45	2008-07-07 15:10:45
3271	480	544	123	76	3	2008-07-07 15:10:45	2008-07-07 15:10:45
3272	481	544	123	76	3	2008-07-07 15:10:45	2008-07-07 15:10:45
3273	479	544	122	38	4	2008-07-07 15:10:45	2008-07-07 15:10:45
3274	480	544	122	38	4	2008-07-07 15:10:45	2008-07-07 15:10:45
3275	481	544	122	38	4	2008-07-07 15:10:45	2008-07-07 15:10:45
3276	458	533	115	76	1	2008-07-07 15:11:19	2008-07-07 15:11:19
3277	458	533	116	74	2	2008-07-07 15:11:19	2008-07-07 15:11:19
3278	458	533	117	75	3	2008-07-07 15:11:19	2008-07-07 15:11:19
3279	458	533	115	35	4	2008-07-07 15:11:19	2008-07-07 15:11:19
3280	458	534	31	74	1	2008-07-07 15:11:19	2008-07-07 15:11:19
3281	458	534	33	74	2	2008-07-07 15:11:19	2008-07-07 15:11:19
3282	458	534	32	75	3	2008-07-07 15:11:19	2008-07-07 15:11:19
3283	458	534	31	34	4	2008-07-07 15:11:19	2008-07-07 15:11:19
3284	485	547	196	73	1	2008-07-07 15:12:25	2008-07-07 15:12:25
3285	486	547	196	73	1	2008-07-07 15:12:25	2008-07-07 15:12:25
3286	487	547	196	75	1	2008-07-07 15:12:25	2008-07-07 15:12:25
3287	485	547	197	74	2	2008-07-07 15:12:25	2008-07-07 15:12:25
3288	486	547	197	73	2	2008-07-07 15:12:25	2008-07-07 15:12:25
3289	487	547	197	77	2	2008-07-07 15:12:25	2008-07-07 15:12:25
3290	485	547	198	74	3	2008-07-07 15:12:25	2008-07-07 15:12:25
3291	486	547	198	74	3	2008-07-07 15:12:25	2008-07-07 15:12:25
3292	487	547	198	77	3	2008-07-07 15:12:25	2008-07-07 15:12:25
3293	485	547	197	37.5	4	2008-07-07 15:12:25	2008-07-07 15:12:25
3294	486	547	197	36	4	2008-07-07 15:12:25	2008-07-07 15:12:25
3295	487	547	197	38	4	2008-07-07 15:12:25	2008-07-07 15:12:25
3296	485	548	139	75	1	2008-07-07 15:12:25	2008-07-07 15:12:25
3297	486	548	139	74	1	2008-07-07 15:12:25	2008-07-07 15:12:25
3298	487	548	139	77	1	2008-07-07 15:12:25	2008-07-07 15:12:25
3299	485	548	140	74	2	2008-07-07 15:12:25	2008-07-07 15:12:25
3300	486	548	140	75	2	2008-07-07 15:12:25	2008-07-07 15:12:25
3301	487	548	140	76	2	2008-07-07 15:12:25	2008-07-07 15:12:25
3302	485	548	141	75	3	2008-07-07 15:12:25	2008-07-07 15:12:25
3303	486	548	141	76	3	2008-07-07 15:12:25	2008-07-07 15:12:25
3304	487	548	141	76	3	2008-07-07 15:12:25	2008-07-07 15:12:25
3305	485	548	139	38	4	2008-07-07 15:12:25	2008-07-07 15:12:25
3306	486	548	139	38	4	2008-07-07 15:12:25	2008-07-07 15:12:25
3307	487	548	139	37	4	2008-07-07 15:12:25	2008-07-07 15:12:25
3308	488	549	2	73	1	2008-07-07 15:14:19	2008-07-07 15:14:19
3309	489	549	2	75	1	2008-07-07 15:14:19	2008-07-07 15:14:19
3310	490	549	2	75	1	2008-07-07 15:14:19	2008-07-07 15:14:19
3311	488	549	3	72	2	2008-07-07 15:14:19	2008-07-07 15:14:19
3312	489	549	3	75	2	2008-07-07 15:14:19	2008-07-07 15:14:19
3313	490	549	3	75	2	2008-07-07 15:14:19	2008-07-07 15:14:19
3314	488	549	1	72	3	2008-07-07 15:14:19	2008-07-07 15:14:19
3315	489	549	1	75	3	2008-07-07 15:14:19	2008-07-07 15:14:19
3316	490	549	1	75	3	2008-07-07 15:14:19	2008-07-07 15:14:19
3317	488	549	3	36.5	4	2008-07-07 15:14:19	2008-07-07 15:14:19
3318	489	549	3	37.5	4	2008-07-07 15:14:19	2008-07-07 15:14:19
3319	490	549	3	37.5	4	2008-07-07 15:14:19	2008-07-07 15:14:19
3320	488	550	166	73	1	2008-07-07 15:14:19	2008-07-07 15:14:19
3321	489	550	166	75	1	2008-07-07 15:14:19	2008-07-07 15:14:19
3322	490	550	166	73	1	2008-07-07 15:14:19	2008-07-07 15:14:19
3323	488	550	167	72	2	2008-07-07 15:14:19	2008-07-07 15:14:19
3324	489	550	167	73	2	2008-07-07 15:14:19	2008-07-07 15:14:19
3325	490	550	167	72	2	2008-07-07 15:14:19	2008-07-07 15:14:19
3326	488	550	168	71	3	2008-07-07 15:14:19	2008-07-07 15:14:19
3327	489	550	168	73	3	2008-07-07 15:14:19	2008-07-07 15:14:19
3328	490	550	168	73	3	2008-07-07 15:14:19	2008-07-07 15:14:19
3329	488	550	166	36	4	2008-07-07 15:14:19	2008-07-07 15:14:19
3330	489	550	166	37	4	2008-07-07 15:14:19	2008-07-07 15:14:19
3331	490	550	166	37	4	2008-07-07 15:14:19	2008-07-07 15:14:19
3332	447	509	11	77	1	2008-07-07 15:14:37	2008-07-07 15:14:37
3333	447	509	10	78	2	2008-07-07 15:14:37	2008-07-07 15:14:37
3334	447	509	12	76	3	2008-07-07 15:14:37	2008-07-07 15:14:37
3335	447	509	11	38.5	4	2008-07-07 15:14:37	2008-07-07 15:14:37
3336	447	510	150	76	1	2008-07-07 15:14:37	2008-07-07 15:14:37
3337	447	510	149	77	2	2008-07-07 15:14:37	2008-07-07 15:14:37
3338	447	510	148	74	3	2008-07-07 15:14:37	2008-07-07 15:14:37
3339	447	510	150	37.5	4	2008-07-07 15:14:37	2008-07-07 15:14:37
3340	467	535	152	75	1	2008-07-07 15:14:39	2008-07-07 15:14:39
3341	468	535	152	75	1	2008-07-07 15:14:39	2008-07-07 15:14:39
3342	469	535	152	76	1	2008-07-07 15:14:39	2008-07-07 15:14:39
3343	467	535	151	76	2	2008-07-07 15:14:39	2008-07-07 15:14:39
3344	468	535	151	76	2	2008-07-07 15:14:39	2008-07-07 15:14:39
3345	469	535	151	77	2	2008-07-07 15:14:39	2008-07-07 15:14:39
3346	467	535	153	75	3	2008-07-07 15:14:39	2008-07-07 15:14:39
3347	468	535	153	76	3	2008-07-07 15:14:39	2008-07-07 15:14:39
3348	469	535	153	76	3	2008-07-07 15:14:39	2008-07-07 15:14:39
3349	467	535	151	37.5	4	2008-07-07 15:14:39	2008-07-07 15:14:39
3350	468	535	151	38	4	2008-07-07 15:14:39	2008-07-07 15:14:39
3351	469	535	151	38	4	2008-07-07 15:14:39	2008-07-07 15:14:39
3352	467	536	48	75	1	2008-07-07 15:14:39	2008-07-07 15:14:39
3353	468	536	48	75	1	2008-07-07 15:14:39	2008-07-07 15:14:39
3354	469	536	48	75	1	2008-07-07 15:14:39	2008-07-07 15:14:39
3355	467	536	46	75	2	2008-07-07 15:14:39	2008-07-07 15:14:39
3356	468	536	46	74	2	2008-07-07 15:14:39	2008-07-07 15:14:39
3357	469	536	46	76	2	2008-07-07 15:14:39	2008-07-07 15:14:39
3358	467	536	47	75	3	2008-07-07 15:14:39	2008-07-07 15:14:39
3359	468	536	47	75	3	2008-07-07 15:14:39	2008-07-07 15:14:39
3360	469	536	47	75	3	2008-07-07 15:14:39	2008-07-07 15:14:39
3361	467	536	46	37.5	4	2008-07-07 15:14:39	2008-07-07 15:14:39
3362	468	536	46	36	4	2008-07-07 15:14:39	2008-07-07 15:14:39
3363	469	536	46	37.5	4	2008-07-07 15:14:39	2008-07-07 15:14:39
3364	448	507	99	77	1	2008-07-07 15:15:55	2008-07-07 15:15:55
3365	448	507	97	76	2	2008-07-07 15:15:55	2008-07-07 15:15:55
3366	448	507	98	77	3	2008-07-07 15:15:55	2008-07-07 15:15:55
3367	448	507	99	38	4	2008-07-07 15:15:55	2008-07-07 15:15:55
3368	448	508	130	76	1	2008-07-07 15:15:55	2008-07-07 15:15:55
3369	448	508	131	75	2	2008-07-07 15:15:55	2008-07-07 15:15:55
3370	448	508	132	75	3	2008-07-07 15:15:55	2008-07-07 15:15:55
3371	448	508	130	37.5	4	2008-07-07 15:15:55	2008-07-07 15:15:55
3372	494	553	138	75	1	2008-07-07 15:16:14	2008-07-07 15:16:14
3373	495	553	138	76	1	2008-07-07 15:16:14	2008-07-07 15:16:14
3374	496	553	138	75	1	2008-07-07 15:16:14	2008-07-07 15:16:14
3375	494	553	136	74	2	2008-07-07 15:16:14	2008-07-07 15:16:14
3376	495	553	136	77	2	2008-07-07 15:16:14	2008-07-07 15:16:14
3377	496	553	136	75	2	2008-07-07 15:16:14	2008-07-07 15:16:14
3378	494	553	137	75	3	2008-07-07 15:16:14	2008-07-07 15:16:14
3379	495	553	137	76	3	2008-07-07 15:16:14	2008-07-07 15:16:14
3380	496	553	137	74	3	2008-07-07 15:16:14	2008-07-07 15:16:14
3381	494	553	138	37	4	2008-07-07 15:16:14	2008-07-07 15:16:14
3382	495	553	138	38.5	4	2008-07-07 15:16:14	2008-07-07 15:16:14
3383	496	553	138	36	4	2008-07-07 15:16:14	2008-07-07 15:16:14
3384	494	554	25	75	1	2008-07-07 15:16:14	2008-07-07 15:16:14
3385	495	554	25	76	1	2008-07-07 15:16:14	2008-07-07 15:16:14
3386	496	554	25	76	1	2008-07-07 15:16:14	2008-07-07 15:16:14
3387	494	554	26	75	2	2008-07-07 15:16:14	2008-07-07 15:16:14
3388	495	554	26	77	2	2008-07-07 15:16:14	2008-07-07 15:16:14
3389	496	554	26	76	2	2008-07-07 15:16:14	2008-07-07 15:16:14
3390	494	554	27	76	3	2008-07-07 15:16:14	2008-07-07 15:16:14
3391	495	554	27	77	3	2008-07-07 15:16:14	2008-07-07 15:16:14
3392	496	554	27	74	3	2008-07-07 15:16:14	2008-07-07 15:16:14
3393	494	554	25	37.5	4	2008-07-07 15:16:14	2008-07-07 15:16:14
3394	495	554	25	39	4	2008-07-07 15:16:14	2008-07-07 15:16:14
3395	496	554	25	37.5	4	2008-07-07 15:16:14	2008-07-07 15:16:14
3396	442	497	8	78	1	2008-07-07 15:17:11	2008-07-07 15:17:11
3397	442	497	9	79	2	2008-07-07 15:17:11	2008-07-07 15:17:11
3398	442	497	7	78	3	2008-07-07 15:17:11	2008-07-07 15:17:11
3399	442	497	9	38.5	4	2008-07-07 15:17:11	2008-07-07 15:17:11
3400	442	498	70	77	1	2008-07-07 15:17:11	2008-07-07 15:17:11
3401	442	498	71	76	2	2008-07-07 15:17:11	2008-07-07 15:17:11
3402	442	498	72	74	3	2008-07-07 15:17:11	2008-07-07 15:17:11
3403	442	498	70	38	4	2008-07-07 15:17:11	2008-07-07 15:17:11
3404	444	505	180	77	1	2008-07-07 15:17:14	2008-07-07 15:17:14
3405	444	505	178	76	2	2008-07-07 15:17:14	2008-07-07 15:17:14
3406	444	505	179	76	3	2008-07-07 15:17:14	2008-07-07 15:17:14
3407	444	505	180	39	4	2008-07-07 15:17:14	2008-07-07 15:17:14
3408	444	506	13	76	1	2008-07-07 15:17:14	2008-07-07 15:17:14
3409	444	506	14	76	2	2008-07-07 15:17:14	2008-07-07 15:17:14
3410	444	506	15	77	3	2008-07-07 15:17:14	2008-07-07 15:17:14
3411	444	506	13	38	4	2008-07-07 15:17:14	2008-07-07 15:17:14
3412	500	555	65	75	1	2008-07-07 15:18:21	2008-07-07 15:18:21
3413	501	555	65	73	1	2008-07-07 15:18:21	2008-07-07 15:18:21
3414	502	555	65	76	1	2008-07-07 15:18:21	2008-07-07 15:18:21
3415	500	555	64	75	2	2008-07-07 15:18:21	2008-07-07 15:18:21
3416	501	555	64	76	2	2008-07-07 15:18:21	2008-07-07 15:18:21
3417	502	555	64	77	2	2008-07-07 15:18:21	2008-07-07 15:18:21
3418	500	555	66	76	3	2008-07-07 15:18:21	2008-07-07 15:18:21
3419	501	555	66	78	3	2008-07-07 15:18:21	2008-07-07 15:18:21
3420	502	555	66	75	3	2008-07-07 15:18:21	2008-07-07 15:18:21
3421	500	555	64	37.5	4	2008-07-07 15:18:21	2008-07-07 15:18:21
3422	501	555	64	35	4	2008-07-07 15:18:21	2008-07-07 15:18:21
3423	502	555	64	35	4	2008-07-07 15:18:21	2008-07-07 15:18:21
3424	500	556	49	74	1	2008-07-07 15:18:21	2008-07-07 15:18:21
3425	501	556	49	73	1	2008-07-07 15:18:21	2008-07-07 15:18:21
3426	502	556	49	74	1	2008-07-07 15:18:21	2008-07-07 15:18:21
3427	500	556	51	74	2	2008-07-07 15:18:21	2008-07-07 15:18:21
3428	501	556	51	75	2	2008-07-07 15:18:21	2008-07-07 15:18:21
3429	502	556	51	75	2	2008-07-07 15:18:21	2008-07-07 15:18:21
3430	500	556	50	75	3	2008-07-07 15:18:21	2008-07-07 15:18:21
3431	501	556	50	76	3	2008-07-07 15:18:21	2008-07-07 15:18:21
3432	502	556	50	75	3	2008-07-07 15:18:21	2008-07-07 15:18:21
3433	500	556	51	36.5	4	2008-07-07 15:18:21	2008-07-07 15:18:21
3434	501	556	51	34	4	2008-07-07 15:18:21	2008-07-07 15:18:21
3435	502	556	51	35	4	2008-07-07 15:18:21	2008-07-07 15:18:21
3436	470	537	147	74	1	2008-07-07 15:19:22	2008-07-07 15:19:22
3437	471	537	147	75	1	2008-07-07 15:19:22	2008-07-07 15:19:22
3438	472	537	147	72	1	2008-07-07 15:19:22	2008-07-07 15:19:22
3439	470	537	146	74	2	2008-07-07 15:19:22	2008-07-07 15:19:22
3440	471	537	146	76	2	2008-07-07 15:19:22	2008-07-07 15:19:22
3441	472	537	146	75	2	2008-07-07 15:19:22	2008-07-07 15:19:22
3442	470	537	145	74	3	2008-07-07 15:19:22	2008-07-07 15:19:22
3443	471	537	145	75	3	2008-07-07 15:19:22	2008-07-07 15:19:22
3444	472	537	145	75	3	2008-07-07 15:19:22	2008-07-07 15:19:22
3445	470	537	146	37.5	4	2008-07-07 15:19:22	2008-07-07 15:19:22
3446	471	537	146	38	4	2008-07-07 15:19:22	2008-07-07 15:19:22
3447	472	537	146	37.5	4	2008-07-07 15:19:22	2008-07-07 15:19:22
3448	470	538	80	75	1	2008-07-07 15:19:22	2008-07-07 15:19:22
3449	471	538	80	74	1	2008-07-07 15:19:22	2008-07-07 15:19:22
3450	472	538	80	74	1	2008-07-07 15:19:22	2008-07-07 15:19:22
3451	470	538	81	74	2	2008-07-07 15:19:22	2008-07-07 15:19:22
3452	471	538	81	74	2	2008-07-07 15:19:22	2008-07-07 15:19:22
3453	472	538	81	73	2	2008-07-07 15:19:22	2008-07-07 15:19:22
3454	470	538	79	76	3	2008-07-07 15:19:22	2008-07-07 15:19:22
3455	471	538	79	74	3	2008-07-07 15:19:22	2008-07-07 15:19:22
3456	472	538	79	77	3	2008-07-07 15:19:22	2008-07-07 15:19:22
3457	470	538	80	37	4	2008-07-07 15:19:22	2008-07-07 15:19:22
3458	471	538	80	37.5	4	2008-07-07 15:19:22	2008-07-07 15:19:22
3459	472	538	80	37	4	2008-07-07 15:19:22	2008-07-07 15:19:22
3460	482	545	163	78	1	2008-07-07 15:20:28	2008-07-07 15:20:28
3461	483	545	163	73	1	2008-07-07 15:20:28	2008-07-07 15:20:28
3462	484	545	163	75	1	2008-07-07 15:20:28	2008-07-07 15:20:28
3463	482	545	164	77	2	2008-07-07 15:20:28	2008-07-07 15:20:28
3464	483	545	164	76	2	2008-07-07 15:20:28	2008-07-07 15:20:28
3465	484	545	164	76	2	2008-07-07 15:20:28	2008-07-07 15:20:28
3466	482	545	165	78	3	2008-07-07 15:20:28	2008-07-07 15:20:28
3467	483	545	165	73	3	2008-07-07 15:20:28	2008-07-07 15:20:28
3468	484	545	165	75	3	2008-07-07 15:20:28	2008-07-07 15:20:28
3469	482	545	163	38.5	4	2008-07-07 15:20:28	2008-07-07 15:20:28
3470	483	545	163	36	4	2008-07-07 15:20:28	2008-07-07 15:20:28
3471	484	545	163	37	4	2008-07-07 15:20:28	2008-07-07 15:20:28
3472	482	546	225	76	1	2008-07-07 15:20:28	2008-07-07 15:20:28
3473	483	546	225	75	1	2008-07-07 15:20:28	2008-07-07 15:20:28
3474	484	546	225	76	1	2008-07-07 15:20:28	2008-07-07 15:20:28
3475	482	546	223	77	2	2008-07-07 15:20:28	2008-07-07 15:20:28
3476	483	546	223	75	2	2008-07-07 15:20:28	2008-07-07 15:20:28
3477	484	546	223	76	2	2008-07-07 15:20:28	2008-07-07 15:20:28
3478	482	546	224	78	3	2008-07-07 15:20:28	2008-07-07 15:20:28
3479	483	546	224	74	3	2008-07-07 15:20:28	2008-07-07 15:20:28
3480	484	546	224	76	3	2008-07-07 15:20:28	2008-07-07 15:20:28
3481	482	546	225	38	4	2008-07-07 15:20:28	2008-07-07 15:20:28
3482	483	546	225	36.5	4	2008-07-07 15:20:28	2008-07-07 15:20:28
3483	484	546	225	37	4	2008-07-07 15:20:28	2008-07-07 15:20:28
3484	492	551	207	70	1	2008-07-07 15:24:51	2008-07-07 15:24:51
3485	493	551	207	73	1	2008-07-07 15:24:52	2008-07-07 15:24:52
3486	491	551	207	74	1	2008-07-07 15:24:52	2008-07-07 15:24:52
3487	492	551	205	70	2	2008-07-07 15:24:52	2008-07-07 15:24:52
3488	493	551	205	71	2	2008-07-07 15:24:52	2008-07-07 15:24:52
3489	491	551	205	73	2	2008-07-07 15:24:52	2008-07-07 15:24:52
3490	492	551	206	73	3	2008-07-07 15:24:52	2008-07-07 15:24:52
3491	493	551	206	78	3	2008-07-07 15:24:52	2008-07-07 15:24:52
3492	491	551	206	75	3	2008-07-07 15:24:52	2008-07-07 15:24:52
3493	492	551	205	35.5	4	2008-07-07 15:24:52	2008-07-07 15:24:52
3494	493	551	205	37.5	4	2008-07-07 15:24:52	2008-07-07 15:24:52
3495	491	551	205	37.5	4	2008-07-07 15:24:52	2008-07-07 15:24:52
3496	492	552	68	72	1	2008-07-07 15:24:52	2008-07-07 15:24:52
3497	493	552	68	75	1	2008-07-07 15:24:52	2008-07-07 15:24:52
3498	491	552	68	75	1	2008-07-07 15:24:52	2008-07-07 15:24:52
3499	492	552	67	73	2	2008-07-07 15:24:52	2008-07-07 15:24:52
3500	493	552	67	74	2	2008-07-07 15:24:52	2008-07-07 15:24:52
3501	491	552	67	74	2	2008-07-07 15:24:52	2008-07-07 15:24:52
3502	492	552	69	72	3	2008-07-07 15:24:52	2008-07-07 15:24:52
3503	493	552	69	73	3	2008-07-07 15:24:52	2008-07-07 15:24:52
3504	491	552	69	76	3	2008-07-07 15:24:52	2008-07-07 15:24:52
3505	492	552	68	36	4	2008-07-07 15:24:52	2008-07-07 15:24:52
3506	493	552	68	38.5	4	2008-07-07 15:24:52	2008-07-07 15:24:52
3507	491	552	68	38	4	2008-07-07 15:24:52	2008-07-07 15:24:52
3508	505	563	86	73	1	2008-07-07 15:25:13	2008-07-07 15:25:13
3509	505	563	87	73	2	2008-07-07 15:25:13	2008-07-07 15:25:13
3510	505	563	85	74	3	2008-07-07 15:25:13	2008-07-07 15:25:13
3511	505	563	86	37.5	4	2008-07-07 15:25:13	2008-07-07 15:25:13
3512	505	564	4	75	1	2008-07-07 15:25:13	2008-07-07 15:25:13
3513	505	564	5	75	2	2008-07-07 15:25:13	2008-07-07 15:25:13
3514	505	564	6	76	3	2008-07-07 15:25:13	2008-07-07 15:25:13
3515	505	564	4	37.5	4	2008-07-07 15:25:13	2008-07-07 15:25:13
3516	473	539	217	75	1	2008-07-07 15:31:14	2008-07-07 15:31:14
3517	474	539	217	75	1	2008-07-07 15:31:14	2008-07-07 15:31:14
3518	475	539	217	74	1	2008-07-07 15:31:14	2008-07-07 15:31:14
3519	473	539	218	75	2	2008-07-07 15:31:14	2008-07-07 15:31:14
3520	474	539	218	76	2	2008-07-07 15:31:14	2008-07-07 15:31:14
3521	475	539	218	74	2	2008-07-07 15:31:14	2008-07-07 15:31:14
3522	473	539	219	76	3	2008-07-07 15:31:14	2008-07-07 15:31:14
3523	474	539	219	76	3	2008-07-07 15:31:14	2008-07-07 15:31:14
3524	475	539	219	75	3	2008-07-07 15:31:14	2008-07-07 15:31:14
3525	473	539	217	37	4	2008-07-07 15:31:14	2008-07-07 15:31:14
3526	474	539	217	37.5	4	2008-07-07 15:31:14	2008-07-07 15:31:14
3527	475	539	217	37.5	4	2008-07-07 15:31:14	2008-07-07 15:31:14
3528	473	540	76	75	1	2008-07-07 15:31:14	2008-07-07 15:31:14
3529	474	540	76	77	1	2008-07-07 15:31:14	2008-07-07 15:31:14
3530	475	540	76	75	1	2008-07-07 15:31:14	2008-07-07 15:31:14
3531	473	540	77	75	2	2008-07-07 15:31:14	2008-07-07 15:31:14
3532	474	540	77	73	2	2008-07-07 15:31:14	2008-07-07 15:31:14
3533	475	540	77	74	2	2008-07-07 15:31:14	2008-07-07 15:31:14
3534	473	540	78	74	3	2008-07-07 15:31:14	2008-07-07 15:31:14
3535	474	540	78	72	3	2008-07-07 15:31:14	2008-07-07 15:31:14
3536	475	540	78	73	3	2008-07-07 15:31:14	2008-07-07 15:31:14
3537	473	540	76	37	4	2008-07-07 15:31:14	2008-07-07 15:31:14
3538	474	540	76	39	4	2008-07-07 15:31:14	2008-07-07 15:31:14
3539	475	540	76	38	4	2008-07-07 15:31:14	2008-07-07 15:31:14
3540	461	527	105	75	1	2008-07-07 15:33:25	2008-07-07 15:33:25
3541	462	527	105	76	1	2008-07-07 15:33:25	2008-07-07 15:33:25
3542	463	527	105	76	1	2008-07-07 15:33:25	2008-07-07 15:33:25
3543	461	527	104	74	2	2008-07-07 15:33:25	2008-07-07 15:33:25
3544	462	527	104	76	2	2008-07-07 15:33:25	2008-07-07 15:33:25
3545	463	527	104	75	2	2008-07-07 15:33:25	2008-07-07 15:33:25
3546	461	527	103	74	3	2008-07-07 15:33:25	2008-07-07 15:33:25
3547	462	527	103	76	3	2008-07-07 15:33:25	2008-07-07 15:33:25
3548	463	527	103	77	3	2008-07-07 15:33:25	2008-07-07 15:33:25
3549	461	527	105	38	4	2008-07-07 15:33:25	2008-07-07 15:33:25
3550	462	527	105	38	4	2008-07-07 15:33:25	2008-07-07 15:33:25
3551	463	527	105	38	4	2008-07-07 15:33:25	2008-07-07 15:33:25
3552	461	528	202	73	1	2008-07-07 15:33:25	2008-07-07 15:33:25
3553	462	528	202	75	1	2008-07-07 15:33:25	2008-07-07 15:33:25
3554	463	528	202	75	1	2008-07-07 15:33:25	2008-07-07 15:33:25
3555	461	528	203	74	2	2008-07-07 15:33:25	2008-07-07 15:33:25
3556	462	528	203	76	2	2008-07-07 15:33:25	2008-07-07 15:33:25
3557	463	528	203	75	2	2008-07-07 15:33:25	2008-07-07 15:33:25
3558	461	528	204	75	3	2008-07-07 15:33:25	2008-07-07 15:33:25
3559	462	528	204	76	3	2008-07-07 15:33:25	2008-07-07 15:33:25
3560	463	528	204	76	3	2008-07-07 15:33:25	2008-07-07 15:33:25
3561	461	528	202	37	4	2008-07-07 15:33:25	2008-07-07 15:33:25
3562	462	528	202	38	4	2008-07-07 15:33:25	2008-07-07 15:33:25
3563	463	528	202	37.5	4	2008-07-07 15:33:25	2008-07-07 15:33:25
3564	498	557	28	73	1	2008-07-07 15:33:54	2008-07-07 15:33:54
3565	499	557	28	74	1	2008-07-07 15:33:54	2008-07-07 15:33:54
3566	497	557	28	75	1	2008-07-07 15:33:54	2008-07-07 15:33:54
3567	498	557	29	73	2	2008-07-07 15:33:54	2008-07-07 15:33:54
3568	499	557	29	73	2	2008-07-07 15:33:54	2008-07-07 15:33:54
3569	497	557	29	77	2	2008-07-07 15:33:54	2008-07-07 15:33:54
3570	498	557	30	72	3	2008-07-07 15:33:54	2008-07-07 15:33:54
3571	499	557	30	72	3	2008-07-07 15:33:54	2008-07-07 15:33:54
3572	497	557	30	76	3	2008-07-07 15:33:54	2008-07-07 15:33:54
3573	498	557	29	36.5	4	2008-07-07 15:33:54	2008-07-07 15:33:54
3574	499	557	29	36	4	2008-07-07 15:33:54	2008-07-07 15:33:54
3575	497	557	29	37.5	4	2008-07-07 15:33:54	2008-07-07 15:33:54
3576	498	558	221	73	1	2008-07-07 15:33:54	2008-07-07 15:33:54
3577	499	558	221	73	1	2008-07-07 15:33:54	2008-07-07 15:33:54
3578	497	558	221	77	1	2008-07-07 15:33:54	2008-07-07 15:33:54
3579	498	558	220	74	2	2008-07-07 15:33:54	2008-07-07 15:33:54
3580	499	558	220	74	2	2008-07-07 15:33:54	2008-07-07 15:33:54
3581	497	558	220	76	2	2008-07-07 15:33:54	2008-07-07 15:33:54
3582	498	558	222	74	3	2008-07-07 15:33:54	2008-07-07 15:33:54
3583	499	558	222	74	3	2008-07-07 15:33:54	2008-07-07 15:33:54
3584	497	558	222	78	3	2008-07-07 15:33:54	2008-07-07 15:33:54
3585	498	558	220	37	4	2008-07-07 15:33:54	2008-07-07 15:33:54
3586	499	558	220	36	4	2008-07-07 15:33:54	2008-07-07 15:33:54
3587	497	558	220	38	4	2008-07-07 15:33:54	2008-07-07 15:33:54
3588	464	525	58	75	1	2008-07-07 15:35:39	2008-07-07 15:35:39
3589	465	525	58	75	1	2008-07-07 15:35:39	2008-07-07 15:35:39
3590	466	525	58	76	1	2008-07-07 15:35:39	2008-07-07 15:35:39
3591	464	525	59	74	2	2008-07-07 15:35:39	2008-07-07 15:35:39
3592	465	525	59	74	2	2008-07-07 15:35:39	2008-07-07 15:35:39
3593	466	525	59	78	2	2008-07-07 15:35:39	2008-07-07 15:35:39
3594	464	525	60	75	3	2008-07-07 15:35:39	2008-07-07 15:35:39
3595	465	525	60	76	3	2008-07-07 15:35:39	2008-07-07 15:35:39
3596	466	525	60	78	3	2008-07-07 15:35:39	2008-07-07 15:35:39
3597	464	525	58	38	4	2008-07-07 15:35:39	2008-07-07 15:35:39
3598	465	525	58	38	4	2008-07-07 15:35:39	2008-07-07 15:35:39
3599	466	525	58	38	4	2008-07-07 15:35:39	2008-07-07 15:35:39
3600	464	526	161	76	1	2008-07-07 15:35:39	2008-07-07 15:35:39
3601	465	526	161	76	1	2008-07-07 15:35:39	2008-07-07 15:35:39
3602	466	526	161	78	1	2008-07-07 15:35:39	2008-07-07 15:35:39
3603	464	526	160	76	2	2008-07-07 15:35:39	2008-07-07 15:35:39
3604	465	526	160	74	2	2008-07-07 15:35:39	2008-07-07 15:35:39
3605	466	526	160	76	2	2008-07-07 15:35:39	2008-07-07 15:35:39
3606	464	526	162	74	3	2008-07-07 15:35:39	2008-07-07 15:35:39
3607	465	526	162	74	3	2008-07-07 15:35:39	2008-07-07 15:35:39
3608	466	526	162	74	3	2008-07-07 15:35:39	2008-07-07 15:35:39
3609	464	526	161	37	4	2008-07-07 15:35:39	2008-07-07 15:35:39
3610	465	526	161	37	4	2008-07-07 15:35:40	2008-07-07 15:35:40
3611	466	526	161	37	4	2008-07-07 15:35:40	2008-07-07 15:35:40
3612	476	541	35	71	1	2008-07-07 15:36:15	2008-07-07 15:36:15
3613	477	541	35	72	1	2008-07-07 15:36:15	2008-07-07 15:36:15
3614	478	541	35	73	1	2008-07-07 15:36:15	2008-07-07 15:36:15
3615	476	541	36	71	2	2008-07-07 15:36:15	2008-07-07 15:36:15
3616	477	541	36	71	2	2008-07-07 15:36:15	2008-07-07 15:36:15
3617	478	541	36	73	2	2008-07-07 15:36:15	2008-07-07 15:36:15
3618	476	541	34	71	3	2008-07-07 15:36:15	2008-07-07 15:36:15
3619	477	541	34	73	3	2008-07-07 15:36:15	2008-07-07 15:36:15
3620	478	541	34	73	3	2008-07-07 15:36:15	2008-07-07 15:36:15
3621	476	541	35	35.5	4	2008-07-07 15:36:15	2008-07-07 15:36:15
3622	477	541	35	36.5	4	2008-07-07 15:36:15	2008-07-07 15:36:15
3623	478	541	35	36	4	2008-07-07 15:36:15	2008-07-07 15:36:15
3624	476	542	94	74	1	2008-07-07 15:36:15	2008-07-07 15:36:15
3625	477	542	94	76	1	2008-07-07 15:36:15	2008-07-07 15:36:15
3626	478	542	94	75	1	2008-07-07 15:36:15	2008-07-07 15:36:15
3627	476	542	95	73	2	2008-07-07 15:36:15	2008-07-07 15:36:15
3628	477	542	95	76	2	2008-07-07 15:36:15	2008-07-07 15:36:15
3629	478	542	95	75	2	2008-07-07 15:36:15	2008-07-07 15:36:15
3630	476	542	96	73	3	2008-07-07 15:36:15	2008-07-07 15:36:15
3631	477	542	96	74	3	2008-07-07 15:36:15	2008-07-07 15:36:15
3632	478	542	96	74	3	2008-07-07 15:36:15	2008-07-07 15:36:15
3633	476	542	94	36	4	2008-07-07 15:36:15	2008-07-07 15:36:15
3634	477	542	94	38	4	2008-07-07 15:36:15	2008-07-07 15:36:15
3635	478	542	94	38	4	2008-07-07 15:36:15	2008-07-07 15:36:15
3636	453	495	173	77	1	2008-07-07 15:36:39	2008-07-07 15:36:39
3637	454	495	173	77	1	2008-07-07 15:36:39	2008-07-07 15:36:39
3638	455	495	173	78	1	2008-07-07 15:36:39	2008-07-07 15:36:39
3639	453	495	174	77	2	2008-07-07 15:36:39	2008-07-07 15:36:39
3640	454	495	174	77	2	2008-07-07 15:36:39	2008-07-07 15:36:39
3641	455	495	174	77	2	2008-07-07 15:36:39	2008-07-07 15:36:39
3642	453	495	172	76	3	2008-07-07 15:36:39	2008-07-07 15:36:39
3643	454	495	172	76	3	2008-07-07 15:36:39	2008-07-07 15:36:39
3644	455	495	172	79	3	2008-07-07 15:36:39	2008-07-07 15:36:39
3645	453	495	173	38	4	2008-07-07 15:36:39	2008-07-07 15:36:39
3646	454	495	173	38	4	2008-07-07 15:36:39	2008-07-07 15:36:39
3647	455	495	173	38	4	2008-07-07 15:36:39	2008-07-07 15:36:39
3648	453	496	171	78	1	2008-07-07 15:36:39	2008-07-07 15:36:39
3649	454	496	171	76	1	2008-07-07 15:36:39	2008-07-07 15:36:39
3650	455	496	171	78	1	2008-07-07 15:36:39	2008-07-07 15:36:39
3651	453	496	169	77	2	2008-07-07 15:36:39	2008-07-07 15:36:39
3652	454	496	169	76	2	2008-07-07 15:36:39	2008-07-07 15:36:39
3653	455	496	169	78	2	2008-07-07 15:36:39	2008-07-07 15:36:39
3654	453	496	170	78	3	2008-07-07 15:36:39	2008-07-07 15:36:39
3655	454	496	170	77	3	2008-07-07 15:36:39	2008-07-07 15:36:39
3656	455	496	170	79	3	2008-07-07 15:36:39	2008-07-07 15:36:39
3657	453	496	169	38	4	2008-07-07 15:36:39	2008-07-07 15:36:39
3658	454	496	169	38	4	2008-07-07 15:36:39	2008-07-07 15:36:39
3659	455	496	169	38	4	2008-07-07 15:36:39	2008-07-07 15:36:39
3660	509	577	215	78	1	2008-07-07 18:25:12	2008-07-07 18:25:12
3661	509	577	214	77	2	2008-07-07 18:25:12	2008-07-07 18:25:12
3662	509	577	216	78	3	2008-07-07 18:25:12	2008-07-07 18:25:12
3663	509	577	215	39	4	2008-07-07 18:25:12	2008-07-07 18:25:12
3664	509	578	178	77	1	2008-07-07 18:25:12	2008-07-07 18:25:12
3665	509	578	180	76	2	2008-07-07 18:25:12	2008-07-07 18:25:12
3666	509	578	179	76	3	2008-07-07 18:25:12	2008-07-07 18:25:12
3667	509	578	178	38	4	2008-07-07 18:25:12	2008-07-07 18:25:12
3668	508	573	129	75	1	2008-07-07 18:26:12	2008-07-07 18:26:12
3669	508	573	128	75	2	2008-07-07 18:26:12	2008-07-07 18:26:12
3670	508	573	127	75	3	2008-07-07 18:26:12	2008-07-07 18:26:12
3671	508	573	129	37	4	2008-07-07 18:26:12	2008-07-07 18:26:12
3672	508	574	159	76	1	2008-07-07 18:26:12	2008-07-07 18:26:12
3673	508	574	158	76	2	2008-07-07 18:26:12	2008-07-07 18:26:12
3674	508	574	157	77	3	2008-07-07 18:26:12	2008-07-07 18:26:12
3675	508	574	159	37.5	4	2008-07-07 18:26:12	2008-07-07 18:26:12
3676	513	585	184	74	1	2008-07-07 18:27:40	2008-07-07 18:27:40
3677	513	585	185	76	2	2008-07-07 18:27:40	2008-07-07 18:27:40
3678	513	585	186	74	3	2008-07-07 18:27:40	2008-07-07 18:27:40
3679	513	585	185	37	4	2008-07-07 18:27:40	2008-07-07 18:27:40
3680	513	586	122	74	1	2008-07-07 18:27:40	2008-07-07 18:27:40
3681	513	586	121	75	2	2008-07-07 18:27:40	2008-07-07 18:27:40
3682	513	586	123	75	3	2008-07-07 18:27:40	2008-07-07 18:27:40
3683	513	586	121	36	4	2008-07-07 18:27:40	2008-07-07 18:27:40
3684	571	639	82	72	1	2008-07-07 18:28:50	2008-07-07 18:28:50
3685	571	639	84	71	2	2008-07-07 18:28:50	2008-07-07 18:28:50
3686	571	639	83	70	3	2008-07-07 18:28:50	2008-07-07 18:28:50
3687	571	639	82	34	4	2008-07-07 18:28:50	2008-07-07 18:28:50
3688	571	640	86	71	1	2008-07-07 18:28:50	2008-07-07 18:28:50
3689	571	640	87	72	2	2008-07-07 18:28:50	2008-07-07 18:28:50
3690	571	640	85	69	3	2008-07-07 18:28:50	2008-07-07 18:28:50
3691	571	640	86	35.5	4	2008-07-07 18:28:50	2008-07-07 18:28:50
3692	572	641	42	73	1	2008-07-07 18:29:17	2008-07-07 18:29:17
3693	572	641	40	71	2	2008-07-07 18:29:17	2008-07-07 18:29:17
3694	572	641	41	70	3	2008-07-07 18:29:17	2008-07-07 18:29:17
3695	572	641	42	36	4	2008-07-07 18:29:17	2008-07-07 18:29:17
3696	572	642	39	74	1	2008-07-07 18:29:17	2008-07-07 18:29:17
3697	572	642	37	72	2	2008-07-07 18:29:17	2008-07-07 18:29:17
3698	572	642	38	71	3	2008-07-07 18:29:17	2008-07-07 18:29:17
3699	572	642	39	37.5	4	2008-07-07 18:29:17	2008-07-07 18:29:17
3700	561	613	225	76	1	2008-07-07 18:30:17	2008-07-07 18:30:17
3701	561	613	223	75	2	2008-07-07 18:30:17	2008-07-07 18:30:17
3702	561	613	224	77	3	2008-07-07 18:30:17	2008-07-07 18:30:17
3703	561	613	225	38.5	4	2008-07-07 18:30:17	2008-07-07 18:30:17
3704	561	614	73	74	1	2008-07-07 18:30:17	2008-07-07 18:30:17
3705	561	614	74	75	2	2008-07-07 18:30:17	2008-07-07 18:30:17
3706	561	614	75	74	3	2008-07-07 18:30:17	2008-07-07 18:30:17
3707	561	614	73	37	4	2008-07-07 18:30:17	2008-07-07 18:30:17
3708	551	611	48	76	1	2008-07-07 18:32:31	2008-07-07 18:32:31
3709	552	611	48	75	1	2008-07-07 18:32:31	2008-07-07 18:32:31
3710	553	611	48	74	1	2008-07-07 18:32:31	2008-07-07 18:32:31
3711	551	611	46	76	2	2008-07-07 18:32:31	2008-07-07 18:32:31
3712	552	611	46	77	2	2008-07-07 18:32:31	2008-07-07 18:32:31
3713	553	611	46	76	2	2008-07-07 18:32:31	2008-07-07 18:32:31
3714	551	611	47	76	3	2008-07-07 18:32:31	2008-07-07 18:32:31
3715	552	611	47	76	3	2008-07-07 18:32:31	2008-07-07 18:32:31
3716	553	611	47	77	3	2008-07-07 18:32:31	2008-07-07 18:32:31
3717	551	611	46	37	4	2008-07-07 18:32:31	2008-07-07 18:32:31
3718	552	611	46	38	4	2008-07-07 18:32:31	2008-07-07 18:32:31
3719	553	611	46	35	4	2008-07-07 18:32:31	2008-07-07 18:32:31
3720	551	612	31	77	1	2008-07-07 18:32:31	2008-07-07 18:32:31
3721	552	612	31	75	1	2008-07-07 18:32:31	2008-07-07 18:32:31
3722	553	612	31	73	1	2008-07-07 18:32:31	2008-07-07 18:32:31
3723	551	612	33	74	2	2008-07-07 18:32:31	2008-07-07 18:32:31
3724	552	612	33	74	2	2008-07-07 18:32:31	2008-07-07 18:32:31
3725	553	612	33	75	2	2008-07-07 18:32:31	2008-07-07 18:32:31
3726	551	612	32	75	3	2008-07-07 18:32:31	2008-07-07 18:32:31
3727	552	612	32	76	3	2008-07-07 18:32:31	2008-07-07 18:32:31
3728	553	612	32	76	3	2008-07-07 18:32:31	2008-07-07 18:32:31
3729	551	612	31	37	4	2008-07-07 18:32:31	2008-07-07 18:32:31
3730	552	612	31	38	4	2008-07-07 18:32:31	2008-07-07 18:32:31
3731	553	612	31	34	4	2008-07-07 18:32:31	2008-07-07 18:32:31
3732	512	581	181	78	1	2008-07-07 18:32:37	2008-07-07 18:32:37
3733	512	581	182	77	2	2008-07-07 18:32:37	2008-07-07 18:32:37
3734	512	581	183	78	3	2008-07-07 18:32:37	2008-07-07 18:32:37
3735	512	581	181	39.5	4	2008-07-07 18:32:37	2008-07-07 18:32:37
3736	512	582	10	77	1	2008-07-07 18:32:37	2008-07-07 18:32:37
3737	512	582	11	78	2	2008-07-07 18:32:37	2008-07-07 18:32:37
3738	512	582	12	77	3	2008-07-07 18:32:37	2008-07-07 18:32:37
3739	512	582	11	39	4	2008-07-07 18:32:37	2008-07-07 18:32:37
3740	515	595	126	75	1	2008-07-07 18:33:22	2008-07-07 18:33:22
3741	515	595	124	74	2	2008-07-07 18:33:22	2008-07-07 18:33:22
3742	515	595	125	75	3	2008-07-07 18:33:22	2008-07-07 18:33:22
3743	515	595	124	38	4	2008-07-07 18:33:22	2008-07-07 18:33:22
3744	515	596	217	75	1	2008-07-07 18:33:22	2008-07-07 18:33:22
3745	515	596	218	76	2	2008-07-07 18:33:22	2008-07-07 18:33:22
3746	515	596	219	75	3	2008-07-07 18:33:22	2008-07-07 18:33:22
3747	515	596	217	38	4	2008-07-07 18:33:22	2008-07-07 18:33:22
3748	520	593	150	76	1	2008-07-07 18:34:14	2008-07-07 18:34:14
3749	520	593	149	76	2	2008-07-07 18:34:14	2008-07-07 18:34:14
3750	520	593	148	75	3	2008-07-07 18:34:14	2008-07-07 18:34:14
3751	520	593	150	38	4	2008-07-07 18:34:14	2008-07-07 18:34:14
3752	520	594	116	77	1	2008-07-07 18:34:14	2008-07-07 18:34:14
3753	520	594	115	77	2	2008-07-07 18:34:14	2008-07-07 18:34:14
3754	520	594	117	76	3	2008-07-07 18:34:14	2008-07-07 18:34:14
3755	520	594	116	38.5	4	2008-07-07 18:34:14	2008-07-07 18:34:14
3756	570	637	138	73	1	2008-07-07 18:34:33	2008-07-07 18:34:33
3757	570	637	136	73	2	2008-07-07 18:34:33	2008-07-07 18:34:33
3758	570	637	137	72	3	2008-07-07 18:34:33	2008-07-07 18:34:33
3759	570	637	138	36.5	4	2008-07-07 18:34:33	2008-07-07 18:34:33
3760	570	638	209	74	1	2008-07-07 18:34:33	2008-07-07 18:34:33
3761	570	638	208	74	2	2008-07-07 18:34:33	2008-07-07 18:34:33
3762	570	638	210	74	3	2008-07-07 18:34:33	2008-07-07 18:34:33
3763	570	638	209	37	4	2008-07-07 18:34:33	2008-07-07 18:34:33
3764	568	633	193	75	1	2008-07-07 18:35:21	2008-07-07 18:35:21
3765	568	633	194	74	2	2008-07-07 18:35:21	2008-07-07 18:35:21
3766	568	633	195	75	3	2008-07-07 18:35:21	2008-07-07 18:35:21
3767	568	633	193	37.5	4	2008-07-07 18:35:21	2008-07-07 18:35:21
3768	568	634	4	73	1	2008-07-07 18:35:21	2008-07-07 18:35:21
3769	568	634	5	74	2	2008-07-07 18:35:21	2008-07-07 18:35:21
3770	568	634	6	75	3	2008-07-07 18:35:21	2008-07-07 18:35:21
3771	568	634	4	37.5	4	2008-07-07 18:35:21	2008-07-07 18:35:21
3780	516	589	14	77	1	2008-07-07 18:36:16	2008-07-07 18:36:16
3781	516	589	13	79	2	2008-07-07 18:36:16	2008-07-07 18:36:16
3782	516	589	15	77	3	2008-07-07 18:36:16	2008-07-07 18:36:16
3783	516	589	14	38.5	4	2008-07-07 18:36:16	2008-07-07 18:36:16
3784	516	590	108	75	1	2008-07-07 18:36:16	2008-07-07 18:36:16
3785	516	590	107	76	2	2008-07-07 18:36:16	2008-07-07 18:36:16
3786	516	590	106	76	3	2008-07-07 18:36:16	2008-07-07 18:36:16
3787	516	590	108	38.5	4	2008-07-07 18:36:16	2008-07-07 18:36:16
3788	510	575	101	77	1	2008-07-07 18:37:40	2008-07-07 18:37:40
3789	510	575	102	77	2	2008-07-07 18:37:40	2008-07-07 18:37:40
3790	510	575	100	76	3	2008-07-07 18:37:40	2008-07-07 18:37:40
3791	510	575	101	38.5	4	2008-07-07 18:37:40	2008-07-07 18:37:40
3792	510	576	211	79	1	2008-07-07 18:37:40	2008-07-07 18:37:40
3793	510	576	212	78	2	2008-07-07 18:37:40	2008-07-07 18:37:40
3794	510	576	213	79	3	2008-07-07 18:37:40	2008-07-07 18:37:40
3795	510	576	211	39	4	2008-07-07 18:37:40	2008-07-07 18:37:40
3820	567	631	49	75	1	2008-07-07 18:39:31	2008-07-07 18:39:31
3821	567	631	51	77	2	2008-07-07 18:39:31	2008-07-07 18:39:31
3822	567	631	50	77	3	2008-07-07 18:39:31	2008-07-07 18:39:31
3823	567	631	51	36.5	4	2008-07-07 18:39:31	2008-07-07 18:39:31
3824	567	632	57	74	1	2008-07-07 18:39:31	2008-07-07 18:39:31
3825	567	632	56	74	2	2008-07-07 18:39:31	2008-07-07 18:39:31
3826	567	632	55	75	3	2008-07-07 18:39:31	2008-07-07 18:39:31
3827	567	632	57	36	4	2008-07-07 18:39:31	2008-07-07 18:39:31
3828	517	587	111	75	1	2008-07-07 18:40:22	2008-07-07 18:40:22
3829	518	587	111	75	1	2008-07-07 18:40:22	2008-07-07 18:40:22
3830	519	587	111	76	1	2008-07-07 18:40:22	2008-07-07 18:40:22
3831	517	587	109	76	2	2008-07-07 18:40:22	2008-07-07 18:40:22
3832	518	587	109	75	2	2008-07-07 18:40:22	2008-07-07 18:40:22
3833	519	587	109	76	2	2008-07-07 18:40:22	2008-07-07 18:40:22
3834	517	587	110	74	3	2008-07-07 18:40:22	2008-07-07 18:40:22
3835	518	587	110	74	3	2008-07-07 18:40:22	2008-07-07 18:40:22
3836	519	587	110	75	3	2008-07-07 18:40:22	2008-07-07 18:40:22
3837	517	587	111	38	4	2008-07-07 18:40:22	2008-07-07 18:40:22
3838	518	587	111	37.5	4	2008-07-07 18:40:22	2008-07-07 18:40:22
3839	519	587	111	37.5	4	2008-07-07 18:40:22	2008-07-07 18:40:22
3840	517	588	119	76	1	2008-07-07 18:40:22	2008-07-07 18:40:22
3841	518	588	119	76	1	2008-07-07 18:40:22	2008-07-07 18:40:22
3842	519	588	119	77	1	2008-07-07 18:40:22	2008-07-07 18:40:22
3843	517	588	120	75	2	2008-07-07 18:40:22	2008-07-07 18:40:22
3844	518	588	120	76	2	2008-07-07 18:40:22	2008-07-07 18:40:22
3845	519	588	120	76	2	2008-07-07 18:40:22	2008-07-07 18:40:22
3846	517	588	118	76	3	2008-07-07 18:40:22	2008-07-07 18:40:22
3847	518	588	118	76	3	2008-07-07 18:40:22	2008-07-07 18:40:22
3848	519	588	118	76	3	2008-07-07 18:40:22	2008-07-07 18:40:22
3849	517	588	119	37.5	4	2008-07-07 18:40:22	2008-07-07 18:40:22
3850	518	588	119	37.5	4	2008-07-07 18:40:22	2008-07-07 18:40:22
3851	519	588	119	38	4	2008-07-07 18:40:22	2008-07-07 18:40:22
3852	511	579	99	77	1	2008-07-07 18:42:34	2008-07-07 18:42:34
3853	511	579	97	77	2	2008-07-07 18:42:34	2008-07-07 18:42:34
3854	511	579	98	78	3	2008-07-07 18:42:34	2008-07-07 18:42:34
3855	511	579	97	37.5	4	2008-07-07 18:42:34	2008-07-07 18:42:34
3856	511	580	70	77	1	2008-07-07 18:42:34	2008-07-07 18:42:34
3857	511	580	71	77	2	2008-07-07 18:42:34	2008-07-07 18:42:34
3858	511	580	72	75	3	2008-07-07 18:42:34	2008-07-07 18:42:34
3859	511	580	70	37.5	4	2008-07-07 18:42:34	2008-07-07 18:42:34
3860	557	615	139	75	1	2008-07-07 18:43:01	2008-07-07 18:43:01
3861	558	615	139	74	1	2008-07-07 18:43:01	2008-07-07 18:43:01
3862	559	615	139	75	1	2008-07-07 18:43:01	2008-07-07 18:43:01
3863	557	615	141	74	2	2008-07-07 18:43:01	2008-07-07 18:43:01
3864	558	615	141	75	2	2008-07-07 18:43:01	2008-07-07 18:43:01
3865	559	615	141	74	2	2008-07-07 18:43:01	2008-07-07 18:43:01
3866	557	615	140	74	3	2008-07-07 18:43:01	2008-07-07 18:43:01
3867	558	615	140	74	3	2008-07-07 18:43:01	2008-07-07 18:43:01
3868	559	615	140	73	3	2008-07-07 18:43:01	2008-07-07 18:43:01
3869	557	615	139	37.5	4	2008-07-07 18:43:01	2008-07-07 18:43:01
3870	558	615	139	37.5	4	2008-07-07 18:43:01	2008-07-07 18:43:01
3871	559	615	139	37.5	4	2008-07-07 18:43:01	2008-07-07 18:43:01
3872	557	616	147	75	1	2008-07-07 18:43:01	2008-07-07 18:43:01
3873	558	616	147	75	1	2008-07-07 18:43:01	2008-07-07 18:43:01
3874	559	616	147	75	1	2008-07-07 18:43:01	2008-07-07 18:43:01
3875	557	616	146	75	2	2008-07-07 18:43:01	2008-07-07 18:43:01
3876	558	616	146	74	2	2008-07-07 18:43:01	2008-07-07 18:43:01
3877	559	616	146	75	2	2008-07-07 18:43:01	2008-07-07 18:43:01
3878	557	616	145	74	3	2008-07-07 18:43:01	2008-07-07 18:43:01
3879	558	616	145	74	3	2008-07-07 18:43:01	2008-07-07 18:43:01
3880	559	616	145	73	3	2008-07-07 18:43:01	2008-07-07 18:43:01
3881	557	616	146	38	4	2008-07-07 18:43:01	2008-07-07 18:43:01
3882	558	616	146	36.5	4	2008-07-07 18:43:01	2008-07-07 18:43:01
3883	559	616	146	37.5	4	2008-07-07 18:43:01	2008-07-07 18:43:01
3884	527	591	155	74	1	2008-07-07 18:44:45	2008-07-07 18:44:45
3885	528	591	155	75	1	2008-07-07 18:44:45	2008-07-07 18:44:45
3886	529	591	155	74	1	2008-07-07 18:44:45	2008-07-07 18:44:45
3887	527	591	156	76	2	2008-07-07 18:44:45	2008-07-07 18:44:45
3888	528	591	156	75	2	2008-07-07 18:44:45	2008-07-07 18:44:45
3889	529	591	156	76	2	2008-07-07 18:44:45	2008-07-07 18:44:45
3890	527	591	154	74	3	2008-07-07 18:44:45	2008-07-07 18:44:45
3891	528	591	154	74	3	2008-07-07 18:44:45	2008-07-07 18:44:45
3892	529	591	154	74	3	2008-07-07 18:44:45	2008-07-07 18:44:45
3893	527	591	155	36	4	2008-07-07 18:44:45	2008-07-07 18:44:45
3894	528	591	155	37.5	4	2008-07-07 18:44:45	2008-07-07 18:44:45
3895	529	591	155	37	4	2008-07-07 18:44:45	2008-07-07 18:44:45
3896	527	592	58	74	1	2008-07-07 18:44:45	2008-07-07 18:44:45
3897	528	592	58	74	1	2008-07-07 18:44:45	2008-07-07 18:44:45
3898	529	592	58	74	1	2008-07-07 18:44:45	2008-07-07 18:44:45
3899	527	592	59	75	2	2008-07-07 18:44:45	2008-07-07 18:44:45
3900	528	592	59	75	2	2008-07-07 18:44:45	2008-07-07 18:44:45
3901	529	592	59	74	2	2008-07-07 18:44:45	2008-07-07 18:44:45
3902	527	592	60	76	3	2008-07-07 18:44:45	2008-07-07 18:44:45
3903	528	592	60	76	3	2008-07-07 18:44:45	2008-07-07 18:44:45
3904	529	592	60	75	3	2008-07-07 18:44:45	2008-07-07 18:44:45
3905	527	592	58	37.5	4	2008-07-07 18:44:45	2008-07-07 18:44:45
3906	528	592	58	37.5	4	2008-07-07 18:44:45	2008-07-07 18:44:45
3907	529	592	58	37	4	2008-07-07 18:44:45	2008-07-07 18:44:45
3908	562	621	202	73	1	2008-07-07 18:45:24	2008-07-07 18:45:24
3909	562	621	203	74	2	2008-07-07 18:45:24	2008-07-07 18:45:24
3910	562	621	204	75	3	2008-07-07 18:45:24	2008-07-07 18:45:24
3911	562	621	202	37	4	2008-07-07 18:45:24	2008-07-07 18:45:24
3912	562	622	221	72	1	2008-07-07 18:45:24	2008-07-07 18:45:24
3913	562	622	220	72	2	2008-07-07 18:45:24	2008-07-07 18:45:24
3914	562	622	222	73	3	2008-07-07 18:45:24	2008-07-07 18:45:24
3915	562	622	221	36	4	2008-07-07 18:45:24	2008-07-07 18:45:24
3916	564	625	187	77	1	2008-07-07 18:45:46	2008-07-07 18:45:46
3917	564	625	188	75	2	2008-07-07 18:45:46	2008-07-07 18:45:46
3918	564	625	189	76	3	2008-07-07 18:45:46	2008-07-07 18:45:46
3919	564	625	187	37.5	4	2008-07-07 18:45:46	2008-07-07 18:45:46
3920	564	626	52	76	1	2008-07-07 18:45:46	2008-07-07 18:45:46
3921	564	626	53	76	2	2008-07-07 18:45:46	2008-07-07 18:45:46
3922	564	626	54	76	3	2008-07-07 18:45:46	2008-07-07 18:45:46
3923	564	626	52	38.5	4	2008-07-07 18:45:46	2008-07-07 18:45:46
3924	560	619	2	74	1	2008-07-07 18:46:49	2008-07-07 18:46:49
3925	560	619	3	76	2	2008-07-07 18:46:49	2008-07-07 18:46:49
3926	560	619	1	74	3	2008-07-07 18:46:49	2008-07-07 18:46:49
3927	560	619	3	37	4	2008-07-07 18:46:49	2008-07-07 18:46:49
3928	560	620	191	73	1	2008-07-07 18:46:49	2008-07-07 18:46:49
3929	560	620	192	73	2	2008-07-07 18:46:49	2008-07-07 18:46:49
3930	560	620	190	74	3	2008-07-07 18:46:49	2008-07-07 18:46:49
3931	560	620	191	36	4	2008-07-07 18:46:49	2008-07-07 18:46:49
3940	563	623	25	73	1	2008-07-07 18:47:44	2008-07-07 18:47:44
3941	563	623	26	73	2	2008-07-07 18:47:44	2008-07-07 18:47:44
3942	563	623	27	71	3	2008-07-07 18:47:44	2008-07-07 18:47:44
3943	563	623	25	34	4	2008-07-07 18:47:44	2008-07-07 18:47:44
3944	563	624	35	74	1	2008-07-07 18:47:44	2008-07-07 18:47:44
3945	563	624	36	72	2	2008-07-07 18:47:44	2008-07-07 18:47:44
3946	563	624	34	73	3	2008-07-07 18:47:44	2008-07-07 18:47:44
3947	563	624	35	34	4	2008-07-07 18:47:44	2008-07-07 18:47:44
3948	554	617	63	76	1	2008-07-07 18:49:03	2008-07-07 18:49:03
3949	555	617	63	75	1	2008-07-07 18:49:03	2008-07-07 18:49:03
3950	556	617	63	75	1	2008-07-07 18:49:03	2008-07-07 18:49:03
3951	554	617	61	76	2	2008-07-07 18:49:03	2008-07-07 18:49:03
3952	555	617	61	76	2	2008-07-07 18:49:03	2008-07-07 18:49:03
3953	556	617	61	75	2	2008-07-07 18:49:03	2008-07-07 18:49:03
3954	554	617	62	77	3	2008-07-07 18:49:03	2008-07-07 18:49:03
3955	555	617	62	77	3	2008-07-07 18:49:03	2008-07-07 18:49:03
3956	556	617	62	76	3	2008-07-07 18:49:03	2008-07-07 18:49:03
3957	554	617	63	37.5	4	2008-07-07 18:49:03	2008-07-07 18:49:03
3958	555	617	63	39	4	2008-07-07 18:49:03	2008-07-07 18:49:03
3959	556	617	63	36	4	2008-07-07 18:49:03	2008-07-07 18:49:03
3960	554	618	76	78	1	2008-07-07 18:49:03	2008-07-07 18:49:03
3961	555	618	76	78	1	2008-07-07 18:49:03	2008-07-07 18:49:03
3962	556	618	76	76	1	2008-07-07 18:49:03	2008-07-07 18:49:03
3963	554	618	77	74	2	2008-07-07 18:49:03	2008-07-07 18:49:03
3964	555	618	77	76	2	2008-07-07 18:49:03	2008-07-07 18:49:03
3965	556	618	77	75	2	2008-07-07 18:49:03	2008-07-07 18:49:03
3966	554	618	78	75	3	2008-07-07 18:49:03	2008-07-07 18:49:03
3967	555	618	78	75	3	2008-07-07 18:49:03	2008-07-07 18:49:03
3968	556	618	78	73	3	2008-07-07 18:49:03	2008-07-07 18:49:03
3969	554	618	76	38.5	4	2008-07-07 18:49:03	2008-07-07 18:49:03
3970	555	618	76	40	4	2008-07-07 18:49:03	2008-07-07 18:49:03
3971	556	618	76	36	4	2008-07-07 18:49:03	2008-07-07 18:49:03
3972	539	605	152	74	1	2008-07-07 18:49:30	2008-07-07 18:49:30
3973	540	605	152	75	1	2008-07-07 18:49:30	2008-07-07 18:49:30
3974	541	605	152	74	1	2008-07-07 18:49:30	2008-07-07 18:49:30
3975	539	605	151	74	2	2008-07-07 18:49:30	2008-07-07 18:49:30
3976	540	605	151	76	2	2008-07-07 18:49:30	2008-07-07 18:49:30
3977	541	605	151	74	2	2008-07-07 18:49:30	2008-07-07 18:49:30
3978	539	605	153	74	3	2008-07-07 18:49:30	2008-07-07 18:49:30
3979	540	605	153	76	3	2008-07-07 18:49:30	2008-07-07 18:49:30
3980	541	605	153	76	3	2008-07-07 18:49:30	2008-07-07 18:49:30
3981	539	605	151	37	4	2008-07-07 18:49:30	2008-07-07 18:49:30
3982	540	605	151	38.5	4	2008-07-07 18:49:30	2008-07-07 18:49:30
3983	541	605	151	37.5	4	2008-07-07 18:49:30	2008-07-07 18:49:30
3984	539	606	105	74	1	2008-07-07 18:49:30	2008-07-07 18:49:30
3985	540	606	105	75	1	2008-07-07 18:49:30	2008-07-07 18:49:30
3986	541	606	105	74	1	2008-07-07 18:49:30	2008-07-07 18:49:30
3987	539	606	104	74	2	2008-07-07 18:49:30	2008-07-07 18:49:30
3988	540	606	104	76	2	2008-07-07 18:49:30	2008-07-07 18:49:30
3989	541	606	104	75	2	2008-07-07 18:49:30	2008-07-07 18:49:30
3990	539	606	103	75	3	2008-07-07 18:49:30	2008-07-07 18:49:30
3991	540	606	103	77	3	2008-07-07 18:49:30	2008-07-07 18:49:30
3992	541	606	103	76	3	2008-07-07 18:49:30	2008-07-07 18:49:30
3993	539	606	105	37	4	2008-07-07 18:49:30	2008-07-07 18:49:30
3994	540	606	105	38.5	4	2008-07-07 18:49:30	2008-07-07 18:49:30
3995	541	606	105	38	4	2008-07-07 18:49:30	2008-07-07 18:49:30
3996	569	635	207	72	1	2008-07-07 18:51:02	2008-07-07 18:51:02
3997	569	635	205	70	2	2008-07-07 18:51:02	2008-07-07 18:51:02
3998	569	635	206	75	3	2008-07-07 18:51:02	2008-07-07 18:51:02
3999	569	635	207	37	4	2008-07-07 18:51:02	2008-07-07 18:51:02
4000	569	636	29	73	1	2008-07-07 18:51:02	2008-07-07 18:51:02
4001	569	636	28	75	2	2008-07-07 18:51:02	2008-07-07 18:51:02
4002	569	636	30	72	3	2008-07-07 18:51:02	2008-07-07 18:51:02
4003	569	636	29	37	4	2008-07-07 18:51:02	2008-07-07 18:51:02
4004	545	607	21	75	1	2008-07-07 18:52:36	2008-07-07 18:52:36
4005	546	607	21	78	1	2008-07-07 18:52:36	2008-07-07 18:52:36
4006	547	607	21	77	1	2008-07-07 18:52:36	2008-07-07 18:52:36
4007	545	607	19	75	2	2008-07-07 18:52:36	2008-07-07 18:52:36
4008	546	607	19	76	2	2008-07-07 18:52:36	2008-07-07 18:52:36
4009	547	607	19	77	2	2008-07-07 18:52:36	2008-07-07 18:52:36
4010	545	607	20	75	3	2008-07-07 18:52:36	2008-07-07 18:52:36
4011	546	607	20	77	3	2008-07-07 18:52:36	2008-07-07 18:52:36
4012	547	607	20	75	3	2008-07-07 18:52:36	2008-07-07 18:52:36
4013	545	607	21	37.5	4	2008-07-07 18:52:36	2008-07-07 18:52:36
4014	546	607	21	38	4	2008-07-07 18:52:36	2008-07-07 18:52:36
4015	547	607	21	35	4	2008-07-07 18:52:36	2008-07-07 18:52:36
4016	545	608	68	75	1	2008-07-07 18:52:36	2008-07-07 18:52:36
4017	546	608	68	76	1	2008-07-07 18:52:36	2008-07-07 18:52:36
4018	547	608	68	76	1	2008-07-07 18:52:36	2008-07-07 18:52:36
4019	545	608	67	75	2	2008-07-07 18:52:36	2008-07-07 18:52:36
4020	546	608	67	75	2	2008-07-07 18:52:36	2008-07-07 18:52:36
4021	547	608	67	76	2	2008-07-07 18:52:36	2008-07-07 18:52:36
4022	545	608	69	73	3	2008-07-07 18:52:36	2008-07-07 18:52:36
4023	546	608	69	77	3	2008-07-07 18:52:36	2008-07-07 18:52:36
4024	547	608	69	75	3	2008-07-07 18:52:36	2008-07-07 18:52:36
4025	545	608	68	37.5	4	2008-07-07 18:52:36	2008-07-07 18:52:36
4026	546	608	68	37	4	2008-07-07 18:52:36	2008-07-07 18:52:36
4027	547	608	68	35	4	2008-07-07 18:52:36	2008-07-07 18:52:36
4028	533	597	130	74	1	2008-07-07 18:53:14	2008-07-07 18:53:14
4029	534	597	130	76	1	2008-07-07 18:53:14	2008-07-07 18:53:14
4030	535	597	130	74	1	2008-07-07 18:53:14	2008-07-07 18:53:14
4031	533	597	131	74	2	2008-07-07 18:53:14	2008-07-07 18:53:14
4032	534	597	131	75	2	2008-07-07 18:53:14	2008-07-07 18:53:14
4033	535	597	131	75	2	2008-07-07 18:53:14	2008-07-07 18:53:14
4034	533	597	132	74	3	2008-07-07 18:53:14	2008-07-07 18:53:14
4035	534	597	132	75	3	2008-07-07 18:53:14	2008-07-07 18:53:14
4036	535	597	132	75	3	2008-07-07 18:53:14	2008-07-07 18:53:14
4037	533	597	130	37	4	2008-07-07 18:53:14	2008-07-07 18:53:14
4038	534	597	130	37	4	2008-07-07 18:53:14	2008-07-07 18:53:14
4039	535	597	130	37	4	2008-07-07 18:53:14	2008-07-07 18:53:14
4040	533	598	94	75	1	2008-07-07 18:53:14	2008-07-07 18:53:14
4041	534	598	94	78	1	2008-07-07 18:53:14	2008-07-07 18:53:14
4042	535	598	94	75	1	2008-07-07 18:53:14	2008-07-07 18:53:14
4043	533	598	95	75	2	2008-07-07 18:53:14	2008-07-07 18:53:14
4044	534	598	95	76	2	2008-07-07 18:53:14	2008-07-07 18:53:14
4045	535	598	95	75	2	2008-07-07 18:53:14	2008-07-07 18:53:14
4046	533	598	96	74	3	2008-07-07 18:53:14	2008-07-07 18:53:14
4047	534	598	96	75	3	2008-07-07 18:53:14	2008-07-07 18:53:14
4048	535	598	96	75	3	2008-07-07 18:53:14	2008-07-07 18:53:14
4049	533	598	94	38	4	2008-07-07 18:53:14	2008-07-07 18:53:14
4050	534	598	94	39	4	2008-07-07 18:53:14	2008-07-07 18:53:14
4051	535	598	94	38	4	2008-07-07 18:53:14	2008-07-07 18:53:14
4052	565	627	163	74	1	2008-07-07 18:54:13	2008-07-07 18:54:13
4053	565	627	164	75	2	2008-07-07 18:54:13	2008-07-07 18:54:13
4054	565	627	165	74	3	2008-07-07 18:54:13	2008-07-07 18:54:13
4055	565	627	163	36.5	4	2008-07-07 18:54:13	2008-07-07 18:54:13
4056	565	628	196	73	1	2008-07-07 18:54:13	2008-07-07 18:54:13
4057	565	628	197	76	2	2008-07-07 18:54:13	2008-07-07 18:54:13
4058	565	628	198	74	3	2008-07-07 18:54:13	2008-07-07 18:54:13
4059	565	628	197	37.5	4	2008-07-07 18:54:13	2008-07-07 18:54:13
4060	566	629	166	74	1	2008-07-07 18:55:00	2008-07-07 18:55:00
4061	566	629	167	74	2	2008-07-07 18:55:00	2008-07-07 18:55:00
4062	566	629	168	74	3	2008-07-07 18:55:00	2008-07-07 18:55:00
4063	566	629	166	37.5	4	2008-07-07 18:55:00	2008-07-07 18:55:00
4064	566	630	24	74	1	2008-07-07 18:55:00	2008-07-07 18:55:00
4065	566	630	22	75	2	2008-07-07 18:55:00	2008-07-07 18:55:00
4066	566	630	23	74	3	2008-07-07 18:55:00	2008-07-07 18:55:00
4067	566	630	24	37.5	4	2008-07-07 18:55:00	2008-07-07 18:55:00
4068	521	599	80	75	1	2008-07-07 18:55:35	2008-07-07 18:55:35
4069	522	599	80	76	1	2008-07-07 18:55:35	2008-07-07 18:55:35
4070	523	599	80	76	1	2008-07-07 18:55:35	2008-07-07 18:55:35
4071	521	599	81	75	2	2008-07-07 18:55:35	2008-07-07 18:55:35
4072	522	599	81	76	2	2008-07-07 18:55:35	2008-07-07 18:55:35
4073	523	599	81	75	2	2008-07-07 18:55:35	2008-07-07 18:55:35
4074	521	599	79	75	3	2008-07-07 18:55:35	2008-07-07 18:55:35
4075	522	599	79	77	3	2008-07-07 18:55:35	2008-07-07 18:55:35
4076	523	599	79	75	3	2008-07-07 18:55:35	2008-07-07 18:55:35
4077	521	599	80	37.5	4	2008-07-07 18:55:35	2008-07-07 18:55:35
4078	522	599	80	37.5	4	2008-07-07 18:55:35	2008-07-07 18:55:35
4079	523	599	80	37.5	4	2008-07-07 18:55:35	2008-07-07 18:55:35
4080	521	600	43	76	1	2008-07-07 18:55:35	2008-07-07 18:55:35
4081	522	600	43	77	1	2008-07-07 18:55:35	2008-07-07 18:55:35
4082	523	600	43	76	1	2008-07-07 18:55:35	2008-07-07 18:55:35
4083	521	600	45	75	2	2008-07-07 18:55:35	2008-07-07 18:55:35
4084	522	600	45	77	2	2008-07-07 18:55:35	2008-07-07 18:55:35
4085	523	600	45	75	2	2008-07-07 18:55:35	2008-07-07 18:55:35
4086	521	600	44	75	3	2008-07-07 18:55:35	2008-07-07 18:55:35
4087	522	600	44	78	3	2008-07-07 18:55:35	2008-07-07 18:55:35
4088	523	600	44	76	3	2008-07-07 18:55:35	2008-07-07 18:55:35
4089	521	600	43	37.5	4	2008-07-07 18:55:35	2008-07-07 18:55:35
4090	522	600	43	38	4	2008-07-07 18:55:35	2008-07-07 18:55:35
4091	523	600	43	37.5	4	2008-07-07 18:55:35	2008-07-07 18:55:35
4092	536	601	142	75	1	2008-07-07 18:56:08	2008-07-07 18:56:08
4093	537	601	142	75	1	2008-07-07 18:56:08	2008-07-07 18:56:08
4094	538	601	142	74	1	2008-07-07 18:56:08	2008-07-07 18:56:08
4095	536	601	144	75	2	2008-07-07 18:56:08	2008-07-07 18:56:08
4096	537	601	144	75	2	2008-07-07 18:56:08	2008-07-07 18:56:08
4097	538	601	144	76	2	2008-07-07 18:56:08	2008-07-07 18:56:08
4098	536	601	143	76	3	2008-07-07 18:56:08	2008-07-07 18:56:08
4099	537	601	143	74	3	2008-07-07 18:56:08	2008-07-07 18:56:08
4100	538	601	143	76	3	2008-07-07 18:56:08	2008-07-07 18:56:08
4101	536	601	144	38	4	2008-07-07 18:56:08	2008-07-07 18:56:08
4102	537	601	144	37	4	2008-07-07 18:56:08	2008-07-07 18:56:08
4103	538	601	144	37	4	2008-07-07 18:56:08	2008-07-07 18:56:08
4104	536	602	93	75	1	2008-07-07 18:56:08	2008-07-07 18:56:08
4105	537	602	93	75	1	2008-07-07 18:56:08	2008-07-07 18:56:08
4106	538	602	93	77	1	2008-07-07 18:56:08	2008-07-07 18:56:08
4107	536	602	92	76	2	2008-07-07 18:56:08	2008-07-07 18:56:08
4108	537	602	92	75	2	2008-07-07 18:56:08	2008-07-07 18:56:08
4109	538	602	92	77	2	2008-07-07 18:56:08	2008-07-07 18:56:08
4110	536	602	91	76	3	2008-07-07 18:56:08	2008-07-07 18:56:08
4111	537	602	91	76	3	2008-07-07 18:56:08	2008-07-07 18:56:08
4112	538	602	91	75	3	2008-07-07 18:56:08	2008-07-07 18:56:08
4113	536	602	93	38	4	2008-07-07 18:56:08	2008-07-07 18:56:08
4114	537	602	93	38	4	2008-07-07 18:56:08	2008-07-07 18:56:08
4115	538	602	93	38	4	2008-07-07 18:56:08	2008-07-07 18:56:08
4116	524	603	16	76	1	2008-07-07 18:56:34	2008-07-07 18:56:34
4117	525	603	16	76	1	2008-07-07 18:56:34	2008-07-07 18:56:34
4118	526	603	16	76	1	2008-07-07 18:56:34	2008-07-07 18:56:34
4119	524	603	18	77	2	2008-07-07 18:56:34	2008-07-07 18:56:34
4120	525	603	18	77	2	2008-07-07 18:56:34	2008-07-07 18:56:34
4121	526	603	18	77	2	2008-07-07 18:56:34	2008-07-07 18:56:34
4122	524	603	17	77	3	2008-07-07 18:56:34	2008-07-07 18:56:34
4123	525	603	17	76	3	2008-07-07 18:56:34	2008-07-07 18:56:34
4124	526	603	17	78	3	2008-07-07 18:56:34	2008-07-07 18:56:34
4125	524	603	16	38.5	4	2008-07-07 18:56:34	2008-07-07 18:56:34
4126	525	603	16	38	4	2008-07-07 18:56:34	2008-07-07 18:56:34
4127	526	603	16	38.5	4	2008-07-07 18:56:34	2008-07-07 18:56:34
4128	524	604	133	76	1	2008-07-07 18:56:34	2008-07-07 18:56:34
4129	525	604	133	75	1	2008-07-07 18:56:34	2008-07-07 18:56:34
4130	526	604	133	76	1	2008-07-07 18:56:34	2008-07-07 18:56:34
4131	524	604	134	76	2	2008-07-07 18:56:34	2008-07-07 18:56:34
4132	525	604	134	76	2	2008-07-07 18:56:34	2008-07-07 18:56:34
4133	526	604	134	77	2	2008-07-07 18:56:34	2008-07-07 18:56:34
4134	524	604	135	75	3	2008-07-07 18:56:34	2008-07-07 18:56:34
4135	525	604	135	75	3	2008-07-07 18:56:34	2008-07-07 18:56:34
4136	526	604	135	76	3	2008-07-07 18:56:34	2008-07-07 18:56:34
4137	524	604	133	36.5	4	2008-07-07 18:56:34	2008-07-07 18:56:34
4138	525	604	133	37.5	4	2008-07-07 18:56:34	2008-07-07 18:56:34
4139	526	604	133	38	4	2008-07-07 18:56:34	2008-07-07 18:56:34
4140	514	583	175	75	1	2008-07-07 18:58:40	2008-07-07 18:58:40
4141	514	583	177	76	2	2008-07-07 18:58:40	2008-07-07 18:58:40
4142	514	583	176	76	3	2008-07-07 18:58:40	2008-07-07 18:58:40
4143	514	583	175	38	4	2008-07-07 18:58:40	2008-07-07 18:58:40
4144	514	584	201	75	1	2008-07-07 18:58:40	2008-07-07 18:58:40
4145	514	584	200	75	2	2008-07-07 18:58:40	2008-07-07 18:58:40
4146	514	584	199	76	3	2008-07-07 18:58:40	2008-07-07 18:58:40
4147	514	584	201	37.5	4	2008-07-07 18:58:40	2008-07-07 18:58:40
4148	548	609	161	76	1	2008-07-07 18:59:41	2008-07-07 18:59:41
4149	549	609	161	77	1	2008-07-07 18:59:41	2008-07-07 18:59:41
4150	550	609	161	77	1	2008-07-07 18:59:41	2008-07-07 18:59:41
4151	548	609	160	75	2	2008-07-07 18:59:41	2008-07-07 18:59:41
4152	549	609	160	76	2	2008-07-07 18:59:41	2008-07-07 18:59:41
4153	550	609	160	76	2	2008-07-07 18:59:41	2008-07-07 18:59:41
4154	548	609	162	75	3	2008-07-07 18:59:42	2008-07-07 18:59:42
4155	549	609	162	76	3	2008-07-07 18:59:42	2008-07-07 18:59:42
4156	550	609	162	78	3	2008-07-07 18:59:42	2008-07-07 18:59:42
4157	548	609	160	37.5	4	2008-07-07 18:59:42	2008-07-07 18:59:42
4158	549	609	160	39.5	4	2008-07-07 18:59:42	2008-07-07 18:59:42
4159	550	609	160	39	4	2008-07-07 18:59:42	2008-07-07 18:59:42
4160	548	610	64	73	1	2008-07-07 18:59:42	2008-07-07 18:59:42
4161	549	610	64	76	1	2008-07-07 18:59:42	2008-07-07 18:59:42
4162	550	610	64	75	1	2008-07-07 18:59:42	2008-07-07 18:59:42
4163	548	610	65	74	2	2008-07-07 18:59:42	2008-07-07 18:59:42
4164	549	610	65	76	2	2008-07-07 18:59:42	2008-07-07 18:59:42
4165	550	610	65	76	2	2008-07-07 18:59:42	2008-07-07 18:59:42
4166	548	610	66	74	3	2008-07-07 18:59:42	2008-07-07 18:59:42
4167	549	610	66	76	3	2008-07-07 18:59:42	2008-07-07 18:59:42
4168	550	610	66	78	3	2008-07-07 18:59:42	2008-07-07 18:59:42
4169	548	610	64	37	4	2008-07-07 18:59:42	2008-07-07 18:59:42
4170	549	610	64	37.5	4	2008-07-07 18:59:42	2008-07-07 18:59:42
4171	550	610	64	38	4	2008-07-07 18:59:42	2008-07-07 18:59:42
4172	542	571	9	79	1	2008-07-07 19:01:13	2008-07-07 19:01:13
4173	543	571	9	79	1	2008-07-07 19:01:13	2008-07-07 19:01:13
4174	544	571	9	77	1	2008-07-07 19:01:13	2008-07-07 19:01:13
4175	542	571	8	76	2	2008-07-07 19:01:13	2008-07-07 19:01:13
4176	543	571	8	76	2	2008-07-07 19:01:13	2008-07-07 19:01:13
4177	544	571	8	78	2	2008-07-07 19:01:13	2008-07-07 19:01:13
4178	542	571	7	78	3	2008-07-07 19:01:13	2008-07-07 19:01:13
4179	543	571	7	78	3	2008-07-07 19:01:13	2008-07-07 19:01:13
4180	544	571	7	77	3	2008-07-07 19:01:13	2008-07-07 19:01:13
4181	542	571	9	38.5	4	2008-07-07 19:01:13	2008-07-07 19:01:13
4182	543	571	9	38	4	2008-07-07 19:01:13	2008-07-07 19:01:13
4183	544	571	9	38.5	4	2008-07-07 19:01:13	2008-07-07 19:01:13
4184	542	572	89	78	1	2008-07-07 19:01:13	2008-07-07 19:01:13
4185	543	572	89	76	1	2008-07-07 19:01:13	2008-07-07 19:01:13
4186	544	572	89	77	1	2008-07-07 19:01:13	2008-07-07 19:01:13
4187	542	572	88	79	2	2008-07-07 19:01:13	2008-07-07 19:01:13
4188	543	572	88	77	2	2008-07-07 19:01:13	2008-07-07 19:01:13
4189	544	572	88	78	2	2008-07-07 19:01:13	2008-07-07 19:01:13
4190	542	572	90	78	3	2008-07-07 19:01:13	2008-07-07 19:01:13
4191	543	572	90	77	3	2008-07-07 19:01:13	2008-07-07 19:01:13
4192	544	572	90	79	3	2008-07-07 19:01:13	2008-07-07 19:01:13
4193	542	572	89	38.5	4	2008-07-07 19:01:13	2008-07-07 19:01:13
4194	543	572	89	38	4	2008-07-07 19:01:13	2008-07-07 19:01:13
4195	544	572	89	38.5	4	2008-07-07 19:01:13	2008-07-07 19:01:13
4196	530	569	171	76	1	2008-07-07 19:03:23	2008-07-07 19:03:23
4197	531	569	171	76	1	2008-07-07 19:03:23	2008-07-07 19:03:23
4198	532	569	171	77	1	2008-07-07 19:03:23	2008-07-07 19:03:23
4199	530	569	169	76	2	2008-07-07 19:03:23	2008-07-07 19:03:23
4200	531	569	169	77	2	2008-07-07 19:03:23	2008-07-07 19:03:23
4201	532	569	169	77	2	2008-07-07 19:03:23	2008-07-07 19:03:23
4202	530	569	170	77	3	2008-07-07 19:03:23	2008-07-07 19:03:23
4203	531	569	170	77	3	2008-07-07 19:03:23	2008-07-07 19:03:23
4204	532	569	170	79	3	2008-07-07 19:03:23	2008-07-07 19:03:23
4205	530	569	169	37	4	2008-07-07 19:03:23	2008-07-07 19:03:23
4206	531	569	169	38	4	2008-07-07 19:03:23	2008-07-07 19:03:23
4207	532	569	169	38.5	4	2008-07-07 19:03:23	2008-07-07 19:03:23
4208	530	570	173	77	1	2008-07-07 19:03:23	2008-07-07 19:03:23
4209	531	570	173	76	1	2008-07-07 19:03:23	2008-07-07 19:03:23
4210	532	570	173	76	1	2008-07-07 19:03:23	2008-07-07 19:03:23
4211	530	570	174	77	2	2008-07-07 19:03:23	2008-07-07 19:03:23
4212	531	570	174	76	2	2008-07-07 19:03:23	2008-07-07 19:03:23
4213	532	570	174	77	2	2008-07-07 19:03:23	2008-07-07 19:03:23
4214	530	570	172	78	3	2008-07-07 19:03:23	2008-07-07 19:03:23
4215	531	570	172	77	3	2008-07-07 19:03:23	2008-07-07 19:03:23
4216	532	570	172	77	3	2008-07-07 19:03:23	2008-07-07 19:03:23
4217	530	570	173	37	4	2008-07-07 19:03:23	2008-07-07 19:03:23
4218	531	570	173	37	4	2008-07-07 19:03:23	2008-07-07 19:03:23
4219	532	570	173	38.5	4	2008-07-07 19:03:23	2008-07-07 19:03:23
\.


--
-- Data for Name: speaker_scores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY speaker_scores (id, debater_id, total_speaker_score, created_at, updated_at) FROM stdin;
5	5	595	2008-07-04 17:20:52	2008-07-07 19:05:07
6	6	596.5	2008-07-04 17:20:52	2008-07-07 19:05:08
7	7	623.5	2008-07-04 17:20:53	2008-07-07 19:05:08
8	8	616	2008-07-04 17:20:53	2008-07-07 19:05:08
9	9	622	2008-07-04 17:20:53	2008-07-07 19:05:08
10	10	613	2008-07-04 17:20:53	2008-07-07 19:05:09
11	11	612.66666666699996	2008-07-04 17:20:53	2008-07-07 19:05:09
12	12	608.33333333300004	2008-07-04 17:20:53	2008-07-07 19:05:09
13	13	610.5	2008-07-04 17:20:53	2008-07-07 19:05:09
14	14	606.5	2008-07-04 17:20:53	2008-07-07 19:05:09
15	15	609.5	2008-07-04 17:20:53	2008-07-07 19:05:10
50	50	597.33333333300004	2008-07-04 17:20:55	2008-07-07 19:05:17
51	51	594.66666666699996	2008-07-04 17:20:55	2008-07-07 19:05:18
52	52	600	2008-07-04 17:20:55	2008-07-07 19:05:18
54	54	599.5	2008-07-04 17:20:55	2008-07-07 19:05:18
55	55	594.5	2008-07-04 17:20:55	2008-07-07 19:05:19
56	56	590.5	2008-07-04 17:20:55	2008-07-07 19:05:19
57	57	604.33333333300004	2008-07-04 17:20:55	2008-07-07 19:05:19
58	58	602.83333333300004	2008-07-04 17:20:55	2008-07-07 19:05:19
59	59	602	2008-07-04 17:20:55	2008-07-07 19:05:20
60	60	602	2008-07-04 17:20:55	2008-07-07 19:05:20
61	61	598.66666666699996	2008-07-04 17:20:55	2008-07-07 19:05:20
62	62	602	2008-07-04 17:20:55	2008-07-07 19:05:20
63	63	601.33333333300004	2008-07-04 17:20:55	2008-07-07 19:05:21
65	65	597.33333333300004	2008-07-04 17:20:55	2008-07-07 19:05:21
66	66	602.33333333300004	2008-07-04 17:20:55	2008-07-07 19:05:21
67	67	593.83333333300004	2008-07-04 17:20:56	2008-07-07 19:05:22
68	68	601.33333333300004	2008-07-04 17:20:56	2008-07-07 19:05:22
70	70	613.66666666699996	2008-07-04 17:20:56	2008-07-07 19:05:22
71	71	605	2008-07-04 17:20:56	2008-07-07 19:05:23
72	72	604.66666666699996	2008-07-04 17:20:56	2008-07-07 19:05:23
73	73	600	2008-07-04 17:20:56	2008-07-07 19:05:23
74	74	598	2008-07-04 17:20:56	2008-07-07 19:05:23
75	75	604.5	2008-07-04 17:20:56	2008-07-07 19:05:23
76	76	602.66666666699996	2008-07-04 17:20:56	2008-07-07 19:05:24
77	77	595	2008-07-04 17:20:56	2008-07-07 19:05:24
78	78	587	2008-07-04 17:20:56	2008-07-07 19:05:24
80	80	601.66666666699996	2008-07-04 17:20:57	2008-07-07 19:05:25
81	81	599.83333333300004	2008-07-04 17:20:57	2008-07-07 19:05:25
82	82	591.83333333300004	2008-07-04 17:20:57	2008-07-07 19:05:25
83	83	578.66666666699996	2008-07-04 17:20:57	2008-07-07 19:05:25
84	84	584.83333333300004	2008-07-04 17:20:57	2008-07-07 19:05:26
86	86	582	2008-07-04 17:20:57	2008-07-07 19:05:26
87	87	579.16666666699996	2008-07-04 17:20:57	2008-07-07 19:05:26
88	88	619.16666666699996	2008-07-04 17:20:57	2008-07-07 19:05:27
89	89	613.16666666699996	2008-07-04 17:20:57	2008-07-07 19:05:27
90	90	616.5	2008-07-04 17:20:57	2008-07-07 19:05:27
91	91	595.33333333300004	2008-07-04 17:20:57	2008-07-07 19:05:27
92	92	602	2008-07-04 17:20:57	2008-07-07 19:05:28
93	93	604.33333333300004	2008-07-04 17:20:57	2008-07-07 19:05:28
95	95	597.33333333300004	2008-07-04 17:20:57	2008-07-07 19:05:28
96	96	593.66666666699996	2008-07-04 17:20:57	2008-07-07 19:05:28
97	97	609	2008-07-04 17:20:58	2008-07-07 19:05:29
98	98	616	2008-07-04 17:20:58	2008-07-07 19:05:29
99	99	616	2008-07-04 17:20:58	2008-07-07 19:05:29
100	100	605	2008-07-04 17:20:58	2008-07-07 19:05:29
102	102	615.66666666699996	2008-07-04 17:20:58	2008-07-07 19:05:30
103	103	602.66666666699996	2008-07-04 17:20:58	2008-07-07 19:05:30
104	104	605	2008-07-04 17:20:58	2008-07-07 19:05:30
105	105	601	2008-07-04 17:20:58	2008-07-07 19:05:30
106	106	605	2008-07-04 17:20:58	2008-07-07 19:05:31
107	107	600	2008-07-04 17:20:58	2008-07-07 19:05:31
108	108	604	2008-07-04 17:20:58	2008-07-07 19:05:31
110	110	605.33333333300004	2008-07-04 17:20:58	2008-07-07 19:05:31
111	111	606.33333333300004	2008-07-04 17:20:58	2008-07-07 19:05:32
115	115	602.33333333300004	2008-07-04 17:20:59	2008-07-07 19:05:32
116	116	603.33333333300004	2008-07-04 17:20:59	2008-07-07 19:05:32
117	117	610	2008-07-04 17:20:59	2008-07-07 19:05:32
118	118	607.66666666699996	2008-07-04 17:20:59	2008-07-07 19:05:32
119	119	603	2008-07-04 17:20:59	2008-07-07 19:05:33
121	121	603.16666666699996	2008-07-04 17:20:59	2008-07-07 19:05:33
122	122	598.66666666699996	2008-07-04 17:20:59	2008-07-07 19:05:33
123	123	606.16666666699996	2008-07-04 17:20:59	2008-07-07 19:05:34
125	125	602.66666666699996	2008-07-04 17:20:59	2008-07-07 19:05:34
126	126	606	2008-07-04 17:20:59	2008-07-07 19:05:34
127	127	612	2008-07-04 17:20:59	2008-07-07 19:05:34
128	128	609	2008-07-04 17:20:59	2008-07-07 19:05:35
129	129	609	2008-07-04 17:20:59	2008-07-07 19:05:35
130	130	605.66666666699996	2008-07-04 17:20:59	2008-07-07 19:05:35
131	131	600.16666666699996	2008-07-04 17:20:59	2008-07-07 19:05:35
132	132	605.33333333300004	2008-07-04 17:20:59	2008-07-07 19:05:35
133	133	598.33333333300004	2008-07-04 17:21:00	2008-07-07 19:05:36
135	135	600.33333333300004	2008-07-04 17:21:00	2008-07-07 19:05:36
136	136	593.33333333300004	2008-07-04 17:21:00	2008-07-07 19:05:36
149	149	609	2008-07-04 17:21:01	2008-07-07 19:05:40
150	150	605.16666666699996	2008-07-04 17:21:01	2008-07-07 19:05:40
151	151	605	2008-07-04 17:21:01	2008-07-07 19:05:40
166	166	599.66666666699996	2008-07-04 17:21:01	2008-07-07 19:05:43
167	167	592	2008-07-04 17:21:01	2008-07-07 19:05:44
168	168	596.33333333300004	2008-07-04 17:21:02	2008-07-07 19:05:44
183	183	611	2008-07-04 17:21:02	2008-07-07 19:05:47
184	184	605	2008-07-04 17:21:02	2008-07-07 19:05:47
185	185	609	2008-07-04 17:21:02	2008-07-07 19:05:47
186	186	612	2008-07-04 17:21:02	2008-07-07 19:05:48
187	187	602	2008-07-04 17:21:03	2008-07-07 19:05:48
201	201	610	2008-07-04 17:21:03	2008-07-07 19:05:51
203	203	599.66666666699996	2008-07-04 17:21:03	2008-07-07 19:05:51
204	204	599.66666666699996	2008-07-04 17:21:03	2008-07-07 19:05:51
205	205	579.5	2008-07-04 17:21:04	2008-07-07 19:05:52
206	206	601.5	2008-07-04 17:21:04	2008-07-07 19:05:52
207	207	589.16666666699996	2008-07-04 17:21:04	2008-07-07 19:05:52
208	208	588.66666666699996	2008-07-04 17:21:04	2008-07-07 19:05:53
209	209	591.66666666699996	2008-07-04 17:21:04	2008-07-07 19:05:53
210	210	584	2008-07-04 17:21:04	2008-07-07 19:05:53
211	211	619.16666666699996	2008-07-04 17:21:04	2008-07-07 19:05:53
212	212	614.83333333300004	2008-07-04 17:21:04	2008-07-07 19:05:53
213	213	618.33333333300004	2008-07-04 17:21:04	2008-07-07 19:05:54
214	214	608.66666666699996	2008-07-04 17:21:04	2008-07-07 19:05:54
215	215	611	2008-07-04 17:21:04	2008-07-07 19:05:54
216	216	610	2008-07-04 17:21:04	2008-07-07 19:05:54
218	218	602	2008-07-04 17:21:04	2008-07-07 19:05:55
219	219	606.66666666699996	2008-07-04 17:21:04	2008-07-07 19:05:55
220	220	586.33333333300004	2008-07-04 17:21:04	2008-07-07 19:05:55
221	221	583.83333333300004	2008-07-04 17:21:05	2008-07-07 19:05:56
222	222	594.33333333300004	2008-07-04 17:21:05	2008-07-07 19:05:56
223	223	594.5	2008-07-29 10:40:29	2008-07-07 19:05:56
189	189	604.33333333300004	2008-07-04 17:21:03	2008-07-07 19:05:57
25	25	598.16666666699996	2008-07-04 17:20:54	2008-07-07 19:05:57
26	26	594	2008-07-04 17:20:54	2008-07-07 19:05:57
2	2	593	2008-07-04 17:20:52	2008-07-07 19:05:07
3	3	593	2008-07-04 17:20:52	2008-07-07 19:05:07
30	30	588.5	2008-07-04 17:20:54	2008-07-07 19:05:13
31	31	598.83333333300004	2008-07-04 17:20:54	2008-07-07 19:05:13
32	32	598.5	2008-07-04 17:20:54	2008-07-07 19:05:13
33	33	594.16666666699996	2008-07-04 17:20:54	2008-07-07 19:05:13
34	34	585.5	2008-07-04 17:20:54	2008-07-07 19:05:14
35	35	583.5	2008-07-04 17:20:54	2008-07-07 19:05:14
47	47	603	2008-07-04 17:20:55	2008-07-07 19:05:17
48	48	598	2008-07-04 17:20:55	2008-07-07 19:05:17
49	49	592	2008-07-04 17:20:55	2008-07-07 19:05:17
53	53	597	2008-07-04 17:20:55	2008-07-07 19:05:18
225	225	591.16666667000004	2008-07-29 10:40:29	2008-07-07 19:05:56
64	64	594.16666666699996	2008-07-04 17:20:55	2008-07-07 19:05:21
140	140	592.83333333300004	2008-07-04 17:21:00	2008-07-07 19:05:37
141	141	603.33333333300004	2008-07-04 17:21:00	2008-07-07 19:05:38
142	142	602.66666666699996	2008-07-04 17:21:00	2008-07-07 19:05:38
143	143	608.33333333300004	2008-07-04 17:21:00	2008-07-07 19:05:38
144	144	601	2008-07-04 17:21:00	2008-07-07 19:05:38
145	145	592.5	2008-07-04 17:21:00	2008-07-07 19:05:39
146	146	598.33333333300004	2008-07-04 17:21:00	2008-07-07 19:05:39
147	147	595	2008-07-04 17:21:00	2008-07-07 19:05:39
148	148	600	2008-07-04 17:21:01	2008-07-07 19:05:39
152	152	593.66666666699996	2008-07-04 17:21:01	2008-07-07 19:05:40
153	153	596	2008-07-04 17:21:01	2008-07-07 19:05:40
154	154	605.66666666699996	2008-07-04 17:21:01	2008-07-07 19:05:41
155	155	603.83333333300004	2008-07-04 17:21:01	2008-07-07 19:05:41
156	156	602.5	2008-07-04 17:21:01	2008-07-07 19:05:41
157	157	620	2008-07-04 17:21:01	2008-07-07 19:05:41
158	158	616	2008-07-04 17:21:01	2008-07-07 19:05:41
159	159	618	2008-07-04 17:21:01	2008-07-07 19:05:42
160	160	603.66666666699996	2008-07-04 17:21:01	2008-07-07 19:05:42
161	161	608.66666666699996	2008-07-04 17:21:01	2008-07-07 19:05:42
162	162	601.33333333300004	2008-07-04 17:21:01	2008-07-07 19:05:42
163	163	599.33333333300004	2008-07-04 17:21:01	2008-07-07 19:05:42
164	164	601	2008-07-04 17:21:01	2008-07-07 19:05:43
165	165	598	2008-07-04 17:21:01	2008-07-07 19:05:43
169	169	624.16666666699996	2008-07-04 17:21:02	2008-07-07 19:05:44
170	170	625.83333333300004	2008-07-04 17:21:02	2008-07-07 19:05:44
171	171	616.83333333300004	2008-07-04 17:21:02	2008-07-07 19:05:45
172	172	617	2008-07-04 17:21:02	2008-07-07 19:05:45
173	173	620	2008-07-04 17:21:02	2008-07-07 19:05:45
174	174	619.5	2008-07-04 17:21:02	2008-07-07 19:05:45
180	180	610.33333333300004	2008-07-04 17:21:02	2008-07-07 19:05:46
181	181	608	2008-07-04 17:21:02	2008-07-07 19:05:47
182	182	605	2008-07-04 17:21:02	2008-07-07 19:05:47
188	188	600.5	2008-07-04 17:21:03	2008-07-07 19:05:48
190	190	599.66666666699996	2008-07-04 17:21:03	2008-07-07 19:05:48
191	191	596.5	2008-07-04 17:21:03	2008-07-07 19:05:49
192	192	599.5	2008-07-04 17:21:03	2008-07-07 19:05:49
193	193	591.83333333300004	2008-07-04 17:21:03	2008-07-07 19:05:49
194	194	593.66666666699996	2008-07-04 17:21:03	2008-07-07 19:05:49
195	195	592	2008-07-04 17:21:03	2008-07-07 19:05:49
196	196	591	2008-07-04 17:21:03	2008-07-07 19:05:50
197	197	596.5	2008-07-04 17:21:03	2008-07-07 19:05:50
198	198	595	2008-07-04 17:21:03	2008-07-07 19:05:50
199	199	606	2008-07-04 17:21:03	2008-07-07 19:05:50
200	200	601	2008-07-04 17:21:03	2008-07-07 19:05:50
202	202	596.33333333300004	2008-07-04 17:21:03	2008-07-07 19:05:51
217	217	598.66666666699996	2008-07-04 17:21:04	2008-07-07 19:05:55
1	1	596	2008-07-04 17:20:52	2008-07-07 19:05:06
4	4	595.66666666699996	2008-07-04 17:20:52	2008-07-07 19:05:07
16	16	604.66666666699996	2008-07-04 17:20:53	2008-07-07 19:05:10
17	17	605	2008-07-04 17:20:53	2008-07-07 19:05:10
18	18	605	2008-07-04 17:20:53	2008-07-07 19:05:10
19	19	608	2008-07-04 17:20:53	2008-07-07 19:05:10
20	20	603.66666666699996	2008-07-04 17:20:53	2008-07-07 19:05:11
21	21	604.66666666699996	2008-07-04 17:20:53	2008-07-07 19:05:11
22	22	596.16666666699996	2008-07-04 17:20:53	2008-07-07 19:05:11
23	23	593.83333333300004	2008-07-04 17:20:53	2008-07-07 19:05:11
24	24	592.5	2008-07-04 17:20:53	2008-07-07 19:05:12
27	27	592.16666666699996	2008-07-04 17:20:54	2008-07-07 19:05:12
28	28	595	2008-07-04 17:20:54	2008-07-07 19:05:12
29	29	597.16666666699996	2008-07-04 17:20:54	2008-07-07 19:05:12
36	36	586.33333333300004	2008-07-04 17:20:54	2008-07-07 19:05:14
37	37	585.33333333300004	2008-07-04 17:20:54	2008-07-07 19:05:14
38	38	582.66666666699996	2008-07-04 17:20:54	2008-07-07 19:05:15
39	39	586.33333333300004	2008-07-04 17:20:54	2008-07-07 19:05:15
40	40	584.33333333300004	2008-07-04 17:20:54	2008-07-07 19:05:15
41	41	575.33333333300004	2008-07-04 17:20:54	2008-07-07 19:05:15
42	42	579.83333333300004	2008-07-04 17:20:54	2008-07-07 19:05:16
43	43	609.33333333300004	2008-07-04 17:20:54	2008-07-07 19:05:16
44	44	605.33333333300004	2008-07-04 17:20:54	2008-07-07 19:05:16
69	69	595.66666666699996	2008-07-04 17:20:56	2008-07-07 19:05:22
79	79	605.16666666699996	2008-07-04 17:20:57	2008-07-07 19:05:24
85	85	579	2008-07-04 17:20:57	2008-07-07 19:05:26
94	94	609	2008-07-04 17:20:57	2008-07-07 19:05:28
101	101	607.66666666699996	2008-07-04 17:20:58	2008-07-07 19:05:29
109	109	605.66666666699996	2008-07-04 17:20:58	2008-07-07 19:05:31
120	120	599	2008-07-04 17:20:59	2008-07-07 19:05:33
124	124	601	2008-07-04 17:20:59	2008-07-07 19:05:34
134	134	605	2008-07-04 17:21:00	2008-07-07 19:05:36
137	137	589.16666666699996	2008-07-04 17:21:00	2008-07-07 19:05:37
138	138	595.33333333300004	2008-07-04 17:21:00	2008-07-07 19:05:37
139	139	600.16666666699996	2008-07-04 17:21:00	2008-07-07 19:05:37
175	175	607.33333333300004	2008-07-04 17:21:02	2008-07-07 19:05:45
176	176	611.33333333300004	2008-07-04 17:21:02	2008-07-07 19:05:46
177	177	610	2008-07-04 17:21:02	2008-07-07 19:05:46
178	178	614.33333333300004	2008-07-04 17:21:02	2008-07-07 19:05:46
179	179	616	2008-07-04 17:21:02	2008-07-07 19:05:46
45	45	601.66666666699996	2008-07-04 17:20:54	2008-07-07 19:05:16
46	46	607	2008-07-04 17:20:54	2008-07-07 19:05:16
224	224	593	2008-07-29 10:40:29	2008-07-07 19:05:56
\.


--
-- Data for Name: team_score_sheets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY team_score_sheets (id, adjudicator_allocation_id, debate_team_xref_id, score, created_at, updated_at) FROM stdin;
1	16	31	1	2008-07-29 11:27:26	2008-07-29 11:27:26
2	16	32	0	2008-07-29 11:27:26	2008-07-29 11:27:26
3	7	13	0	2008-07-29 11:32:27	2008-07-29 11:32:27
4	7	14	1	2008-07-29 11:32:27	2008-07-29 11:32:27
5	26	51	0	2008-07-29 11:34:26	2008-07-29 11:34:26
6	26	52	1	2008-07-29 11:34:26	2008-07-29 11:34:26
7	4	7	1	2008-07-29 11:34:43	2008-07-29 11:34:43
8	4	8	0	2008-07-29 11:34:43	2008-07-29 11:34:43
9	21	41	1	2008-07-29 11:36:33	2008-07-29 11:36:33
10	21	42	0	2008-07-29 11:36:34	2008-07-29 11:36:34
11	6	11	1	2008-07-29 11:38:34	2008-07-29 11:38:34
12	6	12	0	2008-07-29 11:38:34	2008-07-29 11:38:34
13	51	69	0	2008-07-29 11:39:42	2008-07-29 11:39:42
14	51	70	1	2008-07-29 11:39:42	2008-07-29 11:39:42
15	52	69	0	2008-07-29 11:39:42	2008-07-29 11:39:42
16	52	70	1	2008-07-29 11:39:42	2008-07-29 11:39:42
17	53	69	0	2008-07-29 11:39:42	2008-07-29 11:39:42
18	53	70	1	2008-07-29 11:39:42	2008-07-29 11:39:42
19	3	5	1	2008-07-29 11:41:35	2008-07-29 11:41:35
20	3	6	0	2008-07-29 11:41:35	2008-07-29 11:41:35
21	15	29	0	2008-07-29 11:43:03	2008-07-29 11:43:03
22	15	30	1	2008-07-29 11:43:03	2008-07-29 11:43:03
23	36	59	1	2008-07-29 11:43:51	2008-07-29 11:43:51
24	36	60	0	2008-07-29 11:43:51	2008-07-29 11:43:51
25	38	59	1	2008-07-29 11:43:51	2008-07-29 11:43:51
26	38	60	0	2008-07-29 11:43:51	2008-07-29 11:43:51
27	37	59	1	2008-07-29 11:43:51	2008-07-29 11:43:51
28	37	60	0	2008-07-29 11:43:51	2008-07-29 11:43:51
29	9	17	0	2008-07-29 11:45:36	2008-07-29 11:45:36
30	9	18	1	2008-07-29 11:45:36	2008-07-29 11:45:36
31	2	3	0	2008-07-29 11:47:04	2008-07-29 11:47:04
32	2	4	1	2008-07-29 11:47:04	2008-07-29 11:47:04
33	34	57	1	2008-07-29 11:47:41	2008-07-29 11:47:41
34	34	58	0	2008-07-29 11:47:41	2008-07-29 11:47:41
35	35	57	1	2008-07-29 11:47:41	2008-07-29 11:47:41
36	35	58	0	2008-07-29 11:47:41	2008-07-29 11:47:41
37	33	57	1	2008-07-29 11:47:41	2008-07-29 11:47:41
38	33	58	0	2008-07-29 11:47:41	2008-07-29 11:47:41
39	17	33	0	2008-07-29 11:49:16	2008-07-29 11:49:16
40	17	34	1	2008-07-29 11:49:16	2008-07-29 11:49:16
41	19	37	0	2008-07-29 11:52:28	2008-07-29 11:52:28
42	19	38	1	2008-07-29 11:52:29	2008-07-29 11:52:29
43	8	15	0	2008-07-29 11:54:24	2008-07-29 11:54:24
44	8	16	1	2008-07-29 11:54:24	2008-07-29 11:54:24
45	45	65	0	2008-07-29 11:55:32	2008-07-29 11:55:32
46	45	66	1	2008-07-29 11:55:32	2008-07-29 11:55:32
47	46	65	0	2008-07-29 11:55:32	2008-07-29 11:55:32
48	46	66	1	2008-07-29 11:55:32	2008-07-29 11:55:32
49	47	65	0	2008-07-29 11:55:32	2008-07-29 11:55:32
50	47	66	1	2008-07-29 11:55:32	2008-07-29 11:55:32
51	25	49	1	2008-07-29 11:56:27	2008-07-29 11:56:27
52	25	50	0	2008-07-29 11:56:27	2008-07-29 11:56:27
53	11	21	1	2008-07-29 11:58:13	2008-07-29 11:58:13
54	11	22	0	2008-07-29 11:58:13	2008-07-29 11:58:13
55	18	35	1	2008-07-29 11:59:39	2008-07-29 11:59:39
56	18	36	0	2008-07-29 11:59:39	2008-07-29 11:59:39
57	57	73	0	2008-07-29 11:59:48	2008-07-29 11:59:48
58	57	74	1	2008-07-29 11:59:48	2008-07-29 11:59:48
59	58	73	0	2008-07-29 11:59:48	2008-07-29 11:59:48
60	58	74	1	2008-07-29 11:59:48	2008-07-29 11:59:48
61	59	73	0	2008-07-29 11:59:48	2008-07-29 11:59:48
62	59	74	1	2008-07-29 11:59:48	2008-07-29 11:59:48
63	5	9	0	2008-07-29 12:01:03	2008-07-29 12:01:03
64	5	10	1	2008-07-29 12:01:03	2008-07-29 12:01:03
65	13	25	0	2008-07-29 12:02:30	2008-07-29 12:02:30
66	13	26	1	2008-07-29 12:02:30	2008-07-29 12:02:30
67	23	45	1	2008-07-29 12:02:42	2008-07-29 12:02:42
68	23	46	0	2008-07-29 12:02:42	2008-07-29 12:02:42
69	22	43	0	2008-07-29 12:03:55	2008-07-29 12:03:55
70	22	44	1	2008-07-29 12:03:55	2008-07-29 12:03:55
71	24	47	0	2008-07-29 12:05:18	2008-07-29 12:05:18
72	24	48	1	2008-07-29 12:05:18	2008-07-29 12:05:18
73	14	27	1	2008-07-29 12:05:22	2008-07-29 12:05:22
74	14	28	0	2008-07-29 12:05:22	2008-07-29 12:05:22
75	48	67	1	2008-07-29 12:05:55	2008-07-29 12:05:55
76	48	68	0	2008-07-29 12:05:55	2008-07-29 12:05:55
77	49	67	1	2008-07-29 12:05:55	2008-07-29 12:05:55
78	49	68	0	2008-07-29 12:05:55	2008-07-29 12:05:55
79	50	67	1	2008-07-29 12:05:55	2008-07-29 12:05:55
80	50	68	0	2008-07-29 12:05:55	2008-07-29 12:05:55
81	12	23	0	2008-07-29 12:07:47	2008-07-29 12:07:47
82	12	24	1	2008-07-29 12:07:47	2008-07-29 12:07:47
83	27	53	1	2008-07-29 12:09:25	2008-07-29 12:09:25
84	27	54	0	2008-07-29 12:09:25	2008-07-29 12:09:25
85	28	53	1	2008-07-29 12:09:25	2008-07-29 12:09:25
86	28	54	0	2008-07-29 12:09:25	2008-07-29 12:09:25
87	29	53	1	2008-07-29 12:09:25	2008-07-29 12:09:25
88	29	54	0	2008-07-29 12:09:25	2008-07-29 12:09:25
89	10	19	0	2008-07-29 12:11:35	2008-07-29 12:11:35
90	10	20	1	2008-07-29 12:11:35	2008-07-29 12:11:35
91	42	63	1	2008-07-29 12:13:06	2008-07-29 12:13:06
92	42	64	0	2008-07-29 12:13:06	2008-07-29 12:13:06
93	43	63	1	2008-07-29 12:13:06	2008-07-29 12:13:06
94	43	64	0	2008-07-29 12:13:06	2008-07-29 12:13:06
95	44	63	1	2008-07-29 12:13:06	2008-07-29 12:13:06
96	44	64	0	2008-07-29 12:13:06	2008-07-29 12:13:06
97	40	61	0	2008-07-29 12:14:28	2008-07-29 12:14:28
98	40	62	1	2008-07-29 12:14:28	2008-07-29 12:14:28
99	41	61	0	2008-07-29 12:14:28	2008-07-29 12:14:28
100	41	62	1	2008-07-29 12:14:28	2008-07-29 12:14:28
101	39	61	0	2008-07-29 12:14:28	2008-07-29 12:14:28
102	39	62	1	2008-07-29 12:14:28	2008-07-29 12:14:28
103	30	55	0	2008-07-29 12:15:00	2008-07-29 12:15:00
104	30	56	1	2008-07-29 12:15:00	2008-07-29 12:15:00
105	31	55	0	2008-07-29 12:15:00	2008-07-29 12:15:00
106	31	56	1	2008-07-29 12:15:00	2008-07-29 12:15:00
107	32	55	0	2008-07-29 12:15:00	2008-07-29 12:15:00
108	32	56	1	2008-07-29 12:15:00	2008-07-29 12:15:00
109	1	1	1	2008-07-29 12:15:43	2008-07-29 12:15:43
110	1	2	0	2008-07-29 12:15:43	2008-07-29 12:15:43
111	20	39	1	2008-07-29 12:18:55	2008-07-29 12:18:55
112	20	40	0	2008-07-29 12:18:55	2008-07-29 12:18:55
113	54	71	0	2008-07-29 12:19:40	2008-07-29 12:19:40
114	54	72	1	2008-07-29 12:19:40	2008-07-29 12:19:40
115	55	71	0	2008-07-29 12:19:40	2008-07-29 12:19:40
116	55	72	1	2008-07-29 12:19:40	2008-07-29 12:19:40
117	56	71	0	2008-07-29 12:19:40	2008-07-29 12:19:40
118	56	72	1	2008-07-29 12:19:40	2008-07-29 12:19:40
119	61	77	1	2008-07-29 15:27:32	2008-07-29 15:27:32
120	61	78	0	2008-07-29 15:27:32	2008-07-29 15:27:32
121	60	75	0	2008-07-29 15:28:15	2008-07-29 15:28:15
122	60	76	1	2008-07-29 15:28:15	2008-07-29 15:28:15
123	62	79	0	2008-07-29 15:30:15	2008-07-29 15:30:15
124	62	80	1	2008-07-29 15:30:15	2008-07-29 15:30:15
125	81	117	0	2008-07-29 15:31:37	2008-07-29 15:31:37
126	81	118	1	2008-07-29 15:31:37	2008-07-29 15:31:37
127	78	111	1	2008-07-29 15:32:59	2008-07-29 15:32:59
128	78	112	0	2008-07-29 15:32:59	2008-07-29 15:32:59
129	79	113	1	2008-07-29 15:33:24	2008-07-29 15:33:24
130	79	114	0	2008-07-29 15:33:24	2008-07-29 15:33:24
131	65	95	1	2008-07-29 15:35:21	2008-07-29 15:35:21
132	65	96	0	2008-07-29 15:35:21	2008-07-29 15:35:21
133	76	105	1	2008-07-29 15:35:25	2008-07-29 15:35:25
134	76	106	0	2008-07-29 15:35:25	2008-07-29 15:35:25
137	71	103	0	2008-07-29 15:36:18	2008-07-29 15:36:18
138	71	104	1	2008-07-29 15:36:18	2008-07-29 15:36:18
139	63	81	0	2008-07-29 15:36:45	2008-07-29 15:36:45
140	63	82	1	2008-07-29 15:36:45	2008-07-29 15:36:45
141	90	115	1	2008-07-29 15:39:21	2008-07-29 15:39:21
142	90	116	0	2008-07-29 15:39:21	2008-07-29 15:39:21
143	91	115	1	2008-07-29 15:39:21	2008-07-29 15:39:21
144	91	116	0	2008-07-29 15:39:21	2008-07-29 15:39:21
145	92	115	0	2008-07-29 15:39:21	2008-07-29 15:39:21
146	92	116	1	2008-07-29 15:39:21	2008-07-29 15:39:21
147	83	129	0	2008-07-29 15:40:31	2008-07-29 15:40:31
148	83	130	1	2008-07-29 15:40:31	2008-07-29 15:40:31
149	87	127	1	2008-07-29 15:42:04	2008-07-29 15:42:04
150	87	128	0	2008-07-29 15:42:04	2008-07-29 15:42:04
151	89	127	1	2008-07-29 15:42:04	2008-07-29 15:42:04
152	89	128	0	2008-07-29 15:42:04	2008-07-29 15:42:04
153	88	127	1	2008-07-29 15:42:04	2008-07-29 15:42:04
154	88	128	0	2008-07-29 15:42:04	2008-07-29 15:42:04
155	108	139	1	2008-07-29 15:44:35	2008-07-29 15:44:35
156	108	140	0	2008-07-29 15:44:35	2008-07-29 15:44:35
157	109	139	1	2008-07-29 15:44:35	2008-07-29 15:44:35
158	109	140	0	2008-07-29 15:44:35	2008-07-29 15:44:35
159	110	139	1	2008-07-29 15:44:35	2008-07-29 15:44:35
160	110	140	0	2008-07-29 15:44:35	2008-07-29 15:44:35
161	120	147	0	2008-07-29 15:45:05	2008-07-29 15:45:05
162	120	148	1	2008-07-29 15:45:05	2008-07-29 15:45:05
163	105	141	0	2008-07-29 15:45:21	2008-07-29 15:45:21
164	105	142	1	2008-07-29 15:45:21	2008-07-29 15:45:21
165	106	141	0	2008-07-29 15:45:21	2008-07-29 15:45:21
166	106	142	1	2008-07-29 15:45:21	2008-07-29 15:45:21
167	107	141	0	2008-07-29 15:45:21	2008-07-29 15:45:21
168	107	142	1	2008-07-29 15:45:21	2008-07-29 15:45:21
171	69	93	1	2008-07-29 15:47:34	2008-07-29 15:47:34
172	69	94	0	2008-07-29 15:47:34	2008-07-29 15:47:34
173	84	137	0	2008-07-29 15:48:33	2008-07-29 15:48:33
174	84	138	1	2008-07-29 15:48:33	2008-07-29 15:48:33
175	85	137	0	2008-07-29 15:48:33	2008-07-29 15:48:33
176	85	138	1	2008-07-29 15:48:33	2008-07-29 15:48:33
177	86	137	0	2008-07-29 15:48:33	2008-07-29 15:48:33
178	86	138	1	2008-07-29 15:48:33	2008-07-29 15:48:33
179	67	97	0	2008-07-29 15:50:11	2008-07-29 15:50:11
180	67	98	1	2008-07-29 15:50:11	2008-07-29 15:50:11
181	117	145	0	2008-07-29 15:51:32	2008-07-29 15:51:32
182	117	146	1	2008-07-29 15:51:32	2008-07-29 15:51:32
183	118	145	0	2008-07-29 15:51:32	2008-07-29 15:51:32
184	118	146	1	2008-07-29 15:51:32	2008-07-29 15:51:32
185	119	145	0	2008-07-29 15:51:32	2008-07-29 15:51:32
186	119	146	1	2008-07-29 15:51:32	2008-07-29 15:51:32
187	96	131	1	2008-07-29 15:52:49	2008-07-29 15:52:49
188	96	132	0	2008-07-29 15:52:49	2008-07-29 15:52:49
189	97	131	0	2008-07-29 15:52:49	2008-07-29 15:52:49
190	97	132	1	2008-07-29 15:52:49	2008-07-29 15:52:49
191	98	131	1	2008-07-29 15:52:49	2008-07-29 15:52:49
192	98	132	0	2008-07-29 15:52:49	2008-07-29 15:52:49
193	93	143	1	2008-07-29 15:53:39	2008-07-29 15:53:39
194	93	144	0	2008-07-29 15:53:39	2008-07-29 15:53:39
195	94	143	1	2008-07-29 15:53:39	2008-07-29 15:53:39
196	94	144	0	2008-07-29 15:53:39	2008-07-29 15:53:39
197	95	143	1	2008-07-29 15:53:39	2008-07-29 15:53:39
198	95	144	0	2008-07-29 15:53:39	2008-07-29 15:53:39
199	80	119	0	2008-07-29 15:53:56	2008-07-29 15:53:56
200	80	120	1	2008-07-29 15:53:56	2008-07-29 15:53:56
201	99	133	1	2008-07-29 15:54:41	2008-07-29 15:54:41
202	99	134	0	2008-07-29 15:54:41	2008-07-29 15:54:41
203	101	133	1	2008-07-29 15:54:41	2008-07-29 15:54:41
204	101	134	0	2008-07-29 15:54:41	2008-07-29 15:54:41
205	100	133	0	2008-07-29 15:54:41	2008-07-29 15:54:41
206	100	134	1	2008-07-29 15:54:41	2008-07-29 15:54:41
207	74	109	1	2008-07-29 15:55:24	2008-07-29 15:55:24
208	74	110	0	2008-07-29 15:55:24	2008-07-29 15:55:24
209	70	99	1	2008-07-29 15:56:23	2008-07-29 15:56:23
210	70	100	0	2008-07-29 15:56:23	2008-07-29 15:56:23
213	68	91	1	2008-07-29 15:57:02	2008-07-29 15:57:02
214	68	92	0	2008-07-29 15:57:02	2008-07-29 15:57:02
215	64	107	0	2008-07-29 15:59:30	2008-07-29 15:59:30
216	64	108	1	2008-07-29 15:59:30	2008-07-29 15:59:30
217	114	121	0	2008-07-29 15:59:32	2008-07-29 15:59:32
218	114	122	1	2008-07-29 15:59:32	2008-07-29 15:59:32
219	115	121	0	2008-07-29 15:59:32	2008-07-29 15:59:32
220	115	122	1	2008-07-29 15:59:32	2008-07-29 15:59:32
221	116	121	1	2008-07-29 15:59:32	2008-07-29 15:59:32
222	116	122	0	2008-07-29 15:59:32	2008-07-29 15:59:32
223	72	87	0	2008-07-29 15:59:39	2008-07-29 15:59:39
224	72	88	1	2008-07-29 15:59:39	2008-07-29 15:59:39
225	111	123	1	2008-07-29 16:02:17	2008-07-29 16:02:17
226	111	124	0	2008-07-29 16:02:17	2008-07-29 16:02:17
227	112	123	1	2008-07-29 16:02:17	2008-07-29 16:02:17
228	112	124	0	2008-07-29 16:02:17	2008-07-29 16:02:17
229	113	123	0	2008-07-29 16:02:17	2008-07-29 16:02:17
230	113	124	1	2008-07-29 16:02:17	2008-07-29 16:02:17
231	75	89	0	2008-07-29 16:03:45	2008-07-29 16:03:45
232	75	90	1	2008-07-29 16:03:45	2008-07-29 16:03:45
233	102	135	1	2008-07-29 16:04:37	2008-07-29 16:04:37
234	102	136	0	2008-07-29 16:04:37	2008-07-29 16:04:37
235	103	135	1	2008-07-29 16:04:37	2008-07-29 16:04:37
236	103	136	0	2008-07-29 16:04:37	2008-07-29 16:04:37
237	104	135	1	2008-07-29 16:04:37	2008-07-29 16:04:37
238	104	136	0	2008-07-29 16:04:37	2008-07-29 16:04:37
239	77	85	0	2008-07-29 16:06:22	2008-07-29 16:06:22
240	77	86	1	2008-07-29 16:06:23	2008-07-29 16:06:23
241	82	125	0	2008-07-29 16:07:01	2008-07-29 16:07:01
242	82	126	1	2008-07-29 16:07:01	2008-07-29 16:07:01
243	66	83	1	2008-07-29 16:08:23	2008-07-29 16:08:23
244	66	84	0	2008-07-29 16:08:23	2008-07-29 16:08:23
245	73	101	0	2008-07-29 16:11:16	2008-07-29 16:11:16
246	73	102	1	2008-07-29 16:11:16	2008-07-29 16:11:16
247	125	155	1	2008-07-29 18:46:58	2008-07-29 18:46:58
248	125	156	0	2008-07-29 18:46:58	2008-07-29 18:46:58
249	133	193	0	2008-07-29 18:50:04	2008-07-29 18:50:04
250	133	194	1	2008-07-29 18:50:04	2008-07-29 18:50:04
251	139	195	0	2008-07-29 18:51:17	2008-07-29 18:51:17
252	139	196	1	2008-07-29 18:51:17	2008-07-29 18:51:17
253	163	211	0	2008-07-29 18:55:43	2008-07-29 18:55:43
254	163	212	1	2008-07-29 18:55:43	2008-07-29 18:55:43
255	164	211	0	2008-07-29 18:55:43	2008-07-29 18:55:43
256	164	212	1	2008-07-29 18:55:43	2008-07-29 18:55:43
257	165	211	0	2008-07-29 18:55:43	2008-07-29 18:55:43
258	165	212	1	2008-07-29 18:55:43	2008-07-29 18:55:43
259	121	149	1	2008-07-29 18:56:33	2008-07-29 18:56:33
260	121	150	0	2008-07-29 18:56:33	2008-07-29 18:56:33
261	151	199	0	2008-07-29 18:57:29	2008-07-29 18:57:29
262	151	200	1	2008-07-29 18:57:29	2008-07-29 18:57:29
263	152	199	0	2008-07-29 18:57:29	2008-07-29 18:57:29
264	152	200	1	2008-07-29 18:57:29	2008-07-29 18:57:29
265	153	199	0	2008-07-29 18:57:29	2008-07-29 18:57:29
266	153	200	1	2008-07-29 18:57:29	2008-07-29 18:57:29
267	122	151	0	2008-07-29 18:57:51	2008-07-29 18:57:51
268	122	152	1	2008-07-29 18:57:51	2008-07-29 18:57:51
269	127	159	1	2008-07-29 18:58:27	2008-07-29 18:58:27
270	127	160	0	2008-07-29 18:58:27	2008-07-29 18:58:27
271	141	189	0	2008-07-29 18:59:56	2008-07-29 18:59:56
272	141	190	1	2008-07-29 18:59:56	2008-07-29 18:59:56
273	123	153	1	2008-07-29 19:00:04	2008-07-29 19:00:04
274	123	154	0	2008-07-29 19:00:04	2008-07-29 19:00:04
275	138	191	0	2008-07-29 19:01:16	2008-07-29 19:01:16
276	138	192	1	2008-07-29 19:01:16	2008-07-29 19:01:16
277	144	185	0	2008-07-29 19:03:07	2008-07-29 19:03:07
278	144	186	1	2008-07-29 19:03:07	2008-07-29 19:03:07
279	145	185	0	2008-07-29 19:03:07	2008-07-29 19:03:07
280	145	186	1	2008-07-29 19:03:07	2008-07-29 19:03:07
281	146	185	1	2008-07-29 19:03:07	2008-07-29 19:03:07
282	146	186	0	2008-07-29 19:03:07	2008-07-29 19:03:07
283	126	161	1	2008-07-29 19:03:38	2008-07-29 19:03:38
284	126	162	0	2008-07-29 19:03:38	2008-07-29 19:03:38
285	181	221	1	2008-07-29 19:04:31	2008-07-29 19:04:31
286	181	222	0	2008-07-29 19:04:31	2008-07-29 19:04:31
287	135	171	0	2008-07-29 19:04:49	2008-07-29 19:04:49
288	135	172	1	2008-07-29 19:04:49	2008-07-29 19:04:49
289	129	165	0	2008-07-29 19:04:53	2008-07-29 19:04:53
290	129	166	1	2008-07-29 19:04:53	2008-07-29 19:04:53
291	130	167	1	2008-07-29 19:06:06	2008-07-29 19:06:06
292	130	168	0	2008-07-29 19:06:06	2008-07-29 19:06:06
293	157	205	0	2008-07-29 19:06:08	2008-07-29 19:06:08
294	157	206	1	2008-07-29 19:06:08	2008-07-29 19:06:08
295	158	205	0	2008-07-29 19:06:08	2008-07-29 19:06:08
296	158	206	1	2008-07-29 19:06:08	2008-07-29 19:06:08
297	159	205	0	2008-07-29 19:06:08	2008-07-29 19:06:08
298	159	206	1	2008-07-29 19:06:08	2008-07-29 19:06:08
299	124	157	0	2008-07-29 19:06:12	2008-07-29 19:06:12
300	124	158	1	2008-07-29 19:06:12	2008-07-29 19:06:12
301	166	207	1	2008-07-29 19:07:08	2008-07-29 19:07:08
302	166	208	0	2008-07-29 19:07:08	2008-07-29 19:07:08
303	167	207	1	2008-07-29 19:07:08	2008-07-29 19:07:08
304	167	208	0	2008-07-29 19:07:08	2008-07-29 19:07:08
305	168	207	1	2008-07-29 19:07:08	2008-07-29 19:07:08
306	168	208	0	2008-07-29 19:07:08	2008-07-29 19:07:08
307	147	201	0	2008-07-29 19:07:09	2008-07-29 19:07:09
308	147	202	1	2008-07-29 19:07:09	2008-07-29 19:07:09
309	128	163	0	2008-07-29 19:07:44	2008-07-29 19:07:44
310	128	164	1	2008-07-29 19:07:44	2008-07-29 19:07:44
311	154	203	1	2008-07-29 19:09:11	2008-07-29 19:09:11
312	154	204	0	2008-07-29 19:09:11	2008-07-29 19:09:11
313	155	203	1	2008-07-29 19:09:11	2008-07-29 19:09:11
314	155	204	0	2008-07-29 19:09:11	2008-07-29 19:09:11
315	156	203	0	2008-07-29 19:09:11	2008-07-29 19:09:11
316	156	204	1	2008-07-29 19:09:11	2008-07-29 19:09:11
317	137	187	0	2008-07-29 19:14:12	2008-07-29 19:14:12
318	137	188	1	2008-07-29 19:14:12	2008-07-29 19:14:12
319	172	215	0	2008-07-29 19:27:05	2008-07-29 19:27:05
320	172	216	1	2008-07-29 19:27:05	2008-07-29 19:27:05
321	173	215	0	2008-07-29 19:27:05	2008-07-29 19:27:05
322	173	216	1	2008-07-29 19:27:05	2008-07-29 19:27:05
323	174	215	0	2008-07-29 19:27:05	2008-07-29 19:27:05
324	174	216	1	2008-07-29 19:27:05	2008-07-29 19:27:05
325	175	217	1	2008-07-29 19:27:51	2008-07-29 19:27:51
326	175	218	0	2008-07-29 19:27:51	2008-07-29 19:27:51
327	176	217	1	2008-07-29 19:27:51	2008-07-29 19:27:51
328	176	218	0	2008-07-29 19:27:51	2008-07-29 19:27:51
329	177	217	1	2008-07-29 19:27:51	2008-07-29 19:27:51
330	177	218	0	2008-07-29 19:27:51	2008-07-29 19:27:51
331	169	213	0	2008-07-29 19:28:00	2008-07-29 19:28:00
332	169	214	1	2008-07-29 19:28:00	2008-07-29 19:28:00
333	170	213	0	2008-07-29 19:28:00	2008-07-29 19:28:00
334	170	214	1	2008-07-29 19:28:00	2008-07-29 19:28:00
335	171	213	0	2008-07-29 19:28:00	2008-07-29 19:28:00
336	171	214	1	2008-07-29 19:28:00	2008-07-29 19:28:00
337	136	181	1	2008-07-29 19:29:07	2008-07-29 19:29:07
338	136	182	0	2008-07-29 19:29:08	2008-07-29 19:29:08
339	143	175	0	2008-07-29 19:29:45	2008-07-29 19:29:45
340	143	176	1	2008-07-29 19:29:45	2008-07-29 19:29:45
347	178	219	0	2008-07-29 19:30:37	2008-07-29 19:30:37
348	178	220	1	2008-07-29 19:30:37	2008-07-29 19:30:37
349	179	219	1	2008-07-29 19:30:37	2008-07-29 19:30:37
350	179	220	0	2008-07-29 19:30:37	2008-07-29 19:30:37
351	180	219	0	2008-07-29 19:30:37	2008-07-29 19:30:37
352	180	220	1	2008-07-29 19:30:37	2008-07-29 19:30:37
353	134	173	1	2008-07-29 19:31:20	2008-07-29 19:31:20
354	134	174	0	2008-07-29 19:31:20	2008-07-29 19:31:20
355	148	197	1	2008-07-29 19:31:22	2008-07-29 19:31:22
356	148	198	0	2008-07-29 19:31:22	2008-07-29 19:31:22
357	149	197	1	2008-07-29 19:31:22	2008-07-29 19:31:22
358	149	198	0	2008-07-29 19:31:22	2008-07-29 19:31:22
359	150	197	1	2008-07-29 19:31:22	2008-07-29 19:31:22
360	150	198	0	2008-07-29 19:31:22	2008-07-29 19:31:22
367	140	179	0	2008-07-29 19:32:43	2008-07-29 19:32:43
368	140	180	1	2008-07-29 19:32:43	2008-07-29 19:32:43
369	132	169	1	2008-07-29 19:32:54	2008-07-29 19:32:54
370	132	170	0	2008-07-29 19:32:54	2008-07-29 19:32:54
371	142	183	0	2008-07-29 19:33:45	2008-07-29 19:33:45
372	142	184	1	2008-07-29 19:33:45	2008-07-29 19:33:45
375	131	177	0	2008-07-29 19:36:11	2008-07-29 19:36:11
376	131	178	1	2008-07-29 19:36:11	2008-07-29 19:36:11
377	160	209	1	2008-07-29 19:39:18	2008-07-29 19:39:18
378	160	210	0	2008-07-29 19:39:18	2008-07-29 19:39:18
379	161	209	0	2008-07-29 19:39:18	2008-07-29 19:39:18
380	161	210	1	2008-07-29 19:39:18	2008-07-29 19:39:18
381	162	209	1	2008-07-29 19:39:18	2008-07-29 19:39:18
382	162	210	0	2008-07-29 19:39:18	2008-07-29 19:39:18
383	200	255	1	2008-07-06 11:35:46	2008-07-06 11:35:46
384	200	256	0	2008-07-06 11:35:46	2008-07-06 11:35:46
385	207	273	0	2008-07-06 11:36:04	2008-07-06 11:36:04
386	207	274	1	2008-07-06 11:36:04	2008-07-06 11:36:04
387	189	237	0	2008-07-06 11:40:01	2008-07-06 11:40:01
388	189	238	1	2008-07-06 11:40:01	2008-07-06 11:40:01
389	224	283	1	2008-07-06 11:41:53	2008-07-06 11:41:53
390	224	284	0	2008-07-06 11:41:53	2008-07-06 11:41:53
391	225	283	1	2008-07-06 11:41:53	2008-07-06 11:41:53
392	225	284	0	2008-07-06 11:41:53	2008-07-06 11:41:53
393	226	283	1	2008-07-06 11:41:53	2008-07-06 11:41:53
394	226	284	0	2008-07-06 11:41:53	2008-07-06 11:41:53
395	233	289	0	2008-07-06 11:41:55	2008-07-06 11:41:55
396	233	290	1	2008-07-06 11:41:55	2008-07-06 11:41:55
397	234	289	0	2008-07-06 11:41:55	2008-07-06 11:41:55
398	234	290	1	2008-07-06 11:41:55	2008-07-06 11:41:55
399	235	289	0	2008-07-06 11:41:55	2008-07-06 11:41:55
400	235	290	1	2008-07-06 11:41:55	2008-07-06 11:41:55
401	201	243	0	2008-07-06 11:42:50	2008-07-06 11:42:50
402	201	244	1	2008-07-06 11:42:50	2008-07-06 11:42:50
403	188	239	1	2008-07-06 11:43:02	2008-07-06 11:43:02
404	188	240	0	2008-07-06 11:43:02	2008-07-06 11:43:02
407	209	267	0	2008-07-06 11:44:34	2008-07-06 11:44:34
408	209	268	1	2008-07-06 11:44:34	2008-07-06 11:44:34
409	194	253	1	2008-07-06 11:44:37	2008-07-06 11:44:37
410	194	254	0	2008-07-06 11:44:37	2008-07-06 11:44:37
411	195	253	1	2008-07-06 11:44:38	2008-07-06 11:44:38
412	195	254	0	2008-07-06 11:44:38	2008-07-06 11:44:38
413	196	253	1	2008-07-06 11:44:38	2008-07-06 11:44:38
414	196	254	0	2008-07-06 11:44:38	2008-07-06 11:44:38
415	193	235	0	2008-07-06 11:45:34	2008-07-06 11:45:34
416	193	236	1	2008-07-06 11:45:34	2008-07-06 11:45:34
417	199	247	1	2008-07-06 11:46:19	2008-07-06 11:46:19
418	199	248	0	2008-07-06 11:46:19	2008-07-06 11:46:19
419	198	249	0	2008-07-06 11:47:07	2008-07-06 11:47:07
420	198	250	1	2008-07-06 11:47:07	2008-07-06 11:47:07
421	187	233	1	2008-07-06 11:47:34	2008-07-06 11:47:34
422	187	234	0	2008-07-06 11:47:34	2008-07-06 11:47:34
423	204	259	0	2008-07-06 11:50:09	2008-07-06 11:50:09
424	204	260	1	2008-07-06 11:50:09	2008-07-06 11:50:09
425	239	293	1	2008-07-06 11:51:22	2008-07-06 11:51:22
426	239	294	0	2008-07-06 11:51:22	2008-07-06 11:51:22
427	240	293	1	2008-07-06 11:51:22	2008-07-06 11:51:22
428	240	294	0	2008-07-06 11:51:22	2008-07-06 11:51:22
429	241	293	1	2008-07-06 11:51:22	2008-07-06 11:51:22
430	241	294	0	2008-07-06 11:51:22	2008-07-06 11:51:22
431	236	291	1	2008-07-06 11:51:25	2008-07-06 11:51:25
432	236	292	0	2008-07-06 11:51:25	2008-07-06 11:51:25
433	237	291	0	2008-07-06 11:51:25	2008-07-06 11:51:25
434	237	292	1	2008-07-06 11:51:25	2008-07-06 11:51:25
435	238	291	1	2008-07-06 11:51:25	2008-07-06 11:51:25
436	238	292	0	2008-07-06 11:51:25	2008-07-06 11:51:25
437	202	251	1	2008-07-06 11:51:26	2008-07-06 11:51:26
438	202	252	0	2008-07-06 11:51:26	2008-07-06 11:51:26
439	208	279	1	2008-07-06 11:52:48	2008-07-06 11:52:48
440	208	280	0	2008-07-06 11:52:48	2008-07-06 11:52:48
441	211	263	1	2008-07-06 11:53:09	2008-07-06 11:53:09
442	211	264	0	2008-07-06 11:53:09	2008-07-06 11:53:09
443	197	257	0	2008-07-06 11:54:02	2008-07-06 11:54:02
444	197	258	1	2008-07-06 11:54:02	2008-07-06 11:54:02
445	190	241	1	2008-07-06 11:54:07	2008-07-06 11:54:07
446	190	242	0	2008-07-06 11:54:07	2008-07-06 11:54:07
447	191	241	0	2008-07-06 11:54:07	2008-07-06 11:54:07
448	191	242	1	2008-07-06 11:54:07	2008-07-06 11:54:07
449	192	241	1	2008-07-06 11:54:07	2008-07-06 11:54:07
450	192	242	0	2008-07-06 11:54:07	2008-07-06 11:54:07
451	203	245	1	2008-07-06 11:55:33	2008-07-06 11:55:33
452	203	246	0	2008-07-06 11:55:33	2008-07-06 11:55:33
453	205	261	1	2008-07-06 11:56:43	2008-07-06 11:56:43
454	205	262	0	2008-07-06 11:56:43	2008-07-06 11:56:43
455	221	281	1	2008-07-06 11:56:45	2008-07-06 11:56:45
456	221	282	0	2008-07-06 11:56:45	2008-07-06 11:56:45
457	222	281	0	2008-07-06 11:56:45	2008-07-06 11:56:45
458	222	282	1	2008-07-06 11:56:45	2008-07-06 11:56:45
459	223	281	1	2008-07-06 11:56:45	2008-07-06 11:56:45
460	223	282	0	2008-07-06 11:56:45	2008-07-06 11:56:45
461	230	287	0	2008-07-06 11:57:09	2008-07-06 11:57:09
462	230	288	1	2008-07-06 11:57:09	2008-07-06 11:57:09
463	231	287	0	2008-07-06 11:57:09	2008-07-06 11:57:09
464	231	288	1	2008-07-06 11:57:09	2008-07-06 11:57:09
465	232	287	0	2008-07-06 11:57:09	2008-07-06 11:57:09
466	232	288	1	2008-07-06 11:57:09	2008-07-06 11:57:09
467	206	265	0	2008-07-06 11:58:22	2008-07-06 11:58:22
468	206	266	1	2008-07-06 11:58:22	2008-07-06 11:58:22
469	186	231	1	2008-07-06 11:58:39	2008-07-06 11:58:39
470	186	232	0	2008-07-06 11:58:39	2008-07-06 11:58:39
471	210	277	1	2008-07-06 11:58:52	2008-07-06 11:58:52
472	210	278	0	2008-07-06 11:58:52	2008-07-06 11:58:52
473	183	225	0	2008-07-06 12:00:03	2008-07-06 12:00:03
474	183	226	1	2008-07-06 12:00:03	2008-07-06 12:00:03
475	185	229	0	2008-07-06 12:00:38	2008-07-06 12:00:38
476	185	230	1	2008-07-06 12:00:38	2008-07-06 12:00:38
477	184	227	1	2008-07-06 12:01:27	2008-07-06 12:01:27
478	184	228	0	2008-07-06 12:01:27	2008-07-06 12:01:27
479	227	285	0	2008-07-06 12:01:37	2008-07-06 12:01:37
480	227	286	1	2008-07-06 12:01:37	2008-07-06 12:01:37
481	228	285	0	2008-07-06 12:01:37	2008-07-06 12:01:37
482	228	286	1	2008-07-06 12:01:37	2008-07-06 12:01:37
483	229	285	0	2008-07-06 12:01:37	2008-07-06 12:01:37
484	229	286	1	2008-07-06 12:01:37	2008-07-06 12:01:37
485	182	223	0	2008-07-06 12:03:56	2008-07-06 12:03:56
486	182	224	1	2008-07-06 12:03:56	2008-07-06 12:03:56
487	218	271	1	2008-07-06 12:04:19	2008-07-06 12:04:19
488	218	272	0	2008-07-06 12:04:19	2008-07-06 12:04:19
489	219	271	0	2008-07-06 12:04:19	2008-07-06 12:04:19
490	219	272	1	2008-07-06 12:04:19	2008-07-06 12:04:19
491	220	271	1	2008-07-06 12:04:19	2008-07-06 12:04:19
492	220	272	0	2008-07-06 12:04:19	2008-07-06 12:04:19
493	212	275	0	2008-07-06 12:04:51	2008-07-06 12:04:51
494	212	276	1	2008-07-06 12:04:51	2008-07-06 12:04:51
495	213	275	1	2008-07-06 12:04:51	2008-07-06 12:04:51
496	213	276	0	2008-07-06 12:04:51	2008-07-06 12:04:51
497	214	275	1	2008-07-06 12:04:51	2008-07-06 12:04:51
498	214	276	0	2008-07-06 12:04:51	2008-07-06 12:04:51
499	242	295	1	2008-07-06 12:08:38	2008-07-06 12:08:38
500	242	296	0	2008-07-06 12:08:38	2008-07-06 12:08:38
501	243	295	1	2008-07-06 12:08:38	2008-07-06 12:08:38
502	243	296	0	2008-07-06 12:08:38	2008-07-06 12:08:38
503	244	295	1	2008-07-06 12:08:38	2008-07-06 12:08:38
504	244	296	0	2008-07-06 12:08:38	2008-07-06 12:08:38
505	215	269	1	2008-07-06 12:08:46	2008-07-06 12:08:46
506	215	270	0	2008-07-06 12:08:46	2008-07-06 12:08:46
507	216	269	1	2008-07-06 12:08:46	2008-07-06 12:08:46
508	216	270	0	2008-07-06 12:08:46	2008-07-06 12:08:46
509	217	269	1	2008-07-06 12:08:46	2008-07-06 12:08:46
510	217	270	0	2008-07-06 12:08:46	2008-07-06 12:08:46
515	255	311	1	2008-07-06 15:44:19	2008-07-06 15:44:19
516	255	312	0	2008-07-06 15:44:19	2008-07-06 15:44:19
517	250	303	0	2008-07-06 15:48:33	2008-07-06 15:48:33
518	250	304	1	2008-07-06 15:48:33	2008-07-06 15:48:33
519	252	305	0	2008-07-06 15:49:44	2008-07-06 15:49:44
520	252	306	1	2008-07-06 15:49:44	2008-07-06 15:49:44
521	245	297	0	2008-07-06 15:50:55	2008-07-06 15:50:55
522	245	298	1	2008-07-06 15:50:55	2008-07-06 15:50:55
523	437	297	0	2008-07-06 15:50:55	2008-07-06 15:50:55
524	437	298	1	2008-07-06 15:50:55	2008-07-06 15:50:55
525	438	297	0	2008-07-06 15:50:55	2008-07-06 15:50:55
526	438	298	1	2008-07-06 15:50:55	2008-07-06 15:50:55
527	277	349	0	2008-07-06 15:51:12	2008-07-06 15:51:12
528	277	350	1	2008-07-06 15:51:12	2008-07-06 15:51:12
529	276	347	0	2008-07-06 15:52:42	2008-07-06 15:52:42
530	276	348	1	2008-07-06 15:52:42	2008-07-06 15:52:42
531	269	341	1	2008-07-06 15:53:16	2008-07-06 15:53:16
532	269	342	0	2008-07-06 15:53:16	2008-07-06 15:53:16
533	270	341	1	2008-07-06 15:53:16	2008-07-06 15:53:16
534	270	342	0	2008-07-06 15:53:16	2008-07-06 15:53:16
535	271	341	1	2008-07-06 15:53:16	2008-07-06 15:53:16
536	271	342	0	2008-07-06 15:53:16	2008-07-06 15:53:16
537	256	319	1	2008-07-06 15:53:46	2008-07-06 15:53:46
538	256	320	0	2008-07-06 15:53:46	2008-07-06 15:53:46
539	275	345	1	2008-07-06 15:54:53	2008-07-06 15:54:53
540	275	346	0	2008-07-06 15:54:53	2008-07-06 15:54:53
541	299	365	0	2008-07-06 15:56:53	2008-07-06 15:56:53
542	299	366	1	2008-07-06 15:56:53	2008-07-06 15:56:53
543	300	365	0	2008-07-06 15:56:53	2008-07-06 15:56:53
544	300	366	1	2008-07-06 15:56:53	2008-07-06 15:56:53
545	301	365	0	2008-07-06 15:56:53	2008-07-06 15:56:53
546	301	366	1	2008-07-06 15:56:53	2008-07-06 15:56:53
547	257	321	1	2008-07-06 15:59:14	2008-07-06 15:59:14
548	257	322	0	2008-07-06 15:59:14	2008-07-06 15:59:14
549	265	335	1	2008-07-06 15:59:37	2008-07-06 15:59:37
550	265	336	0	2008-07-06 15:59:37	2008-07-06 15:59:37
551	248	315	1	2008-07-06 16:01:49	2008-07-06 16:01:49
552	248	316	0	2008-07-06 16:01:49	2008-07-06 16:01:49
553	263	333	0	2008-07-06 16:02:50	2008-07-06 16:02:50
554	263	334	1	2008-07-06 16:02:50	2008-07-06 16:02:50
555	296	363	1	2008-07-06 16:03:40	2008-07-06 16:03:40
556	296	364	0	2008-07-06 16:03:40	2008-07-06 16:03:40
557	297	363	1	2008-07-06 16:03:40	2008-07-06 16:03:40
558	297	364	0	2008-07-06 16:03:40	2008-07-06 16:03:40
559	298	363	1	2008-07-06 16:03:40	2008-07-06 16:03:40
560	298	364	0	2008-07-06 16:03:40	2008-07-06 16:03:40
561	292	357	1	2008-07-06 16:05:20	2008-07-06 16:05:20
562	292	358	0	2008-07-06 16:05:20	2008-07-06 16:05:20
563	291	357	1	2008-07-06 16:05:20	2008-07-06 16:05:20
564	291	358	0	2008-07-06 16:05:20	2008-07-06 16:05:20
565	290	357	1	2008-07-06 16:05:20	2008-07-06 16:05:20
566	290	358	0	2008-07-06 16:05:20	2008-07-06 16:05:20
567	258	325	0	2008-07-06 16:06:03	2008-07-06 16:06:03
568	258	326	1	2008-07-06 16:06:03	2008-07-06 16:06:03
569	251	317	0	2008-07-06 16:06:46	2008-07-06 16:06:46
570	251	318	1	2008-07-06 16:06:46	2008-07-06 16:06:46
571	266	337	0	2008-07-06 16:07:09	2008-07-06 16:07:09
572	266	338	1	2008-07-06 16:07:09	2008-07-06 16:07:09
573	268	337	1	2008-07-06 16:07:09	2008-07-06 16:07:09
574	268	338	0	2008-07-06 16:07:09	2008-07-06 16:07:09
575	267	337	1	2008-07-06 16:07:09	2008-07-06 16:07:09
576	267	338	0	2008-07-06 16:07:09	2008-07-06 16:07:09
577	264	339	0	2008-07-06 16:07:46	2008-07-06 16:07:46
578	264	340	1	2008-07-06 16:07:46	2008-07-06 16:07:46
579	253	307	1	2008-07-06 16:11:02	2008-07-06 16:11:02
580	253	308	0	2008-07-06 16:11:02	2008-07-06 16:11:02
581	302	367	0	2008-07-06 16:11:14	2008-07-06 16:11:14
582	302	368	1	2008-07-06 16:11:14	2008-07-06 16:11:14
583	303	367	0	2008-07-06 16:11:14	2008-07-06 16:11:14
584	303	368	1	2008-07-06 16:11:14	2008-07-06 16:11:14
585	304	367	0	2008-07-06 16:11:14	2008-07-06 16:11:14
586	304	368	1	2008-07-06 16:11:14	2008-07-06 16:11:14
587	305	369	0	2008-07-06 16:11:28	2008-07-06 16:11:28
588	305	370	1	2008-07-06 16:11:28	2008-07-06 16:11:28
589	306	369	1	2008-07-06 16:11:28	2008-07-06 16:11:28
590	306	370	0	2008-07-06 16:11:28	2008-07-06 16:11:28
591	307	369	0	2008-07-06 16:11:28	2008-07-06 16:11:28
592	307	370	1	2008-07-06 16:11:28	2008-07-06 16:11:28
593	249	309	1	2008-07-06 16:13:19	2008-07-06 16:13:19
594	249	310	0	2008-07-06 16:13:19	2008-07-06 16:13:19
595	259	327	1	2008-07-06 16:13:26	2008-07-06 16:13:26
596	259	328	0	2008-07-06 16:13:26	2008-07-06 16:13:26
597	246	299	1	2008-07-06 16:13:37	2008-07-06 16:13:37
598	246	300	0	2008-07-06 16:13:37	2008-07-06 16:13:37
599	247	301	1	2008-07-06 16:15:29	2008-07-06 16:15:29
600	247	302	0	2008-07-06 16:15:29	2008-07-06 16:15:29
601	254	313	0	2008-07-06 16:19:03	2008-07-06 16:19:03
602	254	314	1	2008-07-06 16:19:03	2008-07-06 16:19:03
603	287	359	1	2008-07-06 16:20:21	2008-07-06 16:20:21
604	287	360	0	2008-07-06 16:20:21	2008-07-06 16:20:21
605	288	359	1	2008-07-06 16:20:21	2008-07-06 16:20:21
606	288	360	0	2008-07-06 16:20:21	2008-07-06 16:20:21
607	289	359	0	2008-07-06 16:20:21	2008-07-06 16:20:21
608	289	360	1	2008-07-06 16:20:21	2008-07-06 16:20:21
609	261	329	1	2008-07-06 16:20:28	2008-07-06 16:20:28
610	261	330	0	2008-07-06 16:20:28	2008-07-06 16:20:28
611	278	361	1	2008-07-06 16:20:46	2008-07-06 16:20:46
612	278	362	0	2008-07-06 16:20:46	2008-07-06 16:20:46
613	279	361	1	2008-07-06 16:20:46	2008-07-06 16:20:46
614	279	362	0	2008-07-06 16:20:46	2008-07-06 16:20:46
615	280	361	1	2008-07-06 16:20:46	2008-07-06 16:20:46
616	280	362	0	2008-07-06 16:20:46	2008-07-06 16:20:46
617	260	323	0	2008-07-06 16:23:32	2008-07-06 16:23:32
618	260	324	1	2008-07-06 16:23:32	2008-07-06 16:23:32
619	293	351	1	2008-07-06 16:25:03	2008-07-06 16:25:03
620	293	352	0	2008-07-06 16:25:03	2008-07-06 16:25:03
621	294	351	1	2008-07-06 16:25:03	2008-07-06 16:25:03
622	294	352	0	2008-07-06 16:25:03	2008-07-06 16:25:03
623	295	351	1	2008-07-06 16:25:03	2008-07-06 16:25:03
624	295	352	0	2008-07-06 16:25:03	2008-07-06 16:25:03
625	272	343	0	2008-07-06 16:25:25	2008-07-06 16:25:25
626	272	344	1	2008-07-06 16:25:25	2008-07-06 16:25:25
627	273	343	1	2008-07-06 16:25:25	2008-07-06 16:25:25
628	273	344	0	2008-07-06 16:25:25	2008-07-06 16:25:25
629	274	343	0	2008-07-06 16:25:25	2008-07-06 16:25:25
630	274	344	1	2008-07-06 16:25:25	2008-07-06 16:25:25
631	282	353	0	2008-07-06 16:51:04	2008-07-06 16:51:04
632	282	354	1	2008-07-06 16:51:04	2008-07-06 16:51:04
633	283	353	0	2008-07-06 16:51:04	2008-07-06 16:51:04
634	283	354	1	2008-07-06 16:51:04	2008-07-06 16:51:04
635	281	353	0	2008-07-06 16:51:04	2008-07-06 16:51:04
636	281	354	1	2008-07-06 16:51:04	2008-07-06 16:51:04
637	284	355	1	2008-07-06 16:51:45	2008-07-06 16:51:45
638	284	356	0	2008-07-06 16:51:46	2008-07-06 16:51:46
639	285	355	0	2008-07-06 16:51:46	2008-07-06 16:51:46
640	285	356	1	2008-07-06 16:51:46	2008-07-06 16:51:46
641	286	355	1	2008-07-06 16:51:46	2008-07-06 16:51:46
642	286	356	0	2008-07-06 16:51:46	2008-07-06 16:51:46
643	262	331	1	2008-07-06 16:53:33	2008-07-06 16:53:33
644	262	332	0	2008-07-06 16:53:33	2008-07-06 16:53:33
647	318	406	0	2008-07-07 11:36:27	2008-07-07 11:36:27
648	318	407	1	2008-07-07 11:36:27	2008-07-07 11:36:27
649	334	421	0	2008-07-07 11:36:40	2008-07-07 11:36:40
650	334	420	1	2008-07-07 11:36:40	2008-07-07 11:36:40
651	311	396	1	2008-07-07 11:37:11	2008-07-07 11:37:11
652	311	397	0	2008-07-07 11:37:11	2008-07-07 11:37:11
653	346	446	1	2008-07-07 11:37:33	2008-07-07 11:37:33
654	346	447	0	2008-07-07 11:37:33	2008-07-07 11:37:33
655	316	402	0	2008-07-07 11:37:47	2008-07-07 11:37:47
656	316	403	1	2008-07-07 11:37:47	2008-07-07 11:37:47
657	335	428	0	2008-07-07 11:38:33	2008-07-07 11:38:33
658	335	429	1	2008-07-07 11:38:33	2008-07-07 11:38:33
659	336	430	0	2008-07-07 11:38:35	2008-07-07 11:38:35
660	336	431	1	2008-07-07 11:38:35	2008-07-07 11:38:35
661	337	430	0	2008-07-07 11:38:35	2008-07-07 11:38:35
662	337	431	1	2008-07-07 11:38:35	2008-07-07 11:38:35
663	338	430	0	2008-07-07 11:38:35	2008-07-07 11:38:35
664	338	431	1	2008-07-07 11:38:35	2008-07-07 11:38:35
665	315	400	0	2008-07-07 11:38:43	2008-07-07 11:38:43
666	315	401	1	2008-07-07 11:38:43	2008-07-07 11:38:43
667	339	436	1	2008-07-07 11:39:03	2008-07-07 11:39:03
668	339	437	0	2008-07-07 11:39:03	2008-07-07 11:39:03
669	320	410	0	2008-07-07 11:39:34	2008-07-07 11:39:34
670	320	411	1	2008-07-07 11:39:34	2008-07-07 11:39:34
671	321	412	1	2008-07-07 11:39:50	2008-07-07 11:39:50
672	321	413	0	2008-07-07 11:39:50	2008-07-07 11:39:50
673	348	450	0	2008-07-07 11:40:20	2008-07-07 11:40:20
674	348	451	1	2008-07-07 11:40:20	2008-07-07 11:40:20
675	342	432	0	2008-07-07 11:40:25	2008-07-07 11:40:25
676	342	433	1	2008-07-07 11:40:25	2008-07-07 11:40:25
677	340	438	0	2008-07-07 11:41:20	2008-07-07 11:41:20
678	340	439	1	2008-07-07 11:41:20	2008-07-07 11:41:20
679	341	440	1	2008-07-07 11:41:27	2008-07-07 11:41:27
680	341	441	0	2008-07-07 11:41:27	2008-07-07 11:41:27
681	347	448	1	2008-07-07 11:41:55	2008-07-07 11:41:55
682	347	449	0	2008-07-07 11:41:55	2008-07-07 11:41:55
683	439	448	0	2008-07-07 11:41:55	2008-07-07 11:41:55
684	439	449	1	2008-07-07 11:41:56	2008-07-07 11:41:56
685	440	448	1	2008-07-07 11:41:56	2008-07-07 11:41:56
686	440	449	0	2008-07-07 11:41:56	2008-07-07 11:41:56
687	329	418	1	2008-07-07 11:42:11	2008-07-07 11:42:11
688	329	419	0	2008-07-07 11:42:11	2008-07-07 11:42:11
689	317	405	0	2008-07-07 11:42:23	2008-07-07 11:42:23
690	317	404	1	2008-07-07 11:42:23	2008-07-07 11:42:23
691	322	415	1	2008-07-07 11:43:28	2008-07-07 11:43:28
692	322	414	0	2008-07-07 11:43:28	2008-07-07 11:43:28
693	319	408	1	2008-07-07 11:43:30	2008-07-07 11:43:30
694	319	409	0	2008-07-07 11:43:30	2008-07-07 11:43:30
695	344	442	0	2008-07-07 11:44:22	2008-07-07 11:44:22
696	344	443	1	2008-07-07 11:44:22	2008-07-07 11:44:22
697	343	434	0	2008-07-07 11:44:42	2008-07-07 11:44:42
698	343	435	1	2008-07-07 11:44:42	2008-07-07 11:44:42
699	349	452	0	2008-07-07 11:44:57	2008-07-07 11:44:57
700	349	453	1	2008-07-07 11:44:57	2008-07-07 11:44:57
701	350	452	0	2008-07-07 11:44:57	2008-07-07 11:44:57
702	350	453	1	2008-07-07 11:44:57	2008-07-07 11:44:57
703	351	452	0	2008-07-07 11:44:57	2008-07-07 11:44:57
704	351	453	1	2008-07-07 11:44:57	2008-07-07 11:44:57
705	330	424	1	2008-07-07 11:45:30	2008-07-07 11:45:30
706	330	425	0	2008-07-07 11:45:30	2008-07-07 11:45:30
707	331	424	1	2008-07-07 11:45:30	2008-07-07 11:45:30
708	331	425	0	2008-07-07 11:45:30	2008-07-07 11:45:30
709	332	424	1	2008-07-07 11:45:30	2008-07-07 11:45:30
710	332	425	0	2008-07-07 11:45:30	2008-07-07 11:45:30
711	345	444	1	2008-07-07 11:45:45	2008-07-07 11:45:45
712	345	445	0	2008-07-07 11:45:45	2008-07-07 11:45:45
713	323	417	1	2008-07-07 11:46:55	2008-07-07 11:46:55
714	323	416	0	2008-07-07 11:46:55	2008-07-07 11:46:55
715	324	417	1	2008-07-07 11:46:55	2008-07-07 11:46:55
716	324	416	0	2008-07-07 11:46:55	2008-07-07 11:46:55
717	325	417	1	2008-07-07 11:46:55	2008-07-07 11:46:55
718	325	416	0	2008-07-07 11:46:55	2008-07-07 11:46:55
719	333	427	1	2008-07-07 11:47:07	2008-07-07 11:47:07
720	333	426	0	2008-07-07 11:47:07	2008-07-07 11:47:07
721	356	456	0	2008-07-07 11:47:36	2008-07-07 11:47:36
722	356	457	1	2008-07-07 11:47:36	2008-07-07 11:47:36
723	357	456	0	2008-07-07 11:47:36	2008-07-07 11:47:36
724	357	457	1	2008-07-07 11:47:36	2008-07-07 11:47:36
725	355	456	0	2008-07-07 11:47:36	2008-07-07 11:47:36
726	355	457	1	2008-07-07 11:47:36	2008-07-07 11:47:36
727	361	460	0	2008-07-07 11:49:32	2008-07-07 11:49:32
728	361	461	1	2008-07-07 11:49:32	2008-07-07 11:49:32
729	362	460	1	2008-07-07 11:49:32	2008-07-07 11:49:32
730	362	461	0	2008-07-07 11:49:32	2008-07-07 11:49:32
731	363	460	0	2008-07-07 11:49:32	2008-07-07 11:49:32
732	363	461	1	2008-07-07 11:49:32	2008-07-07 11:49:32
733	312	398	0	2008-07-07 11:49:43	2008-07-07 11:49:43
734	312	399	1	2008-07-07 11:49:43	2008-07-07 11:49:43
735	313	398	1	2008-07-07 11:49:43	2008-07-07 11:49:43
736	313	399	0	2008-07-07 11:49:43	2008-07-07 11:49:43
737	314	398	0	2008-07-07 11:49:43	2008-07-07 11:49:43
738	314	399	1	2008-07-07 11:49:43	2008-07-07 11:49:43
739	364	463	1	2008-07-07 11:49:52	2008-07-07 11:49:52
740	364	462	0	2008-07-07 11:49:52	2008-07-07 11:49:52
741	365	463	0	2008-07-07 11:49:52	2008-07-07 11:49:52
742	365	462	1	2008-07-07 11:49:52	2008-07-07 11:49:52
743	366	463	0	2008-07-07 11:49:52	2008-07-07 11:49:52
744	366	462	1	2008-07-07 11:49:52	2008-07-07 11:49:52
745	353	454	1	2008-07-07 11:50:46	2008-07-07 11:50:46
746	353	455	0	2008-07-07 11:50:46	2008-07-07 11:50:46
747	354	454	0	2008-07-07 11:50:46	2008-07-07 11:50:46
748	354	455	1	2008-07-07 11:50:46	2008-07-07 11:50:46
749	352	454	0	2008-07-07 11:50:46	2008-07-07 11:50:46
750	352	455	1	2008-07-07 11:50:46	2008-07-07 11:50:46
751	370	466	1	2008-07-07 11:51:47	2008-07-07 11:51:47
752	370	467	0	2008-07-07 11:51:47	2008-07-07 11:51:47
753	371	466	1	2008-07-07 11:51:47	2008-07-07 11:51:47
754	371	467	0	2008-07-07 11:51:47	2008-07-07 11:51:47
755	372	466	1	2008-07-07 11:51:47	2008-07-07 11:51:47
756	372	467	0	2008-07-07 11:51:47	2008-07-07 11:51:47
757	373	468	1	2008-07-07 11:52:04	2008-07-07 11:52:04
758	373	469	0	2008-07-07 11:52:04	2008-07-07 11:52:04
759	374	468	1	2008-07-07 11:52:04	2008-07-07 11:52:04
760	374	469	0	2008-07-07 11:52:04	2008-07-07 11:52:04
761	375	468	1	2008-07-07 11:52:04	2008-07-07 11:52:04
762	375	469	0	2008-07-07 11:52:04	2008-07-07 11:52:04
763	367	464	0	2008-07-07 11:53:15	2008-07-07 11:53:15
764	367	465	1	2008-07-07 11:53:15	2008-07-07 11:53:15
765	368	464	0	2008-07-07 11:53:15	2008-07-07 11:53:15
766	368	465	1	2008-07-07 11:53:15	2008-07-07 11:53:15
767	369	464	0	2008-07-07 11:53:15	2008-07-07 11:53:15
768	369	465	1	2008-07-07 11:53:15	2008-07-07 11:53:15
769	326	423	1	2008-07-07 11:53:39	2008-07-07 11:53:39
770	326	422	0	2008-07-07 11:53:39	2008-07-07 11:53:39
771	327	423	1	2008-07-07 11:53:39	2008-07-07 11:53:39
772	327	422	0	2008-07-07 11:53:39	2008-07-07 11:53:39
773	328	423	1	2008-07-07 11:53:39	2008-07-07 11:53:39
774	328	422	0	2008-07-07 11:53:39	2008-07-07 11:53:39
784	358	458	0	2008-07-07 11:57:28	2008-07-07 11:57:28
785	358	459	1	2008-07-07 11:57:28	2008-07-07 11:57:28
786	359	458	0	2008-07-07 11:57:28	2008-07-07 11:57:28
787	359	459	1	2008-07-07 11:57:28	2008-07-07 11:57:28
788	360	458	0	2008-07-07 11:57:28	2008-07-07 11:57:28
789	360	459	1	2008-07-07 11:57:28	2008-07-07 11:57:28
790	507	567	0	2008-07-07 14:54:08	2008-07-07 14:54:08
791	507	568	1	2008-07-07 14:54:08	2008-07-07 14:54:08
792	452	515	1	2008-07-07 14:54:59	2008-07-07 14:54:59
793	452	516	0	2008-07-07 14:54:59	2008-07-07 14:54:59
794	449	519	1	2008-07-07 14:55:50	2008-07-07 14:55:50
795	449	520	0	2008-07-07 14:55:50	2008-07-07 14:55:50
796	506	565	1	2008-07-07 14:57:44	2008-07-07 14:57:44
797	506	566	0	2008-07-07 14:57:44	2008-07-07 14:57:44
798	446	511	0	2008-07-07 14:58:40	2008-07-07 14:58:40
799	446	512	1	2008-07-07 14:58:40	2008-07-07 14:58:40
800	450	517	0	2008-07-07 14:59:51	2008-07-07 14:59:51
801	450	518	1	2008-07-07 14:59:51	2008-07-07 14:59:51
802	460	521	0	2008-07-07 15:00:18	2008-07-07 15:00:18
803	460	522	1	2008-07-07 15:00:18	2008-07-07 15:00:18
804	504	561	1	2008-07-07 15:00:45	2008-07-07 15:00:45
805	504	562	0	2008-07-07 15:00:45	2008-07-07 15:00:45
806	503	559	1	2008-07-07 15:01:14	2008-07-07 15:01:14
807	503	560	0	2008-07-07 15:01:14	2008-07-07 15:01:14
808	443	499	1	2008-07-07 15:01:38	2008-07-07 15:01:38
809	443	500	0	2008-07-07 15:01:38	2008-07-07 15:01:38
810	456	523	1	2008-07-07 15:02:10	2008-07-07 15:02:10
811	456	524	0	2008-07-07 15:02:10	2008-07-07 15:02:10
812	451	513	1	2008-07-07 15:02:56	2008-07-07 15:02:56
813	451	514	0	2008-07-07 15:02:56	2008-07-07 15:02:56
814	441	501	1	2008-07-07 15:03:04	2008-07-07 15:03:04
815	441	502	0	2008-07-07 15:03:04	2008-07-07 15:03:04
816	445	503	1	2008-07-07 15:03:48	2008-07-07 15:03:48
817	445	504	0	2008-07-07 15:03:48	2008-07-07 15:03:48
818	457	529	1	2008-07-07 15:05:07	2008-07-07 15:05:07
819	457	530	0	2008-07-07 15:05:07	2008-07-07 15:05:07
820	459	531	1	2008-07-07 15:05:51	2008-07-07 15:05:51
821	459	532	0	2008-07-07 15:05:51	2008-07-07 15:05:51
822	479	543	0	2008-07-07 15:10:44	2008-07-07 15:10:44
823	479	544	1	2008-07-07 15:10:44	2008-07-07 15:10:44
824	480	543	0	2008-07-07 15:10:44	2008-07-07 15:10:44
825	480	544	1	2008-07-07 15:10:44	2008-07-07 15:10:44
826	481	543	0	2008-07-07 15:10:45	2008-07-07 15:10:45
827	481	544	1	2008-07-07 15:10:45	2008-07-07 15:10:45
828	458	533	1	2008-07-07 15:11:19	2008-07-07 15:11:19
829	458	534	0	2008-07-07 15:11:19	2008-07-07 15:11:19
830	485	547	0	2008-07-07 15:12:24	2008-07-07 15:12:24
831	485	548	1	2008-07-07 15:12:25	2008-07-07 15:12:25
832	486	547	0	2008-07-07 15:12:25	2008-07-07 15:12:25
833	486	548	1	2008-07-07 15:12:25	2008-07-07 15:12:25
834	487	547	1	2008-07-07 15:12:25	2008-07-07 15:12:25
835	487	548	0	2008-07-07 15:12:25	2008-07-07 15:12:25
836	488	549	1	2008-07-07 15:14:19	2008-07-07 15:14:19
837	488	550	0	2008-07-07 15:14:19	2008-07-07 15:14:19
838	489	549	1	2008-07-07 15:14:19	2008-07-07 15:14:19
839	489	550	0	2008-07-07 15:14:19	2008-07-07 15:14:19
840	490	549	1	2008-07-07 15:14:19	2008-07-07 15:14:19
841	490	550	0	2008-07-07 15:14:19	2008-07-07 15:14:19
842	447	509	1	2008-07-07 15:14:37	2008-07-07 15:14:37
843	447	510	0	2008-07-07 15:14:37	2008-07-07 15:14:37
844	467	535	1	2008-07-07 15:14:39	2008-07-07 15:14:39
845	467	536	0	2008-07-07 15:14:39	2008-07-07 15:14:39
846	468	535	1	2008-07-07 15:14:39	2008-07-07 15:14:39
847	468	536	0	2008-07-07 15:14:39	2008-07-07 15:14:39
848	469	535	1	2008-07-07 15:14:39	2008-07-07 15:14:39
849	469	536	0	2008-07-07 15:14:39	2008-07-07 15:14:39
850	448	507	1	2008-07-07 15:15:55	2008-07-07 15:15:55
851	448	508	0	2008-07-07 15:15:55	2008-07-07 15:15:55
852	494	553	0	2008-07-07 15:16:14	2008-07-07 15:16:14
853	494	554	1	2008-07-07 15:16:14	2008-07-07 15:16:14
854	495	553	0	2008-07-07 15:16:14	2008-07-07 15:16:14
855	495	554	1	2008-07-07 15:16:14	2008-07-07 15:16:14
856	496	553	0	2008-07-07 15:16:14	2008-07-07 15:16:14
857	496	554	1	2008-07-07 15:16:14	2008-07-07 15:16:14
858	442	497	1	2008-07-07 15:17:11	2008-07-07 15:17:11
859	442	498	0	2008-07-07 15:17:11	2008-07-07 15:17:11
860	444	505	1	2008-07-07 15:17:14	2008-07-07 15:17:14
861	444	506	0	2008-07-07 15:17:14	2008-07-07 15:17:14
862	500	555	1	2008-07-07 15:18:21	2008-07-07 15:18:21
863	500	556	0	2008-07-07 15:18:21	2008-07-07 15:18:21
864	501	555	1	2008-07-07 15:18:21	2008-07-07 15:18:21
865	501	556	0	2008-07-07 15:18:21	2008-07-07 15:18:21
866	502	555	1	2008-07-07 15:18:21	2008-07-07 15:18:21
867	502	556	0	2008-07-07 15:18:21	2008-07-07 15:18:21
868	470	537	0	2008-07-07 15:19:22	2008-07-07 15:19:22
869	470	538	1	2008-07-07 15:19:22	2008-07-07 15:19:22
870	471	537	1	2008-07-07 15:19:22	2008-07-07 15:19:22
871	471	538	0	2008-07-07 15:19:22	2008-07-07 15:19:22
872	472	537	0	2008-07-07 15:19:22	2008-07-07 15:19:22
873	472	538	1	2008-07-07 15:19:22	2008-07-07 15:19:22
874	482	545	1	2008-07-07 15:20:28	2008-07-07 15:20:28
875	482	546	0	2008-07-07 15:20:28	2008-07-07 15:20:28
876	483	545	0	2008-07-07 15:20:28	2008-07-07 15:20:28
877	483	546	1	2008-07-07 15:20:28	2008-07-07 15:20:28
878	484	545	0	2008-07-07 15:20:28	2008-07-07 15:20:28
879	484	546	1	2008-07-07 15:20:28	2008-07-07 15:20:28
880	492	551	0	2008-07-07 15:24:51	2008-07-07 15:24:51
881	492	552	1	2008-07-07 15:24:51	2008-07-07 15:24:51
882	493	551	0	2008-07-07 15:24:51	2008-07-07 15:24:51
883	493	552	1	2008-07-07 15:24:51	2008-07-07 15:24:51
884	491	551	0	2008-07-07 15:24:51	2008-07-07 15:24:51
885	491	552	1	2008-07-07 15:24:51	2008-07-07 15:24:51
886	505	563	0	2008-07-07 15:25:13	2008-07-07 15:25:13
887	505	564	1	2008-07-07 15:25:13	2008-07-07 15:25:13
888	473	539	1	2008-07-07 15:31:14	2008-07-07 15:31:14
889	473	540	0	2008-07-07 15:31:14	2008-07-07 15:31:14
890	474	539	1	2008-07-07 15:31:14	2008-07-07 15:31:14
891	474	540	0	2008-07-07 15:31:14	2008-07-07 15:31:14
892	475	539	1	2008-07-07 15:31:14	2008-07-07 15:31:14
893	475	540	0	2008-07-07 15:31:14	2008-07-07 15:31:14
894	461	527	1	2008-07-07 15:33:25	2008-07-07 15:33:25
895	461	528	0	2008-07-07 15:33:25	2008-07-07 15:33:25
896	462	527	1	2008-07-07 15:33:25	2008-07-07 15:33:25
897	462	528	0	2008-07-07 15:33:25	2008-07-07 15:33:25
898	463	527	1	2008-07-07 15:33:25	2008-07-07 15:33:25
899	463	528	0	2008-07-07 15:33:25	2008-07-07 15:33:25
900	498	557	0	2008-07-07 15:33:54	2008-07-07 15:33:54
901	498	558	1	2008-07-07 15:33:54	2008-07-07 15:33:54
902	499	557	0	2008-07-07 15:33:54	2008-07-07 15:33:54
903	499	558	1	2008-07-07 15:33:54	2008-07-07 15:33:54
904	497	557	0	2008-07-07 15:33:54	2008-07-07 15:33:54
905	497	558	1	2008-07-07 15:33:54	2008-07-07 15:33:54
906	464	525	0	2008-07-07 15:35:39	2008-07-07 15:35:39
907	464	526	1	2008-07-07 15:35:39	2008-07-07 15:35:39
908	465	525	1	2008-07-07 15:35:39	2008-07-07 15:35:39
909	465	526	0	2008-07-07 15:35:39	2008-07-07 15:35:39
910	466	525	1	2008-07-07 15:35:39	2008-07-07 15:35:39
911	466	526	0	2008-07-07 15:35:39	2008-07-07 15:35:39
912	476	541	0	2008-07-07 15:36:15	2008-07-07 15:36:15
913	476	542	1	2008-07-07 15:36:15	2008-07-07 15:36:15
914	477	541	0	2008-07-07 15:36:15	2008-07-07 15:36:15
915	477	542	1	2008-07-07 15:36:15	2008-07-07 15:36:15
916	478	541	0	2008-07-07 15:36:15	2008-07-07 15:36:15
917	478	542	1	2008-07-07 15:36:15	2008-07-07 15:36:15
918	453	495	0	2008-07-07 15:36:39	2008-07-07 15:36:39
919	453	496	1	2008-07-07 15:36:39	2008-07-07 15:36:39
920	454	495	1	2008-07-07 15:36:39	2008-07-07 15:36:39
921	454	496	0	2008-07-07 15:36:39	2008-07-07 15:36:39
922	455	495	0	2008-07-07 15:36:39	2008-07-07 15:36:39
923	455	496	1	2008-07-07 15:36:39	2008-07-07 15:36:39
924	509	577	1	2008-07-07 18:25:12	2008-07-07 18:25:12
925	509	578	0	2008-07-07 18:25:12	2008-07-07 18:25:12
926	508	573	0	2008-07-07 18:26:12	2008-07-07 18:26:12
927	508	574	1	2008-07-07 18:26:12	2008-07-07 18:26:12
928	513	585	1	2008-07-07 18:27:40	2008-07-07 18:27:40
929	513	586	0	2008-07-07 18:27:40	2008-07-07 18:27:40
930	571	639	0	2008-07-07 18:28:50	2008-07-07 18:28:50
931	571	640	1	2008-07-07 18:28:50	2008-07-07 18:28:50
932	572	641	0	2008-07-07 18:29:17	2008-07-07 18:29:17
933	572	642	1	2008-07-07 18:29:17	2008-07-07 18:29:17
934	561	613	1	2008-07-07 18:30:17	2008-07-07 18:30:17
935	561	614	0	2008-07-07 18:30:17	2008-07-07 18:30:17
936	551	611	1	2008-07-07 18:32:31	2008-07-07 18:32:31
937	551	612	0	2008-07-07 18:32:31	2008-07-07 18:32:31
938	552	611	1	2008-07-07 18:32:31	2008-07-07 18:32:31
939	552	612	0	2008-07-07 18:32:31	2008-07-07 18:32:31
940	553	611	1	2008-07-07 18:32:31	2008-07-07 18:32:31
941	553	612	0	2008-07-07 18:32:31	2008-07-07 18:32:31
942	512	581	1	2008-07-07 18:32:37	2008-07-07 18:32:37
943	512	582	0	2008-07-07 18:32:37	2008-07-07 18:32:37
944	515	595	0	2008-07-07 18:33:22	2008-07-07 18:33:22
945	515	596	1	2008-07-07 18:33:22	2008-07-07 18:33:22
946	520	593	0	2008-07-07 18:34:14	2008-07-07 18:34:14
947	520	594	1	2008-07-07 18:34:14	2008-07-07 18:34:14
948	570	637	0	2008-07-07 18:34:33	2008-07-07 18:34:33
949	570	638	1	2008-07-07 18:34:33	2008-07-07 18:34:33
950	568	634	0	2008-07-07 18:35:21	2008-07-07 18:35:21
951	568	633	1	2008-07-07 18:35:21	2008-07-07 18:35:21
954	516	589	1	2008-07-07 18:36:16	2008-07-07 18:36:16
955	516	590	0	2008-07-07 18:36:16	2008-07-07 18:36:16
956	510	575	0	2008-07-07 18:37:40	2008-07-07 18:37:40
957	510	576	1	2008-07-07 18:37:40	2008-07-07 18:37:40
964	567	631	1	2008-07-07 18:39:31	2008-07-07 18:39:31
965	567	632	0	2008-07-07 18:39:31	2008-07-07 18:39:31
966	517	587	0	2008-07-07 18:40:22	2008-07-07 18:40:22
967	517	588	1	2008-07-07 18:40:22	2008-07-07 18:40:22
968	518	587	0	2008-07-07 18:40:22	2008-07-07 18:40:22
969	518	588	1	2008-07-07 18:40:22	2008-07-07 18:40:22
970	519	587	0	2008-07-07 18:40:22	2008-07-07 18:40:22
971	519	588	1	2008-07-07 18:40:22	2008-07-07 18:40:22
972	511	579	1	2008-07-07 18:42:34	2008-07-07 18:42:34
973	511	580	0	2008-07-07 18:42:34	2008-07-07 18:42:34
974	557	615	0	2008-07-07 18:43:01	2008-07-07 18:43:01
975	557	616	1	2008-07-07 18:43:01	2008-07-07 18:43:01
976	558	615	1	2008-07-07 18:43:01	2008-07-07 18:43:01
977	558	616	0	2008-07-07 18:43:01	2008-07-07 18:43:01
978	559	615	0	2008-07-07 18:43:01	2008-07-07 18:43:01
979	559	616	1	2008-07-07 18:43:01	2008-07-07 18:43:01
980	527	591	0	2008-07-07 18:44:45	2008-07-07 18:44:45
981	527	592	1	2008-07-07 18:44:45	2008-07-07 18:44:45
982	528	591	0	2008-07-07 18:44:45	2008-07-07 18:44:45
983	528	592	1	2008-07-07 18:44:45	2008-07-07 18:44:45
984	529	591	1	2008-07-07 18:44:45	2008-07-07 18:44:45
985	529	592	0	2008-07-07 18:44:45	2008-07-07 18:44:45
986	562	621	1	2008-07-07 18:45:24	2008-07-07 18:45:24
987	562	622	0	2008-07-07 18:45:24	2008-07-07 18:45:24
988	564	625	0	2008-07-07 18:45:46	2008-07-07 18:45:46
989	564	626	1	2008-07-07 18:45:46	2008-07-07 18:45:46
990	560	619	1	2008-07-07 18:46:49	2008-07-07 18:46:49
991	560	620	0	2008-07-07 18:46:49	2008-07-07 18:46:49
994	563	623	0	2008-07-07 18:47:44	2008-07-07 18:47:44
995	563	624	1	2008-07-07 18:47:44	2008-07-07 18:47:44
996	554	617	1	2008-07-07 18:49:03	2008-07-07 18:49:03
997	554	618	0	2008-07-07 18:49:03	2008-07-07 18:49:03
998	555	617	0	2008-07-07 18:49:03	2008-07-07 18:49:03
999	555	618	1	2008-07-07 18:49:03	2008-07-07 18:49:03
1000	556	617	1	2008-07-07 18:49:03	2008-07-07 18:49:03
1001	556	618	0	2008-07-07 18:49:03	2008-07-07 18:49:03
1002	539	605	0	2008-07-07 18:49:30	2008-07-07 18:49:30
1003	539	606	1	2008-07-07 18:49:30	2008-07-07 18:49:30
1004	540	605	0	2008-07-07 18:49:30	2008-07-07 18:49:30
1005	540	606	1	2008-07-07 18:49:30	2008-07-07 18:49:30
1006	541	605	0	2008-07-07 18:49:30	2008-07-07 18:49:30
1007	541	606	1	2008-07-07 18:49:30	2008-07-07 18:49:30
1008	569	636	1	2008-07-07 18:51:02	2008-07-07 18:51:02
1009	569	635	0	2008-07-07 18:51:02	2008-07-07 18:51:02
1010	545	607	1	2008-07-07 18:52:36	2008-07-07 18:52:36
1011	545	608	0	2008-07-07 18:52:36	2008-07-07 18:52:36
1012	546	607	1	2008-07-07 18:52:36	2008-07-07 18:52:36
1013	546	608	0	2008-07-07 18:52:36	2008-07-07 18:52:36
1014	547	607	1	2008-07-07 18:52:36	2008-07-07 18:52:36
1015	547	608	0	2008-07-07 18:52:36	2008-07-07 18:52:36
1016	533	597	0	2008-07-07 18:53:14	2008-07-07 18:53:14
1017	533	598	1	2008-07-07 18:53:14	2008-07-07 18:53:14
1018	534	597	0	2008-07-07 18:53:14	2008-07-07 18:53:14
1019	534	598	1	2008-07-07 18:53:14	2008-07-07 18:53:14
1020	535	597	0	2008-07-07 18:53:14	2008-07-07 18:53:14
1021	535	598	1	2008-07-07 18:53:14	2008-07-07 18:53:14
1022	565	627	0	2008-07-07 18:54:13	2008-07-07 18:54:13
1023	565	628	1	2008-07-07 18:54:13	2008-07-07 18:54:13
1024	566	629	0	2008-07-07 18:55:00	2008-07-07 18:55:00
1025	566	630	1	2008-07-07 18:55:00	2008-07-07 18:55:00
1026	521	599	0	2008-07-07 18:55:35	2008-07-07 18:55:35
1027	521	600	1	2008-07-07 18:55:35	2008-07-07 18:55:35
1028	522	599	0	2008-07-07 18:55:35	2008-07-07 18:55:35
1029	522	600	1	2008-07-07 18:55:35	2008-07-07 18:55:35
1030	523	599	0	2008-07-07 18:55:35	2008-07-07 18:55:35
1031	523	600	1	2008-07-07 18:55:35	2008-07-07 18:55:35
1032	536	601	0	2008-07-07 18:56:08	2008-07-07 18:56:08
1033	536	602	1	2008-07-07 18:56:08	2008-07-07 18:56:08
1034	537	601	0	2008-07-07 18:56:08	2008-07-07 18:56:08
1035	537	602	1	2008-07-07 18:56:08	2008-07-07 18:56:08
1036	538	601	0	2008-07-07 18:56:08	2008-07-07 18:56:08
1037	538	602	1	2008-07-07 18:56:08	2008-07-07 18:56:08
1038	524	603	1	2008-07-07 18:56:34	2008-07-07 18:56:34
1039	524	604	0	2008-07-07 18:56:34	2008-07-07 18:56:34
1040	525	603	1	2008-07-07 18:56:34	2008-07-07 18:56:34
1041	525	604	0	2008-07-07 18:56:34	2008-07-07 18:56:34
1042	526	603	1	2008-07-07 18:56:34	2008-07-07 18:56:34
1043	526	604	0	2008-07-07 18:56:34	2008-07-07 18:56:34
1044	514	583	1	2008-07-07 18:58:40	2008-07-07 18:58:40
1045	514	584	0	2008-07-07 18:58:40	2008-07-07 18:58:40
1046	548	609	1	2008-07-07 18:59:41	2008-07-07 18:59:41
1047	548	610	0	2008-07-07 18:59:41	2008-07-07 18:59:41
1048	549	609	1	2008-07-07 18:59:41	2008-07-07 18:59:41
1049	549	610	0	2008-07-07 18:59:41	2008-07-07 18:59:41
1050	550	609	1	2008-07-07 18:59:41	2008-07-07 18:59:41
1051	550	610	0	2008-07-07 18:59:41	2008-07-07 18:59:41
1052	542	571	0	2008-07-07 19:01:13	2008-07-07 19:01:13
1053	542	572	1	2008-07-07 19:01:13	2008-07-07 19:01:13
1054	543	571	1	2008-07-07 19:01:13	2008-07-07 19:01:13
1055	543	572	0	2008-07-07 19:01:13	2008-07-07 19:01:13
1056	544	571	0	2008-07-07 19:01:13	2008-07-07 19:01:13
1057	544	572	1	2008-07-07 19:01:13	2008-07-07 19:01:13
1058	530	569	0	2008-07-07 19:03:23	2008-07-07 19:03:23
1059	530	570	1	2008-07-07 19:03:23	2008-07-07 19:03:23
1060	531	569	1	2008-07-07 19:03:23	2008-07-07 19:03:23
1061	531	570	0	2008-07-07 19:03:23	2008-07-07 19:03:23
1062	532	569	1	2008-07-07 19:03:23	2008-07-07 19:03:23
1063	532	570	0	2008-07-07 19:03:23	2008-07-07 19:03:23
\.


--
-- Data for Name: team_scores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY team_scores (id, team_id, total_team_score, total_speaker_score, total_margin, created_at, updated_at) FROM stdin;
24	24	5	2126.1666666699998	-0.166666666667	2008-07-04 17:20:56	2008-07-07 19:04:31
25	25	3	2102.25	-12.25	2008-07-04 17:20:56	2008-07-07 19:04:32
26	26	3	2085.0833333300002	-14.833333333300001	2008-07-04 17:20:56	2008-07-07 19:04:33
27	27	4	2105.4166666699998	-3.3333333333300001	2008-07-04 17:20:56	2008-07-07 19:04:33
48	48	4	2111.5	0.66666666666700003	2008-07-04 17:21:00	2008-07-07 19:04:47
49	49	4	2084.3333333300002	-1.1666666666700001	2008-07-04 17:21:00	2008-07-07 19:04:47
50	50	4	2115	8.8333333333299997	2008-07-04 17:21:00	2008-07-07 19:04:48
51	51	4	2092.6666666699998	0	2008-07-04 17:21:00	2008-07-07 19:04:49
52	52	4	2112.25	-5.9166666666700003	2008-07-04 17:21:01	2008-07-07 19:04:49
53	53	6	2163	23.5	2008-07-04 17:21:01	2008-07-07 19:04:50
54	54	4	2112.8333333300002	-2.1666666666699999	2008-07-04 17:21:01	2008-07-07 19:04:50
55	55	2	2093.9166666699998	-8.25	2008-07-04 17:21:01	2008-07-07 19:04:51
56	56	2	2085.3333333300002	-16.333333333300001	2008-07-04 17:21:01	2008-07-07 19:04:52
57	57	8	2175.0833333300002	39.333333333299997	2008-07-04 17:21:02	2008-07-07 19:04:53
58	58	6	2164.5	26.75	2008-07-04 17:21:02	2008-07-07 19:04:53
59	59	6	2131	19.666666666699999	2008-07-04 17:21:02	2008-07-07 19:04:54
60	60	5	2146.1666666699998	11.333333333300001	2008-07-04 17:21:02	2008-07-07 19:04:55
61	61	6	2128.5	13.5	2008-07-04 17:21:02	2008-07-07 19:04:55
62	62	5	2128	11.5	2008-07-04 17:21:02	2008-07-07 19:04:56
64	64	3	2091.0833333300002	-4.25	2008-07-04 17:21:03	2008-07-07 19:04:57
65	65	3	2072	-12.833333333300001	2008-07-04 17:21:03	2008-07-07 19:04:57
72	72	6	2132.5	22.666666666699999	2008-07-04 17:21:04	2008-07-07 19:05:02
73	73	5	2106.1666666699998	10	2008-07-04 17:21:04	2008-07-07 19:05:03
74	74	3	2058.5	-20.583333333300001	2008-07-04 17:21:04	2008-07-07 19:05:03
22	22	3	2089.75	-3.6666666666699999	2008-07-04 17:20:55	2008-07-07 19:05:04
63	63	2	2105.9166666699998	-10.666666666699999	2008-07-04 17:21:03	2008-07-07 19:05:05
9	9	3	2080.0833333300002	-1	2008-07-04 17:20:54	2008-07-07 19:05:06
1	1	4	2077.6666666699998	8.3333333333299997	2008-07-04 17:20:52	2008-07-07 19:04:17
2	2	2	2082	-13.416666666699999	2008-07-04 17:20:52	2008-07-07 19:04:18
3	3	6	2167	25.5	2008-07-04 17:20:53	2008-07-07 19:04:18
4	4	5	2139.8333333300002	26.166666666699999	2008-07-04 17:20:53	2008-07-07 19:04:19
5	5	5	2124.5	20	2008-07-04 17:20:53	2008-07-07 19:04:19
6	6	5	2115.5	14.166666666699999	2008-07-04 17:20:53	2008-07-07 19:04:20
7	7	4	2114.1666666699998	1.1666666666700001	2008-07-04 17:20:53	2008-07-07 19:04:21
8	8	3	2076.4166666699998	-7.1666666666700003	2008-07-04 17:20:53	2008-07-07 19:04:21
10	10	3	2078.1666666699998	-9.5833333333299997	2008-07-04 17:20:54	2008-07-07 19:04:22
11	11	3	2086.5	-1	2008-07-04 17:20:54	2008-07-07 19:04:23
12	12	4	2043.25	-19	2008-07-04 17:20:54	2008-07-07 19:04:24
13	13	2	2046.83333333	-27	2008-07-04 17:20:54	2008-07-07 19:04:24
14	14	1	2028.41666667	-34.083333333299997	2008-07-04 17:20:54	2008-07-07 19:04:25
15	15	5	2115	4.8333333333299997	2008-07-04 17:20:54	2008-07-07 19:04:26
16	16	4	2107.6666666699998	6.3333333333299997	2008-07-04 17:20:54	2008-07-07 19:04:26
17	17	3	2076.1666666699998	-20.166666666699999	2008-07-04 17:20:55	2008-07-07 19:04:27
18	18	4	2095.5833333300002	-6.5	2008-07-04 17:20:55	2008-07-07 19:04:28
19	19	2	2082.75	-18.916666666699999	2008-07-04 17:20:55	2008-07-07 19:04:29
20	20	5	2105.3333333300002	11.75	2008-07-04 17:20:55	2008-07-07 19:04:29
21	21	4	2099.4166666699998	3.1666666666699999	2008-07-04 17:20:55	2008-07-07 19:04:30
23	23	3	2089.4166666699998	1.75	2008-07-04 17:20:56	2008-07-07 19:04:31
28	28	1	2043.58333333	-30	2008-07-04 17:20:57	2008-07-07 19:04:34
29	29	2	2032.16666667	-40.916666666700003	2008-07-04 17:20:57	2008-07-07 19:04:35
30	30	7	2152.3333333300002	25.333333333300001	2008-07-04 17:20:57	2008-07-07 19:04:36
31	31	5	2103.3333333300002	2.8333333333300001	2008-07-04 17:20:57	2008-07-07 19:04:36
32	32	5	2104	23.833333333300001	2008-07-04 17:20:57	2008-07-07 19:04:37
33	33	6	2140	25	2008-07-04 17:20:58	2008-07-07 19:04:38
34	34	5	2133.3333333300002	-4.6666666666700003	2008-07-04 17:20:58	2008-07-07 19:04:38
35	35	5	2110	0.5	2008-07-04 17:20:58	2008-07-07 19:04:39
36	36	4	2108.5	-4.5	2008-07-04 17:20:58	2008-07-07 19:04:39
37	37	4	2117.5	-11.666666666699999	2008-07-04 17:20:58	2008-07-07 19:04:40
39	39	5	2110.1666666699998	3.5	2008-07-04 17:20:59	2008-07-07 19:04:41
40	40	5	2108.6666666699998	6.5	2008-07-04 17:20:59	2008-07-07 19:04:41
41	41	4	2104.5	-2	2008-07-04 17:20:59	2008-07-07 19:04:42
42	42	4	2111.3333333300002	10.333333333300001	2008-07-04 17:20:59	2008-07-07 19:04:43
43	43	5	2127.5	11	2008-07-04 17:20:59	2008-07-07 19:04:43
44	44	4	2110.25	-3	2008-07-04 17:20:59	2008-07-07 19:04:44
45	45	4	2100.4166666699998	0.58333333333299997	2008-07-04 17:21:00	2008-07-07 19:04:45
46	46	2	2072.25	-14.583333333300001	2008-07-04 17:21:00	2008-07-07 19:04:45
47	47	3	2096.0833333300002	-2.9166666666699999	2008-07-04 17:21:00	2008-07-07 19:04:46
66	66	3	2078.25	-18.75	2008-07-04 17:21:03	2008-07-07 19:04:58
67	67	5	2120.5	12	2008-07-04 17:21:03	2008-07-07 19:04:58
68	68	4	2093.8333333300002	3.3333333333300001	2008-07-04 17:21:03	2008-07-07 19:04:59
69	69	2	2063.8333333300002	-28.5	2008-07-04 17:21:04	2008-07-07 19:05:00
70	70	2	2058.3333333300002	-17.5	2008-07-04 17:21:04	2008-07-07 19:05:01
71	71	6	2161.1666666699998	23.083333333300001	2008-07-04 17:21:04	2008-07-07 19:05:01
75	75	4	2064.4166667	-20.5	2008-07-29 10:40:28	2008-07-07 19:05:05
\.


--
-- Data for Name: teams; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY teams (id, name, institution_id, swing, active, created_at, updated_at) FROM stdin;
1	Assumption 1	1	f	t	2008-07-04 17:20:52	2008-07-04 17:20:52
2	Assumption 2	1	f	t	2008-07-04 17:20:52	2008-07-04 17:20:52
3	Ateneo 1	2	f	t	2008-07-04 17:20:53	2008-07-04 17:20:53
4	Ateneo 2	2	f	t	2008-07-04 17:20:53	2008-07-04 17:20:53
5	Ateneo 3	2	f	t	2008-07-04 17:20:53	2008-07-04 17:20:53
6	Ateneo 4	2	f	t	2008-07-04 17:20:53	2008-07-04 17:20:53
7	Ateneo 5	2	f	t	2008-07-04 17:20:53	2008-07-04 17:20:53
8	CSB 1	3	f	t	2008-07-04 17:20:53	2008-07-04 17:20:53
10	CUHK 2	4	f	t	2008-07-04 17:20:54	2008-07-04 17:20:54
11	CUHK 3	4	f	t	2008-07-04 17:20:54	2008-07-04 17:20:54
12	DAE 1	5	f	t	2008-07-04 17:20:54	2008-07-04 17:20:54
13	DAE 2	5	f	t	2008-07-04 17:20:54	2008-07-04 17:20:54
14	DAE 3	5	f	t	2008-07-04 17:20:54	2008-07-04 17:20:54
15	DLSU 1	6	f	t	2008-07-04 17:20:54	2008-07-04 17:20:54
16	DLSU 2	6	f	t	2008-07-04 17:20:54	2008-07-04 17:20:54
17	EDIS 1	7	f	t	2008-07-04 17:20:55	2008-07-04 17:20:55
18	FEU 1	8	f	t	2008-07-04 17:20:55	2008-07-04 17:20:55
19	ICU 1	9	f	t	2008-07-04 17:20:55	2008-07-04 17:20:55
20	IIU 1	10	f	t	2008-07-04 17:20:55	2008-07-04 17:20:55
21	IIU 2	10	f	t	2008-07-04 17:20:55	2008-07-04 17:20:55
23	ITB 1	11	f	t	2008-07-04 17:20:56	2008-07-04 17:20:56
24	MMU 1	14	f	t	2008-07-04 17:20:56	2008-07-04 17:20:56
25	MMU 2	14	f	t	2008-07-04 17:20:56	2008-07-04 17:20:56
26	MMU 3	14	f	t	2008-07-04 17:20:56	2008-07-04 17:20:56
27	MMUM 1	15	f	t	2008-07-04 17:20:56	2008-07-04 17:20:56
28	Macau 1	16	f	t	2008-07-04 17:20:57	2008-07-04 17:20:57
29	Macau 2	16	f	t	2008-07-04 17:20:57	2008-07-04 17:20:57
30	Melbourne 1	17	f	t	2008-07-04 17:20:57	2008-07-04 17:20:57
31	Melbourne 2	17	f	t	2008-07-04 17:20:57	2008-07-04 17:20:57
32	Melbourne 3	17	f	t	2008-07-04 17:20:57	2008-07-04 17:20:57
33	Monash 1	18	f	t	2008-07-04 17:20:57	2008-07-04 17:20:57
34	Monash 2	18	f	t	2008-07-04 17:20:58	2008-07-04 17:20:58
35	Monash 3	18	f	t	2008-07-04 17:20:58	2008-07-04 17:20:58
36	Monash 4	18	f	t	2008-07-04 17:20:58	2008-07-04 17:20:58
37	Monash 5	18	f	t	2008-07-04 17:20:58	2008-07-04 17:20:58
39	NTU 1	20	f	t	2008-07-04 17:20:59	2008-07-04 17:20:59
40	NTU 2	20	f	t	2008-07-04 17:20:59	2008-07-04 17:20:59
41	NTU 3	20	f	t	2008-07-04 17:20:59	2008-07-04 17:20:59
42	NUJS 1	21	f	t	2008-07-04 17:20:59	2008-07-04 17:20:59
43	NUS 1	22	f	t	2008-07-04 17:20:59	2008-07-04 17:20:59
44	NUS 2	22	f	t	2008-07-04 17:20:59	2008-07-04 17:20:59
45	SLU 1	24	f	t	2008-07-04 17:21:00	2008-07-04 17:21:00
46	Singapore Poly 1	25	f	t	2008-07-04 17:21:00	2008-07-04 17:21:00
47	UHK 1	26	f	t	2008-07-04 17:21:00	2008-07-04 17:21:00
48	UI 1	27	f	t	2008-07-04 17:21:00	2008-07-04 17:21:00
49	UKM 1	28	f	t	2008-07-04 17:21:00	2008-07-04 17:21:00
50	UNSW 1	29	f	t	2008-07-04 17:21:00	2008-07-04 17:21:00
51	UNSW 2	29	f	t	2008-07-04 17:21:00	2008-07-04 17:21:00
52	UPD 1	30	f	t	2008-07-04 17:21:01	2008-07-04 17:21:01
53	UQ 1	31	f	t	2008-07-04 17:21:01	2008-07-04 17:21:01
54	UQ 2	31	f	t	2008-07-04 17:21:01	2008-07-04 17:21:01
55	UST 1	32	f	t	2008-07-04 17:21:01	2008-07-04 17:21:01
56	UST 2	32	f	t	2008-07-04 17:21:01	2008-07-04 17:21:01
57	USyd 1	33	f	t	2008-07-04 17:21:02	2008-07-04 17:21:02
58	USyd 2	33	f	t	2008-07-04 17:21:02	2008-07-04 17:21:02
59	USyd 3	33	f	t	2008-07-04 17:21:02	2008-07-04 17:21:02
60	USyd 4	33	f	t	2008-07-04 17:21:02	2008-07-04 17:21:02
61	USyd 5	33	f	t	2008-07-04 17:21:02	2008-07-04 17:21:02
62	USyd 6	33	f	t	2008-07-04 17:21:02	2008-07-04 17:21:02
64	UT Mara 2	34	f	t	2008-07-04 17:21:03	2008-07-04 17:21:03
65	UT Mara 3	34	f	t	2008-07-04 17:21:03	2008-07-04 17:21:03
66	UT Mara 4	34	f	t	2008-07-04 17:21:03	2008-07-04 17:21:03
67	UTS 1	36	f	t	2008-07-04 17:21:03	2008-07-04 17:21:03
68	UTS 2	36	f	t	2008-07-04 17:21:03	2008-07-04 17:21:03
69	UiTM Johor 1	38	f	t	2008-07-04 17:21:04	2008-07-04 17:21:04
70	UiTM Terengganu 1	39	f	t	2008-07-04 17:21:04	2008-07-04 17:21:04
71	Vic 1	40	f	t	2008-07-04 17:21:04	2008-07-04 17:21:04
72	Vic 2	40	f	t	2008-07-04 17:21:04	2008-07-04 17:21:04
73	Vic 3	40	f	t	2008-07-04 17:21:04	2008-07-04 17:21:04
74	WUPID 1	41	f	t	2008-07-04 17:21:04	2008-07-04 17:21:04
22	IIU 3	10	f	t	2008-07-04 17:20:55	2008-07-29 15:22:15
63	UT Mara 1	34	f	t	2008-07-04 17:21:03	2008-07-29 16:09:51
75	NLSIU 1	19	t	t	2008-07-29 10:40:28	2008-07-29 16:21:24
9	CUHK 1	4	f	t	2008-07-04 17:20:53	2008-07-06 12:05:10
\.


--
-- Data for Name: trainee_allocations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY trainee_allocations (id, trainee_id, chair_id, round_id, created_at, updated_at) FROM stdin;
1	25	35	1	2008-07-04 18:48:35	2008-07-04 18:48:35
3	2	37	1	2008-07-04 18:48:35	2008-07-04 18:48:35
4	68	12	1	2008-07-04 18:48:35	2008-07-04 18:48:35
5	22	71	1	2008-07-04 18:48:35	2008-07-04 18:48:35
6	46	5	1	2008-07-04 18:48:35	2008-07-04 18:48:35
8	63	55	1	2008-07-04 18:48:35	2008-07-04 18:48:35
9	65	11	1	2008-07-04 18:48:35	2008-07-04 18:48:35
10	72	38	1	2008-07-04 18:48:35	2008-07-04 18:48:35
11	66	4	1	2008-07-04 18:48:35	2008-07-04 18:48:35
12	22	34	2	2008-07-29 13:19:54	2008-07-29 13:19:54
13	43	4	2	2008-07-29 13:19:54	2008-07-29 13:19:54
14	63	55	2	2008-07-29 13:19:54	2008-07-29 13:19:54
15	65	24	2	2008-07-29 13:19:54	2008-07-29 13:19:54
16	66	35	2	2008-07-29 13:19:54	2008-07-29 13:19:54
17	72	30	2	2008-07-29 13:19:54	2008-07-29 13:19:54
18	68	3	2	2008-07-29 13:19:54	2008-07-29 13:19:54
2	43	59	1	2008-07-04 18:48:35	2008-07-04 18:48:35
19	22	5	3	2008-07-29 16:37:28	2008-07-29 16:37:28
20	43	24	3	2008-07-29 16:37:28	2008-07-29 16:37:28
21	46	37	3	2008-07-29 16:37:28	2008-07-29 16:37:28
22	63	71	3	2008-07-29 16:37:28	2008-07-29 16:37:28
23	65	34	3	2008-07-29 16:37:28	2008-07-29 16:37:28
24	66	58	3	2008-07-29 16:37:28	2008-07-29 16:37:28
25	72	55	3	2008-07-29 16:37:28	2008-07-29 16:37:28
26	68	36	3	2008-07-29 16:37:28	2008-07-29 16:37:28
27	22	4	4	2008-07-29 20:49:21	2008-07-29 20:49:21
28	65	71	4	2008-07-29 20:49:21	2008-07-29 20:49:21
29	63	37	4	2008-07-29 20:49:21	2008-07-29 20:49:21
30	68	35	4	2008-07-29 20:49:21	2008-07-29 20:49:21
31	43	34	5	2008-07-06 13:16:05	2008-07-06 13:16:05
32	68	71	5	2008-07-06 13:16:05	2008-07-06 13:16:05
33	65	35	5	2008-07-06 13:16:05	2008-07-06 13:16:05
34	46	37	5	2008-07-06 13:16:05	2008-07-06 13:16:05
\.


--
-- Data for Name: venues; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY venues (id, name, active, priority, created_at, updated_at) FROM stdin;
44	SECA112	t	1	2008-07-04 18:32:53	2008-07-04 18:32:53
47	SECA204	t	1	2008-07-04 18:32:53	2008-07-04 18:32:53
48	SECA205	t	1	2008-07-04 18:32:53	2008-07-04 18:32:53
49	CTC204	t	1	2008-07-04 18:32:53	2008-07-04 18:32:53
69	CTC 202	t	1	2008-07-04 18:32:53	2008-07-29 15:15:13
70	CTC 203	t	1	2008-07-04 18:32:53	2008-07-29 15:15:27
71	CTC 205	t	1	2008-07-04 18:32:53	2008-07-29 15:15:43
72	CTC 206	t	1	2008-07-04 18:32:53	2008-07-29 15:15:54
73	CTC 301	t	1	2008-07-04 18:32:53	2008-07-29 15:16:15
74	CTC 302	t	1	2008-07-04 18:32:53	2008-07-29 15:16:27
76	CTC 303	t	1	2008-07-04 18:32:53	2008-07-29 15:16:47
75	CTC 304	t	1	2008-07-04 18:32:53	2008-07-29 15:17:01
77	CTC 305	t	1	2008-07-04 18:32:53	2008-07-29 15:17:16
53	SOM 105	t	1	2008-07-04 18:32:53	2008-07-07 02:01:43
55	SOM 106	t	1	2008-07-04 18:32:53	2008-07-07 02:02:12
60	SOM 202	t	1	2008-07-04 18:32:53	2008-07-07 02:02:58
41	Escaler Hall	t	999	2008-07-04 18:32:53	2008-07-07 10:24:45
56	SEC LEC B	t	888	2008-07-04 18:32:53	2008-07-07 10:24:55
57	SEC LEC C	t	777	2008-07-04 18:32:53	2008-07-07 10:25:07
50	FAVR	t	666	2008-07-04 18:32:53	2008-07-07 10:25:21
45	SOM 210	t	100	2008-07-04 18:32:53	2008-07-07 02:03:38
46	SOM 211	t	100	2008-07-04 18:32:53	2008-07-07 02:04:00
51	SECA 116	t	100	2008-07-04 18:32:53	2008-07-29 19:38:56
52	SECA 117	t	100	2008-07-04 18:32:53	2008-07-29 19:40:29
54	SECA 214	t	100	2008-07-04 18:32:53	2008-07-29 19:40:43
43	SEC A 208	t	100	2008-07-04 18:32:53	2008-07-29 19:42:32
42	SEC A 124	t	100	2008-07-04 18:32:53	2008-07-29 15:12:31
61	SEC A 209	t	100	2008-07-04 18:32:53	2008-07-29 15:13:10
62	SEC A 210	t	100	2008-07-04 18:32:53	2008-07-29 15:13:29
63	CTC 102	t	100	2008-07-04 18:32:53	2008-07-29 15:13:43
64	CTC 103	t	100	2008-07-04 18:32:53	2008-07-29 15:14:00
65	CTC 104	t	100	2008-07-04 18:32:53	2008-07-29 15:14:15
66	CTC 105	t	100	2008-07-04 18:32:53	2008-07-29 15:14:32
67	CTC 106	t	100	2008-07-04 18:32:53	2008-07-29 15:14:45
68	CTC 107	t	100	2008-07-04 18:32:53	2008-07-29 15:14:56
59	SOM 111	t	100	2008-07-04 18:32:53	2008-07-07 02:02:43
58	CTC 118	t	100	2008-07-04 18:32:53	2008-07-07 14:53:01
\.


--
-- Name: adjudicator_allocations_debate_id_adjudicator_id; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adjudicator_allocations
    ADD CONSTRAINT adjudicator_allocations_debate_id_adjudicator_id UNIQUE (debate_id, adjudicator_id);


--
-- Name: adjudicator_allocations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adjudicator_allocations
    ADD CONSTRAINT adjudicator_allocations_pkey PRIMARY KEY (id);


--
-- Name: adjudicator_conflicts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adjudicator_conflicts
    ADD CONSTRAINT adjudicator_conflicts_pkey PRIMARY KEY (id);


--
-- Name: adjudicator_feedback_sheets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adjudicator_feedback_sheets
    ADD CONSTRAINT adjudicator_feedback_sheets_pkey PRIMARY KEY (id);


--
-- Name: adjudicators_name; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adjudicators
    ADD CONSTRAINT adjudicators_name UNIQUE (name);


--
-- Name: adjudicators_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adjudicators
    ADD CONSTRAINT adjudicators_pkey PRIMARY KEY (id);


--
-- Name: debaters_name; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY debaters
    ADD CONSTRAINT debaters_name UNIQUE (name);


--
-- Name: debaters_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY debaters
    ADD CONSTRAINT debaters_pkey PRIMARY KEY (id);


--
-- Name: debates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY debates
    ADD CONSTRAINT debates_pkey PRIMARY KEY (id);


--
-- Name: debates_round_id_venue_id; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY debates
    ADD CONSTRAINT debates_round_id_venue_id UNIQUE (round_id, venue_id);


--
-- Name: debates_teams_xrefs_debate_id_team_id; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY debates_teams_xrefs
    ADD CONSTRAINT debates_teams_xrefs_debate_id_team_id UNIQUE (debate_id, team_id);


--
-- Name: debates_teams_xrefs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY debates_teams_xrefs
    ADD CONSTRAINT debates_teams_xrefs_pkey PRIMARY KEY (id);


--
-- Name: institutions_code; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY institutions
    ADD CONSTRAINT institutions_code UNIQUE (code);


--
-- Name: institutions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY institutions
    ADD CONSTRAINT institutions_pkey PRIMARY KEY (id);


--
-- Name: rounds_name; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY rounds
    ADD CONSTRAINT rounds_name UNIQUE (name);


--
-- Name: rounds_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY rounds
    ADD CONSTRAINT rounds_pkey PRIMARY KEY (id);


--
-- Name: speaker_score_sheets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY speaker_score_sheets
    ADD CONSTRAINT speaker_score_sheets_pkey PRIMARY KEY (id);


--
-- Name: speaker_scores_debater_id; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY speaker_scores
    ADD CONSTRAINT speaker_scores_debater_id UNIQUE (debater_id);


--
-- Name: speaker_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY speaker_scores
    ADD CONSTRAINT speaker_scores_pkey PRIMARY KEY (id);


--
-- Name: team_score_sheets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY team_score_sheets
    ADD CONSTRAINT team_score_sheets_pkey PRIMARY KEY (id);


--
-- Name: team_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY team_scores
    ADD CONSTRAINT team_scores_pkey PRIMARY KEY (id);


--
-- Name: team_scores_team_id; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY team_scores
    ADD CONSTRAINT team_scores_team_id UNIQUE (team_id);


--
-- Name: teams_name; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY teams
    ADD CONSTRAINT teams_name UNIQUE (name);


--
-- Name: teams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (id);


--
-- Name: trainee_allocations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY trainee_allocations
    ADD CONSTRAINT trainee_allocations_pkey PRIMARY KEY (id);


--
-- Name: trainee_allocations_trainee_id_chair_id_round_id; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY trainee_allocations
    ADD CONSTRAINT trainee_allocations_trainee_id_chair_id_round_id UNIQUE (trainee_id, chair_id, round_id);


--
-- Name: venues_name; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY venues
    ADD CONSTRAINT venues_name UNIQUE (name);


--
-- Name: venues_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY venues
    ADD CONSTRAINT venues_pkey PRIMARY KEY (id);


--
-- Name: adjudicator_allocations_FK_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY adjudicator_allocations
    ADD CONSTRAINT "adjudicator_allocations_FK_1" FOREIGN KEY (debate_id) REFERENCES debates(id);


--
-- Name: adjudicator_allocations_FK_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY adjudicator_allocations
    ADD CONSTRAINT "adjudicator_allocations_FK_2" FOREIGN KEY (adjudicator_id) REFERENCES adjudicators(id);


--
-- Name: adjudicator_conflicts_FK_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY adjudicator_conflicts
    ADD CONSTRAINT "adjudicator_conflicts_FK_1" FOREIGN KEY (team_id) REFERENCES teams(id);


--
-- Name: adjudicator_conflicts_FK_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY adjudicator_conflicts
    ADD CONSTRAINT "adjudicator_conflicts_FK_2" FOREIGN KEY (adjudicator_id) REFERENCES adjudicators(id);


--
-- Name: adjudicator_feedback_sheets_FK_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY adjudicator_feedback_sheets
    ADD CONSTRAINT "adjudicator_feedback_sheets_FK_1" FOREIGN KEY (adjudicator_id) REFERENCES adjudicators(id);


--
-- Name: adjudicator_feedback_sheets_FK_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY adjudicator_feedback_sheets
    ADD CONSTRAINT "adjudicator_feedback_sheets_FK_2" FOREIGN KEY (adjudicator_allocation_id) REFERENCES adjudicator_allocations(id);


--
-- Name: adjudicator_feedback_sheets_FK_3; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY adjudicator_feedback_sheets
    ADD CONSTRAINT "adjudicator_feedback_sheets_FK_3" FOREIGN KEY (debate_team_xref_id) REFERENCES debates_teams_xrefs(id);


--
-- Name: adjudicators_FK_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY adjudicators
    ADD CONSTRAINT "adjudicators_FK_1" FOREIGN KEY (institution_id) REFERENCES institutions(id);


--
-- Name: debaters_FK_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY debaters
    ADD CONSTRAINT "debaters_FK_1" FOREIGN KEY (team_id) REFERENCES teams(id);


--
-- Name: debates_FK_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY debates
    ADD CONSTRAINT "debates_FK_1" FOREIGN KEY (round_id) REFERENCES rounds(id);


--
-- Name: debates_FK_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY debates
    ADD CONSTRAINT "debates_FK_2" FOREIGN KEY (venue_id) REFERENCES venues(id);


--
-- Name: debates_teams_xrefs_FK_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY debates_teams_xrefs
    ADD CONSTRAINT "debates_teams_xrefs_FK_1" FOREIGN KEY (debate_id) REFERENCES debates(id);


--
-- Name: debates_teams_xrefs_FK_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY debates_teams_xrefs
    ADD CONSTRAINT "debates_teams_xrefs_FK_2" FOREIGN KEY (team_id) REFERENCES teams(id);


--
-- Name: rounds_FK_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY rounds
    ADD CONSTRAINT "rounds_FK_1" FOREIGN KEY (preceded_by_round_id) REFERENCES rounds(id);


--
-- Name: speaker_score_sheets_FK_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY speaker_score_sheets
    ADD CONSTRAINT "speaker_score_sheets_FK_1" FOREIGN KEY (adjudicator_allocation_id) REFERENCES adjudicator_allocations(id);


--
-- Name: speaker_score_sheets_FK_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY speaker_score_sheets
    ADD CONSTRAINT "speaker_score_sheets_FK_2" FOREIGN KEY (debate_team_xref_id) REFERENCES debates_teams_xrefs(id);


--
-- Name: speaker_score_sheets_FK_3; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY speaker_score_sheets
    ADD CONSTRAINT "speaker_score_sheets_FK_3" FOREIGN KEY (debater_id) REFERENCES debaters(id);


--
-- Name: speaker_scores_FK_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY speaker_scores
    ADD CONSTRAINT "speaker_scores_FK_1" FOREIGN KEY (debater_id) REFERENCES debaters(id);


--
-- Name: team_score_sheets_FK_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY team_score_sheets
    ADD CONSTRAINT "team_score_sheets_FK_1" FOREIGN KEY (adjudicator_allocation_id) REFERENCES adjudicator_allocations(id);


--
-- Name: team_score_sheets_FK_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY team_score_sheets
    ADD CONSTRAINT "team_score_sheets_FK_2" FOREIGN KEY (debate_team_xref_id) REFERENCES debates_teams_xrefs(id);


--
-- Name: team_scores_FK_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY team_scores
    ADD CONSTRAINT "team_scores_FK_1" FOREIGN KEY (team_id) REFERENCES teams(id);


--
-- Name: teams_FK_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY teams
    ADD CONSTRAINT "teams_FK_1" FOREIGN KEY (institution_id) REFERENCES institutions(id);


--
-- Name: trainee_allocations_FK_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY trainee_allocations
    ADD CONSTRAINT "trainee_allocations_FK_1" FOREIGN KEY (trainee_id) REFERENCES adjudicators(id);


--
-- Name: trainee_allocations_FK_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY trainee_allocations
    ADD CONSTRAINT "trainee_allocations_FK_2" FOREIGN KEY (chair_id) REFERENCES adjudicators(id);


--
-- Name: trainee_allocations_FK_3; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY trainee_allocations
    ADD CONSTRAINT "trainee_allocations_FK_3" FOREIGN KEY (round_id) REFERENCES rounds(id);


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

