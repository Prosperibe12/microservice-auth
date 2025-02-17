from __future__ import absolute_import, unicode_literals
from celery import shared_task

from authentication import utils, models

""" 
*****************************************
TASK FOR SENDING EMAIL NOTIFICATIONS 
*****************************************
"""
@shared_task(name="send_email_verification_link")
def send_email_verification_link(data, domain_name):
    """Send Email Notofication to the user"""
    notifier = utils.AuthNotification()
    # trigger email notofication
    if notifier is not None:
        notifier.register_email_notification(data, domain_name)