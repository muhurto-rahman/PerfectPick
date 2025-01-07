import time 
import streamlit as st
import pandas as pd
import numpy as np



def stream_data(words):
    for word in words.split(" "):
        yield word + " "
        time.sleep(0.12)



st.write("""PerfectPick is your go-to Valorant agent selector for clutch team compositions! When your teammates insta-lock their picks, simply enter your username and their selected agents. PerfectPick will suggest the best agents for you to play, complete with a predicted win rate based on your team’s synergy. Take the guesswork out of agent selection and secure your PerfectPick!
""")
container = st.container(border = True)
chosenteammates = container.multiselect(label = "Pick 4 Agents",
               options = ["brimstone",'phoenix','sage','sova',
                  'viper','cypher','reyna','killjoy',
                  'breach','omen','jett','raze',
                  'skye','yoru','astra','kayo',
                  'chamber','neon','fade','harbor',
                  'gekko','deadlock','iso','clove',
                  'vyse'],
                  max_selections = 4)

agent = "killjoy"
winrate = 60.293717

st.write("\n")
st.write("\n")
st.write("\n")
st.write("\n")

if len(chosenteammates) < 4:
    st.write("Please select 4 teammates")
elif len(chosenteammates) == 4:
    st.write(f"You should play {agent} with a {format(winrate,".2f")}% predicted winrate for this match")
