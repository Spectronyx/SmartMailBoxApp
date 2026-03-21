from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0004_email_ai_processed'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='message_id',
            field=models.CharField(blank=True, help_text='RFC 2822 Message-ID header for deduplication', max_length=500, null=True),
        ),
        migrations.AddIndex(
            model_name='email',
            index=models.Index(fields=['mailbox', 'message_id'], name='emails_emai_mailbox_msg_idx'),
        ),
        migrations.AddConstraint(
            model_name='email',
            constraint=models.UniqueConstraint(
                condition=models.Q(message_id__isnull=False),
                fields=['mailbox', 'message_id'],
                name='unique_message_per_mailbox',
            ),
        ),
    ]
