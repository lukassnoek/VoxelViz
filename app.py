import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import nibabel as nib
import numpy as np

app = dash.Dash(csrf_protect=False)
server = app.server
ex_func = nib.load('test_func_flirted.nii.gz').get_data()
bg_mean = ex_func.mean(axis=-1)
tmp_img = nib.load('cope1.nii.gz')

app.layout = html.Div(
    
    children=[

        html.Div(className='ten columns offset-by-one', children=[

            html.H1(children='VoxelViz: An iteractive viewer for BOLD-fMRI data',
                    style={'textAlign': 'center'},
                    id='title'),

            dcc.Markdown(
                """ This tool is developed to interactively show (f)MRI results
                in a browser using the open-source [Plotly Dash](https://plot.ly/products/dash/)
                framework. It is submitted to the TransIP [VPS-challenge](https://tweakers.net/plan/1299/bouw-een-transip-vps-toepassing-en-win-een-asus-laptop-met-htc-vive.html).
                """)
            ]),

        html.Div(className='six columns', children=[

            html.P("Pick whichever contrast you want to look at:"),
            
            dcc.Dropdown(options=[{'label': 'Cope1', 'value': 'cope1.nii.gz'},
                                  {'label': 'Cope2', 'value': 'cope2.nii.gz'}],
                         value='cope1.nii.gz',
                         id='contrast'),

            dcc.Graph(id='brainplot', animate=False),
            

            html.Div(className='row', children=[

                dcc.Markdown(
                    """Pick a threshold (absolute) here ..."""),

                dcc.Slider(id='threshold',
                           min=0,
                           max=300,
                           step=0.5,
                           value=50)
            ]),

            html.Div(className='tow', children=[

                html.P('Pick a direction/view (and use the slider to "scroll"):'),

                dcc.RadioItems(
                    id='direction',
                    options=[
                        {'label': 'X', 'value': 'X'},
                        {'label': 'Y', 'value': 'Y'},
                        {'label': 'Z', 'value': 'Z'}
                    ],
                    labelStyle={'display': 'inline-block'},
                    value='Z'),

                dcc.Slider(
                    min=0,
                    step=1,
                    value=20,
                    id='slice')
                ], style={'margin-top': 50, 'margin-bottom': 5})
            ]),

        html.Div(className='six columns', children=[

            html.Div(className='row', children=[

                dcc.Graph(id='brainplot_time', animate=False)
                ])
            ]),

    ], className = "page"
)


@app.callback(
    Output(component_id='slice', component_property='max'),
    [Input(component_id='direction', component_property='value')])
def update_slice_slider(direction):

    srange = {'X': tmp_img.shape[0],
              'Y': tmp_img.shape[1],
              'Z': tmp_img.shape[2]}

    return srange[direction]

@app.callback(
    Output(component_id='brainplot', component_property='figure'),
    [Input(component_id='threshold', component_property='value'),
     Input(component_id='contrast', component_property='value'),
     Input(component_id='direction', component_property='value'),
     Input(component_id='slice', component_property='value')])
def update_brainplot(threshold, contrast, direction, sslice):
    
    img = nib.load(contrast).get_data()
    if direction == 'X':
        bg = bg_mean[sslice, :, :]
        img = img[sslice, :, :]
    elif direction == 'Y':
        bg = bg_mean[:, sslice, :]
        img = img[:, sslice, :]
    else:
        bg = bg_mean[:, :, sslice]
        img = img[:, :, sslice]

    bg_func = go.Heatmap(z=bg.T, colorscale='Greys', showscale=False, hoverinfo="none", name='background')
    tmp = np.ma.masked_where(np.abs(img) < threshold, img)
    func = go.Heatmap(z=tmp.T, opacity=threshold, name=contrast.split('.')[0])
    layout = go.Layout(autosize=True,
                       margin={'t': 50, 'l': 5, 'r': 5})
    return {'data': [bg_func, func], 'layout': layout}

"""
ToDo: update timeseries plot on hoover
@app.callback(
    Output(component_id='brainplot_time', component_property='figure'),
    [Input(component_id='threshold', component_property='value'),
     Input(component_id='contrast', component_property='value'),
     Input(component_id='direction', component_property='value'),
     Input(component_id='slice', component_property='value')])
def update_brainplot_time(threshold, contrast, direction, sslice):
    
    img = nib.load(contrast).get_data()
    if direction == 'X':
        img = ex_func[sslice, :, :, :]
    elif direction == 'Y':
        img = img[:, sslice, :]
    else:
        img = img[:, :, sslice]

    go.Scatter(x=np.arange(100), y=)
    func = go.Heatmap(z=tmp.T, opacity=threshold, name=contrast.split('.')[0])
    layout = go.Layout(title='Contrast: %s' % contrast.split('.')[0], autosize=True,
                       margin={'t': 50, 'l': 5, 'r': 5})
    return {'data': [bg_func, func], 'layout': layout}
"""

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css"]
    
for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server()
