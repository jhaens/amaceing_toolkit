#!/bin/bash
echo ============================
echo Testing amaceing_ana
echo ============================
mkdir -p ana_koh
cd ana_koh
echo ----------------------------
amaceing_ana --file=../data/koh1.xyz --pbc=../data/pbc_koh1 --timestep=50.0 --visualize=y
pdflatex analysis.tex
pdflatex analysis.tex
cd ..
echo ----------------------------
mkdir -p ana_koh12
cd ana_koh12
amaceing_ana --file=../data/koh1.xyz,../data/koh2.xyz --pbc=../data/pbc_koh1,../data/pbc_koh2 --timestep=50.0,50.0 --visualize=y
pdflatex analysis.tex
pdflatex analysis.tex
cd ..
echo ----------------------------
echo ============================
echo Testing amaceing_ana done
echo ============================
