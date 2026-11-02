CREATE TABLE leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_name TEXT NOT NULL,
    niche TEXT NOT NULL,
    phone TEXT DEFAULT '',
    website TEXT DEFAULT '',
    address TEXT DEFAULT '',
    city TEXT DEFAULT '',
    latitude TEXT DEFAULT '',
    longitude TEXT DEFAULT '',
    rating TEXT NOT NULL DEFAULT 'n/a',
    osm_url TEXT DEFAULT ''
);
