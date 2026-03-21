"""
IMAP Service for fetching emails from remote servers.

This module provides the logic to connect to IMAP servers,
authenticate, search for new emails, and parse them.
"""

import imaplib
import email
from email.header import decode_header
import logging
from typing import List, Optional
from django.utils import timezone as django_timezone

logger = logging.getLogger(__name__)

class IMAPService:
    """
    Handles connection and fetching from IMAP servers.
    """
    
    def __init__(self, mailbox):
        """
        Initialize with a Mailbox instance.
        """
        self.mailbox = mailbox
        self.mail = None
    
    def connect(self):
        """
        Establish connection to the IMAP server.
        """
        try:
            if self.mailbox.use_ssl:
                self.mail = imaplib.IMAP4_SSL(
                    self.mailbox.imap_server, 
                    self.mailbox.imap_port or 993
                )
            else:
                self.mail = imaplib.IMAP4(
                    self.mailbox.imap_server, 
                    self.mailbox.imap_port or 143
                )
            
            username = self.mailbox.username or self.mailbox.email_address
            self.mail.login(username, self.mailbox.password)
            return True
        except Exception as e:
            logger.error(f"IMAP Connection failed for {self.mailbox.email_address}: {e}")
            return False
    
    def disconnect(self):
        """
        Close connection.
        """
        if self.mail:
            try:
                self.mail.logout()
            except Exception:
                pass
    
    def fetch_new_emails(self) -> int:
        """
        Search and fetch new emails.
        
        Returns:
            Number of new emails created.
        """
        if not self.connect():
            return 0
        
        try:
            self.mail.select('INBOX')
            
            # First sync: fetch ALL emails (full history)
            # Subsequent syncs: fetch emails since last sync date
            if self.mailbox.last_synced_at:
                since_date = self.mailbox.last_synced_at.strftime("%d-%b-%Y")
                status, messages = self.mail.search(None, f'(SINCE {since_date})')
            else:
                status, messages = self.mail.search(None, 'ALL')
            
            if status != 'OK':
                return 0
            
            new_email_ids = messages[0].split()
            logger.info(f"Found {len(new_email_ids)} emails for {self.mailbox.email_address}")
            
            created_count = 0
            for msg_id in new_email_ids:
                if self._process_message(msg_id):
                    created_count += 1
            
            return created_count
            
        except Exception as e:
            logger.error(f"Error fetching emails for {self.mailbox.email_address}: {e}")
            return 0
        finally:
            self.disconnect()
    
    def _process_message(self, msg_id) -> bool:
        """
        Fetch, parse and save a single message (no AI pipeline here).
        """
        from emails.models import Email
        try:
            status, data = self.mail.fetch(msg_id, '(RFC822)')
            if status != 'OK':
                return False
            
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Extract headers
            subject = self._decode_header(msg.get("Subject", "(No Subject)"))
            sender = self._decode_header(msg.get("From", ""))
            email_message_id = (msg.get("Message-ID") or "").strip()
            
            # Parse date
            date_str = msg.get("Date")
            try:
                received_at = email.utils.parsedate_to_datetime(date_str) if date_str else django_timezone.now()
            except Exception:
                received_at = django_timezone.now()
            
            # Extract Body
            body = self._get_email_body(msg)
            
            # Dedup: use Message-ID if available, else fall back to subject+sender+date
            if email_message_id:
                if Email.objects.filter(mailbox=self.mailbox, message_id=email_message_id).exists():
                    return False
            else:
                if Email.objects.filter(mailbox=self.mailbox, subject=subject, sender=sender, received_at=received_at).exists():
                    return False

            email_obj = Email.objects.create(
                mailbox=self.mailbox,
                message_id=email_message_id or None,
                subject=subject,
                sender=sender,
                body=body,
                received_at=received_at
            )
            
            # Extract and save attachments
            self._save_attachments(msg, email_obj)
            return True
            
        except Exception as e:
            logger.error(f"Error processing message {msg_id}: {e}")
            return False
    
    def _decode_header(self, header_value) -> str:
        """Decode MIME encoded headers robustly."""
        from emails.utils.text_processing import decode_headers
        return decode_headers(header_value)
    
    def _get_email_body(self, msg) -> str:
        """Extract body (prefers HTML, falls back to plain text)."""
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
                    try:
                        body_html = part.get_payload(decode=True).decode()
                    except Exception:
                        body_html = part.get_payload(decode=True).decode('iso-8859-1', errors='replace')
                elif content_type == "text/plain" and not body_html:
                    try:
                        body_plain = part.get_payload(decode=True).decode()
                    except Exception:
                        body_plain = part.get_payload(decode=True).decode('iso-8859-1', errors='replace')
        else:
            content_type = msg.get_content_type()
            try:
                payload = msg.get_payload(decode=True).decode()
            except Exception:
                payload = msg.get_payload(decode=True).decode('iso-8859-1', errors='replace')
                
            if content_type == "text/html":
                body_html = payload
            else:
                body_plain = payload

        # Prefer HTML, but strip dangerous tags
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
            return bleach.clean(
                body_html, 
                tags=allowed_tags, 
                attributes=allowed_attrs, 
                css_sanitizer=css_sanitizer, 
                strip=True
            )
            
        return body_plain

    def _save_attachments(self, msg, email_obj):
        """Extract and save metadata for each attachment in the message."""
        from emails.models import Attachment

        if not msg.is_multipart():
            return

        for part in msg.walk():
            filename = part.get_filename()
            if filename:
                filename = self._decode_header(filename)
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
