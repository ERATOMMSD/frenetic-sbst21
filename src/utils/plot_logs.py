import json
import sys
import matplotlib.pyplot as plt
import pandas as pd
import ast
sys.path.append('../../simulations')

"""
Small piece of code to plot the trajectories of simulations that failed in an experiment.
"""

experiment_name = '20210128-001820-RandomFrenetGenerator-results'

df = pd.read_csv('../../experiments/{:s}.csv'.format(experiment_name))

print('Generated test:', len(df))
print('Invalid tests:', len(df[df['outcome'] == 'INVALID']))
print('Valid tests:', len(df[df['outcome'] != 'INVALID']))
print('Failed tests:', len(df[df['outcome'] == 'FAIL']))
print('Passed tests:', len(df[df['outcome'] == 'PASS']))

failed_stats = {}
generation_stats = {}

for index, row in df[df['outcome'] == 'FAIL'].iterrows():
    sim_name = row['description'].split('/')[1]
    print(sim_name, index, 'Generation method:', row['method'],
          'Generation:', row['generation'],
          'Metric:',  row['accum_neg_oob'],
          'Min oob distance:', row['min_oob_distance'])

    method = row['method']
    if method in failed_stats:
        failed_stats[method] += 1
    else:
        failed_stats[method] = 1

    generation = row['generation']
    if generation in generation_stats:
        generation_stats[generation] += 1
    else:
        generation_stats[generation] = 1
    #with open('../../simulations/beamng_executor/{:s}/simulation.full.json'.format(sim_name)) as json_file:
    #    data_1 = json.load(json_file)

    road = ast.literal_eval(row['road'])

    plt.plot(list(map(lambda x: x[0], road)), list(map(lambda x: x[1], road)), label="path", alpha=0.1)

print(generation_stats)
print(failed_stats)

plt.show()

