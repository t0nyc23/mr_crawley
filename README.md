# Mr. Crawley
---
Simple threaded static web crawler in python3

### Options
```
usage: crawley.py [-h] -u TARGET_URL [-t THREADS] [-a USER_AGENT] [-d]
                  [-s SLEEP]

options:
  -h, --help            show this help message and exit
  -u TARGET_URL         target base url to crawl (e.g. -u
                        https://example.com/)
  -t THREADS            number of threads to run (default=4) (e.g. -t 23)
  -a USER_AGENT         set a custom User-Agent string (e.g. -a 'MyUA/0.1')
  -d                    enable debug messages (default=false)
  -s SLEEP, --sleep SLEEP
                        milliseconds to sleep before a request (e.g. -s 200)
                        (default is 600)
```