import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import nibabel as nib
import numpy as np
from glob import glob
import os.path as op
import json
import sys

sys.path.append('..')  # to enable loading from utils
from utils import load_data, index_by_slice, standardize

# csrf_protect = False because otherwise gunicorn doesn't
# serve the app properly
app = dash.Dash(csrf_protect=False)
server = app.server

# Load config (with mappings)
with open('config.json') as config:    
    cfg = json.load(config)

# Get the first key (random) from mappings, and load contrast/func
global_contrast_name = list(cfg['mappings'].keys())[0]
global_func, global_contrast = load_data(global_contrast_name, load_func=True)
global_func = standardize(global_func)

# Kind of an hack: save on disk which contrast we've loaded
# (to avoid reloading the func-data every callback)
with open("current_contrast.txt", "w") as text_file:
    text_file.write(global_contrast_name)

# Use the mean as background
if global_func.shape[:3] == (91, 109, 91):
    bg = nib.load(op.join('..', 'standard.nii.gz')).get_data()
else:
    print("Not yet implemented!")

colors = {
    'background': '#000000',
    'text': '#D3D3D3'
}

# Start layout of app
app.layout = html.Div(
    
    children=[

        html.Div(className='ten columns offset-by-one', children=[

            html.H1(children='VoxelViz: An interactive viewer for BOLD-fMRI data',
                    style={'textAlign': 'center', 'color': colors['text']},
                    id='title'),

            html.Div(className='row' ,children=[
                
                dcc.Markdown("""Developed for the [TransIP](https://www.transip.nl/) VPS-competition""")
            ], style={'textAlign': 'center', 'color': colors['text'], 'padding-bottom': '20px'})

        ]),

        html.Div(className='five columns', children=[

            html.Div(className='row', children=[

                html.Div(className='five columns', children=[
                    
                    dcc.Dropdown(options=[
                                    {'value': key, 'label': val} for key, val in cfg['mappings'].items()
                                 ],
                                 value=global_contrast_name,
                                 id='contrast')
                ]),
                
                html.Div(className='three columns', children=[
                    
                    dcc.RadioItems(
                        id='direction',
                        options=[
                            {'label': 'X', 'value': 'X'},
                            {'label': 'Y', 'value': 'Y'},
                            {'label': 'Z', 'value': 'Z'}
                        ],
                        labelStyle={'display': 'inline-block'},
                        value='X')
                ]),
                
                html.Div(className='four columns', children=[

                    dcc.Slider(
                        min=0,
                        step=1,
                        value=50,
                        id='slice'),

                ]),

            ], style={'padding-bottom': '20px'}),

            html.Div(className='row', children=[

                dcc.Graph(id='brainplot', animate=False)

            ]),

            html.Div(className='row', children=[

                html.Div(className='two columns', children=[

                    html.P('Threshold:')
                ]),

                html.Div(className='ten columns', children=[

                    dcc.Slider(id='threshold',
                               min=0,
                               max=6,
                            step=0.1,
                            value=2.3,
                            marks={i: i for i in np.arange(0, 6.5, 0.5)})
                ])
            ]),
        ]),

        html.Div(className='six columns', children=[

            html.Div(className='row', children=[

                html.Div(className='twelve columns', children=[
                    dcc.Checklist(
                        options=[
                                {'label': 'Voxel', 'value': 'voxel'},
                                {'label': 'Model', 'value': 'model'}
                                ],
                        values=['voxel'])#, labelStyle={'display': 'inline-block'})
                ], style={'padding-left': '550px'})
                    
            ]),
            
            html.Div(className='row', children=[

                dcc.Graph(id='brainplot_time', animate=False)
            ]),

            html.Div(className='row', children=[

                html.P(id='explanation')
            ]),

        ])
    ]
)


@app.callback(
    Output(component_id='slice', component_property='max'),
    [Input(component_id='direction', component_property='value')])
def update_slice_slider(direction):

    # To fix!
    srange = {'X': 91,
              'Y': 109,
              'Z': 91}

    return srange[direction]

@app.callback(
    Output(component_id='brainplot', component_property='figure'),
    [Input(component_id='threshold', component_property='value'),
     Input(component_id='contrast', component_property='value'),
     Input(component_id='direction', component_property='value'),
     Input(component_id='slice', component_property='value')])
def update_brainplot(threshold, contrast, direction, sslice):
    
    with open("current_contrast.txt", "r") as text_file:
        current_contrast = text_file.readlines()[0]

    if contrast != current_contrast:
        global global_contrast
        global_contrast = load_data(contrast, load_func=False)

        with open("current_contrast.txt", "w") as text_file:
            text_file.write(contrast)
    
    bg_slice = index_by_slice(direction, sslice, bg)
    img_slice = index_by_slice(direction, sslice, global_contrast)

    bg_map = go.Heatmap(z=bg_slice.T, colorscale='Greys', showscale=False, hoverinfo="none", name='background')
    tmp = np.ma.masked_where(np.abs(img_slice) < threshold, img_slice)
    func_map = go.Heatmap(z=tmp.T, opacity=1, name='test',
                          colorbar={'thickness': 20, 'title': 'Z-val', 'x': -.1})

    layout = go.Layout(autosize=True,
                       margin={'t': 50, 'l': 5, 'r': 5},
                       plot_bgcolor=colors['background'],
                       paper_bgcolor=colors['background'],
                       font={'color': colors['text']},
                       title='Activation pattern: %s' % contrast,
                       xaxis=dict(autorange=True,
                                  showgrid=False,
                                  zeroline=False,
                                  showline=False,
                                  autotick=True,
                                  ticks='',
                                  showticklabels=False),
                       yaxis=dict(autorange=True,
                                  showgrid=False,
                                  zeroline=False,
                                  showline=False,
                                  autotick=True,
                                  ticks='',
                                  showticklabels=False))

    return {'data': [bg_map, func_map], 'layout': layout}

@app.callback(
    Output(component_id='brainplot_time', component_property='figure'),
    [Input(component_id='threshold', component_property='value'),
     Input(component_id='contrast', component_property='value'),
     Input(component_id='direction', component_property='value'),
     Input(component_id='slice', component_property='value'),
     Input(component_id='brainplot', component_property='hoverData')])
def update_brainplot_time(threshold, contrast, direction, sslice, hoverData):
    
    with open("current_contrast.txt", "r") as text_file:
        current_contrast = text_file.readlines()[0]

    if contrast != current_contrast:
        global global_contrast, global_func
        global_func, global_contrast = load_data(contrast, load_func=True)
        global_func = standardize(global_func)

        with open("current_contrast.txt", "w") as text_file:
            text_file.write(contrast)
    
    if hoverData is None:
        x, y = 40, 40
    else:
        x = hoverData['points'][0]['x']
        y = hoverData['points'][0]['y']
    
    img = index_by_slice(direction, sslice, global_func)
    data = go.Scatter(x=np.arange(global_func.shape[-1]), y=img[x, y, :].ravel())
    layout = go.Layout(autosize=True,
                       margin={'t': 50, 'l': 50, 'r': 5},
                       plot_bgcolor=colors['background'],
                       paper_bgcolor=colors['background'],
                       title='Activation over time',
                       font={'color': colors['text']},
                       xaxis=dict(#autorange=False,
                                  showgrid=True,
                                  zeroline=True,
                                  showline=True,
                                  autotick=True,
                                  #ticks='',
                                  showticklabels=True,
                                  title='Time'),
                       yaxis=dict(autorange=True,
                                  showgrid=True,
                                  zeroline=True,
                                  showline=True,
                                  autotick=True,
                                  #ticks='',
                                  showticklabels=True,
                                  title='Activation (contrast estimate)'))
                                  #range=[-4, 4]))

    return {'data': [data], 'layout': layout}

external_css = ["https://codepen.io/lukassnoek/pen/Kvzmzv.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

#app.css.append_css({"relative_package_path": "app.css"})

if __name__ == '__main__':
    app.run_server()
