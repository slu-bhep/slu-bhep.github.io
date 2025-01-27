from collections import defaultdict
from datetime import date, datetime, timedelta
import pandas as pd
import re
import win32com.client as win32
from dotenv import load_dotenv
import os
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas_gbq

from openai import OpenAI

from alpha_vantage.foreignexchange import ForeignExchange

# --------------------------------------------------------------------------------  CONSTANTS

load_dotenv()

TODAY, YEAR = date.today(), date.today().year
LONG_NO_DEALS = "       No applicable deals."
REVIEWED = 'a.   Reviewed by Birch Hill<br><p style="margin-left: 60px;">'
NOT_REVIEWED = 'b.   Not Reviewed by Birch Hill<br><p style="margin-left: 60px;">'

fx_api_key = 'W3BYO6IK9JLM4RQZ' # Stephanie's free API key (25 API calls/day)
fx = ForeignExchange(key=fx_api_key, output_format='pandas')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

# BIGQUERY CREDENTIALS

serviceAccountKeyFile = '/dbfs/FileStore/keys/polycor_data_warehouse.json'

bq_credentials = service_account.Credentials.from_service_account_file(
    serviceAccountKeyFile,
    scopes=['https://www.googleapis.com/auth/cloud-platform',
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/bigquery"]
)

bq_project = 'bhep-data-resources'

# --------------------------------------------------------------------------------  OVERALL FUNCTIONS

def load_wmu_data(source_path):
    try:
        pe1 = pd.read_excel(f"{source_path}/PE1.xlsx", skiprows=6).dropna(subset='Deal ID').drop("Registration Number", axis=1).drop("Emerging Spaces", axis=1)
    except:
        pe1 = pd.DataFrame()
    
    try:
        pe2 = pd.read_excel(f"{source_path}/PE2.xlsx", skiprows=6).dropna(subset='Deal ID')
    except:
        pe2 = pd.DataFrame()
    
    try:
        mna = pd.read_excel(f"{source_path}/PublicM&AActivity.xls", skiprows=7).dropna(subset='Target/Issuer')
    except:
        mna = pd.DataFrame()
    
    try:    
        ipo = pd.read_excel(f"{source_path}/NotableFinancings_PublicOfferings.xls", skiprows=7).dropna(subset='Target/Issuer')
    except:
        ipo = pd.DataFrame()

    try:    
        mgmt = pd.read_excel(f"{source_path}/PublicCompanyKeyManagementChanges.xls", skiprows=7, skipfooter=2).dropna(subset='Company Name')
    except:
        mgmt = pd.DataFrame()
    
    return pe1, pe2, mna, ipo, mgmt


def date_range_string(delay, n_weeks, state):
    # Get today's date
    today = datetime.now()
    
    # Calculate the end date of the range by subtracting the delay
    end_date = today - timedelta(days=delay)
    
    # Calculate the start date of the range by subtracting n_weeks*7 from the end date
    start_date = end_date - timedelta(days=n_weeks*7-1)
    
    # Format the dates to a human-friendly format
    start_date_str = start_date.strftime("%B %d").replace(" 0", " ")
    end_date_str = end_date.strftime("%B %d").replace(" 0", " ")
    
    # Add the 'th', 'st', 'nd', 'rd' suffixes to the day
    def add_day_suffix(day):
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        return str(day) + suffix
    
    start_date_str = start_date_str.replace(str(start_date.day), add_day_suffix(start_date.day))
    end_date_str = end_date_str.replace(str(end_date.day), add_day_suffix(end_date.day))
    
    # Construct and return the final string
    if state == 'email':
        return f"[DRAFT] Weekly Market Update for the week of {start_date_str} - {end_date_str}"
    else:
        return f"Announced the weeks of {start_date_str} - {end_date_str}"

# Example usage
# print(date_range_string(3, 1, 'table'))  # Example: Announced the weeks of October 23rd ‐ October 26th

# --------------------------------------------------------------------------------  FX Rates

def get_rate(from_curr, to_curr='CAD', columns=['5. Exchange Rate', '6. Last Refreshed']):
    '''
    Returns the spot rate from Alpha Vantage API
    '''
    rate, metadata = fx.get_currency_exchange_rate(from_currency=from_curr, to_currency=to_curr)
    rate.reset_index(inplace=True)
    rate = rate[columns]
    rate.columns = ['rate', 'date']
    rate.set_index('date', inplace=True)
    rate.index = pd.to_datetime(rate.index).strftime('%Y-%m-%d')
    return rate

def get_rates(from_currencies, to_curr='CAD', columns=['5. Exchange Rate', '6. Last Refreshed']):
    '''
    Returns a DataFrame of rates for a list of currencies on Alpha Vantage API  
    '''
    rates = pd.DataFrame()
    for curr in from_currencies:
        rate = get_rate(from_curr=curr, to_curr=to_curr, columns=columns)
        rate.columns = [curr]
        if rate.dropna().empty == False:
            rates = pd.concat([rates, rate], axis=1)
        else:
            print(f"{curr} has no data!")
    return rates

def get_fx_rates(currencies):
    path = r'sourcing\rates.csv'

    update_rates = input('Should we update the saved FX rates (y/n)? ')
    update_rates = True if update_rates.lower() == 'y' else False

    if update_rates:
        try:
            rates = get_rates(currencies)
            rates.to_csv(path)
        except:
            print('API call failed')
    
    try:
        rates = pd.read_csv(path)
        rates = rates.drop(columns=['date']).to_dict('records')[0]
    except:
        rates = []

    print(rates)

    return rates

# --------------------------------------------------------------------------------  Deal Status

def get_deal_status(pe1):
    in_dc = []
    bh_reviewed = []
    in_market = []
    for elem in pe1.Companies:
        ans = ''
        while len(ans) != 3 or not bool(re.match(r'^[tf]+$', ans)):
            ans = input("Status for {} <In DC><>BH-Reviewed><In-Market>: ".format(elem))
        in_dc.append(ans[0] == 't')
        bh_reviewed.append(ans[1] == 't')
        in_market.append(ans[2] == 't')

    deal_status = pe1[['Deal ID', 'Companies', 'Company ID']]
    deal_status['In Salesforce/DealCloud'] = in_dc
    deal_status['BH Reviewed'] = bh_reviewed
    deal_status['In-Market'] = in_market

    return deal_status

# --------------------------------------------------------------------------------  PE1 

# PE1 = {Companies} [{HQ Location}] ({Primary Industry Code}): synopsis + agents listed

def get_agents_listed(input_string):
    input_string = re.sub(r'\(([^,]+?),.*?\)', r'(\1)', input_string)

    # Initialize a dictionary to hold the parsed data
    advisors = defaultdict(lambda: defaultdict(list))

    # Regular expression pattern to parse the input string
    pattern = r'(.+?) \((Legal Advisor|Advisor: General) to (.+?)\)'

    # Parse the input string
    for match in re.findall(pattern, input_string):
        firm, advisor_type, company = match
        advisor_type = 'Legal' if 'Legal' in advisor_type else 'General'
        advisors[company][advisor_type].append(firm.strip())

    # Format the output
    output = ""
    for company in advisors:
        output += f"Advisor to {company}: "
        advisors_list = []
        for advisor_type in advisors[company]:
            for firm in advisors[company][advisor_type]:
                advisors_list.append(f"{firm} ({advisor_type})")
        output += ", ".join(advisors_list) + "\n"

    return output.replace(" , ", " ").replace(" ), ", " ")


# Extract the columns necessary to create a PE1 email
def get_pe1_deal(df, index):

    company = format_company(df.loc[index, "Companies"])
    hq_location = str(df.loc[index, "Company City"]) + ", " + str(df.loc[index, "Company State/Province"])
    industry = format_industry(df.loc[index, "Primary Industry Code"])
    synopsis = df.loc[index, "Deal Synopsis"]
    agents_listed = str(df.loc[index, "Service Providers (All)"]).replace("\xa0", "-").replace("nan", "-").replace("i-c", "inanc")
    agents_listed_raw = agents_listed.replace("&", "\&").replace("Advisor: General", "General Advisor")
    if agents_listed != "-":
        agents_listed = get_agents_listed(str(df.loc[index, "Service Providers (All)"]).replace("\xa0", "-").replace("nan", "-").replace("i-c", "inanc"))
    return company, hq_location, industry, synopsis, agents_listed, agents_listed_raw


# Remove additional details about the company which are usually unwanted
def format_company(text):
    text = str(text)
    pattern = r'\s?\(.*?\)'
    text = re.sub(pattern, '', text)
    return text


# Remove the "Other []" from the industry code and replace "(B2B)" by "- B2B"
def format_industry(text):
    text = str(text)
    pattern = r'^Other\s'
    text = re.sub(pattern, "", text)
    text = text.replace("(B2B)", "- B2B")
    text = text.replace("(B2C)", "- B2C")
    return text


def add_comma_after_year(text):
    text = str(text)
    # Define the regex pattern to match dates in the format 'Month Day, Year'
    # Ensure the year is not followed by a period or a comma
    pattern = re.compile(r'(\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4})(?=[^\.,])')
    
    # Substitute the matched pattern with the same pattern followed by a comma
    text = pattern.sub(r'\1,', text)
    
    return text

# With the synopsis as input, format it to match the email one
def get_synopsis(text, gpt, rates):
    text = str(text)
    if (index := text.find("acquire")) != -1:
        text = 'A' + text[index + 1:]
    elif (index := text.find("receive")) != -1:
        text = 'R' + text[index + 1:]
    elif (index := text.find("entere")) != -1:
        text = 'E' + text[index + 1:]
    else:
        return ''
    
    text = add_comma_after_year(text)

    delete = ['Dr. ', 'Ms. ', 'Mrs. ', 'Mr. ']
    for elem in delete:
        text = text.replace(elem, '')
    
    pattern = re.compile(r'\.\s[A-Z]')
    match = pattern.search(text)
    
    if match:
        # Extract the position up to the end of the match
        end_pos = match.start() + 1  # Adjust to include the period
        substring = text[:end_pos]  # Include the space and the uppercase letter
        if gpt and len(rates) > 0:
            substring = format_currency(substring, rates)
        substring = bold_entities(substring)
        return substring
    else:
        if gpt and len(rates) > 0:
            text = format_currency(text, rates)
        text = bold_entities(text)
        return text


def bold_entities(text):
    text = str(text)
    # Define the pattern to match the entities after "Acquired by" up to "through" or "via"
    pattern = re.compile(r'(Acquired by )((?:(?!\bthrough\b|\bvia\b|,|\.).)*)(?=\s*(through|via|,|\.))', re.IGNORECASE)
    
    # Function to add bold tags around the matched entities
    def add_bold_tags(match):
        entities = match.group(2)
        # Split entities by commas and "and", but handle the trailing "and" or ","
        split_entities = re.split(r'\s*,\s*', entities)
        bolded_entities = ', '.join([f'<b>{entity.strip()}</b>' for entity in split_entities if entity.strip()])
        return match.group(1) + bolded_entities + match.group(3)
    
    # Substitute the matched entities with bolded entities
    bolded_text = pattern.sub(add_bold_tags, text)
    
    # Remove any double commas, extra "and", and fix "through" placement
    bolded_text = re.sub(r',\s*,', ',', bolded_text)
    bolded_text = re.sub(r'(?<!\bvia\b),\s*and\b', ' and', bolded_text)
    bolded_text = re.sub(r'\s*throughthrough\s*', ' through ', bolded_text)

    return bolded_text


# Based on the synopsis of the deal, classify it
def categorize_pe1_deals(deals):
    
    categories = {"Platform": [], "Add-On":[], "Development Capital":[]}
    
    for deal in deals:
        synopsis = deal[0]
        if "development capital" in synopsis.lower():
            categories["Development Capital"].append(deal)
        elif "sponsor" in synopsis.lower():
            categories["Add-On"].append(deal)
        else: # Need additional check because sometimes not all PE1 deals should be included
            categories["Platform"].append(deal)

    return categories


# Define the headers that will be used in PE1
pe1_headers = {"Platform": "<u>I. Platform Investment</u>", 
               "Add-On": "<u>II. Add-On Investment</u>", 
               "Development Capital": "<u>III. Development Capital</u>"}


# Define the title that will be used in PE1
pe1_title = '<h2><u>Canadian PE Ownership Changes</u></h2><h3><i>Canadian Target</i></h3>'


def format_currency(input, rates):

    if 'undisclosed amount' in input:
        return input

    rule_1 = "1. Format all dollar values as: {Currency Symbol}{Value}{M or B}{3 Letter Currency Abbreviation}."
    rule_2 = "2. If the currency is not CAD, add the CAD value after the non-CAD value in brackets. E.g., €40M EUR ($60M CAD). Both values must have the same number of decimal places and the appropriate currency symbols."
    rule_3 = f"3. Use this for the conversion factor to CAD: {rates}. There should be a maximum of 2 decimal places. Round the values when necessary."
    rule_4 = "4. Your response should ONLY be the formatted sentence with ONLY the dollar values changed and NO additional quotes."
    rule_5 = "5. If there are no dollar values, return the given sentence ONLY with NO changes."
    rules = f"\n{rule_1}\n{rule_2}\n{rule_3}\n{rule_4}\n{rule_5}\n"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
                {"role": "system", "content": "You are a helpful assistant and I need you to format some information for me."},
                {"role": "user", "content": f"Given the sentence: {input}, format it using the following rules:{rules}"}
            ]
    )
    response_text = response.choices[0].message.content

    return response_text

# --------------------------------------------------------------------------------  PE2

# PE2 = {Companies} [{HQ Location}] ({Primary Industry Code}): synopsis

# Extract the columns necessary to create a PE2 email
def get_pe2_deal(df, index):

    company = format_company(df.loc[index, "Companies"])
    hq_location = df.loc[index, "HQ Location"]
    industry = format_industry(df.loc[index, "Primary Industry Code"])
    synopsis = df.loc[index, "Deal Synopsis"]

    return company, hq_location, industry, synopsis


pe2_title = '<h3><i>Canadian Buyer/Investor</i></h3>'

# --------------------------------------------------------------------------------  MnA 

def get_mna_comments(comments):
    try:
        text = add_comma_after_year(comments)

        pattern = re.compile(r'\.\s[A-Z]')
        match = pattern.search(text)
        
        if match:
            # Extract the position up to the end of the match
            end_pos = match.start() + 1  # Adjust to include the period
            substring = text[:end_pos]  # Include the space and the uppercase letter
            return substring
        else:
            return text

    except AttributeError:
        return "NaN"


# Extract data from the MnA table
def get_mna_ipo_data(df, index):
    comments = get_mna_comments(df.loc[index, 'Transaction Comments'])
    target, buyer = df.loc[index, 'Target/Issuer'], df.loc[index, 'Buyers/Investors']
    return comments, target, buyer


# Verify if a deal should be included in the MnA section
def should_include_mna(df, index):
    implied_value, comments = df.loc[index, 'Implied Enterprise Value (CADmm, Historical rate)'], get_mna_comments(df.loc[index, 'Transaction Comments'])
    industry_target, industry_buyer = df.loc[index, 'Industry Classifications [Target/Issuer]'], df.loc[index, 'Industry Classifications [Buyers/Investors]']
    return more_than_30M(implied_value) and not_reverse_merger(comments) and industry_okay(comments, industry_target, industry_buyer)


# Deal has a total value of more than 30M 
def more_than_30M(implied_value):
    try:
        return not implied_value < 30
    except TypeError:
        return True


# Deal is not a reverse merger
def not_reverse_merger(comments):
    try:
        return comments.find("reverse merger") == -1
    except:
        return True


# Industry is of interest for BH 
def industry_okay(comments, industry_target, industry_buyer):
    terms = ["Mining", "Oil and Gas Exploration and Production", "mine"]
    for term in terms:
        if (term.lower() in industry_target.lower() or 
            term.lower() in industry_buyer.lower() or 
            term.lower() in comments.lower()):
            return False
    return True


# Get the first sentence and bold the correct parts of the MnA deal 
def add_bold_mna_ipo(comments, gpt, rates):
    
    if not gpt:
        return comments
    
    if len(rates) > 0:
        comments = format_currency(comments, rates)
    
    rule_1 = "Return one sentence that describes the transaction, with HTML bold tags around the acquiring/issuing company. Recall that HTML bold tags are NOT **this**." 
    rule_2 = "Remove the reference to the business structure (e.g., Inc, Corp, LLC, LP, etc.) from company names." 
    rule_3 = "For each company name, add the location of their headquarters and their stock ticker (if applicable) in this format: Company Name [City, State] (Ticker)."
    rule_4 = "The response should be ONLY the formatted sentence."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
                {"role": "system", "content": "You are a helpful assistant and I need you to format some information for me."},
                {"role": "user", "content": f"Given the text:\n\n{comments}\n\n{rule_1} {rule_2} {rule_3} {rule_4}"}
            ]
    )
    
    return response.choices[0].message.content


# Define the title that will be used in MnA
mna_title = '<h2><u>Canadian Public M&A Activity</u></h2><p style="margin-left: 40px;">'

# --------------------------------------------------------------------------------  IPOs 

ipos_title = f'<h2><u>Canadian Notable Financings and IPOs</u></h2><p style="margin-left: 40px;">'

# --------------------------------------------------------------------------------  MGMT 

def mgmt_text(df, index, gpt):
        
    if not gpt:
        return get_mgmt_text_simplified(df, index)
    
    rule_1 = "1. Format it as Company Name + ':' + Summary (all in a single line). For company names, remove any reference to the business structure (e.g., Inc, Corp, LLC, LP, etc.)."
    rule_2 = "2. For the summary, use a single sentence starting with a past tense verb (e.g., Announced, Appointed, etc.) and avoid redundancies."
    rule_3 = "3. Your response should be ONLY the single formatted sentence and not include quotes in the beginning or end."
    rule_4 = "4. When necessary, you can shorten Chief Executive Officer to CEO, Chief Financial Officer to CFO, Vice President to VP, Senior Vice President to SVP, and Board of Directors to the Board."
    rule_5 = "5. Do not include dates."
    # rule_6 = "6. The summary should ONLY include essential information about changes in roles, being as succint as possible. Do not include personal details, honorifics, or details about the career of the executives. Remove all details about the company the executive is from, where they are going to if they are leaving, or the company's plans after someone's departure. Remember that being succinct is mandatory."
    rule_6 = "6. The summary should ONLY include essential information about changes in roles, being as succint as possible. Do not include the role that an executive is coming from."
    rule_7 = "7. A good example is: 'Announced the appointment of John Doe as Interim CFO and Jane Doe to the Board'."

    print(df)
    text = df.loc[index, "Key Developments by Type -  [Last 7 Days]"]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
                {"role": "system", "content": "You are a helpful assistant and I need you to format some information for me."},
                {"role": "user", "content": f"Given the text: {text}, format it using the following rules:\n{rule_1}\n{rule_2}\n{rule_3}\n{rule_4}\n{rule_5}\n{rule_6}\n{rule_7}"}
            ]
        )

    response_text = response.choices[0].message.content
    colon_loc = response_text.find(":")
    return '<b>' + response_text[:colon_loc + 1] + '</b>' + response_text[colon_loc + 1:]


def get_mgmt_text_simplified(df, index):

    cell_value = df.loc[index, "Key Developments by Type -  [Last 7 Days]"]

    return cell_value

    # try:
    #     bracket_position = cell_value.index(")")            # Look for the ")" character
    #     right_substring = cell_value[bracket_position+1:]   # Substring after the ")"

    #     if "Announce" in right_substring:
    #         announce_position = right_substring.index("Announce")
    #         return f"{right_substring[:announce_position].strip()}: Announced {right_substring[announce_position+len('Announce') + 2:]}."

    #     elif "Appoint" in right_substring:
    #         appoint_position = right_substring.index("Appoint")
    #         return f"{right_substring[:appoint_position].strip()}: Appointed {right_substring[appoint_position+len('Appoint') + 2:]}."

    # except Exception as e:
    #     return "Error in generating string"


# --------------------------------------------------------------------------------  FIVETRAN 

def send_fivetran_emails(pe1_path, ds_path):
    update_pe1(pe1_path)
    update_ds(ds_path)


def update_pe1(pe1_path):
    df = pd.read_excel(pe1_path, skiprows=8, skipfooter=2).drop("Registration Number", axis=1)
    df.drop(df.loc[:, 'Top CPC Codes':'PitchBook Link'].columns, axis=1)
    df.to_csv(r'sourcing\pitchbook_pe1.csv')

    outlook = win32.Dispatch('outlook.application')
    dimension = 0x0 
    mail = outlook.CreateItem(dimension)
    mail.To = 'narrator_defendant.bhep_pe_deal_flow.pitchbook_pe_deal_record@email-connector.fivetran.com'
    # mail.To = 'slu@birchhillequity.com'
    mail.Subject = 'WMU Fivetran Sync - PE1'
    mail.Attachments.Add(Source=r'sourcing\pitchbook_pe1.csv')

    mail.Display()


def update_ds(ds_path):
    df = pd.read_excel(ds_path).drop("Companies", axis=1).drop("Company ID", axis=1)
    df.to_csv(r'sourcing\bhep_deal_status.csv')

    outlook = win32.Dispatch('outlook.application')
    dimension = 0x0 
    mail = outlook.CreateItem(dimension)
    mail.To = 'narrator_defendant.bhep_pe_deal_flow.bhep_deal_status@email-connector.fivetran.com'
    mail.Subject = 'WMU Fivetran Sync - Deal Status'
    mail.Attachments.Add(Source=r'sourcing\bhep_deal_status.csv')

    mail.Display()


# --------------------------------------------------------------------------------  EMAIL TO JLOH

def send_jloh_email(name, email_to, pdf_path, email_style):
    outlook = win32.Dispatch('outlook.application')
    dimension = 0x0 
    mail = outlook.CreateItem(dimension)
    mail.To = email_to
    mail.Subject = 'Weekly Market Update Check'
    mail.Attachments.Add(Source=pdf_path)

    greeting = "Hi John,"
    body = "Attached are the Canadian PE deals for the past week. Let me know if we have reviewed any of them and if they would be in Market for us."
    ending = "Kindly,"
    mail.HTMLBody = f"{email_style}<p>{greeting}<br><br>{body}<br><br>{ending}<br>{name}</p>"

    mail.Display()
    # mail.Send()


# --------------------------------------------------------------------------------  DEPRECATED 
def format_mgmt_text(input, gpt):

    if not gpt:
        return input

    rule_1 = "1. Formatted it as Corporation Name + ':' + Summary (all in a single line)."
    rule_2 = "2. For the summary, use a single sentece starting with a past tense verb (e.g., Announced, Appointed, etc.) and avoid redundances."
    rule_3 = "3. Your response should only be the formatted sentence and not include quotes in the beginning or end."
    rule_4 = "4. When necessary, you can shorten Chief Executive Officer to CEO and Chief Financial Officer to CFO"
    rule_5 = "5. Dates should all have the format: Month DD, YYYY"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
                {"role": "system", "content": "You are a helpful assistant and I need you to format some information for me."},
                {"role": "user", "content": f"Given the sentence: {input}, format it using the following rules:\n{rule_1}\n{rule_2}\n{rule_3}\n{rule_4}\n{rule_5}"}
            ]
    )
    response_text = response.choices[0].message.content
    colon_loc = response_text.find(":")
    return '<b>' + response_text[:colon_loc + 1] + '</b>' + response_text[colon_loc + 1:]


mgmt_title = f'<h2><u>Canadian Public Company Key Management Changes</u></h2><p style="margin-left: 40px;">'
