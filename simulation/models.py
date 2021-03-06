# -*-coding:Utf-8 -*

#from django.db import models
import datetime
from django.db import models

from django.forms import Form, IntegerField, DateField, ChoiceField, BooleanField, TextInput  
from django.forms.formsets import BaseFormSet
from django import template

from django.forms.extras.widgets import SelectDateWidget

from django.forms.fields import CheckboxInput
from mahdi.interfaces import Compo



pacs   = [ ('pac' + str(i), 'Personne à charge')  for i in range(1,10)]
QUIFOY = (('vous', 'Vous'), ('conj', 'Conjoint')) +  tuple(pacs)
enfants = [ ('enf' + str(i), 'enfant')  for i in range(1,10)]
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

class IndividualForm(Form):
    noi = IntegerField(label = 'n°')
    birth   = DateField(widget = SelectDateWidget(years=range(1900, datetime.date.today().year)))
    idfoy  = IntegerField(label = 'Numéro de déclaration')
    quifoy  = ChoiceField(label = 'Position déclaration impôts',choices = QUIFOY)
    #remplirdeclar = BooleanField(required = False, initial = True, label = 'Foyer')
    idfam = IntegerField(label = 'Numéro de famille')
    quifam = ChoiceField(label = 'Position famille', choices = QUIFAM )

class LogementForm(Form):
    so = ChoiceField(label = "Statut d'occupation",choices = SO)
    loyer = IntegerField(label = 'Loyer', initial = 500)
    code_postal = IntegerField(label = 'Code postal', initial = 69001)

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



class Declar1Form(Form):
    statmarit = ChoiceField(choices = ((2,'Célibataire'), (1,'Marié'), (5,'Pacsé'), (4,'Veuf'),(5,'Divorcé')))   
    statmarit.initial = 2

    
    def __init__(self, *args, **kwargs):
        super(Declar1Form, self).__init__(*args, **kwargs)
        
        
    def set_declar(self, compo = None, idfoy = None):
        if 'compo' is not None:
            compo = compo
        else:
            compo = Compo()
        
        if 'idfoy' is not None:
            idfoy = idfoy
        else:
            idfoy = 0
        
        scenario = compo.scenario
        birth_dates = {}
        print scenario
        for dct in scenario.indiv.itervalues():        
            if dct['noidec'] == idfoy:
                print dct
                quifoy = dct['quifoy']
                if quifoy == "vous":
                    statmarit = dct['statmarit']
                birth_dates[quifoy] = dct['birth']
                
        
        for quifoy, birth_date in birth_dates.iteritems():
            if quifoy == 'vous': 
                label = "Vous"
                self.fields['statmarit'].value = statmarit
            elif quifoy =='conj':
                label = "Votre conjoint"
            else:
                label = "Personne à charge"
            
            self.fields[quifoy] = MyDateField(initial = birth_date,
                                              label = label)

class Declar2Form(Form):
    def __init__(self, *args, **kwargs):
        super(Declar2Form, self).__init__(*args, **kwargs)

        cases = ['caseL', 'caseE', 'caseN', 'caseP', 'caseF', 'caseW', 'caseS', 'caseG', 'caseT']  
        for case in cases:
            self.fields[case] = MyBooleanField()
            
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
                print col
                print label
                
                if isinstance(col, IntCol):
                    self.fields[field] = MyIntegerField(label=label)
                if isinstance(col, BoolCol):
                    self.fields[field] = MyBooleanField(label=label)

            elif field in ['f1bl', 'f1cb', 'f1dq']:                
                self.fields[field] = MyIntegerField(label='')

    
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


class MonthlyWeatherByCity(models.Model):
    month = models.IntegerField()
    boston_temp = models.DecimalField(max_digits=5, decimal_places=1)
    houston_temp = models.DecimalField(max_digits=5, decimal_places=1)

from django.forms import ModelForm
class MonthlyWeatherByCityForm(ModelForm):
    class Meta:
        model = MonthlyWeatherByCity