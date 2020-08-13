from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import calendar
import time
import csv

class PhoneLine:
    def __init__(self):
        self.usageByMonth = {}

    def addBill(self, date, usage):
        self.usageByMonth[date] = usage

class TotalBill:
    def __init__(self):
        self.billsByMonth = {}

    def addBill(self, date, bill):
        self.billsByMonth[date] = bill

class Bill:
    def __init__(self, *, taxCost, totalCost, deviceCost, talkCost, smsCost, dataCost, usage):
        self.taxCost = taxCost 
        self.totalCost = totalCost
        self.deviceCost = deviceCost
        self.talkCost = talkCost 
        self.smsCost = smsCost
        self.dataCost = dataCost
        self.usage = usage

class Usage:
    def __init__(self, *, talkUsed, smsUsed, dataUsed):
        self.talkUsed = talkUsed
        self.smsUsed = smsUsed
        self.dataUsed = dataUsed

def string_to_float(fullString, removedString):
    reformatString = fullString.replace(removedString, '')
    return float(reformatString)

driver = webdriver.Chrome()
driver.get("https://ting.com/account/bill_history")
driver.implicitly_wait(10)

"""
user = 'usr'
pw = 'pw'
emailElement = driver.find_element_by_id("email")
pwElement = driver.find_element_by_id("password")
emailElement.send_keys(user)
pwElement.send_keys(pw)
pwElement.send_keys(Keys.ENTER)
"""

WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.ID, 'usageHeader')))

driver.get('https://ting.com/account/bill_history')
driver.implicitly_wait(10)
billLinks = driver.find_elements_by_xpath("//a[contains(@href, '/account/bill_details/')]")

totalBill = TotalBill()
allPhoneLines = {}

for i, billPage in enumerate(billLinks[1:]):

    updateBillLinks = driver.find_elements_by_xpath("//a[contains(@href, '/account/bill_details/')]")
    updateBillLinks[i + 1].click()
    
    driver.implicitly_wait(10)
    time.sleep(3)
    WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, 'marketingHeader')))

    dateElement = driver.find_element_by_class_name('date')
    dateSubString = (dateElement.text.split("Mobile service ("))[1].split(" - ")[0]
    monthAbbrvString = dateSubString[0:3]
    monthStringUnformatted = list(calendar.month_abbr).index(monthAbbrvString)
    monthString = f'{monthStringUnformatted:02}'
    yearString = dateSubString[-4:]
    monthYear = yearString + '-' + monthString
    print(monthYear)

    totalCostElement = driver.find_element_by_xpath("//*[@id=\"content\"]/div[3]/div[2]/div/section[3]/table/tbody/tr[3]/td")
    totalCost = string_to_float(totalCostElement.text, '$')
    print(totalCost)

    taxCostElement = driver.find_element_by_xpath("//*[@id=\"content\"]/div[3]/div[2]/div/section[3]/table/tbody/tr[2]/td")
    taxCost = string_to_float(taxCostElement.text, '$')
    print(taxCost)

    talkCostElement = driver.find_element_by_xpath("//*[@id=\"content\"]/div[3]/div[2]/div/section[1]/table/tbody/tr[1]/td[4]")
    talkCost = string_to_float(talkCostElement.text, '$')
    print(talkCost)

    smsCostElement = driver.find_element_by_xpath("//*[@id=\"content\"]/div[3]/div[2]/div/section[1]/table/tbody/tr[2]/td[4]")
    smsCost = string_to_float(smsCostElement.text, '$')
    print(smsCost)

    dataCostElement = driver.find_element_by_xpath("//*[@id=\"content\"]/div[3]/div[2]/div/section[1]/table/tbody/tr[3]/td[4]")
    dataCost = string_to_float(dataCostElement.text, '$')
    print(dataCost)

    deviceCostElement = driver.find_element_by_xpath("//*[@id=\"content\"]/div[3]/div[2]/div/section[1]/table/tbody/tr[4]/td[4]")
    deviceCost = string_to_float(deviceCostElement.text, '$')
    print(deviceCost)

    talkUseElement = driver.find_element_by_xpath("//*[@id=\"content\"]/div[3]/div[2]/div/section[1]/table/tbody/tr[1]/td[3]/a")
    talkUse = string_to_float(talkUseElement.text, ' minutes used')
    print(talkUse)

    smsUseElement = driver.find_element_by_xpath("//*[@id=\"content\"]/div[3]/div[2]/div/section[1]/table/tbody/tr[2]/td[3]/a")
    smsUse = string_to_float(smsUseElement.text, ' messages used')
    print(smsUse)

    dataUseText = driver.find_element_by_xpath("//*[@id=\"content\"]/div[3]/div[2]/div/section[1]/table/tbody/tr[3]/td[3]/a")
    dataUse = string_to_float(dataUseText.text, ' megabytes used')
    print(dataUse)

    monthUsage = Usage(talkUsed=talkUse, smsUsed=smsUse, dataUsed=dataUse)
    monthsBill = Bill(taxCost=taxCost, totalCost=totalCost, deviceCost=deviceCost, talkCost=talkCost, smsCost=smsCost, dataCost=dataCost, usage=monthUsage)
    totalBill.addBill(monthYear, monthsBill)

    talkLink = driver.find_element_by_xpath("//*[@id=\"content\"]/div[3]/div[2]/div/section[1]/table/tbody/tr[1]/td[3]/a")
    talkLink.click()
    driver.implicitly_wait(10)
    time.sleep(4)
    WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.ID, 'tableContainer')))

    users = driver.find_elements_by_tag_name("option")

    for user in users[1:]:
        driver.find_element_by_id("subIdFilter").click()
        time.sleep(2)
        user.click()
        time.sleep(2)
        durationsElements = driver.find_elements_by_class_name("cellDuration")
        totalTalk = 0.0
        for duration in durationsElements[1:]:
            if duration.text != '':
                durationValue = string_to_float(duration.text, " mins")
                totalTalk += durationValue
        print("total talk of " + str(totalTalk) + " for " + user.text)

        driver.find_element_by_id("messages").click()
        time.sleep(4)
        messagesElements = driver.find_elements_by_class_name("To")
        totalText = 0
        for message in messagesElements:
            if message.text != '':
                totalText += 1
        totalText /= 2
        print("total text of " + str(totalText) + " for " + user.text)

        driver.find_element_by_id("megabytes").click()
        time.sleep(4)
        dataElements = driver.find_elements_by_class_name("cellUsage")
        totalData = 0.0
        for data in dataElements:
            if data.text != '':
                totalData += float(data.text)
        print("total data of " + str(totalData) + "Mb for " + user.text)

        driver.find_element_by_id("minutes").click()
        time.sleep(4)

        userUsage = Usage(talkUsed=totalTalk, smsUsed=totalText, dataUsed=totalData)

        if user.text not in allPhoneLines.keys():
            allPhoneLines[user.text] = PhoneLine()

        usersPhoneLine = allPhoneLines.get(user.text)
        usersPhoneLine.addBill(monthYear, userUsage)

    driver.get('https://ting.com/account/bill_history')
    driver.implicitly_wait(10)
    WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, 'billType')))
    time.sleep(4)

print("end data collection")

with open('TingData.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        titleRow = ["Total Bill"]
        talkRow = ["talk"]
        textRow = ["text"]
        dataRow = ["data"]
        taxCost = ["tax cost"]
        totalCost = ["totalCost"]
        deviceCost = ["deviceCost"]
        talkCost = ["talkCost"]
        smsCost = ["smsCost"]
        dataCost = ["dataCost"]

        for date in totalBill.billsByMonth:
            monthBill = totalBill.billsByMonth.get(date)

            titleRow.append(date)
            talkRow.append(monthBill.usage.talkUsed)
            textRow.append(monthBill.usage.smsUsed)
            dataRow.append(monthBill.usage.dataUsed)
            taxCost.append(monthBill.taxCost)
            totalCost.append(monthBill.totalCost)
            deviceCost.append(monthBill.deviceCost)
            talkCost.append(monthBill.talkCost)
            smsCost.append(monthBill.smsCost)
            dataCost.append(monthBill.dataCost)

        writer.writerow(titleRow)
        writer.writerow(talkRow)
        writer.writerow(textRow)
        writer.writerow(dataRow)
        writer.writerow(taxCost)
        writer.writerow(totalCost)
        writer.writerow(deviceCost)
        writer.writerow(talkCost)
        writer.writerow(smsCost)
        writer.writerow(dataCost)
        writer.writerow([])

        for userName in allPhoneLines:
            userData = allPhoneLines.get(userName)

            titleRow = [userName]
            talkRow = ["talk"]
            textRow = ["text"]
            dataRow = ["data"]

            for date in userData.usageByMonth:
                usage = userData.usageByMonth.get(date)
                titleRow.append(date)
                talkRow.append(usage.talkUsed)
                textRow.append(usage.smsUsed)
                dataRow.append(usage.dataUsed)

            writer.writerow(titleRow)
            writer.writerow(talkRow)
            writer.writerow(textRow)
            writer.writerow(dataRow)
            writer.writerow([])
