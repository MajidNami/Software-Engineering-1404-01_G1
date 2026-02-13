from django.db import models
from .word import Word


class WordStory(models.Model):
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name="stories"
    )

    story = models.TextField(
        help_text="2–3 paragraph contextual story for the word"
    )

    image = models.ImageField(
        upload_to="word_stories/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Story for {self.word.word}"
