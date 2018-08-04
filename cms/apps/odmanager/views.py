from django.shortcuts import render
from apps.accounts.models import User
from apps.club.models import Event
from datetime import datetime
# Create your views here.

def testView(request):

    data = {
        "students": [],
        "event": Event.objects.get(id=4),
        "od_date": datetime.now()
    }

    for student in User.objects.all():

        data['students'].append({
            'user': student,
            'subjects': [
                {
                    "name": "Applied Physics",
                    "timing": "[12:00 - 02:00]"
                }
            ],
            'role': 'particpant'
        })
    
    for student in User.objects.all():

        data['students'].append({
            'user': student,
            'subjects': [
                {
                    "name": "Applied Physics",
                    "timing": "[12:00 - 02:00]"
                }
            ],
            'role': 'particpant'
        })
    
    for student in User.objects.all():

        data['students'].append({
            'user': student,
            'subjects': [
                {
                    "name": "Applied Physics",
                    "timing": "[12:00 - 02:00]"
                }
            ],
            'role': 'particpant'
        })
    return render(request, "odmanager/template.html", {"data": data})