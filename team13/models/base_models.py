from django.db import models


class TimeModel(models.Model):
    """An abstract model with time-related fields."""
    created = models.DateTimeField(auto_now_add=True, db_index=True) # The timestamp when the object was created.
    modified = models.DateTimeField(auto_now=True, db_index=True) # The timestamp of the last modification.

    class Meta:
        abstract = True
