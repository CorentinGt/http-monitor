import unittest
import datastruct as dt


class AlertTest(unittest.TestCase):
    """
    test case for alerting logic
    """
    def setUp(self):
        self.datastruct = dt.Datastruct(10, 120) # set up a data structure, periods don't matter

    def test_compute_alert1(self):
        """
        Tests if {no alert --> alert} change of state raises status 1 and put on_alert at True
        """
        for i in range(12):  # range( 120 // 10 )
            self.datastruct.hist_traffic.append(400)  # fill datastruct so that hit debit (per sec) on alert period = 40
        on_alert, alert_info = self.datastruct.compute_alert(20, False)  # we were not on_alert but we are now
        self.assertTrue(on_alert)
        self.assertEqual(alert_info["status_code"], 1)

    def test_compute_alert2(self):
        """
        Tests if {alert --> no alert} change of state raises status 0 and put on_alert at False
        """
        for i in range(12):
            self.datastruct.hist_traffic.append(100) # fill datastruct so that hit debit on alert period = 10
        on_alert, alert_info = self.datastruct.compute_alert(20, True) # we were on_alert but we have recovered
        self.assertFalse(on_alert)
        self.assertEqual(alert_info["status_code"], 0)

    def test_compute_alert3(self):
        """
        Tests if {alert --> alert} change of state (i.e. no change of state) raises status 2 and preserves
        on_alert = True
        """
        for i in range(12):
            self.datastruct.hist_traffic.append(400) # fill datastruct so that hit debit on alert period = 40
        on_alert, alert_info = self.datastruct.compute_alert(20, True) # we were on_alert and still are
        self.assertTrue(on_alert)
        self.assertEqual(alert_info["status_code"], 2)

    def test_compute_alert4(self):
        """
        Tests if {no alert --> no alert} change of state (i.e. no change of state) raises status 2 and preserves
        on_alert = False
        """
        for i in range(12):
            self.datastruct.hist_traffic.append(100)
        on_alert, alert_info = self.datastruct.compute_alert(20, False)
        self.assertFalse(on_alert)
        self.assertEqual(alert_info["status_code"], 2)