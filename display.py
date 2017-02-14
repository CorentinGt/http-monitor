import curses
from contextlib import redirect_stdout
import time
import os
import sys


def hacked_print(string):
    """
    Takes a string and print it to the console by first printing it in a text file and then flushing text file in
    stdout
    :param string: (string)
    :return:
    """
    with open('buffer.txt', 'w+') as f:  # this is a hack against print buffer issues:
        with redirect_stdout(f):    # if we print directly after curses.endwin(), print statement doesn't display
            print(string)           # correctly: buffer issues
        f.seek(0)                   # sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0) solves it but raises an error
        print(f.readline())         # (open bug # 17404). We redirect stout to a file, print in it, then read from file
    try:
        os.remove("buffer.txt")
    except OSError:
        pass


def center_string_box(string, x_start, x_end):
    """
    Computes abscissa so that given string is displayed centered in a box
    :param string: (string) to center
    :param x_start: (int) left coordinate of the box
    :param x_end: (int) right coordinate of the box
    :return: (int) string start abscissa
    """
    return (x_end - x_start) // 2 - len(string) // 2


class Display:
    HEADER_1 = "Statistics of the last period:"
    HEADER_2 = "History of traffic alerts:"
    STATS_INIT = "Please wait for first monitoring period to end."
    STATS_NOTRAFFIC = "There was no traffic on the period."
    STATS_SECTION0 = "Monitoring period number: "
    STATS_SECTION1 = "Number of hits: "
    STATS_SECTION2 = "Top 3 sections: "
    STATS_SECTION3 = "Top 3 users: "
    STATS_SECTION4 = "Top 3 sections with most errors: "
    STATS_SECTION5 = "Total traffic on period (bytes):"
    Q_TO_EXIT = "Press 'q' to end monitoring and return to terminal window"
    HIGH_TRAFFIC_TEMPLATE = "High traffic generated an alert - Hits/s: {:.0f}"
    RECOVER = "Recovered at: {}, hits/s: {:.0f}"
    GETCH_REFRESH_MS = 20 # we check if "q" is pressed by user every GETCH_REFRESH_MS milliseconds to be responsive

    def __init__(self, myscreen):
        try:
            curses.curs_set(0)                                      # set cursor invisible
            self.myscreen = myscreen
            self.box1 = curses.newwin(43, 59, 1, 1)
            self.box2 = curses.newwin(43, 59, 1, 60)
            self.box1.box()
            self.box2.box()
            self.box1.addstr(1, center_string_box(self.HEADER_1, 1, 1 + 59), self.HEADER_1)
            self.box2.addstr(1, center_string_box(self.HEADER_2, 60, 60 + 59), self.HEADER_2)
            self.myscreen.addstr(45, 2, self.Q_TO_EXIT)
            self._refresh_screen()
        except curses.error:    # we have to go back to console environment and ask user to resize window
            myscreen.erase()    # not pretty but couldn't figure any other way to recover from error & print
            myscreen.refresh()  # without displaying stack trace. I don't have resize function in my curses porting to
            myscreen.keypad(0)  # Windows.
            curses.echo()
            curses.nocbreak()
            curses.endwin()
            sys.exit("Please resize terminal window to full screen & retry \nThank you")

    def _refresh_screen(self):
        """
        Refresh the screen to display new elements and remove older
        :return: None
        """
        self.myscreen.refresh()
        self.box1.refresh()
        self.box2.refresh()

    def loop_exit_on_q(self, stats_period):
        """
        Close curses application & go back to console environnement on key pressed ("q")
        :param stats_period: (int) duration (seconds) of the stats monitoring period
        :return:
        """
        start_time = time.time()            # This is the only way I managed to make a curse application with
        while time.time() - start_time <= stats_period:   # screen refreshing exit on key pressed: make window.getch()
            key = self.myscreen.getch()     # non blocking with curses.nodelay(1) (otherwise main loop is interrupted)
            if key == ord('q'):             # and check it every [10-50]ms to be responsive.
                curses.endwin()
                hacked_print("Monitoring ended by user") # cf hacked_print method
                return 1
            curses.napms(self.GETCH_REFRESH_MS)

    def update_stats(self, datastruct):
        """
        Displays last period stats on screen
        :param datastruct: (Datastruct)
        :return: None
        """
        counter = datastruct.counter
        stats_dict = datastruct.compute_stats()
        if counter == 0:
            self.box1.addstr(5, 2, self.STATS_INIT)
        else:
            self.box1.move(2, 1)
            self.box1.clrtobot()
            self.box1.box()
            if datastruct.last_hits == 0:
                self.box1.addstr(5, 2, self.STATS_SECTION0 + str(datastruct.counter))
                self.box1.addstr(8, 2, self.STATS_NOTRAFFIC)
            else:
                self.box1.addstr(5, 2, self.STATS_SECTION0 + str(datastruct.counter))
                self.box1.addstr(8, 2, self.STATS_SECTION1 + str(datastruct.last_hits))
                self.box1.addstr(11, 2, self.STATS_SECTION2)
                for index, (section, hits) in enumerate(stats_dict["top_sections"]):
                    self.box1.addstr(13+2*index, 4, str(index + 1) + "." + section + ":" + str(hits))
                self.box1.addstr(20, 2, self.STATS_SECTION3)
                for index, (user, hits) in enumerate(stats_dict["top_users"]):
                    self.box1.addstr(22+2*index, 4, str(index + 1) + "." + user + ":" + str(hits))
                self.box1.addstr(29, 2, self.STATS_SECTION4)
                for index, (error, hits) in enumerate(stats_dict["errors"]):
                    self.box1.addstr(31+2*index, 4, str(index + 1) + "." + error + ":" + str(hits))
                self.box1.addstr(38, 2, self.STATS_SECTION5 + str(datastruct.last_traffic))
        self._refresh_screen()

    def update_alerts(self, display_dict):
        """
        Display potential alert triggers or recoveries
        :param display_dict: (dict) dict returned by datastruct.compute_alert()
        :return: None
        """
        self._go_to_first_blank(self.box2)
        if display_dict["status_code"] == 1:
            y = self._go_to_first_blank(self.box2)
            self.box2.addstr(y, 4, self.HIGH_TRAFFIC_TEMPLATE.format(display_dict["debit"]))
            self.box2.addstr(y + 1, 4, "Triggered at: {time}".format(time=time.strftime("%H:%M:%S", time.localtime())))
        elif display_dict["status_code"] == 0:
            y = self._go_to_first_blank(self.box2)
            self.box2.addstr(y - 1, 4, self.RECOVER.format(time.strftime("%H:%M:%S", time.localtime()),
                                                           display_dict["debit"]))

    def _go_to_first_blank(self, box):
        """
        Returns first line blank line where we can write without overwriting anything. If there are not enough blank
        lines, scrolls up the window, thus removing oldest entries
        :param box: (curses.window) window object where we want to write
        :return: (int) line number of first writable line
        """
        for y in range(4, 41):
            self.box2.move(y, 4)
            if chr(self.box2.inch() & 0xFF) == ' ': # binary and because char is in bottom 8 bits.
                self.box2.move(y + 1, 4)
                if chr(self.box2.inch() & 0xFF) == ' ': # look for 2 blank lines in a raw
                    y, x = self.box2.getyx()   # store position, we can add new alert below
                    try:
                        if chr(self.box2.inch(y + 1, x) & 0xFF) == ' ':
                            return y
                    except curses.error: # this is the case where we had 2 blank lines but these were the last 2 lines
                        pass # of the screen. We can't /n + write two lines so we need to proceed to screen scrolling
        # screen is filled with alerts
        self.box2.scrollok(True)
        self.box2.move(4, 4)
        self.box2.setscrreg(4, 41)
        self.box2.scroll(4)
        self.box2.box() # need to redraw borders
        return self._go_to_first_blank(self.box2)
