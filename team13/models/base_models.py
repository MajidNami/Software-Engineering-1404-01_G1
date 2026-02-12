from django.db import models
import simple_history.models


class TimeModel(models.Model):
    """An abstract model with time-related fields."""
    created = models.DateTimeField(auto_now_add=True, db_index=True) # The timestamp when the object was created.
    modified = models.DateTimeField(auto_now=True, db_index=True) # The timestamp of the last modification.

    class Meta:
        abstract = True


class HistoricalModel(models.Model):
    """An abstract model providing history tracking functionality records for Django models."""
    history = simple_history.models.HistoricalRecords(inherit=True)

    class Meta:
        abstract = True
