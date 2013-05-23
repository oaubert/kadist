# -*- coding: utf-8 -*-

import sys
import re

from django.core.management.base import BaseCommand, CommandError

from kadist.models import Artist, Work
from rake import RakeKeywordExtractor

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
                    title = data.get('Title', '')
                    year = 0
                    m = re.search('(.+)\s*\((\d+)', title)
                    if m:
                        title = m.group(1).strip()
                        year = long(m.group(2))
                    w = Work(title=title,
                             year=year,
                             worktype=data.get('Work type', ''),
                             technique=data.get('Technique', ''),
                             dimensions=data.get('Measurements', ''),
                             description=data.get('Work Description', ''))

                    # Only take the first 2 words
                    cname = " ".join(data.get('Creator', "").split()[:2])
                    try:
                        creator = Artist.objects.get(name=cname)
                    except Artist.DoesNotExist:
                        # Have to create one
                        creator = Artist(name=cname, description=data.get('Artist Description', ''))
                        creator.save()

                    w.creator = creator
                    w.save()
                    tags = list(t.strip() for t in re.split('\s*,\s*', data.get('Tags', '')))
                    w.tags.add(*tags)
                    data = {}

                if field == 'Description':
                    data['Artist Description'], data['Work Description'] = value.split('||', 2)

                data[field] = value
            
    def _import_works_from_xls(self, filename):
        """Import from a xls file.
        """
        self.stdout.write("** Importing catalogue\n")
        rake = RakeKeywordExtractor()

        import xlrd
        book = xlrd.open_workbook(filename)
        s = book.sheet_by_index(0)
        header = s.row_values(0)
        
        FIRSTNAME = 'Main Artist First Name'
        SURNAME = 'Main Artist Surname'
	TITLE = 'Main Title'
	DATE = 'Main Date'
	COUNTRY = 'Artist Country of Birth'
	DESCRIPTION = 'About the artwork'

        for n in range(1, s.nrows - 1):
            self.stdout.write("[%d]" % n)
            self.stdout.flush()
            row = s.row_values(n)
            data = dict(zip(header, row))

            year = re.findall('(\d+)', data[DATE])
            if year:
                year = year[0]
            else:
                self.stdout.write("YEAR ? %s\n" % data[DATE])
                year = 0
            w = Work(title=data[TITLE].strip(),
                     year=year,
                     description=data[DESCRIPTION])
            # Only take the first 2 words
            cname = data[FIRSTNAME] + " " + data[SURNAME]
            try:
                creator = Artist.objects.get(name=cname)
            except Artist.DoesNotExist:
                # Have to create one
                creator = Artist(name=cname, country=data[COUNTRY])
                creator.save()

            w.creator = creator
            w.save()

            # Extract tags from descriptions
            tags = [ k for k in rake.extract(data[DESCRIPTION], incl_scores=False) if re.match('^\w+$', k) ]
            self.stdout.write(("Tags: %s\n" % ", ".join(tags)).encode('utf-8'))
            w.tags.add(*tags)

    def handle(self, *args, **options):
        if not args:
            self.print_help(sys.argv[0], sys.argv[1])
            return
        command = args[0]
        args = args[1:]
        dispatcher = {
            'import': self._import_works_from_txt,
            'xls': self._import_works_from_xls,
            }
        m = dispatcher.get(command)
        if m is not None:
            m(*args)
        else:
            raise CommandError("Unknown command")

        self.stdout.write("\nDone.\nDO NOT FORGET TO RUN rebuild_index !!!\n")
