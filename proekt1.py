from flask import Flask, request, jsonify
from sqlite3 import connect
import json
from telegram import telegram_funkcija
from pymongo import MongoClient
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/total_spent/<int:user_id>', methods = ['GET']) 
def total_spending(user_id):                                                   
    db_connection = connect('users_vouchers.db')                           # if request.method =='GET':                                                   
    db_cursor = db_connection.cursor()                                     #user_id=request.form['user_id']
    rezultat = db_cursor.execute("SELECT SUM(money_spent) FROM user_spending WHERE user_id = '{}'".format(user_id))
    lista = rezultat.fetchall() #lista od tuples
    if list(lista)==[]:
        return 'Vnesovte nevaliden user_id'
    else:
        suma = list(sum(lista,()))[0]  #float
        # return f'Userot: {json.dumps(user_id)} ima vkupna potrosuvacka od: {json.dumps(suma)}'  #deka treba da sodrzi user_id i vkupna potrosuvacka dali vo lista ili ?
        return jsonify(user_id = user_id,
                       vkupna_potrosuvacka = suma)
    
@app.route('/total_spending_by_age', methods=['GET'])
def total_spent_by_age():

    def funkcija(a,b):
        """
        Funkcijata ja presmetuva prosecnata potrosuvacka na odredena starosna grupa za vnesena granica na starosna grupa
        param a: int 
        param b: int 
        a i b se odnesuvaat vo smisla na dadenata granica [a,b]
        """
        db_connection = connect('users_vouchers.db') 
        db_cursor = db_connection.cursor()
        
        rezultat = db_cursor.execute("SELECT user_id FROM user_info WHERE age>='{}' AND age<='{}' ".format(a,b))   
        lista =rezultat.fetchall()  #lista od tuples od user_id vo taa granica
        lista_user_id = list(sum(lista,()))  # lista od tuples -> to list
        # print(r) 
        br_na_user_id = len(lista_user_id)  #kolkav e brojot na lugje vo taa starosna granica 
        # print("dolzina na lista",len(r))  # dolzina na lista 
        suma=0
        for user_id in lista_user_id:
            grupa = db_cursor.execute("SELECT money_spent FROM user_spending WHERE user_id = '{}'".format(user_id)) #return tuple 
            lista1 = grupa.fetchall() #list of tuples 
            
            lista1_r = list(sum(lista1,())) #list of tuples to list #lista od kolku potrosil toj user_id
            suma = suma + sum(lista1_r)

        return suma/br_na_user_id   

    #pie chart 
    grupi = ['18-24','25-30','31-36','37-47','47>'] 
    sredna_vr = [funkcija(18,24), funkcija(25,30), funkcija(31,36), funkcija(37,47), funkcija(48,100)]  
    plt.subplot(121)
    plt.pie(sredna_vr, labels=grupi, autopct='%.2f%%')
    plt.title("Sredna potrosuvacka na soodvetnite dadeni starosni grupi")
    #bar graph 
    positions = range(len(sredna_vr))
    plt.subplot(122)
    plt.bar(positions, sredna_vr, color = 'lightblue')
    plt.xticks(positions, grupi)
    plt.title('Sredna potrosuvacka na starosnite grupi')
    plt.xlabel('Starosni grupi')
    plt.ylabel('Sredna potrosuvacka')
    plt.show()

    # send to Telegram 
    dics = {'18-24': funkcija(18,24), '25-30': funkcija(25,30), '31-36':funkcija(31,36), '37-47':funkcija(37,47), '47>':funkcija(48,100)}
    telegram_funkcija(dics)

    return jsonify(grupa_18_24=funkcija(18,24),
                   grupa_25_30 =funkcija(25,30),
                   grupa_31_36 = funkcija(31,36),
                   grupa_37_47 = funkcija(37,47),
                   grupa_pogolema_od_47 = funkcija(48,100) )



client = MongoClient('mongodb://localhost:27017/')
db = client.user_db
collection = db.userCollection

@app.route('/write_to_mongodb',methods=['GET','POST'])
def write_to_mongo():

    data = request.get_json()
    if collection.find_one({'user_id': data['user_id']}):
        return json.dumps({'Error': f'Postoi korisnik so user_id {data["user_id"]} '}), 400
    else:
        if data['total_spending'] >= 2000:
            result = collection.insert_one(data)
            if result.inserted_id:
                return json.dumps({'Success': 'Podatocite se uspesno zapisani'}), 201
            else:
                return json.dumps({'Error': 'Ne se zapisaa podatocite'}), 500
        else:
            return json.dumps({'Bad Request': 'Vkupnata potrosuvacka mora da e pogolema od 2000'}), 400

if __name__ == '__main__':
    app.run(debug=True)