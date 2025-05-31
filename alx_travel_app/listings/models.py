from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
# pylint: disable=no-member


class Listing(models.Model):
    """
    Represents a property listing.
    """
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('condo', 'Condominium'),
        ('cabin', 'Cabin'),
        ('loft', 'Loft'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    location = models.CharField(max_length=200)
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPES,
        default='apartment'
    )
    max_guests = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    amenities = models.JSONField(default=list, blank=True)
    available = models.BooleanField(default=True)
    host = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='listings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['property_type']),
            models.Index(fields=['price_per_night']),
            models.Index(fields=['available']),
        ]

    def __str__(self):
        return f"{self.title} - {self.location}"

    def average_rating(self):
        reviews = self.reviews.all()
        return sum(r.rating for r in reviews) / len(reviews) if reviews else 0

    def total_reviews(self):
        return self.reviews.count()


class Booking(models.Model):
    """
    Represents a booking for a listing.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    guests = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    special_requests = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['check_in_date', 'check_out_date']),
            models.Index(fields=['status']),
            models.Index(fields=['user']),
            models.Index(fields=['listing']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out_date__gt=models.F('check_in_date')),
                name='check_out_after_check_in'
            )
        ]

    def __str__(self):
        return f"Booking for {self.listing.title} by {self.user.username}"

    def clean(self):
        if self.check_out_date <= self.check_in_date:
            raise ValidationError('Check-out date must be after check-in date.')
        if self.check_in_date < timezone.now().date():
            raise ValidationError('Check-in date cannot be in the past.')

    def duration(self):
        return (self.check_out_date - self.check_in_date).days

    def save(self, *args, **kwargs):
        if not self.total_price and self.listing and self.check_in_date and self.check_out_date:
            self.total_price = self.listing.price_per_night * self.duration()
        super().save(*args, **kwargs)


class Review(models.Model):
    """
    Represents a review for a listing.
    """
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='review',
        null=True,
        blank=True
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['listing', 'user']
        indexes = [
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Review by {self.user.username} for {self.listing.title} - {self.rating}/5"

    def clean(self):
        if not Booking.objects.filter(
            user=self.user,
            listing=self.listing,
            status='completed'
        ).exists():
            raise ValidationError(
                'You can only review a listing after completing a booking.')
