#!/usr/bin/python

import hotshot.stats
import sys

stats = hotshot.stats.load(sys.argv[1])
stats.sort_stats('cumulative', 'time', 'calls')
stats.print_stats(20)