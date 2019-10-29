from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from assets import models
from assets import asset_handler


# Create your views here.


@csrf_exempt
def report(request):
    if request.method == "POST":
        asset_data = request.POST.get('asset_data')
        data = json.loads(asset_data)
        if not data:
            return HttpResponse("No Data")

        if not issubclass(dict, type(data)):
            return HttpResponse("Data type should be Dictionary")

        sn = data.get('sn', None)
        if sn:
            asset_obj = models.Asset.objects.filter(sn=sn)
            if asset_obj:
                update_asset = asset_handler.UpdateAsset(request, asset_obj[0], data)
                return HttpResponse("Asset info has been updated!")
            else:
                obj = asset_handler.NewAsset(request, data)
                response = obj.add_to_new_assets_zone()
                return HttpResponse(response)
        else:
            return HttpResponse("Asset SN number not founded, Please check your data!")

    return HttpResponse('200 ok')
