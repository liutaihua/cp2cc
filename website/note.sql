--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

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
-- Name: account; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE account (
    id integer NOT NULL,
    name character varying(64),
    email character varying(64)
);


ALTER TABLE public.account OWNER TO postgres;

--
-- Name: account_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE account_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.account_id_seq OWNER TO postgres;

--
-- Name: account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE account_id_seq OWNED BY account.id;


--
-- Name: account_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('account_id_seq', 5, true);


--
-- Name: txt_log; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE txt_log (
    id integer NOT NULL,
    url_id bigint,
    user_id bigint,
    "time" bigint
);


ALTER TABLE public.txt_log OWNER TO postgres;

--
-- Name: txt_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE txt_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.txt_log_id_seq OWNER TO postgres;

--
-- Name: txt_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE txt_log_id_seq OWNED BY txt_log.id;


--
-- Name: txt_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('txt_log_id_seq', 1, false);


--
-- Name: url_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE url_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.url_id_seq OWNER TO postgres;

--
-- Name: url_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('url_id_seq', 1, false);


--
-- Name: url_info; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE url_info (
    url character varying(999),
    id integer NOT NULL
);


ALTER TABLE public.url_info OWNER TO postgres;

--
-- Name: url_info_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE url_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.url_info_id_seq OWNER TO postgres;

--
-- Name: url_info_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE url_info_id_seq OWNED BY url_info.id;


--
-- Name: url_info_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('url_info_id_seq', 20, true);


--
-- Name: user_note; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE user_note (
    id integer NOT NULL,
    url_id bigint,
    user_id bigint,
    state bigint,
    view_time bigint
);


ALTER TABLE public.user_note OWNER TO postgres;

--
-- Name: user_note_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE user_note_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_note_id_seq OWNER TO postgres;

--
-- Name: user_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE user_note_id_seq OWNED BY user_note.id;


--
-- Name: user_note_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('user_note_id_seq', 1, false);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY account ALTER COLUMN id SET DEFAULT nextval('account_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY txt_log ALTER COLUMN id SET DEFAULT nextval('txt_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY url_info ALTER COLUMN id SET DEFAULT nextval('url_info_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_note ALTER COLUMN id SET DEFAULT nextval('user_note_id_seq'::regclass);


--
-- Data for Name: account; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY account (id, name, email) FROM stdin;
1	tt	t@gmail.com
1	tt	t@gmail.com
2	\\u592a\\u534e \\u5218	d@gmail.com
3	\\u592a\\u534e \\u5218	d@gmail.com
4	\\u592a\\u534e \\u5218	d@gmail.com
5	\\u592a\\u534e \\u5218	d@gmail.com
1	tt	t@gmail.com
1	tt	t@gmail.com
2	\\u592a\\u534e \\u5218	d@gmail.com
3	\\u592a\\u534e \\u5218	d@gmail.com
4	\\u592a\\u534e \\u5218	d@gmail.com
5	\\u592a\\u534e \\u5218	d@gmail.com
\.


--
-- Data for Name: txt_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY txt_log (id, url_id, user_id, "time") FROM stdin;
\.


--
-- Data for Name: url_info; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY url_info (url, id) FROM stdin;
tes	1
3jfj39234	2
3jfj39234	3
honm29qj	4
ay55b7qll	5
60mldgq	6
dgyo7xkpl	7
mkrzrhod3	8
ct88tn6	9
96wclgg	10
prxlnesx	11
7udplfy	12
q53xdunyl	13
agh211l0	14
mt8tvdg	15
x8eyj298y	16
y7x8wui8	17
6gjszf5m	18
j1zh7r1m	19
1d9gwz45a	20
jr43l0r9	21
phn0lhaq	22
txt/phn0lhaq	23
zbanjxoat	24
txt/zbanjxoat	25
4zu1choh0	26
txt/4zu1choh0	27
43tcx1s	28
3ga28g4e	29
6wc19u6	30
spz2w5q	31
3j1r18h	32
rhw1jwa	33
fe6djay	34
dgss1kz5	35
images/bg.png	36
images/loading.gif	37
images/favicon.gif	38
borooko45	39
test	40
http://180.153.136.14:8888/fe6djay	41
/fe6djay	42
images/button_bg.png	43
images/bubble_nipple.png	44
kfj61gomy	45
5xc5webi	46
k8rhl2v6	47
a3jnvh45	48
testyou	49
504xmab	50
blg	51
bllj	52
0fng8cl2	53
r7jgpcqfo	54
52pjzxd	55
op5os9i6m	56
7xtiywv	57
justin_1	58
wangjunyan	59
wangjunyan/note1	60
0p8x29bw4	61
jzdhhrl	62
47b9d8w	63
vbo9z43	64
pmaa7izy	65
07c4svvy9	66
yu1wz80wy	67
8oyseb66i	68
rak984ad	69
ku3tqpj0k	70
rs48muo	71
egie020uz	72
ujjur7u	73
xzs18qmq	74
zo0ffl3w2	75
bebiznd5w	76
account/login	77
tes	1
3jfj39234	2
3jfj39234	3
honm29qj	4
ay55b7qll	5
60mldgq	6
dgyo7xkpl	7
mkrzrhod3	8
ct88tn6	9
96wclgg	10
prxlnesx	11
7udplfy	12
q53xdunyl	13
agh211l0	14
mt8tvdg	15
x8eyj298y	16
y7x8wui8	17
6gjszf5m	18
j1zh7r1m	19
1d9gwz45a	20
\.


--
-- Data for Name: user_note; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY user_note (id, url_id, user_id, state, view_time) FROM stdin;
\.


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

