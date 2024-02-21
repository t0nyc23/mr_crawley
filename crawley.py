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
import urllib3
from termcolor import colored
from time import sleep
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def save_results(contents):
	with open("results3.txt", "a") as f:
		f.write(f"{contents}\n")	

def printdbg(message, error_msg=False):
	if debug_messages or error_msg:
		print(colored(message, "red"))

class Crawley:

	def __init__(self, opts):
		self.threads         = opts["threads"]
		self.base_url        = opts["target_url"]
		self.user_agent      = opts["user_agent"]
		self.sleep           = opts["sleep"] / 1000
		self.headers         = {}
		self.extracted_links = set()
		self.crawled         = set()
		self.queue           = Queue()
		self.worker_loop     = True

		self.headers['User-Agent'] = self.user_agent
		printdbg(f"[+] Booting first crawl for {self.base_url}")
		self.crawl_page(self.base_url)

	def set_2_queue(self, ext_links):
		for link in ext_links:
			if not (link in self.crawled):
				self.crawled.add(link)
				if link.startswith(self.base_url):
					self.queue.put(link)

	def crawl_page(self, page_url):
		try:
			printdbg(f"[+] Requesting: {page_url}")
			sleep(self.sleep)
			response = requests.get(page_url, headers=self.headers, verify=False)
			self.crawled.add(page_url)
			self.extract_links(response.text, page_url)
		except Exception as e:
			debug_messages = True
			printdbg(f"  - Can not crawl {page_url}")
			printdbg(f"[EXCEPTION]: {e}", True)
	
	def extract_links(self, html_contents, base_url):
		ext_links = set()
		soup = BeautifulSoup(html_contents, "html.parser")
		a_tags = soup.find_all("a")
		link_tags = soup.find_all("link")
		all_script_tags = soup.find_all("script")
		internal_js = list(filter(lambda script: not script.has_attr("src"), all_script_tags))
		external_js = list(filter(lambda script:script.has_attr("src"), all_script_tags))		
		
		for attr in a_tags:
			link = attr.get("href")
			if link:
				url = urljoin(self.base_url, link)
				if not url in self.crawled and url.startswith(self.base_url):
					print(colored(f"[html] {url}", "green"))
					save_results(url)
					ext_links.add(url)
		
		for attribute in link_tags:
			link = attribute.get("href")
			if link:
				url = urljoin(self.base_url, link)
				if not url in self.crawled and url.startswith(self.base_url):
					print(colored(f"[link_tags] {url}", "green"))
					save_results(url)
					ext_links.add(url)

		for js in external_js:
			link = js.get("src")
			if link:
				url = urljoin(self.base_url, link)
				if not url in self.crawled and url.startswith(self.base_url):
					print(colored(f"[js_tags] {url}", "cyan"))	
					save_results(url)
					ext_links.add(url)

		for ejs in internal_js:
			pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
			urls = re.findall(pattern, ejs.string)
			for url in urls:
				if not url in self.crawled and url.startswith(self.base_url):
					print(colored(f"[JSsource] {url}", "yellow"))
					save_results(url)
					ext_links.add(url)

		self.set_2_queue(ext_links)

	def worker(self):
		while self.worker_loop:
			if self.queue.empty():
				printdbg("[+] Empty Queue")
				self.worker_loop = False
			else:
				page_url = self.queue.get()
				self.crawl_page(page_url)

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

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-u", dest="target_url", required=True, type=str,
		help="target base url to crawl (e.g. -u https://example.com/)")
	parser.add_argument("-t", dest="threads", type=int, default=4,
		help="number of threads to run (default=4) (e.g. -t 23)")
	parser.add_argument("-a", dest="user_agent", default="Mozilla/5.0", type=str,
		help="set a custom User-Agent string (e.g. -a 'MyUA/0.1')")
	parser.add_argument("-d", dest="debug_messages", action="store_true",
		help="enable debug messages (default=false)")
	parser.add_argument("-s", "--sleep", dest="sleep", type=int, default=600,
		help="milliseconds to sleep before a request (e.g. -s 200) (default is 600)")
	args = parser.parse_args()
	opts = vars(args)
	debug_messages = opts["debug_messages"]
	crawley = Crawley(opts)
	printdbg("[+] Starting Crawley.run()")
	crawley.run()