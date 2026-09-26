# Mobility Database — Data Dictionary

## locations
| Column | Type | Description |
|---|---|---|
| location_id | SERIAL (PK) | Unique identifier for a pickup/dropoff zone |
| city | VARCHAR(100) | City name |
| zone_name | VARCHAR(100) | Named area within the city |
| latitude | NUMERIC(9,6) | Zone latitude |
| longitude | NUMERIC(9,6) | Zone longitude |

## customers
| Column | Type | Description |
|---|---|---|
| customer_id | SERIAL (PK) | Unique customer identifier |
| full_name | VARCHAR(150) | Customer's name |
| email | VARCHAR(150), UNIQUE | Customer's email |
| signup_date | DATE | Date the customer joined |
| home_location_id | INTEGER (FK → locations) | Customer's usual pickup zone |

## drivers
| Column | Type | Description |
|---|---|---|
| driver_id | SERIAL (PK) | Unique driver identifier |
| full_name | VARCHAR(150) | Driver's name |
| license_number | VARCHAR(50), UNIQUE | Driver's license number |
| hire_date | DATE | Date the driver was onboarded |
| vehicle_type | VARCHAR(50) | sedan / hatchback / suv |

## rides
| Column | Type | Description |
|---|---|---|
| ride_id | SERIAL (PK) | Unique ride identifier |
| customer_id | INTEGER (FK → customers) | Who booked the ride |
| driver_id | INTEGER (FK → drivers) | Who completed the ride |
| pickup_location_id | INTEGER (FK → locations) | Where the ride started |
| dropoff_location_id | INTEGER (FK → locations) | Where the ride ended |
| requested_at | TIMESTAMP | When the ride was requested |
| completed_at | TIMESTAMP, nullable | When the ride finished (null if cancelled/ongoing) |
| status | VARCHAR(20) | completed / cancelled / ongoing |
| distance_km | NUMERIC(6,2), nullable | Trip distance |
| fare_amount | NUMERIC(8,2), nullable | Fare charged (null if not completed) |

## payments
| Column | Type | Description |
|---|---|---|
| payment_id | SERIAL (PK) | Unique payment identifier |
| ride_id | INTEGER (FK → rides) | Which ride this payment covers |
| amount | NUMERIC(8,2) | Amount paid |
| payment_method | VARCHAR(30) | card / cash / wallet |
| paid_at | TIMESTAMP | When payment was made |

## driver_ratings
| Column | Type | Description |
|---|---|---|
| rating_id | SERIAL (PK) | Unique rating identifier |
| ride_id | INTEGER (FK → rides) | Which ride is being rated |
| driver_id | INTEGER (FK → drivers) | Which driver is being rated |
| rating | SMALLINT (1–5) | Star rating |
| comment | TEXT, nullable | Optional customer comment |

## Relationships summary
`customers` and `drivers` are independent entities. A `ride` connects one customer, one driver, and two locations (pickup/dropoff). Each ride can have at most one `payment` and at most one `driver_rating` in this sample dataset.