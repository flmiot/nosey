import numpy as np
import logging
import nosey

Log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class Label(object):
    def __init__(self):
        self.labels = {}        # Dict of type {ScanName: [Analyzer1, ...], }

    def add_scan_labels(self, label_dict):
        self.labels.update(label_dict)

    def get_labels(self, single_scans = True, single_analyzers = True):
        """
        S           Number of scans
        A           Number of analyzers

        Return S x A array of labels if single_scans = False and
        single_analyzers = False

        Return S x 1 array of labels if single_scans = False and
        single_analyzers = True

        Return A x 1 array of labels if single_scans = True and
        single_analyzers = False

        Return single labels if single_scans = False and
        single_analyzers = False
        """

        lret = []
        if single_scans and single_analyzers:
            fmt = "{} - {}"
            for scan, analyzers in zip(self.labels, self.labels.values()):
                lret.append(list([fmt.format(scan, a) for a in analyzers]))

        elif single_scans and not single_analyzers:
            fmt = "{} - Summed: {}"
            for scan, analyzers in zip(self.labels, self.labels.values()):
                a_str = self.make_comma_separated_list(analyzers)
                lret.append([fmt.format(scan, a_str)])

        elif not single_scans and single_analyzers:
            scan_names = list(self.labels.keys())
            s_str = self.make_comma_separated_list(scan_names)
            first_key = list(self.labels.keys())[0]
            fmt = "{} - Summed: {}"
            lret.append(list([fmt.format(a, s_str) for a in self.labels[first_key]]))

        else:
            scan_names = list(self.labels.keys())
            s_str = self.make_comma_separated_list(scan_names)
            first_key = list(self.labels.keys())[0]
            analyzer_names = list([a for a in self.labels[first_key]])
            a_str = self.make_comma_separated_list(analyzer_names)
            lret.append(["Summed: {} - Summed: {}".format(s_str, a_str)])

        return np.array(lret)


    def make_comma_separated_list(self, labels):
        li = ""
        for ind, l in enumerate(labels):
            if ind == len(labels) - 1:
                li += l
            elif ind == 0 and ind == len(labels) - 1:
                li += l
            else:
                li += l + ", "

        return li
