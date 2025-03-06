import yagmail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime

class FlightTicketBooking:
    def __init__(self):
        print("Flight Ticket Booking System Initialized.")
        self.airlines = {
            "Air India": 5000,
            "Indigo": 4500,
            "Akasa": 4000,
            "Air India Express": 5500
        }
        self.routes = {
            ("Delhi", "Pune"): {
                "distance": 1460, "time": 2.5,
                "available_times": ["08:00 AM", "11:00 AM", "02:00 PM", "05:00 PM"]
            },
            ("Mumbai", "Kolkata"): {
                "distance": 1960, "time": 2.75,
                "available_times": ["06:00 AM", "10:00 AM", "01:00 PM", "04:00 PM"]
            },
            ("Bangalore", "Chennai"): {
                "distance": 290, "time": 1,
                "available_times": ["07:00 AM", "10:00 AM", "01:00 PM", "04:00 PM"]
            },
            ("Hyderabad", "Goa"): {
                "distance": 640, "time": 1.25,
                "available_times": ["08:30 AM", "12:00 PM", "03:00 PM", "06:00 PM"]
            },
            ("Bangalore", "Hyderabad"): {
                "distance": 570, "time": 1.25,
                "available_times": ["09:00 AM", "12:30 PM", "03:30 PM", "07:00 PM"]
            },
            ("Kolkata", "Pune"): {
                "distance": 1575, "time": 2.75,
                "available_times": ["07:30 AM", "11:30 AM", "02:30 PM", "06:00 PM"]
            },
            ("Hyderabad", "Jaipur"): {
                "distance": 1365, "time": 2.25,
                "available_times": ["08:00 AM", "12:00 PM", "04:00 PM", "08:00 PM"]
            },
            ("Delhi", "Mumbai"): {
                "distance": 1400, "time": 2,
                "available_times": ["09:00 AM", "12:30 PM", "03:00 PM", "06:00 PM"]
            },
            ("Chennai", "Kolkata"): {
                "distance": 1670, "time": 2.5,
                "available_times": ["08:30 AM", "11:30 AM", "02:30 PM", "05:30 PM"]
            },
            ("Ahmedabad", "Goa"): {
                "distance": 975, "time": 2,
                "available_times": ["07:00 AM", "10:00 AM", "01:00 PM", "04:00 PM"]
            },
        }

    def input_with_exit(self, prompt):
        """Prompt input and allow exiting the program."""
        user_input = input(prompt).strip().lower()
        if user_input == "exit":
            print("\nExiting the program. Thank you!")
            exit()
        return user_input

    def calculate_discount(self, age, is_student=False):
        """Calculate discount based on age and student status."""
        if is_student and age > 12:
            return 0.06  # 6% discount
        elif age >= 65:
            return 0.10  # 10% discount
        return 0.0

    def select_flight_timing(self, available_times):
        """Allow the user to select a flight timing from the available options."""
        print("\nAvailable Flight Timings:")
        for idx, time in enumerate(available_times, 1):
            print(f"{idx}. {time}")
        timing_choice = self.input_with_exit("\nChoose a flight timing (type 'exit' to quit): ")
        return available_times[int(timing_choice) - 1]
    
    def send_email_confirmation(self, recipient_email, booking_details, airline_name):
        """Send email confirmation with airline logo and signature."""
        sender_email = "dhanwatedeepti2@gmail.com"  
        app_password = "bauz wpui vkiy cewp"   

        # Define the image URL for the airline logo (replace with real URLs)
        airline_logos = {
            "Air India": "https://upload.wikimedia.org/wikipedia/commons/b/bf/Air_India_2023.svg",
            "Indigo": "images/IndiGo-Logo (1).jpg",
            "Akasa": "images/Akasa-logo.png",
            "Air India Express": "images/Air_India_Express_Logo.png",
        }
        logo_url = airline_logos.get(airline_name, "")


        subject = "Flight Ticket Confirmation"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2 style="color: #4CAF50;">Flight Ticket Confirmation</h2>
                <p>Dear Customer,</p>
                <p>Thank you for booking with <strong>{airline_name}</strong>! Below are your booking details:</p>
                <pre style="background-color: #f9f9f9; padding: 10px; border-left: 4px solid #ccc;">
{booking_details}
                </pre>
                <p>We wish you a pleasant journey!</p>
                <p>
                    <img src="{logo_url}" alt="{airline_name} Logo" style="width: 150px; display: block; margin-top: 20px;">
                </p>
                <hr>
                <p style="font-size: 14px; color: #555;">
                    -- <br>
                    <strong>Regards,</strong><br>
                    <strong>Flight Ticket Booking Team</strong><br>
                    Email: your_email@gmail.com<br>
                    Phone: +91 12345 67890
                </p>
            </body>
        </html>
        """

#        try:
 #           if logo_url:
  #           with open(logo_url, 'rb') as img_file:
   #             logo = MIMEImage(img_file.read())
    #            logo.add_header('Content-ID', '<airline_logo>')
     #           logo.add_header('Content-Disposition', 'inline', filename="airline_logo.png")
      #          msg.attach(logo)
       # except FileNotFoundError:
        #     print(f"Error: Logo image for {airline_name} not found at {logo_url}")

        try:
            yag = yagmail.SMTP(sender_email, app_password)
            yag.send(
                to=recipient_email,
                subject=subject,
                contents=body  # Pass the HTML content as the body
            )
            print("\nConfirmation email sent successfully.")
        except Exception as e:
            print("\nFailed to send email. Please check your email settings.")
            print(f"Error: {e}")


    def book_ticket(self):
        print("\nWelcome to the Flight Ticket Booking System\n")

        # Select Airline
        print("Available Airlines:")
        for idx, airline in enumerate(self.airlines.keys(), 1):
            print(f"{idx}. {airline}")
        airline_choice = self.input_with_exit("\nChoose an airline (type 'exit' to quit): ")
        selected_airline = list(self.airlines.keys())[int(airline_choice) - 1]
        base_price = self.airlines[selected_airline]

        # Show Destinations
        print("\nAvailable Routes:")
        for idx, route in enumerate(self.routes.keys(), 1):
            print(f"{idx}. {route[0]} to {route[1]}")
        route_choice = self.input_with_exit("\nChoose a route (type 'exit' to quit): ")
        selected_route = list(self.routes.keys())[int(route_choice) - 1]
        journey_info = self.routes[selected_route]

        print(f"\nRoute Selected: {selected_route[0]} to {selected_route[1]}")
        print(f"Distance: {journey_info['distance']} km")
        print(f"Time Required: {journey_info['time']} hours")

        selected_timing = self.select_flight_timing(journey_info['available_times'])
         # Display the chosen timing
        print(f"\nSelected Flight Timing: {selected_timing}")
        
        # One-way or Round-trip
        trip_type = self.input_with_exit("\nIs it a one-way or round-trip? (one-way/round-trip): ").lower()
        if trip_type == "round-trip":
            base_price *= 2

        # Display Base Price
        print(f"\nBasic Ticket Price: ₹{base_price}")


        try:
         # Prompt the user for day, month, and year
          day = int(input("Enter day (DD): "))
          month = int(input("Enter month (MM): "))
          year = int(input("Enter year (YYYY): "))
    
         # Validate and create a date object
          user_date = datetime(year, month, day)
          print(f"You entered a valid date: {user_date.strftime('%d-%m-%Y')}")
        except ValueError:
          print("Invalid date entered. Please try again.")

    
        # Passenger Details
        #date = int(self.input_with_exit("Enter booking Date: "))
        name = self.input_with_exit("\nEnter your full name: ")
        age = int(self.input_with_exit("Enter your age: "))
        is_student = self.input_with_exit("Do you have a student ID? (yes/no): ").lower() == "yes"

        # Free meal information
        print("\nGood news! All passengers are eligible for a complimentary meal on board.")

        # Calculate discount
        discount_rate = self.calculate_discount(age, is_student)
        discount = base_price * discount_rate

        # Final Price Calculation
        final_price = base_price - discount

        # Confirmation
        print("\nBooking Summary:")
        print(f"Name: {name}")
        print(f"Date:{user_date}")
        print(f"Airline: {selected_airline}")
        print(f"Route: {selected_route[0]} to {selected_route[1]}")
        print(f"Trip Type: {trip_type.capitalize()}")
        print(f"Selected Timing: {selected_timing}")
        print(f"Base Price: ₹{base_price}")
        print(f"Discount: -₹{discount:.2f}")
        print(f"Total Price: ₹{final_price:.2f}")
        print(f"Complimentary Meal: Included")

        # Email Confirmation
        confirm = self.input_with_exit("\nDo you want to confirm the ticket? (yes/no): ").lower()
        if confirm == "yes":
            recipient_email = self.input_with_exit("Enter your email address for confirmation: ")
            booking_details = (
                f"Name: {name}\n"
                f"Airline: {selected_airline}\n"
                f"Route: {selected_route[0]} to {selected_route[1]}\n"
                f"Trip Type: {trip_type.capitalize()}\n"
                f"Date:{user_date}"
                f"Selected Timing: {selected_timing}\n"
                f"Total Price: ₹{final_price:.2f}\n"
                f"Complimentary Meal: Included"
            )
            self.send_email_confirmation(recipient_email, booking_details, selected_airline)
        else:
            print("\nBooking cancelled. Thank you!")

    def select_flight_timing(self, available_times):
        """Allow the user to select a flight timing from the available options."""
        print("\nAvailable Flight Timings:")
        for idx, timing in enumerate(available_times, 1):
            print(f"{idx}. {timing}")
        while True:
            try:
                timing_choice = int(self.input_with_exit("\nChoose a flight timing (type 'exit' to quit): "))
                if 1 <= timing_choice <= len(available_times):
                    return available_times[timing_choice - 1]
                else:
                    print("Invalid choice. Please choose a valid timing.")
            except ValueError:
                print("Invalid input. Please enter a number corresponding to the timing.")

# Run the program
if __name__ == "__main__":
    booking_system = FlightTicketBooking()
    booking_system.book_ticket()
    