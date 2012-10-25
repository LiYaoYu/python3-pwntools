import pwn, socket, time, sys
from threading import Thread
from Queue import Queue, Empty
from subprocess import *

class process:
    def __init__(self, cmd, *args, **kwargs):
        env = kwargs.get('env', {})
        self.debug = pwn.DEBUG
        self.proc = Popen(tuple(cmd.split()) + args,
                          stdin=PIPE, stdout=PIPE, stderr=PIPE,
                          env = env,
                          bufsize = 0)

    def close(self):
        if self.proc:
            self.proc.close()
            self.proc = None

    def send(self, dat):
        self.proc.stdin.write(dat)
        self.proc.stdin.flush()

    def recv(self, numb = 1024):
        res = self.proc.stdout.read(numb)
        if self.debug:
            sys.stdout.write(res)
            sys.stdout.flush()
        return res

    def recvall(self):
        res = []
        while True:
            s = self.recv()
            if not s: break
            res.append(s)
        return ''.join(res)

    def recvn(self, numb):
        res = []
        n = 0
        while n < numb:
            c = self.recv(1)
            if not c:
                break
            res.append(c)
            n += 1
        return ''.join(res)

    def recvuntil(self, delim):
        d = list(delim)
        res = []
        while d:
            c = self.recv(1)
            if not c:
                break
            res.append(c)
            if c == d[0]:
                d.pop(0)
            else:
                d = list(delim)
        return ''.join(res)

    def recvline(self, lines = 1):
        res = []
        for _ in range(lines):
            res.append(self.recvuntil('\n'))
        return ''.join(res)

    def interactive(self, prompt = '> '):
        pwn.trace(' [+] Switching to interactive mode\n')
        debug = self.debug
        self.debug = True
        def loop():
            while True:
                self.recv(1)
        t = Thread(target = loop)
        t.daemon = True
        t.start()
        while True:
            try:
                time.sleep(0.1)
                self.send(raw_input(prompt) + '\n')
            except KeyboardInterrupt:
                self.debug = debug
                break