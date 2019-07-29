import json
from flask import Flask, request, jsonify
from multiprocessing import Process
from RedisConn import RedisQueue
from flask_cors import CORS
import logging
import worker
import mysql.connector
import RedisConn


app = Flask(__name__)
CORS(app)

class serviceClass:
    
    def reciveMeaage(self, content):
        logging.info("Json Received")
        logging.info("pushing into Redis Queue")
        print ("content",content)
        
        if(str(content["messageMethod"])=="randomMessage"):
            content["shortMessage"]="random"
        
        print(content["messageMethod"])
        print(content["shortMessage"])
        
        self.push(content)
        self.pushDb(content)
        worker.wprocess()
        return jsonify({"Response code" : "00"})


    def push(self,data):
        #print(data["name"])
        print("data=====",data)
        json_data=json.dumps(data)
        q=RedisQueue('test')
        q.put(json_data)
    
    def pushDb(self, data):
        database = mysql.connector.connect(host="localhost",user="root",passwd="root",db="smpp")
        mycursor = database.cursor()
        sql = "INSERT INTO smppTrafficMonitor  VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        val = (data["systemId"].encode('utf-8'),
               data["password"].encode('utf-8'),
               data["systemType"].encode('utf-8'),
               (data["ip"].encode('utf-8')) , 
               int (data["portNumber"].encode('utf-8')),
               int (data["sourceAddress"].encode('utf-8')),
               int(data["sourceAddressRange"].encode('utf-8')) ,int(data["destinationAddress"].encode('utf-8')) ,
               int (data["destinationAddressRange"].encode('utf-8')),
               data["shortMessage"].encode('utf-8'),data["msgSend"],data["ackRecv"],data["timeStamp"],"0")
        mycursor.execute(sql,val)
        database.commit()

    
    def start(self, content):
        print("hello")
        return serviceClass().reciveMeaage(content)
    
    def getData(self):
        database = mysql.connector.connect(host="localhost",user="root",passwd="root",db="smpp")
        mycursor = database.cursor()
        sql="select timeStamp,msgSend, ackRecv from smppTrafficMonitor where status='0'"
        mycursor.execute(sql)
        res=mycursor.fetchall()
        my_lsit=[]
        
        print("list====",type(res))
        print(mycursor.rowcount)
        for s in res:
            q=RedisConn.getred()
            key_send=str(s[0].encode('utf-8'))+"_send"
            key_recv=str(s[0].encode('utf-8'))+"_recv"
            msgSent=q.get(key_send)
            msgRecv=q.get(key_recv)

            #print(key)
            di= { 'timeStamp':s[0].encode('utf-8'),

                'messageSent':msgSent ,
                 'messageReceived':msgRecv

                }
            my_lsit.append(di)
        #print(my_lsit)
        return my_lsit
    def completedJob(self):

        database = mysql.connector.connect(host="localhost",user="root",passwd="root",db="smpp")
        mycursor = database.cursor()
        sql="select timeStamp , msgSend , ackRecv from smppTrafficMonitor where status='1'"
        mycursor.execute(sql)
        res=mycursor.fetchall()
        lst=[]
        for row in res:
            dic = {
                    "timeStamp":row[0].encode('utf-8'),
                    "messageSent":row[1] ,
                    "messageReceived":row[2]
                  }
            lst.append(dic)
        print lst
        return lst
    def delete (self,content):
        print "Inside Delete"
        database = mysql.connector.connect(host="localhost",user="root",passwd="root",db="smpp")
        mycursor = database.cursor()
        h=str(content["timeCheck"])
    
        mycursor.execute("delete from smppTrafficMonitor where timeStamp=(%s)",(h,))
        database.commit()
        

     
@app.route('/getJob', methods=['GET', 'OPTIONS'])
def getCompletedDJobs():
    #list1=[{"timeStamp":"00","messageSent":"1","messageReceived":"00"}]
    print("completed jobs")
    service=serviceClass()
    lst=service.completedJob()
    return json.dumps(lst)

@app.route('/delete', methods=['GET', 'POST'])  
def delete():
    service = serviceClass()
    
    content=request.json
    service.delete(content)
    print("tfhfl===",content)
    return "deleted"

@app.route('/reciveMessage', methods=['GET', 'POST'])  
def main():
    service = serviceClass()
    print("hrll")
    return service.start(request.json)
@app.route('/pause', methods=['GET', 'POST', 'OPTIONS'])
def pasueService():
    print 'pause'
    content=request.json
    q=RedisConn.getred()
    if(content != None):
        key=str(content["timeCheck"].encode("utf-8"))+"_pause"
        
        print key
        q.set(key,"1")
        q.set("time",content["timeCheck"].encode("utf-8"))
    #red.set("pause","1")
    return ""

@app.route('/resume', methods=['GET', 'POST', 'OPTIONS'])
def resumeService():
   # print 'pause'
    content=request.json
    q=RedisConn.getred()
    if(content != None):
        key=str(content["timeCheck"].encode("utf-8"))+"_pause"
        
        print key
        q.set(key,"0")
        q.set("time",content["timeCheck"].encode("utf-8"))
    #red.set("pause","1")
    return ""

@app.route('/makeData', methods=['GET', 'OPTIONS'])
def makeData():
    service = serviceClass()
    list1=service.getData()
   # print("======")
   # print(list1)
    #print 'resume'
    return json.dumps(list1)
    #red.set("pause","0")

@app.route('/stop', methods=['GET', 'POST', 'OPTIONS'])
def stopService():

    content=request.json
    q=RedisConn.getred()
    if(content != None):
        key=str(content["timeCheck"].encode("utf-8"))+"_stop"
        
        print key
        q.set(key,"1")
        q.set("time",content["timeCheck"].encode("utf-8"))

    return ""
    return jsonify({"Response code": "00"}) 

if __name__ == '__main__':
    print("Service Started")
    p = Process(target = main)
    p.start()
    p.join()
    app.run(host="0.0.0.0",port=5000)
        