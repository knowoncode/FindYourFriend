import mysql.connector as sql
from flask import session
from datetime import date


class UserOperation:
    def __init__(self):
        self.create_user_table()
        self.create_friend_table()
        self.create_friendLocation_table()

    def connect(self):
        con = sql.connect(host='mysql-13895a0a-knowon-43fc.f.aivencloud.com',port='14619',user='avnadmin',password='AVNS_OhXlk3ZcwW08DrVLo_V',database='defaultdb')
        return con
    
    # --- Create User Table if not exists ---
    def create_user_table(self):
        db = self.connect()
        cur = db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user (
                firstName VARCHAR(255) NOT NULL,
                lastName VARCHAR(255) NOT NULL,
                email VARCHAR(255) PRIMARY KEY,
                mobile VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        db.commit()
        cur.close()
        db.close()
        return

    # --- Create Friend Location Table if not exists ---
    def create_friendLocation_table(self):
        db = self.connect()
        cur = db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS locationrequest (
                flocationRequestID int AUTO_INCREMENT PRIMARY KEY,
                userEmail varchar(255) DEFAULT NULL,
                friendEmail varchar(255) DEFAULT NULL,
                requestDate date DEFAULT NULL,
                status int DEFAULT '0',
            )
        """)
        db.commit()
        cur.close()
        db.close()
        return

    # --- Create Friend Table if not exists ---
    def create_friend_table(self):
        db = self.connect()
        cur = db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS friend (
                friendID int AUTO_INCREMENT PRIMARY KEY,
                userEmail varchar(255) DEFAULT NULL,
                name varchar(255) DEFAULT NULL,
                friendEmail varchar(255) DEFAULT NULL,
            )
        """)
        db.commit()
        cur.close()
        db.close()
        return

    def userInsert(self,firstName,lastName,email,mobile,password):
        db = self.connect()
        cur = db.cursor()
        sq = "insert into user (firstName,lastName,email,mobile,password) values(%s,%s,%s,%s,%s)"
        record = [firstName,lastName,email,mobile,password]
        cur.execute(sq,record)
        db.commit()   #save the data in database
        cur.close()
        db.close()

    def userDelete(self,email):
        db = self.connect()
        cur = db.cursor()
        sq = "delete from user where email=%s"
        record = [email]
        cur.execute(sq,record)
        db.commit()   #save the data in database
        cur.close()
        db.close()

    def userLogin(self,email,password):
        db = self.connect()
        cur = db.cursor()
        sq = "select firstName,email from user where email=%s and password=%s"
        record = [email,password]
        cur.execute(sq,record)
        row = cur.fetchall()
        if row:
            session['userName']=row[0][0]
            session['userEmail']=row[0][1]
            return True
        
        return False
    
    def userProfile(self):
        db = self.connect()
        cur = db.cursor()
        sq = "select firstName,lastName,email,mobile from user where email=%s"
        record = [session['userEmail']]
        cur.execute(sq,record)
        row = cur.fetchall()
        return row
    
    def userUpdate(self,firstName,lastName,mobile):
        db = self.connect()
        cur = db.cursor()
        sq = "update user set firstName=%s,lastName=%s,mobile=%s where email=%s"
        record = [firstName,lastName,mobile,session['userEmail']]
        cur.execute(sq,record)
        db.commit()   #save the data in database
        session['userName'] = firstName
        cur.close()
        db.close()

    def userPasswordChange(self,oldPassword,newPassword):
        db = self.connect()
        cur = db.cursor()
        sq = "select * from user where email=%s and password=%s"
        record=[session['userEmail'],oldPassword]
        cur.execute(sq,record)
        data = cur.fetchall()
        if data:
            sq = "update user set password=%s where email=%s"
            record=[newPassword,session['userEmail']]
            cur.execute(sq,record)
            db.commit() 
            cur.close()
            db.close()
            return True
        
        return False

    def addFriend(self,name,friendEmail):
        db = self.connect()
        cur = db.cursor()
        sq = "insert into friend (userEmail,name,friendEmail) values(%s,%s,%s)"
        record = [session['userEmail'],name,friendEmail]
        cur.execute(sq,record)
        db.commit()   #save the data in database
        cur.close()
        db.close()

    def friendList(self):
        db = self.connect()
        cur = db.cursor()
        sq = "select friendID,name,friendEmail from friend where userEmail=%s"
        record=[session['userEmail']]
        cur.execute(sq,record)
        data = cur.fetchall()
        return data
    
    def deleteFriend(self,friendID):
        db = self.connect()
        cur = db.cursor()
        sq = "delete from friend where friendID=%s"
        record = [friendID]
        cur.execute(sq,record)
        db.commit()   #save the data in database
        cur.close()
        db.close()

    def showFriend(self,friendID):
        db = self.connect()
        cur = db.cursor()
        sq = "select friendID,name,friendEmail from friend where friendID=%s"
        record=[friendID]
        cur.execute(sq,record)
        data = cur.fetchall()
        return data
    
    def editFriend(self,friendID,name,friendEmail):
        db = self.connect()
        cur = db.cursor()
        sq = "update friend set name=%s,friendEmail=%s where friendID=%s"
        record = [name,friendEmail,friendID]
        cur.execute(sq,record)
        db.commit()   #save the data in database
        cur.close()
        db.close()

    def userFriendEmail(self):
        db = self.connect()
        cur = db.cursor()
        sq = "select friendEmail from friend where userEmail=%s"
        record=[session['userEmail']]
        cur.execute(sq,record)
        data = cur.fetchall()
        return data

    
    def friendLocationRequest(self,friendEmail):
        db = self.connect()
        cur = db.cursor()
        requestDate = date.today()
        sq = "insert into locationrequest (userEmail,friendEmail,requestDate) values(%s,%s,%s)"
        record = [session['userEmail'],friendEmail,requestDate]
        cur.execute(sq,record)
        db.commit()   #save the data in database
        cur.close()
        db.close()

    def requestList(self):
        db = self.connect()
        cur = db.cursor()
        sq = "select userEmail,firstName from locationrequest r,user u where friendEmail=%s and status=%s and r.userEmail=u.email"
        record=[session['userEmail'],0]
        cur.execute(sq,record)
        data = cur.fetchall()
        return data
    
    def requestStatusUpdate(self,friendEmail):
        db = self.connect()
        cur = db.cursor()
        sq = "update locationrequest set status=%s where userEmail=%s and friendEmail=%s"
        record = [1,friendEmail,session['userEmail']]
        cur.execute(sq,record)
        db.commit()   #save the data in database
        cur.close()
        db.close()

    def totalFriend(self):
        db = self.connect()
        cur = db.cursor()
        sq = "select count(*) from friend where userEmail=%s"
        record=[session['userEmail']]
        cur.execute(sq,record)
        data = cur.fetchall()
        return data[0][0]
    
    def pendingRequest(self):
        db = self.connect()
        cur = db.cursor()
        sq = "select count(*) from locationrequest where friendEmail=%s and status=%s"
        record=[session['userEmail'],0]
        cur.execute(sq,record)
        data = cur.fetchall()
        return data[0][0]
    
    def totalShare(self):
        db = self.connect()
        cur = db.cursor()
        sq = "select count(*) from locationrequest where friendEmail=%s and status=%s"
        record=[session['userEmail'],1]
        cur.execute(sq,record)
        data = cur.fetchall()
        return data[0][0]
