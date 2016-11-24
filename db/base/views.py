import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

from db.base.models import Mode, Transmitter, Satellite, Suggestion
from db.base.forms import SuggestionForm

logger = logging.getLogger('db')


def home(request):
    """View to render home page."""
    satellites = Satellite.objects.all()
    transmitters = Transmitter.objects.all().count()
    suggestions = Suggestion.objects.all().count()
    contributors = User.objects.filter(is_active=1).count()
    return render(request, 'base/home.html', {'satellites': satellites,
                                              'transmitters': transmitters,
                                              'contributors': contributors,
                                              'suggestions': suggestions})


def custom_404(request):
    """Custom 404 error handler."""
    return HttpResponseNotFound(render(request, '404.html'))


def custom_500(request):
    """Custom 500 error handler."""
    return HttpResponseServerError(render(request, '500.html'))


def robots(request):
    data = render(request, 'robots.txt', {'environment': settings.ENVIRONMENT})
    response = HttpResponse(data,
                            content_type='text/plain; charset=utf-8')
    return response


def satellite(request, norad):
    """View to render home page."""
    satellite = get_object_or_404(Satellite, norad_cat_id=norad)
    suggestions = Suggestion.objects.filter(satellite=satellite)
    modes = Mode.objects.all()

    return render(request, 'base/satellite.html', {'satellite': satellite,
                                                   'suggestions': suggestions,
                                                   'modes': modes})


@login_required
@require_POST
def suggestion(request):
    """View to process suggestion form"""
    suggestion_form = SuggestionForm(request.POST)
    if suggestion_form.is_valid():
        suggestion = suggestion_form.save(commit=False)
        suggestion.user = request.user
        suggestion.save()

        # Notify admins
        admins = User.objects.filter(is_superuser=True)
        site = get_current_site(request)
        subject = '[{0}] A new suggestion was submitted'.format(site.name)
        template = 'emails/new_suggestion.txt'
        saturl = '{0}{1}'.format(
            site.domain,
            reverse('satellite', kwargs={'norad': suggestion.satellite.norad_cat_id})
        )
        data = {
            'satname': suggestion.satellite.name,
            'saturl': saturl,
            'site_name': site.name
        }
        message = render_to_string(template, {'data': data})
        for user in admins:
            try:
                user.email_user(subject, message, from_email=settings.DEFAULT_FROM_EMAIL)
            except:
                logger.error(
                    'Could not send email to user',
                    exc_info=True
                )

        messages.success(request, ('Your suggestion was stored successfully. '
                                   'Thanks for contibuting!'))
        return redirect(reverse('satellite', kwargs={'norad': suggestion.satellite.norad_cat_id}))
    else:
        logger.error(
            'Suggestion form was not valid {0}'.format(suggestion_form.errors),
            exc_info=True,
            extra={
                'form': suggestion_form.errors,
            }
        )
        messages.error(request, 'We are sorry, but some error occured :(')
        return redirect(reverse('home'))


def about(request):
    """View to render about page."""
    return render(request, 'base/about.html')


def faq(request):
    """View to render faq page."""
    return render(request, 'base/faq.html')


def statistics(request):
    """View to create statistics endpoint."""
    satellites = Satellite.objects.all()
    transmitters = Transmitter.objects.all()
    modes = Mode.objects.all()

    total_satellites = satellites.count()
    total_transmitters = transmitters.count()
    alive_transmitters = transmitters.filter(alive=True).count()
    alive_transmitters_percentage = '{0}%'.format((alive_transmitters / total_transmitters) * 100)

    total_modes = []
    for mode in modes:
        tr = transmitters.filter(mode=mode).count()
        data = {
            'name': mode.name,
            'count': tr
        }
        total_modes.append(data)

    bands = []

    # <30.000.000 - HF
    filtered = transmitters.filter(downlink_low__lt=30000000).count()
    bands.append({
        'name': 'HF',
        'count': filtered
    })

    # 30.000.000 ~ 300.000.000 - VHF
    filtered = transmitters.filter(downlink_low__gte=30000000,
                                   downlink_low__lt=300000000).count()
    bands.append({
        'name': 'VHF',
        'count': filtered
    })
    bands.append(data)

    # 300.000.000 ~ 1.000.000.000 - UHF
    filtered = transmitters.filter(downlink_low__gte=300000000,
                                   downlink_low__lt=1000000000).count()
    bands.append({
        'name': 'UHF',
        'count': filtered
    })
    bands.append(data)

    # 1G ~ 2G - L
    filtered = transmitters.filter(downlink_low__gte=1000000000,
                                   downlink_low__lt=2000000000).count()
    bands.append({
        'name': 'L',
        'count': filtered
    })
    bands.append(data)

    # 2G ~ 4G - S
    filtered = transmitters.filter(downlink_low__gte=2000000000,
                                   downlink_low__lt=4000000000).count()
    bands.append({
        'name': 'S',
        'count': filtered
    })
    bands.append(data)

    # 4G ~ 8G - C
    filtered = transmitters.filter(downlink_low__gte=4000000000,
                                   downlink_low__lt=8000000000).count()
    bands.append({
        'name': 'C',
        'count': filtered
    })
    bands.append(data)

    # 8G ~ 12G - X
    filtered = transmitters.filter(downlink_low__gte=8000000000,
                                   downlink_low__lt=12000000000).count()
    bands.append({
        'name': 'X',
        'count': filtered
    })
    bands.append(data)

    # 12G ~ 18G - Ku
    filtered = transmitters.filter(downlink_low__gte=12000000000,
                                   downlink_low__lt=18000000000).count()
    bands.append({
        'name': 'Ku',
        'count': filtered
    })
    bands.append(data)

    # 18G ~ 27G - K
    filtered = transmitters.filter(downlink_low__gte=18000000000,
                                   downlink_low__lt=27000000000).count()
    bands.append({
        'name': 'K',
        'count': filtered
    })
    bands.append(data)

    # 27G ~ 40G - Ka
    filtered = transmitters.filter(downlink_low__gte=27000000000,
                                   downlink_low__lt=40000000000).count()
    bands.append({
        'name': 'Ka',
        'count': filtered
    })
    bands.append(data)

    statistics = {
        'total_satellites': total_satellites,
        'transmitters': total_transmitters,
        'transmitters_alive': alive_transmitters_percentage,
        'modes': total_modes,
        'bands': bands
    }
    return JsonResponse(statistics, safe=False)
