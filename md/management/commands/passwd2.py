#! -*- encoding:utf-8 -*-

from django.core.management.base import BaseCommand, CommandError, AppCommand
from django.contrib.auth.models import User
from pdb import set_trace as bp
from optparse import make_option

class Command(BaseCommand):

    option_list = AppCommand.option_list + (\
        make_option('--password', '-n', action='store', dest='password', \
            default='sample', \
            help=u'要修改的用户密码。'),
    )

    help = u"passwd admin --password 123456"

    requires_model_validation = False

    def handle(self, *args, **options):
        if len(args) > 1:
            raise CommandError("need exactly one or zero arguments for username")
        # elif 0 == len(args):
            # raise CommandError(u"")

        if args:
            username = args[0]

        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError("user %s does not exist" % username)

        print("Changing password for user: %s" % u.username)
        p1 = options.get("password")

        u.set_password(p1)
        u.save()

        return "Password changed successfully for user %s\n" % u.username
