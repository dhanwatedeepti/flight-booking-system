import unittest
import os
from app import app
import database
import email_service

class SkyWingsAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.secret_key = 'test_secret_key'

    def test_01_index_page_and_classes(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Student Discount', response.data)
        self.assertIn(b'Senior Citizen', response.data)
        self.assertIn(b'Armed Forces', response.data)
        self.assertIn(b'Premium Economy', response.data)
        self.assertIn(b'Business', response.data)
        self.assertIn(b'First Class', response.data)

    def test_02_student_and_senior_concessions_search(self):
        # 1. Regular search
        reg_res = self.client.get('/search?from=Pune&to=Delhi&cabin_class=Economy&fare_type=Regular')
        self.assertEqual(reg_res.status_code, 200)
        self.assertIn(b'Regular Fare', reg_res.data)

        # 2. Student concession search
        student_res = self.client.get('/search?from=Pune&to=Delhi&cabin_class=Economy&fare_type=Student')
        self.assertEqual(student_res.status_code, 200)
        self.assertIn(b'Student Concession', student_res.data)
        self.assertIn(b'Student Free', student_res.data)

        # 3. Senior Citizen concession search
        senior_res = self.client.get('/search?from=Pune&to=Delhi&cabin_class=Economy&fare_type=Senior+Citizen')
        self.assertEqual(senior_res.status_code, 200)
        self.assertIn(b'Senior Citizen Concession', senior_res.data)

    def test_03_booking_with_student_discount_and_upi_payment(self):
        # Book flight 1 with Student concession
        booking_payload = {
            'travel_date': '2026-09-25',
            'passengers_count': '1',
            'cabin_class': 'Economy',
            'fare_type': 'Student',
            'p_title_1': 'Mr',
            'p_first_1': 'Aman',
            'p_last_1': 'Verma',
            'p_age_1': '21',
            'p_gender_1': 'Male',
            'email': 'aman.verma.student@example.com',
            'phone': '+91 9988776655',
            'selected_seats': '2A',
            'meals': 'Paneer Club Sandwich',
            'add_on_fee': '180',
            'discount': '345', # 10% student discount
            'coupon_code': '',
            'total_price': '3646'
        }
        res = self.client.post('/book/1', data=booking_payload, follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        pnr = res.headers['Location'].split('/payment/')[-1]
        self.assertTrue(pnr.startswith('SKY-'))

        # Pay using UPI
        upi_pay_res = self.client.post(f'/process-payment/{pnr}', data={'payment_method': 'UPI (aman@okaxis)'}, follow_redirects=True)
        self.assertEqual(upi_pay_res.status_code, 200)
        self.assertIn(b'Payment successful', upi_pay_res.data)
        self.assertIn(b'aman.verma.student@example.com', upi_pay_res.data)

        # Verify Ticket Email was saved in sent_emails
        email_files = os.listdir(email_service.EMAILS_DIR)
        self.assertTrue(any('aman_verma_student_at_example_com' in f for f in email_files))

        # Check Ticket Page
        ticket_res = self.client.get(f'/ticket/{pnr}')
        self.assertEqual(ticket_res.status_code, 200)
        self.assertIn(pnr.encode(), ticket_res.data)
        self.assertIn(b'Cancel Flight (85% Refund)', ticket_res.data)

        # Cancel Flight and verify cancellation email with refund
        cancel_res = self.client.post(f'/cancel-booking/{pnr}', follow_redirects=True)
        self.assertEqual(cancel_res.status_code, 200)
        self.assertIn(b'successfully cancelled', cancel_res.data)
        self.assertIn(b'Refund', cancel_res.data)

        # Verify Cancellation email was generated
        booking = database.get_booking_by_pnr(pnr)
        self.assertEqual(booking['booking_status'], 'Cancelled')
        self.assertGreater(booking['refund_amount'], 0)

    def test_04_net_banking_payment_flow(self):
        # Create a booking and pay via Net Banking
        booking_payload = {
            'travel_date': '2026-09-28',
            'passengers_count': '1',
            'cabin_class': 'Business',
            'fare_type': 'Regular',
            'p_title_1': 'Ms',
            'p_first_1': 'Pooja',
            'p_last_1': 'Kulkarni',
            'p_age_1': '34',
            'p_gender_1': 'Female',
            'email': 'pooja.kulkarni@example.com',
            'phone': '+91 9123456780',
            'selected_seats': '1F',
            'total_price': '8500'
        }
        res = self.client.post('/book/2', data=booking_payload, follow_redirects=False)
        pnr = res.headers['Location'].split('/payment/')[-1]

        # Pay via Net Banking - HDFC Bank
        net_res = self.client.post(f'/process-payment/{pnr}', data={'payment_method': 'Net Banking (HDFC Bank)'}, follow_redirects=True)
        self.assertEqual(net_res.status_code, 200)
        self.assertIn(b'Net Banking (HDFC Bank)', net_res.data)
        self.assertIn(pnr.encode(), net_res.data)

    def test_05_customer_support_forwarding(self):
        # Submit customer grievance for support@skywings.com
        support_payload = {
            'name': 'Vikram Mehta',
            'email': 'vikram.mehta@example.com',
            'pnr': 'SKY-999888',
            'category': 'Flight Delay',
            'subject': 'Delay inquiry for flight 6E-205',
            'message': 'Flight was delayed by 2 hours, requesting compensation details.'
        }
        res = self.client.post('/support', data=support_payload, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'forwarded directly to management (deeptidhanwate0@gmail.com)', res.data)

        # Verify email was dispatched to deeptidhanwate0@gmail.com in sent_emails
        email_files = os.listdir(email_service.EMAILS_DIR)
        self.assertTrue(any('deeptidhanwate0_at_gmail_com' in f for f in email_files))

    def test_06_privacy_and_refresh_clearing(self):
        # 1. Visiting /my-bookings freshly without query must show NO bookings
        fresh_res = self.client.get('/my-bookings')
        self.assertEqual(fresh_res.status_code, 200)
        self.assertIn(b'Private Trip Lookup', fresh_res.data)
        self.assertNotIn(b'booking-item-card', fresh_res.data)

        # 2. Simulate user booking a flight
        with self.client.session_transaction() as sess:
            sess['just_booked_pnr'] = 'SKY-PRIV123'
            
        # Insert dummy booking for SKY-PRIV123
        b_data = {
            'flight_id': 1,
            'passenger_name': 'Secret Traveler',
            'passenger_email': 'secret@example.com',
            'passenger_phone': '+91 9999999999',
            'passengers_count': 1,
            'cabin_class': 'Economy',
            'travel_date': '2026-10-01',
            'base_fare': 3000,
            'taxes': 360,
            'total_price': 3360
        }
        # Direct DB insert for test
        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO bookings (id, pnr, flight_id, passenger_name, passenger_email, passenger_phone, travel_date, base_fare, taxes, total_price, booking_status) VALUES (9999, 'SKY-PRIV123', 1, 'Secret Traveler', 'secret@example.com', '+91 9999999999', '2026-10-01', 3000, 360, 3360, 'Confirmed')")
        conn.commit()
        conn.close()

        # First visit: session view displays booking
        first_visit = self.client.get('/my-bookings')
        self.assertEqual(first_visit.status_code, 200)
        self.assertIn(b'SKY-PRIV123', first_visit.data)
        self.assertIn(b'Active Session Booking', first_visit.data)

        # Page Refresh (second visit): session is cleared, booking is NOT shown!
        refresh_visit = self.client.get('/my-bookings')
        self.assertEqual(refresh_visit.status_code, 200)
        self.assertNotIn(b'SKY-PRIV123', refresh_visit.data)
        self.assertIn(b'Private Trip Lookup', refresh_visit.data)

        # But searching specifically with PNR works:
        search_visit = self.client.get('/my-bookings?q=SKY-PRIV123')
        self.assertEqual(search_visit.status_code, 200)
        self.assertIn(b'SKY-PRIV123', search_visit.data)

if __name__ == '__main__':
    unittest.main()
