import websocket
import time
import streamlit as st
import threading
import websockets
import json
from streamlit.report_thread import add_report_ctx
import asyncio


def on_message(wsapp, message):
    print("received---------------------")
    print(message)
    print(f"on_message() || start || session state: {st.session_state}")

    message = json.loads(message)
    if message['type'] == 'send_state':
        if message['opr_status'] == True:
            st.session_state['data'] = message['data']
            st.session_state['error'] = 0
        else:
            st.session_state['error'] = 1
    elif message['type'] == 'switch':
        st.session_state['data'][message['data']['room']
                                 ][message['data']['opr']] = message['data']['val']
        if message['opr_status'] == False:
            st.session_state['error'] = 1

    print(f"on_message() || end || session state: {st.session_state}")


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    st.session_state['error'] = 1


def on_open(ws):
    print("on_open() ran")
    st.session_state['ws'] = ws
    data = {'type': 'send_state'}
    ws.send(json.dumps(data))
    wait_thread = threading.Thread(target=wait_for_reply, args=('send_state',))
    wait_thread.daemon = True
    add_report_ctx(wait_thread)
    wait_thread.start()
    # wait_for_reply('send_state')
    print("----------------------------------")


async def main():
    print("main started---------------------")
    ws = websocket.WebSocketApp("ws://localhost:8000/ws/raspi4",
                                on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    add_report_ctx(wst)
    wst.start()
    # st.session_state['initial_run'] = 1
    print("Main ended------------------------")
    # st.session_state['ws'] = ws


def text_mapper(type, value):

    if type == 'led':
        if value == 1:
            return ("On", "Turn Off")
        elif value == None:
            return ("Performing Operation", "Pelase Wait")
        else:
            return ("Off", "Turn On")


async def initial_fetch():
    if st.session_state.get("data", None) == None:
        print("initial_fetch() ran--------------------")
        await main()
        print("initial_fetch() completed---------------")


def wait_for_reply(type, room=None, opr=None):

    if type == 'send_state':
        print(f"wait for reply() for {type} started")
        for _ in range(10):
            if st.session_state.get('data', None) == None:
                time.sleep(1)
            else:
                print(f"wait_for_reply() for {type} ended without error")
                return
    elif type == 'switch':
        print(
            f"wait for reply() for {type} || room:{room} || opr:{opr} started")
        print(f"wait for reply() || session state: {st.session_state}")
        for _ in range(10):
            if st.session_state['data'][room][opr] == None:
                time.sleep(1)
            else:
                print(f"wait_for_reply() for {type} ended without error")
                return

    print(f"wait_for_reply() for {type} ended with error")
    st.session_state['error'] = 1


def rerun():
    print("rerun() started")
    print(f"rerun() || session state: {st.session_state}")
    raise st.script_runner.RerunException(
        st.script_request_queue.RerunData(None))


def led_switch():
    data = {"type": "switch", "data": {
        "room": "quuincy_room", "opr": "led", "val": st.session_state['data']['quuincy_room']['led']
    }}
    st.session_state['ws'].send(json.dumps(data))
    st.session_state['data'][data['data']['room']][data['data']['opr']] = None
    # wait_for_reply('switch', data['room'], data['opr'])
    wait_thread = threading.Thread(target=wait_for_reply, args=(
        'switch', data['data']['room'], data['data']['opr'],))
    wait_thread.daemon = True
    add_report_ctx(wait_thread)
    wait_thread.start()


st.title("Home Security System")

# top_placeholder = st.empty()

with st.spinner("Please Wait, fetching data"):
    if st.session_state.get('initial_run', None) == None:
        loop = asyncio.new_event_loop()
        task = loop.create_task(initial_fetch())
        loop.run_until_complete(task)
        st.session_state['initial_run'] = 1
    while st.session_state.get('data', None) == None and st.session_state.get('error', None) == None:
        time.sleep(1)


if st.session_state['error'] == 1:
    st.error("Home system is down, either power is out or wifi is not working, please refresh the browser")
else:

    col1, col2 = st.columns(2)

    # if st.session_state['data']['quuincy_room']['led'] == None:
    #     led_status, button_label = text_mapper(
    #     'led', st.session_state['data']['quuincy_room']['led'])

    #     col1.write(f"Led Status : {led_status}")
    #     col2.info("Performing Operation, please wait")
    # elif st.session_state['data']['quuincy_room']['led'] != None:
    #     led_status, button_label = text_mapper(
    #     'led', st.session_state['data']['quuincy_room']['led'])

    #     col1.write(f"Led Status : {led_status}")
    #     col2.button(button_label, on_click=led_switch)

    led_status, button_label = text_mapper(
        'led', st.session_state['data']['quuincy_room']['led'])

    col1.write(f"Led Status : {led_status}")
    col2.button(button_label, on_click=led_switch)

print(f"Session state : {st.session_state}")
