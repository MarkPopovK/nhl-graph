import json
import requests
import dash
import dash_core_components as dcc
import dash_html_components as html


def server_setup(results):
    app = dash.Dash(__name__)

    app.layout = html.Div(children=[
        html.H1(children='NHL 2018/2019 cumulative points stats'),

        html.Div(children='''
            
        '''),

        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    *results
                ],
                'layout': {
                    'title': 'NHL Data Visualization',
                    'xaxis': {
                        'title': 'Games Played',
                    },
                    'yaxis': {
                        'title': 'Points',
                    },
                    'height': 800,
                    'width': 1000,
                }
            },

        )
    ])

    app.run_server(debug=True)


def main():
    # setup the time span
    start_date = '2018-01-01'
    end_date = '2019-01-01'
    nhl_url = f'https://statsapi.web.nhl.com/api/v1/schedule?startDate={start_date}&endDate={end_date}'

    s = requests.Session()
    games = []

    # download the games
    raw_data = s.get(nhl_url).text
    dates = json.loads(raw_data)['dates']
    for date in dates:
        games.extend(date['games'])

    # filter the games
    games = [game for game in games if all([
        game['season'] == '20182019',
        game['gameType'] == 'R',
    ])]

    # create a data structure of results results = {wsh:{1:1, 2:3}, buf:{1:0, 2:2}}
    results = {}
    for game in games:
        for team in game['teams']:
            name = game['teams'][team]['team']['name']
            record = game['teams'][team]['leagueRecord']
            points = int(record['wins']) * 2 + int(record['ot'])
            games = int(record['wins']) + int(record['losses']) + int(record['ot'])
            results[name] = results.get(name, {})  # creating empty dict for storing results if doesn't exist yet
            results[name][games] = points

    # reformat the data structure for plotly into teams = [{'x':[1,2], 'y':[1,3], 'name':'wsh'}, ]
    teams = []

    points_matrix = {}
    for result in results:
        stats = results[result]
        for game_n in stats:
            points_matrix[game_n] = points_matrix.get(game_n, [])
            points_matrix[game_n].append(stats[game_n])
            points_matrix[game_n] = sorted(points_matrix[game_n])
    print(len(points_matrix))

    for result in results:

        game_ns = list(results[result].keys())
        points = list(results[result].values())
        place = [-(sorted(points_matrix[i]+[point], reverse=True).index(point)+1) for i, point in enumerate(points,1)]

        #points = [point-i for i, point in enumerate(points)]

        teams.append({
            'x': game_ns,
            'y': points,
            'name': result,
            'visible': 'legendonly',
        })

    server_setup(teams)


if __name__ == '__main__':
    main()
