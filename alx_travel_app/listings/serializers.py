from rest_framework import serializers
from django.contrib.auth.models import User
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
        """Validate rating is between 1 and 5"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
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
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price per night must be positive.")
        return value
    
    def validate_max_guests(self, value):
        """Validate max guests is positive"""
        if value <= 0:
            raise serializers.ValidationError("Max guests must be at least 1.")
        return value
    
    def validate_amenities(self, value):
        """Validate amenities is a list"""
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
            'status', 'special_requests', 'duration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Custom validation for booking dates and guests"""
        from django.utils import timezone
        from django.core.exceptions import ValidationError
        
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        guests = data.get('guests')
        listing_id = data.get('listing_id')
        
        # Validate dates
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError(
                    "Check-out date must be after check-in date."
                )
            
            if check_in < timezone.now().date():
                raise serializers.ValidationError(
                    "Check-in date cannot be in the past."
                )
        
        # Validate guests against listing capacity
        if listing_id and guests:
            try:
                listing = Listing.objects.get(id=listing_id)
                if guests > listing.max_guests:
                    raise serializers.ValidationError(
                        f"Number of guests ({guests}) exceeds maximum capacity ({listing.max_guests})."
                    )
            except Listing.DoesNotExist:
                raise serializers.ValidationError("Invalid listing ID.")
        
        # Check for conflicting bookings
        if check_in and check_out and listing_id:
            conflicting_bookings = Booking.objects.filter(
                listing_id=listing_id,
                status__in=['confirmed', 'pending'],
                check_in_date__lt=check_out,
                check_out_date__gt=check_in
            )
            
            # Exclude current booking if updating
            if self.instance:
                conflicting_bookings = conflicting_bookings.exclude(id=self.instance.id)
            
            if conflicting_bookings.exists():
                raise serializers.ValidationError(
                    "Listing is not available for the selected dates."
                )
        
        return data
    
    def create(self, validated_data):
        """Override create to calculate total price"""
        listing = Listing.objects.get(id=validated_data['listing_id'])
        check_in = validated_data['check_in_date']
        check_out = validated_data['check_out_date']
        
        nights = (check_out - check_in).days
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