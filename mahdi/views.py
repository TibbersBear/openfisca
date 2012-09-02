# -*-coding:Utf-8 -*

from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from mahdi.models import (IndividualForm,
                          LogementForm,
                          Declar1Form, Declar2Form, Declar3Form, Declar4Form, Declar5Form)

from django.forms.formsets import formset_factory

from mahdi.interfaces import Simu, Compo, BaseScenarioFormSet


import os, inspect

cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
predirectory = os.path.dirname(cmd_folder)
directory = os.path.join(predirectory,'srcopen')

import sys
sys.path.append(directory)


from france.data import InputTable
from core.datatable import DataTable
from core.utils import Scenario


def menage(request):
    compo = request.session.get('compo', default=None)
    if compo == None:
        compo = Compo()
    if compo.scenario.nbIndiv() == 0:
        compo = Compo()

    if request.method == 'POST':

        if 'reset' in request.POST:
            if 'compo' in request.session:
                del request.session['compo']
            compo = Compo()
            formset = compo.gen_formset()
            request.session['compo'] = compo

        else:
            ScenarioFormSet = formset_factory(IndividualForm, formset = BaseScenarioFormSet)
            formset = ScenarioFormSet(request.POST)
            if formset.is_valid():
                compo.scenario = formset.get_scenario()
        
                if 'add' in request.POST:
                    compo.addPerson()
                    
                elif 'remove' in request.POST:
                    compo.scenario.rmvIndiv(compo.scenario.nbIndiv()-1)

                elif 'validate' in request.POST:
                    print compo.scenario
                
                formset = compo.gen_formset()
                request.session['compo'] = compo
                
                if 'submit' in request.POST:
                    compo.scenario.genNbEnf()
                    simu = Simu(compo.scenario)
                    simu.build()                    
#                    for child in simu.data_courant.children:
#                        for child2 in child.children:
#                            print child2.code
#                            print child2._vals
#    
                    request.session['data'] = simu.data_courant
                    return render(request, 'mahdi/output.html')
            else:
                print 'fromset is not vali in menage' 
            
    else:
        
        formset = compo.gen_formset()
        request.session['compo'] = compo

    units = {'foy': range(1,len(compo.scenario.declar)+1),
             'fam': range(1,len(compo.scenario.famille)+1),
             'ind': range(1,compo.scenario.nbIndiv()+1)}
    
    c = {'formset': formset, 'units' : units}
    c.update(csrf(request))
    return render(request, 'mahdi/menage.html', c)

def output(request):
    return render_to_response('mahdi/output.html')    


#from matplotlib.figure import Figure
#from widgets.Output import drawBareme, drawWaterfall
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#
#def graph_old(request):
#    data = request.session['data']
##    for child in data.children:
##        for child2 in child.children:
##            print child2.code
##            print child2._vals
#
#    
#    xaxis = 'sal' #self.xaxis
#    reforme = False
#    dataDefault = None
#    legend = False
#    fig = Figure()
#    ax = fig.add_subplot(111)
#    drawWaterfall(data, ax)
##    drawBareme(data, ax, xaxis, reforme = reforme,
##               dataDefault = dataDefault, legend = legend)
##    drawBareme(ax, data)
##    print 'apres drawbareme'
##    print fig
#
#    canvas = FigureCanvas(fig)    
#    response= HttpResponse(content_type='image/png')
#    canvas.print_png(response)
#    return response
#




from mahdi.utils import get_zone

def logement(request):

    print 'entering logement'
    print request.method
    compo = request.session.get('compo', default=None)
    commune = 'Indéterminée'
    zone_apl = 0
    
    if request.method == 'POST':
        logt_form = LogementForm(request.POST)
        if logt_form.is_valid():
            vals = logt_form.cleaned_data
            print request.POST    
            if 'validate' in request.POST:
                # compute the apl zone
                commune, zone_apl = compo.set_logement(vals)
                request.session['compo'] = compo
            elif 'submit' in request.POST:
                request.session['compo'] = compo    
    else:
        logt_form = LogementForm()
    c = {'logt_form': logt_form, 'commune' : commune, 'zone_apl' :zone_apl}
    c.update(csrf(request))
    return render(request, 'mahdi/logement.html', c)


def home(request):
    return render_to_response('mahdi/home.html')    

def declar01(request, idfoy=None):
    compo = request.session.get('compo' , default=None)
    if idfoy is None:
        idfoy = 0
    else:
        idfoy = int(idfoy)     
    
    if request.method == 'POST':
        form = Declar1Form(request.POST)
        if form.is_valid():
            compo.get_declar1(data=form.cleaned_data, idfoy = idfoy)
            form = compo.create_declar1(idfoy=idfoy)        
            request.session['compo'] = compo
            return HttpResponseRedirect('/mahdi/declar02/' + str(idfoy))

    else:
        form  = compo.create_declar1(idfoy=idfoy)
    
    request.session['compo'] = compo            
    c = {'form': form}
    c.update(csrf(request))
    return render(request, 'mahdi/declar01.html', c)   
        

def declar02(request, idfoy):
    compo = request.session.get('compo' , default=None)
    if idfoy is None:
        idfoy = 0
    else:
        idfoy = int(idfoy)     

    if request.method == 'POST':
        print 'entering POST'
        form = Declar2Form(request.POST)
        if form.is_valid():
            compo.get_declar(form=form, idfoy = idfoy)
            form = compo.create_declar(Declar2Form, idfoy=idfoy)        
            request.session['compo'] = compo
            return HttpResponseRedirect('/mahdi/declar03/' + str(idfoy))        

    else:
        form  = compo.create_declar(Declar2Form, idfoy=idfoy)

    request.session['compo'] = compo            
    c = {'form': form}
    c.update(csrf(request))
    return render(request, 'mahdi/declar02.html', c)   
    
    
def declar03(request, idfoy):
    
    description = DataTable(InputTable).description
    compo = request.session.get('compo' , default=None)
    if idfoy is None:
        idfoy = 0
    else:
        idfoy = int(idfoy)     
    
    if request.method == 'POST':
        form = Declar3Form(request.POST, description = description)
        print 'declar 3: is form valid :', form.is_valid() 
        if form.is_valid():
            compo.get_declar3(form=form, idfoy = idfoy)
            form = compo.create_declar3(idfoy=idfoy, description = description)        
            request.session['compo'] = compo
            for indiv, val in compo.scenario.indiv.iteritems():
                print indiv
                print val
                
            return HttpResponseRedirect('/mahdi/declar04/' + str(idfoy))

    else:
    
        form = Declar3Form(description = description)

    request.session['compo'] = compo            
    c = {'form': form}
    c.update(csrf(request))
    return render(request, 'mahdi/declar03.html', c)   

        

def declar04(request, idfoy):
    compo = request.session.get('compo' , default=None)
    if idfoy is None:
        idfoy = 0
    else:
        idfoy = int(idfoy)     

    if request.method == 'POST':
        print 'entering POST'
        form = Declar4Form(request.POST)
        if form.is_valid():
            compo.get_declar(form=form, idfoy = idfoy)
            form = compo.create_declar(Declar4Form, idfoy=idfoy)        
            request.session['compo'] = compo
            return HttpResponseRedirect('/mahdi/declar05/' + str(idfoy))

    else:
        form  = compo.create_declar(Declar4Form, idfoy=idfoy)

    request.session['compo'] = compo
    c = {'form': form}
    c.update(csrf(request))
    return render(request, 'mahdi/declar04.html', c)   


def declar05(request, idfoy = None):
    compo = request.session.get('compo' , default=None)
    if idfoy is None:
        idfoy = 0
    else:
        idfoy=int(idfoy)
    
    if request.method == 'POST':
        form = Declar5Form(request.POST)
        if form.is_valid():
            compo.get_declar(form=form, idfoy = idfoy)
            form = compo.create_declar(Declar5Form, idfoy=idfoy)        
            request.session['compo'] = compo
            return render(request, 'mahdi/menage.html')
    else:
        form  = compo.create_declar(Declar5Form, idfoy=idfoy)

    request.session['compo'] = compo            
    c = {'form': form}
    c.update(csrf(request))
    return render(request, 'mahdi/declar05.html', c)   


from chartit import DataPool, Chart
from mahdi.models import Node, NodeForm
from django.db.models import Sum


def graph(request):
    
    ## TODO use low as in http://stackoverflow.com/questions/7969300/highcharts-column-chart
    ## http://fiddle.jshell.net/delfino4747/M8npu/10/
    #data = request.session['data']
    
    scenario = Scenario()
    simu = Simu(scenario=scenario, nmen=1)
    simu.build()
    data = simu.data_courant
    codes  = []    
    
    data.setLeavesVisible()
    
    Node.objects.all().delete()
    
    

    def create_waterfall_NodeForm(node, prv):
        '''
        Creates waterfall node Forms    
        '''
        if node.code == 'nivvie':
            return
        prev = prv + 0
        val = node.vals[0]
        bot = prev
        for child in node.children:
            create_waterfall_NodeForm(child, prev)
            prev += child.vals[0]
        if (val != 0)  and (node.visible) and (node.code != 'root'):
            # r,g,b = node.color
            print node.code
            form = NodeForm(data = {'code': node.code, 'val': val, 'desc': node.desc, 'low': bot })
            form.save()
            codes.append(node.code)
        
    prv = 0
    create_waterfall_NodeForm(data, prv)
    print codes
    
    openfisca_data = DataPool(
       series=
        [{'options': {
            'source': Node.objects.all()},
            'terms': [  'low', 'val', 'code','desc' ]}
         ])
    
    #Step 2: Create the Chart object


    cht = Chart(
        datasource = openfisca_data,
        series_options = 
            [{'options':{
                         'type': 'column',
                          'allowPointSelect': 'true'                         
                         },
              'terms': { 'code' : ['low' , 'val'] }
#                                   {}} , 
#                                {'start': {'showInLegend': False,
#                                           'color' : 'transparent',
#                                           'shadow' : False,
#                                           'borderColor' : 'transparent',
#                                           'borderWidth' : 0,
#                                           #'visible' : False,
#                                           }}
                       }],
        chart_options =
          {'title' : {
               'text': 'Openfisca'},
           }
            )
    
    #Step 3: Send the chart object to the template.
    return render_to_response('mahdi/chartit_graph.html', {'chart': cht})

from mahdi.models import Barem, BaremForm


from chartit import PivotDataPool, PivotChart
def graphBR(request):
    #data = request.session['data']
    
    scenario = Scenario()
    nmen = 11
    simu = Simu(scenario=scenario, nmen = nmen)
    simu.build()
    data = simu.data_courant

    
    if True:
#    if self.mode == 'bareme':
        data['salsuperbrut'].setHidden()
        data['salbrut'].setHidden()
        data['chobrut'].setHidden()
        data['rstbrut'].setHidden()



    codes  = []
    data.setLeavesVisible()
    
    
    def set_visible_level(node, level):
        if level == 0:
            node.visible = True
        else: 
            node.visible = False
        for child in node.children:
            set_visible_level(child, level-1)
    
    set_visible_level(data,5)
    
    
    Barem.objects.all().delete()
    def create_BaremForm(node):
        '''
        Creates waterfall node Forms    
        '''

        for child in node.children:
            create_BaremForm(child)
        index = 0
        if (node.code != 'root') and node.visible:
            for val in node.vals:
                index += 1
                # r,g,b = node.color
                form = BaremForm(data = {'code': node.code, 'val': val, 'desc': node.desc, 'x': index })
                form.save()            
            codes.append(node.code)
        

    create_BaremForm(data)
    print codes

        
#    openfisca_data = DataPool(
#       series=
#        [{'options': {
#            'source': Barem.objects.all(),
#            'categories': ['x']},
#          'terms': [
#            'val',
#            'code',
#            'desc','x']}
#         ])
    



#    cht = Chart(
#        datasource = openfisca_data,
#        series_options = 
#            [{'options':{
#                         'type': 'area',
#                         'stacking': 'normal',
#                         },
#                         
#              'terms':{
#                       'x': [ {'val': {},
#                               }
#                                ]
#                       }}],
#        chart_options =
#          {'title' : {
#               'text': 'Openfisca'},
#           'xAxis' : {'categories': codes}
#           }
#            )
    
    def sortx(x):
        y = x[0][0]
        print y
        return int(round(float(y)*1e6))
    

    openfisca_data = PivotDataPool(
       series=
        [{'options': {
            'source': Barem.objects.all(),
            'categories': ['x'],
            'legend_by': 'code'},
          'terms': { 'val': Sum('val')}, 
            }
         ],
        sortf_mapf_mts = (sortx , lambda x: x,True))
    #Step 2: Create the Chart object

    print openfisca_data.series

    cht = PivotChart(
        datasource = openfisca_data,
        series_options = 
            [{'options':{
                         'type': 'area',
                         'stacking': 'normal',
                         },
                         
              'terms':[{'val': {}},
                        ]
                       }],
        chart_options =
          {'title' : {
               'text': 'Openfisca'},
           'xAxis' : {'categories': codes}
           }
            )



    
    #Step 3: Send the chart object to the template.
    return render_to_response('mahdi/chartit_graph.html', {'chart': cht})


