from flask import render_template, request
from app import app
import pymysql as mdb
from a_Model import ModelIt
import pandas as pd 
import MySQLdb
from sklearn.linear_model import LinearRegression
import numpy as np

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
        title = 'Home',
        )

#@app.route("/db_fancy")
#def cities_page_fancy():
#    db = mdb.connect(user="root", host="localhost", db="nhanes_db", charset='utf8')
#    with db:
#        cur = db.cursor()
#        cur.execute("SELECT DSID_Product_Category_Code, NHANES_DSI_Linking_Code, DSID_Ingredient_Name, NHANES_Ingredient_ID, Label_Amount_per_Serving, Unit_per_Serving, NHANES_Supplement_ID FROM nhanes_tb ORDER BY DSID_Product_Category_Code LIMIT 15;")
#        query_results = cur.fetchall()
#    cities = []
#    for result in query_results:
#        cities.append(dict(DSID_Product_Category_Code=result[0], NHANES_DSI_Linking_Code=result[1], DSID_Ingredient_Name=result[2], NHANES_Ingredient_ID=result[3], Label_Amount_per_Serving=result[4], Unit_per_Serving=result[5], NHANES_Supplement_ID=result[6]))
#    return render_template('cities.html', cities=cities) 
    
@app.route('/input')
def cities_input():
  return render_template("input.html")

@app.route('/output')
def cities_output():
    city = request.args.get('ID')
    db = mdb.connect(user="root", host="localhost", db="recommend_db", charset='utf8')
    
    # find top 10 investors in the company category
    with db:
        cur = db.cursor()
        cur.execute("SELECT Category FROM company_tb WHERE Name='%s';" % city)
        query_results = cur.fetchall()
    if len(query_results)>0: 
        with db:
            cur = db.cursor()
            cur.execute("SELECT Name, TimesInvest FROM investor_tb WHERE Category='%s' ORDER BY TimesInvest DESC;" % query_results[0])
            query_results = cur.fetchall()
        cities = []
        for result in query_results[:10]:
            cities.append(dict(Investor=result[0],Link='https://www.crunchbase.com/search?show_results=1&navigation_search_input='+ result[0].replace(' ','+'),PastInvestments=result[1]))
    else:
        cities=[{'Investor':'Sorry, the company you searched does not have category information. Search CrunchBase.','Link':'https://www.crunchbase.com/'}]
        
    
    
    # find top 10 investors in similar companies (location+stage)
    with db:
        cur = db.cursor()
        cur.execute("SELECT Name, TimesInvest FROM investor_tb;")
        query_results = cur.fetchall()
    investor_df=pd.DataFrame([list(elem) for elem in list(query_results)],columns=['Name','TimesInvest'])
    investor_df = investor_df.sort('TimesInvest',ascending=False)
    with db:
        cur = db.cursor()
        cur.execute("SELECT Location, Title FROM company_tb WHERE Name='%s';" % city)
        query_results = cur.fetchall()
    if len(query_results)>0: 
        the_result = []
        with db:
            cur.execute("SELECT Investors FROM company_tb WHERE Location='%s' AND Title='%s';" % (query_results[0][0], query_results[0][1]))
            queryi_results = cur.fetchall()
        if len(queryi_results)>0:
            list_investor = []
            for result in queryi_results:
                if result[0] is not None:
                    list_investor.extend(result[0].split(' + '))
            for ind in investor_df.index:
                if investor_df['Name'][ind] in list_investor:
                    the_result.append(dict(Investor=investor_df['Name'][ind],Link='https://www.crunchbase.com/search?show_results=1&navigation_search_input='+ investor_df['Name'][ind].replace(' ','+'),PastInvestments=investor_df['TimesInvest'][ind]))
            if len(the_result)==0:
                the_result = [dict(Investor='Sorry, the company you searched does not have similar companies in the database.')]
        else:
            #the_result = [dict(Investor='Sorry, the company you searched does not have similar companies in the database.',Link='https://www.crunchbase.com/')]
            with db:
                cur.execute("SELECT Investors FROM company_tb WHERE Title='Seed';")
                queryi_results = cur.fetchall()
                if len(queryi_results)>0:
                    list_investor = []
                    for result in queryi_results:
                        if result[0] is not None:
                            list_investor.extend(result[0].split(' + '))
                    for ind in investor_df.index:
                        if investor_df['Name'][ind] in list_investor:
                            the_result.append(dict(Investor=investor_df['Name'][ind],Link='https://www.crunchbase.com/search?show_results=1&navigation_search_input='+ investor_df['Name'][ind].replace(' ','+'),PastInvestments=investor_df['TimesInvest'][ind]))

    else:
        the_result=[]
        #the_result = [dict(Investor='Sorry, the company you searched is not in the database.',Link='https://www.crunchbase.com/')]
        with db:
            cur.execute("SELECT Investors FROM company_tb WHERE Title='Seed';")
            queryi_results = cur.fetchall()
            if len(queryi_results)>0:
                list_investor = []
                for result in queryi_results:
                    if result[0] is not None:
                        list_investor.extend(result[0].split(' + '))
                for ind in investor_df.index:
                    if investor_df['Name'][ind] in list_investor:
                        the_result.append(dict(Investor=investor_df['Name'][ind],Link='https://www.crunchbase.com/search?show_results=1&navigation_search_input='+ investor_df['Name'][ind].replace(' ','+'),PastInvestments=investor_df['TimesInvest'][ind]))
       
             
             
    
    
        
          
    
    
    return render_template("output.html", cities = cities, the_result = the_result[:10])

    #call a function from a_Model package. note we are only pulling one result in the query
 
    # read csv source file to panda dataframe
#    df = pd.read_csv('/Users/binxiang/Desktop/Insight/Week 2/funding_modified_for_python.csv')
#    model = LinearRegression()
#    model.fit(df[["TITLE","ncompany","COMPANY_ID"]],df["FUNDING_AMOUNT"])
#    the_result = str(np.around(model.predict(df[df["COMPANY_ID"]==float(city)][["TITLE","ncompany","COMPANY_ID"]]),decimals=1))
#   return render_template("output.html", cities = cities, the_result = the_result)
