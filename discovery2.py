import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import spoticomms

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(external_stylesheets=external_stylesheets)

#Page Attributes
colors = {
    'background': '#A791FF',
    'text': '#0B782B',
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div(children='  ', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    html.Div(children='  ', style={
        'textAlign': 'center',
        'color': colors['text'],
        'padding': 20
    }),
    html.H1(
        children='Welcome to Discovery² !',
        style={
            'textAlign': 'center',
            'color': colors['text'],

        }
    ),
    html.H5(
        children='A simple web-app to help you create focused music discovery playlists, based on what you like :)',
        style={
            'textAlign': 'center',
            'color': colors['text'],

        }
    ),
    html.Div(children='  ', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    html.Div(children='  ', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    html.H5(
        children="Just select the attributes you want for your playlist, then click the button at the bottom",
        style={
            'textAlign': 'center',
            'color': colors['text'],

        }
    ),
    html.Div(children='  ', style={
        'textAlign': 'center',
        'color': colors['text'],
        'padding': 20
    }),

    html.Label('Happy or Sad?', style={'textAlign': 'center',
                                       'fontSize': 20,
                                       'color': colors['text']}),
    html.Div(
        dcc.RadioItems(
            id = 'input-1-state',
            options=[
                {'label': 'Happy', 'value': 'happy'},
                {'label': 'Bit of Both', 'value': 'mixed'},
                {'label': 'Sad', 'value': 'sad'}
            ],
            value='mixed', labelStyle={'display': 'inline-block'}
        ), style={'textAlign': 'center',
                  'fontSize': 18,
                  'color': colors['text']}

    ),
    html.Div(children='  ', style={
        'textAlign': 'center',
        'color': colors['text'],
        'padding': 10
    }),
    html.Label('Electronic or Acoustic?',
               style={'textAlign': 'center',
                      'fontSize': 20,
                      'color': colors['text']}),
    html.Div(
        dcc.RadioItems(
            id = 'input-2-state',
            options=[
                {'label': 'Electronic', 'value': 'electronic'},
                {'label': 'Both', 'value': 'both'},
                {'label': 'Acoustic', 'value': 'acoustic'}
            ],
            value='both', labelStyle={'display': 'inline-block'}
        ), style={'textAlign': 'center',
                  'fontSize': 18,
                  'color': colors['text']}

    ),

    html.Div(children='  ', style={
        'textAlign': 'center',
        'color': colors['text'],
        'padding': 10
    }),
    html.Label('Dancey, or Relaxy?',
               style={'textAlign': 'center',
                      'fontSize': 20,
                      'color': colors['text']}),
    html.Div(
        dcc.RadioItems(
            id = 'input-3-state',
            options=[
                {'label': 'Dancey!', 'value': 'dance'},
                {'label': 'Somewhere in between', 'value': 'both'},
                {'label': 'Relaaaxyyy', 'value': 'relax'}
            ],
            value='both', labelStyle={'display': 'inline-block'}
        ), style={'textAlign': 'center',
                  'fontSize': 18,
                  'color': colors['text']}

    ),


    html.Div(children='  ', style={
        'textAlign': 'center',
        'color': colors['text'],
        'padding': 10
    }),
    html.Label('Do you want vocals?',
               style={'textAlign': 'center',
                      'fontSize': 20,
                      'color': colors['text']}),
    html.Div(
        dcc.RadioItems(
            id = 'input-4-state',
            options=[
                {'label': 'Yes, give me ALL THE VOCALS', 'value': 'vox'},
                {'label': "I could take a few vocals", 'value': 'both'},
                {'label': 'Hell no, I hate vocals', 'value': 'no vox'}
            ],
            value='both', labelStyle={'display': 'inline-block'}
        ), style={'textAlign': 'center',
                  'fontSize': 18,
                  'color': colors['text']}

    ),
    html.Div(children='  ', style={
        'textAlign': 'center',
        'color': colors['text'],
        'padding': 30
    }),

    html.Div([
        html.Button('Connect to Spotify and generate custom playlist', id='connect-button-state', n_clicks=0,
                    style={'fontSize': 20})],
        style={
            'textAlign': 'center',
            'fontSize': 18}
    ),
    html.H6(
        children='Follow the promts and your new playlist should automatically appear in your Spotify library',
        style={
            'textAlign': 'center',
            'color': colors['text'],

        }
    ),
    html.H6(
        children='Enjoy!',
        style={
            'textAlign': 'center',
            'color': colors['text'],

        }
    ),
    html.Div(id='output-state'),
    html.Div(children='  ', style={
        'textAlign': 'center',
        'color': colors['text'],
        'padding': 100
    })

])
@app.callback(Output('output-state', 'children'),
              Input('connect-button-state', 'n_clicks'),
              State('input-1-state', 'value'),
              State('input-2-state', 'value'),
              State('input-3-state', 'value'),
              State('input-4-state', 'value'))
def create_playlist(n_clicks, input1, input2, input3, input4):
    if n_clicks > 0:
        inputs = [input1, input2, input3, input4]
        spoticomms.run(inputs)
        return 'Your playlist should now be ready and waiting in your Spotify library!'
    else:
        return 'Click the button above to generate your playlist'



if __name__ == '__main__':
    app.run_server(debug=True)