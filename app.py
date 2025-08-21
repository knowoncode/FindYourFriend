from flask import Flask,render_template,request,redirect,url_for,flash,session
from user import UserOperation
from encryption import encrypt
from validation import Validation
from myemail import Email
import random
import findAddress


app = Flask(__name__)   # Flask object
app.secret_key ='gguhuis897894uif87yrgyds78r'

userObj = UserOperation()  #object of class UserOperation (user module)
validObj = Validation()    #object of class Validation(validation module)
emailObj = Email(app)      #object of class Email (myemail module)

otp={}   #empty dictionary for otp

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/userSignup',methods=['GET','POST'])
def userSignup():
    if request.method=='GET':
        return render_template('userSignup.html')
    else:
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']
        #------empty validation------------------
        dataList = [firstName,lastName,email,mobile,password]
        if validObj.checkEmpty(dataList):
            flash("field can't be empty!!!")
            return redirect(url_for('userSignup'))
        #--------alpha validation----------
        if validObj.checkAlpha(firstName) or validObj.checkAlpha(lastName):
            flash("name must be alphabate!!")
            return redirect(url_for('userSignup'))
        #--------mobile validation---------
        if validObj.checkMobile(mobile):
            flash("mobile must be 10 digit!!")
            return redirect(url_for('userSignup'))
        #------encryption------------------
        password = encrypt(password)
        #----------------------------------
        try:
            userObj.userInsert(firstName,lastName,email,mobile,password)
            otp['userOTP'] = random.randint(1000,9999)
            subject = "FindYourFriend:Email Verification"
            message = f"Hello {firstName}\nThis is email verification mail.\nYour OTP is: {otp['userOTP']}\nThank You\nFindYourFriend"
            emailObj.compose_mail(subject,email,message)
            return redirect(url_for('emailVerify',userEmail=email))
        except Exception as e:
            flash(f"something wrong {e}")
            return redirect(url_for('userSignup'))

@app.route('/emailVerify',methods=['POST','GET'])
def emailVerify():
    if request.method=='GET':
        email = request.args.get('userEmail')
        return render_template('emailVerify.html',userEmail=email)
    else:
        email = request.args.get('userEmail')
        userOTP = int(request.form['otp'])
        if userOTP==otp['userOTP']:
            otp.pop('userOTP',None)
            flash("successfully registered...login now!!")
            return redirect(url_for('userLogin'))
        else:
            userObj.userDelete(email)
            flash("your email is not verified..register again!!!")
            return redirect(url_for('userSignup'))

@app.route('/userLogin',methods=['POST','GET'])
def userLogin():
    if request.method=='GET':
        return render_template('userLogin.html')
    else:
        email = request.form['email']
        password = request.form['password']
        #------empty validation------------------
        dataList = [email,password]
        if validObj.checkEmpty(dataList):
            flash("field can't be empty!!!")
            return redirect(url_for('userLogin'))
        
        #------encryption------------------
        password = encrypt(password)
        
        status = userObj.userLogin(email,password)
        if status:
            return redirect(url_for('userDash'))
        else:
            flash("invalid email and password!!!")
            return redirect(url_for('userLogin'))
        
@app.route('/userLogout')
def userLogout():
    if 'userEmail' in session:
        session.clear()
        flash("logged out successfully!!!")
        return redirect(url_for('userLogin'))
    else:
        flash("Please Login To Access This Page..")
        return redirect(url_for('userLogin'))
    
@app.route('/userDash')
def userDash():
    if 'userEmail' in session:
        totalFriend = userObj.totalFriend()
        pendingRequest = userObj.pendingRequest()
        totalShare = userObj.totalShare()
        return render_template('userDash.html',totalFriend=totalFriend,pendingRequest=pendingRequest,totalShare=totalShare)
    else:
        flash("Please Login To Access This Page..")
        return redirect(url_for('userLogin'))
    
@app.route('/userProfile',methods=['GET','POST'])
def userProfile():
    if 'userEmail' in session:
        if request.method=='GET':
            record = userObj.userProfile()
            return render_template('userProfile.html',record=record)
        else:
            firstName = request.form['firstName']
            lastName = request.form['lastName']
            mobile = request.form['mobile']
            #------empty validation------------------
            dataList = [firstName,lastName,mobile]
            if validObj.checkEmpty(dataList):
                flash("field can't be empty!!!")
                return redirect(url_for('userProfile'))
            #--------alpha validation----------
            if validObj.checkAlpha(firstName) or validObj.checkAlpha(lastName):
                flash("name must be alphabate!!")
                return redirect(url_for('userProfile'))
            #--------mobile validation---------
            if validObj.checkMobile(mobile):
                flash("mobile must be 10 digit!!")
                return redirect(url_for('userProfile'))
            
            userObj.userUpdate(firstName,lastName,mobile)
            flash("your account is updated successfully!!")
            return redirect(url_for('userProfile'))
    else:
        flash("Please Login To Access This Page..")
        return redirect(url_for('userLogin'))
    
@app.route('/userDelete')
def userDelete():
    if 'userEmail' in session:
        userObj.userDelete(session['userEmail'])
        session.clear()
        flash("Your account is deleted successfully!! Hope to see you again..")
        return redirect(url_for('userSignup'))
    else:
        flash("Please Login To Access This Page..")
        return redirect(url_for('userLogin'))
    
@app.route('/userPassword',methods=['GET','POST'])
def userPassword():
    if 'userEmail' in session:
        if request.method=='GET':
            return render_template('userPassword.html')
        else:
            oldPassword = request.form['oldPassword']
            newPassword = request.form['newPassword']
            #------empty validation------------------
            dataList = [oldPassword,newPassword]
            if validObj.checkEmpty(dataList):
                flash("field can't be empty!!!")
                return redirect(url_for('userPassword'))
            
            #------encryption------------------
            oldPassword = encrypt(oldPassword)
            newPassword = encrypt(newPassword)

            status= userObj.userPasswordChange(oldPassword,newPassword)
            if status:
                session.clear()
                flash("Your password is changed successfully!!Login Again...")
                return redirect(url_for('userLogin'))
            else:
                flash("your old password is invalid..try again..")
                return redirect(url_for('userPassword'))
    else:
        flash("Please Login To Access This Page..")
        return redirect(url_for('userLogin'))
    
@app.route('/addFriend',methods=['GET','POST'])
def addFriend():
    if 'userEmail' in session:
        if request.method=='GET':
            data = userObj.friendList()
            return render_template('addFriend.html',record=data)
        else:
            name = request.form['name']
            friendEmail = request.form['friendEmail']
            #------empty validation------------------
            dataList = [name,friendEmail]
            if validObj.checkEmpty(dataList):
                flash("field can't be empty!!!")
                return redirect(url_for('addFriend'))
            
            userObj.addFriend(name,friendEmail)
            flash("New friend added successfully!!")
            return redirect(url_for('addFriend'))

    else:
        flash("Please Login To Access This Page..")
        return redirect(url_for('userLogin'))
    
@app.route('/deleteFriend',methods=['GET','POST'])
def deleteFriend():
    if 'userEmail' in session:
        if request.method=='GET':
            friendID = request.args.get('friendID')
            userObj.deleteFriend(friendID)
            flash("your one friend is deleted successfully!!!")
            return redirect(url_for('addFriend'))
    else:
        flash("Please Login To Access This Page..")
        return redirect(url_for('userLogin'))
    
@app.route('/editFriend',methods=['GET','POST'])
def editFriend():
    if 'userEmail' in session:
        if request.method=='GET':
            friendID = request.args.get('friendID')
            data = userObj.showFriend(friendID)
            return render_template('editFriend.html',record=data)
        else:
            friendID = request.args.get('friendID')
            name = request.form['name']
            friendEmail = request.form['friendEmail']
            #------empty validation------------------
            dataList = [name,friendEmail]
            if validObj.checkEmpty(dataList):
                flash("field can't be empty!!!")
                return redirect(url_for('editFriend',friendID=friendID))
            
            userObj.editFriend(friendID,name,friendEmail)
            flash("your friend information is updated successfully!!")
            return redirect(url_for('addFriend'))

    else:
        flash("Please Login To Access This Page..")
        return redirect(url_for('userLogin'))

@app.route('/userLocation')
def userLocation():
    if 'userEmail' in session:
        return render_template('myLocation.html')
    else:
        flash("Please Login To Access This Page..")
        return redirect(url_for('userLogin'))

@app.route('/userSendAddress')
def userSendAddress():
    if 'userEmail' in session:
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        location = findAddress.location(lat,lon)
        friendEmail = userObj.userFriendEmail()
        subject = "🌟👫🌟 My Location (FindYourFriend APP)"
        message=f"""
        <h2 style="color:#2e6c80;">Hello 👋,</h2>
        <p>This is my location. Come and meet 😊</p>
        <h3>Address:📍location</h3>
        <p>{location}</p>
        <hr>
        <p style="color:gray;"><a href='https://www.google.com/maps?q={lat},{lon}'>Click here to see my location</a></p>
        """
        
        for email in friendEmail:
            emailObj.compose_mail(subject,email[0],message)
        
        flash("Your location is shared with your friend!!")
        return redirect(url_for('userLocation'))
    else:
        flash("Please Login To Access This Page..")
        return redirect(url_for('userLogin'))
    
@app.route('/friendLocation')
def friendLocation():
    if 'userEmail' in session:
        data = userObj.friendList()
        reqList = userObj.requestList()
        return render_template('friendLocation.html',record=data,record1=reqList)
        
    else:
        flash("Please Login To Access This Page..")
        return redirect(url_for('userLogin'))

@app.route('/friendLocationRequest')
def friendLocationRequest():
    if 'userEmail' in session:
        friendEmail = request.args.get('friendEmail')
        userObj.friendLocationRequest(friendEmail)
        flash("Location Request sent Successfully!!")
        return redirect(url_for('friendLocation'))      
    else:
        flash("Please Login To Access This Page..")
        return redirect(url_for('userLogin'))
    
@app.route('/sendLocation')
def sendLocation():
    if 'userEmail' in session:
        friendEmail = request.args.get('friendEmail')
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        location = findAddress.location(lat,lon)
        subject = "🌟👫🌟 My Location (FindYourFriend APP)"
        message=f"""
        <h2 style="color:#2e6c80;">Hello 👋,</h2>
        <p>This is my location. Come and meet 😊</p>
        <h3>Address:📍location</h3>
        <p>{location}</p>
        <hr>
        <p style="color:gray;"><a href='https://www.google.com/maps?q={lat},{lon}'>Click here to see my location</a></p>
        """
        
        emailObj.compose_mail(subject,friendEmail,message)

        #update status=1 to the given friendEmail
        userObj.requestStatusUpdate(friendEmail)
        
        flash("Your location is shared with your friend!!")
        return redirect(url_for('friendLocation'))
    else:
        flash("Please Login To Access This Page..")
        return redirect(url_for('userLogin'))

if __name__=='__main__':
    app.run(host='0.0.0.0',port='5001',debug=True)  # activate the server