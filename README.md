# Guvi-project-1
YouTube-Data-Harvesting-and-Warehousing
PROJECT TITLE :
YouTube Data Harvesting and Warehousing using SQL, MongoDB and Streamlit
DOMAIN :
SOCIAL MEDIA
PROBLEM STATEMENT:
The problem statement is to create a Streamlit application that allows users to access and analyze data from multiple YouTube channels
APPROACH:
1. Setting up a Streamlit app:
Streamlit is a great choice for building data visualization and analysis tools quickly and easily.
We can use Streamlit to create a simple UI where users can enter a YouTube channel ID, view the channel details, and select channels to migrate to the data warehouse.
2. Connecting to the YouTube API:
We will need to use the YouTube API to retrieve channel and video data.
we can use the Google API client library for Python to make requests to the API.
3. Storing data in a MongoDB data lake:
After retrieving the data from the YouTube API, we should store it in a MongoDB data lake.
MongoDB is a great choice for a data lake because it can handle unstructured and semi-structured data easily.
4. Migrating data to a SQL data warehouse:
After collecting data of multiple channels, we should migrate it to a SQL data warehouse.
We can use a SQL database such as MySQL or PostgreSQL for this.Here we have used MySQL
5. Query the SQL data warehouse:
We can use SQL queries to join the tables in the SQL data warehouse and retrieve data for specific channels based on user input.
We can use a Python SQL library such as SQLAlchemy to interact with the SQL database.
6. Displaying data in the Streamlit app:
Finally,we display the retrieved data in the Streamlit app.
We can use Streamlit's data visualization features to create charts and graphs to help users analyze the data.
DEVELOPER GUIDE:
TOOLS:

YouTube API Key
Python 3.11.0 or higher.
PyCharm
MySQL
MongoDB
Streamlit
SKILLS:

Python scripting
API integration
Data Collection
Data Management using MongoDB and SQL
USER GUIDE:
STEP 1: CHANNEL ID
Obtain the channel id from the channel for which the data to retrieved.
STEP 2: EXTRACT
EXTRACT TAB

Enter the channel id in the Enter the Channel id input box in COLLECT TAB
After entering the channel id, click on the Retrieve and Store data button to retrieve and store data to MongoDB.

EXTRACT TAB

The retrieved channel name appears in the dropdown in the extract tab.
Select the channel
Click on the TRANSFORM to MySQL button.
Data will be migrated from MongoDB to MySQL.

STEP 3 : VIEW
Click on the DROPDOWN to check the updation of the channel
On clicking the SELECTED OPTION, it will display the channels stored

TEP 4 : QUESTIONS
Queries were displayed in the dropdown
Select the queries in the dropdown
Results were displayed based on the analysis done.

RESULT:
Developing a user-friendly Streamlit application that enables users to search for channel details and join tables to view data in the Streamlit app.



