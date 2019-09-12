# custom-mint-categorizer
Maps Inuit Mint's Required Categories to Custom Categories

## Using the Script

Get Exported CSV from Mint:

* Log into inuit Mint
* Transactions Tab
* Scroll to bottom right
* Export all transactions to csv

Create A Custom Mapping:

* Modify example/config.yaml with your custom categories as keys.
* For each custom category key, specify the list of mint categories/descriptions values that should be mapped to it.

## Usage

```
usage: mint_to_personal_categories.py [-h] [--input INPUT] [--conf CONF]
                                      [--mint MINT] [--verbose]
                                      [--output OUTPUT]
                                      [--output-totals OUTPUT_TOTALS]

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        exported csv of transactions from mint
  --conf CONF, -c CONF  yaml file mapping personal categories to mint
                        categories/descriptions
  --mint MINT, -m MINT  Mint categories to descriptions mapping
  --verbose, -v         verbose logging
  --output OUTPUT, -o OUTPUT
                        output filename for new transaction csv
  --output-totals OUTPUT_TOTALS, -O OUTPUT_TOTALS
                        output filename for total transactions by personal
                        category
```

## Example Usage

```
python3 lib/mint_to_personal_categories.py -i example/exported_transactions.csv -c example/config.yaml -o output_transactions.csv -O output_totals.csv
```