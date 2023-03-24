from django.shortcuts import render
from collections import Counter
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, request
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.files import File
from django.core.files.base import ContentFile
from django.conf import settings
from django.views.generic import View, ListView
# ------part2-------
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context


# ---- form-----
from .forms import CreateUserForm
from .forms import uploadcbc
from .models import CBCReport

# ------tools-------
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
import os
from xhtml2pdf import pisa

#------datavisualization------
import mpld3
import matplotlib.pyplot as plt
# -----index-------


def index(request):

    return render(request, 'index.html')
# -----home------


def home(request):
    return render(request, 'home.html')
# -----signup-----


def signup_view(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
        return render(request, 'home.html')

    else:
        form = CreateUserForm()
    return render(request, 'signup.html', {
        'form': form,
    })
# ------login--------


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('base')
        else:
            return render(request, 'home.html')

    else:
        form = AuthenticationForm()
        # return render(request,"login.thml")
    return render(request, 'login.html', {
        'form': form,
    })
# -----base----------


def datatablecbc(request):
    data_cbc = CBCReport.objects.all()
    return render(request, 'base.html', {'data_cbc': data_cbc})


# -----logout----------

def logout_view(request):
    logout(request)
    return redirect('home')
# -----import cbc file----------


def upload_cbcfile(request, **kwargs):

    if request.method == 'POST':

        # -----grading--------
        form = uploadcbc(request.POST, request.FILES)        
        form.instance.user = request.user
        if form.is_valid():
            obj = form.save()
            rawfile = obj.cbcrawfile.open('r')
            df = pd.read_csv(rawfile)
            print(df)
            results = ['normal', 'normal', 'Hb E > 25%',
                       'Hb E < 25%', 'Hb EE', 'Hb E-beta thal', 'Hb H']
            results2 = ['0', '0', '1', '2', '3', '4', '5']

            condition = [
                (df['maf'] >= 13.7),
                (df['maf'] < 13.7) & (df['maf'] >= 11.3),
                (df['maf'] < 11.3) & (df['maf'] >= 9.1),
                (df['maf'] < 9.1) & (df['maf'] >= 7.8),
                (df['maf'] < 7.8) & (df['maf'] >= 6.7),
                (df['maf'] < 6.7) & (df['maf'] >= 5.9),
                (df['maf'] < 5.9) & (df['maf'] >= 5.0),
            ]
            df['type_risk'] = np.select(condition, results)
            df['thal_risk'] = ['negative' if x >
                               11.3 else 'positive' for x in df['maf']]
            df['severity'] = np.select(condition, results2)

            temp_file_path = f"cbgraading_{obj.id}.csv.temp"
            final_file_path = f"cbgraading_{obj.id}.csv"

            # Write DataFrame to temporary file
            with open(temp_file_path, 'w') as outfile:
                df.to_csv(outfile)

            # Save temporary file to Django model field
            with open(temp_file_path, 'r') as infile:
                obj.cbcgrading.save(final_file_path, File(infile))
            

            # ---chart plotly-----

            # gradefile = obj.cbcgrading.open('r')
            df_chart = pd.read_csv(temp_file_path)
            
            print(df_chart)
            
            z = df.loc[:, "severity"]
            z1 = np.array(z, dtype=int)

            value0 = np.count_nonzero(z1 == 0)
            value1 = np.count_nonzero(z1 == 1)
            value2 = np.count_nonzero(z1 == 2)
            value3 = np.count_nonzero(z1 == 3)
            value4 = np.count_nonzero(z1 == 4)
            value5 = np.count_nonzero(z1 == 5)

            all_value = [value0, value1, value2, value3, value4, value5]
            print(all_value)
            labels = ['normal', 'Hb E > 25%', 'Hb E < 25%',
                      'Hb EE', 'Hb E-beta thal', 'Hb H']
            fig = px.pie(values=all_value, names=labels)
            image_bytes = fig.to_image(format='png')

            imagefile = open(f'image_{obj.id}.png.temp', 'wb')
            imagefile.write(image_bytes)
            imagefile.close()

            imagefile = open(f"image_{obj.id}.png.temp", 'rb')
            obj.image.save(f'image_{obj.id}.png',
                           ContentFile(imagefile.read()))
            imagefile.close()
            
            # ------pdf-----------
            # all results
            # ps = CBCReport.objects.all()

            # template_path = 'pdf.html'
            # context = {'ps': ps}
            # # Render the HTML template with the context variables
            # template = get_template(template_path)
            # html = template.render(context)
            # # Create a PDF object with the HTML content
            # pdf_data = BytesIO()
            # pisa_status = pisa.CreatePDF(html, dest=pdf_data, encoding='utf-8')

            # pdf_file = ContentFile(pdf_data.getvalue())
            # obj.pdffile.save(f'pdf_{obj.id}.pdf', pdf_file)
            # -------------pdf----------

        return render(request, 'function.html',)
    else:
        form = uploadcbc()
    return render(request, 'uploadcbc.html', {'form': form})


# -------pdf------------
class pdf_listview(ListView):
    model = CBCReport
    template_name = 'base.html'

    
def pdf(request,*args, **kwargs):
    
    pk = kwargs.get('pk')
    ps = get_object_or_404(CBCReport,pk=pk)
    
    # pa = get_object_or_404(report_img,pk=pk)
    
    template_path = 'pdf.html'
    context = {'ps': ps}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    #display
    # response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response,)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

#---------data visualization------

# def mcv_list(request):
#     data_cbc=CBCReport.objects.all()
    
#     return render(request,'mcvlist.html',{'data_cbc': data_cbc})

def data_visual(request,pk):
    print(pk)
    car = CBCReport.objects.get(pk=pk)
    
    # mcvfile = CBCReport.objects.filter(pk=pk,cbcrawfile__isnull=False).first
    a= (car.cbcrawfile.path)
    print(a)
    if os.path.exists(a):
        with open(a,'r')as file:
            readfile = pd.read_csv(file)
            
        # if mcvfile is not None:
        #     print(mcvfile)
        
        fig, ax = plt.subplots()
        
        df = pd.DataFrame(readfile)
        x =  df.loc[:,"mcv"]
        y =  df.loc[:,"number"]
        num_x = np.array(x,dtype=int)
        num_y= np.array(y,dtype=int)
        ax.bar(num_x, num_y)

        ax.set_ylabel('values')
        ax.set_xlabel('MCV')
        ax.set_title('Mean corpuscular volume(MCV)')
        # ax.legend(title='Fruit color')
        
        graph_html = mpld3.fig_to_html(fig)     
        return render(request, 'data_visual.html',{'graph_html': graph_html})
    else:
        HttpResponse("no file")
    
#------------edit-----------------
def edit_list(request):
    data_cbc=CBCReport.objects.all()
    
    return render(request,'editlist.html',{'data_cbc': data_cbc})
def edit_file(request,pk):
    context={}    
    obj = get_object_or_404(CBCReport,pk=pk)
    form = uploadcbc(request.POST or None, instance = obj)
    if form.is_valid():
        form.save()
        return render(request,'done.html')
 
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "edit.html", context)
    



# -----logout----------


def function(request):

    return render(request, 'function.html')
# -----import cbc file----------


# -------delete function-----
def delete(request, id):
    deletefile = CBCReport.objects.get(id=id)
    deletefile.delete()
    return redirect("base")


# -------delete function-----
def delete_all(request):
    deletefile = CBCReport.objects.all()
    deletefile.delete()
    return redirect("base")

# ---------download------


# -------test2---------
def index(request):

    return render(request, 'index.html')


def test3(request):

    return render(request, 'test2.html')
