import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

df_package = pd.read_csv("package_list.csv")

df = pd.read_csv("Web_Crawler.csv",sep='\t')
df.drop(["Unnamed: 0"],axis=1,inplace=True)

package_list = list(df_package["package"])
data = dict()
core_package = []




for i in range(0,10):
    try:
        URL_part_1 = "https://play.google.com/store/apps/details?id="
        URL_part_2 = package_list[i]
        data["Package"] = URL_part_2
        url = URL_part_1+URL_part_2
        data["Url"] = url
        r = requests.get(url)
        soup = BeautifulSoup(r.content,'html5lib')
        data["Name"] = (soup.find('meta',itemprop='name')).get('content')
        data["Application Group"] = soup.find('a',{'class':'hrTbp R8zArc'}).text
        data["Application Category"] = soup.find('a',{'class':'hrTbp R8zArc','itemprop':'genre'}).text
        data["Application Description"] = soup.find('div',{'class':'DWPxHb','itemprop':'description'}).get_text(separator='\n')
        total_no_of_ratings = soup.find('span',{'class':'EymY4b'}).get_text()
        total_no_of_ratings = total_no_of_ratings.split(" ")
        total_no_of_ratings = total_no_of_ratings[0]
        total_no_of_ratings = int(total_no_of_ratings.replace(',',''))
        ratings_distribution = soup.find('div',{'class':'VEF2C'})
        ratings_distribution = (str(ratings_distribution)).split('>')

        ratings = []
        for j in ratings_distribution:
            if '%' in j:
                ratings.append(j)

        rating_nums = []
        sumup = 0
        for i in range(len(ratings)):
            start = ratings[i].find(':')
            end = ratings[i].find('%')
            sumup += int(ratings[i][start+2:end])
            rating_nums.append(int(ratings[i][start+2:end]))

        multiplier = (total_no_of_ratings)/sumup

        for i in range(len(rating_nums)):
            rating_nums[i] = round(rating_nums[i]*multiplier)

        data["5 star"] = rating_nums[0]
        data["4 star"] = rating_nums[1]
        data["3 star"] = rating_nums[2]
        data["2 star"] = rating_nums[3]
        data["1 star"] = rating_nums[4]

        driver = webdriver.Chrome(executable_path='chromedriver')
        driver.get(url)
        installs = driver.find_element_by_xpath("//div[contains(.,'Installs') and contains(@class, 'hAyfc')]").text.split()
        data["Installs"] = installs[1]
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.LINK_TEXT, "View details")))
        driver.find_element_by_link_text('View details').click()
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'This app has access to')]")))
        permissions = driver.find_element_by_xpath("//div[contains(text(),'This app has access to')]/parent::*")
        permission_text = permissions.get_attribute("innerText")
        data["Permissions"] = permission_text
        
        driver.close()


        df1 = pd.DataFrame(list(data.items()))
        df1 = df1.transpose()
        df1.columns = df1.iloc[0,:]
        df1.drop([0],axis=0,inplace=True)
        df1.reset_index(inplace=True)
        df1.drop(["index"],axis=1,inplace=True)
        df = df.append(df1,ignore_index=True,sort=False)

        df.to_csv("Web_Crawler.csv",sep='\t')
    except:
        core_package.append(i)


