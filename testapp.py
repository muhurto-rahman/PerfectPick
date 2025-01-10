import time 
import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, roc_auc_score
from lightgbm import LGBMClassifier, LGBMRegressor

st.write("""PerfectPick is your go-to Valorant agent selector for clutch team compositions! When your teammates insta-lock their picks, simply enter your username and their selected agents. PerfectPick will suggest the best agents for you to play, complete with a predicted win rate based on your team’s synergy. Take the guesswork out of agent selection and secure your PerfectPick!
""")

st.write("\n")

st.write("Input your username below:")
getprofileid = st.text_input(label = "Profile-Id")
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

st.write("Your username is:", getprofileid)
st.write("Your chosen team comp is:", list(chosenteammates))


if getprofileid == "Muhurto#7071":
    st.dataframe(data = pd.DataFrame({"true":["2"]}))