all: demo

demo: demo_plots.pdf

clean:
	latexmk -c

distclean:
	rm -f demo_plots.pdf
	rm -f stopping-power-mpl.pdf stopping-power.tex
	rm -f shower-front.tex
	rm -f eas-lateral.tex
	rm -f histogram-fit.tex

demo_plots.pdf: demo_plots.tex \
                stopping-power-mpl.pdf stopping-power.tex \
                shower-front.tex eas-lateral.tex histogram-fit.tex
	latexmk -pdf demo_plots.tex

stopping-power-mpl.pdf stopping-power.tex: demo_stopping_power.py
	python $?

shower-front.tex: demo_shower_front.py
	python $?

eas-lateral.tex: demo_eas_ldf.py
	python $?

histogram-fit.tex: demo_histogram_fit.py
	python $?
