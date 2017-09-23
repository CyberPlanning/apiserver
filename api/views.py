from datetime import datetime
import random

from django.shortcuts import render

from django.http import HttpResponse


def index(request):
    end = datetime(int(random.uniform(3017, 5017)), int(random.uniform(1, 13)), int(random.uniform(1, 29)))

    return HttpResponse("Site disponible avant " + end.strftime("%d/%m/%Y"))

