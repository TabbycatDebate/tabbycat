from django.contrib import admin

from utils.admin import ModelAdmin

from .models import BooleanAnswer, FloatAnswer, IntegerAnswer, ManyAnswer, StringAnswer


@admin.register(BooleanAnswer)
@admin.register(FloatAnswer)
@admin.register(IntegerAnswer)
@admin.register(ManyAnswer)
@admin.register(StringAnswer)
class AnswerAdmin(ModelAdmin):
    list_display = ('question', 'answer', 'content_object')
