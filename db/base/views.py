from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse


from db.base.models import Transponder, Satellite, MODE_CHOICES
from db.base.forms import SatelliteSearchForm, SuggestionForm


def home(request):
    satellites = Satellite.objects.all()
    transponders = Transponder.objects.all()
    contributors = User.objects.filter(is_active=1)

    if request.method == 'POST':
        satellite_form = SatelliteSearchForm(request.POST)
        if satellite_form.is_valid():
            term = satellite_form.cleaned_data['term']
            norad_cat_id = term.split()[0]
            try:
                satellite = Satellite.objects.get(norad_cat_id=norad_cat_id)
            except:
                messages.error(request, 'Please select one of the available Satellites')
                return redirect(reverse('home'))

            return render(request, 'base/suggest.html', {'satellites': satellites,
                                                      'transponders': transponders,
                                                      'satellite': satellite,
                                                      'contributors': contributors,
                                                      'satellite_form': satellite_form,
                                                      'modes': MODE_CHOICES})

    return render(request, 'base/home.html', {'satellites': satellites,
                                              'transponders': transponders,
                                              'contributors': contributors})


@login_required
@require_POST
def suggestion(request):
    suggestion_form = SuggestionForm(request.POST)
    if suggestion_form.is_valid():
        suggestion = suggestion_form.save(commit=False)
        suggestion.user = request.user
        suggestion.save()

        messages.success(request, ('Your suggestion was stored successfully. '
                                   'Thanks for contibuting!'))
        return redirect(reverse('home'))

    messages.error(request, 'We are sorry, but some error occured :(')
    return redirect(reverse('home'))


def about(request):
    return render(request, 'base/about.html')


def faq(request):
    return render(request, 'base/faq.html')
