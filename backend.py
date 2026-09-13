# backend.py - High-level API bridging database and services
import database

# Ensure database tables and seed data exist
database.init_db()

def search_flights(source, destination):
    """Search flights by origin and destination city or airport code."""
    return database.search_flights(source, destination)

def book_flight(name, flight_no, date, email="traveler@example.com", phone="+91 9876543210", seat_no=""):
    """Book a seat on a specific flight by flight number."""
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE flight_number = ?", (flight_no,))
    flight = cursor.fetchone()
    conn.close()

    if not flight or flight['available_seats'] <= 0:
        return None

    flight_dict = dict(flight)
    base_fare = flight_dict['price']
    taxes = round(base_fare * 0.12)
    total_price = base_fare + taxes

    booking_data = {
        "flight_id": flight_dict['id'],
        "passenger_name": name,
        "passenger_email": email,
        "passenger_phone": phone,
        "passengers_count": 1,
        "cabin_class": "Economy",
        "travel_date": date,
        "seat_numbers": seat_no or "Auto",
        "meal_preferences": "Standard Meal",
        "add_on_luggage": 0,
        "travel_insurance": 0,
        "base_fare": base_fare,
        "taxes": taxes,
        "add_on_fee": 0,
        "discount": 0,
        "coupon_code": "",
        "total_price": total_price,
        "payment_method": "Credit Card"
    }

    passengers_list = [{
        "title": "Mr",
        "first_name": name.split()[0] if name.split() else name,
        "last_name": name.split()[-1] if len(name.split()) > 1 else "",
        "age": 30,
        "gender": "Male",
        "seat_number": seat_no or "Auto",
        "meal": "Standard Meal"
    }]

    pnr = database.create_booking(booking_data, passengers_list)
    return database.get_booking_by_pnr(pnr)

def cancel_booking(pnr_or_name, flight_no=None):
    """Cancel booking by PNR reference or by passenger name."""
    if pnr_or_name.startswith("SKY-"):
        success, _ = database.cancel_booking(pnr_or_name)
        return success
    
    # Fallback to lookup by name
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT pnr FROM bookings WHERE passenger_name = ? AND booking_status != 'Cancelled'", (pnr_or_name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        success, _ = database.cancel_booking(row['pnr'])
        return success
    return False
