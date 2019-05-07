import time
import logging

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from requests.exceptions import Timeout

from api_protocol import NightscoutCommunicationException
from nightscout import Nightscout

class Manager:
    def __init__(self, nightscout_url, background_location, lockscreen_location):
        self.nightscout = Nightscout(nightscout_url)
        self.background = background_location
        self.lockscreen = lockscreen_location
        self.entries = list()

    def update_entries(self):
        logging.info('updatine entries')
        last_entry = self.entries[-1].get('date') if self.entries else None
        new_entries = sorted(self.nightscout.get_entries_since(timestamp=last_entry), key=lambda k: k['date'])
        logging.debug('got {} new entries'.format(len(new_entries)))
        self.entries.extend(new_entries)

    def generate_files(self):
        logging.info('generating files')
        fig = plt.figure(figsize=(1920/96, 1080/96), dpi=96)
        plt.style.use('dark_background')
        ax = fig.add_subplot(111)
        ax.yaxis.tick_right()
        plt.plot([item['dateString'] for item in self.entries], [(int(item['sgv']) / 18) for item in self.entries], 'o')
        plt.ylim(bottom=0)
        plt.ylim(top=13)
        fig.savefig(self.lockscreen)
        plt.close(fig)

    def run(self, update_interval=100):
        while True:
            try:
                self.update_entries()
            except (Timeout, NightscoutCommunicationException):
                logging.error('Connection error', exc_info=True)
                time.sleep(10)
                continue
            self.generate_files()
            logging.info('sleeping for {} seconds'.format(update_interval))
            time.sleep(update_interval)


if __name__ == '__main__':
    logging.basicConfig(filename='log', format='%(asctime)s - %(message)s')
    man = Manager('http://gotrade.ml:8088', '/usr/share/backgrounds/warty-final-ubuntu.png', '/usr/share/backgrounds/warty-final-ubuntu.png')
    man.run(30)
