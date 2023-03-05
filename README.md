# CNKI Crawler

This is a Python-based crawler for CNKI (China National Knowledge Infrastructure) that utilizes Selenium to extract a paper's title, link, date, abstract, keywords, and generates a corresponding author-department dictionary. 

## Requirements

To use this crawler, you need to have the following installed on your system:

- Python 3.x
- Selenium 
- ChromeDriver (compatible with your Chrome browser version)

## Installation

1. Clone this repository: `git clone https://github.com/thousandyoung/cnki-crawler.git`
2. Navigate to the project directory: `cd cnki-crawler`
3. Install the required packages: `pip install -r requirements.txt`

## Usage

1. Navigate to the project directory: `cd cnki-crawler`
2. Run the script: `python cnki_crawler.py`
3. Enter the search keyword when prompted.
4. The script will generate a CSV file with the extracted data.

## Output

The output of this crawler will be a CSV file with the following columns:

- Title
- Link
- Date
- Abstract
- Keywords
- Corresponding Author
- Department

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improving the code, please submit a pull request or open an issue.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
