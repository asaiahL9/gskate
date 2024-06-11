import requests
from bs4 import BeautifulSoup
import json
import sqlite3
# from rich import print
from tqdm import tqdm
import re
import os

l_initial = "c"
patterns = {
    "Sponsors": r"Sponsors: ?([^\r\n]+)?",
    "Hometown": r"Hometown: ?([^,]+)?,",
    "Stance": r"Stance: ?([^,]+)?,",
    "Age": r"Age: ?(\d+)?,",
    "Status": r"Status: ?([^\r\n]+)?"
}


conn = sqlite3.connect('skaters.db')
cursor = conn.cursor()
def inc_char(char):
    i = ord(char[0]) # Convert the character 'a' to its ASCII value
    i += 1           # Increment the ASCII value by 1
    char = chr(i)    # Convert the incremented ASCII value back to a character
    # if char > 'z':
    #     print('Done')
    return char      # Print the new character

def get_attr(link):
    parsed_info = {}
    response = requests.get(link)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    info = soup.find('p').get_text()
    for key, pattern in patterns.items():
        match = re.search(pattern, info)
        if match:
            parsed_info[key] = match.group(1)   
    os.system('cls')
    # print(parsed_info) 
    
    return parsed_info

for char in tqdm(range(ord('a'), ord('z') + 1)):
    url = f'https://skateparkoftampa.com/spot/sd.aspx?L={l_initial}'
    print(f'\nCURRENT LETTER {l_initial}')
    l_initial = inc_char(l_initial)
        # print(l_initial)

    response = requests.get(url)
    html_content = response.content 
    soup = BeautifulSoup(html_content, 'html.parser')


    # find the appropriate tag that contains the weather data

    table = soup.find_all('div', class_ = "col-xs-6 col-sm-4 skaternames")
    # print(table)
    i = 0
    for div in tqdm(table):
        # os.system('cls')
        sponsors = None
        hometown = None
        stance = None
        age = None
        status = None
        skater_name = div.find('div', class_ = 'SizeSelectionGridItemSmall').get_text(strip=True)
        skater_link = div.find('a')['href']
        skater_title = div.find('a')['title']
        attributes = get_attr(skater_link)
        # print(
        sponsors = attributes['Sponsors']
        # if sponsors:
        #     if "'" in sponsors:
        #         sponsors = sponsors.replace("'", "\\'")
        # if attributes["Hometown"]:
        if attributes['Hometown'].strip() == "":
            hometown = None
        else:
            hometown = attributes['Hometown'].strip()
        # if hometown:
        #     if "'" in hometown:
        #         hometown = hometown.replace("'", "\\'")
        # if attributes["Stance"]:
        stance = attributes['Stance']
        if attributes["Age"]:
            age = attributes['Age']
        # if attributes["Status"]
        status = attributes['Status']
        
        # query = f'''INSERT INTO SKATER (FIRST_NAME, LAST_NAME, AGE, STANCE, HOMETOWN, STATE, SPONSORS, STATUS, SPOT_LINK) 
        #                VALUES 
        #                ('{skater_name.split()[0]}', '{skater_name.split()[1]}', {age if age is not None else 'NULL'}, '{stance}', 
        #                '{' '.join(hometown.split()[:-1]) if hometown is not None else 'NULL'}', '{hometown.split()[-1] if hometown is not None else 'NULL'}', 
        #                '{sponsors}', '{status}', '{skater_link}') '''
       
        query = query = f'''INSERT INTO SKATER (FIRST_NAME, LAST_NAME, AGE, STANCE, HOMETOWN, STATE, SPONSORS, STATUS, SPOT_LINK) 
                       VALUES 
                       (?,?,?,?,?,?,?,?,?)'''
        
        values = (skater_name.split()[0], skater_name.split()[1], age if age is not None else 'NULL', stance, 
                       ' '.join(hometown.split()[:-1]) if hometown is not None else 'NULL', hometown.split()[-1] if hometown is not None else 'NULL', 
                       sponsors, status, skater_link) 

        # print('STATEMENT: ', f'INSERT INTO SKATER (FIRST_NAME, LAST_NAME, AGE, STANCE, HOMETOWN, SPONSORS, STATUS, SPOT_LINK) VALUES ({skater_name.split()[0]}, {skater_name.split()[1]}, {age}, {stance}, {hometown}, {sponsors}, {status}, {skater_link} ;')
        print(values)

        cursor.execute(query,values)

        
        # print('added to db')
        i+=1
        
        print(f"{i} SKATERS ADDED TO DATABASE")
        # print('NAME:', skater_name, 'LINK:', skater_link, 'TITLE:', skater_title)
    conn.commit()
cursor.close()
conn.close()