from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import connection
from django.db.models import Q
from django.core.files.storage import default_storage

import datetime
import json
import pdfplumber as pp
import re
import requests

from .models import Materijal, Racuni, Krm

app_name = 'racuni'

def convertPDF(request):
    file = request.FILES['inputfile']

    if default_storage.exists('racunPDF'):
        default_storage.delete('racunPDF')
    file_name = default_storage.save('racunPDF', file)

    zelengrad_re = re.compile(r'(\d+)/ 40[\s*\d/]*, (.*?)\s\s [\s]+([\d.]+\,\d{1}) (KOM|MET|KG|M\*2|PAK)[\s]+([\d.]+\,\d+)\s\s')
    tablica = False
    prvi_red = False

    data = []

    with pp.open(file_name) as pdf:
        pages = pdf.pages
        
        for i,pg in enumerate(pages):
            text = pages[i].extract_text()
        
            for row in text.split("\n"):
                if row.startswith("Šifra"):
                    tablica = True
                    continue
                    
                if row.startswith("/6 POVRAT ROBE:"):
                    tablica = False
                    break
                    
                if row.startswith("Copyright Aura Soft 2001."):
                    tablica = False
                    continue
                
                if tablica and (row.startswith("*/ 40") != 1):
                    m = zelengrad_re.search(row)
                    data.append(m.group(1) + "@" + m.group(2) + "@" + m.group(3) + "@" + m.group(4) + "@" + m.group(5) + "\n")
                    continue
                
                if row.startswith("ZELENGRAD d.o.o. PAZIN") and prvi_red == False:
                    data.append("ZELENGRAD d.o.o.@" + row.split()[-1] + "@") 
                elif (row.find('Datum:') != -1) and prvi_red == False:
                    data.append(row.split()[-2] + "\n") 
                    prvi_red = True
        

    return JsonResponse(data, safe=False)


def ulaz(request):
    datum = datetime.datetime.strptime(request.POST['datum_racuna'], '%d/%m/%Y').strftime('%Y-%m-%d')
    broj_racuna = request.POST['br_racuna']
    Racuni(firma=request.POST['dobavljac'], broj_racuna=broj_racuna, datum=datum).save()
    #id_racun = Racuni.objects.all().order_by("-id").only("id")[0]
    id_racun = Racuni.objects.values('id').order_by('-id').first()
    str_id = str(id_racun['id'])
    x = int(request.POST['x'])

    for i in range(x):
        sifra = request.POST['sif'+str(i)]
        naziv = request.POST['naz'+str(i)]
        kolicina = request.POST['kol'+str(i)]
        mj = request.POST['mj'+str(i)]
        cijena = request.POST['cij'+str(i)]
        cursor = connection.cursor()
        cursor.execute("call procedura_ulaz('"+sifra+"', '"+naziv+"', '"+cijena+"', '"+str_id+"', '"+kolicina+"', '"+mj+"')")

    return redirect(ulazniRacun)

def ulazniRacun(request):
    if 'term' in request.GET:
        qs = Materijal.objects.filter(sifra__istartswith=request.GET.get('term'))
        sifre = list()
        for materijal in qs:
            sifre.append(materijal.sifra)

        return JsonResponse(sifre, safe=False)
    return render(request, 'racuni/ulazniRacun.html')

def racuni(request):
    all_racuni = Racuni.objects.all().order_by('-datum')
    context = {'all_racuni': all_racuni}
    return render(request, 'racuni/racuni.html', context)    

def racun(request, racun_id):
    racun = Racuni.objects.filter(id=racun_id)
    all_materijal = Krm.objects.filter(racunID=racun_id).select_related('materijalID')
    context = {'all_materijal': all_materijal, 'racun': racun}
    return render(request, 'racuni/racun.html', context)

def info(request):
    return render(request, 'racuni/info.html')





