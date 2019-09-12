import argparse
import csv
import logging
import pprint

import pandas as pd
import yaml

MINT_CATEGORY_TO_DESCRIPTIONS = {'auto & transport': set(['auto insurance', 'auto payment', 'gas & fuel', 'parking', 'public transportation', 'service & parts']),
                                   'bills & utilities': set(['home phone', 'internet', 'mobile phone', 'television', 'utilities']),
                                   'business services': set(['advertising', 'legal', 'office supplies', 'printing', 'shipping']),
                                   'education': set(['books & supplies', 'student loan', 'tuition']),
                                   'entertainment': set(['amusement', 'arts', 'music', 'movies & dvds', 'newspaper & magazines']),
                                   'fees & charges': set(['atm fee', 'bank fee', 'finance charge', 'late fee', 'service fee', 'trade commissions']),
                                   'financial': set(['financial advisor', 'life insurance']),
                                   'food & dining': set(['alcohol & bars', 'coffee shops', 'fast food', 'groceries', 'restaurants']),
                                   'gifts & donations': set(['charity', 'gift']),
                                   'health & fitness': set(['dentist', 'doctor', 'eyecare', 'gym', 'health insurance', 'pharmacy', 'sports']),
                                   'home': set(['furnishings', 'home improvement', 'home insurance', 'home services', 'home supplies', 'lawn & garden', 'mortgage & rent']),
                                   'income': set(['bonus', 'paycheck', 'returned purchase', 'interest income', 'reimbursement', 'rental income']),
                                   'investments': set(['buy', 'deposit', 'dividend & cap gains', 'sell', 'withdrawal']),
                                   'kids': set(['allowance', 'baby supplies', 'babysitter & daycare', 'child support', 'kids activities', 'toys']),
                                   'loans': set(['loan fees and charges', 'loan insurance', 'loan interest', 'loan payment', 'loan principal']),
                                   'misc expenses': set([]),
                                   'personal care': set(['hair', 'laundry', 'spa & massage']),
                                   'pets': set(['pet food & supplies', 'pet grooming', 'veterinary']),
                                   'shopping': set(['books', 'clothing', 'electronics & software', 'hobbies', 'sporting goods']),
                                   'taxes': set(['federal tax', 'local tax', 'property tax', 'sales tax', 'state tax']),
                                   'transfer': set(['credit card payment', 'transfer for cash spending']),
                                   'travel': set(['air travel', 'hotel', 'rental car & taxi', 'vacation']),
                                   'uncategorized': set(['cash & atm', 'check'])}

def get_settings():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='exported csv of transactions from mint')
    parser.add_argument('--conf', '-c', help='yaml file mapping personal categories to mint categories/descriptions')
    parser.add_argument('--mint', '-m', help='Mint categories to descriptions mapping')
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose logging')
    parser.add_argument('--output', '-o', help='output filename for new transaction csv')
    parser.add_argument('--output-totals', '-O', help='output filename for total transactions by personal category')    
    
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level)

    settings = vars(args)
    global MINT_CATEGORY_TO_DESCRIPTIONS
    logging.debug('Mint categories to descriptions:\n%s' % pprint.pformat(MINT_CATEGORY_TO_DESCRIPTIONS))
    logging.debug('Settings:\n%s' % pprint.pformat(settings))
    return settings

def main():
    settings = get_settings()
    transaction_df = pd.read_csv(settings['input'], dtype=str)
    with open(settings['conf'], 'r') as f:
        personal_to_mint_vals = yaml.safe_load(f)
    logging.debug('Personal to mint categories:\n%s' % pprint.pformat(personal_to_mint_vals))

    # will be category to unclaimed descriptions
    global MINT_CATEGORY_TO_DESCRIPTIONS
    unspecified_mint_cats = set()
    unspecified_mint_descs = set()
    for cat, descs in MINT_CATEGORY_TO_DESCRIPTIONS.items():
        unspecified_mint_cats.add(cat)
        for desc in descs:
            unspecified_mint_descs.add(desc)
    specified_mint_cat_to_personal_cat = {}
    specified_mint_desc_to_personal_cat = {}
    custom_cat_to_personal_cat = {}
            
    # FILL ME IN
    mint_value_to_personal_cat = {}
    for personal_cat, mint_vals in personal_to_mint_vals.items():
        for mint_val in mint_vals:
            if mint_val in unspecified_mint_cats:
                unspecified_mint_cats.remove(mint_val)
                specified_mint_cat_to_personal_cat[mint_val] = personal_cat
            elif mint_val in unspecified_mint_descs:
                unspecified_mint_descs.remove(mint_val)
                specified_mint_desc_to_personal_cat[mint_val] = personal_cat
            else:
                custom_cat_to_personal_cat[mint_val] = personal_cat

    # add all descriptions in these to personal cat as well
    specified_mint_cats = specified_mint_cat_to_personal_cat.keys()

    logging.debug('Specified mint category to personal category:\n%s' % pprint.pformat(specified_mint_cat_to_personal_cat))
    logging.debug('Specified mint description to personal category:\n%s' % pprint.pformat(specified_mint_desc_to_personal_cat))
    logging.debug('Custom category to personal category:\n%s' % pprint.pformat(custom_cat_to_personal_cat))

    for mint_cat, personal_cat in specified_mint_cat_to_personal_cat.items():
        for mint_desc in MINT_CATEGORY_TO_DESCRIPTIONS[mint_cat]:
            mint_value_to_personal_cat[mint_desc] = personal_cat
    mint_value_to_personal_cat.update(specified_mint_cat_to_personal_cat)
    mint_value_to_personal_cat.update(custom_cat_to_personal_cat)
    mint_value_to_personal_cat.update(specified_mint_desc_to_personal_cat)

    logging.debug('Mint value to personal category:\n%s' % pprint.pformat(mint_value_to_personal_cat))

    transaction_df['Category'] = transaction_df['Category'].map(str.lower)
    input_categories = set(transaction_df['Category'])
    mapped_categories = set(mint_value_to_personal_cat.keys())
    unmapped_mint_vals = input_categories.difference(mapped_categories)
    logging.debug('Unmapped mint values:\n%s' % pprint.pformat(unmapped_mint_vals))
    if unmapped_mint_vals and 'default' not in personal_to_mint_vals:
        raise KeyError("No default category specified and unmapped categories encountered:\n%s" % pprint.pformat(unmapped_mint_vals))
    elif unmapped_mint_vals:
        default_personal_cat = personal_to_mint_vals['default']
        for mint_val in unmapped_mint_vals:
            mint_value_to_personal_cat[mint_val] = default_personal_cat
        logging.info('Using default personal category of %s for the following mint categories:\n%s' % (default_personal_cat, pprint.pformat(unmapped_mint_vals)))
            
    transaction_df['Category'] = transaction_df['Category'].map(mint_value_to_personal_cat)
    
    cat_to_expense = {}
    for cat, cat_df in transaction_df.groupby('Category'):
        cat_to_expense[cat] = pd.to_numeric(cat_df['Amount']).sum()
    cat_to_expense = pd.DataFrame(cat_to_expense.items(), columns = ['Category', 'Total Spent'])
    cat_to_expense.sort_values(by=['Total Spent'], inplace=True, ascending=False)

    if settings.get('output') is not None:
        transaction_df.to_csv(settings['output'], index=False, quoting=csv.QUOTE_ALL, float_format='%.2f')
    if settings.get('output_totals') is not None:
        cat_to_expense.to_csv(settings['output_totals'], index=False, float_format='%.2f')

if __name__=='__main__':
    main()
