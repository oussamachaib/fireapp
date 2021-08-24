# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 15:50:00 2021

@author: chaibou001
"""

from pylab import*
from matplotlib import*
from scripts import*
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import urllib
import os as os
from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)
v=1.1
app.secret_key = "super secret key"


@app.route("/")
def homepage():
    return render_template("index.html",beta_version='v'+str(v))

@app.route("/collect_data", methods=["POST","GET"])
def collect():
    if request.method == "POST":
        pt=request.form["pt"]
        nm=request.form["nm"]
        session["pt"]=pt
        session["nm"]=nm
        ishere=pt+'\\'+nm+'.xlsx'
        ishere=r"{}".format(ishere)
        if(os.path.isfile(ishere)==True):
            #return render_template("cockpit.html",pt=pt,nm=nm)
            return redirect(url_for("home_cockpit"))
                        
        else:
            return render_template("collect.html")
    else:
        return render_template("collect.html")
    

@app.route("/cockpit", methods=["POST","GET"])
def home_cockpit():
    pt=session["pt"]
    nm=session["nm"]
    if request.method == "POST":
        if request.form["submit"] == "Clean table":
            save_name=nm+'_clean'
            df_dirty=read_table_dirty(pt,nm)
            placeholder=clean_table(df_dirty,pt,save_name)
            return render_template("cleaned.html",pt=pt,nm=nm,sv=save_name)        
        elif request.form["submit"] == "Display table":
            df=read_table(pt,nm)
            html=df.to_html()
            return html
        elif request.form["submit"] == "Display statistics":
            df=read_table(pt,nm)
            a,b,c,d=statistics(df)                                              
            b=b.to_frame()
            c=c.to_frame()
            d=d.to_frame()
            b.columns=['Tests']
            c.columns=['Tests']
            d.columns=['Tests']
            b=b.to_html()
            c=c.to_html()
            d=d.to_html()                
            #return f'<p> Fire test count : {a} fire tests</p><br><p> Site distribution : {b} </p><br><p> Cable distribution: {c} </p><br><p> Compound distribution: {d} </p><br>'
            return render_template("stats.html",i=a,ii=b,iii=c,iv=d)
        elif request.form["submit"] == "Search engine":
            return redirect(url_for("search_engine"))
        else:
            return('Error')
    else:
        return render_template("cockpit.html",pt=pt,nm=nm)

@app.route('/search', methods=["POST","GET"])
def search_engine():
    pt=session["pt"]
    xl_nm=session["nm"]  
    if request.method == "POST":
        site=request.form["site"]
        cable=request.form["cable"]
        compound=request.form["compound"]
        df=read_table(pt,xl_nm)
        df_target=search(df,site,cable,compound)
        table=df_target.to_html()
        return render_template("search_engine_display.html",i=table)
    else:
        return render_template("search_engine.html")

'''
@app.route('/test_home',methods=['POST','GET'])
def test_home():
    if request.method == "POST":
        bbox2=request.form["box2"]        
        print(bbox2)
        #bbox3=request.form["box3"]
        return redirect(url_for("test_target",text2=str(bbox2)))
    else:
        return render_template("test_home.html")

@app.route('/<text2>')
def test_target(text2):
    print(text2)
    return f'<p>{text2}</p>'

@app.route('/test_home2')
def test_home2():
    return ("test_home.html")
    

@app.route('/<path><title><sheet>')
def read_file(path,title,sheet):
    #df=read_table_pandas_clean(pt,title,sheet)
    #return 'OK'
    print(path)
    print(title)
    print(sheet)
    return f'<p>{path}</p><p>{title}</p><p>{sheet}</p>'



@app.route('/<location><cable><compound>')
def disp(location,cable,compound):
    return f"<p>{urllib.parse.quote(location)}</p><p>{urllib.parse.quote(cable)}</p><p>{urllib.parse.quote(compound)}</p>"
'''

       
if __name__ == "__main__":
    app.run(host="127.0.0.1",port=8080,debug=True)
    
