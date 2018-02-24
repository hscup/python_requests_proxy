import logging
import random
import time
import requests
from requests.exceptions import (ChunkedEncodingError, ConnectionError,
                                 ReadTimeout, TooManyRedirects)

from proxy import Proxy
from useragent import UserAgent

__author__ = 'heyuno'
# Push back requests library to at least warnings
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-6s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)


class RequestProxy:
    def __init__(self, db_username, db_password, db_name, db_proxy_table,  db_host="127.0.0.1"):
        self.userAgent = UserAgent()
        self.proxyGetter = Proxy(db_username, db_password,
                                 db_host, db_name, db_proxy_table)
        self.proxy_list = []
        self.current_proxy = None
        self.proxy_time_start_used = 0
        self.logger = logging.getLogger()
        self.logger.addHandler(handler)
        self.logger.setLevel(0)

    def generate_random_request_headers(self):
        headers = {
            "Connection": "close",  # another way to cover tracks
            "User-Agent": self.userAgent.generate_random_user_agent()
        }  # select a random user agent
        return headers

    def get_random_proxy_list(self):
        return self.proxyGetter.query_random_proxy()

    def generate_proxied_requests(self, url, method="GET", req_timeout=20):
        headers = self.generate_random_request_headers()
        if not self.proxy_list:
            self.proxy_list = self.get_random_proxy_list()
        if not self.proxy_list:
            raise Exception("No proxy list")
        if not self.current_proxy:
            self.current_proxy = self.randomize_proxy()
        elif (time.time() - self.proxy_time_start_used) > 600:
            # Change proxy for every 10 minutes
            self.current_proxy = self.randomize_proxy()
        proxies = {
            "http": "http://{}".format(self.current_proxy),
            "https": "https://{}".format(self.current_proxy)
        }

        try:
            request = requests.request(
                url=url, method=method, headers=headers, proxies=proxies, timeout=req_timeout)
            # Avoid HTTP request errors
            if request.status_code == 409:
                raise ConnectionError(
                    "HTTP Response [409] - Possible Cloudflare DNS resolution error")
            elif request.status_code == 403:
                raise ConnectionError(
                    "HTTP Response [403] - Permission denied error")
            elif request.status_code == 503:
                raise ConnectionError(
                    "HTTP Response [503] - Service unavailable error")
            print('RR Status {}'.format(request.status_code))
            return request
        except ConnectionError:
            try:
                self.proxy_list.remove(self.current_proxy)
            except ValueError:
                pass
            self.logger.debug("Proxy unreachable - Removed Straggling proxy: {0} PL Size = {1}".format(
                self.current_proxy, len(self.proxy_list)))
            self.randomize_proxy()
        except ReadTimeout:
            try:
                self.proxy_list.remove(self.current_proxy)
            except ValueError:
                pass
            self.logger.debug("Read timed out - Removed Straggling proxy: {0} PL Size = {1}".format(
                self.current_proxy, len(self.proxy_list)))
            self.randomize_proxy()
        except ChunkedEncodingError:
            try:
                self.proxy_list.remove(self.current_proxy)
            except ValueError:
                pass
            self.logger.debug("Wrong server chunked encoding - Removed Straggling proxy: {0} PL Size = {1}".format(
                self.current_proxy, len(self.proxy_list)))
            self.randomize_proxy()
        except TooManyRedirects:
            try:
                self.proxy_list.remove(self.current_proxy)
            except ValueError:
                pass
            self.logger.debug("Too many redirects - Removed Straggling proxy: {0} PL Size = {1}".format(
                self.current_proxy, len(self.proxy_list)))
            self.randomize_proxy()

    def randomize_proxy(self):
        if len(self.proxy_list) == 0:
            raise Exception("list is empty")
        rand_proxy = random.choice(self.proxy_list)
        while not rand_proxy:
            rand_proxy = random.choice(self.proxy_list)
        self.current_proxy = rand_proxy
        self.proxy_time_start_used = time.time()
        return rand_proxy


if __name__ == "__main__":
    customRequests = RequestProxy("root", "secret", "testdb", "proxies")
    r = None
    while not r:
        try:
            r = customRequests.generate_proxied_requests(
            "https://edition.cnn.com/")
        except Exception as ex:
            print(ex)

    if r:
        print(r.text)
