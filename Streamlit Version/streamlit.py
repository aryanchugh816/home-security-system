import streamlit as st

lock_state = {
    "Quuincy Room": {
        "Medicine Cabinet" : [0, "Lock"]
    }
}

def lock(room, lock):
    if lock_state[room][lock][0] == 0:
        lock_state[room][lock] = [1, "Unlock"]
    else:
        lock_state[room][lock] = [0, "Lock"]

st.title('Home Security System')

if st.button(label=lock_state["Quuincy Room"]["Medicine Cabinet"][1]):
    lock("Quuincy Room", "Medicine Cabinet")
    print("Lock state-----------------------")
    print(lock_state)
    print("-------------------------------------")