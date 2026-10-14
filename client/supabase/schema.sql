-- SPARK — Supabase schema (email + username auth)
-- Run in Supabase SQL editor (Database → SQL editor → New query).
--
-- If you already ran the old migration, this script is safe to re-run:
-- it drops old policies/triggers and recreates them.
--
-- ── Auth setup (no SMTP / no paid email required) ───────────────────────────
-- Also disable email confirmation in the dashboard (recommended):
--   Authentication → Providers → Email → turn OFF "Confirm email" → Save
--
-- The trigger below auto-confirms new accounts even if that toggle is still on,
-- so users can sign up and sign in immediately without verification emails.

-- ── Schema for privileged auth helpers (not exposed via Data API) ────────────
create schema if not exists private;

-- ── users ────────────────────────────────────────────────────────────────────
-- auth.users is managed by Supabase Auth.
-- This table stores the public profile (email, username, settings).
create table if not exists public.users (
  id           uuid primary key references auth.users (id) on delete cascade,
  email        text unique not null,
  username     text unique not null,
  settings     jsonb not null default '{"primaryCommunicationMethod":"nats"}'::jsonb,
  integrations jsonb not null default '[]'::jsonb,
  created_at   timestamptz not null default now()
);

-- Add email column if upgrading from the old schema
alter table public.users add column if not exists email text;

-- Backfill email from auth.users for any existing rows
update public.users u
set email = a.email
from auth.users a
where u.id = a.id and (u.email is null or u.email = '');

-- Enforce NOT NULL after backfill (skip if you still have orphan rows)
-- alter table public.users alter column email set not null;

-- ── groups ───────────────────────────────────────────────────────────────────
create table if not exists public.groups (
  id               uuid primary key default gen_random_uuid(),
  name             text not null default 'New Group',
  assigned_user_id uuid references public.users (id) on delete cascade,
  devices          jsonb not null default '{"client":[],"server":[]}'::jsonb,
  messages         jsonb not null default '[]'::jsonb,
  command_presets  jsonb not null default '[]'::jsonb,
  ai_messages      jsonb not null default '[]'::jsonb,
  settings         jsonb not null default '{}'::jsonb,
  created_at       timestamptz not null default now()
);

-- ── client_devices ────────────────────────────────────────────────────────────
create table if not exists public.client_devices (
  id                uuid primary key default gen_random_uuid(),
  name              text,
  assigned_group_id uuid references public.groups (id) on delete set null,
  assigned_user_id  uuid references public.users (id) on delete cascade,
  messages          jsonb not null default '[]'::jsonb,
  device_commands   jsonb not null default '[]'::jsonb,
  settings          jsonb not null default '{}'::jsonb,
  aliases           text[] not null default '{}',
  created_at        timestamptz not null default now()
);

-- ── server_devices ────────────────────────────────────────────────────────────
create table if not exists public.server_devices (
  id                uuid primary key default gen_random_uuid(),
  name              text,
  assigned_group_id uuid references public.groups (id) on delete set null,
  assigned_user_id  uuid references public.users (id) on delete cascade,
  messages          jsonb not null default '[]'::jsonb,
  device_commands   jsonb not null default '{}'::jsonb,
  settings          jsonb not null default '{}'::jsonb,
  aliases           text[] not null default '{}',
  created_at        timestamptz not null default now()
);

-- ── messages ─────────────────────────────────────────────────────────────────
create table if not exists public.messages (
  id               uuid primary key default gen_random_uuid(),
  "from"           text,
  "to"             text,
  content          text,
  from_device_type text not null default 'server',
  status           int  not null default 0,
  created_at       timestamptz not null default now()
);

-- ── Row-Level Security ────────────────────────────────────────────────────────
alter table public.users          enable row level security;
alter table public.groups         enable row level security;
alter table public.client_devices enable row level security;
alter table public.server_devices enable row level security;
alter table public.messages       enable row level security;

-- Drop legacy single-policy definitions
drop policy if exists "Users: own row" on public.users;
drop policy if exists "Groups: own" on public.groups;
drop policy if exists "ClientDevices: own" on public.client_devices;
drop policy if exists "ServerDevices: own" on public.server_devices;
drop policy if exists "Messages: authenticated" on public.messages;

-- users: split policies so INSERT/UPDATE/SELECT all work correctly
create policy "users_select_own" on public.users
  for select to authenticated
  using (auth.uid() = id);

create policy "users_insert_own" on public.users
  for insert to authenticated
  with check (auth.uid() = id);

create policy "users_update_own" on public.users
  for update to authenticated
  using (auth.uid() = id)
  with check (auth.uid() = id);

create policy "users_delete_own" on public.users
  for delete to authenticated
  using (auth.uid() = id);

-- groups
create policy "groups_select_own" on public.groups
  for select to authenticated
  using (auth.uid() = assigned_user_id);

create policy "groups_insert_own" on public.groups
  for insert to authenticated
  with check (auth.uid() = assigned_user_id);

create policy "groups_update_own" on public.groups
  for update to authenticated
  using (auth.uid() = assigned_user_id)
  with check (auth.uid() = assigned_user_id);

create policy "groups_delete_own" on public.groups
  for delete to authenticated
  using (auth.uid() = assigned_user_id);

-- client_devices
create policy "client_devices_select_own" on public.client_devices
  for select to authenticated
  using (auth.uid() = assigned_user_id);

create policy "client_devices_insert_own" on public.client_devices
  for insert to authenticated
  with check (auth.uid() = assigned_user_id);

create policy "client_devices_update_own" on public.client_devices
  for update to authenticated
  using (auth.uid() = assigned_user_id)
  with check (auth.uid() = assigned_user_id);

create policy "client_devices_delete_own" on public.client_devices
  for delete to authenticated
  using (auth.uid() = assigned_user_id);

-- server_devices
create policy "server_devices_select_own" on public.server_devices
  for select to authenticated
  using (auth.uid() = assigned_user_id);

create policy "server_devices_insert_own" on public.server_devices
  for insert to authenticated
  with check (auth.uid() = assigned_user_id);

create policy "server_devices_update_own" on public.server_devices
  for update to authenticated
  using (auth.uid() = assigned_user_id)
  with check (auth.uid() = assigned_user_id);

create policy "server_devices_delete_own" on public.server_devices
  for delete to authenticated
  using (auth.uid() = assigned_user_id);

-- messages: any authenticated user for now
create policy "messages_select_authenticated" on public.messages
  for select to authenticated
  using (true);

create policy "messages_insert_authenticated" on public.messages
  for insert to authenticated
  with check (true);

create policy "messages_update_authenticated" on public.messages
  for update to authenticated
  using (true)
  with check (true);

create policy "messages_delete_authenticated" on public.messages
  for delete to authenticated
  using (true);

-- ── Trigger: auto-confirm email (no SMTP required) ───────────────────────────
-- Marks new auth users as confirmed before insert so sign-in works immediately.

drop trigger if exists on_auth_user_auto_confirm on auth.users;
drop function if exists public.auto_confirm_email();

create or replace function private.auto_confirm_email()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  new.email_confirmed_at := coalesce(new.email_confirmed_at, now());
  new.confirmed_at := coalesce(new.confirmed_at, now());
  return new;
end;
$$;

create trigger on_auth_user_auto_confirm
  before insert on auth.users
  for each row execute function private.auto_confirm_email();

revoke all on function private.auto_confirm_email() from public, anon, authenticated;

-- ── Trigger: auto-create profile on auth signup ───────────────────────────────
-- Runs as security definer in the private schema so it bypasses RLS.
-- This is the ONLY place profile rows should be created — the client must NOT
-- insert into public.users during signUp (no session yet when email confirm is on).

drop trigger if exists on_auth_user_created on auth.users;
drop function if exists public.handle_new_user();

create or replace function private.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_username text;
begin
  v_username := coalesce(
    nullif(trim(new.raw_user_meta_data->>'username'), ''),
    split_part(new.email, '@', 1)
  );

  insert into public.users (id, email, username)
  values (new.id, new.email, v_username)
  on conflict (id) do update
    set email    = excluded.email,
        username = excluded.username;

  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function private.handle_new_user();

-- Revoke public access to the private helper function
revoke all on function private.handle_new_user() from public;
revoke all on function private.handle_new_user() from anon, authenticated;
