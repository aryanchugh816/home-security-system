from streamlit.state.session_state import SessionState
import websocket
import time
import streamlit as st
import _thread
import threading
import asyncio
import websockets
import json
from streamlit.report_thread import add_report_ctx

async def hello():
    uri = "ws://localhost:8000/ws/raspi4"
    async with websockets.connect(uri) as websocket:
        name = input("What's your name? ")

        await websocket.send(name)
        print(f">>> {name}")

        greeting = await websocket.recv()
        print(f"<<< {greeting}")

def on_message(wsapp, message):
    print("received---------------------")
    print(message)
    print(f"session state: {st.session_state}")
    message = json.loads(message)
    st.session_state['data'][message['type']] = message['op']
    if message['op_status'] == False:
        st.session_state['error'] = 1
    print(f"session state: {st.session_state}")
    print("----------------------------")

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("on_open() ran")
    ws.send("Server Started")
    print(ws.recv())
    print("----------------------------------")

def  main():
    ws = websocket.WebSocketApp("ws://localhost:8000/ws/raspi4", on_message=on_message, on_error=on_error, on_close=on_close)
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    add_report_ctx(wst)
    wst.start()
    # ws.run_forever()
    # ws = websocket.WebSocket()
    # ws.connect("ws://localhost:8000/ws/raspi4")
    # ws.send("Server Started")
    # print(ws.recv())
    st.session_state['ws'] = ws

def initial_fetch():
    if st.session_state.get("data", None) == None:
        print("this ran")
        # _thread.start_new_thread(main, ())
        main()
        # asyncio.run(hello())
        st.session_state['data'] = {
            'led' : 1
        }
        st.session_state['counter'] = 0
        st.session_state['error'] = 0
        

def increment_counter():
    print("increment_counter() ran")
    try:   
        st.session_state['ws'].send("Sending from counter press")
        st.session_state['counter'] += 1
        print("trial ran")
    except websocket._exceptions.WebSocketConnectionClosedException:
        print("error ran")
        main()

def wait_for_reply(id):
    for _ in range(5):
        if st.session_state['data'][id] == None:
            time.sleep(1)
        else:
            return
    
    st.session_state['error'] = 1

def led_switch():
    data = {"type" : "led", "op": 1}
    st.session_state['ws'].send(json.dumps(data))
    st.session_state['data']['led'] = None
    wait_for_reply('led')

initial_fetch()

st.write("this app works")
st.write(f"Counter: {st.session_state['counter']}")
st.button("Increase Counter", on_click=increment_counter)

st.button("Led Button", on_click=led_switch)

if st.session_state['error'] == 1:
    st.error("Server is not responding")
    time.sleep(3)
    st.session_state['error'] = 0