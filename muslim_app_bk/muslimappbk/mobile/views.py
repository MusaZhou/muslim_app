from django.shortcuts import render, get_object_or_404
from management.models import MobileApp, Banner, AppCategory
from django_comments_xtd.models import (TmpXtdComment,
                                        XtdComment,
                                        MaxThreadLevelExceededException,
                                        LIKEDIT_FLAG, DISLIKEDIT_FLAG)
from django_comments_xtd.forms import XtdCommentForm
from django.http import Http404, HttpResponseForbidden
from django.db.models import Q

def index(request):
    banner_list = Banner.objects.all()
    category_list = AppCategory.objects.all()
    context = {'banner_list': banner_list, 'category_list': category_list}
    return render(request, 'mobile/index.html', context)

def app(request, slug):
    mobile_app = get_object_or_404(MobileApp.objects.prefetch_related('images', 'videos', 'ratings', 'tags'), slug=slug)
    app_version = mobile_app.latest_version()
    context = {'mobile_app': mobile_app, 'app_version': app_version}
    return render(request, 'mobile/app.html', context)

def reply(request, cid, app_slug):
    try:
        comment = XtdComment.objects.get(pk=cid)
        if not comment.allow_thread():
            raise MaxThreadLevelExceededException(comment)
    except MaxThreadLevelExceededException as exc:
        return HttpResponseForbidden(exc)
    except XtdComment.DoesNotExist as exc:
        raise Http404(exc)

    form = XtdCommentForm(comment.content_object, comment=comment)

    template_arg = [
        "mobile/reply.html",
    ]
    return render(request, template_arg,
                  {"comment": comment, "form": form, "cid": cid, 'app_slug': app_slug})
    
def search(request):
    search_word = request.POST.get('search_word', 'Quran')
    app_list = MobileApp.shown_apps.filter(Q(name__icontains=search_word)|\
                                           Q(description__icontains=search_word)|\
                                           Q(category__name__icontains=search_word))
    context = {'app_list': app_list}
    return render(request, 'mobile/search.html', context)
