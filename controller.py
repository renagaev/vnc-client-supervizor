from threading import Thread
import subprocess
import socket
import time


class Controller:
    def __init__(self, host, port):
        self.process = None
        self.host = host
        self.port = port
        self.status = "inited"
        self.output = ""

    def get_status(self):
        return "status: "+self.status + "\n\n\n" + self.output

    def start(self):
        Thread(target=self._start).start()

    def host_reachable(self):
        command = ["ping", "-c1", self.host]
        return subprocess.call(command, stdout=subprocess.DEVNULL) == 0

    def port_reachable(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)

        result = s.connect_ex((self.host, self.port)) == 0
        s.close()
        return result

    def wait_host(self):
        self.status = "wait host"
        while True:
            time.sleep(1)
            reachable = self.host_reachable()
            if reachable:
                self.status = "host reachable"
                break

    def wait_port(self):
        self.status = "wait port"
        while True:
            time.sleep(1)
            reachable = self.port_reachable()
            if reachable:
                self.status = "port reachable"
                break

    def _start_read(self):
        if self.process is None:
            return
        while True:
            output = self.process.stdout.readline()
            if output == '' and self.process.poll() is not None:
                break
            if output:
                self.output += "\n" + output.strip()
                if len(self.output) > 2000:
                    self.output = self.output[:1998]

    def _start_watch(self):
        while True:
            time.sleep(1)
            if self.status == 'app active':
                if self.process.poll() is not None:
                    self.force_restart()
                    break

    def _start(self):
        self.wait_host()
        self.wait_port()
        self.start_app()

    def start_app(self):
        command = ["ssvncviewer", "-fullscreen", self.host]
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE)
        self.status = "app active"
        Thread(target=self._start_read).start()
        Thread(target=self._start_watch).start()

    def force_restart(self):
        if self.status == "app active":
            self.process.terminate()
            self.start()
