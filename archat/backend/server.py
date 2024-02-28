
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import hashlib
import math
import random

import mysql.connector

mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database = "ArcChat"
)
print(mydb)

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        mydb.reconnect()
        if self.path == "/login":
            if self.headers['user'] and self.headers['pwd']:
                cursor = mydb.cursor()

                cursor.execute("SELECT id FROM users WHERE username = \""+self.headers['user']+"\" AND password = \""+self.headers['pwd']+"\"")
                
                print("SELECT id FROM users WHERE username = \""+self.headers['user']+"\" AND password = \""+self.headers['pwd']+"\"")

                id = cursor.fetchone()[0]

                if id != "":
                    cursor.execute("SELECT token from tokens WHERE userid = \""+str(id)+"\"")

                    token = cursor.fetchone()
                    if token:
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(bytes(token[0], "utf-8"))
                    else:
                        tokenrng = str(random.randint(0,10000000))
                        token = hashlib.md5(tokenrng.encode()).hexdigest()
                        cursor.execute(str("INSERT INTO tokens (token, userid) VALUES (\""+str(token)+"\",\""+str(id)+"\")"))
                        mydb.commit()
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(bytes(token, "utf-8"))
                else:
                    self.send_response(403)
                    self.end_headers()
                    self.wfile.write(bytes("Incorrect username or password.", "utf-8"))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(bytes("Missing credentials.", "utf-8"))
        elif self.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes("Success.", "utf-8"))
        elif self.path == '/tokenlogin':
            if self.headers['token']:
                cursor = mydb.cursor()

                cursor.execute("SELECT userid FROM tokens WHERE token=\""+self.headers['token']+"\"")

                uid = str(cursor.fetchone()[0])

                print(uid)

                if uid != "":
                    cursor.execute("SELECT username FROM users WHERE id=\""+uid+"\"")

                    username = cursor.fetchone()[0]
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(bytes("{\"user\":\""+username+"\"}", "utf-8"))
                else:
                    self.send_response(403)
                    self.end_headers()
                    self.wfile.write(bytes('Token incorrect.', "utf-8"))
                    return
                    
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(bytes('Token Error.', "utf-8"))
        elif self.path == "/getmsgs":
            if self.headers['token']:
                token = self.headers['token']
                print(token)
                cursor = mydb.cursor()
                command = "SELECT userid FROM tokens WHERE token = \""+token+"\""
                print(command)
                cursor.execute(command)
                uidtest = cursor.fetchone()
                print(uidtest[0])
                

                if uidtest:
                        messagestring = ""
                        i = 0
                        self.send_response(200)
                        self.end_headers()
                        mycursor = mydb.cursor()

                        mycursor.execute("SELECT messagedata FROM messages WHERE community = 0 AND channel = 0")

                        myresult = mycursor.fetchall()
                        
                        for x in myresult:
                            messagestring = messagestring + myresult[i][0] + "\\"
                            i+=1
                        i = 0
                        if messagestring.endswith("\\"):
                            messagestring = messagestring[:-1]
                        self.wfile.write(bytes(messagestring, "utf-8"))
                else:
                    self.send_response(403)
                    self.end_headers()
                    self.wfile.write(bytes('Bad Token', "utf-8"))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(bytes('Token Missing.', "utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes('Not Found.', "utf-8"))
    def do_POST(self):
        mydb.reconnect()
        if self.path == '/sendmsg':
            if self.headers['token']:
                token = self.headers['token']
                print(token)
                cursor = mydb.cursor()
                command = "SELECT userid FROM tokens WHERE token = \""+token+"\""
                print(command)
                cursor.execute(command)
                uidtest = cursor.fetchone()
                print(uidtest[0])
                

                if uidtest:
                    
                    mycursor = mydb.cursor()

                    sql = "INSERT INTO messages (community, channel, messagedata) VALUES (%s, %s, %s)"

                    messagedata = str(self.headers['message'])

                    val = (0,0,messagedata)
                    mycursor.execute(sql, val)

                    mydb.commit()   
                    print(self.headers['token'])
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(bytes('Success.', "utf-8"))
                else:
                    print("why.")
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(bytes('Token Error.', "utf-8"))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(bytes('Token Error.', "utf-8"))
            #pobam
            print('/sendmsg')

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
