# -*- coding: utf-8 -*-

import sys
import re
import itertools

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
import urllib2
from BeautifulSoup import BeautifulSoup

from kadist.models import Artist, Work, ProfileData, SimilarityMatrix, MajorTag, compare, TagSimilarity
from rake import RakeKeywordExtractor

class Command(BaseCommand):
    args = '[command] [param]'
    help = """Administration commands for Kadist catalogue
  import <txt file> : import the catalogue from a txt file
  xls <xls file> : import the catalogue from a xls file
  acsv <csv file> : import the artists from a csv file
  wcsv <csv file> : import the works from a csv file
  similarity PROFILEID LABEL MAXITEMS=5 MAJMIN=.5 MINMAJ=.5 MINMIN=.3
  dump PROFILEID : dump similarity matrix as csv
  tagsimilarity [THRESHOLD=.8]
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
            cname = (data[FIRSTNAME].capitalize() + " " + data[SURNAME].capitalize()).strip()
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

    def _import_artists_from_csv(self, filename):
        """Import artists from a csv file.
        """
        self.stdout.write("** Importing artists from %s\n" % filename)

        import csv
        reader = csv.reader(open(filename, 'r'))
        header = reader.next()

        AID = 'Nid'
        FIRSTNAME = 'First name'
        SURNAME = 'Last name'
	DESCRIPTION = 'Corps'
        URL = 'Chemin'

        for n, row in enumerate(reader):
            self.stdout.write("[%d]" % n)
            self.stdout.flush()
            data = dict(zip(header, row))

            cname = (data[FIRSTNAME].strip().capitalize() + " " + data[SURNAME].strip().capitalize()).strip()
            try:
                a = Artist(pk=long(data[AID]),
                           name=cname,
                           description=data[DESCRIPTION],
                           url='http://www.kadist.org' + data[URL])
                a.save()
            except IntegrityError, e:
                self.stderr.write("Integrity error: %s\n" % unicode(e))

    def _import_works_from_csv(self, filename):
        """Import works from a csv file.
        """
        self.stdout.write("** Importing works from %s\n" % filename)

        import csv
        reader = csv.reader(open(filename, 'r'))
        header = reader.next()

        TITLE = ""
        WID = "Nid"
        AID = "people nids"
        CREATOR = "Personnes"
        DATE = "Work Date"
        DESCRIPTION = "Corps"
        URL = "Chemin"
        TYPE = "Moyen"
        IMG = "Images"
        COLLECTION = "Collection"

        for n, row in enumerate(reader):
            self.stdout.write("[%d]" % n)
            self.stdout.flush()
            data = dict(zip(header, row))

            try:
                year = long(data[DATE])
            except ValueError:
                year = 0
            w = Work(pk=long(data[WID]),
                     title=data[TITLE].strip(),
                     year=year,
                     worktype=data[TYPE],
                     url='http://www.kadist.org' + data[URL],
                     description=data[DESCRIPTION])
                     # FIXME: handle Collection field

            if data[AID]:
                aid = long(data[AID].split(',')[0].strip())
                try:
                    creator = Artist.objects.get(pk=aid)
                    w.creator = creator
                    w.save()
                except Artist.DoesNotExist:
                    # Have to create one
                    self.stderr.write("Error: missing artist for %s - %s\n" % (data[WID], data[TITLE]))

    def _similarity(self, profileid=None, label="", maxitems=5, majmin=.5, minmaj=.5, minmin=.3):
        maxitems = float(maxitems)
        majmin = float(majmin)
        minmaj = float(minmaj)
        minmin = float(minmin)
        if not label:
            label = "Similarity profile (maxitems=%.02f/majmin=%.02f/minmaj=%.02f/minmin=%.02f)" % (maxitems, majmin, minmaj, minmin)
        if profileid is None:
            # List existing profiles
            self.stdout.write("List of profiles")
            for p in ProfileData.objects.all():
                self.stdout.write("#%s %s - MAXITEMS = %d - MAJMIN = %f - MINMAJ = %f - %d items\n" % (
                        p.profile,
                        p.name,
                        p.maxitems,
                        p.majmin,
                        p.minmaj,
                        SimilarityMatrix.objects.filter(profile=p.profile).count()))
            return

        # Delete previous data with the same profile
        SimilarityMatrix.objects.filter(profile=profileid).delete()
        ProfileData.objects.filter(profile=profileid).delete()

        profile = ProfileData(profile=profileid,
                              name=label,
                              maxitems=maxitems,
                              majmin=majmin,
                              minmaj=minmaj)
        profile.save()

        # Generate data
        tagged = [ w for w in Work.objects.all() if w.major_tags.all() ]
        total = len(tagged)
        for i, w in enumerate(tagged):
            self.stderr.write("[%d/%d] %s" % (i, total, unicode(w)))
            for ind, d in enumerate(tagged):
                cell = SimilarityMatrix(origin=w,
                                        destination=d,
                                        profile=profileid,
                                        value=w.similarity(d, maxitems, majmin, minmaj, minmin))
                cell.save()
                self.stderr.write("  %d / %d / %d %f - %s\r" % (ind, i, total, cell.value, unicode(d)))

    def _dump_similarity(self, profileid=None):
        # Generate data
        tagged = [ w for w in Work.objects.all() if w.major_tags.all() ]
        self.stdout.write(" " + ";".join(unicode(w).replace(";", " ").replace('"', '') for w in tagged))
        for w in tagged:
            self.stdout.write( unicode(w).replace(";", " ").replace('"', '') + ";"
                               + ";".join( "%.04f" % (SimilarityMatrix.objects.filter(origin=w.id, destination=d.id, profile=profileid).values_list('value', flat=True) or [0])[0]
                                           for d in tagged) )

    def _tag_similarity(self, threshold=.8):
        """Compute tag similarity.
        """
        TagSimilarity.objects.all().delete()
        threshold = float(threshold)
        tags = [ t.name for t in MajorTag.objects.all() ]
        total = len(tags)
        for n, ref in enumerate(tags):
            self.stderr.write("%d\t / %d\r" % (n+1, total))
            self.stderr.flush()
            similar = [ t.name for t in MajorTag.objects.all() if compare(ref, t.name) >= threshold ]
            if similar:
                item = TagSimilarity(ref=ref,
                                     threshold=threshold,
                                     similar=",".join(similar),
                                     count=len(similar))
                item.save()

    def _scrape(self):
        """Scrape img urls from Kadist website.
        """
        for w in itertools.chain(Work.objects.filter(imgurl=""),
                                Artist.objects.filter(imgurl="")):
            if w.url:
                self.stdout.write("[%d]" % w.pk)
                self.stdout.flush()
                try:
                    soup = BeautifulSoup(urllib2.urlopen(w.url).read())
                    w.imgurl = soup.find('figure').find('img').get('src')
                    w.save()
                except AttributeError:
                    pass

    def handle(self, *args, **options):
        if not args:
            self.print_help(sys.argv[0], sys.argv[1])
            return
        command = args[0]
        args = args[1:]
        dispatcher = {
            'import': self._import_works_from_txt,
            'xls': self._import_works_from_xls,
            'wcsv': self._import_works_from_csv,
            'acsv': self._import_artists_from_csv,
            'scrape': self._scrape,
            'similarity': self._similarity,
            'dump': self._dump_similarity,
            'tagsimilarity': self._tag_similarity,
            }
        m = dispatcher.get(command)
        if m is not None:
            m(*args)
        else:
            raise CommandError("Unknown command")

