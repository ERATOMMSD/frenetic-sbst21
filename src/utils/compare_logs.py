import json
import sys
import matplotlib.pyplot as plt

sys.path.append('../../simulations')

"""
Small piece of code to compare the results of two simulations.
"""

#same path
log_1 = 'sim_2021-01-05--16-15-24'
log_2 = 'sim_2021-01-05--16-19-47'

#mirrored paths
#log_1 = 'sim_2021-01-06--09-27-10' #right
#log_2 = 'sim_2021-01-06--09-29-16' #left

with open('../../simulations/beamng_executor/{:s}/simulation.full.json'.format(log_2)) as json_file:
    data_2 = json.load(json_file)

with open('../../simulations/beamng_executor/{:s}/simulation.full.json'.format(log_1)) as json_file:
    data_1 = json.load(json_file)

print(data_2['road'])
print(data_1['road'])
print('The roads generated are the same.')

print(list(map(lambda x: x['pos'], data_2['records'])))
print(list(map(lambda x: x['pos'], data_1['records'])))

print('The frequency of metrics is very different in these two executions...')
print('One log has {:d} records, while the other one has {:d} records.'.format(len(data_2['records']), len(data_1['records'])))
print('However, the final position is almost the same: ({:f},{:f}) and ({:f},{:f})'.format(
    data_1['records'][-1]['pos'][0],data_1['records'][-1]['pos'][1],
    data_2['records'][-1]['pos'][0],data_2['records'][-1]['pos'][1]))

plt.plot(list(map(lambda x: x['pos'][0], data_1['records'])), list(map(lambda x: x['pos'][1], data_1['records'])), label="path_1")
plt.plot(list(map(lambda x: x['pos'][0], data_2['records'])), list(map(lambda x: x['pos'][1], data_2['records'])), label="path_2")
plt.plot(list(map(lambda x: x[0], data_1['road']['nodes'])), list(map(lambda x: x[1], data_1['road']['nodes'])), label="road_1")
plt.plot(list(map(lambda x: x[0], data_2['road']['nodes'])), list(map(lambda x: x[1], data_2['road']['nodes'])), label="road_2")


plt.legend()
plt.show()

#plt.plot(list(map(lambda x: x['timer'], data_1['records'])), list(map(lambda x: x['oob_distance'], data_1['records'])), label='oob_distance_1')
#plt.plot(list(map(lambda x: x['timer'], data_2['records'])), list(map(lambda x: x['oob_distance'], data_2['records'])), label='oob_distance_2')
plt.plot(list(map(lambda x: x['timer'], data_1['records'])), list(map(lambda x: x['vel_kmh']/10, data_1['records'])), label='vel_kmh/10_1')
plt.plot(list(map(lambda x: x['timer'], data_2['records'])), list(map(lambda x: x['vel_kmh']/10, data_2['records'])), label='vel_kmh/10_2')

plt.legend()
plt.show()
