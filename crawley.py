#!/usr/bin/env python3
import os
import re
import sys
import time
import urllib3
import requests
import argparse
import threading
from datetime import datetime
from queue import Queue, Empty
from termcolor import colored
from bs4 import BeautifulSoup
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
DEFAULT_USER_AGENT = "Mozilla/5.0"
banner = """
	\r                          ▄▀▀▄ ▄▀▄   ▄▀█▀▀▀▄                             
	\r                         ▐  █ ▀  █  ▐  █   █                             
	\r                            █    █    █▀▀█▀                              
	\r                           ▐     ▐  ▄▀   ▐▄                              
	\r  ▄▀▄▄▄▄   ▄▀▀▄▀▀▀▄  ▄▀▀█▄   ▄▀▀▄    ▄▀▀▄  ▄▀▀▀▀▄     ▄▀▀█▄▄▄▄  ▄▀▀▄ ▀▀▄ 
	\r █ █    ▌ █   █   █ ▐ ▄▀ ▀▄ █   █    ▐  █ █    █     ▐  ▄▀   ▐ █   ▀▄ ▄▀ 
	\r ▐ █      ▐  █▀▀█▀    █▄▄▄█ ▐  █        █ ▐    █       █▄▄▄▄▄  ▐     █   
	\r   █       ▄▀    █   ▄▀   █   █   ▄    █      █        █    ▌        █   
	\r  ▄▀▄▄▄▄▀ █     █   █   ▄▀     ▀▄▀ ▀▄ ▄▀    ▄▀▄▄▄▄▄▄▀ ▄▀▄▄▄▄       ▄▀    
	\r █     ▐  ▐     ▐   ▐   ▐            ▀      █         █    ▐       █     
	\r ▐                                          ▐         ▐            ▐     
	\r ▐  ~ mr.crawley // by @t0nyc // v1.0.0 ~    ▐        ▐            ▐       
                                                      ▐"""
def printdbg(message, error_msg=False):
	if debug_messages or error_msg:
		print(colored(message, "red"))

class Crawley:

	def __init__(self, options):
		self.headers         = {}
		self.worker_loop     = True
		self.extracted_links = set()
		self.crawled         = set()
		self.queue           = Queue()
		self.headers_args    = options["headers"]
		self.threads         = options["threads"]
		self.base_url        = options["target_url"]
		self.proxy_args      = options["proxy_args"]
		self.user_agent      = options["user_agent"]
		self.output_file     = options["output_file"]
		self.sleep           = options["sleep"] / 1000

	def create_output(self):
		if not os.path.isfile(self.output_file):
			printdbg(f"[+] Saving results to {self.output_file}")
			with open(self.output_file, "w") as _:
				pass
		else:
			timestamp = datetime.now().strftime("%d_%m_%Y_%H-%M-%S")
			new_name = f"{timestamp}_{self.output_file}"
			printdbg(f"[!] {self.output_file} already exists, creating backup {new_name}")
			os.rename(self.output_file, new_name)
			with open(self.output_file, "w") as _:
				pass

	def create_headers(self):
		self.headers["User-Agent"] = self.user_agent
		for header in self.headers_args:
			key, value = header.split(":")
			self.headers[key] = value.strip()

	def create_proxy(self):
		if self.proxy_args:
			self.proxy = {"http":self.proxy_args, "https":self.proxy_args}
		else:
			self.proxy = self.proxy_args

	def print_and_save(self):
		print(self.url)
		if self.output_file:
			with open(self.output_file, "a") as save:
				save.write(f"{self.url}\n")

	def set_2_queue(self, ext_links):
		for link in ext_links:
			if not (link in self.crawled):
				self.crawled.add(link)
				if link.startswith(self.base_url):
					self.queue.put(link)
	
	def extract_links(self, html_contents):
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
				self.url = urljoin(self.base_url, link)
				if not self.url in self.crawled and self.url.startswith(self.base_url):
					self.print_and_save()
					ext_links.add(self.url)
		
		for attribute in link_tags:
			link = attribute.get("href")
			if link:
				self.url = urljoin(self.base_url, link)
				if not self.url in self.crawled and self.url.startswith(self.base_url):
					self.print_and_save()
					ext_links.add(self.url)

		for js in external_js:
			link = js.get("src")
			if link:
				self.url = urljoin(self.base_url, link)
				if not self.url in self.crawled and self.url.startswith(self.base_url):
					self.print_and_save()
					ext_links.add(self.url)

		for ejs in internal_js:
			pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
			urls = re.findall(pattern, ejs.string)
			for url in urls:
				self.url = urljoin(self.base_url, link)
				if not self.url in self.crawled and self.url.startswith(self.base_url):
					self.print_and_save()
					ext_links.add(self.url)

		self.set_2_queue(ext_links)
	
	def crawl_page(self, page_url):
		try:
			printdbg(f"[+] Requesting: {page_url}")
			time.sleep(self.sleep)
			response = requests.get(
				page_url, headers=self.headers, proxies=self.proxy, verify=False)
			self.crawled.add(page_url)
			self.extract_links(response.text)
		except requests.exceptions.ProxyError:
			proxy_error = f"Cannot connect to proxy {self.userProxy}"
			print(colored(proxy_error, "red"))
		except requests.exceptions.ConnectionError as err:
			print(colored(err, 'red'))
		except requests.exceptions.InvalidProxyURL:
			invalid_url_msg = f"Invalid proxy URL: \"{self.userProxy}\"."
			print(colored(invalid_url_msg, 'red'))
		except requests.exceptions.InvalidURL:
			invalid_url_msg = f"Invalid target URL: \"{page_url}\"."
			print(colored(invalid_url_msg, 'red'))
		except requests.exceptions.MissingSchema:
			invalid_url_msg = f"Invalid target URL: \"{page_url}\"."
			print(colored(invalid_url_msg, 'red'))
		except Exception as e:
			debug_messages = True
			printdbg(f"  - Can not crawl {page_url}")
			printdbg(f"[EXCEPTION]: {e}", True)

	def worker(self):
		try:
			while self.worker_loop:
				page_url = self.queue.get(block=False)
				self.crawl_page(page_url)
		except Empty:
			self.worker_loop = False

	def run(self):
		try:
			self.create_proxy()
			self.create_headers()
			if self.output_file:
				self.create_output()
			printdbg(f"[+] Booting first crawl for {self.base_url}")
			self.crawl_page(self.base_url)
			threads_list = []
			for _ in range(self.threads):
				crawler_thread = threading.Thread(target=self.worker)
				threads_list.append(crawler_thread)
				crawler_thread.daemon = True
				crawler_thread.start()
			for threads in threads_list:
				threads.join()
		except KeyboardInterrupt:
			printdbg(f"\r[+] Keyboard Interrupt detected. Exiting")
			self.worker_loop = False
			sys.exit()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		usage="./crawley.py -u <target url> [options]         ▐", add_help=False)
	parser.add_argument('-u', dest="target_url", type=str,
		help="target url to crawl (e.g. -u http://example.com)")
	parser.add_argument('-H', dest="headers", default=[], nargs="*", 
		help="headers to use (e.g. -H 'Header1: Value' 'Header2: value')")
	parser.add_argument('-t', dest='threads', type=int, default=5, 
		help="number of threads to use. default is 5 (e.g. -t 30)")
	parser.add_argument('-o', dest='output_file', type=str, 
		help='save results to a file (e.g. -o results.txt)')
	parser.add_argument('-a', dest='user_agent', default=DEFAULT_USER_AGENT, type=str, 
		help="use custom User-Agent string (e.g. -a \"MyUA /0.1\")")
	parser.add_argument('-s', dest="sleep", type=int, default=0, 
		help="milliseconds to wait before each request (e.g. -s 1000)")
	parser.add_argument('-p', dest="proxy_args", default=None,
		help="http proxy to use (e.g. -p 'http://127.0.0.1:8080')")
	parser.add_argument("-d", dest="debug_messages", action="store_true",
		help="enable verbose messages (default=false)")
	parser.add_argument("-h", "--help", action="store_true")
	arguments = parser.parse_args()

	if arguments.help:
		print(banner)
		parser.print_help()
	elif not arguments.target_url:
		print(colored("[+] A target url is required ( e.g. ./crawley.py -u http://example.com )", "red"))
		print(colored("[+] Run \"python3 crawley.py --help\" to get help", "red"))
	else:
		debug_messages = argparse.debug_messages
		options = vars(arguments)
		crawley = Crawley(options)
		printdbg("[+] Starting Crawley.run()")
		crawley.run()