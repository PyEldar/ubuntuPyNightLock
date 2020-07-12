import time
import logging
import sys
import datetime
from collections import deque

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from gi.repository import Notify

from config import display as display_conf
from config import manager as manager_conf
from config import plot as plot_conf
from api_protocol import NightscoutCommunicationException
from nightscout import Nightscout

class Manager:
    def __init__(self):
        self.nightscout = Nightscout()
        self.background = manager_conf.get('background_path')
        self.lockscreen = manager_conf.get('lockscreen_path')
        self.resolution = (int(display_conf.get('width_px')), int(display_conf.get('height_px')))
        self.dpi = int(display_conf.get('dpi'))
        self.entries = deque(maxlen=int(manager_conf.get('entries_num')))

        Notify.init('background_manager')
        self.notification = Notify.Notification.new('Waiting for data')

    def update_entries(self):
        logging.debug('updatine entries')
        last_entry = self.entries[-1].get('date') if self.entries else None
        new_entries = sorted(self.nightscout.get_entries_since(timestamp=last_entry, entry_type='sgv'), key=lambda k: k['date'])
        logging.debug('got {} new entries'.format(len(new_entries)))
        self.entries.extend(new_entries)
        return len(new_entries)

    def update_and_show_notification(self):
        num_of_entries = int(manager_conf.get('entries_in_notification'))
        last_time = datetime.datetime.fromtimestamp(self.entries[-1].get('date') / 1000).strftime('%H:%M')
        label_text = '{bg} - {time}'.format(bg=round(self.entries[-1].get('sgv', 0) / 18, 1), time=last_time)
        body_text = ' --> '.join([str(round(entry.get('sgv', 0) / 18, 1)) for entry in list(self.entries)[-(min(num_of_entries, len(self.entries))):]])
        self.notification.update(label_text, body_text)
        self.notification.show()

    def generate_data(self):
        logging.debug('generating data')
        bgs = [(int(item['sgv']) / 18) for item in self.entries if item.get('sgv') and item.get('date')]
        datetimes = [datetime.datetime.fromtimestamp(item['date'] / 1000) for item in self.entries if item.get('sgv') and item.get('date')]
        # self._fill_missing_readings(datetimes, bgs)
        times = [date.strftime("%H:%M") for date in datetimes]
        self.create_and_save_figure(times, bgs)

    def _fill_missing_readings(self, datetimes, bgs):
        max_no_reading_time = datetime.timedelta(seconds=350)
        diffs_between_readings = {i: t - s for i, (s, t) in enumerate(zip(datetimes, datetimes[1:])) if (t - s) > max_no_reading_time}
        additional_adjustments = 0
        for i, (index, time_diff) in enumerate(diffs_between_readings.items()):
            final_index = index + i + additional_adjustments
            if time_diff > max_no_reading_time * 2:
                for x in range(1, 4):
                    datetimes.insert(index + i, datetimes[final_index] + datetime.timedelta(seconds=300 * x))
                    bgs.insert(final_index, 0)
                    additional_adjustments += 2
            elif time_diff > max_no_reading_time * 2:
                for x in range(1, 3):
                    datetimes.insert(index + i, datetimes[final_index] + datetime.timedelta(seconds=300 * x))
                    bgs.insert(final_index, 0)
                    additional_adjustments += 1
            else:
                datetimes.insert(final_index, datetimes[final_index] + datetime.timedelta(seconds=300))
                bgs.insert(final_index, 0)

    def create_and_save_figure(self, datetimes, bgs):
        fig = plt.figure(figsize=(self.resolution[0] / self.dpi, self.resolution[1] / self.dpi), dpi=self.dpi)
        plt.style.use('dark_background')
        ax = fig.add_subplot(111)
        ax.yaxis.tick_right()
        ax.tick_params(axis='y', labelsize=plot_conf.get('bg_label_size'))
        plt.gcf().autofmt_xdate()
        plt.plot(datetimes, bgs, 'o')
        plt.ylim(bottom=0)
        plt.ylim(top=max(12, max(bgs)))
        fig.savefig(self.lockscreen)
        plt.close(fig)

    def get_sleep_time(self):
        waiting_period = int(manager_conf.get('default_sleep_time'))
        last_timestamp = self.entries[-1].get('date') / 1000
        now_timestamp = int(time.time())
        sleep_time = waiting_period - (now_timestamp - last_timestamp)
        return sleep_time if sleep_time > 0 else waiting_period

    def run(self):
        while True:
            try:
                if self.update_entries():
                    self.update_and_show_notification()
                    self.generate_data()
                    sleep_time = self.get_sleep_time()
                    logging.debug('sleeping for {} seconds'.format(sleep_time))
                    time.sleep(sleep_time)
                else:
                    time.sleep(20)
            except NightscoutCommunicationException as ex:
                logging.error('Connection error: {}'.format(ex))
                time.sleep(10)


def logger_setup():
    logging.basicConfig(filename='log', filemode='a', format='%(asctime)s - %(message)s', level=logging.DEBUG)


if __name__ == '__main__':
    logger_setup()
    man = Manager()
    man.run()
