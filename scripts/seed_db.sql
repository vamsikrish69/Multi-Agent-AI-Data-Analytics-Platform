-- ============================================================
-- Mobility / Taxi Business Schema (idempotent: safe to re-run)
-- ============================================================

DROP TABLE IF EXISTS driver_ratings CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS rides CASCADE;
DROP TABLE IF EXISTS drivers CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS locations CASCADE;

CREATE TABLE locations (
    location_id     SERIAL PRIMARY KEY,
    city            VARCHAR(100) NOT NULL,
    zone_name       VARCHAR(100) NOT NULL,
    latitude        NUMERIC(9,6),
    longitude       NUMERIC(9,6)
);

CREATE TABLE customers (
    customer_id     SERIAL PRIMARY KEY,
    full_name       VARCHAR(150) NOT NULL,
    email           VARCHAR(150) UNIQUE NOT NULL,
    signup_date     DATE NOT NULL DEFAULT CURRENT_DATE,
    home_location_id INTEGER REFERENCES locations(location_id)
);

CREATE TABLE drivers (
    driver_id       SERIAL PRIMARY KEY,
    full_name       VARCHAR(150) NOT NULL,
    license_number  VARCHAR(50) UNIQUE NOT NULL,
    hire_date       DATE NOT NULL DEFAULT CURRENT_DATE,
    vehicle_type    VARCHAR(50) NOT NULL
);

CREATE TABLE rides (
    ride_id             SERIAL PRIMARY KEY,
    customer_id         INTEGER NOT NULL REFERENCES customers(customer_id),
    driver_id           INTEGER NOT NULL REFERENCES drivers(driver_id),
    pickup_location_id  INTEGER NOT NULL REFERENCES locations(location_id),
    dropoff_location_id INTEGER NOT NULL REFERENCES locations(location_id),
    requested_at        TIMESTAMP NOT NULL,
    completed_at        TIMESTAMP,
    status              VARCHAR(20) NOT NULL CHECK (status IN ('completed','cancelled','ongoing')),
    distance_km         NUMERIC(6,2),
    fare_amount         NUMERIC(8,2)
);

CREATE TABLE payments (
    payment_id      SERIAL PRIMARY KEY,
    ride_id         INTEGER NOT NULL REFERENCES rides(ride_id),
    amount          NUMERIC(8,2) NOT NULL,
    payment_method  VARCHAR(30) NOT NULL CHECK (payment_method IN ('card','cash','wallet')),
    paid_at         TIMESTAMP NOT NULL
);

CREATE TABLE driver_ratings (
    rating_id       SERIAL PRIMARY KEY,
    ride_id         INTEGER NOT NULL REFERENCES rides(ride_id),
    driver_id       INTEGER NOT NULL REFERENCES drivers(driver_id),
    rating          SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment         TEXT
);

-- ============================================================
-- Sample Data
-- ============================================================

INSERT INTO locations (city, zone_name, latitude, longitude) VALUES
('Hyderabad', 'Gachibowli', 17.4400, 78.3489),
('Hyderabad', 'Banjara Hills', 17.4126, 78.4482),
('Hyderabad', 'Secunderabad', 17.4399, 78.4983),
('Hyderabad', 'HITEC City', 17.4483, 78.3915);

INSERT INTO customers (full_name, email, home_location_id) VALUES
('Asha Rao', 'asha.rao.cust1@example.com', 1),
('Vikram Shetty', 'vikram.shetty.cust2@example.com', 2),
('Meera Nair', 'meera.nair.cust3@example.com', 3);

INSERT INTO drivers (full_name, license_number, vehicle_type) VALUES
('Ramesh Kumar', 'LIC-1001', 'sedan'),
('Suresh Babu', 'LIC-1002', 'hatchback'),
('Farida Khan', 'LIC-1003', 'suv');

INSERT INTO rides (customer_id, driver_id, pickup_location_id, dropoff_location_id, requested_at, completed_at, status, distance_km, fare_amount) VALUES
(1, 1, 1, 4, '2026-09-01 08:00', '2026-09-01 08:25', 'completed', 6.2, 180.00),
(2, 2, 2, 3, '2026-09-02 09:15', '2026-09-02 09:40', 'completed', 8.1, 220.00),
(3, 3, 3, 1, '2026-09-03 18:30', NULL, 'cancelled', NULL, NULL),
(1, 2, 4, 2, '2026-09-04 20:00', '2026-09-04 20:35', 'completed', 10.4, 260.00);

INSERT INTO payments (ride_id, amount, payment_method, paid_at) VALUES
(1, 180.00, 'card', '2026-09-01 08:26'),
(2, 220.00, 'wallet', '2026-09-02 09:41'),
(4, 260.00, 'cash', '2026-09-04 20:36');

INSERT INTO driver_ratings (ride_id, driver_id, rating, comment) VALUES
(1, 1, 5, 'Smooth ride, polite driver'),
(2, 2, 4, 'Good, slightly late'),
(4, 2, 3, 'AC was not working well');