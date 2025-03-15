set terminal pngcairo
set output 'images/gnuplot.png'

set yrange [0:42]
# Line style for axes
set style line 80 lt rgb "#808080"

# Line style for grid, border and tics
set style line 81 lt 0
set style line 81 lt rgb "#808080"
set grid back linestyle 81
set border 3 back linestyle 80
set xtics nomirror 2
set ytics nomirror

set key autotitle columnheader
set key top right box

# Line styles: try to pick pleasing colors, rather
# than strictly primary colors or hard-to-see colors
# like gnuplot's default yellow.

set xlabel 'Model Time [h]' offset 0,0.5

plot 'gnuplot/data.dat' using 1:2 with lines title 'TemperatureOutside', \
     'gnuplot/data.dat' using 1:3 with lines title 'TemperatureBoiler', \
     'gnuplot/data.dat' using 1:4 with lines title 'WantedTemperature', \
     'gnuplot/data.dat' using 1:5 with lines title 'TemperatureRoom', \
     'gnuplot/data.dat' using 1:6 with lines title 'TemperatureHeating', \
     'gnuplot/data.dat' using 1:7 with lines title 'WindowHeatLoss', \
     'gnuplot/data.dat' using 1:8 with lines title 'ValveHeating'


