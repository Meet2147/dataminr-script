###########################################################################################################################################

## Imports
from selenium import webdriver
import re
import time
import pandas as pd

## Open auto-browser window
bot = webdriver.chrome.webdriver.WebDriver()
bot.set_page_load_timeout(360)
bot.maximize_window()

###########################################################################################################################################

## Load GMail webpage
bot.get("https://mail.google.com/")
time.sleep(3)

## Read credentials file
with open('dm.txt') as file:
    file.seek(0)
    lines = file.readlines()
    
## Type in the EMAIL ID... ### //*[@id="identifierId"]
bot.find_element_by_xpath("""//*[@id="identifierId"]""").send_keys(lines[0][:-1])

## Press 'Next'...         ### //*[@id="identifierNext"]/span
bot.find_element_by_xpath("""//*[@id="identifierNext"]/span""").click()
time.sleep(3)

## AUTHENTICATION STEP
# key = input("Enter Access Key: ")
# while key!=lines[1][:-1]:
#     key = input("\nWrong Key!\nPlease enter correct Key: ")

## Type in the PASSWORD... ### //*[@id="password"]/div[1]/div/div[1]/input
bot.find_element_by_xpath("""//*[@id="password"]/div[1]/div/div[1]/input""").send_keys(lines[2])

## Press 'Next'...         ### //*[@id="passwordNext"]/span
bot.find_element_by_xpath("""//*[@id="passwordNext"]/span""").click()

## Wait 10s for successful login...
time.sleep(5)

###########################################################################################################################################

## LASSIPORA
lassi = re.findall("""class="TO" id="(.{,4})" data-tooltip="Lassipora" """, bot.page_source)[0]
bot.find_element_by_id(lassi).click()
time.sleep(5)

###########################################################################################################################################

def correct(obj):
    diff = len(obj)-50
    if diff>0:
        obj = obj[diff:]
    return obj

def getConte():
    r = re.findall('''role="listitem".+?id="(.+?)"''', bot.page_source)
    if len(r) > 1:
        for rs in r[:-1]:
            bot.find_element_by_id(rs).click()
    split = bot.find_element_by_class_name('aAX').text.split('\n')
    split = [each.strip() for each in split]
    for i, one in enumerate(split):
        yus = re.findall('''(\d{2}:\d{2}.+?IST).+?(\w+)''', one)
        if yus:
            loc = split[i-1]
    Split = [each for each in split if len(each.split())>=4]
    heff, pulw, shop, seim, tral, wanp, tops = 'N.A.', 'N.A.', 'N.A.', 'N.A.', 'N.A.', 'N.A.', 'N.A.'
    flag = False
    content=''
    end = None
    details = ''
    done = False
    j=1
    for i, one in enumerate(Split):
        ################################################################################# HEADER
        if j==1:
            yus = re.findall('''\[.+?\].+?(\w+ .+)''', one)
            header = yus[0]
            j+=1
        ################################################################################# ALERT, CLOSEST
        if j==2:
            yus = re.findall('''(\w{5,6} \w{,6}) {,1}\d{1,2}\.{,1}\d{0,2} mi from (\w+)''', one)
            if yus:
                aTag = ''.join([x for x in yus[0][0] if x.isalpha() or x == ' '])
                aTag = aTag.upper().strip()
                cSpot = yus[0][1]
                j+=1
        ################################################################################# TIME, SOURCE
        if j==3:
            yus = re.findall('''(\d{2}:\d{2}.+?IST).+?(\w+)''', one)
            if yus:
                tStamp = yus[0][0]
                src = yus[0][1]
                j+=1
        ################################################################################# LOCDATA
        if j>=4 and j<10:
            yus = re.findall('''\d{1,2}.\d{1,2} mi from \w+''', one)
            if yus:
                if 'Heff' in yus[0]:
                    heff = yus[0].split()[0]
                    j+=1
                    start = i
                elif 'Pulwama' in yus[0]:
                    pulw = yus[0].split()[0]
                    j+=1
                    start = i
                elif 'Shopian' in yus[0]:
                    shop = yus[0].split()[0]
                    j+=1
                    start = i
                elif 'Siemens' in yus[0]:
                    seim = yus[0].split()[0]
                    j+=1
                    start = i
                elif 'Tral' in yus[0]:
                    tral = yus[0].split()[0]
                    j+=1
                    start = i
                elif 'Wanpoh' in yus[0]:
                    wanp = yus[0].split()[0]
                    j+=1
                    start = i
        ################################################################################# CONTENT
        if re.findall('''\d{1,2}.\d{1,2} mi from \w+''', one):
            flag = False
        if flag:
            content += one + ' '
        if one == header:
            flag = True
        ################################################################################# TOPICS
        if one[:7] == 'Topics:':
            tops = one[8:]
            end = i
        ################################################################################# MORE CONTENT (DETAILS)
        if end and not done:
            for k in range(start+1, end):
                details += Split[k] + ' '
                done = True
    return tStamp, src, loc, aTag, tops, cSpot, header, content + details.strip(), heff, pulw, shop, seim, tral, wanp

def getLinks():
    links = re.findall("""button" href="(.+?)".""", bot.page_source)
    ExtLink, DMLink, DMTLink = 'N.A.', 'N.A.', 'N.A.'
    for each in links:
        if 'dataminr' in each:
            if 'track' in each:
                DMTLink = each
            else:
                DMLink = each
        else:
            ExtLink = each
    return ExtLink, DMLink, DMTLink

###########################################################################################################################################

columns = ['TStamp', 'Source', 'Location', 'AType', 'Topics', 'NearestTo', 'Headline', 'Content',
           'd(Heff)', 'd(Pulwama)', 'd(Shopian)', 'd(Siemens)', 'd(Tral)', 'd(Wanpoh)',
           'ExtLink', 'DMLink', 'DMTLink']
data = pd.DataFrame(columns = columns)
edat = [[None, None, None, None, None, None, None,
         None, None, None, None, None, None,
         None, None, None, None]]

t0 = time.time()

while time.time()-t0<180:
    for i in range(5):
        Ids = re.findall("""<tr class="zA yO".+?id="(.{,5})" """, bot.page_source)
        Ids = correct(Ids)
        bot.find_element_by_id(Ids[i]).click()
        time.sleep(3)
        edat[0][0], edat[0][1], edat[0][2], edat[0][3], edat[0][4], edat[0][5], edat[0][6], edat[0][7], edat[0][8], edat[0][9], edat[0][10],edat[0][11], edat[0][12], edat[0][13] = getConte()
        edat[0][14], edat[0][15], edat[0][16] = getLinks()
        entry = pd.DataFrame(edat, columns = columns)
        data = data.append(entry)
        bot.back()
        
        og = pd.read_csv('omega.csv')
        og = og.append(data, sort=False)
        
        og.reset_index(inplace=True)
        og.drop('index', axis=1, inplace=True)
        og = og.drop_duplicates()
        
        data.to_csv('omega.csv', index=False)
        
        bot.back()
        
        lassi = re.findall("""class="TO" id="(.{,4})" data-tooltip="Lassipora" """, bot.page_source)[0]
        bot.find_element_by_id(lassi).click()
        time.sleep(5)

#     bot.find_element_by_class_name('asa').click()

bot.quit()

##################################################################################################################