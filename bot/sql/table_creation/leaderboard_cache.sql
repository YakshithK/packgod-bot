create table leaderboard_cache (
  user_id text primary key,
  roast_count integer default 0,
  last_updated timestamp with time zone default now(),
  foreign key (user_id) references users(id) on delete cascade
);