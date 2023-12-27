# Mr. Crawley
---
Simple threaded web crawler in python3
###### Usage
`crawley.py -h -t THREADS -a USER_AGENT -d  target_url`
###### Options
`target_url`             Target url to crawl
  `-h, --help`           Show this help message and exit
  `-t THREADS `         Number of threads to run (default=4)
  `-a USER_AGENT`     Set a custom User-Agent string
  `-d`                            Show debug messages (default=false)
###### Example
`python3 crawley.py http://example.com -t 6 -a "Mozilla/5.0" | tee crawley.out`
