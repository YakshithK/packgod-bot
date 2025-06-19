create table roasts (
  id bigserial primary key,
  target_id text not null,
  roaster_id text not null,
  style text not null,
  brutal_mode boolean default false,
  content text not null,
  created_at timestamp with time zone default now(),
  foreign key (target_id) references users(id) on delete cascade,
  foreign key (roaster_id) references users(id) on delete cascade
);
