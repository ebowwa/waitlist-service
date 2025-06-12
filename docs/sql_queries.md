# SQL Queries Overview

This document summarizes SQL files and database schema definitions found in the repository. These queries define the waitlist tables and related policies both for local development and for Supabase.

## init.sql

Creates the `waitlist` table and associated trigger to automatically update the `updated_at` timestamp on row updates.

```sql
CREATE TABLE IF NOT EXISTS waitlist (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    ip_address VARCHAR(45),
    comment TEXT,
    referral_source VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_waitlist_email ON waitlist(email);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_waitlist_updated_at ON waitlist;
CREATE TRIGGER update_waitlist_updated_at
    BEFORE UPDATE ON waitlist
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## create_supabase_waitlist_table.sql

Defines the Supabase table `public.waitlist` with a unique constraint on `email`.

```sql
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
);
```

## rls_policy.sql

Enables row level security on the Supabase table and sets policies for both authenticated and anonymous users.

```sql
ALTER TABLE public.waitlist ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all access for authenticated users" ON public.waitlist
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Enable insert for anonymous users" ON public.waitlist
    FOR INSERT
    TO anon
    WITH CHECK (true);

CREATE POLICY "Enable select for anonymous users" ON public.waitlist
    FOR SELECT
    TO anon
    USING (true);
```

## SQLite Schema

The SQLite database located at `src/data/development.db` contains the table `waitlist_entries` with indexes on `email` and `id`.

```sql
CREATE TABLE waitlist_entries (
        id INTEGER NOT NULL,
        name VARCHAR NOT NULL,
        email VARCHAR NOT NULL,
        comment VARCHAR,
        referral_source VARCHAR,
        created_at DATETIME,
        is_active BOOLEAN,
        PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_waitlist_entries_email ON waitlist_entries (email);
CREATE INDEX ix_waitlist_entries_id ON waitlist_entries (id);
```

