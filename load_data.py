import datetime
import redis

from io import BytesIO
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
import calendar
import argparse
from zipfile import ZipFile
from urllib import urlopen

radio_buttons = {
    'equity': 'rbteqty',
    'derivatives': 'rbtDeri',
    'debt-clean': 'rbClean',
    'currency': 'rbtCurrency',
    'debt': 'rbtDebt',
    'slb': 'rbtSLB'
}

chrome_options = Options()
chrome_options.add_argument("--headless")

parser = argparse.ArgumentParser(description='Download Bhav copy for specific date and type of instrument.')
parser.add_argument('-d', '--date', help="Date to download the CSV file for. Format - DD/MM/YYYY")
parser.add_argument('-t', '--type', help='Type of instrument to download CSV for.')
args = parser.parse_args()

date_object = datetime.datetime.strptime(args.date, '%d/%m/%Y')
day_number = '0' + str(date_object.day) if date_object.day / 10 == 0 else str(date_object.day)

selected_type = args.type

driver = webdriver.Chrome('/home/soldierx/Desktop/chromedriver', options=chrome_options)
driver.get('https://www.bseindia.com/markets/equity/EQReports/Equitydebcopy.aspx')

radio_button_xpath = "//*[@id='{}']".format(radio_buttons[selected_type])
radio_button = driver.find_element_by_xpath(radio_button_xpath)
radio_button.click()

day = Select(driver.find_element_by_xpath('//*[@id="fdate1"]'))
day.select_by_visible_text(str(day_number))

month = Select(driver.find_element_by_xpath('//*[@id="fmonth1"]'))
month.select_by_visible_text(calendar.month_abbr[date_object.month])

year = Select(driver.find_element_by_xpath("//*[@id='fyear1']"))
year.select_by_visible_text(str(date_object.year))

submit_button = driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()
lines = None
try:
    file_link = driver.find_element_by_xpath('//*[@id="btnHylSearBhav"]').get_attribute('href')
    resp = urlopen(file_link)
    zipfile = ZipFile(BytesIO(resp.read()))
    for file_name in zipfile.namelist():
        lines = zipfile.read(file_name).splitlines()
except NoSuchElementException:
    print 'Bhav Copy not available for the date!'
finally:
    driver.quit()

info_collection = {}
for line in lines[1:]:
    info = {}
    split_line = line.split(',')
    info['code'] = split_line[0].strip()
    info['name'] = split_line[1].strip().lower()
    info['open'] = float(split_line[4])
    info['high'] = float(split_line[5])
    info['low'] = float(split_line[6])
    info['close'] = float(split_line[7])
    info_collection[split_line[1].strip().lower()] = info

conn = redis.Redis('localhost')
conn.hmset('bse_data', info_collection)

# SEARCH IN REDIS
# for stock in conn.scan_iter(match='*ICIC*'):
#     print conn.hget('bse_data', stock)
