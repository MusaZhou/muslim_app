from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save
from .choices import ACTIVE_CHOICES, APPROVE_CHOICES, GENDER_CHOICES
from django_comments_xtd.moderation import moderator, XtdCommentModerator
from django.urls import reverse
from star_ratings.models import Rating
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from ordered_model.models import OrderedModel
from taggit.managers import TaggableManager
from django.db.models import Q
import datetime

class ApprovedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(approve_status='approved')
    
# Create your models here.
class Profile(models.Model):
    nick_name = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Nick Name"))
    gender =models.CharField(max_length=10, verbose_name=_("Gender"),
                             choices=GENDER_CHOICES, default='male')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=_("Date of birth"))
    avatar = models.ImageField(upload_to="avatar/%Y/%m/%d/",blank=True, null=True, verbose_name=_("Avatar"))
    wechatid = models.CharField(max_length=100,blank=True,db_index=True,null=True)
    weiboid = models.CharField(max_length=100,blank=True,db_index=True,null=True)
    qqid = models.CharField(max_length=100,blank=True,db_index=True,null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.user.username, allow_unicode=True)
        super(Profile, self).save(*args, **kwargs)
    
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        if not hasattr(instance, 'profile'):
            Profile.objects.create(user=instance)
        instance.profile.save()

class Image(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey()
    picture = models.ImageField(upload_to="pictures/%Y/%m/%d/",blank=True, max_length=150)
    width = models.CharField(null=True, max_length=8, blank=True)
    height = models.CharField(null=True, max_length=8, blank=True)
    upyun_task_id = models.UUIDField(blank=True, null=True)
    thumbnail_picture = models.ImageField(upload_to="pictures",blank=True, max_length=150, null=True)

    def __str__(self):
        return self.picture.url
    
class Video(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey()
    file = models.FileField(upload_to="videos", blank=True, null=True, max_length=150)
    upyun_task_id = models.UUIDField(blank=True, null=True)
    width = models.PositiveIntegerField(null=True)
    height = models.PositiveIntegerField(null=True)
    duration = models.PositiveIntegerField(null=True)

class AppCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Category'))

    def __str__(self):
        return self.name
    
class ActiveAppManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
class ShownAppManager(ActiveAppManager):
    def get_queryset(self):
        qs_appversion = AppVersion.approved_manager.values_list('mobile_app', flat=True).distinct()
        return super().get_queryset().filter(id__in=qs_appversion)
    
class UploadOrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('-upload_date')
        

class MobileApp(OrderedModel):
    name = models.CharField(max_length=100,unique=True,
                            db_index=True, verbose_name=_('App Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    upload_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  verbose_name=_('Uploader'))
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Upload Time'), db_index=True)
    category = models.ForeignKey(AppCategory, on_delete=models.CASCADE)
    comment_count = models.PositiveIntegerField(null=True, verbose_name=_('Comment Count'), default=0)
    download_count = models.PositiveIntegerField(null=True, verbose_name=_('Download Count'), default=0)
    slug = models.CharField(unique=True, null=True, blank=True, db_index=True, max_length=100, \
                            validators=[validators.validate_unicode_slug])
    images = GenericRelation(Image, related_query_name='imaged_app', verbose_name=_('Screenshots'))
    tags = TaggableManager()
    is_active = models.BooleanField(default=False, verbose_name=_('Active Status'))
    icon = models.ImageField(upload_to="icons")
    developer = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Developer"))
    ratings = GenericRelation(Rating, related_query_name='rating_apps')
    videos = GenericRelation(Video, related_query_name='video_app', verbose_name=_('Video Show'))
    
    order_with_respect_to = 'category'
    
    objects = models.Manager()
    active_apps = ActiveAppManager()
    shown_apps = ShownAppManager()
    upload_order = UploadOrderManager()
    
    class Meta(OrderedModel.Meta):
        permissions = (("can_approve_app", "Can approve newly uploaded app"),)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
    
        super(MobileApp, self).save(*args, **kwargs)
    
    def latest_version(self):
        if self.canShow():
            return self.versions.filter(approve_status='approved').select_related('apk')[0]
        return None
    
    def get_absolute_url(self):
        return reverse('showcase:app', args=[self.slug])
    
    def has_approved_version(self):
        if self.versions.filter(approve_status='approved').exists():
            return True
        return False
    
    def canShow(self):
        return self.is_active and self.has_approved_version()
    
    @property
    def userLink(self):
        return reverse('showcase:app', args=[self.slug])
    
    @property
    def user_link_mobile(self):
        return reverse('mobile:app', args=[self.slug])
    
    @property
    def latestAPK(self):
        latestVersion = self.latest_version()
        if latestVersion is not None:
            return latestVersion.apk.file.url
        return None
    
    def latestTime(self):
        latestVersion = self.latest_version()
        if latestVersion is not None:
            return latestVersion.created_time
        return None
    
    @property
    def avg_rate(self):
        last_rating = self.ratings.last()
        if last_rating is not None:
            return last_rating.average
        return 5.0
           
class AppVersion(models.Model):
    version_number = models.CharField(max_length=10,
                                      validators=[validators.RegexValidator("[a-zA-Z0-9\.]*")],
                                      verbose_name=_('Version No.'))
    created_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Created Time'), db_index=True)
    approve_status = models.CharField(max_length=10,
                                      choices=APPROVE_CHOICES,
                                      default='new', verbose_name=_('Approve Status'))
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE,
                                    null=True, blank=True, verbose_name=_('Approved By'))
    approved_time = models.DateTimeField(null=True, blank=True, verbose_name=_('Approved Time'))
    mobile_app = models.ForeignKey(MobileApp, on_delete=models.CASCADE, blank=True,
                                   null=True, verbose_name=_('Application'), related_name='versions')
    whats_new = models.TextField(blank=True, null=True, verbose_name=_("What's New"))
    translator = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Translator"))
    android_version = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Supported Android Version"))
    remark = models.CharField(max_length=200, null=True, blank=True, verbose_name=_("Remark"))
    
    objects = models.Manager()
    approved_manager = ApprovedManager()
    
    class Meta:
        ordering = ["-created_time"]
        unique_together = (('mobile_app', 'version_number'),)
        get_latest_by = "created_time"
    
    def __str__(self):
        return self.version_number

class ApkFile(models.Model):
    app_version = models.OneToOneField(AppVersion, on_delete=models.CASCADE, null=True, related_name='apk')
    file = models.FileField(upload_to="apk", blank=True, null=True,verbose_name=_("APK File"), \
                            validators=[validators.FileExtensionValidator(['apk', 'xapk'])])

class Download(models.Model):
    download_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Download At'))
    os = models.CharField(max_length=100, verbose_name=_('Operating System'))
    mobile = models.CharField(max_length=100, verbose_name=_('Mobile Phone'))
    app = models.ForeignKey(MobileApp,on_delete=models.CASCADE,
                            null=True, verbose_name=_('Application'))

class Banner(models.Model):
    title = models.CharField(verbose_name=_('Title'), max_length=100)
    description = models.TextField(verbose_name=_('Description'), blank=True, null=True)
    image = models.ImageField(upload_to='banners', verbose_name=_('Banner Image'))
    link = models.CharField(verbose_name=_("Link"), max_length=200)
    
    def __str__(self):
        return self.title

class AppCommentModerator(XtdCommentModerator):
    removal_suggestion_notification = True
    email_notification = True

moderator.register(MobileApp, AppCommentModerator)
 
class PDFDoc(models.Model):
    title = models.CharField(verbose_name=_('Title'), max_length=200, unique=True)
    description = models.TextField(verbose_name=_('Description'), blank=True, null=True)
    tags = TaggableManager()
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Upload Time'), db_index=True)
    approve_status = models.CharField(max_length=10,
                                      choices=APPROVE_CHOICES,
                                      default='new', verbose_name=_('Approve Status'))
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,
                                    null=True, blank=True, verbose_name=_('Approved By'),\
                                    related_name='pdf_approved')
    approved_time = models.DateTimeField(null=True, blank=True, verbose_name=_('Approved Time'))
    upload_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  verbose_name=_('Uploader'), related_name='pdf_uploaded')
    download_count = models.PositiveIntegerField(null=True, verbose_name=_('Download Count'), default=0)
    slug = models.CharField(unique=True, null=True, blank=True, db_index=True, max_length=100, \
                            validators=[validators.validate_unicode_slug])
    ratings = GenericRelation(Rating, related_query_name='rating_pdf')
    remark = models.CharField(max_length=200, null=True, blank=True, verbose_name=_("Remark"))
    author = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Author'))
    publish_year = models.DateField(null=True, blank=True, verbose_name=_('Publish Year'))
    
    objects = models.Manager()
    approved_pdf = ApprovedManager()
    
    class Meta:
        ordering = ["-upload_time"]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super(PDFDoc, self).save(*args, **kwargs)
    
    def canShow(self):
        return self.approve_status == 'approved'
    
    def get_absolute_url(self):
        return reverse('showcase:detail_pdf', args=[self.slug])
    
    def __str__(self):
        return self.title

class PDFFile(models.Model):
    pdf_doc = models.ForeignKey(PDFDoc, on_delete=models.CASCADE, null=True, related_name='pdf_files')
    file = models.FileField(upload_to="pdf", blank=True, null=True,verbose_name=_("PDF File"), \
                            validators=[validators.FileExtensionValidator(['pdf'])])
    
class VideoAlbum(models.Model):
    title = models.CharField(max_length=100, verbose_name=_('Title'), unique=True) 
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Upload Time'), db_index=True)
    approve_status = models.CharField(max_length=10,choices=APPROVE_CHOICES,
                                      default='new', verbose_name=_('Approve Status'))
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,
                                    null=True, blank=True, verbose_name=_('Approved By'),\
                                    related_name='album_approved')
    approved_time = models.DateTimeField(null=True, blank=True, verbose_name=_('Approved Time'))
    upload_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  verbose_name=_('Uploader'), related_name='album_uploaded')
    slug = models.CharField(unique=True, null=True, blank=True, db_index=True, max_length=100, \
                            validators=[validators.validate_unicode_slug])
    images = GenericRelation(Image, related_query_name='imaged_video_album', verbose_name=_('Public Image'))
    remark = models.CharField(max_length=200, null=True, blank=True, verbose_name=_("Remark"))
    
    objects = models.Manager()
    approved_albums = ApprovedManager()
    
    class Meta:
        ordering = ["-upload_time"]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super(VideoAlbum, self).save(*args, **kwargs)
            
    def __str__(self):
        return self.title
    
    def get_image(self):
        return self.images.last()

class ShownInspiredVideoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(Q(approve_status='approved') & (Q(album__approve_status='approved') | Q(album__isnull=True)))
            
class InspiredVideo(models.Model):
    video = GenericRelation(Video, related_query_name='video_controller', verbose_name=_('video'))
    title = models.CharField(max_length=100, verbose_name=_('title'), unique=True)
    description = models.TextField(blank=True, null=True, verbose_name=_('description'))
    tags = TaggableManager()
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Upload Time'), db_index=True)
    approve_status = models.CharField(max_length=10,choices=APPROVE_CHOICES,
                                      default='new', verbose_name=_('Approve Status'))
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,
                                    null=True, blank=True, verbose_name=_('Approved By'),\
                                    related_name='video_approved')
    approved_time = models.DateTimeField(null=True, blank=True, verbose_name=_('Approved Time'))
    upload_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  verbose_name=_('Uploader'), related_name='video_uploaded')
    slug = models.CharField(unique=True, null=True, blank=True, db_index=True, max_length=100, \
                            validators=[validators.validate_unicode_slug])
    ratings = GenericRelation(Rating, related_query_name='rating_video')
    remark = models.CharField(max_length=200, null=True, blank=True, verbose_name=_("Remark"))
    album = models.ForeignKey(VideoAlbum, null=True, blank=True, verbose_name=_("Album"),on_delete=models.CASCADE,\
                              related_name='album_videos')
    view_count = models.PositiveIntegerField(verbose_name=_("View Count"), default=0)
    images = GenericRelation(Image, related_query_name='thumnail_video')
    
    objects = models.Manager()
    approved_videos = ApprovedManager()
    shown_videos = ShownInspiredVideoManager()
    
    class Meta:
        ordering = ["-upload_time"]
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
    
        super(InspiredVideo, self).save(*args, **kwargs)
        
    def latest_valid_video(self):
        return self.video.exclude(file__isnull=True).exclude(file__exact='').last()
    
    def thumbnail(self):
        return self.images.last()
    
    def thumbnail_path(self):
        return str(self.thumbnail() or '')
    
    def __str__(self):
        return self.title
    
    @property
    def userLink(self):
        return reverse('showcase:detail_inspired_video', args=[self.slug])
    
    @property
    def user_link_mobile(self):
        return reverse('showcase:detail_inspired_video', args=[self.slug])
#         return reverse('mobile:app', args=[self.slug])

    def video_duration(self):
        return self.latest_valid_video().duration
    
    @property
    def video_duration_str(self):
        seconds = self.video_duration() or 0
        return str(datetime.timedelta(seconds=seconds))
    
@receiver(post_save, sender=InspiredVideo)    
@receiver(post_save, sender=MobileApp)
@receiver(post_save, sender=PDFDoc)
def add_rating(sender, instance, **kwargs):
    if sender.__name__ == 'MobileApp':
        if not Rating.objects.filter(rating_apps=instance).exists():
            Rating.objects.rate(instance, 5, '127.0.0.1')
            
    if sender.__name__ == 'PDFDoc':
        if not Rating.objects.filter(rating_pdf=instance).exists():
            Rating.objects.rate(instance, 5, '127.0.0.1')
    
    if sender.__name__ == 'InspiredVideo':
        if not Rating.objects.filter(rating_video=instance).exists():
            Rating.objects.rate(instance, 5, '127.0.0.1')