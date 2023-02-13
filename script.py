from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import csv




contest_link = input('Enter Contest link: ')


BASE_USERNAME = input('Enter Roll format: ')
start = int(input('Enter start roll no: '))
end = int(input('Enter end roll no: '))


D_BASE_USERNAME = input('Enter Roll format for D2D: ')
d_start = int(input('Enter start roll no: '))
d_end = int(input('Enter end roll no: '))



driver = webdriver.Firefox()
driver.get("http://172.16.5.23/accounts/login/")

usr_field = driver.find_element(By.ID,"id_username")
usr_field.send_keys("admin")

passwd_field = driver.find_element(By.ID,"id_password")
passwd_field.send_keys("dmojca123")

driver.find_element(By.XPATH,"/html/body/div/main/div/div/form/button").click()


driver.get(contest_link)


rank_link = driver.find_element(By.XPATH, '/html/body/div/main/div[1]/ul/li[3]/a')

rank_link.click()

number_of_rows = len(driver.find_elements(By.XPATH,"/html/body/div/main/div[2]/div/div/div[2]/table/tbody/tr"))
number_of_cols = len(driver.find_elements(By.XPATH, '/html/body/div/main/div[2]/div/div/div[2]/table/thead/tr/th'))

# students_data = {
#     '20CS016': {
#         scores: [],
#         rank: '1',
#         total: "12dsf"
#     }
# }


students_data = dict()


for i in range(start, end+1):
    username = BASE_USERNAME + str(i).zfill(3)
    students_data[username] = {
        'scores': list(),
        'time':list(),
        'rank': 'AB',
        'total': None,
        'plag': 0
    }

for i in range(d_start, d_end+1):
    username = D_BASE_USERNAME + str(i).zfill(3)
    students_data[username] = dict({
        'scores': list(),
        'time':list(),
        'rank': 'AB',
        'total': None,
        'plag': 0
    })

for i in range(1, number_of_rows+1):
    username = driver.find_element(By.XPATH, f'/html/body/div/main/div[2]/div/div/div[2]/table/tbody/tr[{i}]/td[3]').text
    for j in range(1, number_of_cols+1):
        if j == 2:
            continue

        if j == 1:
            rank = driver.find_element(By.XPATH, f'/html/body/div/main/div[2]/div/div/div[2]/table/tbody/tr[{i}]/td[1]').text
            students_data[username]['rank'] = int(rank)
            continue
        if j == number_of_cols:
            all_text = driver.find_element(By.XPATH, f'/html/body/div/main/div[2]/div/div/div[2]/table/tbody/tr[{i}]/td[{j}]/a').text
            child_text = driver.find_element(By.XPATH, f'/html/body/div/main/div[2]/div/div/div[2]/table/tbody/tr[{i}]/td[{j}]/a/div').text
            total_score = all_text.replace(child_text, '').replace('\n', '')
            students_data[username]['total'] = total_score
            continue
        
        if j >=4:
            try:
                all_text = driver.find_element(By.XPATH, f'/html/body/div/main/div[2]/div/div/div[2]/table/tbody/tr[{i}]/td[{j}]/a').text
                child_text = driver.find_element(By.XPATH, f'/html/body/div/main/div[2]/div/div/div[2]/table/tbody/tr[{i}]/td[{j}]/a/div').text
            
                score = all_text.replace(child_text, '').replace('\n', '')
                students_data[username]['scores'].append(score)
                students_data[username]['time'].append(child_text)
            except:
                students_data[username]['scores'].append(None)
                students_data[username]['time'].append(None)


for username, data in students_data.items():
    if data['rank'] == 'AB':
        students_data[username]['plag'] = None




mosslink = driver.find_element(By.XPATH, '/html/body/div/main/div[1]/ul/li[5]/a')
mosslink.click()


number_of_rows = len(driver.find_elements(By.XPATH,"/html/body/div/main/div[2]/table/tbody/tr"))


problems = {}

number_of_rows = len(driver.find_elements(By.XPATH,"/html/body/div/main/div[2]/table/tbody/tr"))


for i in range(1, number_of_rows+1):
    tab = driver.find_element(By.XPATH,f'/html/body/div/main/div[2]/table/tbody/tr[{i}]/td[1]')
    problem_name = tab.text
    links = []
    for j in range(2, 6):
        try:
            moss_problem_link_a = driver.find_element(By.XPATH,f'/html/body/div/main/div[2]/table/tbody/tr[{i}]/td[{j}]/a')
        except:
            links.append(None)
            continue
        links.append(moss_problem_link_a.get_attribute('href'))
    
    problems[problem_name] = links



result = {}
result_all = {}

for problem_name, links in problems.items():
    result[problem_name] = dict()
    for link in links:
        if link is None:
            continue
        driver.get(link)
        number_of_entries = len(driver.find_elements(By.XPATH, '/html/body/table/tbody/tr'))
        for i in range(2, number_of_entries+1):
            for j in range(1, 3):
                anchor = driver.find_element(By.XPATH, f'/html/body/table/tbody/tr[{i}]/td[{j}]/a')
                splitted = anchor.text.split(' ')
                username = splitted[0]
                percent = int(splitted[1][1:-2])
                if username in result_all:
                    result_all[username]=max(result_all[username],percent)
                else:
                    result_all[username] = percent
                if username in result[problem_name]:
                    result[problem_name][username] = max(result[problem_name][username], percent)
                    
                else:
                    result[problem_name][username] = percent



for username, plag_score in result_all.items():
    students_data[username]['plag'] = plag_score


num_problems = number_of_cols-4

heading = ['Rank', 'Username']

for i in range(1, num_problems+1):
    heading.append('Problem '+str(i))
heading.append('Total score')
heading.append('Max Plag')
for i in range(1, num_problems+1):
    heading.append('Time '+str(i))


csv_data = []
max_rank = -1
for username, data in students_data.items():
    to_append = [data['rank'], username]
    try:
        max_rank = max(max_rank, int(data['rank']))
    except:
        pass

    for k in range(num_problems):
        try:
            to_append.append(data['scores'][k])
        except:
            to_append.append(None)
    
    to_append.append(data['total'])
    to_append.append(data['plag'])

    for k in range(num_problems):
        try:
            to_append.append(data['time'][k])
        except:
            to_append.append(None)
    
    csv_data.append(to_append)


csv_data.sort(key=lambda x: str(x[0]).zfill(len(str(max_rank))+1))
csv_data.insert(0, heading)

with open('result.csv', "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(csv_data)


driver.close()
