from debate import models as m
import csv

def main():
    reader = csv.reader(open('people.csv'))
    for barcode, ins_name, team, first, last in reader:
        print ins_name
        if team not in ('Judge', 'Observer'):
            speaker = m.Speaker.objects.get(name='%s %s' % (first, last))
            speaker.barcode_id = barcode
            speaker.save()

if __name__ =='__main__':
    main()


