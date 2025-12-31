from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    openai_api_key = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, default='New Conversation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class Paper(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='papers')
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500)
    date = models.CharField(max_length=20)
    paper_type = models.CharField(max_length=50, default='PDF')
    link = models.URLField(max_length=1000, blank=True, default='')
    summary = models.TextField()
    bibtex = models.TextField(blank=True, default='')
    in_context = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title[:50]}..."


class Verification(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='verifications')
    confidence_score = models.FloatField()  # 0-100
    paper_ratings = models.JSONField()  # List of paper ratings with details
    link_verification = models.JSONField()  # List of link check results
    bibtex_verification = models.JSONField()  # List of bibtex check results
    hallucination_warnings = models.JSONField()  # List of hallucination warnings
    summary = models.TextField()  # Human-readable summary
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Verification for message {self.message.id} (Score: {self.confidence_score})"
