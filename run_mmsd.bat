git config --global user.name "Ezequiel Castellano
git config --global user.email "ezequiel.castellano@gmail.com"
git pull

del /s /q .\simulations\beamng_executor
del /s /q .\experiments
del %1_%3.log*
mkdir experiments

@echo off

python competition.py --time-budget %1 --module-name src.generators.%2 --class-name %3 --executor beamng --beamng-home D:\Programs\BeamNG.research.v1.7.0.1 --beamng-user C:\Users\mmsd-admin\Documents\BeamNG.research --log-to %1_%3.log

timeout /t 10

mkdir ..\sbst-results\%1_%3\
move %1_%3.log* ..\sbst-results\%1_%3\
move simulations ..\sbst-results\%1_%3\
move experiments ..\sbst-results\%1_%3\	

cd ..\sbst-results\

git pull
git add *
git commit -m "Uploading results"
git push

PAUSE