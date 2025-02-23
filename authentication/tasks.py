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
    """
    Send email verification link to the user registered email
    """
    notifier = utils.AuthNotification()
    # trigger email notofication
    if notifier is not None:
        notifier.verify_email_notification(data, domain_name)
        
@shared_task(name="send_password_reset_link")        
def send_password_reset_link(data, domain_name):
    """
    Send password reset ink to the user
    """
    notifier = utils.AuthNotification()
    # trigger email notofication
    if notifier is not None:
        notifier.password_reset_notification(data, domain_name)
        
@shared_task(name="send_password_change_confirmation")
def send_password_change_confirmation(data, name):
    """
    Send password change confirmation email
    """
    # trigger email notification
    notifier = utils.AuthNotification()
    if notifier is not None:
        notifier.password_confirm_notification(data)