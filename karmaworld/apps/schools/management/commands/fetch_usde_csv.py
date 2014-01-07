import csv
import requests
import itertools as it

from bs4 import BeautifulSoup as BS
from urlparse import urljoin
from subprocess import call

from django.core.management.base import BaseCommand
from karmaworld.apps.schools.models import School

class Command(BaseCommand):
    args = '<destination>'
    USDE_LINK = 'http://ope.ed.gov/accreditation/GetDownloadFile.aspx'
    help = (""" Downloads data from US Department of Education.
                Supply a destination for the csv file to be written to. """)

    def handle(self, *args, **kwargs):

        if len(args) < 1:
            self.stdout.write('Provide a filename to save csv data into.\n')
            return

        filename = args[0]

        r = requests.get(self.USDE_LINK)
        # Ensure the page was retrieved with 200
        if not r.ok:
            r.raise_for_status()
    
        # Process the HTML with BeautifulSoup
        soup = BS(r.text)
        # Extract all the anchor links.
        a = soup.find_all('a')

        # Extract the HREFs from anchors.
        def get_href(anchor):
            return anchor.get('href')
        #a = map(get_href, a)

        # Filter out all but the Accreditation links.
        def contains_accreditation(link):
            return 'Accreditation' in link and 'zip' in link
        #a = filter(contains_accreditation, a)

        # do the above stuff with itertools
        a_iter = it.ifilter(contains_accreditation, it.imap(get_href, iter(a)))

        # Find the most recent. (Accreditation_YYYY_MM.zip means alphanumeric sort)
        link = sorted(a_iter)[-1]

        # Ensure link is absolute not relative
        link = urljoin(self.USDE_LINK, link)

        # Download the linked file to the FS and extract the CSV
        tempfile = '/tmp/accreditation.zip'
        call(['wget', '-O', tempfile, link])
        fd = open(filename, 'w')
        call(['7z', 'e', "-i!*.csv", '-so', tempfile], stdout=fd)
        fd.close()
        call(['rm', tempfile])
