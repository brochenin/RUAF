@echo off
python FutureLearnProcess.py SETTINGS.csv graph\data.csv
cd graph
pdflatex graphs.tex
pdflatex graphs.tex
pause