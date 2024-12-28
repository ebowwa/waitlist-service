-- Create waitlist_entries table
CREATE TABLE public.waitlist (
  id bigserial NOT NULL,
  name character varying NOT NULL,
  email character varying NOT NULL,
  ip_address character varying NULL,
  comment character varying NULL,
  referral_source character varying NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT waitlist_pkey PRIMARY KEY (id),
  CONSTRAINT waitlist_email_key UNIQUE (email)
) TABLESPACE pg_default;