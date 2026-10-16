from unittest.mock import patch

from django.forms import modelformset_factory
from django.test import SimpleTestCase, TestCase

from participants.models import Institution, Region

from ..forms import ImportInstitutionsRawForm, InstitutionDetailsForm


class TestImportInstitutionsRawForm(SimpleTestCase):

    def test_optional_region_column(self):
        form = ImportInstitutionsRawForm({'institutions_raw': (
            'First University,FIRST\n'
            'Second University,SECOND,\n'
            'Third University,THIRD, Oceania \n'
        )})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['institutions_raw'], [
            {'name': 'First University', 'code': 'FIRST', 'region_name': ''},
            {'name': 'Second University', 'code': 'SECOND', 'region_name': ''},
            {'name': 'Third University', 'code': 'THIRD', 'region_name': 'Oceania'},
        ])

    def test_extra_columns_rejected(self):
        form = ImportInstitutionsRawForm({'institutions_raw': 'University,UNI,Region,Extra'})
        self.assertFalse(form.is_valid())
        self.assertIn('too many columns', str(form.errors))

    def test_import_limit_accounts_for_region_field(self):
        with patch('importer.forms.MAX_FORM_DATA_FIELDS', 8):
            form = ImportInstitutionsRawForm({'institutions_raw': 'A,A\nB,B\nC,C'})
            self.assertFalse(form.is_valid())
            self.assertIn('up to 2 institutions', str(form.errors))


class TestInstitutionDetailsForm(TestCase):

    def test_formset_reuses_and_creates_regions_on_save(self):
        region = Region.objects.create(name='Existing')
        formset_class = modelformset_factory(Institution, form=InstitutionDetailsForm, extra=0)
        data = {
            'form-TOTAL_FORMS': '4', 'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
        }
        for i, name in enumerate(['Existing', 'New', 'New', '']):
            data.update({
                f'form-{i}-name': f'University {i}',
                f'form-{i}-code': f'U{i}',
                f'form-{i}-region_name': name,
            })
        formset = formset_class(data, queryset=Institution.objects.none())
        self.assertTrue(formset.is_valid(), formset.errors)
        self.assertEqual(Region.objects.count(), 1)
        institutions = formset.save()
        self.assertEqual(institutions[0].region, region)
        self.assertEqual(institutions[1].region.name, 'New')
        self.assertEqual(institutions[1].region, institutions[2].region)
        self.assertIsNone(institutions[3].region)
        self.assertEqual(Region.objects.count(), 2)
        self.assertEqual(Institution.objects.count(), 4)

    def test_region_name_length_validated_before_creation(self):
        form = InstitutionDetailsForm({'name': 'University', 'code': 'UNI', 'region_name': 'x' * 101})
        self.assertFalse(form.is_valid())
        self.assertIn('region_name', form.errors)
        self.assertFalse(Region.objects.exists())
