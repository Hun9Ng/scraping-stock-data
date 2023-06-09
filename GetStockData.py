import numpy as np
import pandas as pd
import requests
import bs4
from bs4 import BeautifulSoup
from bs4 import element
import datetime

#### CREATE PERIOD FOR DATA COLLECTION ####
from_date = '10/05/2023'
from_date_dt = datetime.datetime.strptime(from_date,'%d/%m/%Y').date()

to_date = '19/05/2023'
to_date_dt = datetime.datetime.strptime(to_date,'%d/%m/%Y').date()

period=[]
for i in range((to_date_dt - from_date_dt).days+1):
    d = from_date_dt + datetime.timedelta(days=i)
    if d.isoweekday() != 6 and d.isoweekday()!= 7:
        period.append(d.strftime('%d/%m/%Y'))

url_list = pd.DataFrame({'date':period})
url_list['URL'] = 'https://s.cafef.vn/TraCuuLichSu2/1/HOSE/' + url_list['date'] +'.chn'

#### SCRAPING DATA ####
def get_elements_df(stock_elements):
    share = []
    change = []
    price = []
    share_element = stock_elements.find('td', class_='Item_DateItem_lsg')
    price_element = stock_elements.find_all('td', class_='Item_Price1')
    change_element = stock_elements.find('td', class_='Item_ChangePrice_lsg')
    share.append(share_element.text.strip())
    change.append(change_element.text.strip())
    for p in price_element:
        price.append(p.text.strip())
    df = pd.DataFrame({'Mã':share,
                       'Thay đổi':change,
                       'Giá đóng cửa':price[0],
                       'Giá tham chiếu':price[2],
                       'Giá mở cửa':price[3],
                       'Giá cao nhất':price[4],
                       'Giá thấp nhất':price[5],
                       'KLGD khớp lệnh':price[6],
                       'GTGD khớp lệnh':price[7],
                       'KLGD thỏa thuận':price[8],
                       'GTGD thỏa thuận':price[9]})
    return df


df_each_day = pd.DataFrame(columns=['Mã', 'Thay đổi', 'Giá đóng cửa', 'Giá tham chiếu', 'Giá mở cửa',
                                    'Giá cao nhất', 'Giá thấp nhất', 'KLGD khớp lệnh', 'GTGD khớp lệnh',
                                    'KLGD thỏa thuận', 'GTGD thỏa thuận', 'Ngày'])
# 394 mã cổ phiếu
stock_quantity = range(1, 395)
for url in url_list['URL']:
    try:
        page = requests.get(url)
        page.raise_for_status()  # Raise an exception if the page returns an error status code
        soup = BeautifulSoup(page.content, 'html.parser')
        table_elements = soup.find(id='table2sort')

        try:
            for i in stock_quantity:
                df_each_day = pd.concat(
                    [df_each_day, get_elements_df(table_elements.find_all('tr')[i]).assign(Ngày=url[40:50])])
        except Exception as e:
            # Handle the exception raised by the get_elements_df function (e.g., print an error message)
            print(f"Holiday detection: {url[40:50]}")

    except requests.exceptions.RequestException as e:
        # Handle the exception (e.g., print an error message)
        print(f"Cannot access URL: {url}")
        continue

df_each_day.reset_index(inplace=True, drop=True)

#### EXPORTING DATA ####
df_each_day.to_excel('Stockdata.xlsx', index=False)