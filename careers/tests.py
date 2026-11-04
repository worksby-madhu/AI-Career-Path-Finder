from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import CareerProfile, CareerAnalysis

class CareerProfileAccessTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user(username='alice',password='safe-password-123')
        self.other=User.objects.create_user(username='bob',password='safe-password-123')
        self.profile=CareerProfile.objects.create(user=self.user,name='Python Plan')
        self.analysis=CareerAnalysis.objects.create(profile=self.profile,snapshot={'target_career':'Python Developer'})
    def test_dashboard_requires_login(self):
        response=self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code,302)
    def test_user_cannot_open_other_users_analysis(self):
        self.client.login(username='bob',password='safe-password-123')
        response=self.client.get(reverse('open_analysis',args=[self.analysis.pk]))
        self.assertEqual(response.status_code,404)
    def test_user_can_open_own_history(self):
        self.client.login(username='alice',password='safe-password-123')
        response=self.client.get(reverse('profile_history',args=[self.profile.pk]))
        self.assertEqual(response.status_code,200)
