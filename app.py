import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import dill


########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title='nextread'

#### pictures from https://www.emojipng.com/ #####

########### Read in the dataset and functions ######
good_books=pd.read_pickle('resources/good_books.pkl')
cosine_sim_reads=pd.read_pickle('resources/cosine_sim_reads.pkl')

books_genre=[]
for i in good_books['genres'].drop_duplicates():
    books_genre.append(i.split("|"))

books_genre = [item for elem in books_genre for item in elem]
book_genre_list = list(set(books_genre))

# read in the recommendation functions
file=open(f'resources/next_read.pkl', 'rb')
next_read=dill.load(file)
file.close()
        
########### Set up the layout

app.layout = html.Div(children=[
    html.Div(children=[
        html.Img(src=app.get_asset_url('books.jpeg'), style={'width':'8%', 'height':'8%','display':'inline'}),
        html.H2('Next Book Recommender', style={'margin-left':'25%','display':'inline'})
    ], style={'verticalAlign': 'top'}),
    html.Br(),
    html.Br(),
    dcc.Tabs(id="BookTabs", value='ByBookTitle', children=[
    dcc.Tab(label='By Book Title', value='ByBookTitle', children=[
     html.Div([
        html.Div([
            html.Div([], className='one column'),
            html.Div([
                html.H6('Last Book Read:'),
                dcc.Dropdown(
                    id='title',
                    options=[{"label": i, "value": i} for i in sorted(list(good_books['book_title']))],
                    value=[] 
                ),
                html.Br(),
            ], className='four columns'),
            html.Div([], className='one column'),
            html.Br(),
            ], className='twenty columns')])
    ]),
    dcc.Tab(label='By Genre', value='ByGenre', children=[
     html.Div([
        html.Div([
            html.Div([], className='one column'),
            html.Div([
                html.H6('Genre:'),
                dcc.Dropdown(
                    id='genre',
                    options=[{"label": i, "value": i} for i in sorted(book_genre_list)],
                    value=[],
                    multi=True
                ),
                html.Br(),
            ], className='four columns'),
            html.Div([], className='one column'),
            html.Br(),
            ], className='twenty columns')])
    ]),
    ]),
    html.Div(children=[
     dcc.Loading(children=[
         html.P(id='recommendation', style={'textAlign': 'center','marginLeft':'50'})], id='spinner', type='circle'),
     html.Br(),
     html.Br(),
     html.Footer(children=[
     html.A('Code on Github', href='https://git.generalassemb.ly/mchittal/med-capstone-project'),
     html.Br(),
     html.A('Data source:', href='https://www.kaggle.com/datasets/meetnaren/goodreads-best-books/download')
     ])
     ], className='eight columns'),
])

######### Define Callbacks
# Message callback
    
@app.callback(
    Output('recommendation','children'),
    [Input('BookTabs', 'value'),
     Input('title', 'value'),
     Input('genre', 'value')])
def display_results(value0,value1="",value2=[]):
    imgs=[]
    
    if value0 == 'ByBookTitle':
        # Get the recommendations from the cosine similar functions for books having similar author/genre to that of the title provided
        read_recommended = next_read('book_title', value1, cosine_sim_reads)
    elif value0 == 'ByGenre':
        # Get the recommendations from the cosine similar functions for books having similar author/genre to the genre selected
        try:
            read_recommended = next_read('genres', value2, cosine_sim_reads)
        except:
            return (html.H6([f"Sorry! Your Next Read could not be determined by these combination of Genres. Please try a different combination."]))
    
    # Display book cover image at the bottom of the table
    for i in list(read_recommended.index):
        imgs.append(html.Img(src=good_books['image_url'].loc[i],style={'width':'6%', 'height':'6%','display':'inline'}))
    col = [{'name': i, 'id': i} for i in read_recommended.columns]
        
    return (html.H6([f"Your Next Read could be One of below:"]),html.Br(),html.Br(),html.Div([dt.DataTable(style_data_conditional=[{'if': {'column_id': 'genres'},'whiteSpace': 'normal','height': 'auto'},{'if': {'column_id': 'image_url'},'display': 'none'}],style_cell={'textAlign': 'left'},style_header={'backgroundColor': '#D3D3D3','fontWeight': 'bold'},id='table', columns=col, data=read_recommended.to_dict("rows"))]),html.Div(imgs))


############ Execute the app
if __name__ == '__main__':
    app.run_server()
