import unittest
from app import app
import database

class SkyWingsAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_01_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SkyWings', response.data)
        self.assertIn(b'Search Flights', response.data)

    def test_02_flight_search(self):
        response = self.client.get('/search?from=Pune&to=Delhi')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Pune', response.data)
        self.assertIn(b'Delhi', response.data)
        self.assertIn(b'IndiGo', response.data)
        self.assertIn(b'Book Now', response.data)

    def test_03_airport_autocomplete_api(self):
        response = self.client.get('/api/airports?q=Mum')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(any(a['code'] == 'BOM' for a in data))

    def test_04_booking_flow_and_payment(self):
        # 1. Load book page
        flight = database.get_flight_by_id(1)
        self.assertIsNotNone(flight)
        res = self.client.get(f'/book/{flight["id"]}?date=2026-09-20&passengers=1')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Passenger Information', res.data)
        self.assertIn(b'Select Your Seats', res.data)

        # 2. Submit booking form
        booking_payload = {
            'travel_date': '2026-09-20',
            'passengers_count': '1',
            'cabin_class': 'Economy',
            'p_title_1': 'Mr',
            'p_first_1': 'Rahul',
            'p_last_1': 'Sharma',
            'p_age_1': '32',
            'p_gender_1': 'Male',
            'email': 'rahul.sharma@example.com',
            'phone': '+91 9876543210',
            'selected_seats': '1A',
            'meals': 'Veg Dum Biryani',
            'add_on_fee': '750', # 500 extra legroom + 250 meal
            'discount': '500',
            'coupon_code': 'SKY500',
            'total_price': '4114'
        }
        post_res = self.client.post(f'/book/{flight["id"]}', data=booking_payload, follow_redirects=False)
        self.assertEqual(post_res.status_code, 302)
        redirect_url = post_res.headers['Location']
        self.assertIn('/payment/SKY-', redirect_url)

        pnr = redirect_url.split('/payment/')[-1]
        self.assertTrue(pnr.startswith('SKY-'))

        # 3. Access Payment Gateway
        pay_page = self.client.get(f'/payment/{pnr}')
        self.assertEqual(pay_page.status_code, 200)
        self.assertIn(b'Select Payment Method', pay_page.data)
        self.assertIn(b'Rahul Sharma', pay_page.data)

        # 4. Process Payment
        pay_res = self.client.post(f'/process-payment/{pnr}', data={'payment_method': 'UPI'}, follow_redirects=True)
        self.assertEqual(pay_res.status_code, 200)
        self.assertIn(b'Booking Confirmed!', pay_res.data)
        self.assertIn(b'BOARDING PASS', pay_res.data)
        self.assertIn(pnr.encode(), pay_res.data)

        # 5. Check Boarding Pass Ticket Page
        ticket_res = self.client.get(f'/ticket/{pnr}')
        self.assertEqual(ticket_res.status_code, 200)
        self.assertIn(b'Boarding Pass & E-Ticket', ticket_res.data)
        self.assertIn(b'Print / Save as PDF', ticket_res.data)

        # 6. Lookup in My Bookings
        my_res = self.client.get(f'/my-bookings?q={pnr}')
        self.assertEqual(my_res.status_code, 200)
        self.assertIn(pnr.encode(), my_res.data)
        self.assertIn(b'Confirmed', my_res.data)

        # 7. Cancel Booking
        cancel_res = self.client.post(f'/cancel-booking/{pnr}', follow_redirects=True)
        self.assertEqual(cancel_res.status_code, 200)
        self.assertIn(b'successfully cancelled', cancel_res.data)

        # Verify status is now cancelled
        cancelled_booking = database.get_booking_by_pnr(pnr)
        self.assertEqual(cancelled_booking['booking_status'], 'Cancelled')

    def test_05_deals_page(self):
        res = self.client.get('/deals')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'FLYHIGH', res.data)
        self.assertIn(b'SKY500', res.data)

if __name__ == '__main__':
    unittest.main()
