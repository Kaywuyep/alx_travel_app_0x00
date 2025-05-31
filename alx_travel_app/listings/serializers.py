# pylint: disable=no-member
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Listing, Booking, Review


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""

    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_id', 'booking', 'rating',
            'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5.")
        return value


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model"""

    host = UserSerializer(read_only=True)
    host_id = serializers.IntegerField(write_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    total_reviews = serializers.ReadOnlyField()

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'price_per_night', 'location',
            'property_type', 'max_guests', 'bedrooms', 'bathrooms',
            'amenities', 'available', 'host', 'host_id', 'reviews',
            'average_rating', 'total_reviews', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_price_per_night(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price per night must be positive.")
        return value

    def validate_max_guests(self, value):
        if value <= 0:
            raise serializers.ValidationError("Max guests must be at least 1.")
        return value

    def validate_amenities(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Amenities must be a list.")
        return value


class ListingBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for Listing model (for nested representations)"""

    host = UserSerializer(read_only=True)
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'price_per_night', 'location',
            'property_type', 'max_guests', 'host', 'average_rating'
        ]


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model"""

    listing = ListingBasicSerializer(read_only=True)
    listing_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    duration = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_id', 'user', 'user_id',
            'check_in_date', 'check_out_date', 'guests', 'total_price',
            'status', 'special_requests', 'duration', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']

    def validate(self, attrs):
        check_in = attrs.get('check_in_date')
        check_out = attrs.get('check_out_date')
        listing_id = attrs.get('listing_id')

        # Validate dates
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError(
                    "Check-out date must be after check-in date.")
            if check_in < timezone.now().date():
                raise serializers.ValidationError(
                    "Check-in date cannot be in the past.")

        # Check for conflicting bookings
        if check_in and check_out and listing_id:
            conflicts = Booking.objects.filter(
                listing_id=listing_id,
                status__in=['confirmed', 'pending'],
                check_in_date__lt=check_out,
                check_out_date__gt=check_in
            )
            if self.instance:
                conflicts = conflicts.exclude(id=self.instance.id)
            if conflicts.exists():
                raise serializers.ValidationError(
                    "Listing is not available for the selected dates.")

        return attrs

    def create(self, validated_data):
        listing = Listing.objects.get(id=validated_data['listing_id'])
        nights = (
            validated_data['check_out_date'] - validated_data['check_in_date']
            ).days
        validated_data['total_price'] = listing.price_per_night * nights
        return super().create(validated_data)


class BookingBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for Booking model (for nested representations)"""

    user = UserSerializer(read_only=True)
    duration = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'check_in_date', 'check_out_date',
            'guests', 'total_price', 'status', 'duration'
        ]
