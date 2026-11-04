from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='CareerProfile', fields=[('id',models.BigAutoField(primary_key=True,serialize=False, auto_created=True, verbose_name='ID')),('name',models.CharField(max_length=120)),('resume',models.FileField(upload_to='career_resumes/%Y/%m/',blank=True,null=True)),('extracted_skills',models.JSONField(default=list,blank=True)),('interests',models.JSONField(default=list,blank=True)),('target_career',models.CharField(max_length=180,blank=True)),('education',models.CharField(max_length=250,blank=True)),('experience_years',models.FloatField(default=0)),('projects',models.TextField(blank=True)),('certifications',models.TextField(blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('user',models.ForeignKey(to=settings.AUTH_USER_MODEL,on_delete=django.db.models.deletion.CASCADE,related_name='career_profiles'))],),
        migrations.CreateModel(name='CareerAnalysis', fields=[('id',models.BigAutoField(primary_key=True,serialize=False,auto_created=True,verbose_name='ID')),('snapshot',models.JSONField(default=dict)),('roadmap_progress',models.JSONField(default=dict,blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),('profile',models.ForeignKey(to='careers.careerprofile',on_delete=django.db.models.deletion.CASCADE,related_name='analyses'))], options={'ordering':['-created_at']}),
    ]
