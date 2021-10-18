srcdir = src
includedir = include
resultsdir = results
bindir = bin

.PHONY: all

all: results/animation.gif

results/animation.gif: plot_results.py $(resultsdir)/R.dat $(resultsdir)/r.dat $(resultsdir)/cnfg.dat
	python3 $<

$(resultsdir)/R.dat $(resultsdir)/r.dat $(resultsdir)/cnfg.dat: spherical_elevator.exe
	./spherical_elevator.exe

spherical_elevator.exe: spherical_elevator.cpp
	g++ -o $@ $^ -lm -I.