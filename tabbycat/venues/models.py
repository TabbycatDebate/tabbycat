from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class Venue(models.Model):
    name = models.CharField(max_length=40,
        verbose_name=_("name"))
    priority = models.IntegerField(
        verbose_name=_("priority"),
        help_text=_("Rooms with a higher priority number will be preferred when allocating rooms to debates"))
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE,
        null=True, db_index=True,
        verbose_name=_("tournament"))
    url = models.URLField(verbose_name=_("URL"), blank=True,
        help_text=_("A URL that contains extra information about this room, e.g. a map or a meeting link (for online tournaments)"))

    round_availabilities = GenericRelation('availability.RoundAvailability')

    class Meta:
        ordering = ['name']
        index_together = ['name']
        verbose_name = _("room")
        verbose_name_plural = _("rooms")

    @property
    def display_name(self):
        categories = self.venuecategory_set.all()
        prefixes = []
        suffixes = []
        for category in categories:
            if category.display_in_venue_name == VenueCategory.DISPLAY_PREFIX:
                prefixes.append(category.name)
            elif category.display_in_venue_name == VenueCategory.DISPLAY_SUFFIX:
                suffixes.append(category.name)
        display_name = ""
        if prefixes:
            prefixes.sort()
            display_name += ", ".join(prefixes) + " "
        display_name += self.name
        if suffixes:
            suffixes.sort()
            display_name += " " + ", ".join(suffixes)
        return display_name

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return "<Venue: %s (%s) [%s]>" % (str(self), self.priority, self.id)


class VenueCategory(models.Model):
    """Represents a category of venues, typically used for (physical real-world)
    navigation aid and/or venue constraints."""

    DISPLAY_NONE = '-'
    DISPLAY_PREFIX = 'P'
    DISPLAY_SUFFIX = 'S'
    DISPLAY_IN_VENUE_NAME_CHOICES = ((DISPLAY_NONE, _("Don't display in room name")),
                                     (DISPLAY_PREFIX, _("Display as prefix")),
                                     (DISPLAY_SUFFIX, _("Display as suffix")))

    name = models.CharField(max_length=80,
        verbose_name=_("name"),
        help_text=_("Name of category, e.g., \"Purple\", \"Step-free access\", "
            "\"Close to tab room\". This name is shown when the category is "
            "prefixed or suffixed to a room name in the draw, e.g., \"Purple – G05\"."))
    description = models.CharField(max_length=200, blank=True,
        verbose_name=_("description"),
        help_text=_("Description, as the predicate of a sentence, e.g. \"has step-free access\", "
            "\"is close to the briefing hall\". This description follows \"This room\" when "
            "shown in tooltips, e.g., \"This room is close to the briefing hall.\"."))

    venues = models.ManyToManyField(Venue, verbose_name=_("rooms"), blank=True)
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE,
        null=True, verbose_name=_("tournament"))

    display_in_venue_name = models.CharField(max_length=1, choices=DISPLAY_IN_VENUE_NAME_CHOICES,
        default=DISPLAY_NONE,
        verbose_name=_("display in room name"),
        help_text=_("Prefix: \"Purple – G05\", Suffix: \"G05 – Purple\""))
    display_in_public_tooltip = models.BooleanField(default=False,
        verbose_name=_("display in public tooltip"),
        help_text=_("Displays the description in the tooltip for the room on public pages. "
            "The description, if not blank, will always show on admin pages."))

    class Meta:
        verbose_name = _("room category")
        verbose_name_plural = _("room categories")

    def __repr__(self):
        return "<VenueCategory: %s [%d]>" % (self.name, self.id)

    def __str__(self):
        return self.name


class VenueConstraintManager(models.Manager):

    def filter_for_debates(self, debates):
        """Convenience function. Filters for all constraints relevant to the
        given iterable of debates."""
        return VenueConstraint.objects.filter(
            models.Q(team__debateteam__debate__in=debates) |
            models.Q(institution__team__debateteam__debate__in=debates) |
            models.Q(adjudicator__debateadjudicator__debate__in=debates),
        ).distinct()


class VenueConstraint(models.Model):

    SUBJECT_CONTENT_TYPE_CHOICES = models.Q(app_label='participants', model='team') | \
                                   models.Q(app_label='participants', model='adjudicator') | \
                                   models.Q(app_label='participants', model='institution')

    category = models.ForeignKey(VenueCategory, models.CASCADE,
        verbose_name=_("category"))
    priority = models.IntegerField(verbose_name=_("priority"))

    subject_content_type = models.ForeignKey(ContentType, models.CASCADE,
        verbose_name=_("subject content type"),
        limit_choices_to=SUBJECT_CONTENT_TYPE_CHOICES)
    subject_id = models.PositiveIntegerField(
        verbose_name=_("subject ID"))
    subject = GenericForeignKey('subject_content_type', 'subject_id')

    objects = VenueConstraintManager()

    class Meta:
        verbose_name = _("room constraint")
        verbose_name_plural = _("room constraints")

    def __str__(self):
        return "%s for %s [%s]" % (self.subject, self.category, self.priority)
