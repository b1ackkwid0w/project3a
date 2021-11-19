# Stock Data Visualizer
# This program does 3 things:
# Get input from the user
# Call api with input from user
# Generates a graph and open in the user’s default browser
#
# 10/20/2021
# Amy Snell, Eric Stranquist, Joel Spencer, Luke Manary, Michael Shamsutdinov, Stephen White

#imports
from datetime import datetime, timedelta
import requests
import pygal
import config

GRAPH = {
    '1': 'bar',
    '2': 'line'
}
FUNCTION = {
    '1': 'TIME_SERIES_INTRADAY',
    '2': 'TIME_SERIES_DAILY',
    '3': 'TIME_SERIES_WEEKLY',
    '4': 'TIME_SERIES_MONTHLY'
}


#this function collects and tests user data for the queries - stock symbol, chart type, time series, start date and end date
def get_user_input():
    #initializing values
    stock_symbol = "" #initializing stock symbol
    chart_type = "1" #initializing chart type
    time_series = "1" #initializing time series
    start_day = "1900-01-01" #initiazing start date at Jan 1 1900
    today = datetime.now().date() #initiazing end date obj as today
    end_date_obj = today
    end_day = datetime.strftime(today, "%Y-%m-%d") #converting end date to string
    return_dict = {}    # default return value

    print('Stock Data Visualizer\n-----------------------')
    
        
    #stock symbol input
    while True:
        try: 
            stock_symbol = input('Enter the Stock Symbol you are looking for: ')
            stock_symbol = stock_symbol.upper()
            if stock_symbol == "": #testing if user input is null
                print('Stock Symbol Example: GOOGL')    #input example due to null input
                raise Exception
            break
        except Exception: #catching errors
            print('\nInvalid Entry. Please try again...')
            continue

    #graph type input
    while True:
        try: 
            print('\nGraph Types\n------------\n1. Bar\n2. Line\n')
            graph_type = int(input('Enter the Graph Type you want (1, 2): '))
            if graph_type < 1 or graph_type > 2:
                raise Exception
            break
        except Exception: #catching invalid input
            print('\nInvalid entry: Please try again...')
            continue

    #time series input
    while True:
        try: 
            print('\nTime Series\n-----------\n1. Intraday (past 60 days)\n2. Daily\n3. Weekly\n4. Monthly')
            time_series = int(input("Enter time series option (1, 2, 3, 4): "))
            if time_series < 1 or time_series > 4:
                raise Exception
            break
        except Exception: #catching invalid input
            print('\nInvalid entry: Please try again...')
            continue

    
        
    #start date input
    while True:
        try: 
            start_day = input('\nEnter the start date (YYYY-MM-DD): ') 
            start_date_obj = datetime.strptime(start_day, "%Y-%m-%d") #converting string input to date object and formmating
            start_date = start_date_obj.date() #removing time from date object
            if time_series == 1:    # if intraday
                earliest_date = today - timedelta(days=60) # 60 days prior to today
                if start_date < earliest_date:
                    raise IOError
            break
        except IOError: # specific error for date out of bounds
            print('\nEarliest date for intraday is: ' + datetime.strftime(earliest_date,'%Y-%m-%d'))
            continue
        except Exception: #raising exception for date format error
            print('\nInvalid entry. Please try again...')
            continue
        
    #end date input
    while True:
        try:
            end_day = input('Enter the end date (YYYY-MM-DD): ')
            end_date_obj = datetime.strptime(end_day, "%Y-%m-%d")   # input string to date object
            if end_date_obj <= start_date_obj:  # raise exception if end date is before start date
                raise IOError
            break
        except IOError:
            print('\nEnd Date must be after Start Date. Current Start Date is ' + datetime.strftime(start_date,'%Y-%m-%d'))
            continue
        except Exception:   # catching other error like date formats
            continue

    end_date = end_date_obj.date() #removing time from date objectls

    graph_type_str = GRAPH[str(graph_type)]             # converting ints to proper strings for queries
    time_series_str = FUNCTION[str(time_series)]        # converting ints to proper strings for queries
    

    return_dict = {
        "stock_symbol": stock_symbol,       # string
        "graph_type": graph_type_str,       # string
        "time_series": time_series_str,     # string
        "start_date": start_date,           # datetime object
        "end_date": end_date                # datetime object
    }
        
    #returning string values to send for queries
    return return_dict

    



# calls the api given inputs
def call_api(inputs, API_KEY):
  # inputs = {
  #   "stock_symbol": string,
  #   "chart_type": string,
  #   "time_series": string,
  #   "time_interval": string,
  #   "start_date": string,
  #   "end_date": string
  # }
  # Required fields based on 'function': (//optional: only including relevant fields)
  #   TIME_SERIES_INTRADAY --> function, symbol, interval, apikey   //optional: outputsize
  #   TIME_SERIES_DAILY --> function, symbol, apikey                //optional: outputsize
  #   TIME_SERIES_WEEKLY --> function, symbol, apikey               //optional: n/a
  #   TIME_SERIES_MONTHLY --> function, symbol, apikey              //optional: n/a

  # create url string
  url = 'https://www.alphavantage.co/query?function=' + inputs['time_series'] + '&symbol=' + inputs['stock_symbol']

  # if time_series is 'TIME_SERIES_INTRADAY' then add the required 'interval' field to the url string
  if inputs['time_series'] == 'TIME_SERIES_INTRADAY':
    url = url + '&interval=60min'
    url = url + '&outputsize=full'  # request more than the last 100 data points
  elif inputs['time_series'] == 'TIME_SERIES_DAILY':
    url = url + '&outputsize=full'  # request more than the last 100 data points

  # add API_KEY to url string
  url = url + '&apikey=' + API_KEY

  # make request using url string
  try:
    r = requests.get(url)
  except Exception:
    print('An error occurred during api call. Exiting program...')
    exit(1)

  # parse response from json to dictionary
  data = r.json()
    
    

  # check json status
  # print(r.status_code)
  if r.status_code == 200:
    print('API call successful... ')
    return data
  else:
    print('Error: ', r.status_code)
    return {}



def filter_dates(api_data, inputs):
  start = inputs['start_date']
  end = inputs['end_date']

  #FUNCTION:
  # 1. intraday     } --> must also match time of day
  # 2. daily          |
  # 3. weekly         |--> same format
  # 4. monthly        |
  pattern = '%Y-%m-%d'
  if inputs['time_series'] == FUNCTION['1']: # if it's intraday
    pattern = pattern + ' %H:%M:%S' # adjust pattern to match time of day

  # variables for simplicity
  try:
    dates_key = list(api_data.keys())[1]  # key corresponding to the value for the list of data entries
    dates_dict = api_data[dates_key]  # make new dict to hold the dates
  except Exception:
    print('An error occurred retrieving data from the API. No data sent...')
    return {}
  

  # remove dates from dates_dict as specified by start and end
  for key in list(dates_dict.keys()): # list(<>.keys()) for iterating over keys. Note that dates_dict is still the entire dict of objects
    try:
      current_key = datetime.strptime(key, pattern)
      if current_key.date() < start or current_key.date() > end:
        dates_dict.pop(key)
    except Exception:
      print('exception occured on data entry: ', key)
      continue

  return dates_dict




#function to render graph in browser
def render_graph(data, inputs):
  # Created arrays to hold data
  dates = []
  open_data = []
  high_data = []
  low_data = []
  close_data = []

  # Looped through the data and added values to arrays
  for x in data:
    dates.append(x)
    open_data.append(float(data[x]['1. open']))
    high_data.append(float(data[x]['2. high']))
    low_data.append(float(data[x]['3. low']))
    close_data.append(float(data[x]['4. close']))

  # Reversed the arrays so they are in ascending order
  dates.reverse()
  open_data.reverse()
  high_data.reverse()
  low_data.reverse()
  close_data.reverse()

  # Selected Graph Type based of the Inputs array from user_input.py
  if(inputs["graph_type"].upper() == "BAR"):
    line_chart = pygal.Bar()
  elif(inputs["graph_type"].upper() == "LINE"):
    line_chart = pygal.Line()   
  else:
    print("Invalid graph choice")

  # Added Data to Chart and Rendered Graph in browser
  line_chart.title = "Stock Prices for $" + inputs['stock_symbol']
  line_chart.x_labels = map(str, dates)
  line_chart.add('Open', open_data)
  line_chart.add('High', high_data)
  line_chart.add('Low', low_data)
  line_chart.add('Close', close_data)
  line_chart.render_in_browser()
  return

  

API_KEY = "NDN2S8ZUZVMFC79X"

