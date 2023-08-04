from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# importing the data
df = pd.read_csv('https://media.githubusercontent.com/media/adrian-florin/datasets/main/terrorism_data.csv', encoding = "ISO-8859-1")
df['count'] = 1
years_attack = df['iyear'].unique()
years_options = {1970: '1970', 1972: '1972', 1975: '1975', 1980: '1980', 1985: '1985', 1990: '1990', 1995: '1995', 2000: '2000', 2005: '2005', 2010: '2010', 2014: '2014', 2017: '2017'}


# dropdown options
value_one = ['nkill', 'nwound']
value_two = ['count']
grp_option = ['gname', 'attacktype1_txt', 'targtype1_txt', 'weaptype1_txt']
region_option = df['region_txt'].unique()

# data transformation for visualizations
df_region = df.loc[df['region_txt'] == region_option[0]].reset_index(drop=True)

df_hor_bar = df_region.groupby(['country_txt'])[[value_one[0], value_two[0]]].sum().reset_index()
df_hor_bar = df_hor_bar.sort_values(by=value_one[0], ascending=True).tail(5)

df_pie = pd.DataFrame(df_region.groupby(grp_option[0])[value_one[0]].sum()).reset_index()
df_pie = df_pie.sort_values(by=value_one[0], ascending=True).head(9)

df_time = pd.DataFrame(df_region.groupby([grp_option[0], 'iyear'], as_index=False)[value_one[0]].sum())
df_time_sorted = df_time.sort_values(by=value_one[0], ascending=False)
top_five_kills = df_time_sorted[grp_option[0]].unique()[:5].tolist()
df_time = df_time.loc[(df_time[grp_option[0]] == top_five_kills[0]) | 
                      (df_time[grp_option[0]] == top_five_kills[1]) | 
                      (df_time[grp_option[0]] == top_five_kills[2]) | 
                      (df_time[grp_option[0]] == top_five_kills[3]) | 
                      (df_time[grp_option[0]] == top_five_kills[4])]

df_stacked = pd.DataFrame(df_region.groupby(['country_txt', grp_option[0]])[value_one[0]].sum())
df_stacked = df_stacked.sort_values(by=[value_one[0]])
df_stacked = df_stacked.reset_index()

top_group = df_pie[grp_option[0]].unique().tolist()
top_group.append('country_txt')
top_group

df_stacked_pivot = pd.pivot_table(data=df_stacked, 
                                  index='country_txt', 
                                  columns=grp_option[0], 
                                  values=value_one[0])
df_stacked_pivot['total'] = df_stacked_pivot.sum(axis=1)
df_stacked_pivot = df_stacked_pivot.sort_values(by=['total'], ascending=False).head(10)
df_stacked_pivot = df_stacked_pivot.reset_index()
df_stacked_pivot = df_stacked_pivot[top_group]

# scatter map data
scatter_dict_region = {}
for i in region_option:
    df_selected_region = df[df['region_txt'] == i].reset_index(drop=True)
    scatter_dict_region = {**scatter_dict_region, i : df_selected_region}

scatter_dict_top_group = {}
for i in scatter_dict_region:
    df_selected_group = scatter_dict_region.get(i)
    df_selected_group = df_selected_group.groupby(['region_txt', 'gname', ]).size().reset_index(name='attack_count').sort_values(by=['region_txt', 'attack_count'], ascending=[True, False]).head(5)
    name_df = i + " Top 10"
    scatter_dict_top_group = {**scatter_dict_top_group, name_df : df_selected_group}

top_10_groups_list = []
for i in scatter_dict_top_group:
    selected_df = scatter_dict_top_group.get(i)
    top_10_groups_list.append(selected_df)

top_10_groups_per_region = pd.concat(top_10_groups_list)
dropped = ['attack_count', 'region_txt']
top_10_groups_per_region = top_10_groups_per_region.drop(dropped, axis=1).drop_duplicates().reset_index(drop=True)

top_10_groups_per_region_list = top_10_groups_per_region['gname'].tolist()
top_10_groups_all_regions = df[df['gname'].isin(top_10_groups_per_region_list)]

# plotly figures

## big map
fig_map = px.scatter_mapbox(top_10_groups_all_regions,
                            lat='latitude',
                            lon='longitude',
                            hover_name="city",
                            color=grp_option[0],
                            zoom=1)
fig_map.update_layout(showlegend=False)

## small map
fig_map_small = px.scatter_mapbox(top_10_groups_all_regions,
                                  lat='latitude',
                                  lon='longitude',
                                  hover_name="city",
                                  color=grp_option[0],
                                  zoom=2)
fig_map_small.update_layout(height=350, 
                            width=450, 
                            margin={"r":0,"t":0,"l":0,"b":0}, 
                            showlegend=False)

## grouped bar
fig_bar = px.bar(df_hor_bar, 
                 x=[value_one[0], value_two[0]], 
                 y='country_txt', 
                 orientation='h', 
                 barmode='group')
fig_bar.update_layout(width=400, 
                      height=350, 
                      margin=dict(l=0, r=0, b=0, t=0, pad=3), 
                      legend=dict(yanchor="bottom", y=0.01, xanchor="right", x=0.99), 
                      font=dict(size=9))

## pie chart
fig_pie = px.pie(df_pie, 
                 values=value_one[0], 
                 names=grp_option[0])
fig_pie.update_layout(showlegend=False, 
                      width=250, 
                      height=250, 
                      margin=dict(l=50, r=0, b=0, t=0, pad=3), 
                      legend=dict(yanchor="bottom", y=0.01, xanchor="right", x=0.99), 
                      font=dict(size=9,))

## line chart
fig_line = px.area(df_time, 
                   x='iyear', 
                   y=value_one[0], 
                   color=grp_option[0])
fig_line.update_layout(width=400, 
                       height=350, 
                       margin=dict(l=0,r=0,b=0,t=0,pad=3),
                       legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01),
                       font=dict(size=9,))

## stacked bar chart
fig_stacked = px.bar(df_stacked_pivot.reset_index(), x='country_txt', y=df_stacked_pivot.columns)
fig_stacked.update_layout(width=400, 
                          height=350, 
                          margin=dict(l=0,r=0,b=0,t=0,pad=3), 
                          legend=dict(yanchor="top",y=0.99,xanchor="right",x=0.99), 
                          labels={
                            "country_txt": "Country",
                            "df_stacked_pivot.columns" : "Group, Attack, Target Type",
                                },
                          title='Killed, Wounded, and Attacked per country according to Terrorist Group, Attack Type, and Target Type', 
                          font=dict(size=9))

# Initialize Dash application
app = Dash(__name__, 
           external_stylesheets=[dbc.themes.BOOTSTRAP])

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Global Terrorism Visualization",
    brand_href="#",
    color="dark",
    dark=True,
)

region_options = []
for i in region_option:
    region_options.append({
        'label': i, 
        'value': i
    })

# App layout
app.layout = html.Div(children=[
    navbar,
    dbc.Container([
        dbc.Row(children=[
            dbc.Col(children=[
                dcc.Graph(id="scatter-map", figure=fig_map)
                ]),
        ]),
        dbc.Row(children=[
            dcc.Slider(id="birth-year-slider", 
                       min=years_attack.min(), 
                       max=years_attack.max(), 
                       marks=years_options, 
                       step=1)
        ]),
        dbc.Row(children=[
            dbc.Col(children=[
                dcc.Graph(id="scatter-map-small", figure=fig_map_small)
            ], width=4),
            dbc.Col(children=[
                dcc.Graph(id="bar-chart", figure=fig_bar)
            ], width=4),
            dbc.Col(children=[
                html.Div(children=[dcc.Dropdown(id="region-dropdown", 
                                                options=region_options, value=None)], 
                                                className='mb-2'),
                dcc.Graph(id="pie-chart", figure=fig_pie)
            ], width=4),
        ]),
        dbc.Row(children=[
            dbc.Col(children=[
                dcc.Graph(id="line-chart", figure=fig_line)
            ], width=4),
            dbc.Col(children=[
                dcc.Dropdown(id="stacked-dropdown", options=grp_option, value=grp_option[0]),
                dcc.Graph(id="stacked-chart", figure=fig_stacked)
            ], width=4),
        ])
    ])
])

#define callbacks

## scatter big map callback
@callback(
    Output('scatter-map', 'figure'),
    Input('birth-year-slider', 'value')
)

def update_attack_map(selected_year):

    scatter_dict_region = {}
    for i in region_option:
        df_selected_region = df[df['region_txt'] == i].reset_index(drop=True)
        scatter_dict_region = {**scatter_dict_region, i : df_selected_region}

    scatter_dict_top_group = {}
    for i in scatter_dict_region:
        df_selected_group = scatter_dict_region.get(i)
        df_selected_group = df_selected_group.groupby(['region_txt', 'gname', ]).size().reset_index(name='attack_count').sort_values(by=['region_txt', 'attack_count'], ascending=[True, False]).head(5)
        name_df = i + " Top 10"
        scatter_dict_top_group = {**scatter_dict_top_group, name_df : df_selected_group}

    top_10_groups_list = []
    for i in scatter_dict_top_group:
        selected_df = scatter_dict_top_group.get(i)
        top_10_groups_list.append(selected_df)

    top_10_groups_per_region = pd.concat(top_10_groups_list)
    dropped = ['attack_count', 'region_txt']
    top_10_groups_per_region = top_10_groups_per_region.drop(dropped, axis=1).drop_duplicates().reset_index(drop=True)

    top_10_groups_per_region_list = top_10_groups_per_region['gname'].tolist()
    top_10_groups_all_regions = df[df['gname'].isin(top_10_groups_per_region_list)]

        
    if selected_year is None:
        top_10_groups_all_regions = top_10_groups_all_regions[top_10_groups_all_regions['iyear'] == 1970]

    else:
        top_10_groups_all_regions = top_10_groups_all_regions[top_10_groups_all_regions['iyear'] == selected_year]

    fig_map = px.scatter_mapbox(top_10_groups_all_regions,
                        lat='latitude',
                        lon='longitude',
                        hover_name="city",
                        color=grp_option[0],
                        zoom=1)
    fig_map.update_layout(showlegend=False)

    return fig_map

# scatter small map callback
@callback(
    Output('scatter-map-small', 'figure'),
    Input('region-dropdown', 'value')
)

def display_small_map(selected_region):
    region_to_map = top_10_groups_all_regions[top_10_groups_all_regions['region_txt'] == selected_region]

    fig_map_small = px.scatter_mapbox(region_to_map,
                        lat='latitude',
                        lon='longitude',
                        hover_name="city",
                        color=grp_option[0],
                        zoom=2)
    fig_map_small.update_layout(height=350, width=450, margin={"r":0,"t":0,"l":0,"b":0}, showlegend=False)

    return fig_map_small

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)