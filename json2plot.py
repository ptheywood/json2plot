#!/usr/bin/python3
"""
Py script to generate graph from json
@author Peter Heywood <ptheywood1@sheffield.ac.uk>
"""
import os
import re
import sys
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from distutils.util import strtobool
import seaborn as sns

class Series:
    """ Class for convinient storage of data to be plotted.
    """

    def __init__(self, name, color, linewidth, linestyle, marker, marker_size, x, y):
        self.name = name
        self.color = color
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.marker = marker
        self.marker_size = marker_size
        self.x = x
        self.y = y


class Fill:
    """ Class for convinent storage of fill data
    """

    def __init__(self, color, x, y0, y1):
        self.color = color
        self.x = x
        self.y0 = y0
        self.y1 = y1


class PlotData:
    """ Class which loads data from json file, and createas an approriate figure based on the data.
    """

    # Class constnats containing json keys
    TITLE_KEY = "title"
    X_LABEL_KEY = "x_label"
    Y_LABEL_KEY = "y_label"
    LEGEND_Y_OFFSET_KEY = "legend_y_offset"
    LEGEND_LOC_KEY = "legend_loc"
    X_LIM_KEY = "x_lim"
    Y_LIM_KEY = "y_lim"
    X_SCALE_KEY = "x_scale"
    Y_SCALE_KEY = "y_scale"
    X_LOG_BASE_KEY = "x_log_base"
    Y_LOG_BASE_KEY = "y_log_base"
    X_TICKS_KEY = "x_ticks"
    Y_TICKS_KEY = "y_ticks"
    X_TICKS_LABELS_KEY = "x_ticks_labels"
    Y_TICKS_LABELS_KEY = "y_ticks_labels"
    X_TICKS_MINOR_KEY = "x_ticks_minor"
    Y_TICKS_MINOR_KEY = "y_ticks_minor"
    GRID_MAJOR_KEY = "grid_major"
    GRID_MINOR_KEY = "grid_minor"
    SERIES_TAG = "series"
    SERIES_NAME_TAG = "name"
    SERIES_COLOR_TAG = "color"
    SERIES_LINEWIDTH_TAG = "linewidth"
    SERIES_LINESTYLE_TAG = "linestyle"
    SERIES_MARKER_TAG = "marker"
    SERIES_MARKER_SIZE_TAG = "marker_size"
    SERIES_DATA_TAG = "data"
    FILL_TAG = "fill"
    FILL_COLOR_TAG = "color"
    FILL_DATA_TAG = "data"

    FONTSIZE_TITLE_KEY = "fontsize_title"
    FONTSIZE_LABEL_KEY = "fontsize_label"
    FONTSIZE_LEGEND_KEY = "fontsize_legend"
    FONTWEIGHT_TITLE_KEY = "fontweight_title"
    LABELSIZE_TICK_KEY = "labelsize_tick"

    DEFUALT_LEGEND_Y_OFFSET = -0.15
    DEFUALT_LEGEND_LOC = "best"
    DEFAULT_LOG_BASE = 10
    SERIES_DEFAULT_LINEWIDTH = 2.0
    SERIES_DEFAULT_MARKER_SIZE = 4
    # DEFAULT_FIGSIZE = (8, 5.5)

    def __init__(self, path_to_file):
        self.title = None
        self.x_label = None
        self.y_label = None
        self.legend_y_offset = self.DEFUALT_LEGEND_Y_OFFSET
        self.legend_loc = self.DEFUALT_LEGEND_LOC
        self.x_lim = None
        self.y_lim = None
        self.x_scale = None
        self.y_scale = None
        self.x_log_base = self.DEFAULT_LOG_BASE
        self.y_log_base = self.DEFAULT_LOG_BASE
        self.x_ticks = None
        self.y_ticks = None
        self.x_ticks_labels = None
        self.y_ticks_labels = None
        self.x_ticks_minor = False
        self.y_ticks_minor = False
        self.grid_major = False
        self.grid_minor = False
        self.series_data = None 
        self.fill_data = None

        self.fontsize_title = 16
        self.fontsize_label = 14
        self.fontsize_legend = 9
        self.fontweight_title = 600
        self.labelsize_tick = 13

        self.process_file(path_to_file)

    def __repr__(self):
        return "PlotData(\"{:}\", \"{:}\", \"{:}\", {:})".format(self.title, self.x_label, self.y_label, self.series_data)

    def process_file(self, path_to_file):
        """ Given the path to a file, decode any json contained within. Checks the file exists and contains valid JSON
        """
        # Check the file exists
        if os.path.isfile(path_to_file):
            # process the csv
            with open(path_to_file, 'r') as f:
                try:
                    raw_data = json.load(f)
                    self.process_json(raw_data)
                except ValueError:
                    sys.exit("Error: Please specify a valid JSON file")
        else:
            # Error if the file does not exist
            sys.exit("Error: File `{:}` does not exist".format(path_to_file))

    def process_json(self, raw_json):
        """ Given a decoded json object, extract targeted information and store data appropraitely for later usage.
        """
        # Look for certain strings and if they exist store the approprate data for later use.

        # Extract and store the title for later
        if self.TITLE_KEY in raw_json:
            self.title = raw_json[self.TITLE_KEY]
        # Extract and store the x_label for later
        if self.X_LABEL_KEY in raw_json:
            self.x_label = raw_json[self.X_LABEL_KEY]
        # Extract and store the y_label for later
        if self.Y_LABEL_KEY in raw_json:
            self.y_label = raw_json[self.Y_LABEL_KEY]
        if self.LEGEND_Y_OFFSET_KEY in raw_json:
            self.legend_y_offset = raw_json[self.LEGEND_Y_OFFSET_KEY]
        if self.LEGEND_LOC_KEY in raw_json and raw_json[self.LEGEND_LOC_KEY] is not None and len(raw_json[self.LEGEND_LOC_KEY]) > 0:
            self.legend_loc = raw_json[self.LEGEND_LOC_KEY]
        # Extract and store the x_lim for later
        if self.X_LIM_KEY in raw_json and isinstance(raw_json[self.X_LIM_KEY], list) and len(raw_json[self.X_LIM_KEY]) > 0:
            self.x_lim = tuple(raw_json[self.X_LIM_KEY])
        # Extract and store the y_lim for later
        if self.Y_LIM_KEY in raw_json and isinstance(raw_json[self.Y_LIM_KEY], list) and len(raw_json[self.Y_LIM_KEY]) > 0:
            self.y_lim = tuple(raw_json[self.Y_LIM_KEY])

        if self.X_SCALE_KEY in raw_json:
            self.x_scale = raw_json[self.X_SCALE_KEY]
        if self.Y_SCALE_KEY in raw_json:
            self.y_scale = raw_json[self.Y_SCALE_KEY]
        if self.X_LOG_BASE_KEY in raw_json:
            self.x_log_base = raw_json[self.X_LOG_BASE_KEY]
        if self.Y_LOG_BASE_KEY in raw_json:
            self.y_log_base = raw_json[self.Y_LOG_BASE_KEY]

        if self.X_TICKS_KEY in raw_json and len(raw_json[self.X_TICKS_KEY]) > 0:
            self.x_ticks = raw_json[self.X_TICKS_KEY]
        if self.Y_TICKS_KEY in raw_json and len(raw_json[self.Y_TICKS_KEY]) > 0:
            self.y_ticks = raw_json[self.Y_TICKS_KEY]

        if self.X_TICKS_LABELS_KEY in raw_json and len(raw_json[self.X_TICKS_LABELS_KEY]) > 0:
            self.x_ticks_labels = raw_json[self.X_TICKS_LABELS_KEY]
        if self.Y_TICKS_LABELS_KEY in raw_json and len(raw_json[self.Y_TICKS_LABELS_KEY]) > 0:
            self.y_ticks_labels = raw_json[self.Y_TICKS_LABELS_KEY]

        if self.X_TICKS_MINOR_KEY in raw_json and raw_json[self.X_TICKS_MINOR_KEY] == 1 or raw_json[self.X_TICKS_MINOR_KEY] == "True":
            self.x_ticks_minor = True
        if self.Y_TICKS_MINOR_KEY in raw_json and raw_json[self.Y_TICKS_MINOR_KEY] == 1 or raw_json[self.Y_TICKS_MINOR_KEY] == "True":
            self.y_ticks_minor = True

        # Extract and store the major and minor grid values
        if self.GRID_MAJOR_KEY in raw_json and raw_json[self.GRID_MAJOR_KEY] == 1 or raw_json[self.GRID_MAJOR_KEY] == "True":
            self.grid_major = True
        if self.GRID_MINOR_KEY in raw_json and raw_json[self.GRID_MINOR_KEY] == 1 or raw_json[self.GRID_MINOR_KEY] == "True":
            self.grid_minor = True

        # Extract and process the series data if set
        if self.SERIES_TAG in raw_json:
            self.series_data = self.process_series_data(raw_json[self.SERIES_TAG])

        if self.FILL_TAG in raw_json:
            self.fill_data = self.process_fill_data(raw_json[self.FILL_TAG])


        if self.FONTSIZE_TITLE_KEY in raw_json:
            self.fontsize_title = raw_json[self.FONTSIZE_TITLE_KEY] #if raw_json[self.FONTSIZE_TITLE_KEY] 
        if self.FONTSIZE_LABEL_KEY in raw_json:
            self.fontsize_label = raw_json[self.FONTSIZE_LABEL_KEY] #if raw_json[self.FONTSIZE_LABEL_KEY] 
        if self.FONTSIZE_LEGEND_KEY in raw_json:
            self.fontsize_legend = raw_json[self.FONTSIZE_LEGEND_KEY] #if raw_json[self.FONTSIZE_LEGEND_KEY] 
        if self.FONTWEIGHT_TITLE_KEY in raw_json:
            self.fontweight_title = raw_json[self.FONTWEIGHT_TITLE_KEY] #if raw_json[self.FONTWEIGHT_TITLE_KEY] 
        if self.LABELSIZE_TICK_KEY in raw_json:
            self.labelsize_tick = raw_json[self.LABELSIZE_TICK_KEY] #if raw_json[self.LABELSIZE_TICK_KEY] 

    def process_series_data(self, series_json):
        """ Given a list decoded from json, extract useful values and store them approprately for plotting
        """
        series_data = []
        for series in series_json:
            name = series[self.SERIES_NAME_TAG] if self.SERIES_NAME_TAG in series else None
            color = series[self.SERIES_COLOR_TAG] if self.SERIES_COLOR_TAG in series else None
            linewidth = series[self.SERIES_LINEWIDTH_TAG] if self.SERIES_LINEWIDTH_TAG in series else self.SERIES_DEFAULT_LINEWIDTH
            linestyle = series[self.SERIES_LINESTYLE_TAG] if self.SERIES_LINESTYLE_TAG in series else None
            marker = series[self.SERIES_MARKER_TAG] if self.SERIES_MARKER_TAG in series else None
            marker_size = series[self.SERIES_MARKER_SIZE_TAG] if self.SERIES_MARKER_SIZE_TAG in series else self.SERIES_DEFAULT_MARKER_SIZE
            x = []
            y = []
            if self.SERIES_DATA_TAG in series:
                for v in series[self.SERIES_DATA_TAG]:
                    if isinstance(v, list):
                        if len(v) == 2:
                            x.append(v[0])
                            y.append(v[1])
                        elif len(v) == 1:
                            x.append(len(x))
                            y.append(v[0])
                    elif type(v) == float or type(v) == int:
                        x.append(len(x))
                        y.append(v)
            obj = Series(name, color, linewidth, linestyle, marker, marker_size, x, y)
            series_data.append(obj)
        return series_data

    def process_fill_data(self, fill_json):
        """ Given a list decoded from json, extract useful values and store them approprately for plotting
        """
        fill_data = []
        for fill in fill_json:
            color = fill[self.FILL_COLOR_TAG] if self.FILL_COLOR_TAG in fill else None
            x = []
            y0 = []
            y1 = []
            if self.FILL_DATA_TAG in fill:
                for values in fill[self.FILL_DATA_TAG]:
                    if len(values) == 3:
                        x.append(values[0])
                        y0.append(values[1])
                        y1.append(values[2])
                    elif len(values) ==2:
                        x.append(values[0])
                        y0.append(0)
                        y1.append(values[1])
            obj = Fill(color, np.array(x), np.array(y0), np.array(y1))

            fill_data.append(obj)
        return fill_data

    def plot(self, output_file, dpi, force, series_filter, series_regex):
        """ Plot a figure based on the stored class variables.
        Either view the plot interactivley, or write it out to a file, at a target dpi (or default).
        If the file exists already check with the user about overwriting it, unless the --force flag is set.
        """
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')

        sns.set_style("white")
        sns.set_style("ticks")
        # sns.set_context(rc={'lines.markeredgewidth': 0.1})

        fig, ax = plt.subplots()
        if self.title is not None:
            ax.set_title(self.title, y=1.05, fontdict={'fontsize': self.fontsize_title, 'fontweight' : self.fontweight_title})
        if self.x_label is not None:
            ax.set_xlabel(self.x_label, labelpad=8, fontdict={'fontsize': self.fontsize_label})
        if self.y_label is not None:
            ax.set_ylabel(self.y_label, labelpad=8, fontdict={'fontsize': self.fontsize_label})

        if self.x_scale is not None:
            try:
                ax.set_xscale(self.x_scale, basex=self.x_log_base)
            except ValueError as e:
                print("Caught Exception: {:}".format(e))
        if self.y_scale is not None:
            try:
                ax.set_yscale(self.y_scale, basey=self.y_log_base)
            except ValueError as e:
                print("Caught Exception: {:}".format(e))

        if self.x_ticks is not None:
            ax.set_xticks(self.x_ticks)
            ax.get_xaxis().set_major_formatter(ticker.ScalarFormatter())

        if self.x_ticks_labels is not None:
            ax.set_xticklabels(self.x_ticks_labels, rotation=90, ha='center')
        if self.y_ticks_labels is not None:
            ax.set_yticklabels(self.y_ticks_labels)

        if self.y_ticks is not None:
            ax.set_yticks(self.y_ticks)
            ax.get_yaxis().set_major_formatter(ticker.ScalarFormatter())

        # set the minor ticks options, including other parameters
        if self.x_ticks_minor == False:
            ax.get_xaxis().set_minor_locator(ticker.NullLocator())
        elif self.grid_minor:
            ax.get_xaxis().set_minor_locator(ticker.AutoMinorLocator())

        if self.y_ticks_minor == False:
            ax.get_yaxis().set_minor_locator(ticker.NullLocator())
        elif self.grid_minor:
            ax.get_yaxis().set_minor_locator(ticker.AutoMinorLocator())

        if self.grid_major == True:
            ax.grid(self.grid_major, "major")

        if self.grid_minor == True:
            ax.grid(self.grid_minor, "minor")

        # Make major lableticks larger
        ax.tick_params(axis='both', which='major', labelsize=self.labelsize_tick)

        # If any regular expressions were provided, compile them.
        filter_expressions = None
        if series_regex is not None and len(series_regex) > 0:
            filter_expressions = []
            for pattern in series_regex:
                filter_expressions.append(re.compile(pattern))

        # plot each series of data, subject to any filters or regular expressions.
        for series in self.series_data:
            plot_series = False if series_filter is not None or series_regex is not None else True
            # If filtering by string
            if series_filter is not None:
                # If the series name contains the filter string it is to be rendered.
                for string in series_filter:
                    if string in series.name:
                        plot_series = True
            if series_regex is not None and not plot_series:
                for regex in filter_expressions:
                    if regex.match(series.name):
                        plot_series = True

            if plot_series:
                line, = ax.plot(series.x, series.y, color=series.color, linestyle=series.linestyle, marker=series.marker, label=series.name, linewidth=series.linewidth, markersize=series.marker_size)
                # manually change -- lengths
                if series.linestyle == "--":
                    line.set_dashes([3, 3])
                elif series.linestyle == "-.":
                    line.set_dashes([2, 2, 1, 1])
                elif series.linestyle == ":":
                    line.set_dashes([1, 1])


        # Fill where neccesary
        if self.fill_data is not None:
            for fill in self.fill_data:
                ax.fill_between(fill.x, fill.y0, fill.y1, where=fill.y0<fill.y1, interpolate=True)
                ax.fill_between(fill.x, fill.y0, fill.y1, where=fill.y0<fill.y1, facecolor=fill.color, interpolate=True)

        # Now add the legend with some customizations.
        # legend = ax.legend(loc='upper center', fontsize=self.fontsize_legend, bbox_to_anchor=(0.5, self.legend_y_offset))
        legend = ax.legend(loc=self.legend_loc, fontsize=self.fontsize_legend, handlelength=3)


        # draw grid below items
        ax.set_axisbelow(True)

        if self.x_lim is not None:
            left = self.x_lim[0]
            if  len(self.x_lim) > 0 and self.x_scale == "log" and self.x_lim[0] == 0:
                left = 1
            if len(self.x_lim) == 1:
                ax.set_xlim(left=left)
            else:
                ax.set_xlim(left, self.x_lim[1])
        if self.y_lim is not None:
            bottom = self.y_lim[0]
            if len(self.y_lim) > 0 and self.y_scale == "log" and self.y_lim[0] == 0:
                bottom = 1
            if len(self.y_lim) == 1:
                ax.set_ylim(bottom=bottom)
            else:
                ax.set_ylim(bottom, self.y_lim[1])

        if output_file is None:
            plt.show()
        else:
            if force or self.file_overwrite_check(output_file):
                if legend is not None:
                    plt.savefig(output_file, dpi=dpi, bbox_extra_artists=(legend,), bbox_inches='tight')
                else:
                    plt.savefig(output_file, dpi=dpi)
                print("Figure saved to file: {:} ({:} DPI)".format(output_file, dpi if dpi is not None else "Default"))
            else:
                print("Figure not saved - file protected")

    def file_overwrite_check(self, f):
        """ Return if it is safe to write to the target file, potentially after user involvement
        """
        if os.path.isfile(f):
            overwrite = self.user_yes_no_query("The file {:} exists, do you wish to overwrite?".format(f))
            return overwrite
        else:
            return True

    def user_yes_no_query(self, question):
        """ Simple y/n prompy to the user, via SO: http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
        """
        sys.stdout.write('%s [y/n]\n' % question)
        while True:
            try:
                return strtobool(input().lower())
            except ValueError:
                sys.stdout.write('Please respond with \'y\' or \'n\'.\n')


def main():
    """ Main method invoking argparse, creating the PlotData instance and then plotting the figure
    """
    parser = argparse.ArgumentParser(description="Python script to generate line plot for input data, with a custom legend")
    parser.add_argument("-v", "--verbose", action="store_true", help="increase verbosity of output")
    parser.add_argument("-f", "--force", action="store_true", help="Force overwriting of files (surpress user confirmation)")
    parser.add_argument("-o", "--output-file", type=str, help="file to output plot to")
    parser.add_argument("--dpi", type=int, help="DPI for output file")
    parser.add_argument("--series-filter", nargs="*", type=str, help="List of series keys to render")
    parser.add_argument("--series-regex", nargs="*", type=str, help="Regular expression(s) to match against series keys for plotting.")

    parser.add_argument("input_file", type=str, help="data to be plotted")

    args = parser.parse_args()

    plot_data = PlotData(args.input_file)
    plot_data.plot(args.output_file, args.dpi, args.force, args.series_filter, args.series_regex)


if __name__ == "__main__":
    main();
