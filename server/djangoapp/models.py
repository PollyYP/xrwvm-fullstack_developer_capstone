"""
Django models for the application.

This module defines the CarMake and CarModel models
for representing car data in the database,
including make, model, type, year, and relationships.
"""

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# CarMake model
class CarMake(models.Model):
    """
    Model representing a car manufacturer.

    Attributes:
        name (str): The name of the car make.
        description (str): A detailed description of the car make.
    """

    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        """
        String representation of a CarMake instance.

        Returns:
            str: The name of the car make.
        """
        return str(self.name)


# CarModel model
class CarModel(models.Model):
    """
    Model representing a car model.

    Attributes:
        car_make (CarMake): The car make associated with this model.
        dealer_id (int): The ID of the dealer for this car model.
        name (str): The name of the car model.
        type (str): The type of the car (e.g., Sedan, SUV, Wagon).
        year (int): The manufacturing year of the car.
    """

    car_make = models.ForeignKey(
        CarMake, on_delete=models.CASCADE
    )  # Many-to-One relationship
    dealer_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=100)
    CAR_TYPES = [
        ('SEDAN', 'Sedan'),
        ('SUV', 'SUV'),
        ('WAGON', 'Wagon'),
        # Add more choices as required
    ]
    type = models.CharField(max_length=10, choices=CAR_TYPES, default='SUV')
    year = models.IntegerField(
        default=2023,
        validators=[
            MaxValueValidator(2023),
            MinValueValidator(2015)
        ]
    )

    def __str__(self):
        """
        String representation of a CarModel instance.

        Returns:
            str: The name of the car model with its type and year.
        """
        return f"{self.name} ({self.type}, {self.year})"
