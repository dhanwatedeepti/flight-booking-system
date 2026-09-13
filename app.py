from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
import database

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "skywings_secret_super_secure_key"

# Initialize SQLite database and seed records on startup
database.init_db()

@app.route('/')
def index():
    default_from = request.args.get('from', 'Pune')
    default_to = request.args.get('to', 'Delhi')
    return render_template("index.html", default_from=default_from, default_to=default_to)

@app.route('/search', methods=["GET", "POST"])
def search():
    if request.method == "POST":
        from_city = request.form.get("from", "").strip()
        to_city = request.form.get("to", "").strip()
        travel_date = request.form.get("date", date.today().isoformat())
        return_date = request.form.get("return_date", "")
        trip_type = request.form.get("trip_type", "one_way")
        passengers = int(request.form.get("passengers", "1").split('_')[0])
        cabin_class = "Business" if "business" in str(request.form.get("passengers", "")) else "Economy"
    else:
        from_city = request.args.get("from", "Pune").strip()
        to_city = request.args.get("to", "Delhi").strip()
        travel_date = request.args.get("date", date.today().isoformat())
        return_date = request.args.get("return_date", "")
        trip_type = request.args.get("trip_type", "one_way")
        passengers_param = request.args.get("passengers", "1")
        passengers = int(passengers_param.split('_')[0]) if passengers_param else 1
        cabin_class = "Business" if "business" in passengers_param else "Economy"

    # Search flights in database
    results = database.search_flights(from_city, to_city)

    # Adjust base price for Business class if selected
    if cabin_class == "Business":
        for f in results:
            f['price'] = int(f['price'] * 2.2)

    return render_template(
        "results.html",
        results=results,
        from_city=from_city,
        to_city=to_city,
        travel_date=travel_date,
        return_date=return_date,
        trip_type=trip_type,
        passengers=passengers,
        cabin_class=cabin_class
    )

@app.route('/api/airports')
def api_airports():
    query = request.args.get('q', '')
    if query:
        airports = database.search_airports(query)
    else:
        airports = database.get_all_airports()
    return jsonify(airports)

@app.route('/book/<int:flight_id>', methods=["GET", "POST"])
def book(flight_id):
    flight = database.get_flight_by_id(flight_id)
    if not flight:
        flash("Flight not found or invalid flight ID.", "error")
        return redirect(url_for("index"))

    travel_date = request.args.get('date') or request.form.get('travel_date') or date.today().isoformat()
    passengers_count = int(request.args.get('passengers', '1')) if request.method == 'GET' else int(request.form.get('passengers_count', '1'))
    cabin_class = request.args.get('cabin_class', 'Economy') if request.method == 'GET' else request.form.get('cabin_class', 'Economy')

    if cabin_class == "Business":
        flight['price'] = int(flight['price'] * 2.2)

    if request.method == "POST":
        # Parse Passenger Details
        p_first = request.form.get("p_first_1", "").strip()
        p_last = request.form.get("p_last_1", "").strip()
        contact_name = f"{p_first} {p_last}".strip() or "Primary Traveler"
        contact_email = request.form.get("email", "").strip()
        contact_phone = request.form.get("phone", "").strip()

        passengers_list = []
        for i in range(1, passengers_count + 1):
            p_title = request.form.get(f"p_title_{i}", "Mr")
            pf = request.form.get(f"p_first_{i}", "").strip()
            pl = request.form.get(f"p_last_{i}", "").strip()
            page = int(request.form.get(f"p_age_{i}", 28) or 28)
            pgender = request.form.get(f"p_gender_{i}", "Male")
            passengers_list.append({
                "title": p_title,
                "first_name": pf,
                "last_name": pl,
                "age": page,
                "gender": pgender,
                "seat_number": "",
                "meal": "Standard Meal"
            })

        # Process Seat Selection
        selected_seats_str = request.form.get("selected_seats", "").strip()
        if selected_seats_str:
            seat_tokens = [s.strip() for s in selected_seats_str.split(',') if s.strip()]
            for idx, p in enumerate(passengers_list):
                if idx < len(seat_tokens):
                    p['seat_number'] = seat_tokens[idx]

        # Financial Calculations
        base_fare = flight['price'] * passengers_count
        taxes = round(base_fare * 0.12, 2)
        add_on_fee = float(request.form.get("add_on_fee", 0))
        discount = float(request.form.get("discount", 0))
        coupon_code = request.form.get("coupon_code", "").strip().upper()
        total_price = float(request.form.get("total_price", base_fare + taxes + add_on_fee - discount))

        # Selected Meals
        meals_selected = request.form.getlist("meals")
        meals_str = ", ".join(meals_selected) if meals_selected else "Standard Meal"

        # Baggage & Insurance
        add_on_luggage = int(request.form.get("extra_luggage", 0) or 0)
        travel_insurance = int(request.form.get("insurance", 0) or 0)

        booking_data = {
            "flight_id": flight_id,
            "passenger_name": contact_name,
            "passenger_email": contact_email,
            "passenger_phone": contact_phone,
            "passengers_count": passengers_count,
            "cabin_class": cabin_class,
            "travel_date": travel_date,
            "seat_numbers": selected_seats_str,
            "meal_preferences": meals_str,
            "add_on_luggage": add_on_luggage,
            "travel_insurance": travel_insurance,
            "base_fare": base_fare,
            "taxes": taxes,
            "add_on_fee": add_on_fee,
            "discount": discount,
            "coupon_code": coupon_code,
            "total_price": total_price
        }

        pnr = database.create_booking(booking_data, passengers_list)
        return redirect(url_for("payment", pnr=pnr))

    # Fetch occupied seats for this flight and date
    occupied_seats = database.get_occupied_seats(flight_id, travel_date)
    base_fare = flight['price'] * passengers_count
    taxes = round(base_fare * 0.12)
    total_initial_price = base_fare + taxes

    return render_template(
        "book.html",
        flight=flight,
        travel_date=travel_date,
        passengers_count=passengers_count,
        cabin_class=cabin_class,
        occupied_seats=occupied_seats,
        total_initial_price=total_initial_price
    )

@app.route('/payment/<pnr>')
def payment(pnr):
    booking = database.get_booking_by_pnr(pnr)
    if not booking:
        flash("Booking not found.", "error")
        return redirect(url_for("my_bookings"))
    
    if booking['payment_status'] == 'Completed':
        return redirect(url_for("ticket", pnr=pnr))

    return render_template("payment.html", booking=booking)

@app.route('/process-payment/<pnr>', methods=["POST"])
def process_payment(pnr):
    booking = database.get_booking_by_pnr(pnr)
    if not booking:
        flash("Booking reference not found.", "error")
        return redirect(url_for("my_bookings"))

    payment_method = request.form.get("payment_method", "Credit / Debit Card")
    database.update_payment_status(pnr, payment_method, status='Completed')

    flash(f"🎉 Payment successful! Flight {booking['flight_number']} booked for {booking['passenger_name']}.", "success")
    return redirect(url_for("ticket", pnr=pnr))

@app.route('/ticket/<pnr>')
def ticket(pnr):
    booking = database.get_booking_by_pnr(pnr)
    if not booking:
        flash("Boarding pass not found for PNR: " + pnr, "error")
        return redirect(url_for("my_bookings"))
    
    return render_template("ticket.html", booking=booking)

@app.route('/my-bookings')
def my_bookings():
    search_query = request.args.get('q', '').strip()
    if search_query:
        bookings = database.get_bookings_by_query(search_query)
    else:
        bookings = database.get_all_recent_bookings()

    return render_template("my_bookings.html", bookings=bookings, search_query=search_query)

@app.route('/cancel-booking/<pnr>', methods=["POST"])
def cancel_flight_booking(pnr):
    success, message = database.cancel_booking(pnr)
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for("my_bookings", q=pnr))

@app.route('/deals')
def deals():
    return render_template("deals.html")

# Legacy routes backward compatibility
@app.route('/success')
def success():
    return redirect(url_for("my_bookings"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
