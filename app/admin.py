from django.contrib import admin
from django.contrib import admin
from django.shortcuts import render

from app.models import CBCReport
import pandas as pd
import numpy as np
from django.core.files import File
from .forms import CBCReport

# Register your models here.


class CBCReportAdmin(admin.ModelAdmin):

    def save_model(self, request, obj: CBCReport, form, change):

        super().save_model(request, obj, form, change)
        rawfile = obj.cbcrawfile.open('r')
        df = pd.read_csv(rawfile)
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

        outfile = open(f"cbgraading_{obj.id}.csv.temp", 'w')
        df.to_csv(outfile)
        outfile.close()
        outfile = open(f"cbgraading_{obj.id}.csv.temp", 'r')
        obj.cbcgrading.save(f'cbgraading_{obj.id}.csv', File(outfile))
        outfile.close()


# generate chart

# generate report

# 1. generate report pdf
# 2. create pdf file
# 3. save to model


admin.site.register(CBCReport, CBCReportAdmin)
