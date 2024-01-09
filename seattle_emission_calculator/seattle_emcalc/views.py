from django.shortcuts import render, redirect
from plotly.offline import plot
from .models import Buildings, NewBuilding, SaveForm, UploadFile, UploadModel, CalcMultiBat
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, BlobType
from pyJoules.energy_meter import measure_energy
from datetime import datetime

import pandas as pd
import os, time, pickle, io, sys


"""
|---------------------------------------------------------------- Page index.html pour la page d'accueil ----------------------------------------------------------------|
"""
def index(request):
    return render(request, 'index.html')
"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""




"""
|---------------------------------------------------------------- Page calcul_des_emissions.html pour le calcul des emissions ----------------------------------------------------------------|
"""
def calcul_des_emissions(request):
    
    if request.method == 'POST':

        start_time = time.time()
        @measure_energy
        def foo():
            # Récupérer les données du formulaire
            form_data = request.POST

            primarypropertytype = form_data['primarypropertytype']
            yearbuilt = form_data['yearbuilt']
            numberofbuildings = form_data['numberofbuildings']
            numberoffloors = form_data['numberoffloors']
            propertygfatotal = form_data['propertygfatotal']
            propertygfaparking = form_data['propertygfaparking']

            # Créer un dictionnaire des données
            data = {
                'primarypropertytype': primarypropertytype,
                'yearbuilt': yearbuilt,
                'numberofbuildings': numberofbuildings,
                'numberoffloors': numberoffloors,
                'propertygfatotal': propertygfatotal,
                'propertygfaparking': propertygfaparking,
                # Ajoutez d'autres champs du formulaire ici
            }

            # Créer une ligne DataFrame à partir du dictionnaire de données
            df = pd.DataFrame([data])
            df_stacked = df.stack().reset_index(level=0, drop=True).reset_index()
            global html_table 
            html_table = df_stacked.to_html(index=False, header=False)

            # Utilisation du dataframe

            # Chemin relatif vers le fichier picklé
            pickle_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pickle_models', 'best.model')

            # Charger le modèle picklé
            with open(pickle_file, 'rb') as f:
                model = pickle.load(f)

            prediction=model.predict(df)
            print("\n------------ Rapport console ---------")
            print(f"Matrice prédite => {prediction}")
            print(f"The total amount of greenhouse gas emissions (TotalGHGEmissions) => {prediction[0][0]}")
            print(f"The annual amount of energy consumed by the property from all sources of energy (SiteEnergyUse_kbtu) => {prediction[0][1]}")
            end_time = time.time()
            traitement = end_time - start_time
            print(f"------------ {traitement:.2f} seconds ------------\n")

            global TotalGHGEmissions 
            TotalGHGEmissions = prediction[0][0]
            global SiteEnergyUse_kbtu
            SiteEnergyUse_kbtu = prediction[0][1]

        # foo()
        # 1 joule = 0,000000277kWh
        # 1 joule = 1 Wh

        # Rediriger la sortie standard vers un flux mémoire
        with io.StringIO() as output_buffer:
            sys.stdout = output_buffer

            # Appeler la fonction foo() pour que les valeurs soient affichées dans le flux mémoire
            foo()

            # Récupérer la chaîne de caractères de la sortie capturée
            output_str = output_buffer.getvalue()

        # Rétablir la sortie standard
        sys.stdout = sys.__stdout__

        # Découper la chaîne en utilisant le séparateur ";"
        elements = output_str.split(";")

        # Extrayez les valeurs spécifiques à partir des éléments séparés
        timestamp = float(elements[0].split(":")[1].strip())
        
        # Convertir le timestamp en un objet datetime
        date = datetime.fromtimestamp(timestamp)

        tag = elements[1].split(":")[1].strip()
        duration = float(elements[2].split(":")[1].strip())
        nvidia_gpu_0 = int(elements[3].split(":")[1].strip())
        conso_kwh = nvidia_gpu_0 * 0.000000277

        # Afficher les valeurs extraites
        print("Démarrage:", date)
        print("Tag:", tag)
        print("Duration:", duration)
        print("Nvidia GPU 0:", nvidia_gpu_0)
        print("Consommation en kWh:", conso_kwh, "\n")

        return render(request, 'calcul_des_emissions.html', {'dataframe': html_table, 'TotalGHGEmissions': TotalGHGEmissions, 'SiteEnergyUse_kbtu': SiteEnergyUse_kbtu})

    else:
        # Afficher le formulaire vide
        return render(request, 'calcul_des_emissions.html')
"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""



"""
|---------------------------------------------------------------- Page landing_page_calcul.html ----------------------------------------------------------------|
"""
def landing_page_calcul(request):

    return render(request, 'landing_page_calcul.html')
"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""




"""
|---------------------------------------------------------------- Page upload_file.html pour upload un dataset dans azure ----------------------------------------------------------------|
"""
def upload_file(request):
    connect_str = "DefaultEndpointsProtocol=https;AccountName=ressourceapp;AccountKey=uQb7nkTxDgsNARJMXiHjcG6RUvYFyR+uS/StbzGv6Ygf/ioK/BhqJOjLjtgGsy6UtIsknYLe/+0s+AStWqekMg==;EndpointSuffix=core.windows.net"
    
    container_fichier = "fichier"

    # Connectez-vous à votre compte de stockage Azure
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    if request.method == 'POST':

        form_file = UploadFile(request.POST, request.FILES)
        # Recherche des erreurs de formulaire
        print(form_file.errors.as_data())

        if form_file.is_valid():
            # Récupérer le fichier à partir du formulaire
            uploaded_file = request.FILES['file_upload']
            
            # Accédez au conteneur "fichier" 
            container_client = blob_service_client.get_container_client(container=container_fichier)
            # container_client.create_container() (créez-le s'il n'existe pas)

            # Vérifier si le blob existe déjà dans le conteneur
            blob_client = container_client.get_blob_client(uploaded_file.name)
            blob_exist = blob_client.exists()

            if blob_exist:
                # Le fichier existe déjà, vous pouvez proposer de l'écraser ou gérer autrement le cas
                # Par exemple, vous pouvez renommer le nouveau fichier pour éviter les conflits
                # ou demander à l'utilisateur de confirmer l'opération.
                blob_client.upload_blob(uploaded_file, overwrite=True)
                return render(request, 'upload_file.html', {'form_file': form_file, 'blob_exist': True})

            # Le fichier n'existe pas, procédez normalement à l'upload
            blob_client.upload_blob(uploaded_file)

            # Retournez une réponse indiquant que le fichier a été téléchargé avec succès
            return render(request, 'upload_file_success.html')

    else:
        form_file = UploadFile()

    return render(request, 'upload_file.html', {'form_file': form_file, 'blob_exist': False})
"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""





"""
|---------------------------------------------------------------- Page upload_file_success.html pour upload réussi ----------------------------------------------------------------|
"""
def upload_file_success(request):
    return render(request, 'upload_file_success.html')
"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""





"""
|---------------------------------------------------------------- Page upload_model.html pour upload un modèle sur azure ----------------------------------------------------------------|
"""
def upload_model(request):
    connect_str = "DefaultEndpointsProtocol=https;AccountName=ressourceapp;AccountKey=uQb7nkTxDgsNARJMXiHjcG6RUvYFyR+uS/StbzGv6Ygf/ioK/BhqJOjLjtgGsy6UtIsknYLe/+0s+AStWqekMg==;EndpointSuffix=core.windows.net"
    
    container_model = "model"

    # Connectez-vous à votre compte de stockage Azure
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    #Récuperation du container
    container_client = blob_service_client.get_container_client(container_model)

    if request.method == 'POST':

        form_model = UploadModel(request.POST, request.FILES)
        # Recherche des erreurs de formulaire
        print(form_model.errors.as_data())
        print(form_model.fields["model_upload"])

        if form_model.is_valid():
            # Récupérer le fichier à partir du formulaire
            uploaded_model = request.FILES['model_upload']
            
            # Accédez au conteneur "fichier" 
            container_client = blob_service_client.get_container_client(container=container_model)
            # container_client.create_container() (créez-le s'il n'existe pas)

            # Vérifier si le blob existe déjà dans le conteneur
            blob_client = container_client.get_blob_client(uploaded_model.name)
            if blob_client.exists():
                # Le fichier existe déjà, vous pouvez proposer de l'écraser ou gérer autrement le cas
                # Par exemple, vous pouvez renommer le nouveau fichier pour éviter les conflits
                # ou demander à l'utilisateur de confirmer l'opération.

                # Ici, nous allons écraser automatiquement le fichier existant
                blob_client.upload_blob(uploaded_model, overwrite=True)
            else:
                # Le fichier n'existe pas, procédez normalement à l'upload
                blob_client.upload_blob(uploaded_model)

            # Retournez une réponse indiquant que le fichier a été téléchargé avec succès
            return render(request, 'upload_model_success.html')
    else:
        form_file = UploadFile()

    return render(request, 'upload_model.html', {'form_file': form_file})
"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""





"""
|---------------------------------------------------------------- Page upload_model_success.html pour upload réussi ----------------------------------------------------------------|
"""
def upload_model_success(request):
    return render(request, 'upload_model_success.html')
"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""




"""
|---------------------------------------------------------------- Page calcul_fichier_ext.html pour le calcul de csv ----------------------------------------------------------------|
"""
def calcul_fichier_ext(request):

    # Création des listes du formulaire
    connect_str = "DefaultEndpointsProtocol=https;AccountName=ressourceapp;AccountKey=uQb7nkTxDgsNARJMXiHjcG6RUvYFyR+uS/StbzGv6Ygf/ioK/BhqJOjLjtgGsy6UtIsknYLe/+0s+AStWqekMg==;EndpointSuffix=core.windows.net"

    container_file = "fichier"
    container_model = "model"

    # Connectez-vous à votre compte de stockage Azure
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Récupération des containers
    files = blob_service_client.get_container_client(container_file)
    models = blob_service_client.get_container_client(container_model)

    # Création des listes
    blob_list_files = files.list_blobs()
    blob_list_models = models.list_blobs()

    if request.method == 'POST':

        start_time = time.time()
        chemin_fichier = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp', 'resultat_prediction.csv')
        if os.path.exists(chemin_fichier):
            os.remove(chemin_fichier)

        form_calc = request.POST

        dataset = form_calc['dataset']
        model = form_calc['model']

        # Récupération du blob spécifié contenant le csv
        blob_client = blob_service_client.get_blob_client(container=container_file, blob=dataset)
        blob_data = blob_client.download_blob().readall().decode("utf-8")

        # Lecture du contenu CSV dans un DataFrame
        df = pd.read_csv(io.StringIO(blob_data), sep=";")

        # Preparation du dataframe
        select_col = ['PrimaryPropertyType', 'YearBuilt', 'NumberofBuildings', 'NumberofFloors', 'PropertyGFATotal', 'PropertyGFAParking']
        df_prepared = df[select_col].copy()
        noms_colonnes = {'PrimaryPropertyType': 'primarypropertytype',
                        'YearBuilt': 'yearbuilt',
                        'NumberofBuildings': 'numberofbuildings',
                        'NumberofFloors': 'numberoffloors',
                        'PropertyGFATotal': 'propertygfatotal',
                        'PropertyGFAParking': 'propertygfaparking'
        }
        df_prepared.rename(columns=noms_colonnes, inplace=True)
        #df_prepared = df_prepared.astype(str)
        df_prepared["numberofbuildings"].replace("0", "1", inplace=True)
        df_prepared["numberofbuildings"].fillna("1", inplace=True)
        df_prepared["numberoffloors"].replace(["0", "99"], "1", inplace=True)
        #print(f"\n{df_prepared.dtypes}")

        # Récupération du blob spécifié contenant le modèle
        blob_client_model = blob_service_client.get_blob_client(container=container_model, blob=model)
        model_data = blob_client_model.download_blob().readall()

        loaded_model = pickle.loads(model_data)

        """
        Test avec fichier temporaire
        # Téléchargement du contenu du blob vers un fichier local temporaire
        local_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp', model)
        with open(local_file_path, "wb") as file:
            blob_data = blob_client_model.download_blob()
            blob_data.readinto(file)

        # Chargement du modèle à partir du fichier local temporaire
        with open(local_file_path, "rb") as file:
            loaded_model = pickle.load(file)
        """

        #print(loaded_model)
        print("\nModel chargé : ok")

        print("\nDataframe chargé : ok\n")

        pred_matrix=loaded_model.predict(df_prepared)

        # Formatage du résultat
        df_matrix = pd.DataFrame(pred_matrix, columns=['TotalGHGEmissions_predict', 'SiteEnergyUse_kbtu_predict'])
        df_join = df_matrix.join(df, how='inner')
        select_col_result = ['PropertyName', 'PrimaryPropertyType', 'YearBuilt', 'TotalGHGEmissions_predict', 'TotalGHGEmissions', 'SiteEnergyUse_kbtu_predict', 'SiteEnergyUse(kBtu)']
        df_result = df_join[select_col_result].copy()

        # Print rapport dans la console
        print(f"\n------------ Rapport console ---------")
        print(f"Dataset => {dataset}")
        print(f"Modele => {model}")
        print(f"Matrice prédite :\n {df_matrix}")
        print(f"Prédiction test TotalGHGEmissions => {pred_matrix[0][0]}")
        print(f"Prédiction test SiteEnergyUse_kbtu => {pred_matrix[0][1]}")
        end_time = time.time()
        traitement = end_time - start_time
        print(f"------------ {traitement:.2f} seconds ------------\n")

        df_result.to_csv(chemin_fichier)
        #blob_client_test = blob_service_client.get_blob_client(container=container_file, blob='resultat_prediction.csv')
        #blob_client_test.upload_blob(df_result.to_csv(), overwrite=True)


        html_table = df_result.to_html(index=False)
        return render(request, 'calcul_fichier_ext.html', {'blob_list_files': blob_list_files, 'blob_list_models': blob_list_models, 'resultat': html_table})

    return render(request, 'calcul_fichier_ext.html', {'blob_list_files': blob_list_files, 'blob_list_models': blob_list_models} )
"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""




"""
|---------------------------------------------------------------- Page ajout_de_batiment.html pour ajouter un batiment dans une bdd ----------------------------------------------------------------|
"""
def ajout_de_batiment(request):
    if request.method == 'POST':

        form = SaveForm(request.POST)
        print(form.errors.as_data())

        if form.is_valid():
            primarypropertytype = form.cleaned_data['primarypropertytype']
            yearbuilt = form.cleaned_data['yearbuilt']
            numberofbuildings = form.cleaned_data['numberofbuildings']
            numberoffloors = form.cleaned_data['numberoffloors']
            propertygfatotal = form.cleaned_data['propertygfatotal']
            propertygfaparking = form.cleaned_data['propertygfaparking']
            
            # Crée une instance du modèle avec les données du formulaire
            mon_instance = NewBuilding(primarypropertytype=primarypropertytype, yearbuilt=yearbuilt, numberofbuildings=numberofbuildings, numberoffloors=numberoffloors, propertygfatotal=propertygfatotal, propertygfaparking=propertygfaparking)

            # Enregistre l'instance dans la table spécifique de la base de données
            mon_instance.save()
            
            # Faites quelque chose avec les données enregistrées
            
    else:
        form = SaveForm()

    return render(request, 'ajout_de_batiment.html', {'form': form})
"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""




"""
|---------------------------------------------------------------- Page bdd_seattle pour afficher le dataset fourni de seattle ----------------------------------------------------------------|
"""
def bdd_seattle(request):
    bdd_seattle = pd.DataFrame.from_records(list(Buildings.objects.all().values()))
    bdd_ajout_bat = pd.DataFrame.from_records(list(NewBuilding.objects.all().values()))

    bdd_seattle_table = bdd_seattle.head(100).to_html(index=False)
    bdd_ajout_bat_table = bdd_ajout_bat.to_html(index=False)

    return render(request, 'bdd_seattle.html', {'bdd_seattle':bdd_seattle_table,'bdd_ajout_bat': bdd_ajout_bat_table })
"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""