#!/usr/bin/env python3.5
from chatty import create
import config, time
import functions as fun
import signal
from bot import bot as b
from tornado.httpserver import HTTPServer
from tornado.ioloop import PeriodicCallback, IOLoop

# This is an unnecessary function that checks a file that contains the current song 
# playing on stream for changes and then sends it to the chat.
def nowplaying():
    global np, t, tprev, npprev
    np = fun.now_playing()
    t = time.time()
    if(t-tprev)>15.0:
        if np:
            if not np == npprev:
                chat.message("Now Playing: " + fun.removeNonAscii(np))
                npprev = np
        tprev = time.time()

def addmoney():
    global chat, ph
    users = chat.get_users()

    ##ADD MONEY
    ph.add_money_to_users(users)

def sendchat():
    global chats, chat
    if len(chats) == 0:
        chats = config.CHATMESSAGES[:]
    chat.message(chats.pop(0))

def sig_handler(sig, frame):
    print ('Caught signal: %s' % sig)
    IOLoop.instance().add_callback(shutdown)

def shutdown():
    MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3
    print ( 'Stopping http server ' )
    http_server.stop()

    print ( 'Will shutdown in %s seconds ...' % MAX_WAIT_SECONDS_BEFORE_SHUTDOWN )
    io_loop = IOLoop.instance()
    deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            print ( 'Shutdown' )
    stop_loop()

if __name__ == "__main__":
    tprev = time.time()
    npprev = fun.now_playing()
    chats = config.CHATMESSAGES[:]
    print(npprev)

    chat = create(config)
    ph = b(chat)

    # Tell chat to authenticate with the beam server. It'll throw
    # a chatty.errors.NotAuthenticatedError if it fails.
    chat.authenticate(config.CHANNEL)

    # Listen for incoming messages.
    chat.on("message", ph.filtermessage)

    # Send Now playing to chat when song changes
    PeriodicCallback(
        lambda: nowplaying(),
        1000
    ).start()


    # Add money to viewers after user defined seconds
    PeriodicCallback(
        lambda: addmoney(),
        ph.moneyupdate * 1000
    ).start()

    # Send predetermined chat messages
    if (config.CHATTIMER > 0) and (len(config.CHATMESSAGES) > 0):
        PeriodicCallback(
            lambda: sendchat(),
            config.CHATTIMER * 1000
        ).start()

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    global http_server
    http_server = HTTPServer()
    http_server.start(0)
# Start the tornado event loop.
    IOLoop.instance().start()
