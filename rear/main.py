#!/usr/bin/env python3
# coding=utf-8
# -*- coding: UTF-8 -*-
#uvicorn main:app --reload

from xmlrpc.client import boolean
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pymysql

app = FastAPI()

origins = ["*"]


db_settings = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "db": "db_project",
    "charset": "utf8",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)
c = pymysql.connect(**db_settings)

cursor = c.cursor(pymysql.cursors.DictCursor)
cursor2 = c.cursor()


def checkUID(UID):
    command = f"SELECT COUNT(*) FROM `student` WHERE `StudentID` = \"{UID}\""
    cursor2.execute(command)
    r1 = cursor2.fetchall()
    if(boolean(r1[0][0])):
        return False
    else:
        return True


def checkselected(UID):
    command = f"SELECT COUNT(*) FROM `selectedcourse` WHERE `StudentID` = \"{UID}\""
    cursor2.execute(command)
    r1 = cursor2.fetchall()
    if(r1[0][0]==0):
        return False
    else:
        return True


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


# def delrc(rc,Schedule):
#     for i in range(len(rc)):
#         if (rc[i][7]==Schedule):
#             del rc[i]
#             return rc
#     return rc


def opcourse_A():  # 驗證選課人數
    command = f"SELECT * FROM `course` WHERE `Capacity` > `Enrollment`;"
    cursor2.execute(command)
    r1 = cursor2.fetchall()
    r = list(r1)
    print(len(r))
    return r


def opcourse_B(ra,S_CIDs):  # 去除已選課程
    for i in range(len(S_CIDs)):
        rb = delra(ra,S_CIDs[i])
    print(len(rb))
    return rb

    

def opcourse_C(rb,S_CIDs):  # 去除學分不足課程
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


# def opcourse_D(rc,S_CIDs):  # 去除相同時間課程
#     Schedule = []
#     for i in range(len(S_CIDs)):
#         command = f"SELECT Schedule FROM `course` where CourseID = \"{S_CIDs[i]}\";"
#         cursor2.execute(command)
#         rr = cursor2.fetchall()
#         Schedule.append(rr[0][0])

#     for i in range(len(rc)):
#         for j in range(Schedule):
#             rd = delrc(rc,Schedule[j])
#     print(len(rd))
#     return rd


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
        print("rb",rb)
        if(rb==None):
            print("123")
            return rb
        rc = opcourse_C(rb,S_CIDs)
        print("rc",rc)
        if(rc==None):
            print("456")
            return rc
        # rd = opcourse_D(rc,S_CIDs)
        # print("rd",rd)
        # if(rd==None):
        #     print("789")
        #     return rd
    else:
        return ra


@app.get('/')
def index():
    print(456)


@app.get("/login/{UID}")
def login(UID):
    flag = checkUID(UID)
    if(flag):
        print(1111)
        return "U"   
    else:
        if(checkselected(UID)):
            command = f"SELECT CourseID FROM `selectedcourse` where StudentID = \"{UID}\";"
            cursor2.execute(command)
            S_CID = cursor2.fetchall()
            if(len(S_CID)>1):
                command = f"SELECT * FROM `course` where "
                for i in range(len(S_CID)):
                    if(i == len(S_CID)-1):
                        command += f"CourseID = \"{S_CID[i][0]}\";"
                        print(command)
                    else:
                        command += f"CourseID = \"{S_CID[i][0]}\" or "
                        print(command)
                cursor2.execute(command)
                data_a = cursor2.fetchall()
            else:
                command = f"SELECT * FROM `course` where CourseID = \"{S_CID[0][0]}\";"
                cursor2.execute(command)
                data_a = cursor2.fetchall()
                
            print(data_a)
            command = f"SELECT * FROM `course` ;"
            cursor2.execute(command)
            data_b = cursor2.fetchall()
            return data_a,data_b
        else:
            command = f"SELECT * FROM `course` ;"
            cursor2.execute(command)
            data_b = cursor2.fetchall()
            return 0,data_b
                

c.commit()
# login(100002) 
opcourse(100002)