from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import re

## start the driver and input our initial url
url = 'https://www.homedepot.com/l/storeDirectory'
try: 
    driver = webdriver.Chrome()
    driver.get(url)
    print("Inital Page Successfully Loaded")
except: 
    print("Uh oh! Couldn't grab the requested URL")
    driver.close()

## declare an empty list to fill up with state/territory names
state_names = []


## create a function to format our state ids into useable urls for the driver
def get_url(state_name):
    template = 'https://www.homedepot.com/l/{}'
    return template.format(state_name)

##parse the landing page with beautiful soup, extract the items we need
soup = BeautifulSoup(driver.page_source, 'html.parser')
results = soup.find_all('li', class_='stateList__item')
#iterate through containers and grab the state ids
for result in results:
    clk = result.find('a', attrs={'href' : re.compile("^/l/")})
    state_names.append(clk.get('href')[3:5])
list_length = int(len(state_names)/2)
print("successfully grabbed", list_length, "states and territories")

# lets prepare our master lists of store information
store_names=[]
store_numbers =[]
store_address = []
store_zip = []
store_state = []

## this is the meat of the process, this cycles through the states/territories we grabbed, uses the function to format them into links
## opens them and scrapes the relevant store information using html classes and regular expressions
for x in range(list_length):
    ph = get_url(state_names[x])
    driver.get(ph)
    statesoup = BeautifulSoup(driver.page_source, 'html.parser') #using beautiful soup may be a misuse of selenium, but for this purpose it works
    page = statesoup.find('ul', class_='col__12-12 storeList') #isolate the part of the page we want
    stores = page.find_all('li', class_='storeList__item') #returns all store information
    for store in stores:
        store_names.append(store.a.text) #store name is relatively simple
        store_state.append(state_names[x])
        try: 
            clky = store.find('a', attrs={'href': re.compile('^/l/')}) #the store number is contained in the url
            store_nummy = re.findall(('[0-9]+$'), clky.get('href')) #we get a one object list of the store id
            store_numbers.append(store_nummy[0]) #we isolate the object from the list and append it to the master list
        except: store_numbers.append("null")
        ##the try and except "null" portions help us keep the list congruent with other entries in case there are any unexpected errors
        ##there are two stores without store numbers, which makes the one above especially useful
        try: 
            store_ad = re.findall(('(?<=\>).*(?=\<)'), str(store.ul.find_all('li')[0]))
            store_address.append(store_ad[0])
        except: store_address.append("null")
        # every store should have an address, but in case something changes that breaks the code it's good to have these try/except portions
        try: 
            zippy = re.findall(('[0-9]+'), str(store.ul.find_all('li')[1]))
            store_zip.append(zippy[0])
        except: store_zip.append("null")
#print to the console that everything above worked
print("Filled Master Lists")
#now lets close our webdriver, it's served us well!
driver.quit()

#import pandas and numpy to make a dataframe for store information
import pandas as pd
import numpy as np

#lets add the master lists to a pandas data frame
homedepots = pd.DataFrame({
    'StoreNum' : store_numbers,
    'Name' : store_names,
    'Address' : store_address,
    'ZipCode' : store_zip,
    'StoreState' : store_state
})
#verify our dataframe was created, then write it to a csv file
if homedepots.empty == False:
    print("Created DataFrame Successfully!")
    with open("homedepotlist.csv", "w") as my_home_depot_list:
        homedepots.to_csv(my_home_depot_list)
    print("CSV created! Enjoy!")
# if something went wrong, print an error to the console
if homedepots.empty == True:
    print("DataFrame failed to import values")