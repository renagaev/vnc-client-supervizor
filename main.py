from flask import Flask
from controller import Controller

app = Flask(__name__)

host = "192.168.0.109"
port = 5900
controller = Controller(host, port)

controller.start()


@app.route("/status")
def get_status():
    return controller.get_status()


@app.route("/restart")
def restart():
    controller.force_restart()
    return "ok"


app.run("0.0.0.0", 80)
