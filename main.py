# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 15:50:00 2021

@author: chaibou001
"""

from pylab import*
from matplotlib import*
matplotlib.use('Agg') # NON-GUI BACKEND, CANNOT SHOW FIGURES IN SPYDER
from scripts import*
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import urllib
import os as os
from flask import Flask, render_template, redirect, url_for, request, session
from io import*
import base64

app = Flask(__name__)
v=1.2
app.secret_key = "super secret key"


@app.route("/")
def homepage():
    return render_template("index.html",beta_version='v'+str(v))

@app.route("/collect_data", methods=["POST","GET"])
def collect():
    if request.method == "POST":
        pt=request.form["pt"].strip()
        nm=request.form["nm"].strip()
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
        elif request.form["submit"] == "Plotting":
            return redirect(url_for("plotting"))
        else:
            return('Error')
    else:
        return render_template("cockpit.html",pt=pt,nm=nm)

@app.route('/search', methods=["POST","GET"])
def search_engine():
    pt=session["pt"]
    xl_nm=session["nm"]  
    if request.method == "POST":
        site=request.form["site"].replace(' ','')
        cable=request.form["cable"].strip().upper().replace(',','.').replace(' AS ',' (AS) ').replace('1000V','1KV').replace('1000 V','1KV')
        compound=request.form["compound"].replace(' ','').replace('(','').replace(')','').replace(',','.').upper()
        df=read_table(pt,xl_nm)
        df_target=search(df,site,cable,compound)
        table=df_target.to_html()
        return render_template("search_engine_display.html",i=table)
    else:
        return render_template("search_engine.html")
    
'''
@app.route('/plotting')
def plotting():
    fig=plt.figure()    
    x=linspace(0,20,21)
    y=pow(x,2)
    plt.plot(x,y,'.')
    title('$y=x^2$')
    xlabel('x')
    ylabel('y')
    img = BytesIO()
    plt.savefig(img,dpi=500)
    #img.seek(0) used to select the 0th frame
    # convert to base64 image
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return render_template('plot.html', plot_url=plot_url)
    #return send_file(img, mimetype='image/png')
'''

@app.route('/plotting',methods=["POST","GET"])
def plotting():
    if request.method=="POST":
        pt=session["pt"]
        xl_nm=session["nm"]
        # read table
        df=read_table(pt,xl_nm)
        # read site, cable, and compound data
        site=request.form["site"].replace(' ','')
        cable=request.form["cable"].strip().upper().replace(',','.').replace(' AS ',' (AS) ').replace('1000V','1KV').replace('1000 V','1KV')
        compound=request.form["compound"].replace(' ','').replace('(','').replace(')','').replace(',','.').upper()
    
        # read y-axis, x-axis, and legend parameters = takes value of the html form
        y=request.form["y"]
        x=request.form["x"]
        l=request.form["legend"]       
        # fills y,x,l data from the cleaned data frame
        x_axis, y_axis, l_arr = plot_data(df,site,cable,compound,y,x,l)
        
        # general, regardless of input
        fig=plt.figure(figsize=(7,8))
        for i in range(len(x_axis)):
            plot(x_axis.iloc[i],y_axis.iloc[i],'.',markersize=16)           
        myTitle='Laboratory: '+str(site)+'\n'+'Cable: '+str(cable)+'\n'+'Compound: '+str(compound)
        suptitle(myTitle, wrap=True,fontsize=15)
        xticks(fontsize=14)
        yticks(fontsize=14)
        
        # specific to each input
        units={'FS':'Flame spread (m)',
               'THR1200s':r'$THR_{1200s} (MJ)$',
               'HRRpeak':r'$HRR_{peak} (kW)$',
               'FIGRA':'FIGRA (-)',
               'Humidity':'Relative humidity (%)',
               'Temperature':'Temperature (C)'
               }
        xlim_max={'Temperature':55,
                  'Humidity':100,        
                  } 
        ylim_max={'FS':4,
                'THR1200s':150,
                'HRRpeak':300,
                'FIGRA':1000,
                }
        boundaries={'FS':[1.5,2.0,],
                    'THR1200s':[15,30,70],
                    'HRRpeak':[30,60,400],
                    'FIGRA':[150,300,1300]   
                        }
        xlabel(units[x],fontsize=15)
        ylabel(units[y], fontsize=15)
        xlim((0,xlim_max[x]))
        ylim((0,ylim_max[y]))        
        axhline(y=boundaries[y][0], color='k', linestyle='--')
        axhline(y=boundaries[y][1], color='k', linestyle='--')
        fill_between([0,100],y1=boundaries[y][0],y2=boundaries[y][1],color='#F7E6E3')
        text(1,(.45*boundaries[y][0]),r'$B_{ca}$',fontsize=20,color='k')
        text(1,(.45*(boundaries[y][0]+boundaries[y][1])),r'$C_{ca}$',fontsize=20,color='k')
        if(y!='FS'):
            axhline(y=boundaries[y][2], color='k', linestyle='--')
            text(1,(.45*(boundaries[y][1]+boundaries[y][2])),r'$D_{ca}$',fontsize=20,color='k')
            text(1,(.45*(boundaries[y][2]+ylim_max[y])),r'$E_{ca}$',fontsize=20,color='k')
            fill_between([0,100],y1=boundaries[y][1],y2=boundaries[y][2],color='#F3BFB4')
            fill_between([0,100],y1=boundaries[y][2],y2=ylim_max[y],color='#F77F6A')
        else:
            fill_between([0,100],y1=boundaries[y][1],y2=ylim_max[y],color='#F3BFB4')
            text(1,(.45*(boundaries[y][1]+ylim_max[y])),r'$D_{ca}+$',fontsize=20,color='k')
        #text(1,72,r'$E_{ca}$',fontsize=20,color='k')
        if(l!='nolegend'):
            legend(l_arr,bbox_to_anchor=(1,0), loc="lower left")
        plt.tight_layout()
        img = BytesIO()
        plt.savefig(img,dpi=500)
        img.seek(0) #used to select the 0th frame
        # convert to base64 image
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        return render_template('plot.html', plot_url=plot_url)
    else:
        return(render_template("plot_input.html"))
    
    






























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
    
