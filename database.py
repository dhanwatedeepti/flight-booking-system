import sqlite3
import os
import random
import string
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(__file__), "flights.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Create airports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS airports (
            code TEXT PRIMARY KEY,
            city TEXT NOT NULL,
            name TEXT NOT NULL,
            country TEXT NOT NULL
        )
    """)

    # Create flights table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_number TEXT NOT NULL,
            airline TEXT NOT NULL,
            airline_code TEXT NOT NULL,
            origin_code TEXT NOT NULL,
            origin_city TEXT NOT NULL,
            destination_code TEXT NOT NULL,
            destination_city TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            duration TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            price INTEGER NOT NULL,
            stops INTEGER DEFAULT 0,
            layover TEXT DEFAULT 'Non-stop',
            aircraft TEXT NOT NULL,
            baggage_checkin TEXT DEFAULT '15 kg',
            baggage_cabin TEXT DEFAULT '7 kg',
            total_seats INTEGER DEFAULT 60,
            available_seats INTEGER DEFAULT 45,
            FOREIGN KEY (origin_code) REFERENCES airports(code),
            FOREIGN KEY (destination_code) REFERENCES airports(code)
        )
    """)

    # Create bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pnr TEXT UNIQUE NOT NULL,
            flight_id INTEGER NOT NULL,
            passenger_name TEXT NOT NULL,
            passenger_email TEXT NOT NULL,
            passenger_phone TEXT NOT NULL,
            passengers_count INTEGER NOT NULL DEFAULT 1,
            cabin_class TEXT NOT NULL DEFAULT 'Economy',
            travel_date TEXT NOT NULL,
            seat_numbers TEXT,
            meal_preferences TEXT,
            add_on_luggage INTEGER DEFAULT 0,
            travel_insurance INTEGER DEFAULT 0,
            base_fare REAL NOT NULL,
            taxes REAL NOT NULL,
            add_on_fee REAL DEFAULT 0,
            discount REAL DEFAULT 0,
            coupon_code TEXT,
            total_price REAL NOT NULL,
            payment_method TEXT DEFAULT 'Credit Card',
            payment_status TEXT DEFAULT 'Pending',
            booking_status TEXT DEFAULT 'Confirmed',
            terminal TEXT DEFAULT 'T2',
            gate TEXT DEFAULT '12B',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (flight_id) REFERENCES flights(id)
        )
    """)

    # Create individual passengers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passengers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            title TEXT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            seat_number TEXT,
            meal TEXT,
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        )
    """)

    # Create coupons table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coupons (
            code TEXT PRIMARY KEY,
            discount_percent INTEGER DEFAULT 0,
            flat_discount INTEGER DEFAULT 0,
            max_discount INTEGER DEFAULT 0,
            min_fare INTEGER DEFAULT 0,
            description TEXT NOT NULL
        )
    """)

    conn.commit()

    # Check if seed data exists
    cursor.execute("SELECT COUNT(*) FROM airports")
    if cursor.fetchone()[0] == 0:
        seed_data(cursor)
        conn.commit()

    conn.close()

def seed_data(cursor):
    # Seed airports
    airports = [
        ("DEL", "Delhi", "Indira Gandhi International Airport", "India"),
        ("BOM", "Mumbai", "Chhatrapati Shivaji Maharaj International Airport", "India"),
        ("BLR", "Bangalore", "Kempegowda International Airport", "India"),
        ("PNQ", "Pune", "Pune International Airport", "India"),
        ("HYD", "Hyderabad", "Rajiv Gandhi International Airport", "India"),
        ("MAA", "Chennai", "Chennai International Airport", "India"),
        ("CCU", "Kolkata", "Netaji Subhash Chandra Bose International Airport", "India"),
        ("GOI", "Goa", "Dabolim / Manohar International Airport", "India"),
        ("JAI", "Jaipur", "Jaipur International Airport", "India"),
        ("COK", "Kochi", "Cochin International Airport", "India"),
        ("AMD", "Ahmedabad", "Sardar Vallabhbhai Patel International Airport", "India"),
        ("DXB", "Dubai", "Dubai International Airport", "United Arab Emirates"),
        ("SIN", "Singapore", "Singapore Changi Airport", "Singapore"),
        ("LHR", "London", "Heathrow Airport", "United Kingdom")
    ]
    cursor.executemany("INSERT INTO airports VALUES (?, ?, ?, ?)", airports)

    # Seed coupons
    coupons = [
        ("FLYHIGH", 15, 0, 1200, 3000, "15% off up to ₹1,200 on domestic & international flights"),
        ("SKY500", 0, 500, 500, 2500, "Flat ₹500 off on all bookings above ₹2,500"),
        ("FIRSTFLY", 20, 0, 1500, 3500, "20% off up to ₹1,500 for first time travelers"),
        ("FESTIVE", 10, 0, 800, 2000, "10% off up to ₹800 festival special discount")
    ]
    cursor.executemany("INSERT INTO coupons VALUES (?, ?, ?, ?, ?, ?)", coupons)

    # Seed realistic flights across major routes
    flights_data = [
        # Pune -> Delhi
        ("6E-205", "IndiGo", "6E", "PNQ", "Pune", "DEL", "Delhi", "06:15", "08:25", "2h 10m", 130, 3450, 0, "Non-stop", "Airbus A320neo", "15 kg", "7 kg", 60, 42),
        ("AI-852", "Air India", "AI", "PNQ", "Pune", "DEL", "Delhi", "08:45", "11:00", "2h 15m", 135, 3890, 0, "Non-stop", "Boeing 787-8", "25 kg", "7 kg", 60, 38),
        ("UK-992", "Vistara", "UK", "PNQ", "Pune", "DEL", "Delhi", "14:20", "16:35", "2h 15m", 135, 4200, 0, "Non-stop", "Airbus A321neo", "20 kg", "7 kg", 60, 25),
        ("QP-1304", "Akasa Air", "QP", "PNQ", "Pune", "DEL", "Delhi", "19:10", "21:25", "2h 15m", 135, 3299, 0, "Non-stop", "Boeing 737 MAX 8", "15 kg", "7 kg", 60, 50),
        ("SG-8114", "SpiceJet", "SG", "PNQ", "Pune", "DEL", "Delhi", "11:30", "15:45", "4h 15m", 255, 2950, 1, "1 stop via BOM (1h 10m)", "Boeing 737-800", "15 kg", "7 kg", 60, 30),

        # Delhi -> Pune
        ("6E-206", "IndiGo", "6E", "DEL", "Delhi", "PNQ", "Pune", "09:10", "11:20", "2h 10m", 130, 3550, 0, "Non-stop", "Airbus A320neo", "15 kg", "7 kg", 60, 44),
        ("AI-853", "Air India", "AI", "DEL", "Delhi", "PNQ", "Pune", "17:30", "19:45", "2h 15m", 135, 3950, 0, "Non-stop", "Boeing 787-8", "25 kg", "7 kg", 60, 35),
        ("UK-993", "Vistara", "UK", "DEL", "Delhi", "PNQ", "Pune", "20:15", "22:30", "2h 15m", 135, 4350, 0, "Non-stop", "Airbus A321neo", "20 kg", "7 kg", 60, 28),

        # Mumbai -> Bangalore
        ("6E-451", "IndiGo", "6E", "BOM", "Mumbai", "BLR", "Bangalore", "06:00", "07:45", "1h 45m", 105, 3100, 0, "Non-stop", "Airbus A320neo", "15 kg", "7 kg", 60, 48),
        ("AI-607", "Air India", "AI", "BOM", "Mumbai", "BLR", "Bangalore", "10:30", "12:15", "1h 45m", 105, 3600, 0, "Non-stop", "Airbus A320", "25 kg", "7 kg", 60, 34),
        ("UK-861", "Vistara", "UK", "BOM", "Mumbai", "BLR", "Bangalore", "16:00", "17:50", "1h 50m", 110, 4100, 0, "Non-stop", "Airbus A321neo", "20 kg", "7 kg", 60, 29),
        ("QP-1120", "Akasa Air", "QP", "BOM", "Mumbai", "BLR", "Bangalore", "21:15", "23:00", "1h 45m", 105, 2850, 0, "Non-stop", "Boeing 737 MAX 8", "15 kg", "7 kg", 60, 52),

        # Bangalore -> Mumbai
        ("6E-452", "IndiGo", "6E", "BLR", "Bangalore", "BOM", "Mumbai", "08:30", "10:15", "1h 45m", 105, 3200, 0, "Non-stop", "Airbus A320neo", "15 kg", "7 kg", 60, 45),
        ("UK-862", "Vistara", "UK", "BLR", "Bangalore", "BOM", "Mumbai", "18:45", "20:35", "1h 50m", 110, 4250, 0, "Non-stop", "Airbus A321neo", "20 kg", "7 kg", 60, 31),

        # Mumbai -> Delhi
        ("AI-102", "Air India", "AI", "BOM", "Mumbai", "DEL", "Delhi", "07:00", "09:10", "2h 10m", 130, 4100, 0, "Non-stop", "Boeing 777-300ER", "25 kg", "7 kg", 60, 40),
        ("6E-5011", "IndiGo", "6E", "BOM", "Mumbai", "DEL", "Delhi", "13:15", "15:25", "2h 10m", 130, 3750, 0, "Non-stop", "Airbus A321neo", "15 kg", "7 kg", 60, 36),
        ("UK-970", "Vistara", "UK", "BOM", "Mumbai", "DEL", "Delhi", "19:40", "21:55", "2h 15m", 135, 4600, 0, "Non-stop", "Boeing 787-9 Dreamliner", "20 kg", "7 kg", 60, 22),

        # Delhi -> Mumbai
        ("6E-5012", "IndiGo", "6E", "DEL", "Delhi", "BOM", "Mumbai", "06:30", "08:40", "2h 10m", 130, 3800, 0, "Non-stop", "Airbus A321neo", "15 kg", "7 kg", 60, 41),
        ("AI-101", "Air India", "AI", "DEL", "Delhi", "BOM", "Mumbai", "15:00", "17:15", "2h 15m", 135, 4250, 0, "Non-stop", "Boeing 777-300ER", "25 kg", "7 kg", 60, 38),

        # Hyderabad -> Chennai
        ("6E-711", "IndiGo", "6E", "HYD", "Hyderabad", "MAA", "Chennai", "07:15", "08:30", "1h 15m", 75, 2750, 0, "Non-stop", "ATR 72-600", "15 kg", "7 kg", 60, 47),
        ("AI-542", "Air India", "AI", "HYD", "Hyderabad", "MAA", "Chennai", "14:40", "15:55", "1h 15m", 75, 3100, 0, "Non-stop", "Airbus A320", "25 kg", "7 kg", 60, 39),
        ("SG-302", "SpiceJet", "SG", "HYD", "Hyderabad", "MAA", "Chennai", "20:10", "21:30", "1h 20m", 80, 2450, 0, "Non-stop", "Boeing 737-700", "15 kg", "7 kg", 60, 33),

        # Chennai -> Hyderabad
        ("6E-712", "IndiGo", "6E", "MAA", "Chennai", "HYD", "Hyderabad", "09:15", "10:30", "1h 15m", 75, 2800, 0, "Non-stop", "ATR 72-600", "15 kg", "7 kg", 60, 44),

        # Bangalore -> Goa
        ("6E-618", "IndiGo", "6E", "BLR", "Bangalore", "GOI", "Goa", "11:00", "12:15", "1h 15m", 75, 2600, 0, "Non-stop", "Airbus A320neo", "15 kg", "7 kg", 60, 49),
        ("QP-1450", "Akasa Air", "QP", "BLR", "Bangalore", "GOI", "Goa", "16:45", "18:00", "1h 15m", 75, 2350, 0, "Non-stop", "Boeing 737 MAX 8", "15 kg", "7 kg", 60, 55),

        # Goa -> Bangalore
        ("6E-619", "IndiGo", "6E", "GOI", "Goa", "BLR", "Bangalore", "13:00", "14:15", "1h 15m", 75, 2650, 0, "Non-stop", "Airbus A320neo", "15 kg", "7 kg", 60, 46),

        # Kolkata -> Delhi
        ("6E-314", "IndiGo", "6E", "CCU", "Kolkata", "DEL", "Delhi", "06:45", "09:05", "2h 20m", 140, 3900, 0, "Non-stop", "Airbus A320neo", "15 kg", "7 kg", 60, 37),
        ("AI-701", "Air India", "AI", "CCU", "Kolkata", "DEL", "Delhi", "18:30", "20:50", "2h 20m", 140, 4300, 0, "Non-stop", "Airbus A321", "25 kg", "7 kg", 60, 26),

        # Mumbai -> Dubai (International)
        ("EK-501", "Emirates", "EK", "BOM", "Mumbai", "DXB", "Dubai", "04:30", "06:15", "3h 15m", 195, 14200, 0, "Non-stop", "Boeing 777-300ER", "30 kg", "7 kg", 60, 20),
        ("AI-983", "Air India", "AI", "BOM", "Mumbai", "DXB", "Dubai", "19:00", "20:50", "3h 20m", 200, 11800, 0, "Non-stop", "Boeing 787-8", "30 kg", "7 kg", 60, 28),
        ("6E-1455", "IndiGo", "6E", "BOM", "Mumbai", "DXB", "Dubai", "22:15", "00:10", "3h 25m", 205, 9900, 0, "Non-stop", "Airbus A321neo", "20 kg", "7 kg", 60, 32),

        # Delhi -> Singapore (International)
        ("SQ-403", "Singapore Airlines", "SQ", "DEL", "Delhi", "SIN", "Singapore", "09:50", "18:10", "5h 50m", 350, 18500, 0, "Non-stop", "Airbus A380-800", "30 kg", "7 kg", 60, 18),
        ("AI-382", "Air India", "AI", "DEL", "Delhi", "SIN", "Singapore", "23:05", "07:25", "5h 50m", 350, 15200, 0, "Non-stop", "Boeing 787-8", "25 kg", "7 kg", 60, 24),

        # Delhi -> London Heathrow (International)
        ("AI-161", "Air India", "AI", "DEL", "Delhi", "LHR", "London", "02:45", "07:30", "9h 15m", 555, 38500, 0, "Non-stop", "Boeing 777-300ER", "35 kg", "7 kg", 60, 15),
        ("BA-142", "British Airways", "BA", "DEL", "Delhi", "LHR", "London", "10:15", "15:20", "9h 35m", 575, 42000, 0, "Non-stop", "Boeing 787-9", "32 kg", "7 kg", 60, 12),

        # Pune -> Bangalore
        ("6E-582", "IndiGo", "6E", "PNQ", "Pune", "BLR", "Bangalore", "08:15", "09:40", "1h 25m", 85, 2900, 0, "Non-stop", "Airbus A320neo", "15 kg", "7 kg", 60, 40),
        ("AI-518", "Air India", "AI", "PNQ", "Pune", "BLR", "Bangalore", "18:30", "19:55", "1h 25m", 85, 3350, 0, "Non-stop", "Airbus A320", "25 kg", "7 kg", 60, 35),

        # Bangalore -> Pune
        ("6E-583", "IndiGo", "6E", "BLR", "Bangalore", "PNQ", "Pune", "16:10", "17:35", "1h 25m", 85, 2950, 0, "Non-stop", "Airbus A320neo", "15 kg", "7 kg", 60, 42),
    ]

    cursor.executemany("""
        INSERT INTO flights (
            flight_number, airline, airline_code, origin_code, origin_city, 
            destination_code, destination_city, departure_time, arrival_time, 
            duration, duration_minutes, price, stops, layover, aircraft, 
            baggage_checkin, baggage_cabin, total_seats, available_seats
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, flights_data)

# Query functions
def get_all_airports():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM airports ORDER BY city ASC")
    airports = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return airports

def search_airports(query):
    conn = get_db()
    cursor = conn.cursor()
    pattern = f"%{query.strip()}%"
    cursor.execute("""
        SELECT * FROM airports 
        WHERE code LIKE ? OR city LIKE ? OR name LIKE ?
        ORDER BY city ASC LIMIT 10
    """, (pattern, pattern, pattern))
    airports = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return airports

def search_flights(origin, destination, max_price=None, airlines=None, stops=None, time_slot=None, sort_by='cheapest'):
    conn = get_db()
    cursor = conn.cursor()

    origin = origin.strip().upper()
    dest = destination.strip().upper()

    query = """
        SELECT * FROM flights 
        WHERE (origin_code = ? OR UPPER(origin_city) = ?) 
          AND (destination_code = ? OR UPPER(destination_city) = ?)
    """
    params = [origin, origin, dest, dest]

    if max_price:
        query += " AND price <= ?"
        params.append(int(max_price))

    if airlines and len(airlines) > 0:
        placeholders = ','.join('?' for _ in airlines)
        query += f" AND airline IN ({placeholders})"
        params.extend(airlines)

    if stops is not None and stops != "":
        query += " AND stops = ?"
        params.append(int(stops))

    if time_slot:
        if time_slot == 'early_morning': # Before 6 AM
            query += " AND departure_time < '06:00'"
        elif time_slot == 'morning': # 6 AM to 12 PM
            query += " AND departure_time >= '06:00' AND departure_time < '12:00'"
        elif time_slot == 'afternoon': # 12 PM to 6 PM
            query += " AND departure_time >= '12:00' AND departure_time < '18:00'"
        elif time_slot == 'evening': # After 6 PM
            query += " AND departure_time >= '18:00'"

    # Sorting
    if sort_by == 'cheapest':
        query += " ORDER BY price ASC"
    elif sort_by == 'fastest':
        query += " ORDER BY duration_minutes ASC"
    elif sort_by == 'earliest':
        query += " ORDER BY departure_time ASC"
    elif sort_by == 'latest':
        query += " ORDER BY departure_time DESC"
    else:
        query += " ORDER BY price ASC"

    cursor.execute(query, params)
    flights = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return flights

def get_flight_by_id(flight_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE id = ?", (flight_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_coupon(code):
    if not code:
        return None
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coupons WHERE UPPER(code) = ?", (code.strip().upper(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def generate_pnr():
    chars = string.ascii_uppercase + string.digits
    while True:
        pnr = "SKY-" + ''.join(random.choices(chars, k=6))
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM bookings WHERE pnr = ?", (pnr,))
        if not cursor.fetchone():
            conn.close()
            return pnr
        conn.close()

def get_occupied_seats(flight_id, travel_date):
    """Returns occupied seat numbers for a given flight and travel date."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT seat_numbers FROM bookings 
        WHERE flight_id = ? AND travel_date = ? AND booking_status != 'Cancelled'
    """, (flight_id, travel_date))
    rows = cursor.fetchall()
    conn.close()
    
    occupied = set()
    for row in rows:
        if row['seat_numbers']:
            for s in row['seat_numbers'].split(','):
                s_clean = s.strip()
                if s_clean:
                    occupied.add(s_clean)
    
    # Pre-populate some realistic occupied seats if none booked yet
    if len(occupied) < 10:
        default_occupied = ["1B", "2E", "3C", "4D", "5A", "6F", "7B", "8E", "9A", "10C"]
        for s in default_occupied:
            occupied.add(s)
            
    return sorted(list(occupied))

def create_booking(booking_data, passengers_list):
    conn = get_db()
    cursor = conn.cursor()

    pnr = generate_pnr()
    terminal = random.choice(["T1", "T2", "T3"])
    gate = f"{random.randint(1, 25)}{random.choice(['A', 'B', 'C'])}"

    cursor.execute("""
        INSERT INTO bookings (
            pnr, flight_id, passenger_name, passenger_email, passenger_phone,
            passengers_count, cabin_class, travel_date, seat_numbers, meal_preferences,
            add_on_luggage, travel_insurance, base_fare, taxes, add_on_fee,
            discount, coupon_code, total_price, payment_method, payment_status,
            booking_status, terminal, gate
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        pnr,
        booking_data['flight_id'],
        booking_data['passenger_name'],
        booking_data['passenger_email'],
        booking_data['passenger_phone'],
        booking_data.get('passengers_count', 1),
        booking_data.get('cabin_class', 'Economy'),
        booking_data['travel_date'],
        booking_data.get('seat_numbers', ''),
        booking_data.get('meal_preferences', 'Standard Meal'),
        booking_data.get('add_on_luggage', 0),
        booking_data.get('travel_insurance', 0),
        booking_data['base_fare'],
        booking_data['taxes'],
        booking_data.get('add_on_fee', 0),
        booking_data.get('discount', 0),
        booking_data.get('coupon_code', ''),
        booking_data['total_price'],
        booking_data.get('payment_method', 'Credit Card'),
        'Pending',
        'Confirmed',
        terminal,
        gate
    ))

    booking_id = cursor.lastrowid

    # Insert individual passengers
    for p in passengers_list:
        cursor.execute("""
            INSERT INTO passengers (
                booking_id, title, first_name, last_name, age, gender, seat_number, meal
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            booking_id,
            p.get('title', 'Mr'),
            p.get('first_name', ''),
            p.get('last_name', ''),
            p.get('age', 30),
            p.get('gender', 'Male'),
            p.get('seat_number', ''),
            p.get('meal', 'Standard Veg')
        ))

    # Reduce available seats on flight
    cursor.execute("""
        UPDATE flights 
        SET available_seats = MAX(0, available_seats - ?) 
        WHERE id = ?
    """, (booking_data.get('passengers_count', 1), booking_data['flight_id']))

    conn.commit()
    conn.close()
    return pnr

def update_payment_status(pnr, payment_method, status='Completed'):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE bookings 
        SET payment_status = ?, payment_method = ? 
        WHERE pnr = ?
    """, (status, payment_method, pnr))
    conn.commit()
    conn.close()

def get_booking_by_pnr(pnr):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.*, f.flight_number, f.airline, f.airline_code, f.origin_code, f.origin_city,
               f.destination_code, f.destination_city, f.departure_time, f.arrival_time,
               f.duration, f.aircraft, f.baggage_checkin, f.baggage_cabin
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        WHERE UPPER(b.pnr) = ?
    """, (pnr.strip().upper(),))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    booking = dict(row)
    # Fetch passengers
    cursor.execute("SELECT * FROM passengers WHERE booking_id = ?", (booking['id'],))
    booking['passengers'] = [dict(p) for p in cursor.fetchall()]
    conn.close()
    return booking

def get_bookings_by_query(query_str):
    """Find bookings by PNR or Email."""
    conn = get_db()
    cursor = conn.cursor()
    val = query_str.strip().upper()
    email_val = query_str.strip().lower()

    cursor.execute("""
        SELECT b.*, f.flight_number, f.airline, f.airline_code, f.origin_code, f.origin_city,
               f.destination_code, f.destination_city, f.departure_time, f.arrival_time,
               f.duration, f.aircraft
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        WHERE UPPER(b.pnr) = ? OR LOWER(b.passenger_email) = ?
        ORDER BY b.created_at DESC
    """, (val, email_val))
    rows = cursor.fetchall()
    
    results = []
    for r in rows:
        b = dict(r)
        cursor.execute("SELECT * FROM passengers WHERE booking_id = ?", (b['id'],))
        b['passengers'] = [dict(p) for p in cursor.fetchall()]
        results.append(b)
        
    conn.close()
    return results

def cancel_booking(pnr):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE UPPER(pnr) = ?", (pnr.strip().upper(),))
    booking = cursor.fetchone()
    if not booking:
        conn.close()
        return False, "Booking not found."
    
    if booking['booking_status'] == 'Cancelled':
        conn.close()
        return False, "Booking is already cancelled."

    cursor.execute("UPDATE bookings SET booking_status = 'Cancelled' WHERE pnr = ?", (pnr.strip().upper(),))
    
    # Restore seat count
    cursor.execute("""
        UPDATE flights 
        SET available_seats = MIN(total_seats, available_seats + ?) 
        WHERE id = ?
    """, (booking['passengers_count'], booking['flight_id']))

    conn.commit()
    conn.close()
    
    refund_amount = round(booking['total_price'] * 0.85, 2)
    return True, f"Booking {pnr} successfully cancelled. Refund of ₹{refund_amount:,.2f} initiated to original payment method."

def get_all_recent_bookings():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.*, f.flight_number, f.airline, f.origin_code, f.origin_city,
               f.destination_code, f.destination_city, f.departure_time, f.arrival_time
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        ORDER BY b.id DESC LIMIT 10
    """)
    bookings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return bookings
