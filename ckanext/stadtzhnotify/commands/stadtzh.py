import ckan.lib.cli
import sys

class StadtzhCommand(ckan.lib.cli.CkanCommand):
    '''Command to send email notifications for activities

Usage:

# General usage
paster --plugin=ckanext-stadtzh-notify <command> -c <path to config file>

# Show this help
paster stadtzh help

'''
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def command(self):
        # load pylons config
        self._load_config()
        options = {
            'help': self.helpCmd,
        }

        try:
            cmd = self.args[0]
            options[cmd](*self.args[1:])
        except KeyError:
            self.helpCmd()
            sys.exit(1)

    def helpCmd(self):
        print self.__doc__
