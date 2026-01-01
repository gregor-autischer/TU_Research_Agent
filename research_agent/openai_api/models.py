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
    system_prompt = models.TextField(blank=True, default='')

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


class PaperVerification(models.Model):
    """Individual paper verification results."""
    verification = models.ForeignKey('Verification', on_delete=models.CASCADE, related_name='paper_verification_details')
    paper_index = models.IntegerField()
    title = models.CharField(max_length=500)
    link = models.URLField(max_length=1000, blank=True, default='')
    claimed_authors = models.CharField(max_length=500, blank=True, default='')
    claimed_date = models.CharField(max_length=50, blank=True, default='')
    
    # OpenAlex metadata
    openalex_metadata = models.JSONField(null=True, blank=True)
    verified_metadata = models.JSONField(null=True, blank=True)
    
    # Content verification
    content_fetch = models.JSONField(null=True, blank=True)
    content_verification = models.JSONField(null=True, blank=True)
    
    # Paper quality assessment (from LLM)
    paper_quality = models.JSONField(null=True, blank=True)
    
    # Summary evaluation (from LLM)
    summary_evaluation = models.JSONField(null=True, blank=True)
    
    # Overall assessment
    overall_assessment = models.TextField(blank=True, default='')
    
    # Scores
    credibility_score = models.FloatField(default=5.0)
    credibility_notes = models.TextField(blank=True, default='')
    overall_quality = models.FloatField(default=5.0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['paper_index']

    def __str__(self):
        return f"Paper verification for {self.title[:50]}"


class Verification(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='verifications')
    confidence_score = models.FloatField()  # 0-100
    textual_verification = models.JSONField()  # Textual response analysis
    summary = models.TextField()  # Human-readable summary
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Verification for message {self.message.id} (Score: {self.confidence_score})"
    
    def get_paper_verifications(self):
        """Helper method to get paper verifications as list of dicts (for API compatibility)."""
        return [
            {
                'paper_index': pv.paper_index,
                'title': pv.title,
                'link': pv.link,
                'claimed_authors': pv.claimed_authors,
                'claimed_date': pv.claimed_date,
                'openalex_metadata': pv.openalex_metadata,
                'verified_metadata': pv.verified_metadata,
                'content_fetch': pv.content_fetch,
                'content_verification': pv.content_verification,
                'paper_quality': pv.paper_quality,
                'summary_evaluation': pv.summary_evaluation,
                'overall_assessment': pv.overall_assessment,
                'credibility_score': pv.credibility_score,
                'credibility_notes': pv.credibility_notes,
                'overall_quality': pv.overall_quality,
            }
            for pv in self.paper_verification_details.all()
        ]
