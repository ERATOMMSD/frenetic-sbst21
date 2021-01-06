# Cyber-Physical Systems Testing Competition (ERATO-fork)

## ERATO-Team SBST 2021 AV Competition

This is a fork of [sbst-tool-competition-av](https://github.com/se2p/tool-competition-av) to develop our algorithms.

The fork was done following this [instructions](https://stackoverflow.com/questions/10065526/github-how-to-make-a-fork-of-public-repository-private). Let's use the branch 'erato-mmsd' for dev and keep the branch 'main' clean to reduce conflicts when pulling updates from the original repository.

To bring changes from the original repository follow this steps:
```
cd sbst-tool-competition-av
git remote add public https://github.com/se2p/tool-competition-av.git
git pull public main # Creates a merge commit
git push origin main
```


## Cyber-Physical Systems Testing Competition ##

Starting this year, the [SBST Workshop](https://sbst21.github.io/) offers a challenge for software testers who want to work with self-driving cars in the context
of the usual [tool competition](https://sbst21.github.io/tools/).

## Goal ##
The competitors should generate virtual roads to test a lane keeping assist system. 

The generated roads are evaluated in a driving simulator. We partnered with BeamNG GmbH which offers a version of their simulators for researchers, named [BeamNG.research](https://beamng.gmbh/research/). This simulator is ideal for researchers due to its state-of-the-art soft-body physics simulation, ease of access to sensory data, and a Python API to control the simulation.

[![Video by BeamNg GmbH](https://github.com/BeamNG/BeamNGpy/raw/master/media/steering.gif)](https://github.com/BeamNG/BeamNGpy/raw/master/media/steering.gif)

## Implement Your Test Generator ##
We make available a [code pipeline](code_pipeline) that will integrate your test generator with the simulator by validating, executing and evaluating your test cases. Moreover, we offer some [sample test generators](sample_test_generators/README.md) to show how to use our code pipeline.

## Information About the Competition ##
More information can be found on the SBST tool competition website: [https://sbst21.github.io/tools/](https://sbst21.github.io/tools/)

## Repository Structure ##
[Code pipeline](code_pipeline): code that integrates your test generator with the simulator

[Self driving car testing library](self_driving): library that helps the integration of the test input generators, our code pipeline, and the BeamNG simulator

[Scenario template](levels_template/tig): basic scenario used in this competition

[Documentation](documentation/README.md): contains the installation guide and the detailed rules of the competition

[Sample test generators](sample_test_generators/README.md): sample test generators already integrated with the code pipeline for illustrative purposes 

[Requirements](requirements-36.txt): file containing the list of the required packages

## License ##
The software we developed is distributed under GNU GPL license. See the [LICENSE.md](LICENSE.md) file.

## Contacts ##

Dr. Alessio Gambi  - Passau University, Germany - alessio.gambi@uni-passau.de

Dr. Vincenzo Riccio  - Software Institute @ USI, Lugano, Switzerland - vincenzo.riccio@usi.ch

Dr. Fiorella Zampetti  - University of Sannio, Italy - fiorella.zampetti@unisannio.it

Dr. Sebastiano Panichella - Zurich University of Applied Science (ZHAW), Switzerland - panc@zhaw.ch
