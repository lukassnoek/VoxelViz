import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import nibabel as nib
import numpy as np
from utils import load_data, index_by_slice

# csrf_protect = False because otherwise gunicorn doesn't
# serve the app properly
app = dash.Dash(csrf_protect=False)
server = app.server

# Get the functional data (4D timeseries)
func, contrast = load_data('self', 'action')
func -= func.mean(axis=-1, keepdims=True)
func /= func.std(axis=-1, keepdims=True)

# Use the mean as background
bg = nib.load('standard.nii.gz').get_data()

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

            html.Div(className='row', style={'textAlign': 'center', 'color': colors['text']}, children=[
                dcc.Markdown("""Developed for the [TransIP](https://www.transip.nl/) VPS-competition""")
                ])
            ]),

        
        html.Div(className='five columns', children=[

            html.Div(className='row', children=[

                html.Div(className='five columns', children=[
                    
                    dcc.Dropdown(options=[{'label': 'action', 'value': 'action'},
                                          {'label': 'interoception', 'value': 'interoception'},
                                          {'label': 'situation', 'value': 'situation'},
                                          {'label': 'action > interoception', 'value': 'action>interoception'},
                                          {'label': 'action > situation', 'value': 'action>situation'},
                                          {'label': 'interoception > situation', 'value': 'interoception>situation'}],
                                 value='action',
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

                ]),

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

            html.Div(className='row', style={'textAlign': 'center'}, children=[

                html.P(' ')]),
            
            html.Div(className='row', children=[

                dcc.Graph(id='brainplot_time', animate=False)
                ])
        ])

    ]
)


@app.callback(
    Output(component_id='slice', component_property='max'),
    [Input(component_id='direction', component_property='value')])
def update_slice_slider(direction):

    srange = {'X': contrast.shape[0],
              'Y': contrast.shape[1],
              'Z': contrast.shape[2]}

    return srange[direction]

@app.callback(
    Output(component_id='brainplot', component_property='figure'),
    [Input(component_id='threshold', component_property='value'),
     Input(component_id='contrast', component_property='value'),
     Input(component_id='direction', component_property='value'),
     Input(component_id='slice', component_property='value')])
def update_brainplot(threshold, contrast, direction, sslice):
    name = contrast
    _, contrast = load_data('self', contrast)
    bg_slice = index_by_slice(direction, sslice, bg)
    img_slice = index_by_slice(direction, sslice, contrast)

    bg_map = go.Heatmap(z=bg_slice.T, colorscale='Greys', showscale=False, hoverinfo="none", name='background')
    tmp = np.ma.masked_where(np.abs(img_slice) < threshold, img_slice)
    func_map = go.Heatmap(z=tmp.T, opacity=1, name='test',
                          colorbar={'thickness': 20, 'title': 'Z-val', 'x': -.1})

    layout = go.Layout(autosize=True,
                       margin={'t': 50, 'l': 5, 'r': 5},
                       plot_bgcolor=colors['background'],
                       paper_bgcolor=colors['background'],
                       font={'color': colors['text']},
                       title='Activation pattern: %s' % name,
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
    
    if hoverData is None:
        x, y = 40, 40
    else:
        x = hoverData['points'][0]['x']
        y = hoverData['points'][0]['y']
    
    img = index_by_slice(direction, sslice, func)
    data = go.Scatter(x=np.arange(func.shape[-1]), y=img[x, y, :].ravel())
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
                       yaxis=dict(autorange=False,
                                  showgrid=True,
                                  zeroline=True,
                                  showline=True,
                                  autotick=True,
                                  #ticks='',
                                  showticklabels=True,
                                  title='Activation (contrast estimate)',
                                  range=[-4, 4]))

    return {'data': [data], 'layout': layout}

external_css = [#"https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://codepen.io/lukassnoek/pen/Kvzmzv.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

#app.css.append_css({"relative_package_path": "app.css"})

if __name__ == '__main__':
    app.run_server()
