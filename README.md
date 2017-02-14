#HTTP Monitoring Application
----

##1. To do:

> **Create a simple console program that monitors HTTP traffic on your machine:**
> 
> - Consume an actively written-to w3c-formatted HTTP access log (https://en.wikipedia.org/wiki/Common_Log_Format)
> - Every 10s, display in the console the sections of the web site with the most hits (a section is defined as being what's before the second '/' in a URL. i.e. the section for "http://my.site.com/pages/create' is "http://my.site.com/pages"), as well as interesting summary statistics on the traffic as a whole.
> - Make sure a user can keep the console app running and monitor traffic on their machine
> - Whenever total traffic for the past 2 minutes exceeds a certain number on average, add a message saying that “High traffic generated an alert - hits = {value}, triggered at {time}”
> - Whenever the total traffic drops again below that value on average for the past 2 minutes, add another message detailing when the alert recovered
> - Make sure all messages showing when alerting thresholds are crossed remain visible on the page for historical reasons.
> - Write a test for the alerting logic
> - Explain how you’d improve on this application design

##2. Requirements

I have developped & tested the application with:

- Windows 10
- Python 3.6
- C. Gohlke's **curses** porting for windows platform, that you can download here: [http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses](http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses "Curses for Windows")
	- Choose and download the appropriate version for your machine
	- Go to download directory and do `pip install curses-{your-version}.whl`

This console application is untested on Linux

##3. Usage

1. There is a log creator that simulates a W3C formatted log file. Run it in a terminal window or IDE with: 

		python logcreator.py
It will print lines as they are written into the file

2. In another terminal window, run the monitor:

		usage: monitor.py [-h] [-s P_STATS] [-a P_ALERT] [-t T_ALERT]
		optional arguments:
		  -h, --help  show this help message and exit
		  -s P_STATS  monitoring period length in seconds (int)
		  -a P_ALERT  alert period length in seconds (int)
		  -t T_ALERT  alert treshold in hits/seconds (int)

##4. Tests

In the application directory:

	python -m unittest

##5. Potential improvements

On app features:

- Set a **main menu & a curses exit button** so that we do not have to mix standard I/O with curses
- Deliver **more insightful statistics**, especially as far as errors are concerned: which have been raised, trying to access to what and where.
- Ultimately, a **Window application** would be far better: a proper GUI would allow better data visualization + curses module quickly has limitations
- As it is, this console application only consider traffic to one server. It could monitor several


On code:

- Allow configuration of log creator
- **Cross platform test & optimization**: currently only optimized for Windows Powershell. e.g. I used curses to create a GUI in a console environment but couldn't handle console resize properly on Windows.
- Create **separate threads** for the log creator and the monitor, securing file I/O with a mutex



##6. Screenshot


![](http://i.imgur.com/ZxSPQrq.jpg)