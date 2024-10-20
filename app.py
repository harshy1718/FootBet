from flask import Flask, render_template, redirect, request, url_for
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

def Total(n):
    if (n / 7 >= 0.6):
        return 'Over 1.5'
    return 'Under 1.5'

def team1Total(n):
    if (n / 7 >= 0.67):
        return 'Over 0.5'
    return 'Under 0.5'

def team2Total(n):
    if (n / 7 >= 0.67):
        return 'Over 0.5'
    return 'Under 0.5'

def BTTS(n):
    if (n / 7 >= 0.67):
        return 'Yes'
    return 'No'

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        team1 = request.form['team1']
        team2 = request.form['team2']
        if team1 and team2:
            return redirect(url_for('Prediction', team1=team1, team2=team2))
        else:
            return render_template('error.html', error="Enter both the fields")
    return render_template('index.html')

@app.route("/Predict", methods=['GET', 'POST'])
def Prediction():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    
    results_dict = {
        'total': 0,
        'btts': 0,
        team1: 0,
        team2: 0
    }
    if (team2 < team1):
        team1, team2 = team2, team1
        
    t1 = team1.replace(" ", "-")
    t2 = team2.replace(" ", "-")

    options = Options()
    # options.add_argument("--headless=chrome")
    options.add_argument("--disable-gpu")  
    options.add_argument("--no-sandbox") 
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920x1080")  
    options.add_argument("--disable-dev-shm-usage")

    service = Service('D:\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe')

    driver = webdriver.Chrome(service=service, options=options)
    
    url = f"https://www.aiscore.com/head-to-head/soccer-{t1}-vs-{t2}"
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'table')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except Exception as e:
        driver.quit()
        return render_template('error.html', error=str(e))

    driver.quit()

    past_h2h = soup.find('h2', class_='title', text='Past H2H Results')
    table = past_h2h.find_next('div', class_='table') if past_h2h else None
    if table:
        rows = table.find_all('div', class_='w100 flex columnClassName')
        for row in rows[:7]:
            home_team = row.find(itemprop='homeTeam').get_text(strip=True)
            score = row.find('div', class_='cell w-100').find('a').get_text(strip=True)
            g1, g2 = score.split(' - ')
            g1 = int(g1)
            g2 = int(g2)
            if (g1 + g2 >= 2):
                results_dict['total'] += 1
            if (g1 >= 1 and g2 >= 1):
                results_dict['btts'] += 1
            if (g1 >= 1):
                if (home_team.lower() == team1.lower()):
                    results_dict[team1] += 1
                else:
                    results_dict[team2] += 1
            if (g2 >= 1):
                if (home_team.lower() == team1.lower()):
                    results_dict[team2] += 1
                else:
                    results_dict[team1] += 1
    else:
        return render_template('error.html', error = "The teams you entered are either incorrect or there is less data for prediction")
    total = Total(results_dict['total'])
    btts = BTTS(results_dict['btts'])
    t1total = team1Total(results_dict[team1])
    t2total = team2Total(results_dict[team2])
    
    return render_template('predict.html', team1=team1, team2=team2, total=total, btts=btts, t1total=t1total, t2total=t2total)

if __name__ == "__main__":
    app.run(debug=True)
