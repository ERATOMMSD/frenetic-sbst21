git config --global user.name "Ezequiel Castellano
git config --global user.email "ezequiel.castellano@gmail.com"
git pull

timeout /t 5

del /s /q .\simulations\beamng_executor
del /s /q .\experiments
del %1_%3.log*
mkdir experiments

timeout /t 5 

@echo off

python competition.py --time-budget %1 --module-name src.generators.%2 --class-name %3 --executor beamng --beamng-home C:\Users\Administrator\Documents\BeamNG.research --beamng-user C:\Users\Administrator\Documents\BeamNG.research --log-to %1_%3.log

timeout /t 10

git clone https://github.com/ERATOMMSD/sbst-results.git ..\sbst-results

mkdir ..\sbst-results\%1_%3\
move %1_%3.log* ..\sbst-results\%1_%3\
move simulations ..\sbst-results\%1_%3\
move experiments ..\sbst-results\%1_%3\	

cd ..\sbst-results\

timeout /t 10

git pull

git add *

git commit -m "Uploading results"

git push 

shutdown /s /f /t 60
