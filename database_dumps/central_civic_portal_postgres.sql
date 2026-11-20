--
-- PostgreSQL database dump
--

\restrict X0iMGC9ZMhEjt3ZnPPP1q6zpKfTexqruJeoqcRFJzShFfOrbYpKzFyfwc4rft2e

-- Dumped from database version 16.15
-- Dumped by pg_dump version 16.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: administrative_units; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.administrative_units (
    id integer NOT NULL,
    identifier character varying(50) NOT NULL,
    name character varying(150) NOT NULL,
    unit_type character varying(50) NOT NULL,
    parent_id integer,
    status character varying(50) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT check_valid_unit_status CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying])::text[]))),
    CONSTRAINT check_valid_unit_type CHECK (((unit_type)::text = ANY ((ARRAY['country'::character varying, 'state'::character varying, 'district'::character varying, 'sub_district'::character varying, 'ward'::character varying, 'village'::character varying])::text[])))
);


ALTER TABLE public.administrative_units OWNER TO postgres;

--
-- Name: administrative_units_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.administrative_units_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.administrative_units_id_seq OWNER TO postgres;

--
-- Name: administrative_units_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.administrative_units_id_seq OWNED BY public.administrative_units.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    actor_id integer,
    actor_email character varying(255) NOT NULL,
    action character varying(100) NOT NULL,
    resource_type character varying(50) NOT NULL,
    resource_id character varying(100) NOT NULL,
    details text,
    created_at timestamp with time zone NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: citizen_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.citizen_profiles (
    id integer NOT NULL,
    user_id integer,
    citizen_code character varying(50) NOT NULL,
    full_name character varying(255) NOT NULL,
    date_of_birth date,
    phone_number character varying(30),
    preferred_language character varying(10) NOT NULL,
    profile_status character varying(50) NOT NULL,
    face_photo text,
    household_id integer,
    household_relationship character varying(100),
    household_role character varying(50) NOT NULL,
    assigned_tasks text NOT NULL,
    administrative_unit_id integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT check_valid_profile_status CHECK (((profile_status)::text = ANY ((ARRAY['pending_review'::character varying, 'active'::character varying, 'archived'::character varying])::text[])))
);


ALTER TABLE public.citizen_profiles OWNER TO postgres;

--
-- Name: citizen_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.citizen_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.citizen_profiles_id_seq OWNER TO postgres;

--
-- Name: citizen_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.citizen_profiles_id_seq OWNED BY public.citizen_profiles.id;


--
-- Name: education_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.education_records (
    id integer NOT NULL,
    citizen_id integer NOT NULL,
    highest_qualification character varying(150),
    institution_name character varying(255),
    specialization character varying(150),
    year_of_completion integer,
    literacy_status character varying(100),
    certificate_number character varying(100),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.education_records OWNER TO postgres;

--
-- Name: education_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.education_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.education_records_id_seq OWNER TO postgres;

--
-- Name: education_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.education_records_id_seq OWNED BY public.education_records.id;


--
-- Name: household_link_requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.household_link_requests (
    id integer NOT NULL,
    household_id integer NOT NULL,
    requester_citizen_id integer NOT NULL,
    target_citizen_id integer NOT NULL,
    relationship character varying(100) NOT NULL,
    household_role character varying(50) NOT NULL,
    assigned_tasks text NOT NULL,
    status character varying(50) NOT NULL,
    admin_notes text,
    reviewed_by_admin_id integer,
    reviewed_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.household_link_requests OWNER TO postgres;

--
-- Name: household_link_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.household_link_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.household_link_requests_id_seq OWNER TO postgres;

--
-- Name: household_link_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.household_link_requests_id_seq OWNED BY public.household_link_requests.id;


--
-- Name: household_memberships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.household_memberships (
    id integer NOT NULL,
    household_id integer NOT NULL,
    citizen_id integer NOT NULL,
    relationship_type character varying(100) NOT NULL,
    start_date date NOT NULL,
    end_date date,
    status character varying(50) NOT NULL,
    notes character varying(255),
    created_at timestamp with time zone NOT NULL,
    CONSTRAINT check_valid_membership_status CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'ended'::character varying])::text[])))
);


ALTER TABLE public.household_memberships OWNER TO postgres;

--
-- Name: household_memberships_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.household_memberships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.household_memberships_id_seq OWNER TO postgres;

--
-- Name: household_memberships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.household_memberships_id_seq OWNED BY public.household_memberships.id;


--
-- Name: households; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.households (
    id integer NOT NULL,
    household_code character varying(50) NOT NULL,
    address_line character varying(255) NOT NULL,
    locality character varying(100) NOT NULL,
    city character varying(100) NOT NULL,
    state character varying(100) NOT NULL,
    postal_code character varying(20) NOT NULL,
    administrative_notes text,
    administrative_unit_id integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.households OWNER TO postgres;

--
-- Name: households_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.households_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.households_id_seq OWNER TO postgres;

--
-- Name: households_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.households_id_seq OWNED BY public.households.id;


--
-- Name: land_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.land_records (
    id integer NOT NULL,
    household_id integer NOT NULL,
    survey_number character varying(100) NOT NULL,
    land_type character varying(100) NOT NULL,
    area_measurement character varying(100) NOT NULL,
    patta_passbook_number character varying(100),
    district_sub_registrar character varying(150),
    property_tax_status character varying(50),
    market_valuation_inr double precision,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.land_records OWNER TO postgres;

--
-- Name: land_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.land_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.land_records_id_seq OWNER TO postgres;

--
-- Name: land_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.land_records_id_seq OWNED BY public.land_records.id;


--
-- Name: medical_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.medical_records (
    id integer NOT NULL,
    citizen_id integer NOT NULL,
    blood_group character varying(10),
    chronic_conditions character varying(255),
    allergies character varying(255),
    vaccination_status character varying(100),
    disability_status character varying(100),
    abha_id character varying(50),
    emergency_hospital character varying(200),
    emergency_contact_name character varying(150),
    emergency_contact_phone character varying(30),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.medical_records OWNER TO postgres;

--
-- Name: medical_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.medical_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.medical_records_id_seq OWNER TO postgres;

--
-- Name: medical_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.medical_records_id_seq OWNED BY public.medical_records.id;


--
-- Name: otp_verifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.otp_verifications (
    id integer NOT NULL,
    reference_id character varying(50),
    user_id integer,
    recipient character varying(100) NOT NULL,
    otp_code character varying(10) NOT NULL,
    purpose character varying(50) NOT NULL,
    is_verified boolean NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone NOT NULL
);


ALTER TABLE public.otp_verifications OWNER TO postgres;

--
-- Name: otp_verifications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.otp_verifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.otp_verifications_id_seq OWNER TO postgres;

--
-- Name: otp_verifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.otp_verifications_id_seq OWNED BY public.otp_verifications.id;


--
-- Name: outbox_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.outbox_events (
    id integer NOT NULL,
    event_id character varying(50),
    event_type character varying(100) NOT NULL,
    aggregate_type character varying(50) NOT NULL,
    aggregate_id character varying(100) NOT NULL,
    payload_json text NOT NULL,
    created_at timestamp with time zone NOT NULL
);


ALTER TABLE public.outbox_events OWNER TO postgres;

--
-- Name: outbox_events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.outbox_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.outbox_events_id_seq OWNER TO postgres;

--
-- Name: outbox_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.outbox_events_id_seq OWNED BY public.outbox_events.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    phone_number character varying(30),
    password_hash character varying(255) NOT NULL,
    role character varying(50) NOT NULL,
    account_status character varying(50) NOT NULL,
    administrative_unit_id integer,
    biometric_credential_id character varying(255),
    biometric_public_key character varying(512),
    biometric_registered_at timestamp with time zone,
    face_data text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT check_valid_user_role CHECK (((role)::text = ANY ((ARRAY['citizen'::character varying, 'admin'::character varying])::text[]))),
    CONSTRAINT check_valid_user_status CHECK (((account_status)::text = ANY ((ARRAY['active'::character varying, 'suspended'::character varying, 'pending'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: administrative_units id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.administrative_units ALTER COLUMN id SET DEFAULT nextval('public.administrative_units_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: citizen_profiles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.citizen_profiles ALTER COLUMN id SET DEFAULT nextval('public.citizen_profiles_id_seq'::regclass);


--
-- Name: education_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.education_records ALTER COLUMN id SET DEFAULT nextval('public.education_records_id_seq'::regclass);


--
-- Name: household_link_requests id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.household_link_requests ALTER COLUMN id SET DEFAULT nextval('public.household_link_requests_id_seq'::regclass);


--
-- Name: household_memberships id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.household_memberships ALTER COLUMN id SET DEFAULT nextval('public.household_memberships_id_seq'::regclass);


--
-- Name: households id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.households ALTER COLUMN id SET DEFAULT nextval('public.households_id_seq'::regclass);


--
-- Name: land_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.land_records ALTER COLUMN id SET DEFAULT nextval('public.land_records_id_seq'::regclass);


--
-- Name: medical_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medical_records ALTER COLUMN id SET DEFAULT nextval('public.medical_records_id_seq'::regclass);


--
-- Name: otp_verifications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otp_verifications ALTER COLUMN id SET DEFAULT nextval('public.otp_verifications_id_seq'::regclass);


--
-- Name: outbox_events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.outbox_events ALTER COLUMN id SET DEFAULT nextval('public.outbox_events_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: administrative_units; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.administrative_units (id, identifier, name, unit_type, parent_id, status, created_at, updated_at) FROM stdin;
1	IN	India (National Republic)	country	\N	active	2026-11-16 07:03:31.575486+00	2026-11-16 07:03:31.575489+00
2	IN-KA	Karnataka	state	1	active	2026-11-16 07:03:31.57713+00	2026-11-16 07:03:31.577132+00
3	IN-MH	Maharashtra	state	1	active	2026-11-16 07:03:31.578122+00	2026-11-16 07:03:31.578123+00
4	IN-KA-BLR	Bengaluru Urban	district	2	active	2026-11-16 07:03:31.578853+00	2026-11-16 07:03:31.578854+00
5	IN-MH-MUM	Mumbai City	district	3	active	2026-11-16 07:03:31.579732+00	2026-11-16 07:03:31.579733+00
6	IN-KA-BLR-W150	Ward 150 - Bellandur	ward	4	active	2026-11-16 07:03:31.580639+00	2026-11-16 07:03:31.580642+00
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_logs (id, actor_id, actor_email, action, resource_type, resource_id, details, created_at) FROM stdin;
\.


--
-- Data for Name: citizen_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.citizen_profiles (id, user_id, citizen_code, full_name, date_of_birth, phone_number, preferred_language, profile_status, face_photo, household_id, household_relationship, household_role, assigned_tasks, administrative_unit_id, created_at, updated_at) FROM stdin;
1	3	CIT-88219011	Aarav Sharma	1991-05-14	+91 98765 43210	en	active	\N	1	Head of Household	MEMBER	[]	6	2026-11-16 07:03:31.709213+00	2026-11-16 07:03:31.709215+00
2	4	CIT-88219012	Priya Sharma	1993-08-22	+91 98765 43211	en	active	\N	1	Spouse	MEMBER	[]	6	2026-11-16 07:03:31.713371+00	2026-11-16 07:03:31.713374+00
3	5	CIT-77310045	Rohit Verma	1985-11-03	+91 91234 56789	hi	pending_review	\N	2	Head of Household	MEMBER	[]	4	2026-11-16 07:03:31.715403+00	2026-11-16 07:03:31.715404+00
4	6	CIT-66421190	Ananya Patil	1998-02-17	+91 99887 76655	mr	pending_review	\N	3	Member	MEMBER	[]	5	2026-11-16 07:03:31.717056+00	2026-11-16 07:03:31.717057+00
5	7	CIT-55109923	Kavita Deshmukh	1974-12-30	+91 97654 32109	en	active	\N	\N	\N	MEMBER	[]	5	2026-11-16 07:03:31.718579+00	2026-11-16 07:03:31.71858+00
\.


--
-- Data for Name: education_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.education_records (id, citizen_id, highest_qualification, institution_name, specialization, year_of_completion, literacy_status, certificate_number, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: household_link_requests; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.household_link_requests (id, household_id, requester_citizen_id, target_citizen_id, relationship, household_role, assigned_tasks, status, admin_notes, reviewed_by_admin_id, reviewed_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: household_memberships; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.household_memberships (id, household_id, citizen_id, relationship_type, start_date, end_date, status, notes, created_at) FROM stdin;
1	1	1	Head of Household	2025-01-01	\N	active	Initial census verification registration	2026-11-16 07:03:31.711324+00
2	1	2	Spouse	2025-01-01	\N	active	Initial census verification registration	2026-11-16 07:03:31.714622+00
3	2	3	Head of Household	2025-01-01	\N	active	Initial census verification registration	2026-11-16 07:03:31.71633+00
4	3	4	Member	2025-01-01	\N	active	Initial census verification registration	2026-11-16 07:03:31.717858+00
\.


--
-- Data for Name: households; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.households (id, household_code, address_line, locality, city, state, postal_code, administrative_notes, administrative_unit_id, created_at, updated_at) FROM stdin;
1	HHD-1001-BLR	Flat 402, Green Glen Residency, Outer Ring Road	Bellandur	Bengaluru	Karnataka	560103	Verified municipal address during 2026 census review.	6	2026-11-16 07:03:31.644692+00	2026-11-16 07:03:31.644695+00
2	HHD-1002-BLR	12/A, 3rd Cross, Indiranagar 1st Stage	Indiranagar	Bengaluru	Karnataka	560038	Pending updated water connection verification.	4	2026-11-16 07:03:31.645833+00	2026-11-16 07:03:31.645835+00
3	HHD-2001-MUM	B-201, Sunshine Heights, Swami Vivekananda Road	Bandra West	Mumbai	Maharashtra	400050	Legacy household profile from municipal records.	5	2026-11-16 07:03:31.64659+00	2026-11-16 07:03:31.646591+00
\.


--
-- Data for Name: land_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.land_records (id, household_id, survey_number, land_type, area_measurement, patta_passbook_number, district_sub_registrar, property_tax_status, market_valuation_inr, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: medical_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.medical_records (id, citizen_id, blood_group, chronic_conditions, allergies, vaccination_status, disability_status, abha_id, emergency_hospital, emergency_contact_name, emergency_contact_phone, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: otp_verifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.otp_verifications (id, reference_id, user_id, recipient, otp_code, purpose, is_verified, expires_at, created_at) FROM stdin;
\.


--
-- Data for Name: outbox_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.outbox_events (id, event_id, event_type, aggregate_type, aggregate_id, payload_json, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, phone_number, password_hash, role, account_status, administrative_unit_id, biometric_credential_id, biometric_public_key, biometric_registered_at, face_data, created_at, updated_at) FROM stdin;
1	admin@civicportal.gov	\N	$argon2id$v=19$m=65536,t=3,p=4$du7WCV4pTEiWBePAfhm8Zg$IWIwvUbarjxnggYLn2Gqt9ZgbMzYt9YMMDTGEi4DHzA	admin	active	\N	\N	\N	\N	\N	2026-11-16 07:03:21.079213+00	2026-11-16 07:03:21.079217+00
2	admin.bengaluru@nagriksetu.gov.in	\N	$argon2id$v=19$m=65536,t=3,p=4$AorvkA2TxZT1A0UC8V8k/w$rakOJ40o4l5hyLXUk+iPmqiRKH0l3OFnGXOorpi2On8	admin	active	4	\N	\N	\N	\N	2026-11-16 07:03:31.641498+00	2026-11-16 07:03:31.641501+00
3	aarav.sharma@example.com	\N	$argon2id$v=19$m=65536,t=3,p=4$un7pRMGEqCXce7gcHjCLGA$/WpXMVzcLemPs9vDGIth0+5aDXFh4V+pfB8yrY2dQHY	citizen	active	6	\N	\N	\N	\N	2026-11-16 07:03:31.707776+00	2026-11-16 07:03:31.70778+00
4	priya.sharma@example.com	\N	$argon2id$v=19$m=65536,t=3,p=4$un7pRMGEqCXce7gcHjCLGA$/WpXMVzcLemPs9vDGIth0+5aDXFh4V+pfB8yrY2dQHY	citizen	active	6	\N	\N	\N	\N	2026-11-16 07:03:31.71259+00	2026-11-16 07:03:31.712593+00
5	rohit.verma@example.com	\N	$argon2id$v=19$m=65536,t=3,p=4$un7pRMGEqCXce7gcHjCLGA$/WpXMVzcLemPs9vDGIth0+5aDXFh4V+pfB8yrY2dQHY	citizen	active	4	\N	\N	\N	\N	2026-11-16 07:03:31.714996+00	2026-11-16 07:03:31.714997+00
6	ananya.patil@example.com	\N	$argon2id$v=19$m=65536,t=3,p=4$un7pRMGEqCXce7gcHjCLGA$/WpXMVzcLemPs9vDGIth0+5aDXFh4V+pfB8yrY2dQHY	citizen	active	5	\N	\N	\N	\N	2026-11-16 07:03:31.716654+00	2026-11-16 07:03:31.716655+00
7	kavita.deshmukh@example.com	\N	$argon2id$v=19$m=65536,t=3,p=4$un7pRMGEqCXce7gcHjCLGA$/WpXMVzcLemPs9vDGIth0+5aDXFh4V+pfB8yrY2dQHY	citizen	active	5	\N	\N	\N	\N	2026-11-16 07:03:31.718175+00	2026-11-16 07:03:31.718176+00
\.


--
-- Name: administrative_units_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.administrative_units_id_seq', 6, true);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 1, false);


--
-- Name: citizen_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.citizen_profiles_id_seq', 5, true);


--
-- Name: education_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.education_records_id_seq', 1, false);


--
-- Name: household_link_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.household_link_requests_id_seq', 1, false);


--
-- Name: household_memberships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.household_memberships_id_seq', 4, true);


--
-- Name: households_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.households_id_seq', 3, true);


--
-- Name: land_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.land_records_id_seq', 1, false);


--
-- Name: medical_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.medical_records_id_seq', 1, false);


--
-- Name: otp_verifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.otp_verifications_id_seq', 1, false);


--
-- Name: outbox_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.outbox_events_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 7, true);


--
-- Name: administrative_units administrative_units_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.administrative_units
    ADD CONSTRAINT administrative_units_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: citizen_profiles citizen_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.citizen_profiles
    ADD CONSTRAINT citizen_profiles_pkey PRIMARY KEY (id);


--
-- Name: education_records education_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.education_records
    ADD CONSTRAINT education_records_pkey PRIMARY KEY (id);


--
-- Name: household_link_requests household_link_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.household_link_requests
    ADD CONSTRAINT household_link_requests_pkey PRIMARY KEY (id);


--
-- Name: household_memberships household_memberships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.household_memberships
    ADD CONSTRAINT household_memberships_pkey PRIMARY KEY (id);


--
-- Name: households households_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.households
    ADD CONSTRAINT households_pkey PRIMARY KEY (id);


--
-- Name: land_records land_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.land_records
    ADD CONSTRAINT land_records_pkey PRIMARY KEY (id);


--
-- Name: medical_records medical_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medical_records
    ADD CONSTRAINT medical_records_pkey PRIMARY KEY (id);


--
-- Name: otp_verifications otp_verifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otp_verifications
    ADD CONSTRAINT otp_verifications_pkey PRIMARY KEY (id);


--
-- Name: outbox_events outbox_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.outbox_events
    ADD CONSTRAINT outbox_events_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_administrative_units_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_administrative_units_id ON public.administrative_units USING btree (id);


--
-- Name: ix_administrative_units_identifier; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_administrative_units_identifier ON public.administrative_units USING btree (identifier);


--
-- Name: ix_administrative_units_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_administrative_units_name ON public.administrative_units USING btree (name);


--
-- Name: ix_administrative_units_parent_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_administrative_units_parent_id ON public.administrative_units USING btree (parent_id);


--
-- Name: ix_administrative_units_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_administrative_units_status ON public.administrative_units USING btree (status);


--
-- Name: ix_administrative_units_unit_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_administrative_units_unit_type ON public.administrative_units USING btree (unit_type);


--
-- Name: ix_audit_logs_action; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_action ON public.audit_logs USING btree (action);


--
-- Name: ix_audit_logs_actor_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_actor_id ON public.audit_logs USING btree (actor_id);


--
-- Name: ix_audit_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- Name: ix_audit_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_id ON public.audit_logs USING btree (id);


--
-- Name: ix_audit_logs_resource_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_resource_type ON public.audit_logs USING btree (resource_type);


--
-- Name: ix_citizen_profiles_administrative_unit_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_citizen_profiles_administrative_unit_id ON public.citizen_profiles USING btree (administrative_unit_id);


--
-- Name: ix_citizen_profiles_citizen_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_citizen_profiles_citizen_code ON public.citizen_profiles USING btree (citizen_code);


--
-- Name: ix_citizen_profiles_household_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_citizen_profiles_household_id ON public.citizen_profiles USING btree (household_id);


--
-- Name: ix_citizen_profiles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_citizen_profiles_id ON public.citizen_profiles USING btree (id);


--
-- Name: ix_citizen_profiles_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_citizen_profiles_user_id ON public.citizen_profiles USING btree (user_id);


--
-- Name: ix_education_records_citizen_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_education_records_citizen_id ON public.education_records USING btree (citizen_id);


--
-- Name: ix_education_records_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_education_records_id ON public.education_records USING btree (id);


--
-- Name: ix_household_link_requests_household_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_household_link_requests_household_id ON public.household_link_requests USING btree (household_id);


--
-- Name: ix_household_link_requests_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_household_link_requests_id ON public.household_link_requests USING btree (id);


--
-- Name: ix_household_link_requests_requester_citizen_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_household_link_requests_requester_citizen_id ON public.household_link_requests USING btree (requester_citizen_id);


--
-- Name: ix_household_link_requests_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_household_link_requests_status ON public.household_link_requests USING btree (status);


--
-- Name: ix_household_link_requests_target_citizen_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_household_link_requests_target_citizen_id ON public.household_link_requests USING btree (target_citizen_id);


--
-- Name: ix_household_memberships_citizen_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_household_memberships_citizen_id ON public.household_memberships USING btree (citizen_id);


--
-- Name: ix_household_memberships_household_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_household_memberships_household_id ON public.household_memberships USING btree (household_id);


--
-- Name: ix_household_memberships_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_household_memberships_id ON public.household_memberships USING btree (id);


--
-- Name: ix_households_administrative_unit_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_households_administrative_unit_id ON public.households USING btree (administrative_unit_id);


--
-- Name: ix_households_household_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_households_household_code ON public.households USING btree (household_code);


--
-- Name: ix_households_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_households_id ON public.households USING btree (id);


--
-- Name: ix_land_records_household_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_land_records_household_id ON public.land_records USING btree (household_id);


--
-- Name: ix_land_records_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_land_records_id ON public.land_records USING btree (id);


--
-- Name: ix_medical_records_citizen_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_medical_records_citizen_id ON public.medical_records USING btree (citizen_id);


--
-- Name: ix_medical_records_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_medical_records_id ON public.medical_records USING btree (id);


--
-- Name: ix_otp_verifications_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_otp_verifications_id ON public.otp_verifications USING btree (id);


--
-- Name: ix_otp_verifications_reference_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_otp_verifications_reference_id ON public.otp_verifications USING btree (reference_id);


--
-- Name: ix_outbox_events_aggregate_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_outbox_events_aggregate_id ON public.outbox_events USING btree (aggregate_id);


--
-- Name: ix_outbox_events_aggregate_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_outbox_events_aggregate_type ON public.outbox_events USING btree (aggregate_type);


--
-- Name: ix_outbox_events_event_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_outbox_events_event_id ON public.outbox_events USING btree (event_id);


--
-- Name: ix_outbox_events_event_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_outbox_events_event_type ON public.outbox_events USING btree (event_type);


--
-- Name: ix_outbox_events_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_outbox_events_id ON public.outbox_events USING btree (id);


--
-- Name: ix_users_administrative_unit_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_administrative_unit_id ON public.users USING btree (administrative_unit_id);


--
-- Name: ix_users_biometric_credential_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_biometric_credential_id ON public.users USING btree (biometric_credential_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_phone_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_phone_number ON public.users USING btree (phone_number);


--
-- Name: administrative_units administrative_units_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.administrative_units
    ADD CONSTRAINT administrative_units_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.administrative_units(id) ON DELETE RESTRICT;


--
-- Name: audit_logs audit_logs_actor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: citizen_profiles citizen_profiles_administrative_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.citizen_profiles
    ADD CONSTRAINT citizen_profiles_administrative_unit_id_fkey FOREIGN KEY (administrative_unit_id) REFERENCES public.administrative_units(id) ON DELETE SET NULL;


--
-- Name: citizen_profiles citizen_profiles_household_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.citizen_profiles
    ADD CONSTRAINT citizen_profiles_household_id_fkey FOREIGN KEY (household_id) REFERENCES public.households(id) ON DELETE SET NULL;


--
-- Name: citizen_profiles citizen_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.citizen_profiles
    ADD CONSTRAINT citizen_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: education_records education_records_citizen_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.education_records
    ADD CONSTRAINT education_records_citizen_id_fkey FOREIGN KEY (citizen_id) REFERENCES public.citizen_profiles(id) ON DELETE CASCADE;


--
-- Name: household_link_requests household_link_requests_household_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.household_link_requests
    ADD CONSTRAINT household_link_requests_household_id_fkey FOREIGN KEY (household_id) REFERENCES public.households(id) ON DELETE CASCADE;


--
-- Name: household_link_requests household_link_requests_requester_citizen_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.household_link_requests
    ADD CONSTRAINT household_link_requests_requester_citizen_id_fkey FOREIGN KEY (requester_citizen_id) REFERENCES public.citizen_profiles(id) ON DELETE CASCADE;


--
-- Name: household_link_requests household_link_requests_reviewed_by_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.household_link_requests
    ADD CONSTRAINT household_link_requests_reviewed_by_admin_id_fkey FOREIGN KEY (reviewed_by_admin_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: household_link_requests household_link_requests_target_citizen_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.household_link_requests
    ADD CONSTRAINT household_link_requests_target_citizen_id_fkey FOREIGN KEY (target_citizen_id) REFERENCES public.citizen_profiles(id) ON DELETE CASCADE;


--
-- Name: household_memberships household_memberships_citizen_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.household_memberships
    ADD CONSTRAINT household_memberships_citizen_id_fkey FOREIGN KEY (citizen_id) REFERENCES public.citizen_profiles(id) ON DELETE CASCADE;


--
-- Name: household_memberships household_memberships_household_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.household_memberships
    ADD CONSTRAINT household_memberships_household_id_fkey FOREIGN KEY (household_id) REFERENCES public.households(id) ON DELETE CASCADE;


--
-- Name: households households_administrative_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.households
    ADD CONSTRAINT households_administrative_unit_id_fkey FOREIGN KEY (administrative_unit_id) REFERENCES public.administrative_units(id) ON DELETE SET NULL;


--
-- Name: land_records land_records_household_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.land_records
    ADD CONSTRAINT land_records_household_id_fkey FOREIGN KEY (household_id) REFERENCES public.households(id) ON DELETE CASCADE;


--
-- Name: medical_records medical_records_citizen_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medical_records
    ADD CONSTRAINT medical_records_citizen_id_fkey FOREIGN KEY (citizen_id) REFERENCES public.citizen_profiles(id) ON DELETE CASCADE;


--
-- Name: otp_verifications otp_verifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otp_verifications
    ADD CONSTRAINT otp_verifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: users users_administrative_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_administrative_unit_id_fkey FOREIGN KEY (administrative_unit_id) REFERENCES public.administrative_units(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict X0iMGC9ZMhEjt3ZnPPP1q6zpKfTexqruJeoqcRFJzShFfOrbYpKzFyfwc4rft2e

