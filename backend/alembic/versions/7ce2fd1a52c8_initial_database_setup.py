"""Initial database setup

Revision ID: 7ce2fd1a52c8
Revises:
Create Date: 2025-05-18 01:33:19.737471+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7ce2fd1a52c8"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Configure the JWT secret for the db. This should be set via environment variable.
    # See also: https://github.com/PostgREST/postgrest/discussions/3765
    # See also: https://datatracker.ietf.org/doc/html/rfc7519
    op.execute(sa.text("""alter database template_db set "app.jwt_secret" to 'cLrngXnioRTsqo2vBKqiEPCN467PrrRl'"""))

    # Make sure that functions can be executed only by those roles we allow to excute.
    # Thus, we first revoke all privileges and then add them incrementally back as needed.
    # See also: https://docs.postgrest.org/en/v12/explanations/db_authz.html#functions
    op.execute(sa.text("alter default privileges revoke execute on functions from public"))

    # We make use of these extensions:
    #
    # https://www.postgresql.org/docs/current/pgcrypto.html
    # https://github.com/michelp/pgjwt
    # https://github.com/nmandery/pg_byteamagic
    #
    # Install them into the default `public` schema such that they can be accessed from
    # both our own `api` and `auth` and `data` schemas.
    op.execute(
        sa.text(
            """
            create extension pgcrypto;
            create extension pgjwt;
            create extension byteamagic;
            """
        )
    )

    # Public `api` schema where the API related views and functions live. We configure
    # this schema for PostgREST as the one for which REST endpoints are constructed.
    op.execute(sa.text("create schema api"))

    # Private schema for handling user auth. The user table lives here which is not
    # exposed through public REST endpoints.
    op.execute(sa.text("create schema auth"))

    # Private schema that stores the actual tables. Data from these tables are exposed
    # via views to the public `api` schema.
    op.execute(sa.text("create schema data"))

    # This is a special role known to PostgREST from which other users (see below) are
    # impersonated depending on auth.
    # See also: https://postgrest.org/en/stable/references/auth.html#overview-of-role-system
    op.execute(sa.text("create role authenticator login noinherit nocreatedb nocreaterole nosuperuser"))

    # The `anonymous` role PostgREST switches to if no auth header was passed along
    # with a request.
    # TODO What about granting usage on `auth` schema? See functions below.
    op.execute(
        sa.text(
            """
            create role anonymous nologin noinherit;  -- TODO Other settings?
            grant anonymous to authenticator;
            grant usage on schema auth, api to anonymous;
            grant execute on function public.crypt, public.gen_salt(text), public.sign, public.url_encode, public.algorithm_sign, public.hmac(text, text, text) to anonymous;
            """
        )
    )

    # The `apiuser` role PostgREST switches to if JWT auth was successful.
    # See also: https://postgrest.org/en/stable/references/auth.html#jwt-based-user-impersonation
    op.execute(
        sa.text(
            """
            create role apiuser nologin noinherit;  -- TODO Other settings?
            grant apiuser to authenticator;
            grant usage on schema auth, api, data to apiuser;
            grant execute on function public.crypt, public.gen_salt(text), public.byteamagic_mime to apiuser;
            """
        )
    )

    # The `dramatiq` role is *not* used by PostgREST! Instead, async Dramatiq workers
    # that need to access the db to fetch and write back data use this role. These
    # workers are trusted because we built them ourselves.
    op.execute(
        sa.text(
            """
            create role dramatiq login password 'dramatiq' noinherit;  -- TODO Other settings?
            grant usage on schema data to dramatiq;
            """
        )
    )

    # The `user` table in the private `auth` schema contains all users in the system. In the
    # future we might add more roles (e.g. admin, or one role per user account). Furthermore,
    # we grant only limited access to the table for the different roles, and further restrict
    # row-level security: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
    # Lastly we add an insert/update trigger function to hash the password and store that hash.
    # See also: https://postgrest.org/en/stable/how-tos/sql-user-management.html#storing-users-and-passwords
    # TODO See also: https://github.com/PostgREST/postgrest/discussions/3696#discussioncomment-10408092
    op.execute(
        sa.text(
            """
            create table auth.user (
                id bigserial primary key,
                created_at timestamp with time zone default now(),
                email text unique not null,  -- TODO CHECK constraint for email format.
                password text not null,  -- This is the hash, not the clear text password.
                role text not null default 'apiuser' check (role = 'apiuser'),  -- TODO FK to known roles?
                first_name text,
                last_name text
            )
            """
        )
    )

    op.execute(
        sa.text(
            """
            grant select, insert on auth.user to anonymous;  -- TODO Limit select columns!
            grant usage on auth.user_id_seq to anonymous;
            grant select, update(first_name, last_name) on auth.user to apiuser;  -- TODO Limit select columns!
            grant select on auth.user to dramatiq;  -- TODO Limit select columns!
            """
        )
    )

    op.execute(
        sa.text(
            """
            alter table auth.user enable row level security;
            create policy user_email_policy on auth.user to anonymous, apiuser
                using (
                    current_role = 'anonymous'
                    or email = current_setting('request.jwt.claims', true)::json->>'email'
                );
            """
        )
    )

    op.execute(
        sa.text(
            """
            create function auth.encrypt_password() returns trigger language plpgsql as $$
                begin
                    if new.password is not null then
                        new.password = crypt(new.password, gen_salt('bf'));  -- TODO min 8 chars, other rules?
                    end if;
                    return new;
                end;
            $$
            """
        )
    )

    op.execute(
        sa.text(
            """
            create trigger encrypt_password
                before insert or update on auth.user
                for each row
                execute procedure auth.encrypt_password();
            """
        )
    )

    # The `dramatiq_queue` table implements a message queue of messages for the async framework
    # Dramatiq. Messages are inserted and trigger a Postgres notification that the Dramatiq broker
    # listens to; in addition the broker polls this table to ensure messages aren't dropped. Note
    # that responses may be inserted as new rows if the original message was removed from the table;
    # in that case it woulnd't be possible to find the owning user for that response anymore because
    # users are associated with the now-deleted message.
    # See also: https://gitlab.com/dalibo/dramatiq-pg
    # See also: https://www.postgresql.org/docs/current/sql-notify.html
    op.execute(
        sa.text(
            """
            create table data.dramatiq_queue(
                message_id uuid primary key,
                user_id bigint references auth.user(id),
                queue_name text not null,
                state text not null check (state in ('queued', 'consumed', 'rejected', 'done')),
                mtime timestamp with time zone,
                message jsonb,
                result jsonb,
                result_ttl timestamp with time zone
            )  -- TODO Consider `without oids` as Dramatiq-PG uses.
            """
        )
    )

    op.execute(
        sa.text(
            """
            grant select, insert on data.dramatiq_queue to apiuser;
            grant all privileges on table data.dramatiq_queue to dramatiq;
            """
        )
    )

    op.execute(
        sa.text(
            """
            alter table data.dramatiq_queue enable row level security;
            create policy user_message_policy on data.dramatiq_queue to apiuser, dramatiq
                using (
                    current_role = 'dramatiq'
                    or user_id = (
                        select id
                            from auth.user
                            where email = current_setting('request.jwt.claims', true)::json->>'email'
                    )
                );
            """
        )
    )

    # The public `profile` view presents some columns from the `auth.user` table. An auth'ed
    # user can view and update only some of the columns of the underlying table.
    op.execute(
        sa.text(
            """
            create view api.profile with (security_invoker = true) as
                select email, first_name, last_name, created_at from auth.user
            """
        )
    )

    op.execute(sa.text("grant select, update(first_name, last_name) on api.profile to apiuser"))

    #
    op.execute(
        sa.text(
            """
            create view api.job with (security_invoker = true) as
                select message_id as job_id, state, result from data.dramatiq_queue
            """
        )
    )

    op.execute(sa.text("grant select on api.job to apiuser"))

    # Public API function to sign up a new user: insert a row into the private `auth.user` table.
    # TODO How do we return a 201 here? Should this function return any payload at all?
    op.execute(
        sa.text(
            """
            create function api.signup(email text, password text) returns record language plpgsql as $$
                declare
                    ret record;
                begin
                    insert into auth.user as u (email, password)
                        values (signup.email, signup.password)
                        returning u.created_at, u.email into ret;
                    return ret;
                end;
            $$
            """
        )
    )

    op.execute(sa.text("grant execute on function api.signup to anonymous"))

    # Public API function to log in an existing user: return the JWT for the user which allows PostgREST
    # to impersonate the `apiuser` and therewith get access to the resources.
    op.execute(
        sa.text(
            """
            create function api.login(email text, password text) returns record language plpgsql as $$
                declare
                    role_ text;
                    token record;
                begin
                    select role
                        from auth.user
                        where auth.user.email = login.email
                            and auth.user.password = crypt(login.password, auth.user.password)
                        into role_;
                    if not found then
                        raise invalid_password using message = 'invalid user or password';
                    end if;
                    select sign(row_to_json(r), current_setting('app.jwt_secret')) as token
                        from (
                            select role_ as role, login.email as email, extract(epoch from now())::integer + 60*60 as exp
                        ) r
                        into token;
                    return token;
                end;
            $$
            """
        )
    )

    op.execute(sa.text("grant execute on function api.login to anonymous"))

    # Public API function to create & send a message to the async Dramatiq workers.
    op.execute(
        sa.text(
            """
            create function api.job() returns record language sql as $$
                with "user" as (
                    select id from auth.user where email = current_setting('request.jwt.claims', true)::json->>'email'
                ),
                message as (
                    select
                        'job_q' as queue_name,  -- Dramatiq message queue name.
                        'job' as actor_name,  -- Dramatiq actor function.
                        jsonb_build_array() as args,  -- Positional args for function.
                        jsonb_build_object() as kwargs,  -- Keyword args for function.
                        jsonb_build_object() as options,  -- Additional Dramatiq broker options.
                        gen_random_uuid() as message_id,
                        extract(epoch from now())::bigint as message_timestamp
                ),
                enque as (
                    insert into data.dramatiq_queue (user_id, message_id, queue_name, state, mtime, message)
                        select
                            u.id,
                            m.message_id,
                            m.queue_name,
                            'queued',
                            to_timestamp(m.message_timestamp),
                            (select to_json(message) from message)
                        from message m, "user" u
                        returning queue_name, message_id
                ),
                notify as (
                    select
                        message_id,
                        pg_notify('dramatiq.' || queue_name || '.enqueue', jsonb_build_object('message_id', message_id)::text)
                        from enque
                )
                select message_id as job_id from notify
            $$
            """
        )
    )

    op.execute(sa.text("grant execute on function api.job to apiuser"))


def downgrade() -> None:
    """Downgrade schema."""
    raise NotImplementedError("No down migrations beyond this version")
