from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re

app = Flask(__name__)

def retrieve_attendance_data(username, date, month, year):
    url=r"https://parents.msrit.edu/"

    ser=Service(r"C:\Users\adith\OneDrive\Desktop\ABC\chromedriver_win64\chromedriver.exe")
    driver = webdriver.Chrome(service=ser)
    driver.get(url)

    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "dd").send_keys(date)
    driver.find_element(By.NAME, "mm").send_keys(month)
    driver.find_element(By.NAME, "yyyy").send_keys(year)
    driver.find_element(By.CSS_SELECTOR, "input[type=\"submit\" i]").click()
    url2 = driver.current_url
    driver.get(url2)

    html_text0 = driver.page_source
    html_text = html_text0.replace("&amp;", "&")
    soup = BeautifulSoup(html_text, "lxml")

    table = soup.find("table", class_="dash_od_row uk-table uk-table-striped uk-table-hover cn-pay-table uk-table-middle uk-table-responsive")

    rows = table.find_all("tr")
    indexes = []
    links = []
    link = []
    indexes2 = []
    atten = []
    for row in rows:
        link_tags = row.find_all("a")
        if len(link_tags) >= 2:
            link1 = link_tags[2].get("href")
            link2 = link_tags[3].get("href")
            links.append(link1)
            links.append(link2)
    for i in links:
        i = r"https://parents.msrit.edu/parentseven/" + str(i)
        link.append(i)
    print(link)
    Present = []
    Absent = []
    Still_To_Go = []
    for i in range(0, len(link), 2):
        driver.get(link[i])
        att = driver.page_source
        soup2 = BeautifulSoup(att, "lxml")
        try:
            div = soup2.find("div", class_="cn-legend").text
            indices = [match.start() for match in re.finditer(r'\[', div)]
            indices2 = [match.start() for match in re.finditer(r'\]', div)]
            indexes.extend(indices)
            indexes2.extend(indices2)
            Present.append(int(div[indices[0] + 1:indices2[0]]))
            if indices[1] < indices2[1]:
                absent_str = div[indices[1] + 1:indices2[1]]
            if absent_str:
                Absent.append(int(absent_str))
            else:
                Absent.append(0)
            Still_To_Go.append(int(div[indices[2] + 1:indices2[2]]))
        except:
            Present.append(0)
            Absent.append(0)
            Still_To_Go.append(0)
    print(Present)
    print(Absent)
    print(Still_To_Go)

    sub = {0: "AI41/MATHS", 1: "HSB492/CONSTITUTION", 2: "INT411/INTERNSHIP", 3: "AI44/THEORY_OF_COMPUTATION", 4: "AI45/ML", 5: "AIL46/ALGO_LAB", 6: "AIL47/ML_LAB", 7: "AIL48/PY_LAB", 8: "AI42/DCN", 9: "AI43/DAA", 10: 'AEC'}
    lessthan = []
    BOLD = '\033[1;1m'
    RESET = '\033[0m'
    result = ""
    for i in range(len(Present)):
        try:
            result += f"Your attendance in subject {sub[i]} is {(Present[i] * 100 // (Present[i] + Absent[i]))}%."
            result+=f"You can miss {int((Present[i]+Absent[i]+Still_To_Go[i])*0.25)-int(Absent[i])} classes in future.\n"
            lessthan.append((Present[i] * 100 // (Present[i] + Absent[i])))
            if int((Present[i] * 100 // (Present[i] + Absent[i]))) < 75:
                result += "Make sure to attend classes regularly.\n\n"
        except ZeroDivisionError :
            result += f"No data about {sub[i]}.\n"
        

    driver.quit()
    print(result)

    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_attendance', methods=['GET'])
def get_attendance():
    username = request.args.get('username')
    date = request.args.get('date')
    month = request.args.get('month')
    year = request.args.get('year')

    result = retrieve_attendance_data(username, date, month, year)

    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True,port=5000)
