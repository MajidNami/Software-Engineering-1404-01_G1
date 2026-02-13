from django.db import models


class DifficultyLevel(models.TextChoices):
    A1 = "A1", "A1"
    A2 = "A2", "A2"
    B1 = "B1", "B1"
    B2 = "B2", "B2"
    C1 = "C1", "C1"
    C2 = "C2", "C2"


class Word(models.Model):
    word = models.CharField(max_length=100, unique=True)
    definition = models.TextField()

    difficulty = models.CharField(
        max_length=2,
        choices=DifficultyLevel.choices,
        db_index=True
    )

    pronunciation_audio = models.FileField(
        upload_to="pronunciations/",
        null=True,
        blank=True
    )

    ipa = models.CharField(
        max_length=100,
        help_text="IPA transcription (UTF-8 supported)"
    )

    synonyms = models.JSONField(default=list, blank=True)
    antonyms = models.JSONField(default=list, blank=True)
    examples = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["word"]
        indexes = [
            models.Index(fields=["difficulty"]),
        ]

    def __str__(self):
        return self.word
