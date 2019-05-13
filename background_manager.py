import time
import logging
import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from requests.exceptions import Timeout
from gi.repository import Notify

from api_protocol import NightscoutCommunicationException
from nightscout import Nightscout

class Manager:
    def __init__(self, nightscout_url, background_location, lockscreen_location):
        self.nightscout = Nightscout(nightscout_url)
        self.background = background_location
        self.lockscreen = lockscreen_location
        self.entries = list()
        self.resolution = (1920, 1080)
        self.dpi = 96
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
        num_of_entries = 6
        last_time = datetime.datetime.fromtimestamp(self.entries[-1].get('date') / 1000).strftime('%H:%M')
        label_text = '{bg} - {time}'.format(bg=round(self.entries[-1].get('sgv', 0) / 18, 1), time=last_time)
        body_text = ' --> '.join([str(round(entry.get('sgv', 0) / 18, 1)) for entry in self.entries[-(min(num_of_entries, len(self.entries))):]])
        self.notification.update(label_text, body_text)
        self.notification.show()

    def generate_files(self):
        logging.debug('generating files')

        bgs = [(int(item['sgv']) / 18) for item in self.entries if item.get('sgv') and item.get('date')]
        datetimes = [datetime.datetime.fromtimestamp(item['date'] / 1000).strftime('%H:%M') for item in self.entries if item.get('sgv') and item.get('date')]

        fig = plt.figure(figsize=(self.resolution[0] / self.dpi, self.resolution[1] / self.dpi), dpi=self.dpi)
        plt.style.use('dark_background')
        ax = fig.add_subplot(111)
        ax.yaxis.tick_right()
        plt.plot(datetimes, bgs, 'o')
        plt.ylim(bottom=0)
        plt.ylim(top=13)
        fig.savefig(self.lockscreen)
        plt.close(fig)

    def get_sleep_time(self):
        waiting_period = 315
        last_timestamp = self.entries[-1].get('date') / 1000
        now_timestamp = int(time.time())
        sleep_time = waiting_period - (now_timestamp - last_timestamp)
        return sleep_time

    def run(self, update_interval=100):
        while True:
            try:
                if self.update_entries():
                    self.update_and_show_notification()
                    self.generate_files()
                    sleep_time = self.get_sleep_time()
                    logging.debug('sleeping for {} seconds'.format(sleep_time))
                    time.sleep(sleep_time)
                else:
                    time.sleep(20)
            except (Timeout, NightscoutCommunicationException):
                logging.error('Connection error', exc_info=True)
                time.sleep(10)


if __name__ == '__main__':
    logging.basicConfig(filename='log', filemode='a', format='%(asctime)s - %(message)s', level=logging.DEBUG)
    man = Manager('http://gotrade.ml:8088', '/usr/share/backgrounds/warty-final-ubuntu.png', '/usr/share/backgrounds/warty-final-ubuntu.png')
    man.run(50)
