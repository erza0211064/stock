# from selenium import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import time
from bs4 import BeautifulSoup as bs
import pandas as pd

web_url = 'https://goodinfo.tw/StockInfo/index.asp'


class web_browser():
    def __init__(self, web_url, headless=False):
        if headless == True:
            self.browser = webdriver.PhantomJS(
                executable_path=r'C:/Users/kyubi/Desktop/repo/code/phantomjs-2.1.1-windows/phantomjs-2.1.1-windows/bin/phantomjs.exe')
        else:
            self.browser = webdriver.Firefox(
                executable_path=r'C:/Users/kyubi/AppData/Local/Programs/Python/Python39/geckodriver.exe')
        self.web_url = web_url

    def isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def get_website_info(self):
        self.browser.get(self.web_url)

    def click_button(self, by_type, buttonm_str):
        self.browser.find_element(by_type, buttonm_str).click()

    def close_broswer(self):
        self.browser.close()

    def get_conceptstock(self):
        soup = bs(self.browser.page_source, features="lxml")
        conceptstock_page = soup.find(id='txtStockListMenu')
        conceptstock_page = conceptstock_page.find(id="MENU6")
        return conceptstock_page

    def save_csv(self, table_name, path, file_name):
        table_name.to_csv(path+file_name+'.csv', encoding='utf_8_sig')
        print("save successfully under {}".format(path))

    def get_stock_list(self, stock_cat):
        self.get_website_info()
        self.click_button(By.LINK_TEXT, "類股一覽")
        # browser.find_element(By.CSS_SELECTOR, "#MENU1 input:nth-child(7)").click()
        self.click_button(By.CSS_SELECTOR, "#MENU1 input:nth-child(7)")
        stock_list = self.get_conceptstock()
        for li in stock_list.select('td'):
            try:
                col = int(li["colspan"])
            except (ValueError, KeyError) as e:
                continue
            if col == 4 and li.text == stock_cat:
                self.browser.find_element(By.LINK_TEXT, li.text).click()
                soup_cur = bs(self.browser.page_source, features="lxml")
                table = soup_cur.find(id='txtStockListData')
                table = table.find(id='tblStockList')
                dfs = pd.read_html(table.prettify())
                stock_table = dfs[0].copy()
                break
        # drop row that are not stock
        stock_table = stock_table[stock_table['PER'].apply(
            lambda x: self.isfloat(x))]
        # save as csv file
        stock_table.to_csv(
            'C:/Users/kyubi/Desktop/repo/code/stock/output/{}.csv'.format(stock_cat), encoding='utf_8_sig')

    def run_stock(self):
        self.get_website_info()
        # browser.find_element(By.LINK_TEXT, "類股一覽").click()
        self.click_button(By.LINK_TEXT, "類股一覽")
        # browser.find_element(By.CSS_SELECTOR, "#MENU1 input:nth-child(7)").click()
        self.click_button(By.CSS_SELECTOR, "#MENU1 input:nth-child(7)")
        stock_list = self.get_conceptstock()
        idx = 0
        first_table = 0
        for li in stock_list.select('td'):
            try:
                col = int(li["colspan"])
            except (ValueError, KeyError) as e:
                continue
            if col == 4:
                self.browser.find_element(By.LINK_TEXT, li.text).click()
                soup_cur = bs(self.browser.page_source, features="lxml")
                table = soup_cur.find(id='txtStockListData')
                table = table.find(id='tblStockList')
                dfs = pd.read_html(table.prettify())
                if first_table == 0:
                    first_table = 1
                    stock_table = dfs[0].copy()
                    continue
                stock_table = pd.concat([stock_table, dfs[0]]
                                        ).drop_duplicates().reset_index(drop=True)
                print(stock_table.head(30))
                idx += 1
                if idx == 2:
                    break
            print(li.text)
        # drop row that are not stock
        stock_table = stock_table[stock_table['PER'].apply(
            lambda x: self.isfloat(x))]
        # save as csv file
        stock_table.to_csv(
            'C:/Users/kyubi/Desktop/repo/code/stock/output/check1.csv', encoding='utf_8_sig')
        self.close_broswer()


test1 = web_browser(web_url, headless=True)
test1.get_stock_list("ETF–台灣100")
