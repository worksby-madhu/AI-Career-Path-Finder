from django.conf import settings
from django.db import models

class CareerProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='career_profiles')
    name = models.CharField(max_length=120)
    resume = models.FileField(upload_to='career_resumes/%Y/%m/', blank=True, null=True)
    extracted_skills = models.JSONField(default=list, blank=True)
    interests = models.JSONField(default=list, blank=True)
    target_career = models.CharField(max_length=180, blank=True)
    education = models.CharField(max_length=250, blank=True)
    experience_years = models.FloatField(default=0)
    projects = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f'{self.name} ({self.user})'

class CareerAnalysis(models.Model):
    profile = models.ForeignKey(CareerProfile, on_delete=models.CASCADE, related_name='analyses')
    snapshot = models.JSONField(default=dict)
    roadmap_progress = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']
    def __str__(self): return f'{self.profile.name} analysis {self.pk}'
