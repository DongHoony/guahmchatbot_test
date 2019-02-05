from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import urllib.request as ul
import xmltodict
import json
import time as t
import sqlite3
import datetime as dt

# Dump codes below
# BusStops, to School
# schoolBusStop13 = ['벽산아파트', '약수맨션', '노량진역', '대방역2번출구앞']
# schoolBusStop5513 = ['관악구청', '서울대입구', '봉천사거리, 봉천중앙시장', '봉현초등학교', '벽산블루밍벽산아파트303동앞']
# BusStop values, to School
# numBusStop13 = ['21910', '20891', '20867', '20834']
# numBusStop5513 = ['21130', '21252', '21131', '21236', '21247']

bus_db = sqlite3.connect('bus_key.db', check_same_thread=False)

try:
    c = bus_db.cursor()
    c.execute("""CREATE TABLE BusService (
                user_key text,
                bus_num integer,
                school_stn text,
                home_stn text)""")
except sqlite3.OperationalError:
    print("Table already exists, Skip making table...")

# BusStops, to Home
homeBusStop13 = ['관악드림타운북문 방면 (동작13)', '벽산아파트 방면 (동작13)']
homeBusStop5513 = ['관악드림타운북문 방면 (5513)', '벽산아파트 방면 (5513)']
homeBusStop01 = ['관악드림타운북문 방면 (관악01)', '벽산아파트 방면 (관악01)']

# Setting lines
setting13 = ['대방역2번출구앞 (설정)', '현대아파트 (설정)', '노량진역 (설정)', '우성아파트 (설정)', '건영아파트 (설정)', '신동아상가 (설정)',
             '동작등기소 (설정)', '부강탕 (설정)', '밤골 (설정)', '약수맨션 (설정)', '빌라삼거리, 영도교회 (설정)', '방범초소 (설정)', '벽산아파트 (설정)']
setting5513 = ['관악구청 (설정)', '서울대입구 (설정)', '봉천사거리, 봉천중앙시장 (설정)', '봉원중학교, 행운동우성아파트 (설정)',
               '관악푸르지오아파트 (설정)', '봉현초등학교 (설정)', '벽산블루밍벽산아파트303동앞 (설정)']
setting01 = ['봉천역 (설정)', '두산아파트입구 (설정)', '현대시장 (설정)', '구암초등학교정문 (설정)', '성현동주민센터 (설정)', '구암어린이집앞 (설정)',
             '숭실대입구역2번출구 (설정)', '봉천고개현대아파트 (설정)', '봉현초등학교_01 (설정)', '관악드림타운115동 (설정)']

bus_stn_dict_13 = {'대방역2번출구앞': ['20834', 2], '현대아파트': ['20007', 2], '노량진역': ['20867', 1],
                   '우성아파트': ['20878', 1], '건영아파트': ['20894', 0], '신동아상가': ['20897', 0],
                   '동작등기소': ['20730', 2], '부강탕': ['20913', 0], '밤골': ['20918', 0], '약수맨션': ['20891', 1],
                   '빌라삼거리, 영도교회': ['20922', 0], '방범초소': ['20924', 0], '벽산아파트': ['21910', 0]}
bus_stn_dict_5513 = {'관악구청': ['21130', 5], '서울대입구': ['21252', 1], '봉천사거리, 봉천중앙시장': ['21131', 7],
                     '봉원중학교, 행운동우성아파트': ['21132', 8], '관악푸르지오아파트': ['21133', 7], '봉현초등학교': ['21236', 2],
                     '벽산블루밍벽산아파트303동앞': ['21247', 0]}
bus_stn_dict_01 = {'봉천역': ['21508', 0], '두산아파트입구': ['21526', 0], '현대시장': ['21536', 0], '구암초등학교정문': ['21545', 0],
                   '성현동주민센터': ['21565', 0], '구암어린이집앞': ['21575', 0], '숭실대입구역2번출구': ['20810', 0],
                   '봉천고개현대아파트': ['20820', 0], '봉현초등학교_01': ['21236', 0], '관악드림타운115동': ['21239', 0]}

# Meal table, index(0-4) => Mon-Fri
lunch = []
dinner = []

# n은 xml상에서 봤을 때 itemList 순서임, index이므로 0부터 시작.
def bus(n, busStn, busNo):
    print("Attempt to get the {}, {}, {} bus info...".format(n, busStn, busNo))
    url = 'http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid?ServiceKey=fef2WSoMFkV557J%2BKKEe0LmP4Y1o8IsH6x4Lv4p0pArUHTs6sk6sHVGaNfkFZRM2sSUn5Uvw0JzETmEyk5VeoA%3D%3D&arsId=' + busStn
    request = ul.Request(url)
    response = ul.urlopen(request)
    rescode = response.getcode()

    # URL에 정상적으로 접근했을 시 rescode의 값은 200이 된다.
    if rescode == 200:
        responseData = response.read()
        rD = xmltodict.parse(responseData)
        rDJ = json.dumps(rD)
        rDD = json.loads(rDJ)
        busrDD = rDD["ServiceResult"]["msgBody"]["itemList"]

        if len(busrDD) > 30:
            bus01 = busrDD["arrmsg1"]
            bus02 = busrDD["arrmsg2"]
            id01 = busrDD["vehId1"]
            id02 = busrDD["vehId2"]

        else:
            bus01 = busrDD[n]["arrmsg1"]
            bus02 = busrDD[n]["arrmsg2"]
            id01 = busrDD[n]["vehId1"]
            id02 = busrDD[n]["vehId2"]

        bus01 = '곧' if bus01 == '곧 도착' else bus01
        bus01 = bus01.replace('분', '분 ').replace('초후', '초 후 ').replace('번째', ' 정류장')
        bus01 = '전 정류장 출발' if bus01 == '0 정류장 전' else bus01
        bus02 = bus02.replace('분', '분 ').replace('초후', '초 후 ').replace('번째', ' 정류장')

        # 동작13과 5513의 리턴값이 다르다, 타요버스가 없으니까 타요 제외.
        if busNo == 13:
            tayoList = ['24', '57', '58', '92', '95']
            tayo1 = '이번 버스는 타요차량입니다.' if id01[-2:] in tayoList else '이번 버스는 일반차량입니다.'
            tayo2 = '다음 버스는 타요차량입니다.' if id02[-2:] in tayoList else '다음 버스는 일반차량입니다.'
            if bus01 in ['출발대기', '운행종료']:
                tayo1 = ''
            if bus02 in ['출발대기', '운행종료']:
                tayo2 = ''
            return [bus01, bus02, tayo1, tayo2]

        elif busNo in [5513, 1]:
            return [bus01, bus02]


isRefreshed = 0
updatedtime = 0
bus_stn_setting_list = []
isSetting = False
settingTime = 0


def foodie(n):
    global isRefreshed, updatedtime, lunch, dinner
    print("Attempting to access in Meal table, Updated = {}".format(['False', 'True'][isRefreshed]))
    y, m, d = map(str, str(dt.datetime.now())[:10].split('-'))
    # 2018.10.29 형식
    ymd = y + '.' + m + '.' + d
    currenttime = int(t.time())
    dayList = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekendRefresh = 0
    # 일요일, 새로고침되지 않았을 때 실행 (다른 방법 필요할듯, 업데이트 날짜 가져와서 7일 내이면 넘기고, 아니면 업데이트 하는 식으로)
    # food함수 내에는 고쳐질 게 많다. 토요일, 일요일에 리턴하는 0값을 처리해야 함.
    # 또, 방학이나 공휴일처럼 평일이지만 배식하지 않는 경우를 추가해줘야 함.
    # -> 500000초 (약 5.7일) 초과 시 자동 업데이트, 단 foodie 함수가 활성화돼야 함

    print("Time elasped after task built : {}".format(currenttime - updatedtime))
    if currenttime - updatedtime > 500000 or isRefreshed == 0 or lunch == []:
        
        print('Getting meals, wait for moment...')
        from bs4 import BeautifulSoup
        import requests
        # 중식 r1, 석식 r2
        r1 = requests.get(
            "http://stu.sen.go.kr/sts_sci_md01_001.do?"
            "schulCode=B100005528&schMmealScCode=2&schulCrseScCode=4&schYmd=" + ymd)
        r2 = requests.get(
            "http://stu.sen.go.kr/sts_sci_md01_001.do?"
            "schulCode=B100005528&schMmealScCode=3&schulCrseScCode=4&schYmd=" + ymd)
        c1 = r1.content
        c2 = r2.content
        html1 = BeautifulSoup(c1, "html.parser")
        html2 = BeautifulSoup(c2, "html.parser")
        tr1 = html1.find_all('tr')
        td1 = tr1[2].find_all('td')
        tr2 = html2.find_all('tr')
        td2 = tr2[2].find_all('td')
        td1 = ["급식이 없습니다.\n" for i in range(7)] if td1 == [] else td1
        td2 = ["급식이 없습니다.\n" for i in range(7)] if td2 == [] else td2

        for i in range(1, 6):
            td1[i] = str(td1[i])
            td2[i] = str(td2[i])
            tempdish1 = td1[i].replace('<td class="textC">', '').replace('<br/>', '\n', -1).replace('</td>',
                                                                                                    '').replace('&amp;',
                                                                                                                ', ').replace(
                '\n', '\n- ', -1)
            dish1 = '- ======== -\n- '
            for _ in tempdish1:
                if _ in '1234567890.':
                    continue
                else:
                    dish1 += _

            tempdish2 = td2[i].replace('<td class="textC">', '').replace('<br/>', '\n', -1).replace('</td>',
                                                                                                    '').replace('&amp;',
                                                                                                                ', ').replace(
                '\n', '\n- ', -1)
            dish2 = '- ======== -\n- '
            for _ in tempdish2:
                if _ in '1234567890.':
                    continue
                else:
                    dish2 += _

            lunch.append(dish1 + '======== -')
            dinner.append(dish2 + '======== -')

        lunch += ['메뉴가 없습니다.'] * 2
        dinner += ['메뉴가 없습니다.'] * 2
        updatedtime = int(t.time())
        isRefreshed = 1
        if weekendRefresh == 0:
            weekendRefresh = 1
        print("Meal task has been built / refreshed!")

    # 주말에 함수 호출시에 리프레시 0으로 맞춰주자
    if n == 'Sun':
        if weekendRefresh == 0:
            isRefreshed = 0

    return [str(dayList.index(n)), m, d]


def keyboard(request):
    return JsonResponse(
        {
            'type': 'buttons',

            'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
        }
    )


@csrf_exempt
def message(request):
    global bus_stn_setting_list, bus_stn_dict_13, bus_stn_dict_5513, bus_stn_dict_01, isSetting, settingTime
    json_str = (request.body).decode('utf-8')
    received_json = json.loads(json_str)
    clickedButton = received_json['content']
    user_key = received_json['user_key']
    if clickedButton == '초기화면':
        print("User {} pushed '초기화면'".format(user_key))
        return JsonResponse(
            {
                'message': {
                    'text': '초기화면으로 돌아갑니다.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                }
            }
        )

    # Sets up the user_key based route from below
    # 등하굣길 설정은 bus_key.db에 데이터베이스형식으로 저장
    elif clickedButton == '내 등하굣길 설정하기':
        if not isSetting or t.time() - settingTime > 20:
            isSetting = True
            settingTime = t.time()
            if len(bus_stn_setting_list) != 0:
                bus_stn_setting_list = []
                print("Setting list is not empty, Cleaning up...")
            bus_stn_setting_list.append(user_key)
            return JsonResponse(
                {
                    'message': {
                        'text': 'Step 1 / 3: 버스를 선택해 주세요.'
                    },
                    'keyboard': {
                        'type': 'buttons',
                        'buttons': ['관악01 (설정)', '동작13 (설정)', '5513 (설정)']
                    }
                }
            )
        else:
            return JsonResponse(
                {
                    'message': {
                        'text': '현재 설정 중인 사용자가 있습니다. 잠시 후 다시 시도해 주세요.'
                    },
                    'keyboard': {
                        'type': 'buttons',
                        'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                    }
                }
            )

    elif clickedButton == '동작13 (설정)':
        bus_stn_setting_list.append(13)
        return JsonResponse(
            {
                'message': {
                    'text': 'Step 2 / 3: 등교 시 이용하는 버스정류장을 선택해 주세요.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['대방역2번출구앞 (설정)', '현대아파트 (설정)', '노량진역 (설정)', '우성아파트 (설정)', '건영아파트 (설정)', '신동아상가 (설정)',
                                '동작등기소 (설정)', '부강탕 (설정)', '밤골 (설정)', '약수맨션 (설정)', '빌라삼거리, 영도교회 (설정)', '방범초소 (설정)',
                                '벽산아파트 (설정)']
                }
            }
        )

    elif clickedButton == '5513 (설정)':
        bus_stn_setting_list.append(5513)
        return JsonResponse(
            {
                'message': {
                    'text': 'Step 2 / 3: 등교 시 이용하는 버스정류장을 선택해 주세요.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['관악구청 (설정)', '서울대입구 (설정)', '봉천사거리, 봉천중앙시장 (설정)', '봉원중학교, 행운동우성아파트 (설정)',
                                '관악푸르지오아파트 (설정)', '봉현초등학교 (설정)', '벽산블루밍벽산아파트303동앞 (설정)']
                }
            }
        )

    elif clickedButton == '관악01 (설정)':
        bus_stn_setting_list.append(1)
        return JsonResponse(
            {
                'message': {
                    'text': 'Step 2 / 3: 등교 시 이용하는 버스정류장을 선택해 주세요.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['봉천역 (설정)', '두산아파트입구 (설정)', '현대시장 (설정)', '구암초등학교정문 (설정)', '성현동주민센터 (설정)',
                                '구암어린이집앞 (설정)',
                                '숭실대입구역2번출구 (설정)', '봉천고개현대아파트 (설정)', '봉현초등학교_01 (설정)', '관악드림타운115동 (설정)']
                }
            }
        )

    elif clickedButton in setting01:
        bus_stn_setting_list.append(bus_stn_dict_01.get(clickedButton.replace(' (설정)', ''))[0])
        return JsonResponse(
            {
                'message': {
                    'text': 'Step 3 / 3: 하교방향을 선택해 주세요.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['벽산아파트방면 (설정)', '관악드림타운아파트방면 (설정)']
                }
            }
        )

    elif clickedButton in setting13:
        bus_stn_setting_list.append(bus_stn_dict_13.get(clickedButton.replace(' (설정)', ''))[0])
        return JsonResponse(
            {
                'message': {
                    'text': 'Step 3 / 3: 하교방향을 선택해 주세요.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['벽산아파트방면 (설정)', '관악드림타운아파트방면 (설정)']
                }
            }
        )

    elif clickedButton in setting5513:
        bus_stn_setting_list.append(bus_stn_dict_5513.get(clickedButton.replace(' (설정)', ''))[0])
        return JsonResponse(
            {
                'message': {
                    'text': 'Step 3 / 3: 하교방향을 선택해 주세요.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['벽산아파트방면 (설정)', '관악드림타운아파트방면 (설정)']
                }
            }
        )

    elif clickedButton in ['벽산아파트방면 (설정)', '관악드림타운아파트방면 (설정)']:
        bus_stn_setting_list.append(['21243', '21244'][['벽산아파트방면 (설정)', '관악드림타운아파트방면 (설정)'].index(clickedButton)])

        c = bus_db.cursor()

        c.execute("SELECT * FROM BusService WHERE user_key = ?", (bus_stn_setting_list[0],))
        if c.fetchall() != []:
            c.execute("DELETE FROM BusService WHERE user_key = ?", (bus_stn_setting_list[0],))
            print("This user already have the route, Deleting it ... ")

        c.execute("INSERT INTO BusService VALUES (?, ?, ?, ?)",
                  (bus_stn_setting_list[0], bus_stn_setting_list[1], bus_stn_setting_list[2], bus_stn_setting_list[3]))
        bus_db.commit()

        c.execute("SELECT * FROM BusService WHERE user_key = ?", (bus_stn_setting_list[0],))
        print(c.fetchall())
        print("User route has been successfully created. ^ ")
        isSetting = False
        return JsonResponse(
            {
                'message': {
                    'text': '설정되었습니다. 이제 간편하게 내 등하굣길 버스안내를 이용하실 수 있습니다.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                }
            }
        )
    # Setting user_key based route finished.

    elif clickedButton == '구암고 급식안내':
        return JsonResponse(
            {
                'message': {
                    'text': '중 / 석식을 선택해 주세요.\n매일 오후 5시 이후에는 다음날 급식을 안내합니다.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['중식', '석식', '초기화면']
                }
            }
        )

    elif clickedButton in ['중식', '석식']:
        tmr = 0
        flist = foodie(str(t.ctime())[:3])
        day, m, d = map(int, flist)
        print("User {} is trying to get meal task".format(user_key))
        if int(str(t.ctime())[11:13]) > 16:  # 5시가 지나면 내일 밥을 보여준다
            tmr = 1
            if day < 6:
                day += 1
            else:
                day = 0
        return JsonResponse(
            {
                'message': {
                    'text': '🍴 {}의 {}식단 🍴\n📜 {} / {} ( {} ) 📜\n{}'.format('오늘' if tmr == 0 else '내일',
                                                                              '중식' if clickedButton == '중식' else '석식',
                                                                              m, d if tmr == 0 else d + 1,
                                                                              '월화수목금토일'[day],
                                                                              lunch[day] if clickedButton == '중식' else
                                                                              dinner[day])
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                }
            }
        )

    elif clickedButton == '내 등굣길 버스안내':
        c = bus_db.cursor()
        c.execute("SELECT * FROM BusService WHERE user_key = ?", (user_key,))
        school = c.fetchone()
        if not school:
            return JsonResponse(
                {
                    'message': {
                        'text': '내 등/하굣길이 설정돼 있지 않습니다. 초기화면에서 설정해 주세요.'
                    },
                    'keyboard': {
                        'type': 'buttons',
                        'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                    }
                }
            )

        if school[1] == 13:
            for stn_name, stn_list in bus_stn_dict_13.items():
                if stn_list[0] == school[2]:
                    busStn, n = stn_name, stn_list[1]
                    break
            busList = bus(n, school[2], 13)
            bus01, bus02, tayo1, tayo2 = map(str, busList)
            return JsonResponse(
                {
                    'message': {
                        'text': '🚏 {} ( {} )\n\n이번 🚌 : {}{}\n{}\n\n다음 🚌 : {}{}\n{}'.format(busStn, school[2], bus01,
                                                                                              ' 도착 예정' if bus01 not in [
                                                                                                  '출발대기',
                                                                                                  '운행종료'] else '',
                                                                                              tayo1, bus02,
                                                                                              ' 도착 예정' if bus02 not in [
                                                                                                  '출발대기',
                                                                                                  '운행종료'] else '',
                                                                                              tayo2)

                    },
                    'keyboard': {
                        'type': 'buttons',
                        'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                    }
                }
            )
        elif school[1] == 5513:
            for stn_name, stn_list in bus_stn_dict_5513.items():
                if stn_list[0] == school[2]:
                    busStn, n = stn_name, stn_list[1]
                    break
            bus(n, school[2], 5513)
            busList = bus(n, school[2], 5513)
            bus01, bus02 = map(str, busList)
            return JsonResponse(
                {
                    'message': {
                        'text': '🚏 {} ( {} )\n\n이번 🚌 : {}{}\n\n다음 🚌 : {}{}\n'.format(busStn, school[2], bus01,
                                                                                        ' 도착 예정' if bus01 not in [
                                                                                            '출발대기', '운행종료'] else '',
                                                                                        bus02,
                                                                                        ' 도착 예정' if bus02 not in [
                                                                                            '출발대기', '운행종료'] else '')
                    },
                    'keyboard': {
                        'type': 'buttons',
                        'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                    }
                }
            )
        # 01
        else:
            for stn_name, stn_list in bus_stn_dict_01.items():
                if stn_list[0] == school[2]:
                    busStn, n = stn_name, stn_list[1]
                    break
            bus01, bus02 = map(str, bus(n, school[2], 1))
            return JsonResponse(
                {
                    'message': {
                        'text': '🚏 {} ( {} )\n\n이번 🚌 : {}{}\n\n다음 🚌 : {}{}\n'.format(busStn, school[2], bus01,
                                                                                        ' 도착 예정' if bus01 not in [
                                                                                            '출발대기', '운행종료'] else '',
                                                                                        bus02,
                                                                                        ' 도착 예정' if bus02 not in [
                                                                                            '출발대기', '운행종료'] else '')
                    },
                    'keyboard': {
                        'type': 'buttons',
                        'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                    }
                }
            )

    elif clickedButton == '내 하굣길 버스안내':
        c = bus_db.cursor()
        c.execute("SELECT * FROM BusService WHERE user_key = ?", (user_key,))
        school = c.fetchone()
        if not school:
            return JsonResponse(
                {
                    'message': {
                        'text': '내 등/하굣길이 설정돼 있지 않습니다. 초기화면에서 설정해 주세요.'
                    },
                    'keyboard': {
                        'type': 'buttons',
                        'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                    }
                }
            )
        if school[1] == 13:
            bus01, bus02, tayo1, tayo2 = map(str, bus(1, school[3], 13))
            return JsonResponse(
                {
                    'message': {
                        'text': '🚏 {} ( {} )\n\n이번 🚌 : {}{}\n{}\n\n다음 🚌 : {}{}\n{}'.format('구암중고등학교', school[3],
                                                                                              bus01,
                                                                                              ' 도착 예정' if bus01 not in [
                                                                                                  '출발대기',
                                                                                                  '운행종료'] else '',
                                                                                              tayo1, bus02,
                                                                                              ' 도착 예정' if bus02 not in [
                                                                                                  '출발대기',
                                                                                                  '운행종료'] else '',
                                                                                              tayo2)
                    },
                    'keyboard': {
                        'type': 'buttons',
                        'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                    }
                }
            )
        elif school[1] == 5513:
            busList = bus(2, school[3], 5513)
            bus01, bus02 = map(str, busList)
            return JsonResponse(
                {
                    'message': {
                        'text': '🚏 {} ( {} )\n\n이번 🚌 : {}{}\n\n다음 🚌 : {}{}\n'.format('구암중고등학교', school[3], bus01,
                                                                                        ' 도착 예정' if bus01 not in [
                                                                                            '출발대기', '운행종료'] else '',
                                                                                        bus02,
                                                                                        ' 도착 예정' if bus02 not in [
                                                                                            '출발대기', '운행종료'] else '')

                    },
                    'keyboard': {
                        'type': 'buttons',
                        'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                    }
                }
            )
        else:
            bus01, bus02 = map(str, bus(2, school[3], 1))
            return JsonResponse(
                {
                    'message': {
                        'text': '🚏 {} ( {} )\n\n이번 🚌 : {}{}\n\n다음 🚌 : {}{}\n'.format('구암중고등학교', school[3], bus01,
                                                                                        ' 도착 예정' if bus01 not in [
                                                                                            '출발대기', '운행종료'] else '',
                                                                                        bus02,
                                                                                        ' 도착 예정' if bus02 not in [
                                                                                            '출발대기', '운행종료'] else '')
                    },
                    'keyboard': {
                        'type': 'buttons',
                        'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                    }
                }
            )

    elif clickedButton == '등하교 버스안내':
        return JsonResponse(
            {
                'message': {
                    'text': '노선 및 방향을 선택해 주세요'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['초기화면', '관악01 - 등교', '관악01 - 하교', '동작13 - 등교', '동작13 - 하교', '5513 - 등교', '5513 - 하교']
                }
            }
        )

    elif clickedButton == '5513 - 등교':
        return JsonResponse(
            {
                'message': {
                    'text': '정류장을 선택해 주세요.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['초기화면', '관악구청', '서울대입구', '봉천사거리, 봉천중앙시장', '봉원중학교, 행운동우성아파트',
                                '관악푸르지오아파트', '봉현초등학교', '벽산블루밍벽산아파트303동앞']
                }
            }
        )

    elif clickedButton == '동작13 - 등교':
        return JsonResponse(
            {
                'message': {
                    'text': '정류장을 선택해 주세요.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['초기화면', '대방역2번출구앞', '현대아파트', '노량진역', '우성아파트', '건영아파트', '신동아상가',
                                '동작등기소', '부강탕', '밤골', '약수맨션', '빌라삼거리, 영도교회', '방범초소', '벽산아파트']

                }
            }
        )

    elif clickedButton == '관악01 - 등교':
        return JsonResponse(
            {
                'message': {
                    'text': '정류장을 선택해 주세요.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['초기화면', '봉천역', '두산아파트입구', '현대시장', '구암초등학교정문', '성현동주민센터', '구암어린이집앞',
                                '숭실대입구역2번출구', '봉천고개현대아파트', '봉현초등학교_01', '관악드림타운115동']
                }
            }
        )

    if clickedButton in bus_stn_dict_13.keys():
        busStop, n = map(str, bus_stn_dict_13.get(clickedButton))
        busList = bus(int(n), busStop, 13)
        bus01, bus02, tayo1, tayo2 = map(str, busList)

        return JsonResponse(
            {
                'message': {
                    'text': '🚏 {} ( {} )\n\n이번 🚌 : {}{}\n{}\n\n다음 🚌 : {}{}\n{}'.format(clickedButton, busStop, bus01,
                                                                                          ' 도착 예정' if bus01 not in [
                                                                                              '출발대기', '운행종료'] else '',
                                                                                          tayo1, bus02,
                                                                                          ' 도착 예정' if bus02 not in [
                                                                                              '출발대기', '운행종료'] else '',
                                                                                          tayo2)

                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                }
            }
        )

    if clickedButton in bus_stn_dict_5513.keys():
        busStop, n = map(str, bus_stn_dict_5513.get(clickedButton))
        busList = bus(int(n), busStop, 5513)
        bus01, bus02 = map(str, busList)
        return JsonResponse(
            {
                'message': {
                    'text': '🚏 {} ( {} )\n\n이번 🚌 : {}{}\n\n다음 🚌 : {}{}\n'.format(clickedButton, busStop, bus01,
                                                                                    ' 도착 예정' if bus01 not in ['출발대기',
                                                                                                              '운행종료'] else '',
                                                                                    bus02,
                                                                                    ' 도착 예정' if bus02 not in ['출발대기',
                                                                                                              '운행종료'] else '')
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                }
            }
        )

    if clickedButton in bus_stn_dict_01.keys():
        busStop, n = map(str, bus_stn_dict_01.get(clickedButton))
        busList = bus(int(n), busStop, 1)
        bus01, bus02 = map(str, busList)
        return JsonResponse(
            {
                'message': {
                    'text': '🚏 {} ( {} )\n\n이번 🚌 : {}{}\n\n다음 🚌 : {}{}\n'.format(clickedButton, busStop, bus01,
                                                                                    ' 도착 예정' if bus01 not in ['출발대기',
                                                                                                              '운행종료'] else '',
                                                                                    bus02,
                                                                                    ' 도착 예정' if bus02 not in ['출발대기',
                                                                                                              '운행종료'] else '')
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                }
            }
        )

    # No need to touch below, Final

    elif clickedButton == '동작13 - 하교':

        return JsonResponse(
            {
                'message': {
                    'text': '동작13 버스 방향을 선택해 주세요.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['관악드림타운북문 방면 (동작13)', '벽산아파트 방면 (동작13)', '초기화면']
                }
            }
        )

    elif clickedButton == '5513 - 하교':

        return JsonResponse(
            {
                'message': {
                    'text': '5513 버스 방향을 선택해 주세요.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['관악드림타운북문 방면 (5513)', '벽산아파트 방면 (5513)', '초기화면']
                }
            }
        )

    elif clickedButton == '관악01 - 하교':
        return JsonResponse(
            {
                'message': {
                    'text': '관악01 버스 방향을 선택해 주세요.'
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['관악드림타운북문 방면 (관악01)', '벽산아파트 방면 (관악01)', '초기화면']
                }
            }
        )

    elif clickedButton in homeBusStop13:
        busStop = ['21244', '21243'][homeBusStop13.index(clickedButton)]
        busList = bus(1, busStop, 13)
        bus01, bus02, tayo1, tayo2 = map(str, busList)
        return JsonResponse(
            {
                'message': {
                    'text': '🚏 {} ( {} )\n\n이번 🚌 : {}{}\n{}\n\n다음 🚌 : {}{}\n{}'.format(clickedButton, busStop, bus01,
                                                                                          ' 도착 예정' if bus01 not in [
                                                                                              '출발대기', '운행종료'] else '',
                                                                                          tayo1, bus02,
                                                                                          ' 도착 예정' if bus02 not in [
                                                                                              '출발대기', '운행종료'] else '',
                                                                                          tayo2)
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                }
            }
        )

    elif clickedButton in homeBusStop5513:
        busStop = ['21244', '21243'][homeBusStop5513.index(clickedButton)]
        busList = bus(2, busStop, 5513)
        bus01, bus02 = map(str, busList)
        return JsonResponse(
            {
                'message': {
                    'text': '🚏 {} ( {} )\n\n이번 🚌 : {}{}\n\n다음 🚌 : {}{}\n'.format(clickedButton, busStop, bus01,
                                                                                    ' 도착 예정' if bus01 not in ['출발대기',
                                                                                                              '운행종료'] else '',
                                                                                    bus02,
                                                                                    ' 도착 예정' if bus02 not in ['출발대기',
                                                                                                              '운행종료'] else '')

                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                }
            }
        )

    elif clickedButton in homeBusStop01:
        busStop = ['21244', '21243'][homeBusStop01.index(clickedButton)]
        busList = bus(0, busStop, 1)
        bus01, bus02 = map(str, busList)
        return JsonResponse(
            {
                'message': {
                    'text': '🚏 {} ( {} )\n\n이번 🚌 : {}{}\n\n다음 🚌 : {}{}\n'.format(clickedButton, busStop, bus01,
                                                                                    ' 도착 예정' if bus01 not in ['출발대기',
                                                                                                              '운행종료'] else '',
                                                                                    bus02,
                                                                                    ' 도착 예정' if bus02 not in ['출발대기',
                                                                                                              '운행종료'] else '')

                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                }
            }
        )

    elif clickedButton == '도움말':
        return JsonResponse(
            {
                'message': {
                    'text': "안녕하세요! 구암고등학교 급식 및 버스정보를 알려주는 알렉스봇입니다 :)\n"
                            "원하시는 메뉴 중 하나를 골라 정보를 열람하시면 됩니다.\n"
                            "오류나 추가 요구사항은 관리자에게 문의하거나 오픈채팅을 통해 부탁드립니다.\n"
                            "자신이 등하교하는 정류장이 존재하지 않는다면 문의해주세요.\n"
                            "\n============\n\n"
                            "자료제공 : 서울특별시교육청, 서울특별시버스정보시스템\n"
                            "플러스친구 개발 : 구암고등학교 2018학년도 졸업, 건국대학교 컴퓨터공학과 '19 이동훈 \n"
                            "Github : https://github.com/donghoony/guahmchatbot\n"
                            "이용해 주셔서 고맙습니다 :)"

                },


                'keyboard': {
                    'type': 'buttons',
                    'buttons': ['구암고 급식안내', '내 등굣길 버스안내', '내 하굣길 버스안내', '등하교 버스안내', '내 등하굣길 설정하기', '도움말']
                }
            }
        )
