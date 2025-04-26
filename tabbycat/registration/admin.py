from django.contrib import admin

from utils.admin import ModelAdmin

from .models import Answer


@admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    list_display = ('question', 'answer', 'content_object')
