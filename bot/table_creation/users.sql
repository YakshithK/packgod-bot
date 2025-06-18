create table users (
  id uuid primary key,
  premium boolean default false,
  roasts_received integer default 0,
  roasts_given integer default 0,
  favorite_style text default 'packgod',
  brutal_mode boolean default false,
  created_at timestamp with time zone default now()
);