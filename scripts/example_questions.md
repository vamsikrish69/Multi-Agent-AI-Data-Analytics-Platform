# Example Business Questions (for testing the SQL Analyst agent later)

1. **"How many rides were completed vs cancelled?"**
   Expected: 3 completed, 1 cancelled (based on current seed data)

2. **"What is the total revenue collected so far?"**
   Expected: 660.00 (180 + 220 + 260, summed from `payments`)

3. **"Which driver has the highest average rating?"**
   Expected: Ramesh Kumar (single 5-star rating) — a tie-breaking rule will matter once more data exists

4. **"Which customer has taken the most rides?"**
   Expected: Asha Rao (2 rides)

5. **"What is the most common payment method?"**
   Expected: tie between card, wallet, cash (1 each) — good adversarial/ambiguous test case once more data is added

6. **"Show all rides that were cancelled and had no payment."**
   Expected: ride_id 3 (Meera Nair / Farida Khan)