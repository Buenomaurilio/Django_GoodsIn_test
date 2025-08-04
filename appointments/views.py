from django.shortcuts import render, redirect, get_object_or_404
from django.utils.dateparse import parse_date, parse_time
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from .forms import AppointmentForm, CheckerForm
from .models import Appointment, Checker
from datetime import timedelta, datetime
from django.db.models import Sum, Count
from django.utils.timezone import now
from django.http import HttpResponse
from django.contrib import messages
from .models import Appointment
from django import forms
import json
import csv
import io


class CSVImportForm(forms.Form):
    file = forms.FileField()


@login_required
def appointment_list(request):
    today = now().date()
    data_filter = request.GET.get('date', today)
    po_filter = request.GET.get('po', '').strip()
    description_filter = request.GET.get('description', '').strip()

    if isinstance(data_filter, str):
        data_filter = parse_date(data_filter)

    appointments = Appointment.objects.filter(scheduled_date=data_filter)

    if po_filter:
        appointments = appointments.filter(po__icontains=po_filter)
    
    if description_filter:
        appointments = appointments.filter(description__icontains=description_filter)

    # if description_filter:
    #     appointments = appointments.filter(descricao__icontains=description_filter)

    appointments = appointments.order_by('scheduled_time')

    morning_shift = appointments.filter(scheduled_time__gte=parse_time("05:00"), scheduled_time__lt=parse_time("13:30"))
    back_shift = appointments.filter(scheduled_time__gte=parse_time("13:00"), scheduled_time__lt=parse_time("21:30"))

    context = {
        'appointments': appointments,
        'data_filter': data_filter,
        'total_appointments': appointments.count(),
        'morning_count': morning_shift.count(),
        'back_count': back_shift.count(),
        'morning_pallets': morning_shift.aggregate(Sum('qtd_pallet'))['qtd_pallet__sum'] or 0,
        'back_pallets': back_shift.aggregate(Sum('qtd_pallet'))['qtd_pallet__sum'] or 0,
    }
    return render(request, 'appointments/appointment_list.html', context)

# @login_required
# def appointment_list(request):
#     today = now().date()
#     data_filter = request.GET.get('date', today)
#     po_filter = request.GET.get('po', '').strip()

#     if isinstance(data_filter, str):
#         data_filter = parse_date(data_filter)

#     appointments = Appointment.objects.filter(scheduled_date=data_filter)

#     if po_filter:
#         appointments = appointments.filter(po__icontains=po_filter)

#     appointments = appointments.order_by('scheduled_time')

#     morning_shift = appointments.filter(scheduled_time__gte=parse_time("05:00"), scheduled_time__lt=parse_time("13:30"))
#     back_shift = appointments.filter(scheduled_time__gte=parse_time("13:00"), scheduled_time__lt=parse_time("21:30"))

#     context = {
#         'appointments': appointments,
#         'data_filter': data_filter,
#         'total_appointments': appointments.count(),
#         'morning_count': morning_shift.count(),
#         'back_count': back_shift.count(),
#         'morning_pallets': morning_shift.aggregate(Sum('qtd_pallet'))['qtd_pallet__sum'] or 0,
#         'back_pallets': back_shift.aggregate(Sum('qtd_pallet'))['qtd_pallet__sum'] or 0,
#     }
#     return render(request, 'appointments/appointment_list.html', context)

@login_required
def dashboard_view(request):
    date_str = request.GET.get('date')
    selected_date = parse_date(date_str) if date_str else now().date()    

    year = selected_date.year
    month = selected_date.month
    weekday = selected_date.weekday()
    start_of_week = selected_date - timedelta(days=weekday)
    end_of_week = start_of_week + timedelta(days=6)

    pallets_today = Appointment.objects.filter(scheduled_date=selected_date).aggregate(total=Sum('qtd_pallet'))['total'] or 0
    pallets_week = Appointment.objects.filter(scheduled_date__range=(start_of_week, end_of_week)).aggregate(total=Sum('qtd_pallet'))['total'] or 0
    pallets_month = Appointment.objects.filter(scheduled_date__year=year, scheduled_date__month=month).aggregate(total=Sum('qtd_pallet'))['total'] or 0
    pallets_total = Appointment.objects.aggregate(total=Sum('qtd_pallet'))['total'] or 0

    loads_today = Appointment.objects.filter(scheduled_date=selected_date).count()
    loads_week = Appointment.objects.filter(scheduled_date__range=(start_of_week, end_of_week)).count()
    loads_month = Appointment.objects.filter(scheduled_date__year=year, scheduled_date__month=month).count()
    loads_total = Appointment.objects.count()

    checker_day = list(
        Appointment.objects
        .filter(scheduled_date=selected_date, checker__isnull=False)
        .values('checker__name')
        .annotate(total=Sum('qtd_pallet'))
        .order_by('-total')
    )

    checker_week = list(
        Appointment.objects
        .filter(scheduled_date__range=(start_of_week, end_of_week), checker__isnull=False)
        .values('checker__name')
        .annotate(total=Sum('qtd_pallet'))
        .order_by('-total')
    )

    checker_month = list(
        Appointment.objects
        .filter(scheduled_date__year=year, scheduled_date__month=month, checker__isnull=False)
        .values('checker__name')
        .annotate(total=Sum('qtd_pallet'))
        .order_by('-total')
    )
    
    # checker_day = list(Appointment.objects.filter(scheduled_date=selected_date)
    #     .values('checker__name')
    #     .annotate(total=Sum('qtd_pallet'))
    #     .order_by('-total'))

    # checker_week = list(Appointment.objects.filter(scheduled_date__range=(start_of_week, end_of_week))
    #     .values('checker__name')
    #     .annotate(total=Sum('qtd_pallet'))
    #     .order_by('-total'))

    # checker_month = list(Appointment.objects.filter(scheduled_date__year=year, scheduled_date__month=month)
    #     .values('checker__name')
    #     .annotate(total=Sum('qtd_pallet'))
    #     .order_by('-total'))

    loads_status_day = list(Appointment.objects.filter(scheduled_date=selected_date)
        .values('status_load')
        .annotate(count=Count('id')))

    loads_status_week = list(Appointment.objects.filter(scheduled_date__range=(start_of_week, end_of_week))
        .values('status_load')
        .annotate(count=Count('id')))

    loads_status_month = list(Appointment.objects.filter(scheduled_date__year=year, scheduled_date__month=month)
        .values('status_load')
        .annotate(count=Count('id')))

    context = {
        'selected_date': selected_date,
        'pallets_today': pallets_today,
        'pallets_week': pallets_week,
        'pallets_month': pallets_month,
        'pallets_total': pallets_total,
        'loads_today': loads_today,
        'loads_week': loads_week,
        'loads_month': loads_month,
        'loads_total': loads_total,
        'checker_day': json.dumps(checker_day),
        'checker_week': json.dumps(checker_week),
        'checker_month': json.dumps(checker_month),
        'loads_status_day': json.dumps(loads_status_day),
        'loads_status_week': json.dumps(loads_status_week),
        'loads_status_month': json.dumps(loads_status_month),
    }

    return render(request, 'appointments/dashboard.html', context)

@login_required
def edit_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    data_filter = request.GET.get('date')
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect(f"/appointments/?date={data_filter}" if data_filter else 'appointment_list')
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'appointments/edit_appointment.html', {'form': form, 'appointment': appointment})

@login_required
def add_appointment(request):
    data_filter = request.GET.get('date')
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"/appointments/?date={data_filter}" if data_filter else 'appointment_list')
    else:
        form = AppointmentForm()
    return render(request, 'appointments/add_appointment.html', {'form': form})

@login_required
def add_checker(request):
    data_filter = request.GET.get('date')
    if request.method == 'POST':
        form = CheckerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"/appointments/?date={data_filter}" if data_filter else 'appointment_list')
    else:
        form = CheckerForm()
    return render(request, 'appointments/add_checker.html', {'form': form})

@login_required
def export_appointments_csv(request):
    appointments = Appointment.objects.all()

    # Filtros da URL
    date_filter = request.GET.get('date')
    hall = request.GET.get('hall')
    checker = request.GET.get('checker')
    status = request.GET.get('status')
    tipped = request.GET.get('tipped')
    checked = request.GET.get('checked')

    if date_filter:
        appointments = appointments.filter(scheduled_date=date_filter)
    if hall:
        appointments = appointments.filter(hall=hall)
    if checker:
        appointments = appointments.filter(checker__id=checker)
    if status:
        appointments = appointments.filter(status_load=status)
    if tipped in ['true', 'false']:
        appointments = appointments.filter(tipped=(tipped == 'true'))
    if checked in ['true', 'false']:
        appointments = appointments.filter(checked=(checked == 'true'))

    # Resposta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="appointments_filtered.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Description', 'Date', 'Time', 'P.O', 'Qty',
        'Hall', 'Tipped', 'Checked', 'Checker', 'Status',
        'Arrival Time', 'Check Out Time', 'Bay 1'
    ])

    for appt in appointments:
        writer.writerow([
            appt.id,
            appt.description,
            appt.scheduled_date,
            appt.scheduled_time,
            appt.po,
            appt.qtd_pallet,
            appt.hall,
            'Yes' if appt.tipped else 'No',
            'Yes' if appt.checked else 'No',
            appt.checker.name if appt.checker else '',
            appt.status_load,
            appt.arrival_time,
            appt.check_out_time,
            appt.bay1,
        ])

    return response

# @login_required
# def export_appointments_csv(request):
#     data_filter = request.GET.get('date')
#     appointments = Appointment.objects.all()
#     if data_filter:
#         appointments = appointments.filter(scheduled_date=data_filter)

#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="appointments.csv"'

#     writer = csv.writer(response)
#     writer.writerow(['ID', 'Description', 'Date', 'Time', 'P.O', 'Qty', 'Hall', 'Tipped', 'Checked', 'Checker'])

#     for appt in appointments:
#         writer.writerow([
#             appt.id,
#             appt.description,
#             appt.scheduled_date,
#             appt.scheduled_time,
#             appt.po,
#             appt.qtd_pallet,
#             appt.hall,
#             appt.tipped,
#             appt.checked,
#             appt.checker.name if appt.checker else ''
#         ])

#     return response

@login_required
def import_appointments_csv(request):
    data_filter = request.GET.get('date')
    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                decoded_file = io.TextIOWrapper(file, encoding='utf-8')
                reader = csv.DictReader(decoded_file)

                for row in reader:
                    try:
                        Appointment.objects.create(
                            description=row['Description'],
                            scheduled_date=parse_date(row['Date']),
                            scheduled_time=parse_time(row['Time']),
                            po=row['P.O'],
                            qtd_pallet=int(row['Qty']),
                            hall=row.get('Hall', '')
                        )
                    except Exception as e:
                        messages.warning(request, f"Erro ao importar linha {row}: {e}")

                messages.success(request, "Appointments imported successfully.")
                return redirect(f"/appointments/?date={data_filter}" if data_filter else 'appointment_list')
            except Exception as e:
                messages.error(request, f"Erro ao processar arquivo: {e}")
                return redirect(f"/appointments/?date={data_filter}" if data_filter else 'appointment_list')
    else:
        form = CSVImportForm()

    return render(request, 'appointments/import_csv.html', {'form': form})

@login_required
def delete_appointment(request, pk):
    data_filter = request.GET.get('date')
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.delete()
    messages.success(request, "Appointment deleted successfully.")
    return redirect(f"/appointments/?date={data_filter}" if data_filter else 'appointment_list')

@login_required
def appointment_table_partial(request):
    data_filter = request.GET.get('date')
    if data_filter:
        appointments = Appointment.objects.filter(scheduled_date=data_filter).order_by('scheduled_time')
    else:
        appointments = Appointment.objects.all().order_by('-scheduled_date', '-scheduled_time')

    return JsonResponse({
        'table_html': render_to_string('appointments/appointment_table_partial.html', {
            'appointments': appointments
        })
    })


def export_dashboard_csv(request):
    selected_date = request.GET.get('date')
    appointments = Appointment.objects.all()

    if selected_date:
        appointments = appointments.filter(scheduled_date=selected_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="dashboard_{selected_date or "all"}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Description', 'Date', 'Time', 'P.O', 'Qty', 'Hall', 'Tipped', 'Checked', 'Checker', 'Status'])

    for a in appointments:
        writer.writerow([
            a.id, a.description, a.scheduled_date, a.scheduled_time, a.po, a.qtd_pallet,
            a.hall, 'Yes' if a.tipped else 'No', 'Yes' if a.checked else 'No',
            a.checker, a.status_load
        ])

    return response
