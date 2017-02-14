import datastruct as dt
import display as dp
import curses
import argparse


def main(myscreen, args):
    stats_period = args.p_stats
    alert_period = args.p_alert
    alert_treshold = args.t_alert
    log_file = "logs2.txt"
    on_alert = False
    loop = True
    datastruct = dt.Datastruct(alert_period, stats_period)
    display = dp.Display(myscreen)
    myscreen.nodelay(1)
    while loop:
        datastruct.fill(log_file)
        datastruct.compute_stats()
        display.update_stats(datastruct)
        datastruct.clear_last()
        on_alert, to_display = datastruct.compute_alert(alert_treshold, on_alert)
        display.update_alerts(to_display) # has to be called after clear_last()
        if display.loop_exit_on_q(stats_period) == 1:
            loop = False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP Monitoring application')
    parser.add_argument('-s', help='monitoring period length in seconds (int)', type = int, default=10, dest="p_stats")
    parser.add_argument('-a', help='alert period length in seconds (int)', type = int, default=120, dest="p_alert")
    parser.add_argument('-t', help='alert treshold in hits/seconds (int)', type=int, default=20, dest="t_alert")
    args = parser.parse_args()
    curses.wrapper(main, args) #wrapper so that curses.endwin() is called everytime and we can switch back to normal I/O
