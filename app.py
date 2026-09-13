from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime, date
import database
import email_service

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "skywings_secret_super_secure_key_2026"

# Initialize SQLite database and seed records on startup
database.init_db()

CLASS_MULTIPLIERS = {
    "Economy": 1.0,
    "Premium Economy": 1.4,
    "Business": 2.2,
    "First Class": 3.5
}

CONCESSION_DISCOUNTS = {
    "Regular": 0.0,
    "Student": 0.10,        # 10% off + free 10kg baggage
    "Senior Citizen": 0.10, # 10% off (60+ yrs)
    "Armed Forces": 0.15    # 15% off
}

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
        passengers = int(request.form.get("passengers", "1"))
        cabin_class = request.form.get("cabin_class", "Economy")
        fare_type = request.form.get("fare_type", "Regular")
    else:
        from_city = request.args.get("from", "Pune").strip()
        to_city = request.args.get("to", "Delhi").strip()
        travel_date = request.args.get("date", date.today().isoformat())
        return_date = request.args.get("return_date", "")
        trip_type = request.args.get("trip_type", "one_way")
        passengers = int(request.args.get("passengers", "1"))
        cabin_class = request.args.get("cabin_class", "Economy")
        fare_type = request.args.get("fare_type", "Regular")

    # Search flights in database
    results = database.search_flights(from_city, to_city)

    # Adjust prices based on cabin class and special concessions
    class_mult = CLASS_MULTIPLIERS.get(cabin_class, 1.0)
    concession_rate = CONCESSION_DISCOUNTS.get(fare_type, 0.0)

    for f in results:
        adjusted_base = int(f['price'] * class_mult)
        concession_off = int(adjusted_base * concession_rate)
        f['price'] = max(500, adjusted_base - concession_off)

    return render_template(
        "results.html",
        results=results,
        from_city=from_city,
        to_city=to_city,
        travel_date=travel_date,
        return_date=return_date,
        trip_type=trip_type,
        passengers=passengers,
        cabin_class=cabin_class,
        fare_type=fare_type
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
    fare_type = request.args.get('fare_type', 'Regular') if request.method == 'GET' else request.form.get('fare_type', 'Regular')

    class_mult = CLASS_MULTIPLIERS.get(cabin_class, 1.0)
    concession_rate = CONCESSION_DISCOUNTS.get(fare_type, 0.0)
    adjusted_price = int(flight['price'] * class_mult)
    flight['price'] = adjusted_price

    base_fare = adjusted_price * passengers_count
    concession_discount = int(base_fare * concession_rate)

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
        taxes = round((base_fare - concession_discount) * 0.12, 2)
        add_on_fee = float(request.form.get("add_on_fee", 0))
        user_discount = float(request.form.get("discount", 0))
        total_discount = concession_discount + user_discount
        coupon_code = request.form.get("coupon_code", "").strip().upper()
        total_price = float(request.form.get("total_price", max(0, base_fare + taxes + add_on_fee - total_discount)))

        # Selected Meals
        meals_selected = request.form.getlist("meals")
        meals_str = ", ".join(meals_selected) if meals_selected else "Standard Meal"

        # Baggage & Insurance
        add_on_luggage = int(request.form.get("extra_luggage", 0) or 0)
        # Student perk: if student, +10kg is complimentary
        if fare_type == 'Student':
            add_on_luggage += 10

        travel_insurance = int(request.form.get("insurance", 0) or 0)

        booking_data = {
            "flight_id": flight_id,
            "passenger_name": contact_name,
            "passenger_email": contact_email,
            "passenger_phone": contact_phone,
            "passengers_count": passengers_count,
            "cabin_class": cabin_class,
            "fare_type": fare_type,
            "travel_date": travel_date,
            "seat_numbers": selected_seats_str,
            "meal_preferences": meals_str,
            "add_on_luggage": add_on_luggage,
            "travel_insurance": travel_insurance,
            "base_fare": base_fare,
            "taxes": taxes,
            "add_on_fee": add_on_fee,
            "discount": total_discount,
            "coupon_code": coupon_code,
            "total_price": total_price
        }

        pnr = database.create_booking(booking_data, passengers_list)
        session['just_booked_pnr'] = pnr
        return redirect(url_for("payment", pnr=pnr))

    # Fetch occupied seats
    occupied_seats = database.get_occupied_seats(flight_id, travel_date)
    taxes = round((base_fare - concession_discount) * 0.12)
    total_initial_price = max(0, base_fare - concession_discount + taxes)

    return render_template(
        "book.html",
        flight=flight,
        travel_date=travel_date,
        passengers_count=passengers_count,
        cabin_class=cabin_class,
        fare_type=fare_type,
        concession_discount=concession_discount,
        occupied_seats=occupied_seats,
        total_initial_price=total_initial_price
    )

@app.route('/payment/<pnr>')
def payment(pnr):
    booking = database.get_booking_by_pnr(pnr)
    if not booking:
        flash("Booking reference not found.", "error")
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

    # Re-fetch updated booking
    updated_booking = database.get_booking_by_pnr(pnr)

    # Send automated ticket email to the passenger's email address
    email_service.send_ticket_email(updated_booking, updated_booking['passenger_email'])

    # Set session so newly booked flight is visible in this active session
    session['just_booked_pnr'] = pnr

    flash(f"🎉 Payment successful via {payment_method}! Your confirmed e-ticket and boarding pass have been emailed to {updated_booking['passenger_email']}.", "success")
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
    is_temporary_session = False

    if search_query:
        # Search specifically by PNR or email
        bookings = database.get_bookings_by_query(search_query)
    else:
        # Check if there is an active session booking just created
        # Pop it immediately so on page refresh it clears from view!
        just_booked_pnr = session.pop('just_booked_pnr', None)
        if just_booked_pnr:
            booking = database.get_booking_by_pnr(just_booked_pnr)
            bookings = [booking] if booking else []
            is_temporary_session = True
        else:
            # For passenger privacy, NEVER show any other person's booking!
            bookings = []

    return render_template(
        "my_bookings.html", 
        bookings=bookings, 
        search_query=search_query,
        is_temporary_session=is_temporary_session
    )

@app.route('/cancel-booking/<pnr>', methods=["GET", "POST"])
def cancel_flight_booking(pnr):
    success, message, refund_amount, booking = database.cancel_booking(pnr)
    if success and booking:
        # Send Cancellation Confirmation & Refund Breakdown Email to passenger
        email_service.send_cancellation_email(booking, refund_amount, booking['passenger_email'])
        flash(f"✓ Booking {pnr} successfully cancelled. Refund of ₹{refund_amount:,.2f} initiated and confirmation receipt emailed to {booking['passenger_email']}.", "success")
    else:
        flash(message, "error")

    return redirect(url_for("my_bookings", q=pnr))

@app.route('/support', methods=["GET", "POST"])
def support():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        pnr = request.form.get("pnr", "").strip().upper()
        category = request.form.get("category", "General Feedback")
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        full_subject = f"[{category}] {subject} (PNR: {pnr})" if pnr else f"[{category}] {subject}"

        # Save in database
        database.save_complaint(name, email, category, full_subject, message, forwarded_to="deeptidhanwate0@gmail.com")

        # Forward email to deeptidhanwate0@gmail.com
        email_service.send_support_complaint(name, email, full_subject, message, forward_to="deeptidhanwate0@gmail.com")

        flash(f"✓ Thank you {name}. Your inquiry has been received at support@skywings.com and forwarded directly to management (deeptidhanwate0@gmail.com). Ticket logged.", "success")
        return redirect(url_for("support"))

    return render_template("support.html")

@app.route('/deals')
def deals():
    return render_template("deals.html")

@app.route('/success')
def success():
    return redirect(url_for("my_bookings"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
