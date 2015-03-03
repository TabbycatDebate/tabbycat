from django.core.management.base import LabelCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify
import os
import csv
import debate.models as m
from optparse import make_option

class Command(LabelCommand):
    args = 'dirname [--auto-rounds n] [--share-data]'
    help = 'Delete all data for a tournament and import from specified directory.'

    option_list = LabelCommand.option_list + (
        make_option('-r', '--auto-rounds', type=int, metavar='N', default=None,
            help='Create N preliminary rounds automatically. Use either this or a rounds.csv file, but not both.'),
        make_option('-S', '--share-data', action='store_true', default=False,
            help='If specified, all institutions and adjudicators will not be tournament-specific.'),
    )

