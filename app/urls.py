from django.contrib import admin
from django.urls import path
from . import views
from .views import pdf_listview
from . import view_test
from . import admin


urlpatterns = [
    path('', views.index,name='index'),
    path('login', views.login_view,name='login'),
    path('signup', views.signup_view,name='signup'),
    
    path('logout', views.login_view,name='logout'),
    path('uploadcbc', views.upload_cbcfile,name='uploadcbc'),
    path('function', views.function,name='function'),
 
    # path('download/<int:pk>/', views.download, name='download'),
    path('base/', views.datatablecbc, name='base'),
    path('deleteall', views.delete_all,name='deleteall'),
    
    #--------pdf-------------------------
    path('pdf_list/',pdf_listview.as_view(),name="images-list-view"),
    path('pdf_id:/<pk>/',views.pdf,name="image-pdf-view"),
    #-------datavisualization-----------
    # path('analysis/', views.mcv_list, name='analysis'),
    path('datavisual_id:/<pk>/',views.data_visual,name='datavisual'),
    

    #---------------------------------------------
    path('edit/', views.edit_list, name='edit'),
    path('edit_id:/<pk>/', views.edit_file, name='editinfo'),
    #---------test2---------------------
    path('test2/', views.test3, name='test2'),
    path('delete/<int:id>', views.delete, name='delete'),
    #-------datavisualization-------
    
    
    
    
    
    
]
    
    
    
    
    
