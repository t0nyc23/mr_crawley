# Mr.Crawley
---
Simple threaded static web crawler in python3

### Install Requirements (Debian based distributions)
```
sudo apt -y install python3-{requests,bs4,termcolor}
```

### Install and run mr.crawley

```
git clone https://github.com/t0nyc23/mr_crawley
cd mr_crawley && chmod +x crawley.py
./crawley.py -u http://example.com
```

### Usage examples

1. Setting threads and sleep time
```
./crawley.py -u http://example.site -t 20 -s 1000
```

2. Custom headers and User-Agent
```
./crawley.py -u http://example.site -H "Custom-Header: CustomValue"
./crawley.py -u http://example.site -a "MyCustomUserAgent/1.0"
```

3. Use proxy and save results to a file
```
./crawley.py -u http://example.site -p http://127.0.0.1:8080 -o crawley_results.txt
```

### Available Options

```
-u TARGET_URL     target url to crawl (e.g. -u http://example.com)

-H [HEADERS ...]  headers to use (e.g. -H 'Header1: Value' 'Header2: value')

-t THREADS        number of threads to use. default is 5 (e.g. -t 30)

-o OUTPUT_FILE    save results to a file (e.g. -o results.txt)

-a USER_AGENT     use custom User-Agent string (e.g. -a "MyUA /0.1")

-s SLEEP          milliseconds to wait before each request (e.g. -s 1000)

-p PROXY_ARGS     http proxy to use (e.g. -p 'http://127.0.0.1:8080')

-d                enable verbose messages (default=false)

-h, --help
```