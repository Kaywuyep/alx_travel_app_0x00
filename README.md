## A duplicate of the alx travel app 

### Database Modeling and Data Seeding in Django
mandatory
Objective

Define the database models, create serializers for API data representation, and implement a management command to seed the database.

Instructions

Duplicate Project:

Duplicate the project alx_travel_app to alx_travel_app_0x00
Create Models:

In listings/models.py, define Listing, Booking, and Review models based on the provided structure.
Each model should have appropriate fields, relationships, and constraints.
Set Up Serializers:

Create serializers in listings/serializers.py for Listing and Booking models.
Implement Seeders:

Create a management command in listings/management/commands/seed.py to populate the database with sample listings data.
Run Seed Command `python manage.py seed`:

Test the seeder by running the command to populate the database with sample data.