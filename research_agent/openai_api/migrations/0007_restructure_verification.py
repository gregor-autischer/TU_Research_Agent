# Generated migration for restructured Verification model and PaperVerificationCache

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('openai_api', '0006_add_verification_model'),
    ]

    operations = [
        # Create PaperVerificationCache model
        migrations.CreateModel(
            name='PaperVerificationCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField(max_length=1000, unique=True, db_index=True)),
                ('title', models.CharField(max_length=500)),
                ('authors', models.CharField(max_length=500)),
                ('date', models.CharField(max_length=20)),
                ('verification_result', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        
        # Rename fields in Verification model
        migrations.RenameField(
            model_name='verification',
            old_name='paper_ratings',
            new_name='textual_verification',
        ),
        migrations.RenameField(
            model_name='verification',
            old_name='link_verification',
            new_name='paper_verifications',
        ),
        
        # Remove obsolete fields
        migrations.RemoveField(
            model_name='verification',
            name='bibtex_verification',
        ),
    ]
