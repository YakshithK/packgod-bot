-- Increment roasts_received
create or replace function increment_roasts_received(uid text)
returns void as $$
begin
  update users
  set roasts_received = roasts_received + 1
  where id = uid;
end;
$$ language plpgsql;

-- Increment roasts_given
create or replace function increment_roasts_given(uid text)
returns void as $$
begin
  update users
  set roasts_given = roasts_given + 1
  where id = uid;
end;
$$ language plpgsql;
    