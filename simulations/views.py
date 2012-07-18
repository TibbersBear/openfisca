# -*-coding:Utf-8 -*

#from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from simulations.models import IndividuForm
from django.core.context_processors import csrf
#from django.core.urlresolvers import reverse
from facades.views import facade
from simulations.fonctiontest import appellemoi
from dossiertest.fonctiontest import appellemoi2
from srcopen import lanceur
import os

def lancement():
    print('je suis dans le dossier après lancement'), os.getcwd()
    os.chdir('/home/florent/workspace/openfisca/srcopen')
    print('je suis dans le dossier après lancement et modification'), os.getcwd()
    lanceur.main()
    
def simulation(request):
    if request.method == 'POST': # If the form has been submitted...
        indivform = IndividuForm(request.POST) # A form bound to the POST data
        if indivform.is_valid(): # All validation rules pass
            indivform.cleaned_data
            #print form
            indivform = facade(indivform) # je fais appel à la façade et je met le résultat dans la variable form qui s'appelera résultat plus tard
            appellemoi()
            appellemoi2()
            print('je suis dans le dossier avant lancement'), os.getcwd()
            lancement()
            #subprocess.Popen('cd /home/florent/workspace/openfisca/srcopen && python lanceur.py', shell=True)
            #return HttpResponseRedirect(reverse('simulations.views.resultats', form)) # Redirect after POST
            return render_to_response('simulations/resultats.html', {'individuform': indivform})
    else:
        indivform = IndividuForm() # An unbound form
    c = {'individuform': indivform}
    c.update(csrf(request))
    return render_to_response('simulations/simulation.html', c)

#def resultats(request, donnees):
#    return render_to_response('simulations/resultats.html', donnees)