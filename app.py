import os
#from ip import ip_public
import subprocess
import json
#from datetime import datetime
from ldap3 import Server, Connection
from flask import Flask, render_template, request, session, redirect, url_for
import socket
import requests

# import rds_connect_mysql as rds
import flask

app = flask.Flask(__name__)
app.secret_key = 'keykey'


def auth_ldap(username, password):
    server = Server('192.168.0.8')
    domain = 'La'
    conn = Connection(server, user="{}\\{}".format(domain, username), password=password)
    bind = conn.bind()

    output = {}
    if bind:
        conn.search('dc=la,dc=net', '(sAMAccountName={})'.format(username))
        entry = conn.entries[0]
        dn = json.loads(entry.entry_to_json())
        name = dn['dn'].split(',')[0].split('=')[1]
        mail = username + "@la.net"

        output['name'] = name
        output['mail'] = mail
        output['status'] = 'SUCCESS'
    else:
        output['status'] = 'FAIL'
    return output


@app.route("/", methods= ['GET', 'POST'])
def home():
    
    
    if request.method == 'GET':
        
        output = {}
        if 'output' in session:
            output = session['output']
        
            return render_template('dashboard.html', data = output)

        return render_template('login.html', data = output)

    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        #ip local
        iplocal = request.remote_addr
        print("IP local:") 
        print(iplocal)
        
        

        output = auth_ldap(username, password)

        if 'name' in output:
            session['output'] = output
            #them vao
            output['iplocal'] = iplocal

        # print(output)

        if output['status'] == 'FAIL':
            return render_template('login.html', data = output)
           
        else:
            #  Exxcute bat file
            try:
                os.system('iptables -I INPUT -s {} -p udp --dport 1194 -j ACCEPT'.format(iplocal))
               
                
            #    pipe.communicate()

            except :
            
                output['status'] = 'RUN_FAIL'
                
                
            return render_template('dashboard.html', data = output)


@app.route("/logout")
def logout():
    if 'output' in session:
        session.pop('output', None)
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(host='10.10.1.13', port=80, debug=True)
