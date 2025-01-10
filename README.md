# PerfectPick

Try it out here: (https://perfectpick-val.streamlit.app/)

PerfectPick is your go-to Valorant agent selector for clutch team compositions! When your teammates insta-lock their picks, simply enter your username and their selected agents. PerfectPick will suggest the best agents for you to play, complete with a predicted win rate based on your team’s synergy. Take the guesswork out of agent selection and secure your PerfectPick!

## Features
- **Perfect Team Composition**: Enter your username and your teammates' selected agents to get the best agent suggestion for yourself.
- **Win Rate Prediction**: Based on your team’s composition, PerfectPick calculates a predicted win rate using a boosted random forest model, LightGBM.
- **Team Synergy**: The agent suggestions consider the synergy between your chosen agents and your teammates' selections, providing optimal team balance for success.

## How It Works
PerfectPick uses a combination of:
1. **Selenium Web Scraper**: A web scraper powered by Selenium fetches real-time data from [u.gg](https://u.gg), which provides agent win rates and stats for Valorant. This allows PerfectPick to offer accurate and up-to-date suggestions (though requires around 5 minutes to fully load all match data, which I recomend having pre-loaded before you get into queue).
2. **LightGBM Model**: The app employs a boosted random forest model (LightGBM) to predict the win rate based on the selected team composition. The model factors in agent roles (Controller, Duelist, Intiator, and Sentinels) as well as "semi-roles" that are often deemed important to have on a team such as flashes, info, movement, and heals, optimizing for greatest accuracy at predicted winrate over all train-test-splits.


