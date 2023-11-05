#!/usr/bin/env python3
import re
import sys
import requests
from bs4 import BeautifulSoup

def is_valid_url(target_url):
	scheme = re.compile("^https?://[a-z 0-9]")
	is_valid = scheme.match(target_url)
	if not is_valid:
		return False
	return True

def do_get(target_url):
	try:
		if is_valid_url(target_url):
			# maybe add headers for stealth
			response = requests.get(target_url)
			html_contents = response.text
			return html_contents
		else:
			print(f"[!] Not valid url scheme: {target_url}")
	except requests.exceptions.ConnectionError:
		print(f"[+] Failed to establish a new connection to [{target_url}]: Name or service not known")
	
	return False

def clean_link(link):
	scheme = link.split("//")[0] + "//"
	link_cleaned = scheme + link.replace(scheme, "").replace("//", "/")
	return link_cleaned

def print_links(html_contents, target_url):
	scoped_urls = []
	soup = BeautifulSoup(html_contents, "html.parser")
	links_extracted = soup.find_all('a')
	for link in links_extracted:
		try:
			link_href = link["href"]
			if not is_valid_url(link_href):
				link_href = clean_link(f"{target_url}{link_href}")
			if link_href.startswith(target_url):
				scoped_urls.append(link_href)
			print(link_href)
		except KeyError:
			continue

	return scoped_urls

if __name__ == "__main__":
	if not(len(sys.argv) == 2):
		print("[!] Make sure to provide a target url.")
		print(f"[!] Example: {sys.argv[0]} https://target.com")
	else:
		target_url = sys.argv[1]
		print(f"[+] Starting crawl on {target_url}")
		html_contents = do_get(target_url)
		if html_contents:
			print(f"[+] Printing gathered links...\n------")
			scoped_urls = print_links(html_contents, target_url)
			print("-------\n[+] Scoped urls following:")
			for scoped in scoped_urls:
				print(scoped)
