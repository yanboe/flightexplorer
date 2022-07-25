# Setup
To make this project run locally, you need quite a lot of prepwork. Decide for yourself if that's worth your time. If not, it's deployed here: https://flighttracker-yb.herokuapp.com/ 

- First, you need to set up a PostgreSQL server.
- Then you need to create the tables (see models.py).
- Then you need to load the tables (see loaders/). The raw data (18 GB) is not included in this repo. If needed, a pgdump can be provided (around 2 GB). You also need some indexes on the flights table, otherwise your queries need half a minute to execute.
- Then you have to provide a .env file with your DATABASE_URL and your MAPBOX_KEY
- You of course have to install all requirements (requirements.txt)
- Once that's all done, you can run app.py (I probably forgot some steps in the list above though)


# Structure of this project
- assets/: CSS + Fonts
- config/: Figure config, used in dist.py and viz_bar.py
- figures/: Functions creating the figures, called either in pages/flights.py or in pages/airports.py
- layout/: appshell.py is for the general app layout (Header, Navbar, Forms). utils.py contains some helper functions
- lib/: Functions reading data from the database to display on the website
- loaders/: Used once to load the raw data into the database. See loaders/README.md for more information.
- pages/: Dash 2.5 multi page app - main functionality is in flights.py and airports.py.
- utils/: Some more utilities reading data from the database (airline_utils.py and airport_utils.py)


# Other
- The app is not finished yet. 
- There's old data in the database of the deployed app (link above) - e.g. flights for the EuroAirport Basel Mulhouse Freiburg are missing. This will be updated in the next few days.
- If you spot a bug or have a suggestion, please let me know!