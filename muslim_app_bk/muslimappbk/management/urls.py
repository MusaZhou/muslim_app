from django.urls import path
from . import views
from .views import UpdateMobileAppView,  AppTableBasicView,\
AddAppVersionView, AppHistoryView, VersionDetailView
from .views_uploader import AppTableUploaderView, AppHistoryUploaderView,\
PDFListViewUploader, InspiredVideoListUploaderView, VideoAlbumListUploaderView
from .views import BannerListView, BannerEditView
from django.views.decorators.cache import cache_page
from .views_pdf import PDFListView, PDFEditView, PDFDetailView
from .views_inspired_video import InspiredVideoListView, InspiredVideoEditView,\
InspiredVideoDetailView, VideoAlbumListView, VideoAlbumEditView, VideoAlbumDetailView

app_name = 'management'

urlpatterns = [
    path('add_mobile_app', cache_page(24 * 60 * 60 * 15)(views.add_mobile_app), name='add_mobile_app'),
    path('update_mobile_app/<str:slug>', UpdateMobileAppView.as_view(), name='update_mobile_app'),
    path('add_app_version/<str:slug>', cache_page(24 * 60 * 60 * 15)(AddAppVersionView.as_view()), name='add_app_version'),
    path('app_table_basic', AppTableBasicView.as_view(), name='app_table_basic'),
    path('app_history/<str:slug>', AppHistoryView.as_view(), name='app_history'),
    path('version_detail/<str:app_slug>-<str:version_number>', cache_page(24 * 60 * 60 * 15)(VersionDetailView.as_view()), name='version_detail'),
    path('banner_list', BannerListView.as_view(), name="banner_list"),
    path('add_banner', cache_page(24 * 60 * 60 * 15)(BannerEditView.as_view()), name="add_banner"),
    path('edit_banner/<int:id>', BannerEditView.as_view(), name="edit_banner"),
    path('index', views.index, name="index"),
    path('pdf_list', PDFListView.as_view(), name="pdf_list"),
    path('add_pdf', cache_page(24 * 60 * 60 * 15)(PDFEditView.as_view()), name="add_pdf"),
    path('edit_pdf/<str:slug>', PDFEditView.as_view(), name="edit_pdf"),
    path('detail_pdf/<str:slug>', PDFDetailView.as_view(), name="detail_pdf"),
    path('inspired_video_list', InspiredVideoListView.as_view(), name="inspired_video_list"),
    path('add_inspired_video', cache_page(24 * 60 * 60 * 15)(InspiredVideoEditView.as_view()), name="add_inspired_video"),
    path('edit_inspired_video/<str:slug>', InspiredVideoEditView.as_view(), name="edit_inspired_video"),
    path('detail_inspired_video/<str:slug>', InspiredVideoDetailView.as_view(), name="detail_inspired_video"),
    path('video_album_list', VideoAlbumListView.as_view(), name='video_album_list'),
    path('add_video_album', cache_page(24 * 60 * 60 * 15)(VideoAlbumEditView.as_view()), name='add_video_album'),
    path('edit_video_album/<str:slug>', VideoAlbumEditView.as_view(), name="edit_video_album"),
    path('detail_video_album/<str:slug>', VideoAlbumDetailView.as_view(), name="detail_video_album"),
    
    # Uploader path
    path('app_table_uploader', AppTableUploaderView.as_view(), name='app_table_uploader'),
    path('app_history_uploader/<str:slug>', AppHistoryUploaderView.as_view(), name='app_history_uploader'),
    path('pdf_list_uploader', PDFListViewUploader.as_view(), name="pdf_list_uploader"),
    path('inspired_video_list_uploader', InspiredVideoListUploaderView.as_view(), name="inspired_video_list_uploader"),
    path('video_album_list_uploader', VideoAlbumListUploaderView.as_view(), name='video_album_list_uploader'),

]
