"""
Gmail API Service using stored OAuth2 tokens.

Uses google-api-python-client to fetch emails from the Gmail API.
"""

import logging
import base64
from email import message_from_bytes
from django.utils import timezone
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from django.conf import settings

logger = logging.getLogger(__name__)


class GmailService:
    """
    Fetches emails from Gmail using stored OAuth2 access tokens.
    """

    def __init__(self, mailbox, user_profile):
        """
        Args:
            mailbox: Mailbox model instance
            user_profile: UserProfile with google_access_token/refresh_token
        """
        self.mailbox = mailbox
        self.profile = user_profile
        self.service = self._get_service()

    def _get_service(self):
        """Build the Gmail API service object."""
        try:
            creds = Credentials(
                token=self.profile.google_access_token,
                refresh_token=self.profile.google_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
                client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
                scopes=['https://www.googleapis.com/auth/gmail.readonly']
            )
            return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            logger.error(f"Failed to build Gmail service for {self.profile.google_email}: {e}")
            return None

    def fetch_new_messages(self) -> int:
        """
        Fetch new messages since last sync.
        
        Returns:
            Number of new messages processed.
        """
        if not self.service:
            return 0

        try:
            # Search for messages since last_synced_at or just unread ones
            # Query format: "is:unread" or "after:YYYY/MM/DD"
            query = "is:unread"
            if self.mailbox.last_synced_at:
                # Gmail query date format is YYYY/MM/DD
                sync_date = self.mailbox.last_synced_at.strftime("%Y/%m/%d")
                query += f" after:{sync_date}"

            results = self.service.users().messages().list(userId='me', q=query, maxResults=5).execute()
            messages = results.get('messages', [])

            count = 0
            for msg_meta in messages:
                if self._process_message(msg_meta['id']):
                    count += 1
            
            return count

        except Exception as e:
            logger.error(f"Error fetching Gmail messages: {e}")
            return 0

    def _process_message(self, msg_id) -> bool:
        """Fetch full message content, parse and save to Email model."""
        from emails.models import Email
        from emails.services.pipeline_runner import run_full_pipeline

        try:
            msg_data = self.service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
            raw_bytes = base64.urlsafe_b64decode(msg_data['raw'].encode('ASCII'))
            msg = message_from_bytes(raw_bytes)

            # Basic parsing
            from emails.utils.text_processing import decode_headers
            subject = decode_headers(msg.get('Subject', '(No Subject)'))
            sender = decode_headers(msg.get('From', ''))
            received_at = timezone.now() # Should ideally parse from headers

            # Body extraction (hybrid HTML/Text)
            import bleach
            body_html = ""
            body_plain = ""
            
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if "attachment" in content_disposition:
                        continue
                        
                    if content_type == "text/html":
                        body_html = part.get_payload(decode=True).decode(errors='replace')
                    elif content_type == "text/plain":
                        body_plain = part.get_payload(decode=True).decode(errors='replace')
            else:
                content_type = msg.get_content_type()
                if content_type == "text/html":
                    body_html = msg.get_payload(decode=True).decode(errors='replace')
                else:
                    body_plain = msg.get_payload(decode=True).decode(errors='replace')

            if body_html:
                import re
                from bleach.css_sanitizer import CSSSanitizer
                
                # Remove <style> and <script> contents entirely so they don't show as text
                body_html = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', body_html, flags=re.DOTALL | re.IGNORECASE)
                
                allowed_tags = [
                    'a', 'b', 'i', 'u', 'strong', 'em', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                    'br', 'hr', 'div', 'span', 'img', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 
                    'tfoot', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'dl', 'dt', 'dd', 
                    's', 'sub', 'sup', 'cite', 'abbr', 'address', 'center', 'font'
                ]
                
                # CSS Sanitizer allows specific properties within style attributes
                css_sanitizer = CSSSanitizer(allowed_css_properties=[
                    'color', 'background-color', 'font-size', 'font-weight', 'text-align', 
                    'padding', 'margin', 'border', 'width', 'height', 'line-height', 
                    'text-decoration', 'font-family', 'display', 'border-collapse'
                ])
                
                allowed_attrs = {
                    '*': ['class', 'style', 'id'],
                    'a': ['href', 'target', 'title', 'rel'],
                    'img': ['src', 'alt', 'width', 'height', 'loading', 'style'],
                    'table': ['border', 'cellpadding', 'cellspacing', 'width', 'align'],
                    'font': ['color', 'face', 'size']
                }
                body = bleach.clean(
                    body_html, 
                    tags=allowed_tags, 
                    attributes=allowed_attrs, 
                    css_sanitizer=css_sanitizer, 
                    strip=True
                )
            else:
                body = body_plain

            # Save to database
            if not Email.objects.filter(mailbox=self.mailbox, subject=subject, sender=sender).exists():
                email_obj = Email.objects.create(
                    mailbox=self.mailbox,
                    subject=subject,
                    sender=sender,
                    body=body,
                    received_at=received_at
                )

                # Save attachments
                self._save_attachments(msg, email_obj)
                
                # Run the auto-pipeline asynchronously (Classification, Summarization, Tasks)
                from emails.tasks import process_email_pipeline
                process_email_pipeline.delay(email_obj.id)
                return True
            
            return False

        except Exception as e:
            logger.error(f"Error processing Gmail message {msg_id}: {e}")
            return False

    def _save_attachments(self, msg, email_obj):
        """Extract and save metadata for each attachment in the message."""
        from emails.models import Attachment
        
        if not msg.is_multipart():
            return

        for part in msg.walk():
            filename = part.get_filename()
            if filename:
                content_type = part.get_content_type()
                payload = part.get_payload(decode=True)
                
                if payload:
                    Attachment.objects.create(
                        email=email_obj,
                        filename=filename,
                        content_type=content_type,
                        size=len(payload)
                    )
                    logger.info(f"Saved attachment metadata: {filename} for email {email_obj.id}")

