#!/usr/bin/env python3
# coding=utf-8
# -*- coding: UTF-8 -*-
#欲啟用後端請輸入:uvicorn main:app --reload

from xmlrpc.client import boolean
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pymysql

app = FastAPI()

data_a = []
data_b = []
origins = ["*"]


db_settings = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "db": "db_project",
    "charset": "utf8",
}

app.add_middleware(  #使chrome接收所有資料
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)
c = pymysql.connect(**db_settings)

cursor = c.cursor(pymysql.cursors.DictCursor)
cursor2 = c.cursor()

def checkUID(UID):  #確認帳號是否存在
    command = f"SELECT COUNT(*) FROM `student` WHERE `StudentID` = \"{UID}\""
    cursor2.execute(command)
    r1 = cursor2.fetchall()
    if(boolean(r1[0][0])):
        return False
    else:
        return True


def checkselected(UID):  #確認是否有選課
    command = f"SELECT COUNT(*) FROM `selectedcourse` WHERE `StudentID` = \"{UID}\""
    cursor2.execute(command)
    r1 = cursor2.fetchall()
    if(r1[0][0]==0):
        return False
    else:
        return True
    
    

def checkcredit(CID,data): #確認學分是否足夠
    totalcredit = 0
    if(len(data)>0):
        for i in range(len(data)):
            transtemp = data[i][0]
            if(int(transtemp) != int(CID)):
                totalcredit += data[i][8]
        if(totalcredit>8):
            return True
        else:
            return False
    else:
        return False



def delra(ra,S_CID):
    for i in range(len(ra)):
        if (ra[i][0]==S_CID):
            del ra[i]
            return ra
    return ra  


def delrb(rb,lastcredit):
    for i in range(len(rb)):
        if (rb[i][8]>lastcredit):
            del rb[i]
            return rb
    return rb


def delrc(rc,Schedule):
    for i in range(len(rc)):
        if (rc[i][7]==Schedule):
            del rc[i]
            return rc
    return rc


def delrd(rd,CourseName):
    for i in range(len(rd)):
        if (rd[i][1]==CourseName):
            del rd[i]
            return rd
    return rd


def opcourse_A():  # 驗證選課人數 並去除人數已滿之課程
    command = f"SELECT * FROM `course` WHERE `Capacity` > `Enrollment`;"
    cursor2.execute(command)
    r1 = cursor2.fetchall()
    r = list(r1)
    return r


def opcourse_B(ra,S_CIDs):  # 去除已選課程
    for i in range(len(S_CIDs)):
        rb = delra(ra,S_CIDs[i])
    return rb

    

def opcourse_C(rb,S_CIDs):  # 去除學分不合條件課程
    totalcredit = 0
    for i in range(len(S_CIDs)):
        command = f"SELECT Credit FROM `course` where CourseID = \"{S_CIDs[i]}\";"
        cursor2.execute(command)
        credit = cursor2.fetchall()
        
        totalcredit += credit[0][0]
    lastcredit = 30-totalcredit
    for i in range(len(rb)):
        rc = delrb(rb,lastcredit)
    return rc


def opcourse_D(rc,S_CIDs):  # 去除相同時間之課程
    Schedule = []
    for i in range(len(S_CIDs)):
        command = f"SELECT Schedule FROM `course` where CourseID = \"{S_CIDs[i]}\";"
        cursor2.execute(command)
        rr = cursor2.fetchall()
        Schedule.append(rr[0][0])

    for i in range(len(rc)):
        for j in range(len(Schedule)):
            rd = delrc(rc,Schedule[j])
    return rd


def opcourse_E(rd,S_CIDs):  # 去除相同課名之課程
    CourseName = []
    for i in range(len(S_CIDs)):
        command = f"SELECT CourseName FROM `course` where CourseID = \"{S_CIDs[i]}\";"
        cursor2.execute(command)
        rr = cursor2.fetchall()
        CourseName.append(rr[0][0])

    for i in range(len(rd)):
        for j in range(len(CourseName)):
            re = delrd(rd,CourseName[j])
    return re


def opcourse(UID): #可選課程篩選
    ra = opcourse_A()
    S_CIDs = []
    if (checkselected(UID)):
        command = f"SELECT CourseID FROM `selectedcourse` where StudentID = \"{UID}\";"
        cursor2.execute(command)
        rr = cursor2.fetchall()
        for i in range(len(rr)):
            S_CIDs.append(rr[i][0])
        rb = opcourse_B(ra,S_CIDs)
        if(len(rb)==0):
            return []
        rc = opcourse_C(rb,S_CIDs)
        if(len(rc)==0):
            return []
        rd = opcourse_D(rc,S_CIDs)
        if(len(rd)==0):
            return []
        re = opcourse_E(rd,S_CIDs)
        if(len(re)==0):
            return []
        return re
        
    else:
        return ra


def checkCID(CID,data): #確認課號是否存在
    if(len(data)>0):
        for i in range(len(data)):
            transtemp = data[i][0]
            if(int(CID) == int(transtemp)):
                return True
        return False
    else:
        return False 


def data_return(UID): #資料回傳
    global data_a, data_b
    data_a = []
    data_b = []
    if(checkselected(UID)):
        command = f"SELECT CourseID FROM `selectedcourse` where StudentID = \"{UID}\";"
        cursor2.execute(command)
        S_CID = cursor2.fetchall()
        if(len(S_CID)>1):
            command = f"SELECT * FROM `course` where "
            for i in range(len(S_CID)):
                if(i == len(S_CID)-1):
                    command += f"CourseID = \"{S_CID[i][0]}\";"
                else:
                    command += f"CourseID = \"{S_CID[i][0]}\" or "
            cursor2.execute(command)
            data_a = cursor2.fetchall()

        else:
            command = f"SELECT * FROM `course` where CourseID = \"{S_CID[0][0]}\";"
            cursor2.execute(command)
            data_a = cursor2.fetchall()
        data_b = opcourse(UID)
        return data_a,data_b
    else:
        command = f"SELECT * FROM `course` ;"
        cursor2.execute(command)
        data_b = cursor2.fetchall()
        return data_a,data_b


@app.get('/')
def index():
    print("rear on")


@app.get("/login/{UID}")
def login(UID):
    global data_a, data_b
    flag = checkUID(UID)
    if(flag):
        return "U"   
    else:
        return data_return(UID)


@app.get("/delcourse/{UID}/{CID}") # 退選功能
def delcourse(UID, CID):
    global data_a
    if(len(data_a)>0):
        if (checkCID(CID, data_a)):  # 剔除不存在課號
            if(checkcredit(CID, data_a)):  # 學分數檢測
                command = f"DELETE FROM selectedcourse WHERE `selectedcourse`.`StudentID` = \"{UID}\" AND `selectedcourse`.`CourseID` = \"{CID}\";"
                cursor2.execute(command)
                c.commit()
                return "S"
            else:
                return "N"
        else:
            return "F"
    else:
        return "D"

@app.get("/addcourse/{UID}/{CID}")
def addcourse(UID, CID):
    global data_b
    if(len(data_b)>0):
        if (checkCID(CID, data_b)):
            command = f"INSERT INTO `selectedcourse`(`StudentID`, `CourseID`) VALUES (\"{UID}\",\"{CID}\");"
            cursor2.execute(command)
            c.commit()
            return "S"
        else:
            return "F"
    else:
        return "D" 


c.commit()
