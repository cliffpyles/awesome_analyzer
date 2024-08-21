# Awesome Analyzer

`awesome_analyzer` is a Python project designed to ingest and analyze GitHub repository data from (awesome lists)[https://github.com/sindresorhus/awesome].

These repositories serve as catalogs for resources within various communities, and this project allows you to gather and analyze popularity metrics (stars, forks, watchers) for the resources listed in these lists.

## Prerequisites

- Python 3.x
- Pipenv for managing dependencies
- GitHub CLI (`gh`) for authenticated requests (optional)

## Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd awesome_analyzer
   ```

2. Install dependencies using Pipenv:

   ```bash
   pipenv install
   ```

3. Activate the Pipenv shell:

   ```bash
   pipenv shell
   ```

## Usage

### 1. `awesome_scraper.py`

This script scrapes GitHub repository links from an "Awesome `<TopicName>`" webpage and retrieves their popularity metrics.

#### Example:

```bash
./awesome_scraper.py https://github.com/vinta/awesome-python
```

#### Options:

- `--output`: Specify the output JSON file. If not provided, the script generates a file path based on the URL.
- `--max-failures`: Maximum number of consecutive failures allowed before the script exits. Default is 5.

#### Authentication:

The script attempts to use authenticated requests via the GitHub CLI (`gh`). If the CLI is installed and the user is authenticated, the script uses the token for higher rate limits. If not, the script falls back to unauthenticated requests.

### 2. `awesome_analyzer.py`

This script analyzes the data ingested by `awesome_scraper.py`, allowing users to sort and filter repositories based on various metrics.

#### Example:

```bash
./awesome_analyzer.py output.json
```

#### Options:

- `--sort-by`: Sort the data by `stars`, `forks`, or `watchers`. Default is `stars`.
- `--ascending`: Sort in ascending order. By default, the data is sorted in descending order.
- `--min-stars`: Filter by a minimum number of stars.
- `--max-stars`: Filter by a maximum number of stars.
- `--min-forks`: Filter by a minimum number of forks.
- `--max-forks`: Filter by a maximum number of forks.
- `--min-watchers`: Filter by a minimum number of watchers.
- `--max-watchers`: Filter by a maximum number of watchers.

#### Example Usage:

1. **Basic Usage:**

   ```bash
   ./awesome_analyzer.py output.json
   ```

   This command sorts the data by stars in descending order by default.

2. **Sort by Forks in Ascending Order:**

   ```bash
   ./awesome_analyzer.py output.json --sort-by forks --ascending
   ```

   This command sorts the data by forks in ascending order.

3. **Filter and Sort Combined:**

   ```bash
   ./awesome_analyzer.py output.json --min-stars 100 --max-forks 500 --sort-by watchers
   ```

   This command filters the data to include only repositories with at least 100 stars and no more than 500 forks, sorted by watchers in descending order.

## Example Workflow

1. **Ingest Data from an "Awesome" Repository:**

   For example, to ingest data from the [awesome-nodejs](https://github.com/sindresorhus/awesome-nodejs) repository:

   ```bash
   ./awesome_scraper.py https://github.com/sindresorhus/awesome-nodejs
   ```

   This will scrape GitHub repository links from the page and store their popularity metrics in a JSON file.

2. **Analyze the Ingested Data:**

   After scraping the data, analyze it using `awesome_analyzer.py`:

   ```bash
   ./awesome_analyzer.py ./github.com/sindresorhus/awesome-nodejs.json
   ```

   This will display the data, sorted by stars in descending order by default.

## Project Structure

```
awesome_analyzer/
├── awesome_scraper.py     # Script to scrape GitHub data
├── awesome_analyzer.py    # Script to analyze the scraped data
├── Pipfile                # Pipenv dependencies
├── Pipfile.lock           # Pipenv lock file
└── README.md              # Project documentation
```

## Contributing

Contributions are welcome! Please submit a pull request or open an issue if you have suggestions or find bugs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
