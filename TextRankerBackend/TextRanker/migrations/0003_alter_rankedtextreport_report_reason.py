# Generated by Django 4.2.3 on 2023-07-28 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TextRanker', '0002_alter_rankedtext_text_string'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rankedtextreport',
            name='report_reason',
            field=models.TextField(max_length=500),
        ),
    ]
