from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
import sys
import time
import os



class StockAlert:

	sleep_time_normal = 20
	sleep_time_after_exception = 40
	percent_delta = 0.1
	max_range_bound_count = 30
	url_prefix = "https://in.tradingview.com/symbols/NSE-"
	duration = 1000  # milliseconds
	freq = 440  # Hz
	

	def __init__(self, stock_symbol):
		self.stock_symbol = stock_symbol
		self.initialized = False
		self.range_bound_count = 0
		self.url = StockAlert.url_prefix + self.stock_symbol


	def get_stock_alert(self):
		print("installing driver")
		chromedriver_autoinstaller.install()
		self.driver = webdriver.Chrome()
		self.sleep_time = StockAlert.sleep_time_normal
		while 1:			
			self.driver.get(self.url)
			time.sleep(self.sleep_time)
			try:
				if (self.initialized == False):
					self.init_stock_price()
				
				print("Previous, last_traded_price = " + str(self.last_traded_price) +  " and count = " + str(self.range_bound_count))
				self.set_last_traded_price_from_web()

				if (self.last_traded_price >= self.upper_limit):
					self.set_bounds()
					print("    After increase, new limit, " + self.prices_to_string())
					self.notify("Price increased for " + self.stock_symbol, self.last_traded_price)
					self.range_bound_count = 0
					
				elif (self.last_traded_price <= self.lower_limit):
					self.set_bounds()
					print("    After decrease, new limit, " + self.prices_to_string())
					self.notify("Price decreased for " + self.stock_symbol, self.last_traded_price)
					self.range_bound_count = 0
				else:
					self.range_bound_count = self.range_bound_count + 1

				if(self.range_bound_count > StockAlert.max_range_bound_count):
					print("    Range bound, for count, " + str(self.range_bound_count))
					self.notify("Range bound for " + self.stock_symbol, self.last_traded_price)	
					self.range_bound_count = 0

			except Exception  as e:
				print("    Exception in processing price, e = " + str(e))
				self.sleep_time = StockAlert.sleep_time_after_exception
				self.range_bound_count = self.range_bound_count - 1
			else:
				self.sleep_time = StockAlert.sleep_time_normal

	def init_stock_price(self):
		print("Initializing for stock_symbol = " + self.stock_symbol)
		self.set_last_traded_price_from_web()
		self.set_bounds()

		print("Price initialized for stock_symbol " + self.stock_symbol + " " +self.prices_to_string())
		self.notify("Price initialized for " + self.stock_symbol, self.last_traded_price)
		self.initialized = True

	def prices_to_string(self):
		return "lower_limit = " + str(self.lower_limit) + " last_traded_price = " + str(self.last_traded_price) + " upper_limit = " + str(self.upper_limit)

	def set_last_traded_price_from_web(self):
		self.last_traded_price = float(self.driver.find_element(By.CLASS_NAME,"js-symbol-last").text.replace(',',''))

	def set_bounds(self):
		self.delta = StockAlert.percent_delta / 100 * self.last_traded_price
		self.lower_limit = self.last_traded_price - self.delta
		self.upper_limit = self.last_traded_price + self.delta

	def notify(self, title, text):
		print("os.name " + os.name)
		
		if os.name == 'posix':
			os.system('printf "\a"')
			os.system("""
				osascript -e 'display notification "{}" with title "{}"'
				""".format(text, title))
			os.system('say {}'.format(title))
			os.system('say {}'.format(text))
		elif os.name == 'Linux':
			os.system('spd-say {}'.format(title))
			os.system('spd-say {}'.format(text))
			



#stock_alert = StockAlert('TATASTEELK2021')
stock_alert = StockAlert('NIFTY')
stock_alert.get_stock_alert()
