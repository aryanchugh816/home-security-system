import websocket
import time
import streamlit as st
import _thread

import asyncio
import websockets

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
    # ws = websocket.WebSocketApp("ws://localhost:8000/ws/raspi4", on_message=on_message, on_error=on_error, on_close=on_close)
    # ws.run_forever()
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:8000/ws/raspi4")
    ws.send("Server Started")
    print(ws.recv())
    st.session_state['ws'] = ws

def initial_fetch():
    if st.session_state.get("data", None) == None:
        print("this ran")
        # _thread.start_new_thread(main, ())
        # main()
        asyncio.run(hello())
        st.session_state['data'] = 1
        st.session_state['counter'] = 0

def increment_counter():
    print("increment_counter() ran")
    # print(f"timeout: {st.session_state['ws'].timeout}")
    try:   
        st.session_state['ws'].send("Sending from counter press")
        st.session_state['counter'] += 1
        print("trial ran")
    except ConnectionAbortedError:
        print("error ran")
        main()

initial_fetch()

st.write("this app works")
st.write(f"Counter: {st.session_state['counter']}")
st.button("Increase Counter", on_click=increment_counter)