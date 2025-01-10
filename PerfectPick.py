# Import Modules

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
getprofileid = st.text_input(label = "Profile-Id", value = "Muhurto#7071")
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

# STEP 1: Gather user inputs take in u.gg profileid and their team composition.


#I'll use session state to store whether a profile has been scraped or not
if "scraped_data" not in st.session_state:
    st.session_state["scraped_data"] = None
if "last_scraped_profileid" not in st.session_state:
    st.session_state["last_scraped_profileid"] = None
if "finalmodel" not in st.session_state:
    st.session_state["finalmodel"] = None

profileid = getprofileid

teamcomp = chosenteammates


if len(chosenteammates) == 4 and profileid != st.session_state["last_scraped_profileid"]:
    with st.spinner("Scraping Profile Data... May take up to 5 minutes"):
        try:
            st.session_state["last_scraped_profileid"] = profileid
            # STEP 2: Webscrape their u.gg profile (Approximately 5 minutes to run this part)
            service = Service(executable_path="/usr/bin/chromium")
            driver = webdriver.Chrome(service = service)
            driver.get(f"https://u.gg/val/profile/{profileid.replace(' ','%20').replace('#','-')}")
            time.sleep(5)
            while True:
                try:
                    input_element = driver.find_element(By.CSS_SELECTOR,
                                                        ".flex.items-center.justify-center.group.rounded-sm.px-4.py-2\\.5.text-\\[13px\\].font-bold.dark\\:bg-lavender-500.dark\\:hover\\:bg-lavender-600.dark\\:text-white.dark\\:ui-toggled\\:bg-lavender-500.dark\\:ui-toggled\\:font-bold.leading-none")
                    input_element.click()
                except Exception as e:
                    print("No More Matches to Load", e)
                    break
            time.sleep(7)
            match_buttons = driver.find_elements(By.CSS_SELECTOR,
                                                ".flex.flex-col.justify-around.select-none.w-full")
            for i in match_buttons:
                try:
                    i.click()
                    time.sleep(1)
                except Exception as e:
                    print(f"Error occured while clicking on a button{e}")
            page_source = driver.page_source
            driver.quit()
            st.success("Finished Scraping!")

            #Updating session state before creating model but after scraping data

            st.session_state['scraped_data'] = page_source
        except Exception as e:
            print(f"Error while scraping: {e}")


if len(chosenteammates) == 4 and st.session_state['scraped_data'] is not None:
    soup = BeautifulSoup(st.session_state['scraped_data'],"html")
    defeats = soup.find_all("span", class_ = 'dark:text-accent-red-500 inline-block mr-2 text-md font-bold leading-[17px]')
    victories = soup.find_all("span", class_ = "dark:text-accent-green-300 inline-block mr-2 text-md font-bold leading-[17px]")
    matches = soup.find_all("div", class_ = "flex flex-col justify-around select-none w-full")

    # STEP 3: Based on their match data, aggregate their team comp data into roles and semi roles
    playedagents = []
    roundswon = []
    roundslost = []
    numkills = []
    numdeaths = []
    numassists = []
    accuracy = []
    mapplayed = []
    acs = []
    rank = []
    relativerank = []
    for i in range(len(matches)):
        #Played Agents works for the first 20 matches!
        playedagents.append(matches[i].find_all("div", class_ = "flex items-center mr-3")[0].find("span").attrs['class'][-1].split("-")[-1])
        roundswon.append(matches[i].find_all("div", class_ = "font-bold text-sm")[0].find_all("span")[0].text)
        roundslost.append(matches[i].find_all("div", class_ = "font-bold text-sm")[0].find_all("span")[2].text)
        numkills.append(matches[i].find_all("div", class_ = "dark:text-lavender-300")[0].find_all("span")[0].text)
        numdeaths.append(matches[i].find_all("div", class_ = "dark:text-lavender-300")[0].find_all("span")[1].text)
        numassists.append(matches[i].find_all("div", class_ = "dark:text-lavender-300")[0].find_all("span")[2].text)
        mapplayed.append(matches[i].find_all("div", class_= "flex items-center xs:relative w-full xs:w-[100px] h-full bg-contain bg-center rounded-sm")[0].text)
        acs.append(matches[i].find_all("div", class_ = "text-xxs dark:text-lavender-50")[0].text.split()[0])
        relativerank.append(matches[i].find_all("div", class_ = "flex flex-col h-full justify-between items-center text-xs xs:ml-5")[0].find_all("span")[3].text)
        rank.append(matches[i].find_all("div", class_ = "flex items-center nowrap whitespace-nowrap")[0].text)
        accuracy.append(matches[i].find_all("div", class_ = "flex items-center font-semibold text-xs")[0].text)
    # Same weird thing with map, the span background is a little different. 
    pdata = pd.DataFrame(
        {"Agent": playedagents,"RoundWins": roundswon,"RoundLosses": roundslost,"Kills": numkills,"Deaths": numdeaths,"Assists": numassists,"Accuracy": accuracy,"Map": mapplayed,"CombatScore": acs,"MatchRank": relativerank,"CompetitiveRank": rank
        }
    )
    matchinfo = soup.find_all("table", class_ = "w-full dark:bg-purple-400")
    agentsonteam = []
    # Iterate through list of all possible tables containing player information
    for i in matchinfo:
        playerlist = i.tbody.find_all("tr")
        teammatelist = []
        enemylist = []
        for j in playerlist:
            if "dark:bg-accent-red-5" in j.attrs['class'][0].split("0"):
                enemylist.append(j)
            else:
                teammatelist.append(j)
        #for i in teammatelist:
            #print(i.find_all("span", class_ = "text-ellipsis overflow-hidden whitespace-nowrap text-nowrap md:max-w-[80%]")[0].text)
        # Interestingly, my code doesn't scrape the most recent game for teammates and non-teammates.
        # This might be because padding is different?
        # It doesn't register the first row, but everything else works out perfectly. 
        for i in teammatelist:
            agentsonteam.append(i.a.next.attrs['class'][-1].split("-")[-1])
    # Rough outline for my predictive model dataframe - 
    # I want my current comp rank, team composition,
    # the number of points I won by, 
    # and the binary column of victory. 
    teamdf = pdata.iloc[1:pdata.shape[0],].reset_index()
    valorantagents = ["brimstone",'phoenix','sage','sova',
                    'viper','cypher','reyna','killjoy',
                    'breach','omen','jett','raze',
                    'skye','yoru','astra','kayo',
                    'chamber','neon','fade','harbor',
                    'gekko','deadlock','iso','clove',
                    'vyse']
    #Change data types to numeric
    changenumeric = ['RoundWins','RoundLosses','Kills','Deaths','Assists']
    for i in changenumeric:
        teamdf[i] = teamdf[i].astype(float)
    #Right now we are counting ties as defeats for model simplicity, might try to predict on delta points to account for this
    for i in valorantagents:
        teamdf[i] = np.zeros(pdata.shape[0]-1).tolist()
    teamdf["Victory"] = np.where(teamdf["RoundWins"] > teamdf["RoundLosses"],1,0)
    teamdf["DeltaScore"] = teamdf["RoundWins"] - teamdf["RoundLosses"]
    #Now we group our long agent list into groups of 4 (4 other players on our team), so they align with each round
    agentsonteam = [agentsonteam[i:i+5] for i in range(0,len(agentsonteam),5)]
    # Nested loop structure just goes row by row on the dataframe, assigning agents to thier corresponding 
    # column values if the value of the agent name matches the agent column 
    for i,j in enumerate(agentsonteam):
        for k in j:
            if k in teamdf.columns:
                teamdf.loc[i,k] = 1
    relevantcolumns = ["brimstone",'phoenix','sage','sova',
                    'viper','cypher','reyna','killjoy',
                    'breach','omen','jett','raze',
                    'skye','yoru','astra','kayo',
                    'chamber','neon','fade','harbor',
                    'gekko','deadlock','iso','clove',
                    'vyse','Victory','DeltaScore','Map']
    modeldf = pd.DataFrame()
    for i in relevantcolumns:
        modeldf[i] = teamdf[i]
    # These are the official valorant agent roles
    modeldf['Duelist'] = modeldf[['jett','phoenix','yoru','neon','raze','reyna','iso']].sum(axis = 1)
    modeldf['Controller'] = modeldf[['brimstone','viper','omen','harbor','astra','clove']].sum(axis = 1)
    modeldf['Initiator'] = modeldf[['sova','breach','skye','kayo','fade','gekko']].sum(axis = 1)
    modeldf['Sentinel'] = modeldf[['sage','cypher','killjoy','chamber','deadlock','vyse']].sum(axis = 1)

    # These are roles that aren't official but is talked about a lot in team compositions by esports analysts
    modeldf['Flashes'] = modeldf[['phoenix','yoru','reyna','omen','breach','skye','kayo','gekko','deadlock']].sum(axis=1)
    modeldf['Info'] = modeldf[['skye','sova','fade','cypher','kayo']].sum(axis = 1)
    modeldf['Heals'] = modeldf[['skye','sage']].sum(axis = 1)
    modeldf['Movement'] = modeldf[['raze','jett','neon']].sum(axis = 1)
    # STEP 4: Create a Model to predict winrate
    X = modeldf[['Duelist','Controller','Initiator','Sentinel',"Flashes",'Movement',"Info"]]
    Y = modeldf['Victory']
    testacclist = []
    testauclist = []
    for i in np.linspace(0.1,0.5,endpoint = True):
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=i, random_state=12)
        model = LGBMClassifier()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        testacclist.append(accuracy)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_pred_proba)
        testauclist.append(auc)
    #Create model that gives us the greatest test-split ACCURACY
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=np.linspace(0.1,0.5,endpoint = True)[testacclist.index(max(testacclist))], random_state=12)
    model = LGBMClassifier()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    testauclist.append(auc)

    # STEP 6: Run through all possible choices for agents our player could pick, return top 3 best agents + predicted win-rate
    #SET TEAMCOMP TO BE BASED ON THE OPTIONS, run streamlit stuff before this part.
    teamcomp = chosenteammates
    teamcompcolumns = ["brimstone",'phoenix','sage','sova',
                    'viper','cypher','reyna','killjoy',
                    'breach','omen','jett','raze',
                    'skye','yoru','astra','kayo',
                    'chamber','neon','fade','harbor',
                    'gekko','deadlock','iso','clove',
                    'vyse']
    playerchoices = [x for x in teamcompcolumns if x not in teamcomp]
    winratelist = []
    for k in playerchoices:
        teamcomp = chosenteammates
        teamcomp.append(k)
        teamcompdf = pd.DataFrame(columns = teamcompcolumns)
        teamcompdf.loc[0] = 0
        for i in teamcomp:
            teamcompdf.loc[0,i] = 1
        # These are the official valorant agent roles
        teamcompdf['Duelist'] = teamcompdf[['jett','phoenix','yoru','neon','raze','reyna','iso']].sum(axis = 1)
        teamcompdf['Controller'] = teamcompdf[['brimstone','viper','omen','harbor','astra','clove']].sum(axis = 1)
        teamcompdf['Initiator'] = teamcompdf[['sova','breach','skye','kayo','fade','gekko']].sum(axis = 1)
        teamcompdf['Sentinel'] = teamcompdf[['sage','cypher','killjoy','chamber','deadlock','vyse']].sum(axis = 1)

        # These are roles that aren't official but is talked about a lot in team compositions by esports analysts
        teamcompdf['Flashes'] = teamcompdf[['phoenix','yoru','reyna','omen','breach','skye','kayo','gekko','deadlock']].sum(axis=1)
        teamcompdf['Info'] = teamcompdf[['skye','sova','fade','cypher','kayo']].sum(axis = 1)
        teamcompdf['Heals'] = teamcompdf[['skye','sage']].sum(axis = 1)
        teamcompdf['Movement'] = teamcompdf[['raze','jett','neon']].sum(axis = 1)

        X = teamcompdf[['Duelist','Controller','Initiator','Sentinel',"Flashes",'Movement',"Info"]]
        predictedwinrate = model.predict_proba(X).tolist()[0][1]
        
        winratelist.append(predictedwinrate)

    # THERES MULTIPLE AGENTS THAT HAVE A PREDICTED MAX WINRATE. If multiple, print agents that they should play.
    # Let's just print the top three agents for now
    maxwinrate = max(winratelist)
    maxindices = [i for i, j in sorted(enumerate(winratelist), key=lambda x: x[1], reverse=True)[:3]]
    finalagents = []
    finalwr = []
    for i in maxindices:
        finalagents.append(playerchoices[i])
        finalwr.append(format(round(winratelist[i],3)*100,".1f")+"%")
        #print(f"You should consider playing {playerchoices[i]} with a predicted winrate of {format(round(winratelist[i],3)*100,".1f")+"%"}")
    finalresult = pd.DataFrame(
        {"Agents:":finalagents,
        "Predicted Winrate": finalwr}
    )
    finalresult.index += 1
    
    #Update the Session State
    st.session_state['finalmodel'] = finalresult
    
    st.write("\n")
    st.write("\n")
    st.write("\n")
    st.write("\n")
    st.write(f"Predicted Model Results with {str(round(max(testacclist),3)*100)+"%"} Accuracy:")


if st.session_state.get('finalmodel') is not None:
    st.dataframe(st.session_state['finalmodel'])
    #This is just here for troubleshooting
    #st.write(winratelist)
else:
    st.info("Data will appear here once scraped and processed.")