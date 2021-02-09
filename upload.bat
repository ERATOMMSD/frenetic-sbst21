git config --global user.name "Ezequiel Castellano
git config --global user.email "ezequiel.castellano@gmail.com"
git pull

@echo off

git clone https://github.com/ERATOMMSD/sbst-results.git ..\sbst-results

mkdir ..\sbst-results\%1\
move *.log ..\sbst-results\%1\
move simulations ..\sbst-results\%1\
move experiments ..\sbst-results\%1\

cd ..\sbst-results\

timeout /t 10

git pull

git add *

git commit -m "Uploading results"

git push

PAUSE