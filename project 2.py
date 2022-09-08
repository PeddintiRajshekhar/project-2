#!/usr/bin/env python
# coding: utf-8

# In[10]:


import pandas as pd
import warnings


# In[11]:


pd.set_option('display.max_colwidth', 0)
pd.set_option('display.max_columns', None)
pd.options.display.max_seq_items = 2000
warnings.filterwarnings('ignore')


# In[12]:


get_ipython().run_cell_magic('html', '', '<style>\n.dataframe td {\n    white-space: nowrap;\n}\n</style>')


# In[13]:


df_lines = pd.read_csv('C:/Users/Vasu Arjun/Downloads/order_lines.csv', index_col = 0)
print("{:,} order lines to process".format(len(df_lines)))
df_lines.head()


# In[15]:


df_uom = pd.read_csv('C:/Users/Vasu Arjun/Downloads/uom_conversions.csv', index_col = 0)
print("{:,} Unit of Measure Conversions".format(len(df_uom)))

# Join
df_join = df_lines.copy()
COLS_JOIN = ['Item Code']
df_join = pd.merge(df_join, df_uom, on=COLS_JOIN, how='left', suffixes=('', '_y'))
df_join.drop(df_join.filter(regex='_y$').columns.tolist(),axis=1, inplace=True)
print("{:,} records".format(len(df_join)))
df_join.head()


# In[16]:


df_dist = pd.read_csv('C:/Users/Vasu Arjun/Downloads/distances.csv', index_col = 0)
# Location
df_dist['Location'] = df_dist['Customer Country'].astype(str) + ', ' + df_dist['Customer City'].astype(str)
df_dist.head()


# In[17]:


df_gps = pd.read_csv('C:/Users/Vasu Arjun/Downloads/gps_locations.csv', index_col = 0)
print("{:,} Locations".format(len(df_gps)))
df_gps.head()


# In[18]:


df_dist = pd.merge(df_dist, df_gps, on='Location', how='left', suffixes=('', '_y'))
df_dist.drop(df_dist.filter(regex='_y$').columns.tolist(),axis=1, inplace=True)
df_dist


# In[19]:



COLS_JOIN = ['Warehouse Code', 'Customer Code']
df_join = pd.merge(df_join, df_dist, on = COLS_JOIN, how='left', suffixes=('', '_y'))
df_join.drop(df_join.filter(regex='_y$').columns.tolist(),axis=1, inplace=True)
print("{:,} records".format(len(df_join)))
df_join


# In[21]:


# Calculate Weight (KG)
df_join['KG'] = df_join['Units'] * df_join['Conversion Ratio']

# Agg by order
GPBY_ORDER = ['Date', 'Month-Year', 
        'Warehouse Code', 'Warehouse Name', 'Warehouse Country', 'Warehouse City',
        'Customer Code', 'Customer Country', 'Customer City','Location', 'GPS 1', 'GPS 2', 
        'Road', 'Rail', 'Sea', 'Air',
        'Order Number']
df_agg = pd.DataFrame(df_join.groupby(GPBY_ORDER)[['Units', 'KG']].sum())
df_agg.reset_index(inplace = True)
df_agg.head()


# In[22]:


# CO2 Emissions
dict_co2e = dict(zip(['Air' ,'Sea', 'Road', 'Rail'], [2.1, 0.01, 0.096, 0.028]))
MODES = ['Road', 'Rail','Sea', 'Air']
for mode in MODES:
    df_agg['CO2 ' + mode] = df_agg['KG'].astype(float)/1000 * df_agg[mode].astype(float) * dict_co2e[mode]
df_agg['CO2 Total'] = df_agg[['CO2 ' + mode for mode in MODES]].sum(axis = 1)
df_agg.head()


# In[23]:


# Mapping the delivery Mode
df_agg['Delivery Mode'] = df_agg[MODES].astype(float).apply(
    lambda t: [mode if t[mode]>0 else '-' for mode in MODES], axis = 1)
dict_map = dict(zip(df_agg['Delivery Mode'].astype(str).unique(), 
  [i.replace(", '-'",'').replace("'-'",'').replace("'",'') for i in df_agg['Delivery Mode'].astype(str).unique()]))
df_agg['Delivery Mode'] = df_agg['Delivery Mode'].astype(str).map(dict_map)
df_agg


# In[ ]:




