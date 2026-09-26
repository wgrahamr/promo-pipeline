--
-- PostgreSQL database dump
--

\restrict Gs0FnZRh0DDct2X579shUouoIdIUOHynLFOD63eihuJq3jhGWvHke7direkAh2E

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
-- Name: categorias; Type: TABLE; Schema: public; Owner: waha
--

CREATE TABLE public.categorias (
    id smallint NOT NULL,
    nome text NOT NULL
);


ALTER TABLE public.categorias OWNER TO waha;

--
-- Name: categorias_id_seq; Type: SEQUENCE; Schema: public; Owner: waha
--

CREATE SEQUENCE public.categorias_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categorias_id_seq OWNER TO waha;

--
-- Name: categorias_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: waha
--

ALTER SEQUENCE public.categorias_id_seq OWNED BY public.categorias.id;


--
-- Name: grupos_monitorados; Type: TABLE; Schema: public; Owner: waha
--

CREATE TABLE public.grupos_monitorados (
    id smallint NOT NULL,
    chat_id text NOT NULL,
    nome text,
    ativo boolean DEFAULT true NOT NULL
);


ALTER TABLE public.grupos_monitorados OWNER TO waha;

--
-- Name: grupos_monitorados_id_seq; Type: SEQUENCE; Schema: public; Owner: waha
--

CREATE SEQUENCE public.grupos_monitorados_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.grupos_monitorados_id_seq OWNER TO waha;

--
-- Name: grupos_monitorados_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: waha
--

ALTER SEQUENCE public.grupos_monitorados_id_seq OWNED BY public.grupos_monitorados.id;


--
-- Name: mensagens_cruas; Type: TABLE; Schema: public; Owner: waha
--

CREATE TABLE public.mensagens_cruas (
    id bigint NOT NULL,
    wa_message_id text NOT NULL,
    payload jsonb NOT NULL,
    recebida_em timestamp with time zone DEFAULT now() NOT NULL,
    processada boolean DEFAULT false NOT NULL,
    chat_id text NOT NULL
);


ALTER TABLE public.mensagens_cruas OWNER TO waha;

--
-- Name: mensagens_cruas_id_seq; Type: SEQUENCE; Schema: public; Owner: waha
--

CREATE SEQUENCE public.mensagens_cruas_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mensagens_cruas_id_seq OWNER TO waha;

--
-- Name: mensagens_cruas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: waha
--

ALTER SEQUENCE public.mensagens_cruas_id_seq OWNED BY public.mensagens_cruas.id;


--
-- Name: promocoes; Type: TABLE; Schema: public; Owner: waha
--

CREATE TABLE public.promocoes (
    id bigint NOT NULL,
    mensagem_id bigint,
    nome_item text NOT NULL,
    preco_cheio numeric(10,2),
    preco_desconto numeric(10,2) NOT NULL,
    cupom text,
    deadline timestamp with time zone,
    url text NOT NULL,
    loja text,
    criada_em timestamp with time zone DEFAULT now() NOT NULL,
    atualizada_em timestamp with time zone DEFAULT now() NOT NULL,
    categoria_id smallint,
    meio_pagamento text
);


ALTER TABLE public.promocoes OWNER TO waha;

--
-- Name: promocoes_id_seq; Type: SEQUENCE; Schema: public; Owner: waha
--

CREATE SEQUENCE public.promocoes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.promocoes_id_seq OWNER TO waha;

--
-- Name: promocoes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: waha
--

ALTER SEQUENCE public.promocoes_id_seq OWNED BY public.promocoes.id;


--
-- Name: categorias id; Type: DEFAULT; Schema: public; Owner: waha
--

ALTER TABLE ONLY public.categorias ALTER COLUMN id SET DEFAULT nextval('public.categorias_id_seq'::regclass);


--
-- Name: grupos_monitorados id; Type: DEFAULT; Schema: public; Owner: waha
--

ALTER TABLE ONLY public.grupos_monitorados ALTER COLUMN id SET DEFAULT nextval('public.grupos_monitorados_id_seq'::regclass);


--
-- Name: mensagens_cruas id; Type: DEFAULT; Schema: public; Owner: waha
--

ALTER TABLE ONLY public.mensagens_cruas ALTER COLUMN id SET DEFAULT nextval('public.mensagens_cruas_id_seq'::regclass);


--
-- Name: promocoes id; Type: DEFAULT; Schema: public; Owner: waha
--

ALTER TABLE ONLY public.promocoes ALTER COLUMN id SET DEFAULT nextval('public.promocoes_id_seq'::regclass);


--
-- Name: categorias categorias_nome_key; Type: CONSTRAINT; Schema: public; Owner: waha
--

ALTER TABLE ONLY public.categorias
    ADD CONSTRAINT categorias_nome_key UNIQUE (nome);


--
-- Name: categorias categorias_pkey; Type: CONSTRAINT; Schema: public; Owner: waha
--

ALTER TABLE ONLY public.categorias
    ADD CONSTRAINT categorias_pkey PRIMARY KEY (id);


--
-- Name: grupos_monitorados grupos_monitorados_chat_id_key; Type: CONSTRAINT; Schema: public; Owner: waha
--

ALTER TABLE ONLY public.grupos_monitorados
    ADD CONSTRAINT grupos_monitorados_chat_id_key UNIQUE (chat_id);


--
-- Name: grupos_monitorados grupos_monitorados_pkey; Type: CONSTRAINT; Schema: public; Owner: waha
--

ALTER TABLE ONLY public.grupos_monitorados
    ADD CONSTRAINT grupos_monitorados_pkey PRIMARY KEY (id);


--
-- Name: mensagens_cruas mensagens_cruas_pkey; Type: CONSTRAINT; Schema: public; Owner: waha
--

ALTER TABLE ONLY public.mensagens_cruas
    ADD CONSTRAINT mensagens_cruas_pkey PRIMARY KEY (id);


--
-- Name: mensagens_cruas mensagens_cruas_wa_message_id_key; Type: CONSTRAINT; Schema: public; Owner: waha
--

ALTER TABLE ONLY public.mensagens_cruas
    ADD CONSTRAINT mensagens_cruas_wa_message_id_key UNIQUE (wa_message_id);


--
-- Name: promocoes promocoes_pkey; Type: CONSTRAINT; Schema: public; Owner: waha
--

ALTER TABLE ONLY public.promocoes
    ADD CONSTRAINT promocoes_pkey PRIMARY KEY (id);


--
-- Name: promocoes promocoes_url_key; Type: CONSTRAINT; Schema: public; Owner: waha
--

ALTER TABLE ONLY public.promocoes
    ADD CONSTRAINT promocoes_url_key UNIQUE (url);


--
-- Name: idx_mensagens_cruas_chat; Type: INDEX; Schema: public; Owner: waha
--

CREATE INDEX idx_mensagens_cruas_chat ON public.mensagens_cruas USING btree (chat_id, recebida_em DESC);


--
-- Name: promocoes promocoes_categoria_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: waha
--

ALTER TABLE ONLY public.promocoes
    ADD CONSTRAINT promocoes_categoria_id_fkey FOREIGN KEY (categoria_id) REFERENCES public.categorias(id);


--
-- Name: promocoes promocoes_mensagem_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: waha
--

ALTER TABLE ONLY public.promocoes
    ADD CONSTRAINT promocoes_mensagem_id_fkey FOREIGN KEY (mensagem_id) REFERENCES public.mensagens_cruas(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict Gs0FnZRh0DDct2X579shUouoIdIUOHynLFOD63eihuJq3jhGWvHke7direkAh2E

