create table daily_roasts (
    user_id text references users(id),
    last_roast date,
    streak integer default 0,
    primary key (user_id)
)