# -*-coding:Utf-8 -*

from django.db import models

import datetime

from django.forms import ModelForm
from django.forms import Form, IntegerField, DateField, ChoiceField, BooleanField, TextInput  
from django import template
from django.forms.extras.widgets import SelectDateWidget
from django.forms.fields import CheckboxInput
from django.forms.formsets import  BaseFormSet
 

#pacs   = [ ('pac' + str(i), 'Personne à charge')  for i in range(1,10)]
pacs = [('pac', 'Personne à charge')]
QUIFOY = (('vous', 'Vous'), ('conj', 'Conjoint')) +  tuple(pacs)
# enfants = [ ('enf' + str(i), 'enfant')  for i in range(1,10)]
enfants = [ ('enf' , 'Enfant' )]
QUIFAM = (('chef', 'parent 1'), ('part', 'parent 2')) + tuple(enfants) 

SO = ((1, u"Accédant à la propriété"),
      (2, u"Propriétaire non accédant"), 
      (3, u"Locataire d'un logement HLM"),
      (4, u"Locataire ou sous-locataire d'un logement loué vide non-HLM"),
      (5, u"Locataire ou sous-locataire d'un logement loué meublé ou d'une chambre d'hôtel"),
      (6, u"Logé gratuitement par des parents, des amis ou l'employeur"))



register = template.Library()

@register.filter(name='is_checkbox')
def is_checkbox(value):
    return isinstance(value, CheckboxInput)

import os, inspect

cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
predirectory = os.path.dirname(cmd_folder)
directory = os.path.join(predirectory,'srcopen')

import sys
sys.path.append(directory)

from core.utils import Scenario

class BaseScenarioFormSet(BaseFormSet):    
    def get_scenario(self):
        scenario = Scenario()
        for form in self.cleaned_data:
            noi, birth = form['noi']-1, form['birth']
            idfoy, quifoy, idfam, quifam = form['idfoy']-1, form['quifoy'], form['idfam']-1, form['quifam']
            scenario.indiv.update({noi:{'birth':birth, 
                                'inv'     : 0,
                                'alt'     : 0,
                                'activite': 0,
                                'quifoy'  : quifoy,
                                'quifam'  : quifam,
                                'noidec'  : idfoy,
                                'noichef' : idfam,
                                'noipref' : 0,
                                'statmarit': 2}})
            
            scenario._assignPerson(noi, quifoy = quifoy, foyer = idfoy, quifam = quifam, famille = idfam)
            scenario.updateMen()
        return scenario


class MyBooleanField(BooleanField):
    def __init__(self, *args, **kwargs):
        BooleanField.__init__(self, required=False, *args, **kwargs)


class MyIntegerField(IntegerField):
#    def __init__(self, kwargs = {}, *args):
    def __init__(self, *args, **kwargs):
        widgetAttr = {'size':'8', 
                      'align': 'right',
                      'maxlength':'9', 
                      'style' : "text-align: right"
                      }
        wid = TextInput(attrs=widgetAttr)
        fieldAttr = {'max_value': 999999999, 
                     'min_value': 0,
                     'required' : False,
                     'localize': True
                     }
        fieldAttr.update(kwargs)
        IntegerField.__init__(self, widget = wid, **fieldAttr)


class MyDateField(DateField):
    def __init__(self, **kwargs):
        wid = SelectDateWidget(years = [i for i in reversed(xrange(1900,2010))])
        fieldAttr = {'required' : False, 
                     'localize': True
                     }
        fieldAttr.update(kwargs)
        DateField.__init__(self, widget= wid, **fieldAttr)


class IndividualForm(Form):
    noi     = IntegerField(label = u"N° de l'individu", min_value=1, max_value=99)
    birth   = DateField(widget = SelectDateWidget(years=range(1900, datetime.date.today().year)))
    idfoy   = IntegerField(label = 'N° de déclaration',min_value=1, max_value=99)
    quifoy  = ChoiceField(label = 'Position déclaration impôts',choices = QUIFOY)
    #remplirdeclar = BooleanField(required = False, initial = True, label = 'Foyer')
    idfam   = IntegerField(label = 'N° de famille', min_value=1, max_value=99)
    quifam  = ChoiceField(label = 'Position famille', choices = QUIFAM )
    statmarit = ChoiceField(label = 'Statut marital', choices = ((2,'Célibataire'), (1,'Marié'), (5,'Pacsé'), (4,'Veuf'),(5,'Divorcé')))
    activite  = ChoiceField(choices = ((0, u"Actif occupé"), (1, u"Chômeur"), (2, u"Étudiant, élève"), (3, u"Retraité"), (4, u"Autre inactif")))
    inv       = MyBooleanField(label = 'Invalide', initial=False)
    alt       = MyBooleanField(label = 'Garde alternée', initial=False)

    
class LogementForm(Form):
    so = ChoiceField(label = "Statut d'occupation",choices = SO)
    loyer = IntegerField(label = 'Loyer', initial = 500,min_value=0, max_value=100000)
    code_postal = IntegerField(label = 'Code postal', initial = 00000)
#    zone_apl = IntegerField(label = 'Zone allocation logement', initial = 0)



class Declar1Form(Form):
    statmarit = ChoiceField(choices = ((2,'Célibataire'), (1,'Marié'), (5,'Pacsé'), (4,'Veuf'),(5,'Divorcé')), initial=2)   
    

    def __init__(self, *args, **kwargs):

        super(Declar1Form, self).__init__(*args, **kwargs)
        required = False
        for quifoy in [x[0] for x in QUIFOY]:
            if quifoy == 'vous': 
                label = "Vous"
                required = False
            elif quifoy =='conj':
                label = "Votre conjoint"
            else:
                label = "Personne à charge"
            self.fields[quifoy] = MyDateField(label = label, required = required)

class Declar2Form(Form):
    def __init__(self, *args, **kwargs):
        super(Declar2Form, self).__init__(*args, **kwargs)

        cases = ['caseL', 'caseE', 'caseN', 'caseP', 'caseF', 'caseW', 'caseS', 'caseG', 'caseT']  
        for case in cases:
            self.fields[case] = MyBooleanField(initial=False)
            

from core.columns import BoolCol, IntCol

class Declar3Form(Form):
    def __init__(self, *args, **kwargs):
        description = kwargs.pop('description')
        super(Declar3Form, self).__init__(*args, **kwargs)
        fields = ['f1aj', 'f1bj', 'f1cj', 'f1dj', 
                  'f1ap', 'f1bp', 'f1cp', 'f1dp', 
                  'f1ak', 'f1bk', 'f1ck', 'f1dk', 
                  'f1ai', 'f1bi', 'f1ci', 'f1di', 
                  'f1au', 'f1bu', 'f1cu', 'f1du', 
                  'f1ax', 'f1bx', 'f1cx', 'f1dx',
                  'f1av', 'f1bv', 'f1cv', 'f1dv', 
                  'f1bl', 'f1cb',  'f1dq', 
                  'f1as', 'f1bs', 'f1cs', 'f1ds', 
                  'f1at', 'f1bt',
                  'f1ao', 'f1bo', 'f1co', 'f1do']
    
        convert = dict()
        abcd = ['a', 'b', 'c', 'd']
        for l in abcd: 
            convert['f1'+l+'j' ] = 'sali'
            convert['f1'+l+'p' ] = 'choi'
            convert['f1'+l+'k' ] = 'fra'
            convert['f1'+l+'i' ] = 'cho_ld'
            convert['f1'+l+'u' ] = 'hsup'
            convert['f1'+l+'x' ] = 'ppe_tp_sa'
            convert['f1'+l+'v' ] = 'ppe_du_sa'
            convert['f1'+l+'s' ] = 'rsti'
            convert['f1'+l+'o' ] = 'alr'             
        
        for field in fields:
            
#            print 'is ' + str(field) + ' in description :' + str( field in description.col_names) 
            
            if field not in ['f1bl', 'f1cb', 'f1dq', 'f1at', 'f1bt']:
                col = description.get_col(convert[field])
                if col.label is not None:
                    label = col.label
                else:
                    label = field    

                
                if isinstance(col, IntCol):
                    self.fields[field] = MyIntegerField(label=label)
                if isinstance(col, BoolCol):
                    self.fields[field] = MyBooleanField(label=label)

            elif field in ['f1bl', 'f1cb', 'f1dq']:                
                self.fields[field] = MyIntegerField()

    
class Declar4Form(Form):
    def __init__(self, *args, **kwargs):
        super(Declar4Form, self).__init__(*args, **kwargs)
        int_fields = ['f2da', 'f2dh', 'f2ee', 'f2dc', 'f2fu', 'f2ch', 
                      'f2ts', 'f2go', 'f2tr', 'f2cg', 'f2bh', 'f2ca', 
                      'f2ab', 'f2bg', 'f2aa', 'f2al', 'f2am', 'f2an',
                      'f2dm', 'f3vg', 'f3vh', 'f3vt', 'f3vu', 'f3vv',
                       'f4be', 'f4ba', 'f4bb', 'f4bc', 'f4bd', 'f4bf',
                       'f0xx']
        for field in int_fields:
            self.fields[field] = MyIntegerField(label='') 
    

class Declar5Form(Form):
    def __init__(self, *args, **kwargs):
        super(Declar5Form, self).__init__(*args, **kwargs)
        int_fields = ['f6de', 'f6gi', 'f6gj', 'f6el', 'f6em', 'f6gp',
                      'f6gu', 'f6dd', 'f6rs', 'f6rt', 'f6ru', 'f6ss',
                      'f6st', 'f6su', 'faps', 'fapt', 'fapu', 'fbps',
                      'fbpt', 'fbpu', 'fcps', 'fcpt', 'fcpu', 'fdps', 
                      'fdpt', 'fdpu', 'f6qs', 'f6qt', 'f6qu', 'f7ue',
                      'f7ud', 'f7uf', 'f7xs', 'f7xt', 'f7xu', 'f7xw', 
                      'f7xy', 'f7ac', 'f7ae', 'f7ag', 'f7db', 'f7df',
                      'f7dl', 'f7vy', 'f7vz', 'f7vw', 'f7vx', 'f7wn',
                      'f7wo', 'f7wm', 'f7wp', 'f7wq', 'f7wh', 'f7wk',
                      'f7wf', 'f7wi', 'f7wj', 'f7wl', 'f8by', 'f8cy',
                      'f8ut', 'f8tf', 'f8ti', 'f8tl', 'f8tk', 'f7we']
    
        bool_fields = ['f6qr', 'f6qw', 'f7dq', 'f7dg']
    
        for field in int_fields:
            self.fields[field] = MyIntegerField()
           
        for field in bool_fields:
            self.fields[field] = MyBooleanField()




class Barem(models.Model):
    val      = models.FloatField()
    code     = models.CharField(max_length=99)
    desc     = models.CharField(max_length=99)
    x        = models.IntegerField()
    class Meta:
        ordering = ('x',)
    
    
class BaremForm(ModelForm):
    class Meta:
        model = Barem
        
class Node(models.Model):
    val      = models.FloatField()
    code     = models.CharField(max_length=99)
    low      = models.FloatField()
    desc     = models.CharField(max_length=99)

class NodeForm(ModelForm):
    class Meta:
        model = Node
        
