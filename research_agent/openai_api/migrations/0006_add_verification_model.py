# Generated migration for Verification model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('openai_api', '0005_add_bibtex_to_paper'),
    ]

    operations = [
        migrations.CreateModel(
            name='Verification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confidence_score', models.FloatField()),
                ('paper_ratings', models.JSONField()),
                ('link_verification', models.JSONField()),
                ('bibtex_verification', models.JSONField()),
                ('hallucination_warnings', models.JSONField()),
                ('summary', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verifications', to='openai_api.message')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
