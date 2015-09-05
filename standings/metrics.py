


def register(name, annotator):
    pass

def get_annotator(name):
    pass

class MetricAnnotator:
    name = NotImplemented
    dependencies = []

    def annotate(self, standings):
        pass

class DatabaseMetricAnnotator(MetricAnnotator):

    def annotate(self, queryset):
        pass

class WhoBeatWhomMetricAnnotator(MetricAnnotator):
    pass

