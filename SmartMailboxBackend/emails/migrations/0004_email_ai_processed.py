from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0003_email_snippet'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='ai_processed',
            field=models.BooleanField(default=False, help_text='Whether this email has been processed by the AI pipeline'),
        ),
        migrations.AddIndex(
            model_name='email',
            index=models.Index(fields=['mailbox', 'ai_processed', '-received_at'], name='emails_emai_mailbox_ai_idx'),
        ),
    ]
