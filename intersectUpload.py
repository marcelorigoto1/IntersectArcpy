import arcpy
import arcgis
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from arcgis import geometry
from arcgis.features import FeatureLayerCollection
from arcgis import features



user =  '<username>'
password = '<password>'
url_portal = '<portalname>'
url_FeatureService1 =  '<FeatureService1>'
url_FeatureService2 = '<FeatureService2>'
url_upload ='<FeatureServiceReceiveUpload>'
fgdb = r'<path to gdb>'



def main(user,password,url_portal,url_FeatureService1,url_FeatureService2,url_upload,fgdb):
    print(f"Starting login in portal {url_portal}")
    
    arcpy.env.workspace = fgdb
    fc_feature1 = 'feature1'
    fc_FeatureService2 = 'feature2'

    #Login Portal Try/Catch
    try:
        gis = GIS(url_portal, user, password)
        print('Login sucessful.')
    except Exception as e:
        print(e)

    fl_FeatureService1 = FeatureLayer(url_FeatureService1)
    fl_FeatureService2 = FeatureLayer(url_FeatureService2)

    #Store Features services in GDB
    print(f'Features Services Downloaded.')

    fs_FeatureService1 = fl_FeatureService1.query()
    fs_FeatureService2 = fl_FeatureService2.query()


    #Checks if the services already exist in the directory, if they exist they are deleted
    if arcpy.Exists(fgdb+'\feature1'):
        arcpy.Delete_management(fgdb+'\feature1') 
    if arcpy.Exists(fgdb+'\feature2'):
        arcpy.Delete_management(fgdb+'\feature2')

    #Creates the shapes of the downloaded services
    shp_feature1 = fs_FeatureService1.save(fgdb, fc_feature1)
    shp_FeatureService2 = fs_FeatureService2.save(fgdb, fc_FeatureService2)
    print('Shapes Created.')

    #Prepares the features to perform the intersection and the location of the generated file
    in_features = [shp_feature1,shp_FeatureService2]
    out_feature_class = 'intersect'

    #Checks if the intersection already exists in the directory, if it exists it is deleted
    if arcpy.Exists(fgdb+'\intersect'): 
        arcpy.Delete_management(fgdb+'\intersect')

    output_intersect =  arcpy.analysis.Intersect(in_features, out_feature_class)
    print('Intersect Sucessful.')

    #Search for Feature Service that will receive the upload and deletes all features in feature service
    #This method can be changed if you need to check and edit features that alredy exist, I needed only the Area Attribute
    fl_upload = arcgis.features.FeatureLayer(url_upload)
    feature_service = gis.content.search("<url_upload_name>",item_type="Feature Service")
    upload_delete = fl_upload.delete_features(where='objectid!' != '0')
    print("Old features deleted.")

    #Generate the geometries and attributes of the shapes to be uploaded to the service
    lista_fields = ["SHAPE@","Shape_Area"]
    features_for_update = []
    for i in arcpy.da.SearchCursor(output_intersect,lista_fields):
        geometria = arcgis.geometry.Geometry(i[0])
        new_attributes = {
            "Shape_Area":i[1],
        }
        features = {"attributes":new_attributes,"geometry":geometria}

        if features["geometry"].length != None:
            features_for_update.append(features)

    #This method can be changed if you need to check and edit features that alredy exist, I needed only the Area Attribute
    #For more info check edit_features(updates =)
    #Add the shapes in the feature service
    fl_upload.edit_features(adds = features_for_update)
    print("Upload Sucessful.")

main(user,password,url_portal,url_FeatureService1,url_FeatureService2,url_upload,fgdb)

