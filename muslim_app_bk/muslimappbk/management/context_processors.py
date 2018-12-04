from django.core.files.storage import default_storage

def upyun_url_processor(request):
    upyun = default_storage.up
    upyun_url = 'http://%s/%s' % (upyun.endpoint, upyun.service) 
    return {'upyun_url': upyun_url}