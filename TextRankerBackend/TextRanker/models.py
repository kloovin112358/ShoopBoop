from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from detoxify import Detoxify


class Boop(models.Model):
    boop_text = models.TextField(max_length=140, unique=True)
    creation_ts = models.DateTimeField(default=timezone.now)
    num_foops = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return self.boop_text[0:30]

    def clean(self):
        toxicityRating = Detoxify("original").predict(self.boop_text)
        if toxicityRating["toxicity"] > 0.5:
            raise ValidationError(
                "Error: this boop has not met the community standards for toxicity. Please reword your boop."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class UserPOSTSubmission(models.Model):
    """
    The purpose of this model is to ensure users are not cheating the system
    by attempting to send foops via bots - at inhuman speeds
    """

    user_ip = models.GenericIPAddressField(unique=True)
    last_submitted = models.DateTimeField()

    def __str__(self):
        return str(self.user_ip) + " - " + str(self.last_submitted)


class UserPOSTSubmissionWarning(models.Model):
    """
    Every time a user tries to send a foop too fast, the event will be
    recorded here, for admin review later
    """

    user_ip = models.GenericIPAddressField()
    last_submitted = models.DateTimeField()
    submit_attempt = models.DateTimeField()

    def __str__(self):
        return (
            str(self.user_ip)
            + ": "
            + str(self.last_submitted)
            + " - "
            + str(self.submit_attempt)
        )


class BoopReport(models.Model):
    boop = models.ForeignKey(Boop, on_delete=models.CASCADE)
    report_reason = models.TextField(max_length=500)
    report_ts = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.boop.boop_text[0:30] + " - " + self.report_reason[0:30]
