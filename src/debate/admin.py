from django.contrib import admin

import debate.models as models

admin.site.register(models.Institution)
admin.site.register(models.Team)
admin.site.register(models.Speaker)

admin.site.register(models.Adjudicator)
admin.site.register(models.Venue)

admin.site.register(models.Round)
admin.site.register(models.Debate)