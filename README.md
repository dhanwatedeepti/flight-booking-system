# ✈️ SkyWings - Advanced Flight Booking Web Application

**SkyWings** is a modern, production-grade flight reservation platform built with Python (Flask) and SQLite. It provides a real-world air travel booking experience comparable to Google Flights, MakeMyTrip, and Skyscanner.

---

## 🚀 Features

### 1. Smart Flight Search & Discovery
- **One-Way & Round-Trip Modes**: Dynamic date constraints preventing past dates and ensuring return dates follow departures.
- **Airport Autocomplete**: Interactive airport search covering major Indian and international hubs (`DEL`, `BOM`, `BLR`, `PNQ`, `HYD`, `MAA`, `CCU`, `GOI`, `DXB`, `SIN`, `LHR`).
- **Traveler & Class Selection**: Choose between Economy and Business cabin classes with dynamic fare multiplier.
- **Popular Route Chips**: 1-click popular routes (*Pune → Delhi, Mumbai → Bangalore, Bangalore → Goa, Mumbai → Dubai*).
- **City Swap Button**: Quick switch between origin and destination.

### 2. Comprehensive Flight Comparison
- **Realistic Flight Schedules**: Flights operated by **IndiGo, Air India, Vistara, Akasa Air, SpiceJet, and Emirates**.
- **Interactive Filtering**: Filter on-the-fly by stops (Non-stop / 1 Stop), airlines, departure time slots (morning, afternoon, evening), and max price slider.
- **Sorting Engine**: Sort results by Cheapest First, Fastest Duration, or Earliest Departure.
- **Detailed Fare Breakdowns**: In-flight amenities, aircraft types (Airbus A320neo, Boeing 787 Dreamliner), and baggage allowances (Cabin 7kg + Check-in 15kg/25kg).

### 3. Interactive Cabin Seat Map & Checkout Flow
- **Authentic Fuselage Layout**: Visual aircraft cockpit, aisles, and rows 1 to 10 with columns A, B, C | D, E, F.
- **Seat Categories**: Free Standard seats vs. Premium Extra Legroom (Row 1 & Row 5).
- **Multiple Travelers**: Dynamic passenger form inputs (Title, Name, Age, Gender, Contact).
- **In-Flight Add-ons**: Gourmet meals (Veg Dum Biryani, Paneer Club Sandwich, Fresh Fruit Bowl), prepaid extra baggage (+10kg), and comprehensive travel insurance.
- **Promo Coupon System**: Working discount codes:
  - `FLYHIGH`: 15% off up to ₹1,200
  - `SKY500`: Flat ₹500 off
  - `FIRSTFLY`: 20% off up to ₹1,500
  - `FESTIVE`: 10% off up to ₹800

### 4. Realistic Payment Gateway
- **Interactive 3D Credit Card**: Live visual card preview updating card number, cardholder name, expiry date, and card brand (Visa/Mastercard) in real time.
- **UPI & QR Code**: Simulated instant UPI QR scan and VPA ID verification.
- **Net Banking**: Instant bank selection across HDFC, SBI, ICICI, Axis, and others.

### 5. Authentic Boarding Pass & E-Ticket
- **Printable E-Ticket**: Perforated boarding pass design with PNR badge, barcode, and QR code.
- **Flight Details**: Boarding time (45 mins prior to departure), terminal, gate, seat number, and baggage limits.
- **1-Click PDF / Print Support**: Optimized `@media print` layout hiding navbars and buttons for clean A4 printing.

### 6. "My Bookings" & PNR Management
- **PNR & Email Lookup**: Search and manage past and active bookings.
- **Self-Service Cancellation**: Instant cancellation with transparent 85% refund calculation and automatic seat restoration.

---

## 📁 Project Structure

```
FlightBook/
├── app.py                  # Flask routes, API endpoints, and request controllers
├── database.py             # SQLite database layer, schema, query helpers, and seed data
├── backend.py              # High-level API adapter maintaining backward compatibility
├── test_app.py             # Automated unit & integration tests
├── flights.db              # Persistent SQLite database
├── static/
│   ├── css/
│   │   └── style.css       # Responsive design system, seat map, 3D card, and print styles
│   └── js/
│       └── main.js         # Autocomplete, seat selector, filters, coupons, and live pricing
└── templates/
    ├── base.html           # Master layout, navigation, flash alerts, and footer
    ├── index.html          # Hero section, flight search widget, and popular routes
    ├── results.html        # Flight comparison cards, duration lines, and filter sidebar
    ├── book.html           # Passenger forms, visual cabin seat map, meals, and add-ons
    ├── payment.html        # Payment gateway with interactive 3D card and UPI
    ├── ticket.html         # Printable boarding pass & e-ticket with barcode & QR code
    ├── my_bookings.html    # PNR lookup, trip management, and cancellation
    └── deals.html          # Promotional coupons and discount offers
```

---

## 🛠️ How to Run

1. **Activate your Python environment** and install requirements if needed:
   ```bash
   python -m pip install flask
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Open in browser**:
   Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

4. **Run automated tests**:
   ```bash
   python test_app.py
   ```
