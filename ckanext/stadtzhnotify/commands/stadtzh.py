#coding: utf-8

import sys
import os
import datetime
import smtplib
import uuid
import ckan.lib.cli
import paste.deploy.converters
import logging
from time import time
from pylons import config
from email.mime.text import MIMEText
from email.header import Header
from email import Utils
from urlparse import urljoin
from pylons.i18n.translation import _
from ckan import model, __version__
from ckan.lib.helpers import url_for

log = logging.getLogger(__name__)


class MailerException(Exception):
    pass


class StadtzhCommand(ckan.lib.cli.CkanCommand):
    '''Command to send email notifications for activities

    Usage:

    # General usage
    paster --plugin=ckanext-stadtzh-notify <command> -c <path to config file>

    # Show this help
    paster stadtzh help

    # Send a mail with metadata diffs from today (default) or <days> ago
    paster stadtzh send-diffs [<days>]

    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    diff_path = config.get('metadata.diffpath', '/usr/lib/ckan/diffs')

    def command(self):
        # load pylons config
        self._load_config()
        options = {
            'help': self.helpCmd,
            'send-diffs': self.sendDiffsCmd,
        }

        try:
            cmd = self.args[0]
            options[cmd](*self.args[1:])
        except KeyError:
            self.helpCmd()
            sys.exit(1)

    def helpCmd(self):
        print self.__doc__

    def sendDiffsCmd(self, days=1):
        days = int(days)
        diff_date = datetime.date.today() - datetime.timedelta(days)
        body = self._get_body(diff_date)

        # no body, no mail
        if body:
            recipient_email = config.get('recipient_email')
            subject = "CKAN Diffs %s" % (str(diff_date.strftime("%d.%m.%y")))
            headers = {}
            mail_from = config.get('smtp.mail_from', 'ckan@zuerich.ch')
            msg = MIMEText(body, 'html', 'utf-8')
            for k, v in headers.items(): msg[k] = v
            subject = Header(subject.encode('utf-8'), 'utf-8')
            msg['Subject'] = subject
            msg['From'] = _("<%s>") % (mail_from)
            recipient = u"<%s>" % (recipient_email)
            msg['To'] = Header(recipient, 'utf-8')
            msg['Date'] = Utils.formatdate(time())
            msg['X-Mailer'] = "CKAN %s" % __version__

            # Send the email using Python's smtplib.
            smtp_connection = smtplib.SMTP()
            if 'smtp.test_server' in config:
                # If 'smtp.test_server' is configured we assume we're running tests,
                # and don't use the smtp.server, starttls, user, password etc. options.
                smtp_server = config['smtp.test_server']
                smtp_starttls = False
                smtp_user = None
                smtp_password = None
            else:
                smtp_server = config.get('smtp.server', 'localhost')
                smtp_starttls = paste.deploy.converters.asbool(
                        config.get('smtp.starttls'))
                smtp_user = config.get('smtp.user')
                smtp_password = config.get('smtp.password')
            smtp_connection.connect(smtp_server)
            try:
                # smtp_connection.set_debuglevel(True)

                # Identify ourselves and prompt the server for supported features.
                smtp_connection.ehlo()

                # If 'smtp.starttls' is on in CKAN config, try to put the SMTP
                # connection into TLS mode.
                if smtp_starttls:
                    if smtp_connection.has_extn('STARTTLS'):
                        smtp_connection.starttls()
                        # Re-identify ourselves over TLS connection.
                        smtp_connection.ehlo()
                    else:
                        raise MailerException("SMTP server does not support STARTTLS")

                # If 'smtp.user' is in CKAN config, try to login to SMTP server.
                if smtp_user:
                    assert smtp_password, ("If smtp.user is configured then "
                            "smtp.password must be configured as well.")
                    smtp_connection.login(smtp_user, smtp_password)

                smtp_connection.sendmail(mail_from, [recipient_email], msg.as_string())
                log.info("Sent email to {0}".format(recipient_email))

            except smtplib.SMTPException, e:
                msg = '%r' % e
                log.exception(msg)
                raise MailerException(msg)
            finally:
                smtp_connection.quit()
        else:
            log.info("No diffs to send on %s" % (str(diff_date)))

    def _get_body(self, diff_date):
        body = ''
        diff_files = [f for f in os.listdir(self.diff_path) if f.startswith(str(diff_date))]
        for file_name in diff_files:
            with open(os.path.join(self.diff_path, file_name), 'r') as diff:
                body += diff.read()
                log.debug('Diff read with filename: ' + file_name)
        return body
