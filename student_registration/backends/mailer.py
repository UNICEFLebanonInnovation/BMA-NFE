

import logging
from smtplib import SMTPException


logger = logging.getLogger('helpdesk')


def send_messaage(subject, text, sender, recipients, fail_silently=True):
    from django.core.mail import EmailMultiAlternatives

    msg = EmailMultiAlternatives(subject, text,
                                 sender,
                                 recipients)
    try:
        return msg.send()
    except SMTPException as e:
        logger.exception('SMTPException raised while sending email to {}'.format(recipients))
        if not fail_silently:
            raise e
        return 0
