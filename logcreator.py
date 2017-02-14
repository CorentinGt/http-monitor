"""
Generate an actively written-to logfile. Loglines are
- par   tially randomized so that interesting statistics can be infered.
- W3C formatted: 127.0.0.1 user-identifier frank [10/Oct/2000:13:55:36 -0700] "GET /test/image.jpg HTTP/1.1" 200 2326
- generated so that line-throughput varies.
"""
import random
import time
import datetime

W3C_TEMPLATE = "192.168.0.{ip_last} - {user_id} [{datetime} -0700] \"{method} /{section}/{page} HTTP/1.1\" {status} " \
               "{size}"
USER_ID = {"192.168.0.1":"Corentin",
           "192.168.0.2": "Remi",
           "192.168.0.3": "Antoine",
           "192.168.0.4": "Jacques",
           "192.168.0.5": "Brandon",
           "192.168.0.6": "Snoopdog"}
HTTP_METHOD = ["GET", "PUT", "POST", "DELETE"]
HTTP_STATUS = [100, 200, 300, 404, 500]
SITE_SECTIONS = ["fruits", "vegetables", "others"]
SITE_FRUIT_PAGES = ["orange.jpg", "lemon.jpg", "kiwi.jpg", "lime.jpg", "pineapple.jpg"]
SITE_VEGETABLE_PAGES = ["artichoke.jpg", "asparagus.jpg", "corn.jpg", "pea.jpg", "potato.jpg"]
SITE_OTHERS_PAGES = ["rice.jpg", "pasta.jpg", "mushroom.jpg", "42.jpg"]
PATH = "logs2.txt"


def generate_logline():
    """
    Generates a W3C formatted log line
    :return: (string) W3C formatted log line
    """
    ip_last = random.randint(1, 6)
    site_section = random.choice(SITE_SECTIONS)
    if site_section == "fruits":
        site_page = random.choice(SITE_FRUIT_PAGES)
    elif site_section == "vegetables":
        site_page = random.choice(SITE_VEGETABLE_PAGES)
    else:
        site_page = random.choice(SITE_OTHERS_PAGES)

    line = W3C_TEMPLATE.format(ip_last=ip_last,
                               user_id=USER_ID["192.168.0." + str(ip_last)],
                               datetime=time.strftime("%d/%b/%Y:%H:%M:%S"),
                               method=random.choice(HTTP_METHOD),
                               section=site_section,
                               page=site_page,
                               status=random.choice(HTTP_STATUS),
                               size=random.randint(0, 10000))
    return line


def main():
    go_on = True
    with open(str(PATH), 'a') as file:
        while go_on:
            try:
                high = (random.randint(1, 1500) == 1)            # i should have a traffic peak every 1500 lines ~ 2 min
                if not high:                                     # since i write 5 lines/sec to 20 lines / sec
                    milliseconds = float(random.randint(50, 200))
                    seconds = milliseconds / 1000.0
                    time.sleep(seconds)
                    line = generate_logline() + "\n"
                    file.write(line)
                    file.flush()                                  # we need to flush to write to file immediately
                    print(line)
                else:
                    peak_start_time = datetime.datetime.now()
                    high_duration = datetime.timedelta(seconds=random.randint(60, 120))
                    print("traffic peak for", high_duration, "seconds until:", peak_start_time + high_duration)
                    while datetime.datetime.now() <= peak_start_time + high_duration:  # write ca. 30 to 60 lines / sec
                        milliseconds = float(random.randint(15, 30))
                        seconds = milliseconds / 1000.0
                        time.sleep(seconds)
                        line = generate_logline()+"\n"
                        file.write(line)
                        file.flush()
                        print(line)
            except KeyboardInterrupt:
                print("Log generation ended by user")
                go_on = False
    return 0

if __name__ == '__main__':
    main()