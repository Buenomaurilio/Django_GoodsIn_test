from django import forms
from .models import Appointment, Checker
from warehouses.models import Warehouse

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'description',
            'scheduled_date',
            'scheduled_time',
            'po',
            'qtd_pallet',
            'hall',
            'tipped',
            'checked',
            'checker',
            'arrival_time',
            'check_out_time',
            'bay1',
            'status_load',
            # 'warehouse' será incluído dinamicamente abaixo se for superadmin
        ]
        widgets = {
            'scheduled_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'arrival_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'check_out_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'scheduled_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AppointmentForm, self).__init__(*args, **kwargs)

        if user and user.is_superadmin:
            self.fields['warehouse'] = forms.ModelChoiceField(queryset=Warehouse.objects.all(), required=True)

class CheckerForm(forms.ModelForm):
    class Meta:
        model = Checker
        fields = ['name']


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()


# from .models import Checker
# from django import forms
# from .models import Appointment


# class AppointmentForm(forms.ModelForm):
#     class Meta:
#         model = Appointment
#         # Lista de campos que vão aparecer no formulário:
#         fields = [
#             'description',
#             'scheduled_date',
#             'scheduled_time',
#             'po',
#             'qtd_pallet',
#             'hall',
#             'tipped',
#             'checked',
#             'checker',
#             'arrival_time',
#             'check_out_time',
#             'bay1',
#             'status_load',
#         ]
#         widgets = {
#             'scheduled_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
#             'arrival_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
#             'check_out_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
#             'scheduled_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
#         }

# class CheckerForm(forms.ModelForm):
#     class Meta:
#         model = Checker
#         fields = ['name']


# class CSVImportForm(forms.Form):
#     csv_file = forms.FileField()
