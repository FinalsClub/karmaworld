import csv
from itertools import izip

from django.core.management.base import BaseCommand
from karmaworld.apps.courses.models import School


class Command(BaseCommand):
    args = '<filename>'
    help = ("""Import USDE csv file. add schools to the UsdeSchool model.
        Assumes the following header:
        Institution_ID,Institution_Name,Institution_Address,Institution_City,Institution_State,Institution_Zip,Institution_Phone,Institution_OPEID,Institution_IPEDS_UnitID,Institution_Web_Address,Campus_ID,Campus_Name,Campus_Address,Campus_City,Campus_State,Campus_Zip,Campus_IPEDS_UnitID,Accreditation_Type,Agency_Name,Agency_Status,Program_Name,Accreditation_Status,Accreditation_Date_Type,Periods,Last Action"""
    )

    def parse_school_csv(self, filename):
        """parse a csv file, and return a list of dictionaries
        """
        headers = False
        schools = []

        with open(filename) as f:

            reader = csv.reader(f)
            headers = reader.next()
            for row in reader:
                schools.append(row)

        headers = [s.lower() for s in headers]

        return [ dict(izip(headers,school)) for school in schools ]

    def handle(self, *args, **kwargs):

        if len(args) < 1:
            self.stdout.write('Provide a filename\n')
            return

        filename = args[0]

        school_dicts = self.parse_school_csv(filename)

        self.stdout.write('Importing from list of %d schools\n' % len(school_dicts))

        count = 0

        for d in school_dicts:

            if 'institution_id' not in d or not d['institution_id']:
                print d
                raise Exception('Error: School does not have an institution_id!')

            try:
                school = School.objects.get(usde_id=d['institution_id'])

            except School.DoesNotExist:
                school = School()
                #print d['institution_id']
                #print d['institution_name']
                count += 1


            school.name = d['institution_name']
            school.location = d['institution_city'] + ', ' + d['institution_state']
            school.url = d['institution_web_address']
            school.usde_id = d['institution_id']
            school.save()

        self.stdout.write('Imported %d NEW unique schools\n' % count)








