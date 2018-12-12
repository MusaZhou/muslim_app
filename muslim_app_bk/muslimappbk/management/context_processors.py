from django.core.files.storage import default_storage
from showcase.forms import SearchForm

def upyun_url_processor(request):
    upyun = default_storage.up
    upyun_url = 'http://%s/%s' % (upyun.endpoint, upyun.service)
    search_form = SearchForm()
    return {'upyun_url': upyun_url, 'search_form': search_form}