python competition.py --time-budget 36000 --module-name src.generators.frenetic --class-name FreneticGenerator --executor beamng --beamng-home D:\Programs\BeamNG.research.v1.7.0.1 --beamng-user C:\Users\mmsd-admin\Documents\BeamNG.research --log-to ./logs/frenetic.log

timeout /t 5

python competition.py --time-budget 36000 --module-name src.generators.nsgaii_frenet --class-name NSGAIIFrenetGenerator --executor beamng --beamng-home D:\Programs\BeamNG.research.v1.7.0.1 --beamng-user C:\Users\mmsd-admin\Documents\BeamNG.research --log-to ./logs/nsgaii_frenet.log

timeout /t 5

python competition.py --time-budget 36000 --module-name src.generators.random_frenet_generator --class-name CustomFrenetGenerator --executor beamng --beamng-home D:\Programs\BeamNG.research.v1.7.0.1 --beamng-user C:\Users\mmsd-admin\Documents\BeamNG.research --log-to ./logs/custom_random_frenet.log

timeout /t 5

python competition.py --time-budget 36000 --module-name src.generators.local_search_frenet --class-name LocalSearchFrenetGenerator --executor beamng --beamng-home D:\Programs\BeamNG.research.v1.7.0.1 --beamng-user C:\Users\mmsd-admin\Documents\BeamNG.research --log-to ./logs/local_search.log

timeout /t 5

python competition.py --time-budget 36000 --module-name src.generators.evolution_frenet --class-name EvolutionaryFrenetGenerator --executor beamng --beamng-home D:\Programs\BeamNG.research.v1.7.0.1 --beamng-user C:\Users\mmsd-admin\Documents\BeamNG.research --log-to ./logs/evolution_frenet.log

timeout /t 5

python competition.py --time-budget 36000 --module-name src.generators.random_frenet_generator --class-name RandomFrenetGenerator --executor beamng --beamng-home D:\Programs\BeamNG.research.v1.7.0.1 --beamng-user C:\Users\mmsd-admin\Documents\BeamNG.research --log-to ./logs/random_frenet.log

timeout /t 5

python competition.py --time-budget 36000 --module-name src.generators.simulated_annealing_frenet --class-name SimulatedAnnealingFrenetGenerator --executor beamng --beamng-home D:\Programs\BeamNG.research.v1.7.0.1 --beamng-user C:\Users\mmsd-admin\Documents\BeamNG.research --log-to ./logs/simulated_annealing_frenet.log

PAUSE