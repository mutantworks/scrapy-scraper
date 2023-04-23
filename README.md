# Stackoverflow Data Scraper

> This repository contains python project to scrape data from (https://stackoverflow.com/).


## Table of Contents
- [Features](#Features)
- [Usage](#usage)
- [Maintainers](#maintainers)
- [License](#license)

## Features

> 1. Automated python standard Logging
> 2. Rotating Proxy configuration to secure IP
> 3. Data pipeline with SQLAlchemy
> 4. SqlLite data storage
> 5. Domain specific scraping with command line parameter 

## Usage

User can scrape data and store to SqlLite. User can scrap data according to domain. Refer below command to initiate crawler with specific domain scrapping. For example python as a domain provided here.

```sh
$ scrapy crawl stackoverflowspider -a domain=python 
# Prints out the standard-readme spec
```

## Maintainers

[@mutantworks](https://github.com/mutantworks).

## License

[MIT](LICENSE) © Meetkumar Charola