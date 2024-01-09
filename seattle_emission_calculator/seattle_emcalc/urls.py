from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("calcul_des_emissions", views.calcul_des_emissions, name="calcul_des_emissions"),
    path("landing_page_calcul", views.landing_page_calcul, name="landing_page_calcul"),
    path("upload_file", views.upload_file, name='upload_file'),
    path("upload_file_success", views.upload_file_success, name='upload_file_success'),
    path("upload_modele", views.upload_model, name='upload_model'),
    path("upload_modele_success", views.upload_model_success, name='upload_model_success'),
    path("calcul_fichier_ext", views.calcul_fichier_ext, name="calcul_fichier_ext"),
    path("ajout_de_batiment", views.ajout_de_batiment, name="ajout_de_batiment"),
    path("bdd_seattle", views.bdd_seattle, name="bdd_seattle"),
]