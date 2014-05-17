import csv
import debate.models as m

reader = csv.reader(open("institutions.csv"))
for name, code, abbreviation in reader:
    i = m.Institution.objects.get(name=name, code=code)
    i.abbreviation = abbreviation
    i.save()