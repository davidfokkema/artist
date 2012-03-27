all: demo

demo: demo_plots.pdf

clean:
	latexmk -c

realclean:
	rm -f demo_plots.pdf
	rm -f stopping-power-mpl.pdf stopping-power.tex
	rm -f shower-front.tex

demo_plots.pdf: demo_plots.tex \
                stopping-power-mpl.pdf stopping-power.tex \
                shower-front.tex
	latexmk -pdf demo_plots.tex

stopping-power-mpl.pdf stopping-power.tex: demo_stopping_power.py
	python $?

shower-front.tex: demo_shower_front.py
	python $?
