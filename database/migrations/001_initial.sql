-- 001_initial.sql
-- UP

create table if not exists agent_runs (
    id          bigserial primary key,
    agent_name  text          not null,
    layer       text          not null default '',
    task        text          not null default '',
    output      text          not null default '',
    cost_usd    numeric(12,8) not null default 0,
    latency_ms  integer       not null default 0,
    status      text          not null default 'success',
    error       text,
    created_at  timestamptz   not null default now()
);

create table if not exists swarm_runs (
    id              bigserial primary key,
    pipeline_id     text          not null,
    task            text          not null default '',
    total_cost_usd  numeric(12,8) not null default 0,
    agents_used     jsonb         not null default '[]',
    latency_ms      integer       not null default 0,
    status          text          not null default 'ok',
    created_at      timestamptz   not null default now()
);

create table if not exists memory_entries (
    id          bigserial primary key,
    from_agent  text        not null,
    to_agent    text        not null,
    key         text        not null,
    content     text        not null,
    created_at  timestamptz not null default now()
);

create table if not exists dream_reports (
    id          bigserial primary key,
    report      jsonb       not null,
    created_at  timestamptz not null default now()
);

create table if not exists swarm_config (
    id          bigserial primary key,
    config      jsonb       not null,
    created_at  timestamptz not null default now()
);

-- Indexes for common queries
create index if not exists idx_agent_runs_layer     on agent_runs (layer);
create index if not exists idx_agent_runs_created   on agent_runs (created_at desc);
create index if not exists idx_swarm_runs_created   on swarm_runs (created_at desc);
create index if not exists idx_memory_entries_key   on memory_entries (key);
create index if not exists idx_memory_entries_agent on memory_entries (to_agent, from_agent);

-- DOWN
-- drop table if exists swarm_config;
-- drop table if exists dream_reports;
-- drop table if exists memory_entries;
-- drop table if exists swarm_runs;
-- drop table if exists agent_runs;
