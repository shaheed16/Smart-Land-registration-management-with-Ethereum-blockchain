from flask import Flask, render_template, request, redirect, url_for, session,send_from_directory
import json
from web3 import Web3, HTTPProvider
import os
import datetime
import ipfsApi
import pickle


app = Flask(__name__)

global uname, details,pid

api = ipfsApi.Client(host='http://127.0.0.1', port=5001)

def readDetails(contract_type):
    global details
    details = ""
    blockchain_address = 'http://127.0.0.1:8545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Land.json' 
    deployed_contract_address = '0x1238AF37b575f435F686C1d046730abB2c0969e5' #hash address to access counter feit contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
    if contract_type == 'adduser':
        details = contract.functions.getUserDetails().call()
    if contract_type == 'land':
        details = contract.functions.getLandDetails().call()
    if contract_type == 'history':
        details = contract.functions.gethistory().call()
    if contract_type == 'purchase':
        details = contract.functions.getpurchase().call()
    if len(details) > 0:
        if 'empty' in details:
            details = details[5:len(details)]    
    print(details)    

def saveDataBlockChain(currentData, contract_type):
    global details
    global contract
    details = ""
    blockchain_address = 'http://127.0.0.1:8545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Land.json' 
    deployed_contract_address = '0x1238AF37b575f435F686C1d046730abB2c0969e5' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    readDetails(contract_type)
    if contract_type == 'adduser':
        details+=currentData
        msg = contract.functions.setUserDetails(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'land':
        details+=currentData
        msg = contract.functions.setLandDetails(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'history':
        details+=currentData
        msg = contract.functions.sethistory(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'purchase':
        details+=currentData
        msg = contract.functions.setpurchase(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)


@app.route('/UserSignUpAction', methods=['GET', 'POST'])
def UserSignUpAction():
    if request.method == 'POST':
        global details
        uname = request.form['t1']
        password = request.form['t2']
        phone = request.form['t3']
        email = request.form['t4']
        address = request.form['t5']
        status = "none"
        readDetails('adduser')
        arr = details.split("\n")
        status = "none"
        for i in range(len(arr)-1):
            array = arr[i].split("#")
            if array[1] == 'User' and array[2] == uname:
                status = uname+" Username already exists"
                return render_template('UserSignup.html', msg=status)
                break
        if status == "none":
            data = "Requested"+"#"+"User"+"#"+uname+"#"+password+"#"+phone+"#"+email+"#"+address+"\n"
            saveDataBlockChain(data,"adduser")
            context = "Request Sent Successfully."
            return render_template('UserSignup.html', msg=context)
        else:
            status == 'Error in SignUp Process'
            return render_template('UserSignup.html', msg=status)


@app.route('/UserLoginAction', methods=['GET', 'POST'])
def UserLoginAction():
    global uname
    if request.method == 'POST' and 't1' in request.form and 't2' in request.form:
        user = request.form['t1']
        password = request.form['t2']
        status = "none"
        readDetails('adduser')
        arr = details.split("\n")
        for i in range(len(arr)-1):
            array = arr[i].split("#")
            if array[0] == 'Accepted' and array[1] == user and array[2] == password:
                uname = user
                status = "success"
                break
        if status == "success":
            context = "Welcome "+user
            return render_template('UserScreen.html', msg=context)
        else:
            context = "Invalid Details."
            return render_template('UserSignIn.html', msg=context)

@app.route('/CentralAuthorityLoginAction', methods=['GET', 'POST'])
def CentralAuthorityLoginAction():
    global uname
    if request.method == 'POST' and 't1' in request.form and 't2' in request.form:
        user = request.form['t1']
        password = request.form['t2']
        status = "none"
        if user == 'admin' and password == 'admin':
            context = "Welcome Central Authority."
            return render_template('AuthorityScreen.html', msg=context)
        else:
            context = "Invalid Details."
            return render_template('AuthoritySignIn.html', msg=context)

def check_status(name):
    readDetails('adduser')
    arr = details.split("\n")
    for i in range(len(arr)-1):
        array = arr[i].split("#")
        if array[0] in ['Accepted', 'Decline'] and array[1] == name:
            return True
            break
    return False


@app.route('/CheckUser', methods=['GET', 'POST'])
def CheckUser():
    if request.method == 'GET':
        output = '<table border="1" align="center" width="100%">'
        font = '<font size="3" color="black">'
        headers = ['Username', 'Password', 'Phone', 'Email', 'Address', 'Action']

        output += '<tr>'
        for header in headers:
            output += f'<th>{font}{header}{font}</th>'
        output += '</tr>'

        readDetails('adduser')
        arr = details.split("\n")

        for i in range(len(arr) - 1):
            array = arr[i].split("#")
            username = array[2]

            if array[0] == 'Requested' and array[1] == 'User':
                output += '<tr>'
                for cell in array[2:7]:
                    output += f'<td>{font}{cell}{font}</td>'

                action_cell = ''
                if check_status(username):
                    action_cell = f'<td>{font}Already Submitted{font}</td>'
                else:
                    action_cell = f'<td><a href="/SubmitStatus?username={array[2]}&password={array[3]}&phone={array[4]}&email={array[5]}&address={array[6]}">{font}Click Here to Accept/Decline{font}</a></td>'

                output += action_cell
                output += '</tr>'

        output += '</table><br/><br/><br/>'
        return render_template('CheckUser.html', data=output)


@app.route('/SubmitStatus', methods=['GET', 'POST'])
def SubmitStatus():
    global username,password,phone,email,address

    if request.method == 'GET':
        username = request.args.get('username')
        password = request.args.get('password')
        phone = request.args.get('phone')
        email = request.args.get('email')
        address = request.args.get('address')
        return render_template('SubmitStatus.html')

    if request.method == 'POST':
        status = request.form['t1']
        data = status+"#"+username+"#"+password+"#"+phone+"#"+email+"#"+address+"\n"
        saveDataBlockChain(data, "adduser")

        context = "Status Marked Successfully."

        return render_template('SubmitStatus.html', data=context)

@app.route('/AddLandAction', methods=['GET', 'POST'])
def AddLandAction():
    if request.method == 'POST':
        global uname
        pin = request.form['t1']
        psize = request.form['t2']
        paddress = request.form['t3']
        price = request.form['t4']
        typ = request.form['t5']
        uploaded_file = request.files['t6']
        filename = uploaded_file.filename
        myfile = uploaded_file.read()
        myfile = pickle.dumps(myfile)
        hashcode = api.add_pyobj(myfile)
        status = "none"
        readDetails('land')
        arr = details.split("\n")
        status = "none"
        for i in range(len(arr)-1):
            array = arr[i].split("#")
            if array[1] == pin:
                status = "Land is already added."
                return render_template('AddLand.html', msg=status)
                break
        if status == "none":
            data = uname+"#"+pin+"#"+psize+"#"+paddress+"#"+price+"#"+typ+"#"+hashcode+"\n"
            saveDataBlockChain(data,"land")
            context = "Land Details Added Successfully to blockchain with hashcode "+hashcode
            return render_template('AddLand.html', msg=context)
        else:
            status == 'Error in Process'
            return render_template('AddLand.html', msg=status)

def check_land(number,name):
    readDetails('history')
    arr = details.split("\n")
    for i in range(len(arr)-1):
        array = arr[i].split("#")
        if array[0] in ['Accepted', 'Decline'] and array[1] == name and array[2] == number:
            return True
            break
    return False


@app.route('/CheckLand', methods=['GET', 'POST'])
def CheckLand():
    if request.method == 'GET':
        global username,req_id,land_size,address,price,typ,photo
        output = '<table border="1" align="center" width="100%">'
        font = '<font size="3" color="black">'
        headers = ['Username', 'Request Id', 'Land Size', 'Address', 'Price','Type','Photo', 'Action']

        output += '<tr>'
        for header in headers:
            output += f'<th>{font}{header}{font}</th>'
        output += '</tr>'

        readDetails('land')
        arr = details.split("\n")

        for i in range(len(arr) - 1):
            array = arr[i].split("#")
            no = array[1]
            name = array[0]
            output += '<tr>'
            for cell in array[0:6]:
                output += f'<td>{font}{cell}{font}</td>'
            content = api.get_pyobj(array[6])
            content = pickle.loads(content)
            if os.path.exists('static/photo/'+array[6]):
                os.remove('static/photo/'+array[6])
            with open('static/photo/'+array[6], "wb") as file:
                file.write(content)
            file.close()
            output += '<td><img src=static/photo/'+array[6]+'  width=500 height=500></img></td>'  
            action_cell = ''
            if check_land(no,name):
                action_cell = f'<td>{font}Already Submitted{font}</td>'
            else:
                action_cell = f'<td><a href="/SubmitStatusForLand?username={array[0]}&req_id={array[1]}&land_size={array[2]}&address={array[3]}&price={array[4]}&type={array[5]}&photo={array[6]}">{font}Click Here to Accept/Decline{font}</a></td>'

            output += action_cell
            output += '</tr>'

        output += '</table><br/><br/><br/>'
        return render_template('CheckLand.html', data=output)


@app.route('/SubmitStatusForLand', methods=['GET', 'POST'])
def SubmitStatusForLand():
    global username,req_id,land_size,address,price,typ,photo

    if request.method == 'GET':
        username = request.args.get('username')
        req_id = request.args.get('req_id')
        land_size = request.args.get('land_size')
        address = request.args.get('address')
        price = request.args.get('price')
        typ = request.args.get('type')
        photo = request.args.get('photo')
        return render_template('SubmitStatusForLand.html')

    if request.method == 'POST':
        status = request.form['t1']
        data = status+"#"+username+"#"+req_id+"#"+land_size+"#"+address+"#"+price+"#"+typ+"#"+photo+"\n"
        saveDataBlockChain(data, "history")

        context = "Status Marked Successfully."

        return render_template('SubmitStatusForLand.html', data=context)


def check_purchase(req_id):
    readDetails('purchase')
    arr = details.split("\n")
    for i in range(len(arr)-1):
        array = arr[i].split("#")
        if array[2] == req_id:
            return True
            break
    return False


@app.route('/BuyLand', methods=['GET', 'POST'])
def BuyLand():
    if request.method == 'GET':
        global username,req_id,land_size,address,price,typ,photo,uname
        output = '<table border="1" align="center" width="100%">'
        font = '<font size="3" color="black">'
        headers = ['Username', 'Request Id', 'Land Size', 'Address', 'Price','Type','Photo', 'Action']

        output += '<tr>'
        for header in headers:
            output += f'<th>{font}{header}{font}</th>'
        output += '</tr>'

        readDetails('history')
        arr = details.split("\n")

        for i in range(len(arr) - 1):
            array = arr[i].split("#")
            if array[0] == "Accepted" and array[1] != uname:
                req_id = array[2]
                output += '<tr>'
                for cell in array[1:7]:
                    output += f'<td>{font}{cell}{font}</td>'
                content = api.get_pyobj(array[7])
                content = pickle.loads(content)
                if os.path.exists('static/photo/'+array[7]):
                    os.remove('static/photo/'+array[7])
                with open('static/photo/'+array[7], "wb") as file:
                    file.write(content)
                file.close()
                output += '<td><img src=static/photo/'+array[7]+'  width=500 height=500></img></td>'  
                action_cell = ''
                if check_purchase(req_id):
                    action_cell = f'<td>{font}Already Submitted{font}</td>'
                else:
                    action_cell = f'<td><a href="/SubmitPurchase?username={array[1]}&req_id={array[2]}&land_size={array[3]}&address={array[4]}&price={array[5]}&type={array[6]}&photo={array[7]}">{font}Click Here to Accept/Decline{font}</a></td>'

                output += action_cell
                output += '</tr>'

        output += '</table><br/><br/><br/>'
        return render_template('BuyLand.html', data=output)


@app.route('/SubmitPurchase', methods=['GET', 'POST'])
def SubmitPurchase():
    global username,req_id,land_size,address,price,typ,photo,uname

    if request.method == 'GET':
        username = request.args.get('username')
        req_id = request.args.get('req_id')
        land_size = request.args.get('land_size')
        address = request.args.get('address')
        price = float(request.args.get('price', 0))
        typ = request.args.get('type')
        photo = request.args.get('photo')
        return render_template('SubmitPurchase.html')

    if request.method == 'POST':
        amount = float(request.form['t1'])

        if amount > price:
            context = "Purchase Made Successfully, Land is Transferred Successfully."
            data = uname+"#"+username+"#"+req_id+"#"+land_size+"#"+address+"#"+str(price)+"#"+typ+"#"+str(amount)+"#"+photo+"\n"
            saveDataBlockChain(data, "purchase")
        else:
            context = "Required Amount is more."

        return render_template('SubmitPurchase.html', data=context)


@app.route('/ViewPurchase', methods=['GET', 'POST'])
def ViewPurchase():
    if request.method == 'GET':
        global username,req_id,land_size,address,price,typ,photo,uname
        output = '<table border="1" align="center" width="100%">'
        font = '<font size="3" color="black">'
        headers = ['Purchased By','Purchased From', 'Request Id', 'Land Size', 'Address', 'Price','Type','Amount Paid','Photo']

        output += '<tr>'
        for header in headers:
            output += f'<th>{font}{header}{font}</th>'
        output += '</tr>'

        readDetails('purchase')
        arr = details.split("\n")

        for i in range(len(arr) - 1):
            array = arr[i].split("#")
            if array[0] == uname or array[1] == uname:
                output += '<tr>'
                for cell in array[0:8]:
                    output += f'<td>{font}{cell}{font}</td>'
                content = api.get_pyobj(array[8])
                content = pickle.loads(content)
                if os.path.exists('static/photo/'+array[8]):
                    os.remove('static/photo/'+array[8])
                with open('static/photo/'+array[8], "wb") as file:
                    file.write(content)
                file.close()
                output += '<td><img src=static/photo/'+array[8]+'  width=500 height=500></img></td>'  
                output += '</tr>'

        output += '</table><br/><br/><br/>'
        return render_template('ViewPurchase.html', data=output)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html', msg='')

@app.route('/ViewPurchase', methods=['GET', 'POST'])
def ViewPurchases():
    return render_template('ViewPurchase.html', msg='')

@app.route('/AuthoritySignIn', methods=['GET', 'POST'])
def AuthoritySignIn():
    return render_template('AuthoritySignIn.html', msg='')

@app.route('/CheckUser', methods=['GET', 'POST'])
def CheckUsers():
    return render_template('CheckUser.html', msg='')

@app.route('/SubmitStatus', methods=['GET', 'POST'])
def SubmitStatuss():
    return render_template('SubmitStatus.html', msg='')

@app.route('/UserScreen', methods=['GET', 'POST'])
def UserScreen():
    return render_template('UserScreen.html', msg='')

@app.route('/UserSignIn', methods=['GET', 'POST'])
def UserSignIn():
    return render_template('UserSignIn.html', msg='')

@app.route('/UserSignup', methods=['GET', 'POST'])
def UserSignup():
    return render_template('UserSignup.html', msg='')

@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', msg='')

@app.route('/AuthorityScreen', methods=['GET', 'POST'])
def AuthorityScreens():
   return render_template('AuthorityScreen.html', msg='')

@app.route('/AddLand', methods=['GET', 'POST'])
def AddLand():
    return render_template('AddLand.html', msg='')

@app.route('/SubmitStatusForLand', methods=['GET', 'POST'])
def SubmitStatusForLands():
    return render_template('SubmitStatusForLand.html', msg='')

@app.route('/CheckLand', methods=['GET', 'POST'])
def CheckLands():
    return render_template('CheckLand.html', msg='')

@app.route('/BuyLand', methods=['GET', 'POST'])
def BuyLands():
    return render_template('BuyLand.html', msg='')

@app.route('/SubmitPurchase', methods=['GET', 'POST'])
def SubmitPurchases():
    return render_template('SubmitPurchase.html', msg='')

if __name__ == '__main__':
    app.run()










