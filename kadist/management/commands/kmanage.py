# -*- coding: utf-8 -*-

import sys

from django.core.management.base import BaseCommand, CommandError
from django.core import exceptions

from kadist.models import Artist, Work

class Command(BaseCommand):
    args = '[command] [param]'
    help = """Administration commands for Kadist catalogue
  import <txt file> : import the catalogue from a txt file
"""
    def _import_works_from_txt(self, filename):
        """Import from a txt file.
        """
        self.stdout.write("** Importing catalogue\n")
        data = {}

        with open(filename, 'r') as f:
            for l in f.readlines():
                l = l.strip()
                if not l:
                    continue
                print l
                field, value = l.split(':', 1)
                value = value.strip()
                if field == 'Index' and data:
                    # Save previous work
                    w = Work(title=data.get('Title', ""),
                             worktype=data.get('Work type', ''),
                             technique=data.get('Technique', ''),
                             dimensions=data.get('Measurements', ''),
                             description=data.get('Description', ''))

                    # Only take the first 2 words
                    cname = " ".join(data.get('Creator', "").split()[:2])
                    try:
                        creator = Artist.objects.get(name=cname)
                    except Artist.DoesNotExist:
                        # Have to create one
                        creator = Artist(name=cname)
                        creator.save()

                    w.creator = creator
                    w.save()
                    w.tags.add( t for t in data.get('Tags', '').split(',') )
                    data = {}

                data[field] = value
            
    def handle(self, *args, **options):
        if not args:
            self.print_help(sys.argv[0], sys.argv[1])
            return
        command = args[0]
        args = args[1:]
        dispatcher = {
            'import': self._import_works_from_txt,
            }
        m = dispatcher.get(command)
        if m is not None:
            m(*args)
        else:
            raise CommandError("Unknown command")

        self.stdout.write("\nDone.\nDO NOT FORGET TO RUN rebuild_index !!!\n")
