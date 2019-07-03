from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
import unicodedata

app = Flask(__name__)

@app.route('/', methods=["GET"])
def home():
    return render_template("form.html")

@app.route('/forward/', methods=["POST"])
def build():
    LOGIN_URL = 'https://admin.servicefusion.com/'
    estimate_link = request.form['estimateLink']

    if request.form['company'] == 'phd':
        company = 'phd'

    elif request.form['company'] == 'moore':
        company = 'moore'

    username = 'skimura'

    password = 'Tyler802'

    s = requests.Session()

    result = s.post(LOGIN_URL, data={
        'Authenticate[company]': company,
        'Authenticate[uid]': username,
        'Authenticate[pwd]': password
    })

    html = s.get(estimate_link).content

    soup = BeautifulSoup(html, "html.parser")

    #num = soup.find('div', class_='estimate-header-left').a.text

    containers = soup.find_all('div', class_='tab-content widget-content form-container')

    specs = containers[0]

    fields = specs.find_all('div', class_='span8 borders')

    customer = fields[0].text

    contact = fields[1]

    #phone = contact.find('a', class_='phoneNumber1').text

    #email = contact.find('a', class_='emailEstimateBtn').text

    location = fields[2].text

    sales_data = containers[1]

    fields = sales_data.find_all('div', class_='span8 borders')

    date = fields[0].text

    referral_source = fields[2].text

    opp_owner = fields[5].text

    # BUSINESS CHALLENGES
    challenges = request.form.getlist('challenge')

    # PROJECT GOALS
    goals = request.form.getlist('goal')

    # PROJECT Benefits
    benefits = request.form.getlist('benefit')

    # VENDORS
    vendors = request.form.getlist('vendor')

    nhc = 'New Horizons Communications'
    whitemtn = 'White Mountain IT Services'
    vfs = 'Verizon Fiber Services'
    comcast = 'Comcast Business Services'

    nhc_list = ['Description 1', 'Description 2']
    whitemtn_list = ['Description 1', 'Description 2']
    vfs_list = ['Description 1', 'Description 2']
    comcast_list = ['Description 1', 'Description 2']

    vendor_dict = {}

    if nhc in vendors:
        vendor_dict[nhc] = nhc_list

    if whitemtn in vendors:
        vendor_dict[whitemtn] = whitemtn_list

    if vfs in vendors:
        vendor_dict[vfs] = vfs_list

    if comcast in vendors:
        vendor_dict[comcast] = comcast_list


    # Collect data table

    # Parts
    parts = []

    part_container = soup.find_all('dl', class_='dl-custom')

    for tag in part_container:
        part = tag.find('dt').text
        part = unicodedata.normalize("NFKD", part)
        parts.append(part)

    # Quantity
    qty = []

    qty_container = soup.find_all('div', class_='span1 services-div-margin services-div-qty')

    for tag in qty_container:
        num = tag.text.replace('\t', '').replace('\n', '').strip()
        if num != '':
            num = float(num)
            qty.append(num)

    # Rates
    rates = []

    rate_container = soup.find_all('div', class_='span2 services-div-margin unit-price-width')

    for tag in rate_container:
        rate = tag.text.replace('\t', '').replace('\n', '').strip()
        if '$' not in rate and '%' not in rate:
            rate = float(rate)
            rates.append(rate)

    # Totals
    totals = []

    for amount, price in zip(qty, rates):
        total = amount * price
        totals.append(total)

    # Estimate Total
    estimate_total = 0

    for total in totals:
        estimate_total += total

    # Format

    rates = ['$%.2f' % member for member in rates]

    totals = ['$%.2f' % member for member in totals]

    estimate_total = '$%.2f' % estimate_total

    # Combine lists into dictionary
    table_data = dict((z[0], list(z[1:])) for z in zip(parts, qty, rates, totals))


    if request.form['company'] == 'phd':
        return render_template('phd-proposal.html', customer=customer, date=date, owner=opp_owner, challenges=challenges, goals=goals, benefits=benefits, vendors=vendor_dict, data=table_data, total=estimate_total)

    elif request.form['company'] == 'moore':
        return render_template('moore-proposal.html', customer=customer, date=date, owner=opp_owner, challenges=challenges, goals=goals, benefits=benefits, vendors=vendor_dict, data=table_data, total=estimate_total)
