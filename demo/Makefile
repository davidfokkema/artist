.PHONY: all demo clean distclean test

all: demo

demo: demo_plots.pdf

clean:
	latexmk -c

distclean: clean
	rm -f stopping-power.tex
	rm -f shower-front.tex
	rm -f eas-lateral.tex
	rm -f histogram-fit.tex
	rm -f spectrum.tex
	rm -f sciencepark.tex
	rm -f utrecht.tex
	rm -f multiplot.tex
	rm -f polar_histogram.tex
	rm -f discrete_directions.tex
	rm -f histogram2d.tex
	rm -f multi_histogram2d.tex
	rm -f event_display.tex
	rm -f multi_event_display.tex
	rm -f relative_pin.tex
	rm -f relative_pin_log.tex
	rm -f any_option.tex
	rm -f multi_any_option.tex
	rm -f error_bars.tex
	rm -f fourier_with_legend.tex
	rm -f fourier_with_labels.tex
	rm -f mm_paper.tex
	rm -f mm_paper_multiplot.tex
	rm -f *.pdf
	rm -f *.png

demo_plots.pdf: demo_plots.tex \
		stopping-power-mpl.pdf stopping-power.tex \
		shower-front.tex eas-lateral.tex histogram-fit.tex \
		spectrum.tex sciencepark.tex utrecht.tex multiplot.tex \
		polar_histogram.tex discrete_directions.tex histogram2d.tex \
		multi_histogram2d.tex event_display.tex multi_event_display.tex \
		relative_pin.tex relative_pin_log.tex any_option.tex \
		multi_any_option.tex error_bars.tex fourier_with_legend.tex \
		fourier_with_labels.tex mm_paper.tex mm_paper_multiplot.tex
	latexmk -pdf demo_plots.tex

test: shower-front.tex eas-lateral.tex \
		spectrum.tex sciencepark.tex utrecht.tex multiplot.tex \
		polar_histogram.tex discrete_directions.tex histogram2d.tex \
		multi_histogram2d.tex event_display.tex multi_event_display.tex \
		relative_pin.tex relative_pin_log.tex any_option.tex \
		multi_any_option.tex error_bars.tex fourier_with_legend.tex \
		fourier_with_labels.tex mm_paper.tex mm_paper_multiplot.tex

stopping-power-mpl.pdf stopping-power.tex: demo_stopping_power.py
	python $?

shower-front.tex: demo_shower_front.py
	python $?

eas-lateral.tex: demo_eas_ldf.py
	python $?

histogram-fit.tex: demo_histogram_fit.py
	python $?

spectrum.tex: demo_spectrum.py
	python $?

sciencepark.tex: demo_sciencepark.py
	python $?

utrecht.tex: demo_utrecht.py
	python $?

multiplot.tex: demo_multiplot.py
	python $?

polar_histogram.tex: demo_polar_histogram.py
	python $?

discrete_directions.tex: demo_discrete_directions.py
	python $?

histogram2d.tex multi_histogram2d.tex: demo_histogram2d.py
	python $?

event_display.tex multi_event_display.tex: demo_event_display.py
	python $?

relative_pin.tex relative_pin_log.tex: demo_relative_pin.py
	python $?

any_option.tex multi_any_option.tex: demo_any_option.py
	python $?

error_bars.tex: demo_error_bars.py
	python $?

fourier_with_legend.tex fourier_with_labels.tex: demo_fourier_with_legend.py
	python $?

mm_paper.tex mm_paper_multiplot.tex: demo_mm_paper.py
	python $?
