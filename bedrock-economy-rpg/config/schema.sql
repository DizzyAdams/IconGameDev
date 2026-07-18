-- Players core
CREATE TABLE IF NOT EXISTS players (
    xuid VARCHAR(32) PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    class VARCHAR(32) DEFAULT 'adventurer',
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    gems INTEGER DEFAULT 0,
    coins BIGINT DEFAULT 100,
    perm_group VARCHAR(32) DEFAULT 'default',
    first_join TIMESTAMPTZ DEFAULT NOW(),
    last_join TIMESTAMPTZ DEFAULT NOW(),
    playtime_seconds BIGINT DEFAULT 0,
    is_banned BOOLEAN DEFAULT FALSE,
    ban_reason TEXT,
    banned_until TIMESTAMPTZ
);

-- Economy: transactions log
CREATE TABLE IF NOT EXISTS economy_transactions (
    id BIGSERIAL PRIMARY KEY,
    from_xuid VARCHAR(32) REFERENCES players(xuid),
    to_xuid VARCHAR(32) REFERENCES players(xuid),
    amount BIGINT NOT NULL,
    tax BIGINT DEFAULT 0,
    type VARCHAR(32) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Economy: banking (savings accounts)
CREATE TABLE IF NOT EXISTS economy_banking (
    xuid VARCHAR(32) PRIMARY KEY REFERENCES players(xuid),
    balance BIGINT DEFAULT 0,
    interest_rate DECIMAL(5,4) DEFAULT 0.005,
    last_interest_paid TIMESTAMPTZ DEFAULT NOW()
);

-- Economy: player shops
CREATE TABLE IF NOT EXISTS economy_shops (
    id BIGSERIAL PRIMARY KEY,
    owner_xuid VARCHAR(32) REFERENCES players(xuid),
    item_id VARCHAR(64) NOT NULL,
    item_data INTEGER DEFAULT 0,
    amount INTEGER NOT NULL,
    buy_price BIGINT,
    sell_price BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Economy: auction house
CREATE TABLE IF NOT EXISTS economy_auctions (
    id BIGSERIAL PRIMARY KEY,
    seller_xuid VARCHAR(32) REFERENCES players(xuid),
    item_id VARCHAR(64) NOT NULL,
    item_data INTEGER DEFAULT 0,
    amount INTEGER NOT NULL,
    starting_bid BIGINT NOT NULL,
    current_bid BIGINT,
    bidder_xuid VARCHAR(32) REFERENCES players(xuid),
    buyout_price BIGINT,
    ends_at TIMESTAMPTZ NOT NULL,
    status VARCHAR(16) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RPG: skills
CREATE TABLE IF NOT EXISTS rpg_skills (
    id SERIAL PRIMARY KEY,
    xuid VARCHAR(32) REFERENCES players(xuid),
    skill_name VARCHAR(64) NOT NULL,
    level INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0,
    UNIQUE(xuid, skill_name)
);

-- RPG: quests
CREATE TABLE IF NOT EXISTS rpg_quests (
    id BIGSERIAL PRIMARY KEY,
    xuid VARCHAR(32) REFERENCES players(xuid),
    quest_id VARCHAR(64) NOT NULL,
    progress INTEGER DEFAULT 0,
    goal INTEGER NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    reward_claimed BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMPTZ,
    UNIQUE(xuid, quest_id)
);

-- RPG: completed quests (history)
CREATE TABLE IF NOT EXISTS rpg_completed_quests (
    id BIGSERIAL PRIMARY KEY,
    xuid VARCHAR(32) REFERENCES players(xuid),
    quest_id VARCHAR(64) NOT NULL,
    completed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Moderation
CREATE TABLE IF NOT EXISTS moderation_log (
    id BIGSERIAL PRIMARY KEY,
    target_xuid VARCHAR(32) REFERENCES players(xuid),
    moderator_xuid VARCHAR(32) REFERENCES players(xuid),
    action VARCHAR(32) NOT NULL,
    reason TEXT,
    duration_seconds INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Analytics: player sessions
CREATE TABLE IF NOT EXISTS analytics_sessions (
    id BIGSERIAL PRIMARY KEY,
    xuid VARCHAR(32) REFERENCES players(xuid),
    ip_address INET,
    client_version VARCHAR(16),
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    duration_seconds INTEGER
);

-- Analytics: economy snapshots (for graphs)
CREATE TABLE IF NOT EXISTS analytics_economy (
    id BIGSERIAL PRIMARY KEY,
    total_coins BIGINT DEFAULT 0,
    total_players INTEGER DEFAULT 0,
    transactions_24h INTEGER DEFAULT 0,
    top_balance BIGINT DEFAULT 0,
    snapshot_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_transactions_from ON economy_transactions(from_xuid);
CREATE INDEX IF NOT EXISTS idx_transactions_to ON economy_transactions(to_xuid);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON economy_transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_created ON economy_transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_auctions_status ON economy_auctions(status);
CREATE INDEX IF NOT EXISTS idx_auctions_ends ON economy_auctions(ends_at);
CREATE INDEX IF NOT EXISTS idx_quests_xuid ON rpg_quests(xuid);
CREATE INDEX IF NOT EXISTS idx_moderation_target ON moderation_log(target_xuid);
CREATE INDEX IF NOT EXISTS idx_sessions_xuid ON analytics_sessions(xuid);
CREATE INDEX IF NOT EXISTS idx_sessions_joined ON analytics_sessions(joined_at);
