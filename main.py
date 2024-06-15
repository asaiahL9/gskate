import requests
from bs4 import BeautifulSoup
import json
import sqlite3
# from rich import print
from tqdm import tqdm
import re
import os

l_initial = "a"

# regular expressions to extract necessary data
patterns = {
    "Sponsors": r"Sponsors: ?([^\r\n]+)?",
    "Hometown": r"Hometown: ?([^,]+)?,",
    "Stance": r"Stance: ?([^,]+)?,",
    "Age": r"Age: ?(\d+)?,",
    "Status": r"Status: ?([^\r\n]+)?"
}

# database connection
conn = sqlite3.connect('skaters.db')
cursor = conn.cursor()

# Function: inc_char
# increments char by one. 
# Example: a -> b, b-> c, etc.
# Returns: char
def inc_char(char):
    i = ord(char[0]) # Convert the character 'a' to its ASCII value
    i += 1           # Increment the ASCII value by 1
    char = chr(i)    # Convert the incremented ASCII value back to a character

    return char     

# Function: get_attr
# extracts info from a skater profile like 
# Stance, and Sponsors, Hometown
# Returns: Dictionary
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

# requesting info from website
for char in tqdm(range(ord('a'), ord('z') + 1)):
    url = f'https://skateparkoftampa.com/spot/sd.aspx?L={l_initial}'
    print(f'\nCURRENT LETTER {l_initial}')
    l_initial = inc_char(l_initial)
        # print(l_initial)

    response = requests.get(url) # requesting website data
    html_content = response.content # extracting website html
    soup = BeautifulSoup(html_content, 'html.parser') # #parsing html content


    # finding skater names on website
    table = soup.find_all('div', class_ = "col-xs-6 col-sm-4 skaternames")
    # print(table)
    i = 0
    # collecting, cleaning, and parsing extracted skateboarder data
    for div in tqdm(table):
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
  
        if attributes['Hometown'].strip() == "":
            hometown = None
        else:
            hometown = attributes['Hometown'].strip()

        stance = attributes['Stance']
        if attributes["Age"]:
            age = attributes['Age']

        status = attributes['Status']
        
        # SQL query storing data in the sqlite database
        query = query = f'''INSERT INTO SKATER (FIRST_NAME, LAST_NAME, AGE, STANCE, HOMETOWN, STATE, SPONSORS, STATUS, SPOT_LINK) 
                       VALUES 
                       (?,?,?,?,?,?,?,?,?)'''
        # query values to be inserted
        values = (skater_name.split()[0], skater_name.split()[1], age if age is not None else 'NULL', stance, 
                       ' '.join(hometown.split()[:-1]) if hometown is not None else 'NULL', hometown.split()[-1] if hometown is not None else 'NULL', 
                       sponsors, status, skater_link) 

        # printing values to the screen
        print(values)
        # write values to db
        cursor.execute(query,values)

        # counter to log db entries each run
        i+=1
        
        print(f"{i} SKATERS ADDED TO DATABASE")
    # commit data to database after each letter is complete
    conn.commit()
# close database
cursor.close()
conn.close()