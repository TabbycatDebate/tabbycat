from django.db import models


class UniqueConstraint(models.UniqueConstraint):
    def __init__(self, *expressions, fields=(), name=None, **kwargs):
        if name is None:
            name = '%(app_label).7s_%(class)s_' + "__".join(fields) + '_uniq'
        return super().__init__(*expressions, fields=fields, name=name, **kwargs)
