import json
import sys
import matplotlib.pyplot as plt
import pandas as pd
sys.path.append('../../simulations')

"""
Small piece of code to plot the trajectories of simulations that failed in an experiment.
"""

experiment_name = '20210115-184342'

df = pd.read_csv('../../experiments/{:s}-results.csv'.format(experiment_name))

for index, row in df[df['outcome'] == 'FAIL'].iterrows():
    sim_name = row['description'].split('/')[1]
    print(sim_name, 'Generation method:', row['method'], ', Metric:',  row['metric'], ', Min oob distance:',row['min_oob'])
    with open('../../simulations/beamng_executor/{:s}/simulation.full.json'.format(sim_name)) as json_file:
        data_1 = json.load(json_file)

    print('ROAD:', data_1['road'])
    print('PATH:', list(map(lambda x: x['pos'], data_1['records'])))


    plt.plot(list(map(lambda x: x['pos'][0], data_1['records'])), list(map(lambda x: x['pos'][1], data_1['records'])), label="path_1")
    plt.plot(list(map(lambda x: x[0], data_1['road']['nodes'])), list(map(lambda x: x[1], data_1['road']['nodes'])), label="road_1")

    plt.legend()
    plt.show()

    plt.plot(list(map(lambda x: x['timer'], data_1['records'])), list(map(lambda x: x['oob_distance'], data_1['records'])), label='oob_distance_1')
    plt.plot(list(map(lambda x: x['timer'], data_1['records'])), list(map(lambda x: x['vel_kmh']/10, data_1['records'])), label='vel_kmh/10_1')
    plt.plot(list(map(lambda x: x['timer'], data_1['records'])), list(map(lambda x: x['max_oob_percentage'], data_1['records'])), label='max_oob_percentage')

    plt.legend()
    plt.show()
