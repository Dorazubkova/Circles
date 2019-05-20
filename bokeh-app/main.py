#!/usr/bin/env python
# coding: utf-8

# In[22]:


import bokeh
from bokeh.server.server import Server as server
from bokeh.io import show, output_notebook
from bokeh.plotting import figure, show, output_notebook
from bokeh.tile_providers import CARTODBPOSITRON
import pandas as pd
import os
import sys
from bokeh.models import ColumnDataSource, HoverTool, LassoSelectTool, Label, Title
from bokeh.layouts import gridplot
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.plotting import ColumnDataSource, Figure
from bokeh.models.widgets import PreText, Paragraph, Select, Dropdown, RadioButtonGroup, RangeSlider, Slider, CheckboxGroup
import bokeh.layouts as layout
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
output_notebook()


# In[23]:


matrix = pd.read_csv('tinao/matrix.csv', sep = ';', encoding='cp1251')
matrix = matrix.groupby(['taz_from','taz_to']).sum().reset_index()

taz_centr = pd.read_csv('tinao/taz_centr.csv', sep = ';')
taz_centr = taz_centr.drop_duplicates()

matrix = pd.merge(matrix, taz_centr, how = 'inner', 
               left_on = ['taz_from'], right_on=['taz_id']).rename(columns={'X':'X_from','Y':'Y_from'})
matrix = pd.merge(matrix,  taz_centr, how = 'inner', 
            left_on = ['taz_to'], right_on=['taz_id']).rename(columns={'X':'X_to','Y':'Y_to'})
matrix = matrix[['taz_from','taz_to','cnt_auto','cnt_tran', 'cnt_walk', 'X_from','Y_from','X_to','Y_to']]
matrix['cnt_auto'] = round(matrix['cnt_auto'],2)
matrix['cnt_tran'] = round(matrix['cnt_tran'],2)
matrix['cnt_walk'] = round(matrix['cnt_walk'],2)
matrix = matrix[(matrix['cnt_auto'] > 1) & (matrix['cnt_tran'] > 1) & (matrix['cnt_walk'] > 1)]
matrix


# In[24]:


cds = dict(X_from=list(matrix['X_from'].values), 
            Y_from=list(matrix['Y_from'].values),
            taz_from=list(matrix['taz_from'].values),
            taz_to=list(matrix['taz_to'].values),
            X_to=list(matrix['X_to'].values), 
            Y_to=list(matrix['Y_to'].values),
           cnt_auto=list(matrix['cnt_auto'].values),
            cnt_tran=list(matrix['cnt_tran'].values), 
            cnt_walk=list(matrix['cnt_walk'].values))

source_from = ColumnDataSource(data = cds)
source_to = ColumnDataSource(data = cds)
source_from2 = ColumnDataSource(data = cds)
source_to2 = ColumnDataSource(data = cds)


# In[25]:


lasso_from = LassoSelectTool(select_every_mousemove=False)
lasso_to = LassoSelectTool(select_every_mousemove=False)

lasso_from2 = LassoSelectTool(select_every_mousemove=False)
lasso_to2 = LassoSelectTool(select_every_mousemove=False)

toolList_from = [lasso_from, 'tap', 'reset', 'save', 'pan','wheel_zoom']
toolList_to = [lasso_to, 'tap', 'reset', 'save', 'pan','wheel_zoom']

toolList_from2 = [lasso_from2, 'tap', 'reset', 'save', 'pan','wheel_zoom']
toolList_to2 = [lasso_to2, 'tap', 'reset', 'save', 'pan','wheel_zoom']

p = figure(x_range=(4144652.455 , 4231682.949), y_range=(7544374.557,  7466466.973),
          x_axis_type="mercator", y_axis_type="mercator", tools=toolList_from)
p.add_tile(CARTODBPOSITRON)
p.add_layout(Title(text='Фильтр корреспонденций "ИЗ"', text_font_size='10pt', text_color = 'blue'), 'above')


r = p.circle(x = 'X_from',
         y = 'Y_from',
         source=source_from,
        fill_color='navy',
        size=10,
        fill_alpha = 1,
        nonselection_fill_alpha=1,
        nonselection_fill_color='gray')


# In[26]:


p_to = figure(x_range=(4144652.455 , 4231682.949), y_range=(7544374.557,  7466466.973),
          x_axis_type="mercator", y_axis_type="mercator", tools=toolList_to)
p_to.add_tile(CARTODBPOSITRON)

t = p_to.circle(x = 'X_to', y = 'Y_to', fill_color='red', fill_alpha = 0.6, 
                line_color='red', line_alpha = 0.8, size=6 , source = source_to,
                   nonselection_fill_alpha = 0.6, nonselection_fill_color = 'red')


ds = r.data_source
tds = t.data_source


# In[27]:


p2 = figure(x_range=(4144652.455 , 4231682.949), y_range=(7544374.557,  7466466.973),
          x_axis_type="mercator", y_axis_type="mercator", tools=toolList_from2)
p2.add_tile(CARTODBPOSITRON)
p2.add_layout(Title(text='Фильтр корреспонденций "В"', text_font_size='10pt', text_color = 'green'), 'above')


r2 = p2.circle(x = 'X_to',
         y = 'Y_to',
         source=source_to2,
        fill_color='green',
        size=10,
        fill_alpha = 1,
        nonselection_fill_alpha=1,
        nonselection_fill_color='gray')


# In[28]:


p_from = figure(x_range=(4144652.455 , 4231682.949), y_range=(7544374.557,  7466466.973),
          x_axis_type="mercator", y_axis_type="mercator", tools=toolList_to2)
p_from.add_tile(CARTODBPOSITRON)

t2 = p_from.circle(x = 'X_from', y = 'Y_from', fill_color='red', fill_alpha = 0.6, 
                line_color='red', line_alpha = 0.8, size=6 , source = source_from2,
                   nonselection_fill_alpha = 0.6, nonselection_fill_color = 'red')


ds2 = r2.data_source
tds2 = t2.data_source


# In[29]:


#widgets

checkbox_group = CheckboxGroup(labels=['cnt_auto', 'cnt_tran', 'cnt_walk'], active=[])
checkbox_group2 = CheckboxGroup(labels=['cnt_auto', 'cnt_tran', 'cnt_walk'], active=[])


# In[30]:


def callback(attrname, old, new):

    check = checkbox_group.active
    
    idx = source_from.selected.indices

    print("Indices of selected circles from: ", idx)
    print("Length of selected circles from: ", len(idx))

    #таблица с выбранными индексами 
    df = pd.DataFrame(data=ds.data).iloc[idx]
    #сумма movements по выделенным индексам
    size_cnt_auto = df.groupby(['X_to','Y_to'])['cnt_auto'].transform(sum)
    size_cnt_tran = df.groupby(['X_to','Y_to'])['cnt_tran'].transform(sum)
    size_cnt_walk = df.groupby(['X_to','Y_to'])['cnt_walk'].transform(sum)
    
    df['size_cnt_auto'] = size_cnt_auto
    df['size_cnt_tran'] = size_cnt_tran
    df['size_cnt_walk'] = size_cnt_walk

    p_to = figure(x_range=(4144652.455 , 4231682.949), y_range=(7544374.557,  7466466.973),
                  x_axis_type="mercator", y_axis_type="mercator", tools=toolList_to)
    p_to.add_tile(CARTODBPOSITRON)
     
    t = p_to.circle(x = 'X_to', y = 'Y_to', fill_color='red', fill_alpha = 1, 
                            line_color='red', line_alpha = 1, size=6 , source = source_to,
                           nonselection_fill_alpha = 1, nonselection_fill_color = 'red', 
                            nonselection_line_color='red', nonselection_line_alpha = 1)  

    test = df.drop_duplicates(['X_to','Y_to'])
    
    print(test)
    
    q = 0
    w = 1
    e = 2

    if not idx: #если пустое выделение

        layout1.children[1] = p_to #обновить график справа

    else: #если не пустое выделение
        
        if q in check:

            test = test[test['size_cnt_auto'] != 0]
            
            new_data_text = dict()
            new_data_text['x'] = list(test['X_to'])
            new_data_text['y'] = list(test['Y_to'])
            text = list(test['size_cnt_auto'])
            new_data_text['text'] = [round(x, 1) for x in text]
            
            print(new_data_text['text'])
            
            new_data = dict()
            new_data['x'] = list(test['X_to'])
            new_data['y'] = list(test['Y_to'])  
            new_data['size'] = [x / 3 for x in new_data_text['text']]

            t_to = p_to.circle(x = [], y = [], fill_color='darkturquoise', fill_alpha = 0.6, 
                                line_color='cadetblue', line_alpha = 0.9, size=[] )
            tds_to=t_to.data_source
            tds_to.data = new_data

            l = p_to.text(x = [], y = [], text_color='black', text =[], text_font_size='8pt',
                         text_font_style = 'bold' , text_align = 'center', text_baseline = 'top')
            lds=l.data_source
            lds.data = new_data_text

            layout1.children[1] = p_to #обновить график справа
            
        if w in check:

            test = test[test['size_cnt_tran'] != 0]
            
            new_data_text = dict()
            new_data_text['x'] = list(test['X_to'])
            new_data_text['y'] = list(test['Y_to'])
            text = list(test['size_cnt_tran'])
            new_data_text['text'] = [round(x, 1) for x in text]
            
            print(new_data_text['text'])
            
            new_data = dict()
            new_data['x'] = list(test['X_to'])
            new_data['y'] = list(test['Y_to'])  
            new_data['size'] = [x / 3 for x in new_data_text['text']]

            t_to = p_to.circle(x = [], y = [], fill_color='gold', fill_alpha = 0.6, 
                                line_color='darkgoldenrod', line_alpha = 0.9, size=[] )
            tds_to=t_to.data_source
            tds_to.data = new_data

            l = p_to.text(x = [], y = [], text_color='black', text =[], text_font_size='8pt',
                         text_font_style = 'bold',text_align = 'left', text_baseline = 'middle')
            lds=l.data_source
            lds.data = new_data_text

            layout1.children[1] = p_to #обновить график справа
            
        if e in check:
            
            test = test[test['size_cnt_walk'] != 0]
            
            new_data_text = dict()
            new_data_text['x'] = list(test['X_to'])
            new_data_text['y'] = list(test['Y_to'])
            text = list(test['size_cnt_walk'])
            new_data_text['text'] = [round(x, 1) for x in text]
            
            print(new_data_text['text'])
            
            new_data = dict()
            new_data['x'] = list(test['X_to'])
            new_data['y'] = list(test['Y_to'])  
            new_data['size'] = [x / 3 for x in new_data_text['text']]

            t_to = p_to.circle(x = [], y = [], fill_color='olivedrab', fill_alpha = 0.6, 
                                line_color='darkolivegreen', line_alpha = 0.9, size=[] )
            tds_to=t_to.data_source
            tds_to.data = new_data

            l = p_to.text(x = [], y = [], text_color='black', text =[], text_font_size='8pt',
                         text_font_style = 'bold', text_align = 'right', text_baseline = 'bottom')
            lds=l.data_source
            lds.data = new_data_text

            layout1.children[1] = p_to #обновить график справа
            
        else:
            
            layout1.children[1] = p_to
            
        
checkbox_group.on_change('active', callback)
source_from.selected.on_change('indices', callback) 


# In[31]:


def callback2(attrname, old, new):

    check = checkbox_group2.active
    
    idx = source_to2.selected.indices

    print("Indices of selected circles from: ", idx)
    print("Length of selected circles from: ", len(idx))

    #таблица с выбранными индексами 
    df = pd.DataFrame(data=ds2.data).iloc[idx]
    
    #сумма movements по выделенным индексам
    size_cnt_auto = df.groupby(['X_from','Y_from'])['cnt_auto'].transform(sum)
    size_cnt_tran = df.groupby(['X_from','Y_from'])['cnt_tran'].transform(sum)
    size_cnt_walk = df.groupby(['X_from','Y_from'])['cnt_walk'].transform(sum)
    
    df['size_cnt_auto'] = size_cnt_auto
    df['size_cnt_tran'] = size_cnt_tran
    df['size_cnt_walk'] = size_cnt_walk

    p_from = figure(x_range=(4144652.455 , 4231682.949), y_range=(7544374.557,  7466466.973),
                  x_axis_type="mercator", y_axis_type="mercator", tools=toolList_to2)
    p_from.add_tile(CARTODBPOSITRON)
     
    t2 = p_from.circle(x = 'X_to', y = 'Y_to', fill_color='red', fill_alpha = 1, 
                            line_color='red', line_alpha = 1, size=6 , source = source_from2,
                           nonselection_fill_alpha = 1, nonselection_fill_color = 'red', 
                            nonselection_line_color='red', nonselection_line_alpha = 1)  

    test = df.drop_duplicates(['X_from','Y_from'])
    
    print(test)
    
    q = 0
    w = 1
    e = 2

    if not idx: #если пустое выделение

        layout2.children[1] = p_from #обновить график справа

    else: #если не пустое выделение
        
        if q in check:

            test = test[test['size_cnt_auto'] != 0]
            
            new_data_text = dict()
            new_data_text['x'] = list(test['X_from'])
            new_data_text['y'] = list(test['Y_from'])
            text = list(test['size_cnt_auto'])
            new_data_text['text'] = [round(x, 1) for x in text]
            
            print(new_data_text['text'])
            
            new_data = dict()
            new_data['x'] = list(test['X_from'])
            new_data['y'] = list(test['Y_from'])  
            new_data['size'] = [x / 3 for x in new_data_text['text']]

            t_from = p_from.circle(x = [], y = [], fill_color='darkturquoise', fill_alpha = 0.6, 
                                line_color='cadetblue', line_alpha = 0.9, size=[] )
            tds_from=t_from.data_source
            tds_from.data = new_data

            l_from = p_from.text(x = [], y = [], text_color='black', text =[], text_font_size='8pt',
                         text_font_style = 'bold' , text_align = 'center', text_baseline = 'top')
            lds_from=l_from.data_source
            lds_from.data = new_data_text

            layout2.children[1] = p_from #обновить график справа
            
        if w in check:

            test = test[test['size_cnt_tran'] != 0]
            
            new_data_text = dict()
            new_data_text['x'] = list(test['X_from'])
            new_data_text['y'] = list(test['Y_from'])
            text = list(test['size_cnt_tran'])
            new_data_text['text'] = [round(x, 1) for x in text]
            
            print(new_data_text['text'])
            
            new_data = dict()
            new_data['x'] = list(test['X_from'])
            new_data['y'] = list(test['Y_from'])  
            new_data['size'] = [x / 3 for x in new_data_text['text']]

            t_from = p_from.circle(x = [], y = [], fill_color='gold', fill_alpha = 0.6, 
                                line_color='darkgoldenrod', line_alpha = 0.9, size=[] )
            tds_from=t_from.data_source
            tds_from.data = new_data

            l_from = p_from.text(x = [], y = [], text_color='black', text =[], text_font_size='8pt',
                         text_font_style = 'bold' , text_align = 'center', text_baseline = 'top')
            lds_from=l_from.data_source
            lds_from.data = new_data_text

            layout2.children[1] = p_from #обновить график справа
            
        if e in check:
            
            test = test[test['size_cnt_walk'] != 0]
            
            new_data_text = dict()
            new_data_text['x'] = list(test['X_from'])
            new_data_text['y'] = list(test['Y_from'])
            text = list(test['size_cnt_walk'])
            new_data_text['text'] = [round(x, 1) for x in text]
            
            print(new_data_text['text'])
            
            new_data = dict()
            new_data['x'] = list(test['X_from'])
            new_data['y'] = list(test['Y_from'])  
            new_data['size'] = [x / 3 for x in new_data_text['text']]

            t_from = p_from.circle(x = [], y = [], fill_color='olivedrab', fill_alpha = 0.6, 
                                line_color='darkolivegreen', line_alpha = 0.9, size=[] )
            tds_from=t_from.data_source
            tds_from.data = new_data

            l_from = p_from.text(x = [], y = [], text_color='black', text =[], text_font_size='8pt',
                         text_font_style = 'bold' , text_align = 'center', text_baseline = 'top')
            lds_from=l_from.data_source
            lds_from.data = new_data_text

            layout2.children[1] = p_from #обновить график справа
            
        else:
            
            layout2.children[1] = p_from
            
        
checkbox_group2.on_change('active', callback2)
source_to2.selected.on_change('indices', callback2)


# In[32]:


layout1 = layout.row(p, p_to, checkbox_group)
layout2 = layout.row(p2, p_from, checkbox_group2)

# Create Tabs
box = layout.column(layout1, layout2)

curdoc().add_root(box)


# In[ ]:




