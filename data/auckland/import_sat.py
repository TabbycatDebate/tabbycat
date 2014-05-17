import csv
import debate.models as m

def main():
    t = m.Tournament.objects.get(slug='australs')
    
    r = m.Round.objects.get(tournament=t, seq=4)

    r.set_available_venues([])

    reader = csv.reader(open('saturday.csv'))

    for bname, group, room in reader:
        venue,_ = m.Venue.objects.get_or_create(
            name = '%s %s' % (bname.strip(), room.strip()),
            tournament = t,
            defaults = {
                'group': 0,
                'priority': 200,
            },
        )
        venue.group = group
        venue.save()
        r.activate_venue(venue)

    debates = r.get_draw()
    venues = list(r.active_venues.all())[:len(debates)]
    import random
    random.shuffle(venues)

    for debate, venue in zip(debates, venues):
        debate.venue = venue
        debate.save()

if __name__ == '__main__':
    main()

