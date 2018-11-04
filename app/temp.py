from bs4 import BeautifulSoup
import requests
import sqlite3

meal_table = sqlite3.connect('meal_table.db', check_same_thread=False)
month = ['Zeronull','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

c = meal_table.cursor()
try:
    for i in month:
            c.execute("""CREATE TABLE {}(
                        day integer,
                        lunch text,
                        dinner text)""".format(i))
except sqlite3.OperationalError:
    print("Table already exists, Skipping...")


# 중식 r1, 석식 r2
r1 = requests.get(
    "https://stu.sen.go.kr/sts_sci_md00_001.do?schulCode=B100005528&schMmealScCode=2&schulCrseScCode=4")

c1 = r1.content

html1 = BeautifulSoup(c1, "html.parser")

tr1 = html1.find_all('tbody')

td1 = tr1[0].find_all('td')
table = []
for i in range(35):
    table.append(list(map(str, str(td1[i].find('div')).replace('<div>', '').replace('</div>','').replace('&amp;',',',-1).split('<br/>'))))


for i in range(len(table)):
    # 월초여백, 월말여백
    isLunch = 0
    if len(table[i]) == 1:
        continue
    else:
        for j in range(len(table[i])):
            if j == 0:
                day = table[i][j]
                continue
            if table[i][j] == '[중식]':
                isLunch = True
            if table[i][j] == '[석식]':
                isLunch = False
            if isLunch == True and table[i][j] != '[중식]':
                c.execute("INSERT INTO {} (day, lunch) VALUES (?, ?)".format(month[11]), (day, table[i][j],))
                meal_table.commit()
            if isLunch == 0 and table[i][j] != '[석식]':
                c.execute("INSERT INTO {} (day, dinner) VALUES (?, ?)".format(month[11]), (day, table[i][j],))
                meal_table.commit()
day = 5
c.execute("SELECT * FROM Nov WHERE day = 5")
print(c.fetchall())
