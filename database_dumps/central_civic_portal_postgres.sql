--
-- PostgreSQL database dump
--

\restrict STfMA975Xr2weFQAP9jj8CVfJzWVbEgcfC2S4jFtTebUP38uWv0zX03gNa6Shgl

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
    created_at timestamp with time zone NOT NULL,
    log_code character varying(50)
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
    updated_at timestamp with time zone NOT NULL,
    student_id character varying(50),
    permanent_student_id character varying(100),
    record_code character varying(50)
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
    updated_at timestamp with time zone NOT NULL,
    request_code character varying(50)
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
    membership_code character varying(50),
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
    updated_at timestamp with time zone NOT NULL,
    record_code character varying(50)
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
    updated_at timestamp with time zone NOT NULL,
    record_code character varying(50)
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
    user_code character varying(50),
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

INSERT INTO public.administrative_units VALUES (2026104001, 'IN', 'India (National Republic)', 'country', NULL, 'active', '2026-11-16 07:03:31.575486+00', '2026-11-16 07:03:31.575489+00');
INSERT INTO public.administrative_units VALUES (2026104002, 'IN-KA', 'Karnataka', 'state', 2026104001, 'active', '2026-11-16 07:03:31.57713+00', '2026-11-16 07:03:31.577132+00');
INSERT INTO public.administrative_units VALUES (2026104003, 'IN-MH', 'Maharashtra', 'state', 2026104001, 'active', '2026-11-16 07:03:31.578122+00', '2026-11-16 07:03:31.578123+00');
INSERT INTO public.administrative_units VALUES (2026104004, 'IN-KA-BLR', 'Bengaluru Urban', 'district', 2026104002, 'active', '2026-11-16 07:03:31.578853+00', '2026-11-16 07:03:31.578854+00');
INSERT INTO public.administrative_units VALUES (2026104005, 'IN-MH-MUM', 'Mumbai City', 'district', 2026104003, 'active', '2026-11-16 07:03:31.579732+00', '2026-11-16 07:03:31.579733+00');
INSERT INTO public.administrative_units VALUES (2026104006, 'IN-KA-BLR-W150', 'Ward 150 - Bellandur', 'ward', 2026104004, 'active', '2026-11-16 07:03:31.580639+00', '2026-11-16 07:03:31.580642+00');


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.audit_logs VALUES (2026108001, 2026101010, '2023vidyasagar.l@vidyashilp.edu.in', 'CITIZEN_SELF_UPDATE_OTP_VERIFIED', 'citizen', 'CIT-2026-9267D8AF', '{"changes": {"date_of_birth": {"old": "None", "new": "2008-08-07"}}, "otp_ref": "REF-F3E9F82E85"}', '2026-11-21 07:16:14.273002+00', 'AUD-2026-5C0D5110');
INSERT INTO public.audit_logs VALUES (2026108002, 2026101001, 'admin@civicportal.gov', 'CITIZEN_UPDATE', 'citizen', 'CIT-2026-9267D8AF', '{"profile_status": {"old": "pending_review", "new": "active"}, "household_id": {"old": "None", "new": "3"}, "household_relationship": {"old": "None", "new": "Son"}, "administrative_unit_id": {"old": "None", "new": "2"}}', '2026-11-21 07:17:10.672749+00', 'AUD-2026-86C38946');
INSERT INTO public.audit_logs VALUES (2026108003, 2026101010, '2023vidyasagar.l@vidyashilp.edu.in', 'BIOMETRIC_2FA_OTP_CHALLENGE_ISSUED', 'auth', '10', '{"biometric_type": "fingerprint", "recipient": "779****385"}', '2026-11-21 07:17:57.477407+00', 'AUD-2026-6F67B0E4');
INSERT INTO public.audit_logs VALUES (2026108004, 2026101010, '2023vidyasagar.l@vidyashilp.edu.in', 'LOGIN_OTP_SUCCESS', 'auth', '10', '{"identifier": "2023vidyasagar.l@vidyashilp.edu.in", "reference_id": "REF-667EE30FEA"}', '2026-11-21 07:17:59.924739+00', 'AUD-2026-8D30675F');


--
-- Data for Name: citizen_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.citizen_profiles VALUES (2026102009, NULL, 'CIT-2026102009', 'Test Citizen Registration', NULL, '9876543210', 'en', 'pending_review', NULL, NULL, NULL, 'MEMBER', '[]', NULL, '2026-11-20 20:03:14.266021+00', '2026-11-20 20:03:14.266025+00');
INSERT INTO public.citizen_profiles VALUES (2026102007, NULL, 'CIT-2026102007', 'Asha Sharma', '2018-05-10', '+91 98765 43210', 'en', 'active', NULL, 2026103001, 'Daughter', 'MEMBER', '[]', 2026104006, '2026-11-20 19:04:09.892007+00', '2026-11-20 19:04:09.892011+00');
INSERT INTO public.citizen_profiles VALUES (2026102008, 2026101008, 'CIT-2026102008', 'Suresh Varma', NULL, '+91 98111 22233', 'en', 'pending_review', NULL, NULL, NULL, 'MEMBER', '[]', NULL, '2026-11-20 19:16:59.014061+00', '2026-11-20 19:16:59.014064+00');
INSERT INTO public.citizen_profiles VALUES (2026102005, 2026101007, 'CIT-2026102005', 'Kavita Deshmukh', '1974-12-30', '+91 97654 32109', 'en', 'active', NULL, NULL, NULL, 'MEMBER', '[]', 2026104005, '2026-11-16 07:03:31.718579+00', '2026-11-16 07:03:31.71858+00');
INSERT INTO public.citizen_profiles VALUES (2026102001, 2026101003, 'CIT-2026102001', 'Aarav Sharma', '1991-05-14', '+91 98765 43210', 'en', 'active', NULL, 2026103001, 'Head of Household', 'MEMBER', '[]', 2026104006, '2026-11-16 07:03:31.709213+00', '2026-11-16 07:03:31.709215+00');
INSERT INTO public.citizen_profiles VALUES (2026102002, 2026101004, 'CIT-2026102002', 'Priya Sharma', '1993-08-22', '+91 98765 43211', 'en', 'active', NULL, 2026103001, 'Spouse', 'MEMBER', '[]', 2026104006, '2026-11-16 07:03:31.713371+00', '2026-11-16 07:03:31.713374+00');
INSERT INTO public.citizen_profiles VALUES (2026102003, 2026101005, 'CIT-2026102003', 'Rohit Verma', '1985-11-03', '+91 91234 56789', 'hi', 'pending_review', NULL, 2026103002, 'Head of Household', 'MEMBER', '[]', 2026104004, '2026-11-16 07:03:31.715403+00', '2026-11-16 07:03:31.715404+00');
INSERT INTO public.citizen_profiles VALUES (2026102004, 2026101006, 'CIT-2026102004', 'Ananya Patil', '1998-02-17', '+91 99887 76655', 'mr', 'pending_review', NULL, 2026103003, 'Member', 'MEMBER', '[]', 2026104005, '2026-11-16 07:03:31.717056+00', '2026-11-16 07:03:31.717057+00');
INSERT INTO public.citizen_profiles VALUES (2026102010, 2026101010, 'CIT-2026102010', 'VIDYASAGAR L', '2008-08-07', '7795163385', 'en', 'active', 'data:image/jpeg;base64,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', 2026103003, 'Son', 'MEMBER', '[]', 2026104002, '2026-11-21 07:14:16.02967+00', '2026-11-21 07:17:10.673685+00');


--
-- Data for Name: education_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.education_records VALUES (2026107001, 2026102007, 'Primary (Grade 1)', 'Government Model School, Bengaluru', NULL, NULL, 'Literate', NULL, '2026-11-20 19:04:09.896819+00', '2026-11-20 19:04:09.896822+00', 'SCH01125', 'NS-FB8336A812DE468FB8E475443CF673EB', 'EDU-2026-000001');
INSERT INTO public.education_records VALUES (2026107002, 2026102008, 'Secondary (10th)', NULL, NULL, NULL, 'Literate', NULL, '2026-11-20 19:16:59.015416+00', '2026-11-20 19:16:59.015418+00', NULL, NULL, 'EDU-2026-9B38C6');
INSERT INTO public.education_records VALUES (2026107003, 2026102009, 'Secondary (10th)', NULL, NULL, NULL, 'Literate', NULL, '2026-11-20 20:03:14.267074+00', '2026-11-20 20:03:14.267076+00', NULL, NULL, 'EDU-2026-EBA7CB');
INSERT INTO public.education_records VALUES (2026107004, 2026102010, 'Secondary (10th)', NULL, NULL, NULL, 'Literate', NULL, '2026-11-21 07:14:16.038173+00', '2026-11-21 07:14:16.038177+00', NULL, NULL, 'EDU-2026-443A1A');


--
-- Data for Name: household_link_requests; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: household_memberships; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.household_memberships VALUES (2026111001, 2026103001, 2026102001, 'Head of Household', '2025-01-01', NULL, 'active', 'Initial census verification registration', '2026-11-16 07:03:31.711324+00', 'HMB-2026-000001');
INSERT INTO public.household_memberships VALUES (2026111002, 2026103001, 2026102002, 'Spouse', '2025-01-01', NULL, 'active', 'Initial census verification registration', '2026-11-16 07:03:31.714622+00', 'HMB-2026-000002');
INSERT INTO public.household_memberships VALUES (2026111003, 2026103002, 2026102003, 'Head of Household', '2025-01-01', NULL, 'active', 'Initial census verification registration', '2026-11-16 07:03:31.71633+00', 'HMB-2026-000003');
INSERT INTO public.household_memberships VALUES (2026111004, 2026103003, 2026102004, 'Member', '2025-01-01', NULL, 'active', 'Initial census verification registration', '2026-11-16 07:03:31.717858+00', 'HMB-2026-000004');
INSERT INTO public.household_memberships VALUES (2026111005, 2026103001, 2026102007, 'Daughter', '2018-05-10', NULL, 'active', 'Registered child dependent of Aarav & Priya Sharma', '2026-11-20 19:04:09.895073+00', 'HMB-2026-000003');


--
-- Data for Name: households; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.households VALUES (2026103001, 'HHD-2026103001', 'Flat 402, Green Glen Residency, Outer Ring Road', 'Bellandur', 'Bengaluru', 'Karnataka', '560103', 'Verified municipal address during 2026 census review.', 2026104006, '2026-11-16 07:03:31.644692+00', '2026-11-16 07:03:31.644695+00');
INSERT INTO public.households VALUES (2026103002, 'HHD-2026103002', '12/A, 3rd Cross, Indiranagar 1st Stage', 'Indiranagar', 'Bengaluru', 'Karnataka', '560038', 'Pending updated water connection verification.', 2026104004, '2026-11-16 07:03:31.645833+00', '2026-11-16 07:03:31.645835+00');
INSERT INTO public.households VALUES (2026103003, 'HHD-2026103003', 'B-201, Sunshine Heights, Swami Vivekananda Road', 'Bandra West', 'Mumbai', 'Maharashtra', '400050', 'Legacy household profile from municipal records.', 2026104005, '2026-11-16 07:03:31.64659+00', '2026-11-16 07:03:31.646591+00');


--
-- Data for Name: land_records; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: medical_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.medical_records VALUES (2026106001, 2026102007, 'O+', 'None', 'None', 'Fully Vaccinated (Universal Immunization Programme)', 'None', NULL, NULL, NULL, NULL, '2026-11-20 19:04:09.898145+00', '2026-11-20 19:04:09.898146+00', 'MED-2026-000001');
INSERT INTO public.medical_records VALUES (2026106002, 2026102008, 'Unknown', 'None Reported', 'None', 'Up to date', 'None', NULL, NULL, NULL, NULL, '2026-11-20 19:16:59.017555+00', '2026-11-20 19:16:59.017558+00', 'MED-2026-C1C2C5');
INSERT INTO public.medical_records VALUES (2026106003, 2026102009, 'Unknown', 'None Reported', 'None', 'Up to date', 'None', NULL, NULL, NULL, NULL, '2026-11-20 20:03:14.267555+00', '2026-11-20 20:03:14.267556+00', 'MED-2026-E5F4D5');
INSERT INTO public.medical_records VALUES (2026106004, 2026102010, 'Unknown', 'None Reported', 'None', 'Up to date', 'None', NULL, NULL, NULL, NULL, '2026-11-21 07:14:16.039128+00', '2026-11-21 07:14:16.039129+00', 'MED-2026-D3AE78');


--
-- Data for Name: otp_verifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.otp_verifications VALUES (2026109001, 'REF-F3E9F82E85', NULL, '7795163385', '239046', 'CITIZEN_PROFILE_UPDATE', false, '2026-11-21 07:21:09.878702+00', '2026-11-21 07:16:09.893398+00');
INSERT INTO public.otp_verifications VALUES (2026109002, 'REF-FAE3A61E26', NULL, '7795163385', '791296', 'CITIZEN_PROFILE_UPDATE', true, '2026-11-21 07:21:20.661979+00', '2026-11-21 07:16:20.663413+00');
INSERT INTO public.otp_verifications VALUES (2026109003, 'REF-667EE30FEA', 2026101010, '7795163385', '447651', 'BIOMETRIC_LOGIN_2FA', true, '2026-11-21 07:22:57.471233+00', '2026-11-21 07:17:57.471689+00');


--
-- Data for Name: outbox_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.outbox_events VALUES (2026110001, 'EVT-3A934329C402', 'CITIZEN_PROFILE_UPDATED', 'citizen', 'CIT-2026-9267D8AF', '{"citizen_code": "CIT-2026-9267D8AF", "changes": {"date_of_birth": {"old": "None", "new": "2008-08-07"}}}', '2026-11-21 07:16:14.285918+00');
INSERT INTO public.outbox_events VALUES (2026110002, 'EVT-A0FE5322EC57', 'CITIZEN_PROFILE_UPDATED', 'citizen', 'CIT-2026-9267D8AF', '{"citizen_code": "CIT-2026-9267D8AF", "changes": {"profile_status": {"old": "pending_review", "new": "active"}, "household_id": {"old": "None", "new": "3"}, "household_relationship": {"old": "None", "new": "Son"}, "administrative_unit_id": {"old": "None", "new": "2"}}}', '2026-11-21 07:17:10.679357+00');


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.users VALUES (2026101001, 'admin@civicportal.gov', NULL, '$argon2id$v=19$m=65536,t=3,p=4$du7WCV4pTEiWBePAfhm8Zg$IWIwvUbarjxnggYLn2Gqt9ZgbMzYt9YMMDTGEi4DHzA', 'admin', 'active', NULL, NULL, NULL, NULL, NULL, '2026-11-16 07:03:21.079213+00', '2026-11-16 07:03:21.079217+00', 'USR-2026101001');
INSERT INTO public.users VALUES (2026101008, 'citizen.aaf16c@nagriksetu.in', '+91 98111 22233', '$argon2id$v=19$m=65536,t=3,p=4$8YFHRcG7NQexanBEsBtjTw$fRWjclxiX2GHKOoD3q1s5OFquvlTdlfZCsuwG1cIzUU', 'citizen', 'active', NULL, NULL, NULL, NULL, NULL, '2026-11-20 19:16:59.008745+00', '2026-11-20 19:16:59.008748+00', 'USR-2026101008');
INSERT INTO public.users VALUES (2026101010, '2023vidyasagar.l@vidyashilp.edu.in', '7795163385', '$argon2id$v=19$m=65536,t=3,p=4$ooIMfu/6o3mK+CZck7Gbuw$2iTUwNTe0J1v9WhB2jEXg8nbgBM3V+ApJo/RG+DuN1k', 'citizen', 'active', NULL, 'NtwhdUWXeBgDMrC2N3o8RA', NULL, '2026-11-21 07:14:16.00079+00', 'data:image/jpeg;base64,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', '2026-11-21 07:14:16.007863+00', '2026-11-21 07:14:16.007867+00', 'USR-2026101010');
INSERT INTO public.users VALUES (2026101002, 'admin.bengaluru@nagriksetu.gov.in', NULL, '$argon2id$v=19$m=65536,t=3,p=4$AorvkA2TxZT1A0UC8V8k/w$rakOJ40o4l5hyLXUk+iPmqiRKH0l3OFnGXOorpi2On8', 'admin', 'active', 2026104004, NULL, NULL, NULL, NULL, '2026-11-16 07:03:31.641498+00', '2026-11-16 07:03:31.641501+00', 'USR-2026101002');
INSERT INTO public.users VALUES (2026101003, 'aarav.sharma@example.com', NULL, '$argon2id$v=19$m=65536,t=3,p=4$un7pRMGEqCXce7gcHjCLGA$/WpXMVzcLemPs9vDGIth0+5aDXFh4V+pfB8yrY2dQHY', 'citizen', 'active', 2026104006, NULL, NULL, NULL, NULL, '2026-11-16 07:03:31.707776+00', '2026-11-16 07:03:31.70778+00', 'USR-2026101003');
INSERT INTO public.users VALUES (2026101004, 'priya.sharma@example.com', NULL, '$argon2id$v=19$m=65536,t=3,p=4$un7pRMGEqCXce7gcHjCLGA$/WpXMVzcLemPs9vDGIth0+5aDXFh4V+pfB8yrY2dQHY', 'citizen', 'active', 2026104006, NULL, NULL, NULL, NULL, '2026-11-16 07:03:31.71259+00', '2026-11-16 07:03:31.712593+00', 'USR-2026101004');
INSERT INTO public.users VALUES (2026101005, 'rohit.verma@example.com', NULL, '$argon2id$v=19$m=65536,t=3,p=4$un7pRMGEqCXce7gcHjCLGA$/WpXMVzcLemPs9vDGIth0+5aDXFh4V+pfB8yrY2dQHY', 'citizen', 'active', 2026104004, NULL, NULL, NULL, NULL, '2026-11-16 07:03:31.714996+00', '2026-11-16 07:03:31.714997+00', 'USR-2026101005');
INSERT INTO public.users VALUES (2026101006, 'ananya.patil@example.com', NULL, '$argon2id$v=19$m=65536,t=3,p=4$un7pRMGEqCXce7gcHjCLGA$/WpXMVzcLemPs9vDGIth0+5aDXFh4V+pfB8yrY2dQHY', 'citizen', 'active', 2026104005, NULL, NULL, NULL, NULL, '2026-11-16 07:03:31.716654+00', '2026-11-16 07:03:31.716655+00', 'USR-2026101006');
INSERT INTO public.users VALUES (2026101007, 'kavita.deshmukh@example.com', NULL, '$argon2id$v=19$m=65536,t=3,p=4$un7pRMGEqCXce7gcHjCLGA$/WpXMVzcLemPs9vDGIth0+5aDXFh4V+pfB8yrY2dQHY', 'citizen', 'active', 2026104005, NULL, NULL, NULL, NULL, '2026-11-16 07:03:31.718175+00', '2026-11-16 07:03:31.718176+00', 'USR-2026101007');


--
-- Name: administrative_units_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.administrative_units_id_seq', 2026104007, true);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 2026108005, true);


--
-- Name: citizen_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.citizen_profiles_id_seq', 2026102011, true);


--
-- Name: education_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.education_records_id_seq', 2026107005, true);


--
-- Name: household_link_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.household_link_requests_id_seq', 2026112001, true);


--
-- Name: household_memberships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.household_memberships_id_seq', 2026111006, true);


--
-- Name: households_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.households_id_seq', 2026103004, true);


--
-- Name: land_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.land_records_id_seq', 1, false);


--
-- Name: medical_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.medical_records_id_seq', 2026106005, true);


--
-- Name: otp_verifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.otp_verifications_id_seq', 2026109004, true);


--
-- Name: outbox_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.outbox_events_id_seq', 2026110003, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 2026101011, true);


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
-- Name: idx_audit_logs_log_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_audit_logs_log_code ON public.audit_logs USING btree (log_code);


--
-- Name: idx_users_user_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_users_user_code ON public.users USING btree (user_code);


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
    ADD CONSTRAINT administrative_units_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.administrative_units(id) ON DELETE CASCADE;


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

\unrestrict STfMA975Xr2weFQAP9jj8CVfJzWVbEgcfC2S4jFtTebUP38uWv0zX03gNa6Shgl

