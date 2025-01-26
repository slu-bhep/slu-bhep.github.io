import configparser
import pandas as pd
import win32com.client as win32
import os
from functions.wmu_functions import load_wmu_data, send_fivetran_emails, send_jloh_email, get_deal_status, get_fx_rates
from functions.wmu_functions import date_range_string, get_pe1_deal, get_synopsis, categorize_pe1_deals, pe1_headers, pe1_title
from functions.wmu_functions import get_pe2_deal, pe2_title
from functions.wmu_functions import get_mna_ipo_data, should_include_mna, add_bold_mna_ipo, mna_title, ipos_title
from functions.wmu_functions import mgmt_text, mgmt_title
from functions.latex_functions import format_latex, write_deals_table
from functions.wmu_style import style_agents_listed, email_style
from datetime import datetime, timedelta
import shutil


def read_config():

    config = configparser.ConfigParser()

    repo_path = os.getcwd()
    config.read(f'{repo_path}\config.ini')

    GPT = config.getboolean('General', 'GPT')
    UPDATE_DATABASE = config.getboolean('General', 'UPDATE_DATABASE')
    SEND_DRAFT_WMU = config.getboolean('General', 'SEND_DRAFT_WMU')
    SEND_DRAFT_JLOH = config.getboolean('General', 'SEND_DRAFT_JLOH')
    WEEKS = config.getint('General', 'WEEKS')
    DELAY = config.getint('General', 'DELAY')
    UPDATE_DEAL_STATUS = config.getboolean('General', 'UPDATE_DEAL_STATUS')

    source_path = config.get('Data', 'source_path')
    database_path = config.get('Data', 'database_path')
    fivetran_email = config.get('Data', 'fivetran_email')

    email_to = config.get('Email', 'email_to')
    name = config.get('Email', 'name')

    config_values = {
        'repo_path': repo_path,
        'GPT': GPT,
        'UPDATE_DATABASE': UPDATE_DATABASE,
        'SEND_DRAFT_WMU': SEND_DRAFT_WMU,
        'SEND_DRAFT_JLOH': SEND_DRAFT_JLOH,
        'WEEKS': WEEKS,
        'DELAY': DELAY,
        'UPDATE_DEAL_STATUS': UPDATE_DEAL_STATUS,
        'source_path': source_path,
        'database_path': database_path,
        'fivetran_email': fivetran_email,
        'email_to': email_to,
        'name': name
    }

    config_confirm = {
        'Repository Path': [repo_path],
        'GPT': [GPT],
        'UPDATE_DATABASE': [UPDATE_DATABASE],
        'SEND_DRAFT_WMU': [SEND_DRAFT_WMU],
        'SEND_DRAFT_JLOH': [SEND_DRAFT_JLOH],
        'WEEKS': [WEEKS],
        'DELAY': [DELAY],
        'UPDATE_DEAL_STATUS': [UPDATE_DEAL_STATUS],
        'source_path': [source_path],
        'database_path': [database_path],
        'fivetran_email': [fivetran_email],
        'email_to': [email_to],
        'name': [name]
    }

    print(pd.DataFrame(config_confirm).T)

    return config_values


if __name__ == '__main__':

    ######################################################## 
    # Load Configurations
    ########################################################

    config_data = read_config()

    user_confirm = input('Please confirm these config variables (y/n): ')
    if user_confirm.lower() != 'y':
        print('\n############## Input your desired config variables in config.ini ##############')
        exit()

    repo_path = config_data['repo_path']
    GPT = config_data['GPT']
    UPDATE_DATABASE = config_data['UPDATE_DATABASE']
    SEND_DRAFT_WMU = config_data['SEND_DRAFT_WMU']
    SEND_DRAFT_JLOH = config_data['SEND_DRAFT_JLOH']
    WEEKS = config_data['WEEKS']
    DELAY = config_data['DELAY']
    UPDATE_DEAL_STATUS = config_data['UPDATE_DEAL_STATUS']
    source_path = config_data['source_path']
    database_path = config_data['database_path']
    fivetran_email = config_data['fivetran_email']
    email_to = config_data['email_to']
    name = config_data['name']

    outlook = win32.Dispatch('outlook.application')
    dimension = 0x0 
    mail = outlook.CreateItem(dimension)
    mail.To = email_to
    mail.Subject = date_range_string(DELAY, WEEKS, 'email')
    greeting = f"<p>Hi all!<br><br>Below is the Weekly Market Update for the past week.</p><br>"
    signature = "<br><br><p>Have a great weekend!<br><br>Kindly,<br>{}</p>".format(name)

    today = datetime.today() - timedelta(days=DELAY)
    formatted_date = today.strftime('%Y%m%d')
    print('Date String: {}'.format(formatted_date))

    ######################################################## 
    # Get FX rates
    ########################################################

    currencies = ['AUD', 'CNY', 'EUR', 'GBP', 'JPY', 'USD'] # TODO: Should this be hardcoded?
    rates = get_fx_rates(currencies)

    ######################################################## 
    # Load Source Data
    ########################################################

    # Step 1: Load the source data and historical database
    print(f"{source_path}/1. Raw Files/{formatted_date}")
    pe1, pe2, mna, ipo, mgmt = load_wmu_data(f"{source_path}/1. Raw Files/{formatted_date}", database_path)
    print(pe1)

    if not pe1.empty:
        # pe1_db = pd.read_csv(f"{database_path}") # Connect to BHEP Data Resources

        # # Step 2: Remove deals from sources that were already present in the database
        # pe1 = pe1[~pe1["Deal ID"].isin(pe1_db["Deal ID"])].reset_index(drop=True)

        # Step 3: Get deal status
        if UPDATE_DEAL_STATUS:
            print('get deal!!')
            deal_status = get_deal_status(pe1)
            deal_status.to_csv(f"{source_path}/1. Raw Files/{formatted_date}/deal_status.csv")
        else:
            deal_status = pd.read_csv(f"{source_path}/1. Raw Files/{formatted_date}/deal_status.csv")

        # Step 4: If requested, update the database to include the deals from this week
        if UPDATE_DATABASE:
            pe1_path = f"{source_path}/1. Raw Files/{formatted_date}/PE1.xlsx"
            ds_path = f"{source_path}/1. Raw Files/{formatted_date}/deal_status.csv"
            send_fivetran_emails(pe1_path, ds_path)

    ########################################################
    # PE1
    ########################################################

    if not pe1.empty:

        # Create lists that will store the bullets to be added to the email
        pe1_deals_r = []
        pe1_deals_nr = []
        pe1_latex = []
        agents_latex = []
        dc_latex = []

        # For every row, extract information and generate the line to be used in the email 
        for i in range(pe1.shape[0]):
            company, hq_location, sector, synopsis, agents_listed, agents_listed_raw = get_pe1_deal(pe1, i)
            synopsis_formatted = get_synopsis(synopsis, GPT, rates)

            # print(company)
            
            deal_reviewed = deal_status.loc[deal_status['Companies'].str.contains(company, case=False), 'BH Reviewed'].values[0]
            reviewed = ''
            if deal_reviewed:
                pe1_deals_r.append((f"<b>{company}</b> [{hq_location}] ({sector}): {synopsis_formatted}", agents_listed))
            else:
                pe1_deals_nr.append((f"<b>{company}</b> [{hq_location}] ({sector}): {synopsis_formatted}", agents_listed))
            bold_start = '\\textbf{'
            ampersand = '\\&'
            pe1_latex.append(format_latex(f"\\textbf{{{company}}} [{hq_location}] ({sector}): {synopsis_formatted}".replace('é', 'e').replace('<b>', bold_start).replace('</b>', '}').replace('&', ampersand)))
            agents_latex.append(f"{{\\tiny \\textcolor{{blue(pigment)}}{{Agents Listed}}: {agents_listed_raw}}}")
        
        dc_latex = deal_status['In Salesforce/DealCloud'].to_list()

        # Prepare the table that we send to John
        if SEND_DRAFT_JLOH:
            write_deals_table(date_range_string(DELAY, WEEKS, 'table'), pe1_latex, agents_latex, dc_latex, r'sourcing\tex\temp_deals.tex')
            os.system("call latexmk -pdf -output-directory=sourcing\\tex sourcing\\tex\\temp_deals.tex")

        # Categorize the deals based on the synopsis
        categorized_pe1_deals_r = categorize_pe1_deals(pe1_deals_r)
        categorized_pe1_deals_nr = categorize_pe1_deals(pe1_deals_nr)

        # Generate the PE1 section HTML based on the categorized deals
        pe1_body = "<p>"

        for section in ["Platform", "Add-On", "Development Capital"]:
            pe1_body += f"<p>{pe1_headers[section]}</p>" + "<ul>"
            
            # Subsection for reviewed deals
            pe1_body += "<p>a)&ensp;Reviewed by Birch Hill</p>"
            if categorized_pe1_deals_r[section]:
                for deal in categorized_pe1_deals_r[section]:
                    pe1_body += f"<li class='indented-li'>{deal[0]}</li>" + style_agents_listed(deal[1])
            else:
                pe1_body += "<p>&emsp;&emsp;&emsp;No applicable deals.</p><br>"
            
            # Subsection for not reviewed deals
            pe1_body += "<p>b)&ensp;Not Reviewed by Birch Hill</p>"
            if categorized_pe1_deals_nr[section]:
                for deal in categorized_pe1_deals_nr[section]:
                    pe1_body += f"<li class='indented-li'>{deal[0]}</li>" + style_agents_listed(deal[1])
            else:
                pe1_body += "<p>&emsp;&emsp;&emsp;No applicable deals.</p><br>"
            
            pe1_body += "</ul>"

    if pe1.empty:
        pe1_body = "<p>"
        for section in ["Platform", "Add-On", "Development Capital"]:
            pe1_body += f"<p>{pe1_headers[section]}</p>" + "<ul>"
            
            # Subsection for reviewed deals
            pe1_body += "<p>a)&ensp;Reviewed by Birch Hill</p>"
            pe1_body += "<p>&emsp;&emsp;&emsp;No applicable deals.</p><br>"
            
            # Subsection for not reviewed deals
            pe1_body += "<p>b)&ensp;Not Reviewed by Birch Hill</p>"
            pe1_body += "<p>&emsp;&emsp;&emsp;No applicable deals.</p><br>"
            
            pe1_body += "</ul>"
    pe1_body += "</p>"
    pe1_email = pe1_title + pe1_body

    hold = input('PE1 is complete. Continue? (y/n): ')
    if hold.lower() != 'y':
        print('\n############## WMU Automation Stopped ##############')
        exit()

    ########################################################
    # PE2
    ########################################################

    # Create list to store the deals, note that we do not need to get agents listed
    pe2_deals = []

    # For every row, extract information and generate the line to be used in the email 
    for i in range(pe2.shape[0]):
        company, hq_location, sector, synopsis = get_pe2_deal(pe2, i)
        synopsis_formatted = get_synopsis(synopsis, GPT, rates)
        if not "Canada" in str(hq_location): # Canadian companies bought in PE deals should be in PE1, not PE2
            pe2_deals.append(f"<b>{company}</b> [{hq_location}] ({sector}): {synopsis_formatted}")

    # Generate the PE2 section HTML
    pe2_body = "<p><ul>"

    if pe2_deals != []:
        for deal in pe2_deals:
            pe2_body += f"<li>{deal}</li><br>"
    else:
        pe2_body += "<p>No applicable deals.</p><br>"

    pe2_body += "</ul></p>"
    pe2_email = pe2_title + pe2_body

    hold = input('PE2 is complete. Continue? (y/n): ')
    if hold.lower() != 'y':
        print('\n############## WMU Automation Stopped ##############')
        exit()

    ########################################################
    # M&A
    ########################################################

    # Create list that will store the deals
    mna_deals = []

    # Analyze the deals and add them to the list if necessary
    for i in range(mna.shape[0]):
        comments, target, buyer = get_mna_ipo_data(mna, i)
        if should_include_mna(mna, i):
            mna_deals.append(add_bold_mna_ipo(comments, GPT, rates))

    # Generate the MnA section HTML
    mna_body = "<p><ul>"

    if mna_deals != []:
        for deal in mna_deals:
            mna_body += f"<li>{deal}</li>"
    else:
        mna_body += "<p>No applicable deals.</p>"

    mna_body += "</ul></p>"
    mna_email = "<br>" + mna_title + mna_body

    hold = input('M&A is complete. Continue? (y/n): ')
    if hold.lower() != 'y':
        print('\n############## WMU Automation Stopped ##############')
        exit()

    ########################################################
    # IPOs
    ########################################################

    # Create list that will store the deals
    ipo_deals = []

    # Analyze the deals and add them to the list if necessary
    for i in range(ipo.shape[0]):
        comments, target, buyer = get_mna_ipo_data(ipo, i)
        ipo_deals.append(add_bold_mna_ipo(comments, GPT, rates))

    # Generate the MnA section HTML
    ipo_body = "<p><ul>"

    if ipo_deals != []:
        for deal in ipo_deals:
            ipo_body += f"<li>{deal}</li>"
    else:
        ipo_body += "<p>No applicable deals.</p>"

    ipo_body += "</ul></p>"
    ipos_email = "<br><br>" + ipos_title + ipo_body

    hold = input('IPO is complete. Continue? (y/n): ')
    if hold.lower() != 'y':
        print('\n############## WMU Automation Stopped ##############')
        exit()

    ########################################################
    # Management Changes
    ########################################################

    # List that will store the details on mgmt changes
    mgmt_changes = []

    print(mgmt)

    # Append the formatted mgmt changes to the list 
    for i in range(mgmt.shape[0]):
        mgmt_changes.append(mgmt_text(mgmt, i, GPT))

    # Generate the MGMT section HTML
    mgmt_body = "<p><ul>"

    if mgmt_changes != []:
        for change in mgmt_changes:
            mgmt_body += f"<li>{change}</li>"
    else:
        mgmt_body += "<p>No applicable deals.</p>"

    mgmt_body += "</ul></p>"
    mgmt_email = "<br><br>" + mgmt_title + mgmt_body

    hold = input('Management Changes is complete. Continue? (y/n): ')
    if hold.lower() != 'y':
        print('\n############## WMU Automation Stopped ##############')
        exit()

    ########################################################
    # Send the Email
    ########################################################

    # Put all the sections together
    body = f"{email_style}{greeting}{pe1_email}{pe2_email}{mna_email}{ipos_email}{mgmt_email}{signature}"

    # Send the email 
    mail.HTMLBody = body
    if SEND_DRAFT_WMU:
        # mail.Display()
        mail.Send()
        print('\n############## Draft WMU Email Sent ##############')
    if SEND_DRAFT_JLOH:
        shutil.copyfile(r'sourcing\tex\temp_deals.pdf', f'{source_path}/2. To JLoh/Deals - {formatted_date}.pdf')
        send_jloh_email(name, email_to, f'{source_path}/2. To JLoh/Deals - {formatted_date}.pdf', email_style)
        print('\n############## Draft JLoh Email Sent ##############')
        
