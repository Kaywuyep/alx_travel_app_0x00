# pylint: disable=no-member
import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing, Booking, Review


class Command(BaseCommand):
    """
    Command to seed the database with sample
    data for listings, bookings, and reviews."""
    help = 'Seed the database with sample listings, bookings, and reviews data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--listings',
            type=int,
            default=20,
            help='Number of listings to create (default: 20)'
        )
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)'
        )
        parser.add_argument(
            '--bookings',
            type=int,
            default=30,
            help='Number of bookings to create (default: 30)'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=25,
            help='Number of reviews to create (default: 25)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(
                self.style.WARNING('Clearing existing data...')
            )
            self.clear_data()

        self.stdout.write(
            self.style.SUCCESS('Starting database seeding...')
        )

        # Create users
        users = self.create_users(options['users'])
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(users)} users')
        )

        # Create listings
        listings = self.create_listings(users, options['listings'])
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(listings)} listings')
        )

        # Create bookings
        bookings = self.create_bookings(users, listings, options['bookings'])
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(bookings)} bookings')
        )

        # Create reviews
        reviews = self.create_reviews(users, listings, bookings, options['reviews'])
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(reviews)} reviews')
        )

        self.stdout.write(
            self.style.SUCCESS('Database seeding completed successfully!')
        )

    def clear_data(self):
        """Clear existing data"""
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_users(self, count):
        """Create sample users"""
        users = []
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily',
            'Robert', 'Lisa', 'Christopher', 'Jessica', 'Matthew', 'Amanda',
            'Daniel', 'Ashley', 'James', 'Melissa', 'Joseph', 'Michelle'
        ]
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
            'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez',
            'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore'
        ]

        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}{last_name.lower()}{i+1}"
            email = f"{username}@example.com"

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password='password123'
            )
            users.append(user)

        return users

    def create_listings(self, users, count):
        """Create sample listings"""
        listings = []

        sample_listings_data = [
            {
                'title': 'Cozy Downtown Apartment',
                'description': 'A beautiful and cozy apartment in the heart of downtown. Perfect for business travelers and tourists alike.',
                'location': 'New York, NY',
                'property_type': 'apartment',
                'amenities': ['WiFi', 'Kitchen', 'Air Conditioning', 'TV']
            },
            {
                'title': 'Spacious Family House',
                'description': 'Large family house with garden, perfect for families with children. Quiet neighborhood with great schools nearby.',
                'location': 'Los Angeles, CA',
                'property_type': 'house',
                'amenities': ['WiFi', 'Kitchen', 'Garden', 'Parking', 'Pet Friendly']
            },
            {
                'title': 'Luxury Villa with Pool',
                'description': 'Stunning luxury villa with private pool and ocean view. Perfect for romantic getaways and special occasions.',
                'location': 'Miami, FL',
                'property_type': 'villa',
                'amenities': ['WiFi', 'Pool', 'Ocean View', 'Kitchen', 'Air Conditioning']
            },
            {
                'title': 'Modern City Loft',
                'description': 'Contemporary loft in trendy neighborhood. High ceilings, exposed brick, and modern amenities.',
                'location': 'Chicago, IL',
                'property_type': 'loft',
                'amenities': ['WiFi', 'Kitchen', 'Workspace', 'Gym Access']
            },
            {
                'title': 'Mountain Cabin Retreat',
                'description': 'Rustic cabin in the mountains. Perfect for hiking enthusiasts and nature lovers.',
                'location': 'Denver, CO',
                'property_type': 'cabin',
                'amenities': ['WiFi', 'Fireplace', 'Kitchen', 'Hiking Trails']
            },
            {
                'title': 'Beachfront Condo',
                'description': 'Beautiful condominium right on the beach. Wake up to ocean views every morning.',
                'location': 'San Diego, CA',
                'property_type': 'condo',
                'amenities': ['WiFi', 'Beach Access', 'Pool', 'Kitchen', 'Balcony']
            }
        ]
        cities = [
            'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX',
            'Phoenix, AZ', 'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA',
            'Dallas, TX', 'San Jose, CA', 'Austin, TX', 'Jacksonville, FL',
            'San Francisco, CA', 'Columbus, OH', 'Charlotte, NC', 'Indianapolis, IN',
            'Seattle, WA', 'Denver, CO', 'Boston, MA', 'Nashville, TN'
        ]
        property_types = ['apartment', 'house', 'villa', 'condo', 'cabin', 'loft']
        for i in range(count):
            if i < len(sample_listings_data):
                # Use predefined data for first few listings
                data = sample_listings_data[i]
                title = data['title']
                description = data['description']
                location = data['location']
                property_type = data['property_type']
                amenities = data['amenities']
            else:
                # Generate random data for remaining listings
                title = f"{random.choice(['Cozy', 'Spacious', 'Modern', 'Luxury', 'Charming'])} {random.choice(['Apartment', 'House', 'Villa', 'Condo', 'Loft'])}"
                description = f"A wonderful {random.choice(['and comfortable', 'and stylish', 'and elegant'])} place to stay during your visit."
                location = random.choice(cities)
                property_type = random.choice(property_types)
                amenities = random.sample(
                    ['WiFi', 'Kitchen', 'Air Conditioning', 'Pool', 'Parking', 
                     'Pet Friendly', 'Garden', 'Balcony', 'Fireplace', 'Gym Access'],
                    k=random.randint(2, 5)
                )

            listing = Listing.objects.create(
                title=title,
                description=description,
                price_per_night=Decimal(str(random.randint(50, 500))),
                location=location,
                property_type=property_type,
                max_guests=random.randint(1, 8),
                bedrooms=random.randint(1, 4),
                bathrooms=random.randint(1, 3),
                amenities=amenities,
                available=random.choice([True, True, True, False]),  # 75% available
                host=random.choice(users)
            )
            listings.append(listing)

        return listings

    def create_bookings(self, users, listings, count):
        """Create sample bookings"""
        bookings = []
        status_choices = ['pending', 'confirmed', 'cancelled', 'completed']

        for i in range(count):
            listing = random.choice(listings)
            user = random.choice([u for u in users if u != listing.host])  # User can't book their own listing

            # Generate random dates
            start_date = date.today() + timedelta(days=random.randint(-30, 60))
            duration = random.randint(1, 14)
            end_date = start_date + timedelta(days=duration)

            guests = random.randint(1, min(listing.max_guests, 6))
            total_price = listing.price_per_night * duration
            status = random.choice(status_choices)

            # Generate special requests occasionally
            special_requests = None
            if random.random() < 0.3:  # 30% chance of special requests
                requests = [
                    'Late check-in requested',
                    'Need extra towels',
                    'Celebrating anniversary',
                    'Early check-out needed',
                    'Require parking space'
                ]
                special_requests = random.choice(requests)

            booking = Booking.objects.create(
                listing=listing,
                user=user,
                check_in_date=start_date,
                check_out_date=end_date,
                guests=guests,
                total_price=total_price,
                status=status,
                special_requests=special_requests
            )
            bookings.append(booking)

        return bookings

    def create_reviews(self, users, listings, bookings, count):
        """Create sample reviews"""
        reviews = []

        # Get completed bookings for realistic reviews
        completed_bookings = [b for b in bookings if b.status == 'completed']

        sample_comments = [
            "Great place to stay! The host was very accommodating and the location was perfect.",
            "Clean, comfortable, and exactly as described. Would definitely book again.",
            "Amazing property with beautiful views. Highly recommended!",
            "Good value for money. The amenities were exactly what we needed.",
            "Perfect for our family vacation. Kids loved the pool!",
            "Cozy and well-equipped. Great communication from the host.",
            "Excellent location, walking distance to everything we wanted to see.",
            "Beautiful property, but the WiFi was a bit slow.",
            "Fantastic stay! The kitchen was well-stocked and the bed was comfortable.",
            "Great experience overall. Would recommend to friends and family."
        ]

        used_combinations = set()

        for i in range(count):
            # Try to use completed bookings first, then random combinations
            if completed_bookings and random.random() < 0.7:
                booking = random.choice(completed_bookings)
                listing = booking.listing
                user = booking.user
                combination = (listing.id, user.id)
            else:
                listing = random.choice(listings)
                user = random.choice([u for u in users if u != listing.host])
                combination = (listing.id, user.id)
                booking = None

            # Avoid duplicate reviews for same user-listing combination
            if combination in used_combinations:
                continue

            used_combinations.add(combination)

            rating = random.randint(3, 5)  # Mostly positive reviews
            comment = random.choice(sample_comments)

            review = Review.objects.create(
                listing=listing,
                user=user,
                booking=booking,
                rating=rating,
                comment=comment
            )
            reviews.append(review)

        return reviews
