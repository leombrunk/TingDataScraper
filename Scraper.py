"""
This script collects data from Ting's website and formats it into a csv file.
The data collected includes monthly phone usage information for both the total
phone bill and the individual phone lines on the plan. It also includes the
monthly cost information of the total phone bill.
"""
import calendar
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WAIT_TIME = 5

class Bill:
    """ Represents both the total usage and total cost of a phone bill for a month. """
    def __init__(self, *, taxCost, totalCost, deviceCost, talkCost, smsCost, dataCost, usage):
        """ Initialize all the cost and usage data associated with the month's phone bill.
        Args:
            taxCost:    The amount of the phone bill that is tax
            totalCost:  The final cost of the phone bill
            deviceCost: The cost of the phone bill from the number of devices on the plan
            talkCost:   The cost of the phone bill from talk usage
            smsCost:    The cost of the phone bill from text usage
            dataCost:   The cost of the phone bill from data usage
            usage:      The talk, text, and data usage for the month
        """
        self.taxCost = taxCost
        self.totalCost = totalCost
        self.deviceCost = deviceCost
        self.talkCost = talkCost
        self.smsCost = smsCost
        self.dataCost = dataCost
        self.usage = usage

class Usage:
    """ Represents the total usage of an individual phone line or total phone bill for a month. """
    def __init__(self, *, talkUsed, smsUsed, dataUsed):
        """ Initialize the talk, text, and data usage for a month.
        Args:
            talkUsed:   The number of minutes of talk used
            smsUsed:    The number of texts used
            dataUsed:   The total Mbs of data used
        """
        self.talkUsed = talkUsed
        self.smsUsed = smsUsed
        self.dataUsed = dataUsed

def isolate_string_to_float(fullString, removedString):
    """ Trim a substring from a string to isolate a float and return that float as a number.
    Args:
        fullString:     A string that includes a number and some additional substring
        removedString:  The additional substring to be removed

    Returns:
        The isolated float as a number
    """
    reformatString = fullString.replace(removedString, '')
    return float(reformatString)

def retrieve_total_bill_info(xpathTableLocation, extraSubstring, description):
    """ Retrieve a float value from one cell of Ting's table on the Bill Details page.
    Args:
        xpathTableLocation: The substring of the xpath to the value that comes after "section"
        extraSubstring:     The additional substring next to the desired value to be removed
        description:        Description of what value was retrieved to print to terminal

    Returns:
        The number in one cell of Ting's table on the Bill Details page as a float.
    """
    billElement = driver.find_element_by_xpath(
        "//*[@id=\"content\"]/div[3]/div[2]/div/section" + xpathTableLocation)
    billValue = isolate_string_to_float(billElement.text, extraSubstring)
    print(description + ": " + str(billValue))
    return billValue

# Open Ting's login page
driver = webdriver.Chrome()
driver.get("https://ting.com/account/bill_history")
driver.implicitly_wait(WAIT_TIME)

# Log into Ting, replace 'usr' and 'pw' with your username and password.
user = 'usr'
pw = 'pw'
emailElement = driver.find_element_by_id("email")
pwElement = driver.find_element_by_id("password")
emailElement.send_keys(user)
pwElement.send_keys(pw)
pwElement.send_keys(Keys.ENTER)

# Wait 300 seconds for the captcha to be completed.
WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.ID, 'usageHeader')))

# Open Ting's Bill history page and count how many Bills there are.
driver.get('https://ting.com/account/bill_history')
driver.implicitly_wait(WAIT_TIME)
totalBillLinks = len(driver.find_elements_by_xpath("//a[contains(@href, '/account/bill_details/')]"))

# Track each month's total bill totalBill[monthYear] = Bill
totalBill = {}
# Track each phone line's usage allPhoneLines[name] = dateToUsage
allPhoneLines = {}

# Loop through each month's bill skipping the first month which is still in progress
for i in range(1, 3):

    # Click on one month's bill, must get link while on page to avoid StaleElementReferenceException
    updateBillLinks = driver.find_elements_by_xpath(
        "//a[contains(@href, '/account/bill_details/')]")
    updateBillLinks[i].click()

    driver.implicitly_wait(WAIT_TIME)
    time.sleep(WAIT_TIME)
    WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'marketingHeader')))

    # Convert text "Mobile service (MMM DD, YYY - MMM DD, YYY)" to "YYYY-MM" format
    dateElement = driver.find_element_by_class_name('date')
    dateSubString = (dateElement.text.split("Mobile service ("))[1].split(" - ")[0]
    monthAbbrvString = dateSubString[0:3]
    monthStringUnformatted = list(calendar.month_abbr).index(monthAbbrvString)
    monthString = f'{monthStringUnformatted:02}'
    yearString = dateSubString[-4:]
    monthYear = yearString + '-' + monthString
    print(monthYear)

    # Retrieve total bill usage and cost values
    totalCost = retrieve_total_bill_info("[3]/table/tbody/tr[3]/td", '$', "total cost")
    taxCost = retrieve_total_bill_info("[3]/table/tbody/tr[2]/td", '$', "tax cost")
    talkCost = retrieve_total_bill_info("[1]/table/tbody/tr[1]/td[4]", '$', "talk cost")
    smsCost = retrieve_total_bill_info("[1]/table/tbody/tr[2]/td[4]", '$', "sms cost")
    dataCost = retrieve_total_bill_info("[1]/table/tbody/tr[3]/td[4]", '$', "data cost")
    deviceCost = retrieve_total_bill_info("[1]/table/tbody/tr[4]/td[4]", '$', "device cost")
    talkUse = retrieve_total_bill_info("[1]/table/tbody/tr[1]/td[3]/a", ' minutes used', "talk usage")
    smsUse = retrieve_total_bill_info("[1]/table/tbody/tr[2]/td[3]/a", ' messages used', "text usage")
    dataUse = retrieve_total_bill_info("[1]/table/tbody/tr[3]/td[3]/a", ' megabytes used', "data usage")

    # Store this month's cost and usage data
    monthUsage = Usage(talkUsed=talkUse, smsUsed=smsUse, dataUsed=dataUse)
    monthsBill = Bill(taxCost=taxCost, totalCost=totalCost, deviceCost=deviceCost,
                      talkCost=talkCost, smsCost=smsCost, dataCost=dataCost, usage=monthUsage)
    totalBill[monthYear] = monthsBill

    # Go to the talk usage page for this month
    talkLink = driver.find_element_by_xpath(
        "//*[@id=\"content\"]/div[3]/div[2]/div/section[1]/table/tbody/tr[1]/td[3]/a")
    talkLink.click()
    driver.implicitly_wait(WAIT_TIME)
    time.sleep(WAIT_TIME)
    WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.ID, 'tableContainer')))

    # Gather all the users on this month's bill
    users = driver.find_elements_by_tag_name("option")

    # Collect usage data for each user, ignoring the first "All devices" user
    for user in users[1:]:
        # Sort usage by current user
        driver.find_element_by_id("subIdFilter").click()
        user.click()
        time.sleep(WAIT_TIME)

        # Collect the total mins of talk this user used this month
        durationsElements = driver.find_elements_by_class_name("cellDuration")
        totalTalk = 0.0
        for duration in durationsElements[1:]:
            if duration.text != '':
                durationValue = isolate_string_to_float(duration.text, " mins")
                totalTalk += durationValue
        print("total talk of " + str(totalTalk) + " for " + user.text)

        # Click on the messages tab to view text usage for the current user this month
        driver.find_element_by_id("messages").click()
        time.sleep(WAIT_TIME)

        # Collect the total texts this user used this month
        messagesElements = driver.find_elements_by_class_name("To")
        totalText = 0
        for message in messagesElements:
            if message.text != '':
                totalText += 1
        totalText /= 2
        print("total text of " + str(totalText) + " for " + user.text)

        # Click on the megabytes tab to view data usage for the current user this month
        driver.find_element_by_id("megabytes").click()
        time.sleep(WAIT_TIME)


        # Collect the total Mb of data this user used this month
        dataElements = driver.find_elements_by_class_name("cellUsage")
        totalData = 0.0
        for data in dataElements:
            if data.text != '':
                totalData += float(data.text)
        print("total data of " + str(totalData) + "Mb for " + user.text)

        # Gather all usage data for this user this month
        userUsage = Usage(talkUsed=totalTalk, smsUsed=totalText, dataUsed=totalData)

        # Add the user to the dict of all users if not already added
        if user.text not in allPhoneLines.keys():
            allPhoneLines[user.text] = {}

        # Add this month's usage for this user
        usersPhoneLine = allPhoneLines.get(user.text)
        usersPhoneLine[monthYear] = userUsage

        # Go back to the minutes tab to begin again with the next user
        driver.find_element_by_id("minutes").click()
        time.sleep(WAIT_TIME)

    # Go back to the bill history page to begin again with the next month's bill
    driver.get('https://ting.com/account/bill_history')
    WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, 'billType')))
    time.sleep(WAIT_TIME)

print("End Data Collection")

# Create a CSV file with all the collected cost and usage data by month
with open('TingData.csv', 'w', newline='') as file:
    writer = csv.writer(file)

    # Create rows for the total bill's cost and usage each month
    titleRow = ["Total Bill"]
    talkRow = ["talk"]
    textRow = ["text"]
    dataRow = ["data"]
    taxCostRow = ["tax cost"]
    totalCostRow = ["totalCost"]
    deviceCostRow = ["deviceCost"]
    talkCostRow = ["talkCost"]
    smsCostRow = ["smsCost"]
    dataCostRow = ["dataCost"]
    for date in totalBill:
        monthBill = totalBill.get(date)

        titleRow.append(date)
        talkRow.append(monthBill.usage.talkUsed)
        textRow.append(monthBill.usage.smsUsed)
        dataRow.append(monthBill.usage.dataUsed)
        taxCostRow.append(monthBill.taxCost)
        totalCostRow.append(monthBill.totalCost)
        deviceCostRow.append(monthBill.deviceCost)
        talkCostRow.append(monthBill.talkCost)
        smsCostRow.append(monthBill.smsCost)
        dataCostRow.append(monthBill.dataCost)

    writer.writerow(titleRow)
    writer.writerow(talkRow)
    writer.writerow(textRow)
    writer.writerow(dataRow)
    writer.writerow(taxCostRow)
    writer.writerow(totalCostRow)
    writer.writerow(deviceCostRow)
    writer.writerow(talkCostRow)
    writer.writerow(smsCostRow)
    writer.writerow(dataCostRow)
    writer.writerow([])

    # Create rows for each user's talk, text, and data usage each month
    for userName in allPhoneLines:
        userData = allPhoneLines.get(userName)

        titleRow = [userName]
        talkRow = ["talk"]
        textRow = ["text"]
        dataRow = ["data"]

        for date in userData:
            usage = userData.get(date)
            titleRow.append(date)
            talkRow.append(usage.talkUsed)
            textRow.append(usage.smsUsed)
            dataRow.append(usage.dataUsed)

        writer.writerow(titleRow)
        writer.writerow(talkRow)
        writer.writerow(textRow)
        writer.writerow(dataRow)
        writer.writerow([])

print("End CSV Write")
