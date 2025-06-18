CREATE TABLE roasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id TEXT NOT NULL,
    roaster_id TEXT NOT NULL,
    style TEXT NOT NULL,
    timestamp DATETIMES DEFAULT CURRENT_TIMESTAMP,
    FOREGIN KEY (target_id) REFERENCES users(id),
    FOREGIN KEY (roaster_id) REFERENCES users(id)
)