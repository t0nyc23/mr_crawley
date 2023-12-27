#!/usr/bin/env python3
import os
import re
import sys
import requests
import argparse
import threading
from queue import Queue
from bs4 import BeautifulSoup
from requests.compat import urljoin
from urllib.parse import urlparse
from termcolor import colored

class Crawley:

	def __init__(self, opts):
		self.threads         = opts["threads"]
		self.base_url        = opts["target_url"]
		self.user_agent      = opts["user_agent"]
		self.extracted_links = set()
		self.queue           = Queue()
		self.scope           = get_domain_name(self.base_url)
		self.worker_loop     = True

		if self.user_agent == "default":
			self.user_agent = "Mozilla/5.0"
		
		self.headers = {"User-Agent":self.user_agent}

		printdbg(f"[+] Booting first crawl for {self.base_url}")
		printdbg(f"[+] Scope is: {self.scope}")
		self.crawl_page(self.base_url)
		self.set_2_queue()

	def set_2_queue(self):
		for link in self.extracted_links:
			if is_valid_url(link):
				self.queue.put(link)

	def crawl_page(self, page_url):
		try:
			if is_in_scope(page_url, self.scope):
				printdbg(f"[+] Requesting url: {page_url}")
				response = requests.get(page_url, headers=self.headers)
				if "text/html" in response.headers["content-type"]:
					self.extract_links(response.text, page_url)
			else:
				printdbg(f"[+] {page_url} not in scope")
		except Exception as e:
			printdbg(f"[+] Can not crawl {page_url}")
			printdbg(f"[EXCEPTION]: {e}")
	
	def extract_links(self, html_contents, base_url):
		self.extracted_links.clear()
		soup = BeautifulSoup(html_contents, "html.parser")
		a_tags = soup.find_all("a")
		for attr in a_tags:
			link = attr.get("href")
			if not link:
				printdbg(f"[+] Invalid url: {str(link)}")
				continue
			url = urljoin(self.base_url, link)
			if is_valid_url(url) and self.worker_loop:
				print(url)
			if is_in_scope(url, self.scope):
				self.extracted_links.add(url)

	def worker(self):
		while self.worker_loop:
			if self.queue.empty():
				printdbg("[+] Empty Queue")
				self.worker_loop = False
			else:
				page_url = self.queue.get()
				self.crawl_page(page_url)
				self.set_2_queue()

	def run(self):
		try:
			thread_list = []
			for _ in range(self.threads):
				crawler_thread = threading.Thread(target=self.worker)
				thread_list.append(crawler_thread)
				crawler_thread.daemon = True
				crawler_thread.start()
			
			for thr in thread_list:
				thr.join()

		except KeyboardInterrupt:
			self.worker_loop = False
			printdbg(f"\r[+] Keyboard Interrupt detected. Exiting")
			sys.exit()


def printdbg(message):
	if debug_messages:
		print(colored(message, "red"))

def get_domain_name(url):
	results = urlparse(url).netloc
	results =  results.split(".")
	return results[-2] + "." + results[-1]

def is_in_scope(page_url, scope_domain):
	pattern = re.compile(r"https?://(?:\w+\.)?" + re.escape(scope_domain) + r"/?.*")
	return bool(pattern.match(page_url))

def is_valid_url(url):
	scheme = re.compile("^https?://[a-z 0-9]")
	return bool(scheme.match(url))

if __name__ == "__main__":
	try:
		parser = argparse.ArgumentParser()
		parser.add_argument("target_url", type=str, help="Target url to crawl")
		parser.add_argument("-t", dest="threads", type=int, default=4, help="Number of threads to run (default=4)")
		parser.add_argument("-a", dest="user_agent", default="default", type=str, help="Set a custom User-Agent string")
		parser.add_argument("-d", dest="debug_messages", action="store_true", help="Show debug messages (default=false)")
		args = parser.parse_args()
		opts = vars(args)
		debug_messages = opts["debug_messages"]
		crawley = Crawley(opts)
		printdbg("[+] Starting Crawley.run()")
		crawley.run()
	except KeyboardInterrupt:
		printdbg(f"\r[+] Keyboard Interrupt detected. Exiting")
		sys.exit()
		