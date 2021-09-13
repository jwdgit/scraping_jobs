#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
from tqdm import tqdm
import pandas as pd
import time
import json
import numpy as np
import gspread
import math
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import datetime


# In[ ]:


credentials = ServiceAccountCredentials.from_json_keyfile_name('service_account.json')
client = gspread.authorize(credentials)


# In[ ]:


sheet = client.open('Futwiz Data - API')
data_sheet = sheet.worksheet('Data')
input_sheet = sheet.worksheet('Input')


# In[ ]:


urls = input_sheet.col_values(1)[1:]


# In[ ]:


# # Testing API
# url = 'https://www.futwiz.com/en/test_api/16382-17899-17636-17643-17640-17552-17547-17522-17454-16931-16909-16910-18226-18272-18291-18294-18293-18296-18295-18297-18298-18299-14-208'
# res = requests.get(url)


# In[ ]:


url_sets = np.array_split(urls,math.ceil(len(urls)/25))
futwiz = {'Url':[],'Name':[],'Version':[],'Rating':[],'Xbox Price':[],'Xbox Low':[],'Xbox Average':[],'Xbox High':[],'Yesterday Price Xbox':[],'Xbox Price Range':[],'Playstation Price':[],'Playstation Low':[],'Playstation Average':[],'Playstation High':[],'Yesterday Price Playstation':[],'Playstation Price Range':[],'PC Price':[],'PC Low':[],'PC Average':[],'PC High':[],'Yesterday Price PC':[],'PC Price Range':[]}
for us in tqdm(url_sets):
    pids = '-'.join([i.rsplit('/', 1)[1] for i in us])
    time.sleep(1)
    res = requests.get('https://www.futwiz.com/en/test_api/'+pids)
    data = json.loads(res.text)
    for p in data:
        url = 'https://www.futwiz.com/en/test_api/'+p
        pdata = data[p]
        name = pdata['name']
        rating = pdata['rating']
        version = pdata['version']
        xbox_price = pdata['xb']['bin']
        ps_price = pdata['ps']['bin']
        pc_price = pdata['pc']['bin']
        yesterday_price_xbox = None
        yesterday_price_ps = None
        yesterday_price_pc = None
        xbox_price_range = pdata['max_range_xb']
        ps_price_range = pdata['max_range_ps']
        pc_price_range = pdata['max_range_pc']
        graph_url = 'https://www.futwiz.com/en/app/price_history_player21_multi?p='+p+'&h'
        res = requests.get(graph_url)
        graph_data = json.loads(res.text)
        try:
            xb = [i[1] for i in graph_data['xb']]
            xb_low = min(xb)
            xb_average = int(np.mean(xb))
            xb_high = max(xb)
        except:
            xb_low = None
            xb_average = None
            xb_high = None
        try:
            ps = [i[1] for i in graph_data['ps']]
            ps_low = min(ps)
            ps_average = int(np.mean(ps))
            ps_high = max(ps)
        except:
            ps_low = None
            ps_average = None
            ps_high = None
        try:
            pc = [i[1] for i in graph_data['pc']]
            pc_low = min(pc)
            pc_average = int(np.mean(pc))
            pc_high = max(pc)
        except:
            pc_low = None
            pc_average = None
            pc_high = None
        graph_url = 'https://www.futwiz.com/en/app/price_history_player21_multi?p='+p
        res = requests.get(graph_url)
        graph_data = json.loads(res.text)
        yesterday_price_xbox = graph_data['xb'][-1][1]
        yesterday_price_ps = graph_data['ps'][-1][1]
        yesterday_price_pc = graph_data['pc'][-1][1]
        futwiz['Url'].append(url)
        futwiz['Name'].append(name)
        futwiz['Rating'].append(rating)
        futwiz['Version'].append(version)
        futwiz['Xbox Price'].append(xbox_price)
        futwiz['Xbox Low'].append(xb_low)
        futwiz['Xbox Average'].append(xb_average)
        futwiz['Xbox High'].append(xb_high)
        futwiz['Yesterday Price Xbox'].append(yesterday_price_xbox)
        futwiz['Xbox Price Range'].append(xbox_price_range)
        futwiz['Playstation Price'].append(ps_price)
        futwiz['Playstation Low'].append(ps_low)
        futwiz['Playstation Average'].append(ps_average)
        futwiz['Playstation High'].append(ps_high)
        futwiz['Yesterday Price Playstation'].append(yesterday_price_ps)
        futwiz['Playstation Price Range'].append(ps_price_range)
        futwiz['PC Price'].append(pc_price)
        futwiz['PC Low'].append(pc_low)
        futwiz['PC Average'].append(pc_average)
        futwiz['PC High'].append(pc_high)
        futwiz['Yesterday Price PC'].append(yesterday_price_pc)
        futwiz['PC Price Range'].append(pc_price_range)


# In[ ]:


futwiz_df = pd.DataFrame(futwiz)
time = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
futwiz_df['Date & Time'] = time
futwiz_df.to_csv('futwiz_data.csv',index=False)


# In[ ]:


data_sheet.clear()
set_with_dataframe(data_sheet, futwiz_df)

