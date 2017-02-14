import regex_parser as rp
from collections import Counter  # dict subclass more efficient to count hashable objects
from collections import deque    # list-like container with fast appends and pops on either end

class Datastruct:
    """data structure designed to store new log lines in a log files for efficient access to relevant statistics"""

    def __init__(self, alert_period, stats_period):
        self._pos_in_file = 0  # used to store last position in file
        self._pos_offset = 2  # used for 1st iteration, to go to end of file and disregard log file content when we start
        self._last_sections = Counter()  # {section: hits} during last period
        self._last_users = Counter()  # {userid: hits} during last period
        self._last_errors = Counter()  # {section: nb of errors} during last periods
        self.last_hits = 0  # number of hits during last period
        self.last_traffic = 0 # bytes traffic during last period
        self.hist_traffic = deque()  # used to keep traffic information on a longer timeframe to monitor peaks
        self.counter = 0 # historic number of monitoring periods - for display purposes
        self.alert_period = alert_period
        self.stats_period = stats_period

    def _fill_with_parsed(self, parsed_line):
        """
        Takes a parsed line and fills relevant fields of data structure
        :param parsed_line: (dict): a parsed line
        :return: None
        """
        self._last_sections[parsed_line["section"]] += 1
        self._last_users[parsed_line["userid"]] += 1
        self.last_hits += 1
        self.last_traffic += parsed_line["size"]
        if str(parsed_line["status"]).startswith(("4", "5")):  # it's an error code
            self._last_errors[parsed_line["section"]] += 1

    def fill(self, log_file):
        """
        Takes a path to a log file and fills relevant fields of data structure
        :param log_file: (string) path to the log file
        :return: None
        """
        with open(str(log_file), 'r') as log_file:
            log_file.seek(self._pos_in_file, self._pos_offset)  # 1st call: it goes to the end. Otherwise, to pos_in_file
            self._pos_offset = 0
            line = log_file.readline()
            while line != "":
                parsed_line = rp.parse(line)
                self._fill_with_parsed(parsed_line)
                line = log_file.readline()
            self._pos_in_file = log_file.tell()

    def clear_last(self):
        """
        Empty data related to previous time period and stores relevant historic data in another container to monitor
        traffic for peaks
        :return: None
        """
        self.counter += 1                                          # historic counter used to display period number
        if self.counter > 1:  # if counter = 1, first iteration, self.last_hits = 0, we do not append it.
            if len(self.hist_traffic) == self.alert_period // self.stats_period: # hist_traffic has to contain traffic
                self.hist_traffic.popleft()                                      # info for the alert_period only
            self.hist_traffic.append(self.last_hits)
        self._last_sections.clear()                                 # we empty data related to previous period
        self._last_users.clear()
        self.last_hits = 0
        self._last_errors.clear()

    def compute_stats(self):
        """
        Returns a dictionary containing top 3 sections, users and error-filled sections by number of hits
        :return: (dict): dict.keys() = ["top_sections", "top_users", "errors"]
        """
        top_sections = self._last_sections.most_common(3) # returns a list of tuples ordered by occurences
        top_users = self._last_users.most_common(3)
        errors = self._last_errors.most_common(3)
        return {"top_sections": top_sections, "top_users": top_users, "errors": errors}

    def compute_debit(self, decimals=2):
        """
        Computes mean number of hits per second on past alert_period and rounds it.
        :param decimals: (int) number of decimals to keep
        :return: (float) average number of hits on past alert period (avg is computed per second)
        """
        average = float(sum(self.hist_traffic)) / max(1, self.alert_period // self.stats_period)
        debit = average / self.stats_period
        return round(debit, decimals)

    def _is_alert(self, alert_treshold):
        """
        Takes a treshold and returns the current alert state
        :param alert_treshold: (int) in hits/second over alert_period
        :return: (boolean): current alert state
        """
        debit = self.compute_debit()
        if debit >= alert_treshold:
            return True
        else:
            return False

    def compute_alert(self, alert_treshold, on_alert):
        """
        Takes a treshold and the current alert state and indicates whether there is an alert start or
         an alert recover
        :param alert_treshold: (int) in hits/second
        :param on_alert: (boolean) current alert state
        :return: (bool, dict) : bool: on_alert value, current alert state.
                                dict.keys() = [status_code, debit]. 1 for new alert, 0 for recovery, 2 for no change
        """
        alert_info = {}
        if not on_alert:
            if self._is_alert(alert_treshold):
                alert_info["status_code"] = 1
                alert_info["debit"] = self.compute_debit(0)
                return True, alert_info
        else:
            if not self._is_alert(alert_treshold):
                alert_info["status_code"] = 0
                alert_info["debit"] = self.compute_debit(0)
                return False, alert_info
        alert_info["status_code"] = 2
        alert_info["debit"] = None
        return on_alert, alert_info
