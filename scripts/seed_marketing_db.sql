DROP TABLE IF EXISTS fct_attribution_performance CASCADE;
DROP TABLE IF EXISTS fct_channel_attribution CASCADE;
DROP TABLE IF EXISTS fct_campaign_measurement CASCADE;

CREATE TABLE fct_campaign_measurement (
    campaign_id                    INTEGER PRIMARY KEY,
    campaign_name                  VARCHAR(150) NOT NULL,
    channel                        VARCHAR(50) NOT NULL,
    total_spend                    NUMERIC(10,2) NOT NULL,
    total_impressions              INTEGER NOT NULL,
    total_clicks                   INTEGER NOT NULL,
    ctr                            NUMERIC(5,4) NOT NULL,
    first_touch_conversions        INTEGER NOT NULL,
    first_touch_revenue            NUMERIC(10,2) NOT NULL,
    last_touch_conversions         INTEGER NOT NULL,
    last_touch_revenue             NUMERIC(10,2) NOT NULL,
    linear_attributed_conversions  NUMERIC(10,2) NOT NULL,
    linear_attributed_revenue      NUMERIC(10,2) NOT NULL,
    first_touch_roas               NUMERIC(6,2) NOT NULL,
    last_touch_roas                NUMERIC(6,2) NOT NULL,
    linear_roas                    NUMERIC(6,2) NOT NULL
);

CREATE TABLE fct_channel_attribution (
    channel                        VARCHAR(50) PRIMARY KEY,
    total_spend                    NUMERIC(10,2) NOT NULL,
    channel_ctr                    NUMERIC(5,4) NOT NULL,
    first_touch_revenue            NUMERIC(10,2) NOT NULL,
    last_touch_revenue             NUMERIC(10,2) NOT NULL,
    linear_attributed_revenue      NUMERIC(10,2) NOT NULL,
    first_touch_roas               NUMERIC(6,2) NOT NULL,
    last_touch_roas                NUMERIC(6,2) NOT NULL,
    linear_roas                    NUMERIC(6,2) NOT NULL
);

CREATE TABLE fct_attribution_performance (
    id                       SERIAL PRIMARY KEY,
    campaign_id              INTEGER NOT NULL,
    campaign_name            VARCHAR(150) NOT NULL,
    channel                  VARCHAR(50) NOT NULL,
    attribution_model        VARCHAR(20) NOT NULL CHECK (attribution_model IN ('first_touch','last_touch','linear')),
    total_spend              NUMERIC(10,2) NOT NULL,
    attributed_conversions   NUMERIC(10,2) NOT NULL,
    attributed_revenue       NUMERIC(10,2) NOT NULL,
    attributed_roas          NUMERIC(6,2) NOT NULL
);

INSERT INTO fct_campaign_measurement VALUES
(1, 'Summer Meta Prospecting', 'Meta', 5000.00, 200000, 4000, 0.0200, 40, 8000.00, 25, 6000.00, 32.5, 7200.00, 1.60, 1.20, 1.44),
(2, 'Google Search Brand', 'Google', 3000.00, 90000, 5400, 0.0600, 15, 3500.00, 60, 15000.00, 35.0, 8500.00, 1.17, 5.00, 2.83),
(3, 'Affiliate Referral Q3', 'Affiliate', 1200.00, 30000, 1800, 0.0600, 10, 2200.00, 12, 2800.00, 11.0, 2500.00, 1.83, 2.33, 2.08),
(4, 'Email Winback Campaign', 'Email', 200.00, 15000, 3000, 0.2000, 5, 900.00, 45, 9500.00, 22.0, 4600.00, 4.50, 47.50, 23.00);

INSERT INTO fct_channel_attribution VALUES
('Meta', 5000.00, 0.0200, 8000.00, 6000.00, 7200.00, 1.60, 1.20, 1.44),
('Google', 3000.00, 0.0600, 3500.00, 15000.00, 8500.00, 1.17, 5.00, 2.83),
('Affiliate', 1200.00, 0.0600, 2200.00, 2800.00, 2500.00, 1.83, 2.33, 2.08),
('Email', 200.00, 0.2000, 900.00, 9500.00, 4600.00, 4.50, 47.50, 23.00);

INSERT INTO fct_attribution_performance (campaign_id, campaign_name, channel, attribution_model, total_spend, attributed_conversions, attributed_revenue, attributed_roas) VALUES
(1, 'Summer Meta Prospecting', 'Meta', 'first_touch', 5000.00, 40, 8000.00, 1.60),
(1, 'Summer Meta Prospecting', 'Meta', 'last_touch', 5000.00, 25, 6000.00, 1.20),
(1, 'Summer Meta Prospecting', 'Meta', 'linear', 5000.00, 32.5, 7200.00, 1.44),
(2, 'Google Search Brand', 'Google', 'first_touch', 3000.00, 15, 3500.00, 1.17),
(2, 'Google Search Brand', 'Google', 'last_touch', 3000.00, 60, 15000.00, 5.00),
(2, 'Google Search Brand', 'Google', 'linear', 3000.00, 35.0, 8500.00, 2.83);
