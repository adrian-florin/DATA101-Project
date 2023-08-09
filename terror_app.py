from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

#Import data
df = pd.read_csv('https://media.githubusercontent.com/media/adrian-florin/datasets/main/terrorism_data.csv', encoding="ISO-8859-1", low_memory=False)

df.rename(columns={'gname': 'Terrorist Group', 'attacktype1_txt': 'Attack Type', 'targtype1_txt':'Target Type',
                   'weaptype1_txt': 'Weapon Type', 'nkill': 'Kills', 'nwound': 'Wounded', 'count': 'Attacks',
                   'nperps': 'Perpetrators', 'nperpcap': 'Captured Perpetrators', 'iyear':'Year', 'region_txt': 'Region',
                   'country_txt':'Country'},inplace=True)

df['Perpetrators'] = abs(df['Perpetrators'])
df['Captured Perpetrators'] = abs(df['Captured Perpetrators'])
df['Attacks'] = 1

years_attack = df['Year'].unique()

years_options = {1970: '1970', 1972: '1972', 1975: '1975', 1980: '1980', 1985: '1985', 1990: '1990', 1995: '1995', 2000: '2000', 2005: '2005', 2010: '2010', 2014: '2014', 2017: '2017'}

regions = df['Region'].unique()

#Mapbox Token
px.set_mapbox_access_token(open(".mapbox_token").read())

#Var Assignment
value_one = 'Kills'
value_two = 'Attacks'
grp = 'Terrorist Group'
region = 'Central America and Caribbean'

# options
region_option = df['Region'].unique()
grp_option = ['Terrorist Group', 'Attack Type', 'Target Type', 'Weapon Type']
value_one_option = ['Kills', 'Wounded']
value_two_option = ['Attacks', 'Perpetrators', 'Captured Perpetrators']

#Data Transformation
df_region = df.loc[df['Region'] == region_option[0]].reset_index(drop=True)

# scatter map data
scatter_dict_region = {}
for i in region_option:
    df_selected_region = df[df['Region'] == i].reset_index(drop=True)
    scatter_dict_region = {**scatter_dict_region, i : df_selected_region}

scatter_dict_top_group = {}
for i in scatter_dict_region:
    df_selected_group = scatter_dict_region.get(i)
    df_selected_group = df_selected_group.groupby(['Region', 'Terrorist Group', ]).size().reset_index(name='attack_count').sort_values(by=['Region', 'attack_count'], ascending=[True, False]).head(5)
    name_df = i + " Top 10"
    scatter_dict_top_group = {**scatter_dict_top_group, name_df : df_selected_group}

top_10_groups_list = []
for i in scatter_dict_top_group: 
    selected_df = scatter_dict_top_group.get(i)
    top_10_groups_list.append(selected_df)

top_10_groups_per_region = pd.concat(top_10_groups_list)
dropped = ['attack_count', 'Region']
top_10_groups_per_region = top_10_groups_per_region.drop(dropped, axis=1).drop_duplicates().reset_index(drop=True)

top_10_groups_per_region_list = top_10_groups_per_region['Terrorist Group'].tolist()
top_10_groups_all_regions = df[df['Terrorist Group'].isin(top_10_groups_per_region_list)]
top_10_groups_all_regions = top_10_groups_all_regions[top_10_groups_all_regions['Year'] == 1970]

# title font size
title_font_size = 12

# Horizontal Bar Chart Data
df_hor_bar = df_region.groupby(['Country'])[[value_one, value_two]].sum().reset_index()
df_hor_bar = df_hor_bar.sort_values(by=value_one, ascending=True).tail(5)

# Pie Chart Data
df_pie = pd.DataFrame(df_region.groupby(grp)[value_one].sum()).reset_index()
df_pie = df_pie.sort_values(by=value_one, ascending=False).head(5)

# Line Chart Data
df_time = pd.DataFrame(df_region.groupby([grp, 'Year'], as_index=False)[value_one].sum())
df_time_sorted = df_time.sort_values(by=value_one, ascending=False)
top_five_kills = df_time_sorted[grp].unique()[:5].tolist()
df_time = df_time.loc[(df_time[grp] == top_five_kills[0]) | 
                      (df_time[grp] == top_five_kills[1]) | 
                      (df_time[grp] == top_five_kills[2]) | 
                      (df_time[grp] == top_five_kills[3]) | 
                      (df_time[grp] == top_five_kills[4])]

# Stacked Bar Chart Data
df_stacked = pd.DataFrame(df_region.groupby(['Country', grp])[value_one].sum())
df_stacked = df_stacked.sort_values(by=[value_one])
df_stacked = df_stacked.reset_index()

top_group = df_pie[grp].unique().tolist()
top_group.append('Country')
df_stacked_pivot = pd.pivot_table(data=df_stacked, 
                                  index='Country', 
                                  columns=grp, 
                                  values=value_one)
df_stacked_pivot['total'] = df_stacked_pivot.sum(axis=1)
df_stacked_pivot = df_stacked_pivot.sort_values(by=['total'], ascending=False).head(5)
df_stacked_pivot = df_stacked_pivot.reset_index()
df_stacked_pivot = df_stacked_pivot[top_group]

#Plotly Express Figures

## big map
fig_map = px.scatter_mapbox(top_10_groups_all_regions,
                        lat='latitude',
                        lon='longitude',
                        hover_name="city",
                        color=grp,
                        zoom=1,
                        )
fig_map.update_layout(showlegend=True, 
                      height=500, 
                      margin={"r":15,"t":15,"l":15,"b":15},legend=dict(
                        yanchor="top",
                        y=0.99,xanchor="left",
                        x=0.01  
                        ),
                        legend_bgcolor='rgba(0, 0, 0, 0)',
                        title = dict(text = f"Terrorist Activities in the World", automargin=True, yref='paper')
                    )

## small map
fig_map_small = px.scatter_mapbox(top_10_groups_all_regions,
                        lat='latitude',
                        lon='longitude',
                        hover_name="city",
                        color=grp,
                        zoom=2,
                        color_discrete_sequence=px.colors.qualitative.T10)
fig_map_small.update_layout(height=400, 
                            width=400, 
                            margin={"r":0,"t":0,"l":0,"b":0}, 
                            showlegend=False, 
                            title = dict(text=f"Terrorist Activities in the {region}", 
                                         automargin=True, 
                                         font=dict(size=title_font_size), 
                                         yanchor="top",
                                         y=0.99,
                                         xanchor="left",
                                         x=0.01))


## horizontal bar chart
fig_bar = px.bar(df_hor_bar, x=[value_one, value_two], y='Country', orientation='h', barmode='group', color_discrete_sequence=px.colors.qualitative.Safe)
fig_bar.update_layout(
    width=800,
    height=400,
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=0
    ),
    legend=dict(
        yanchor="bottom",
        y=0.01,
        xanchor="right",
        x=0.99,
        font=dict(size=7)
    ),
    font=dict(
            size=9,
    ),
    legend_title_text="Count",
    xaxis_title="Count",
    title = dict(text=f"{value_one} and {value_two} in {region}", 
                 automargin=True, 
                 font=dict(size=title_font_size), 
                 yanchor="top",
                 y=0.99,
                 xanchor="left",
                 x=0.01)
)

## pie chart
fig_pie = px.pie(df_pie, values=value_one, names=grp, color_discrete_sequence=px.colors.qualitative.Prism)
fig_pie.update_layout(showlegend=False,
    width=400,
    height=400,
    margin=dict(l=0,
                r=0,
                b=0,
                t=0,
                pad=0
    ),
    legend=dict(
        yanchor="bottom",
        y=0.01,
        xanchor="right",
        x=0.99
    ),
    font=dict(
            size=8,
    ),
    title = dict(text = f"Percentage of {value_one} by {grp}", automargin=True, font=dict(size=title_font_size), yanchor="top",
                                         y=0.99,
                                         xanchor="left",
                                         x=0.01)
)

## line chart
fig_line = px.area(df_time, 
                   x='Year', 
                   y=value_one, 
                   color=grp, 
                   color_discrete_sequence=px.colors.qualitative.Prism, 
                   )
fig_line.update_layout(
    width=400,
    height=400,
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=0
    ),
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        font=dict(size=7),
        itemsizing='constant'
    ),
    font=dict(
            size=9,
    ),
    legend_bgcolor='rgba(0, 0, 0, 0)', 
    title = dict(text = f"Timeline of {value_one} in {region}", automargin=True, font=dict(size=title_font_size), yanchor="top",
                                       y=0.99,
                                       xanchor="left",
                                       x=0.01)
)

## stacked bar chart
fig_stacked = px.bar(df_stacked_pivot.reset_index(), x='Country', y=df_stacked_pivot.columns, color_discrete_sequence=px.colors.qualitative.Prism)
fig_stacked.update_layout(
    width=400,
    height=400,
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=0
    ),
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99,
        font=dict(size=8),
        itemsizing='constant'
    ),
    font=dict(
            size=9,
    ),
    legend_bgcolor='rgba(0, 0, 0, 0)',
    legend_title_text=grp,
    yaxis_title=value_one, 
    title = dict(text = f"Number of {value_one} based on {grp}", automargin=True, font=dict(size=title_font_size), yanchor="top",
                                     y=0.99,
                                     xanchor="left",
                                     x=0.01))


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
    brand="Global Terrorism",
    brand_href="#",
    color="dark",
    dark=True,
)

region_options = []
for i in regions:
    region_options.append({
        'label': i, 
        'value': i
    })

# App layout
app.layout = html.Div(children=[
    navbar,
    dbc.Container([
        dbc.Row(
            children=[
                dcc.Markdown('''
                    ### Worldwide Terrorist Attacks
                    Use the slider to view the cumulative amount of attacks based on the selected year
                ''')
            ], 
            style={'textAlign': 'left', 'color': 'black', 'padding-top' : '10px', 'padding-left' : '20px'}, 
        ),
         dbc.Row(children=[
            dcc.Slider(id="birth-year-slider",
                        min=years_attack.min(),
                        max=years_attack.max(),
                        marks=years_options,
                        step=1)
        ], className="mt-3"),
        # big map
        dbc.Row(children=[
            dbc.Col(children=[
                dcc.Graph(id="scatter-map", figure=fig_map)
                ]),
            ], style={'padding' : '20px'}),
        html.Hr(),
        # dropdown label
        dbc.Row(
            children=[
                dcc.Markdown('''
                    ### Select Filtering
                    Select the type of filters to be applied on the graphs within the dashboard using the
                    dropdown menus below for each values, category, and region.
                ''')
            ], 
            style={'textAlign': 'left', 'color': 'black', 'padding-bottom' : '2px', 'padding-left' : '20px'}, 
        ),
        # droprows
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(id="value-one", options=value_one_option, value=None, placeholder="Victims")
            ]),
            dbc.Col([
                dcc.Dropdown(id="value-two", options=value_two_option, value=None, placeholder="Terrorists")
            ]),
            dbc.Col([
                dcc.Dropdown(id="grouping-filter", options=grp_option, value=None, placeholder="Group Type")
            ]),
            dbc.Col([
                dcc.Dropdown(id="region-dropdown", options=region_options, value=None, placeholder="Region")
            ])
        ], style={'padding-bottom' : '20px'}),
        html.Hr(),
        # row 1 label
        dbc.Row(
            children=[
                dcc.Markdown('''
                    ### Region based Visualizations
                    The map and grouped bar chart shows the appropriate visualization based on the selected region and
                    values that were selected
                ''')
            ], 
            style={'textAlign': 'left', 'color': 'black', 'padding-left' : '20px'}, 
        ),
        # small scatter map, bar chart
        dbc.Row(children=[
             dbc.Col(children=[
                dcc.Graph(id="scatter-map-small", figure=fig_map_small)
            ], width=4, className="mt-3"),
            dbc.Col(children=[
                dcc.Graph(id="bar-chart", figure=fig_bar)
            ], width=8, className="mt-3"),
        ]),
        html.Hr(),
        # row 2 label
        dbc.Row(
            children=[
                dcc.Markdown('''
                    ### Region and Category based Visualizations
                    The charts show the percentage of the selected values within the region based on the selected grouping type
                ''')
            ], 
            style={'textAlign': 'left', 'color': 'black', 'padding-left' : '20px'}, 
        ),
        # line chart and stacked bar chart, and pie chart
        dbc.Row(children=[
            dbc.Col(children=[
                dcc.Graph(id="pie-chart", figure=fig_pie)
            ], width=4, className="mt-3"),
            dbc.Col(children=[
                dcc.Graph(id="line-chart", figure=fig_line)
            ], width=4, className="mt-3"),
            dbc.Col(children=[
                dcc.Graph(id="stacked-chart", figure=fig_stacked)
            ], width=4, className="mt-3"),
        ])
    ])
])    

# big map callback
@callback(
    Output('scatter-map', 'figure'),
    Input('birth-year-slider', 'value')
)

def update_attack_map(selected_year):

    # update data
    scatter_dict_region = {}
    for i in region_option:
        df_selected_region = df[df['Region'] == i].reset_index(drop=True)
        scatter_dict_region = {**scatter_dict_region, i : df_selected_region}

    scatter_dict_top_group = {}
    for i in scatter_dict_region:
        df_selected_group = scatter_dict_region.get(i)
        df_selected_group = df_selected_group.groupby(['Region', 'Terrorist Group', ]).size().reset_index(name='attack_count').sort_values(by=['Region', 'attack_count'], ascending=[True, False]).head(5)
        name_df = i + " Top 10"
        scatter_dict_top_group = {**scatter_dict_top_group, name_df : df_selected_group}

    top_10_groups_list = []
    for i in scatter_dict_top_group:
        selected_df = scatter_dict_top_group.get(i)
        top_10_groups_list.append(selected_df)

    top_10_groups_per_region = pd.concat(top_10_groups_list)
    dropped = ['attack_count', 'Region']
    top_10_groups_per_region = top_10_groups_per_region.drop(dropped, axis=1).drop_duplicates().reset_index(drop=True)

    top_10_groups_per_region_list = top_10_groups_per_region['Terrorist Group'].tolist()
    top_10_groups_all_regions = df[df['Terrorist Group'].isin(top_10_groups_per_region_list)]
        
    if selected_year is None:
        top_10_groups_all_regions = top_10_groups_all_regions[top_10_groups_all_regions['Year'] == 1970]
        big_map_title = 1970

    else:
        top_10_groups_all_regions = top_10_groups_all_regions[top_10_groups_all_regions['Year'] == selected_year]
        big_map_title = selected_year

    # update big map plot
    fig_map = px.scatter_mapbox(top_10_groups_all_regions,
                        lat='latitude',
                        lon='longitude',
                        hover_name="city",
                        color=grp,
                        zoom=1,
                        )
    fig_map.update_layout(showlegend=True, 
                          height=500, 
                          margin={"r":15,"t":15,"l":15,"b":15},
                          legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01), 
                          legend_bgcolor='rgba(0, 0, 0, 0)', 
                          title = dict(text = f"Terrorist Activities in the World during {big_map_title}", automargin=True, yref='paper')
                          )

    return fig_map

# small map callback
@callback(
    Output('scatter-map-small', 'figure'),
    Input('region-dropdown', 'value')
)

def display_small_map(selected_region):

    scatter_dict_region = {}
    for i in region_option:
        df_selected_region = df[df['Region'] == i].reset_index(drop=True)
        scatter_dict_region = {**scatter_dict_region, i : df_selected_region}

    scatter_dict_top_group = {}
    for i in scatter_dict_region:
        df_selected_group = scatter_dict_region.get(i)
        df_selected_group = df_selected_group.groupby(['Region', 'Terrorist Group', ]).size().reset_index(name='attack_count').sort_values(by=['Region', 'attack_count'], ascending=[True, False]).head(5)
        name_df = i + " Top 10"
        scatter_dict_top_group = {**scatter_dict_top_group, name_df : df_selected_group}

    top_10_groups_list = []
    for i in scatter_dict_top_group:
        selected_df = scatter_dict_top_group.get(i)
        top_10_groups_list.append(selected_df)

    top_10_groups_per_region = pd.concat(top_10_groups_list)
    dropped = ['attack_count', 'Region']
    top_10_groups_per_region = top_10_groups_per_region.drop(dropped, axis=1).drop_duplicates().reset_index(drop=True)

    top_10_groups_per_region_list = top_10_groups_per_region['Terrorist Group'].tolist()
    top_10_groups_all_regions = df[df['Terrorist Group'].isin(top_10_groups_per_region_list)]

    if selected_region is None:
        region_to_map = top_10_groups_all_regions[top_10_groups_all_regions['Region'] == 'North America']
        plot_label = "North America"

    else:
        region_to_map = top_10_groups_all_regions[top_10_groups_all_regions['Region'] == selected_region]
        plot_label = selected_region
    # update data
    

    # update small map plot
    fig_map_small = px.scatter_mapbox(region_to_map,
                        lat='latitude',
                        lon='longitude',
                        hover_name="city",
                        color=grp,
                        zoom=2,
                        color_discrete_sequence=px.colors.qualitative.T10)
    fig_map_small.update_layout(height=400, 
                                width=400, 
                                margin={"r":0,"t":0,"l":0,"b":0}, 
                                showlegend=False, 
                                title = dict(text = f"Terrorist Activities in the {plot_label}", 
                                             automargin=True, 
                                             font=dict(size=title_font_size), yanchor="top",
                                             y=0.99,
                                             xanchor="left",
                                             x=0.01))

    return fig_map_small

# stacked bar callback
@callback(
    Output('stacked-chart', 'figure'),
    Input('value-one', 'value'),
    Input('grouping-filter', 'value'),
    Input('region-dropdown', 'value')
)

def update_stacked(value_one, selected_group, selected_region):

    df_region = df.loc[df['Region'] == selected_region].reset_index(drop=True)

    # updated order data
    df_top = pd.DataFrame(df_region.groupby(selected_group)[value_one].sum()).reset_index()
    df_top = df_top.sort_values(by=value_one, ascending=False).head()

    # updated stacked data
    df_stacked = pd.DataFrame(df_region.groupby(['Country', selected_group])[value_one].sum())
    df_stacked = df_stacked.sort_values(by=[value_one])
    df_stacked = df_stacked.reset_index()

    top_group = df_top[selected_group].unique().tolist()
    top_group.append('Country')

    df_stacked_pivot = pd.pivot_table(data=df_stacked,
                                      index='Country',
                                      columns=selected_group,
                                      values=value_one)
    df_stacked_pivot['total'] = df_stacked_pivot.sum(axis=1)
    df_stacked_pivot = df_stacked_pivot.sort_values(by=['total'], ascending=False).head(5)
    df_stacked_pivot = df_stacked_pivot.reset_index()
    df_stacked_pivot = df_stacked_pivot[top_group]

    # updated stacked visualization
    fig_stacked = px.bar(df_stacked_pivot.reset_index(), x='Country', y=df_stacked_pivot.columns, color_discrete_sequence=px.colors.qualitative.Prism)
    fig_stacked.update_layout(width=400, 
                              height=400, 
                              margin=dict(l=0, r=0, b=0, t=0, pad=0), 
                              legend=dict(
                                        yanchor="top",
                                        y=0.99,
                                        xanchor="right", 
                                        x=0.99, 
                                        font=dict(size=8), 
                                        itemsizing='constant'), 
                              font=dict(size=9),
                              legend_bgcolor='rgba(0.5, 0.5, 0.5, 0.5)',
                              legend_title_text=selected_group,
                              yaxis_title=value_one, 
                              title = dict(text = f"Number of {value_one} based on {selected_group}", automargin=True, font=dict(size=title_font_size), yanchor="top",
                                           y=0.99,
                                           xanchor="left",
                                           x=0.01)),
                              
    
    return fig_stacked

# line chart callback
@callback(
    Output("line-chart", 'figure'),
    Input("value-one", 'value'),
    Input("grouping-filter", 'value'),
    Input("region-dropdown", 'value')
)

def update_line_chart(value_one, selected_group, selected_region):

    df_region = df.loc[df['Region'] == selected_region]

    # updated data
    df_pie = pd.DataFrame(df_region.groupby(selected_group)[value_one].sum()).reset_index()
    df_pie = df_pie.sort_values(by=value_one, ascending=False).head(9)

    df_time = pd.DataFrame(df_region.groupby([selected_group, 'Year'], as_index=False)[value_one].sum())
    df_time_sorted = df_time.sort_values(by=value_one, ascending=False)
    top_five_kills = df_time_sorted[selected_group].unique()[:5].tolist()
    df_time = df_time.loc[(df_time[selected_group] == top_five_kills[0]) | 
                          (df_time[selected_group] == top_five_kills[1]) | 
                          (df_time[selected_group] == top_five_kills[2]) | 
                          (df_time[selected_group] == top_five_kills[3]) | 
                          (df_time[selected_group] == top_five_kills[4])]
    
    # updated chart
    fig_line = px.area(df_time, x='Year', y=value_one, color=selected_group, color_discrete_sequence=px.colors.qualitative.Prism)
    fig_line.update_layout(
        width=400,
        height=400,
        margin=dict(l=0, r=0, b=0, t=0, pad=0),
        legend=dict(yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01, 
                    font=dict(size=7),
                    itemsizing='constant'),
        font=dict(size=9),
        legend_bgcolor='rgba(0, 0, 0, 0)', 
        title = dict(text = f"Timeline {value_one} in {selected_region}", automargin=True, font=dict(size=title_font_size), yanchor="top",
                                        y=0.99,
                                        xanchor="left",
                                        x=0.01)
        )
        

    return fig_line

# grouped bar callback
@callback(
    Output("bar-chart", 'figure'),
    Input("value-one", 'value'),
    Input("value-two", 'value'),
    Input("region-dropdown", 'value')
)

def update_grouped_bar(value_one, value_two, selected_region):
    df_region = df.loc[df['Region'] == selected_region]

    # update data
    df_hor_bar = df_region.groupby(['Country'])[[value_one, value_two]].sum().reset_index()
    df_hor_bar = df_hor_bar.sort_values(by=value_one, ascending=True).tail(5)
    
    # update visualization
    fig_bar = px.bar(df_hor_bar, 
                     x=[value_one, value_two], 
                     y='Country', 
                     orientation='h', 
                     barmode='group', 
                     color_discrete_sequence=px.colors.qualitative.Safe)
    fig_bar.update_layout(width=800,
                          height=400,
                          margin=dict(l=0, r=0, b=0, t=0, pad=0),
                          legend=dict(yanchor="bottom",
                                      y=0.01,
                                      xanchor="right",
                                      x=0.99, font=dict(size=7)),
                          font=dict(size=9),
                          legend_title_text="Count",
                          xaxis_title="Count", 
                          title = dict(text = f"{value_one} and {value_two} in {selected_region}", 
                                       automargin=True, 
                                       font=dict(size=title_font_size), 
                                       yanchor="top",
                                       y=0.99,
                                       xanchor="left",
                                       x=0.01)
                        )
    return fig_bar

# pie chart callback
@ callback(
    Output("pie-chart", 'figure'),
    Input("value-one", 'value'),
    Input("grouping-filter", 'value'),
    Input("region-dropdown", 'value')
)

def update_pie_chart(value_one_select, selected_group, selected_region):

    df_region = df.loc[df['Region'] == selected_region]

    #updated data
    df_pie = pd.DataFrame(df_region.groupby(selected_group)[value_one_select].sum()).reset_index()
    df_pie = df_pie.sort_values(by=value_one_select, ascending=False).head(5)

    # update visualization
    fig_pie = px.pie(df_pie, values=value_one_select, names=selected_group, color_discrete_sequence=px.colors.qualitative.Prism)
    fig_pie.update_layout(showlegend=False,
        width=400,
        height=400,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0
        ),
        legend=dict(
            yanchor="bottom",
            y=0.01,
            xanchor="right",
            x=0.99,
        ),
        font=dict(
                size=8,
        ), 
        title = dict(text = f"Percentage of {value_one} by {grp}", 
                     automargin=True, 
                     font=dict(size=title_font_size), 
                     yanchor="top",
                     y=0.99,
                     xanchor="left",
                     x=0.01)
    )
    
    return fig_pie


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)