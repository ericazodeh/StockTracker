
import mysql.connector
import requests
import json
import urllib.parse
import matplotlib.pyplot as plt

#connect to the AWS database
#sensoring credentials for GitHub purposes
db = mysql.connector.connect(host='###################', user='admin',
                            password='###################')
cursor = db.cursor()

#use the created schema and commit execution
cursor.execute("use newSchema;")
db.commit()


encode = 'Time Series (Daily)' #JSON

#Exit and print an error code if anything wrong happens
try:
    #loop program
    while(True):
        print(" ")
        print("***********************************************")
        #get stock symbol name
        symbol = str(input("Please enter a symbol name for a given company,\nsome valid ones are AAPL (Apple) and AMZN (Amazon) (press Q to quit): "))
        print("***********************************************")
        print(" ")
        #quit program if user said so
        if symbol == 'q' or symbol == 'Q':
            break

        print("1. Daily Trends")
        print("2. Weekly Trends")
        print("3. Monthly Trends")
        print(" ")
        #get the time interval from the user
        timeInterval = str(input("Type 1, 2, or 3 to display values for a company's stock value over the given time interval: "))
        print(" ")
        if timeInterval == '1':
            timeInterval = 'TIME_SERIES_DAILY'
        elif timeInterval == '2':
            timeInterval = 'TIME_SERIES_WEEKLY'
        elif timeInterval == '3':
            timeInterval = 'TIME_SERIES_MONTHLY'
        else:
            #restart program for any other entry
            print("Error: Please use 1, 2, or 3")
            continue

        #construct url with the given time interval, stock name, and api key to get the correct JSON
        url = 'https://www.alphavantage.co/query?function={}&symbol={}&apikey=IF3II9O9IDBE7EGG'.format(timeInterval,symbol)

        url1 = url + urllib.parse.urlencode({'Time Series (Daily)' : encode})
        #get the date from the user (Some old dates are not included in the free API)
        if timeInterval == 'TIME_SERIES_DAILY':
            date = str(input("Please type the day (YYYY-MM-DD) you would like Daily information on?(Monday - Friday)\n Some valid inputs - \n2020-11-12, 2021-02-18, 2021-03-10:  "))
            print("DAILY INFO")

        elif timeInterval == 'TIME_SERIES_WEEKLY':
            date = str(input("Please type the Friday (YYYY-MM-DD) of the week you would like Weekly information on? \n Some valid inputs - \n2020-11-27, 2017-06-23, 2010-06-04:  "))
            print("WEEKLY INFO")

        else:
            date = str(input("Please type the Last Friday (YYYY-MM-DD) of the month you would like Monthly information on? \n Some valid inputs - \n2018-02-28, 2015-01-30, 2021-01-29:  "))
            print("MONTHLY INFO")

        #output results to the terminal
        print("--------SUMMARY-------")
        print("Date: " + date)
        print("Company: " + symbol)



        #convert JSON response to a string
        response = requests.get(url1).text
        # convert JSON into a dictionary
        data = json.loads(response)
        open = 0
        high = 0
        low = 0
        close = 0
        volume = 0
        count = 0
        i = 0


        #get correct spot in JSON by looping to the correct date
        for key in data:
            if count == 0:
                count +=1
                continue
            try:
                #load variables from dictionary keys
                open = data[key][date]["1. open"]
                high = data[key][date]["2. high"]
                low = data[key][date]["3. low"]
                close = data[key][date]["4. close"]
                volume = data[key][date]["5. volume"]

                #output results
                print("On this time interval, " + symbol + " opened at $"+ open + ", with a high of $" + high + ", and a low of $" + low +".\n" + symbol + " finally closed at $" + close+ " with a total of " + volume + " shares traded.")
            except:
                print("Error: Please input a valid symbol or date")
                continue
                print(" ")
        restartProgram = False
        quitProgram = False
        #2nd menu for additional functionality
        while restartProgram != True or quitProgram != True:
            print("---------------")
            print("1. Enter a new stock or time period")
            print("2. Add stock results into AWS Database")
            print("3. Output results of AWS Database")
            print("4. Display a graph of the chart's open, close, high, and low values")
            print("5. Delete a range of entries in AWS Database")
            print("6. Quit")
            print("---------------")

            ans = str(input("PLease choose one response above: "))


            if ans == "1":
                # restart program
                restartProgram =True
                break
            elif ans == "2":
                #create SQL statement with given results

                string = "insert into results(symbol,date,open,close,high,low,volume) values (" + '\'' + symbol + '\'' + ", " + '\'' + date + '\'' + ", " + '\'' + open + '\'' + ", " + '\'' + close + '\'' + ", " + '\'' + high + '\'' + ", " + '\'' + low + '\'' + ", " + '\'' + volume + '\'' + ");"
                # execute and commit query
                cursor.execute(string)
                db.commit()
                continue
            elif ans == "3":
                #create SQL statement
                cursor.execute("SELECT * FROM results;")
                # add result to a list and loop through each item to print it out
                rows = cursor.fetchall()
                print("ID    Symbol    Date         Open($)     Close($)     High($)      Low($)      Volume($)")
                for row in rows:
                    print("[" + str(row[0]) + "]" + " , " + row[1] + " , " + str(row[2]) +  " , " + "[" + str(row[3]) + "]" + " , " + "[" +row[4] + "]" +" , " +"[" + str(row[5])+ "]" +" , " +"[" + str(row[6])+"]"+" , " +"[" + str(row[7])+"]")
                continue
            elif ans == "4":
                #create a graph with matplotlib

                #set x axis
                x2 = ['open', 'high', 'low', 'close']
                #set y axis
                y2 = [float(open), float(high), float(low), float(close)]
                # plot
                plt.plot(x2, y2)
                #label the y axis
                plt.ylabel('Dollar Amount (in $)')
                #title the graph
                plt.title('Stock trends | ' + symbol + " | " + date)
                #show the graph
                plt.show()
            elif ans == "5":
                start = int(input("Select the row you would like to start the delete at (i.e. 3): "))
                end = int(input("Select the row you would like to end the delete at (i.e. 5): "))
                #create SQL statement with user input
                string = "DELETE from results WHERE id >= "+str(start)+" AND id <= "+str(end)+";"
                # execute and commit query
                cursor.execute(string)
                db.commit()
                continue
            elif ans == "6":
                #quit the program
                quitProgram = True
                break
            else:
                #restart the 2nd menu if they give a bad input
                print("Error: please input a valid number. ")
            continue

        if quitProgram == True:
            break
except:
    print("Error: Something went wrong.")


#print(type(data))