import googleapiclient.discovery#from googleapiclient.discovery import build
import pymongo
import mysql.connector as sql
import pandas as pd
from streamlit_option_menu import option_menu
import streamlit as st
import plotly.express as px
import re

# CREATING OPTION MENU
with st.sidebar:
    selected = option_menu(None, ["Home","Extract & Transform","View"],
                           icons=["house-door-fill","tools","card-text"],
                           default_index=0,
                           orientation="vertical",
                           styles={"nav-link": {"font-size": "30px", "text-align": "centre", "margin": "0px",
                                                "--hover-color": "#C80101"},
                                   "icon": {"font-size": "30px"},
                                   "container" : {"max-width": "6000px"},
                                   "nav-link-selected": {"background-color": "#C80101"}})



# Bridging a connection with MongoDB Atlas and Creating a new database(youtube_data)
client=pymongo.MongoClient("mongodb+srv://geetha:geethamani@cluster0.n4xscqo.mongodb.net/?retryWrites=true&w=majority")
db=client["youtube_data"]

# CONNECTING WITH MYSQL DATABASE
mydb = sql.connect(host="127.0.0.1",user="root",password="Pass*8881990",database="youtube_data",port = "3306")
mycursor = mydb.cursor(buffered=True)

# BUILDING CONNECTION WITH YOUTUBE API
def Api_connect():
    api_key="AIzaSyBQYkydDxN_PrbQbbO_RlJJ88HFm2YYeJQ"#we created in google developer console
    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(api_service_name,
        api_version,developerKey=api_key)
    return youtube
youtube=Api_connect()

# FUNCTION TO GET CHANNEL DETAILS
def get_channel_details(channel_id):
        ch_data = []
        response = youtube.channels().list(part='snippet,contentDetails,statistics',
                                           id=channel_id).execute()

        for i in range(len(response['items'])):
            data = dict(Channel_id=channel_id[i],
                        Channel_name=response['items'][i]['snippet']['title'],
                        Playlist_id=response['items'][i]['contentDetails']['relatedPlaylists']['uploads'],
                        Subscribers=response['items'][i]['statistics']['subscriberCount'],
                        Views=response['items'][i]['statistics']['viewCount'],
                        Total_videos=response['items'][i]['statistics']['videoCount'],
                        Description=response['items'][i]['snippet']['description'],
                        Country=response['items'][i]['snippet'].get('country')
                        )
            ch_data.append(data)
        return ch_data



# FUNCTION TO GET VIDEO IDS
def get_channel_videos(channel_id):
    video_ids = []
    # get Uploads playlist id
    res = youtube.channels().list(id=channel_id,
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None

    while True:
        res = youtube.playlistItems().list(playlistId=playlist_id,
                                           part='snippet',
                                           maxResults=50,
                                           pageToken=next_page_token).execute()

        for i in range(len(res['items'])):
            video_ids.append(res['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')

        if next_page_token is None:
            break
    return video_ids

    #[i] index


# FUNCTION TO GET VIDEO DETAILS
def get_video_details(v_ids):
    video_stats = []

    for i in range(0, len(v_ids), 50):
        response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(v_ids[i:i + 50])).execute()
        for video in response['items']:
            video_details = dict(Channel_name=video['snippet']['channelTitle'],
                                 Channel_id=video['snippet']['channelId'],
                                 Video_id=video['id'],
                                 Title=video['snippet']['title'],
                                 Tags=video['snippet'].get('tags'),
                                 Thumbnail=video['snippet']['thumbnails']['default']['url'],
                                 Description=video['snippet']['description'],
                                 Published_date=video['snippet']['publishedAt'],
                                 Duration=video['contentDetails']['duration'],
                                 Views=video['statistics']['viewCount'],
                                 Likes=video['statistics'].get('likeCount'),
                                 Comments=video['statistics'].get('commentCount'),
                                 Favorite_count=video['statistics']['favoriteCount'],
                                 Definition=video['contentDetails']['definition'],
                                 Caption_status=video['contentDetails']['caption']
                                 )
            video_stats.append(video_details)
    return video_stats

# get comment information
# if some comment section is locked v want to use try,except
# FUNCTION TO GET COMMENT DETAILS
def get_comments_details(v_id):
    comment_data = []
    try:
        next_page_token = None
        while True:
            response = youtube.commentThreads().list(part="snippet,replies",
                                                    videoId=v_id,
                                                    maxResults=100,
                                                    pageToken=next_page_token).execute()
            for cmt in response['items']:
                data = dict(Comment_id = cmt['id'],
                            Video_id = cmt['snippet']['videoId'],
                            Comment_text = cmt['snippet']['topLevelComment']['snippet']['textDisplay'],
                            Comment_author = cmt['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            Comment_posted_date = cmt['snippet']['topLevelComment']['snippet']['publishedAt'],
                            Like_count = cmt['snippet']['topLevelComment']['snippet']['likeCount'],
                            Reply_count = cmt['snippet']['totalReplyCount']
                           )
                comment_data.append(data)
            next_page_token = response.get('nextPageToken')
            if next_page_token is None:
                break
    except:
        pass
    return comment_data

# FUNCTION TO GET CHANNEL NAMES FROM MONGODB
def channel_names():
        ch_name = []
        for i in db.channel_details.find():
            ch_name.append(i['Channel_name'])
        return ch_name


# HOME PAGE
if selected == "Home":
    col1,col2 = st.columns(2,gap= 'medium')
    col1.markdown("## :blue[Domain] : Social Media")
    col1.markdown("## :blue[Technologies used] : Python,MongoDB, Youtube Data API, MySql, Streamlit")
    col1.markdown("## :blue[Overview] : Retrieving the Youtube channels data from the Google API, storing it in a MongoDB as data lake, migrating and transforming data into a SQL database,then querying the data and displaying it in the Streamlit app.")
    col2.markdown("#   ")
    col2.markdown("#   ")
    col2.markdown("#   ")

# EXTRACT AND TRANSFORM PAGE
if selected == "Extract & Transform":
    tab1, tab2 = st.tabs(["$\huge  EXTRACT $", "$\huge TRANSFORM $"])

    # EXTRACT TAB
    with tab1:
        st.markdown("#    ")
        st.write("### Enter YouTube Channel_ID below :")
        ch_id = st.text_input( "Hint : Goto channel's home page > Right click > View page source > Find channel_id").split(',')

        if ch_id and st.button("Extract Data"):
            ch_details = get_channel_details(ch_id)
            st.write(f'#### Extracted data from :green["{ch_details[0]["Channel_name"]}"] channel')
            st.table(ch_details)

        if st.button("Upload to MongoDB"):
            with st.spinner('Please Wait for it...'):
                ch_details = get_channel_details(ch_id)
                v_ids = get_channel_videos(ch_id)
                vid_details = get_video_details(v_ids)


                def comments():
                    com_d = []
                    for i in v_ids:
                        com_d += get_comments_details(i)
                    return com_d


                comm_details = comments()

                collections1 = db.channel_details
                collections1.insert_many(ch_details)

                collections2 = db.video_details
                collections2.insert_many(vid_details)

                collections3 = db.comments_details
                collections3.insert_many(comm_details)
                st.success("Upload to MongoDB successful !!")

    # TRANSFORM TAB
    with tab2:
        st.markdown("#   ")
        st.markdown("### Select a channel to begin Transformation to SQL")
        ch_name = channel_names()
        user_inp = st.selectbox("Select channel", options=ch_name)


    def create_channels_table(mycursor):
        # Assuming 'channels' is the name of your table

        create_table_query = """
        CREATE TABLE IF NOT EXISTS channels (
            Channel_id varchar(50)  primary key,
            Channel_name text,
            Playlist_id text,
            Subscribers Bigint,
            Views Bigint,
            Total_videos Bigint,
            Description text,
            Country text
        )
        """

        mycursor.execute(create_table_query)


    def insert_into_channels(user_inp, mycursor, mydb):
        collections = db.channel_details
        create_channels_table(mycursor)
        query = """INSERT INTO channels VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"""

        for i in collections.find({"Channel_name": user_inp}, {'_id': 0}):
            mycursor.execute(query, tuple(i.values()))
            mydb.commit()


    def create_videos_table(mycursor):
        mycursor.execute("drop table if exists videos;")
        create_table_query = """
           CREATE TABLE IF NOT EXISTS videos (
               Channel_name text,
               Channel_id text,
               Video_id varchar(50) primary key,
               Title text,
               Tags text,
               Thumbnail text,
               Description text,
               Published_date text,
               Duration varchar(70),
               Views Bigint,
               Likes Bigint,
               Comments Bigint,
               Favorite_count Bigint,
               Definition text,
               Caption_status text
           )
           """
        mycursor.execute(create_table_query)


    def insert_into_videos(mycursor, mydb):
        vi_list = []
        collections1 = db.video_details
        for vi_data in collections1.find():
            vi_list.append(vi_data)
        df1 = pd.DataFrame(vi_list)
        create_videos_table(mycursor)
        for index, row in df1.iterrows():

            insert_query = '''insert into videos(Channel_Name,
                                                   Channel_Id,
                                                   Video_Id,
                                                   Title,
                                                   Thumbnail,
                                                   Description,
                                                   Published_Date,
                                                   Duration,
                                                   Views,
                                                   Likes,
                                                   Comments,
                                                   Favorite_count,
                                                   Definition,
                                                   Caption_status )
                                   values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

            duration_numeric_values = re.findall(r'\d+', row["Duration"])
            # Format the duration as hh:mm:ss
            formatted_duration = ':'.join(duration_numeric_values)

        
            values = (row['Channel_name'],
                      row['Channel_id'],
                      row['Video_id'],
                      row['Title'],
                      row['Thumbnail'][0:50],
                      row['Description'],
                      row['Published_date'],
                      formatted_duration,
                      row['Views'],
                      row['Likes'],
                      row['Comments'],
                      row['Favorite_count'],
                      row['Definition'],
                      row['Caption_status'])


            # try:
            mycursor.execute(insert_query, values)
            mydb.commit()
        # except TypeError as e:
        # print("Error inserting data:", e)


    def create_comments_table(mycursor):
        mycursor.execute("drop table if exists comments")
        create_table_query = """
        CREATE TABLE IF NOT EXISTS comments (
            Comment_id varchar(50),
            Video_id text,
            Comment_text text,
            Comment_author text,
            Comment_posted_date text,
            Like_count Bigint,
            Reply_count Bigint
        )
        """
        mycursor.execute(create_table_query)


    def insert_into_comments(user_inp, mycursor, mydb):
        collections1 = db.video_details
        collections2 = db.comments_details
        create_comments_table(mycursor)
        query2 = """INSERT INTO comments VALUES(%s,%s,%s,%s,%s,%s,%s)"""

        for vid in collections1.find({"Channel_name": user_inp}, {'_id': 0}):
            for i in collections2.find({'Video_id': vid['Video_id']}, {'_id': 0}):
                mycursor.execute(query2, tuple(i.values()))
                mydb.commit()


    if st.button("Submit"):
        try:
            insert_into_channels(user_inp, mycursor, mydb)
            st.success("Data inserted into 'channels' table successfully.")


        except Exception as e:
            import traceback

            st.error(f"Error during transformation: {str(e)}")
            st.error(f"Traceback: {traceback.format_exc()}")
        try:
            insert_into_videos(mycursor, mydb)
            st.success("Data inserted into 'videos' table successfully.")

        except Exception as e:
            import traceback

            st.error(f"Error during transformation: {str(e)}")
            st.error(f"Traceback: {traceback.format_exc()}")
        try:
            insert_into_comments(user_inp, mycursor, mydb)
            st.success("Data inserted into 'comments' table successfully.")

        except Exception as e:
            import traceback

            st.error(f"Error during transformation: {str(e)}")
            st.error(f"Traceback: {traceback.format_exc()}")
# VIEW PAGE
if selected == "View":

    st.write("## :orange[Select any question to get Insights]")
    questions = st.selectbox('Questions',
                             ['1. What are the names of all the videos and their corresponding channels?',
                              '2. Which channels have the most number of videos, and how many videos do they have?',
                              '3. What are the top 10 most viewed videos and their respective channels?',
                              '4. How many comments were made on each video, and what are their corresponding video names?',
                              '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                              '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                              '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                              '8. What are the names of all the channels that have published videos in the year 2022?',
                              '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                              '10. Which videos have the highest number of comments, and what are their corresponding channel names?'])

    if questions == '1. What are the names of all the videos and their corresponding channels?':
        mycursor.execute("""SELECT title AS Video_Title, channel_name AS Channel_Name
                            FROM videos
                            ORDER BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '2. Which channels have the most number of videos, and how many videos do they have?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, total_videos AS Total_Videos
                            FROM channels
                            ORDER BY total_videos DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Number of videos in each channel :]")
        # st.bar_chart(df,x= mycursor.column_names[0],y= mycursor.column_names[1])
        fig = px.bar(df,
                     x=mycursor.column_names[0],
                     y=mycursor.column_names[1],
                     orientation='v',
                     color=mycursor.column_names[0]
                     )
        st.plotly_chart(fig, use_container_width=True)

    elif questions == '3. What are the top 10 most viewed videos and their respective channels?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, title AS Video_Title, views AS Views 
                            FROM videos
                            ORDER BY views DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Top 10 most viewed videos :]")
        fig = px.bar(df,
                     x=mycursor.column_names[2],
                     y=mycursor.column_names[1],
                     orientation='h',
                     color=mycursor.column_names[0]
                     )
        st.plotly_chart(fig, use_container_width=True)

    elif questions == '4. How many comments were made on each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT a.video_id AS Video_id, a.title AS Video_Title, b.Total_Comments
                            FROM videos AS a
                            LEFT JOIN (SELECT video_id,COUNT(comment_id) AS Total_Comments
                            FROM comments GROUP BY video_id) AS b
                            ON a.video_id = b.video_id
                            ORDER BY b.Total_Comments DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name,title AS Title,likes AS Likes_Count 
                            FROM videos
                            ORDER BY likes DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Top 10 most liked videos :]")
        fig = px.bar(df,
                     x=mycursor.column_names[2],
                     y=mycursor.column_names[1],
                     orientation='h',
                     color=mycursor.column_names[0]
                     )
        st.plotly_chart(fig, use_container_width=True)

    elif questions == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT title AS Title, likes AS Likes_Count
                            FROM videos
                            ORDER BY likes DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, views AS Views
                            FROM channels
                            ORDER BY views DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Channels vs Views :]")
        fig = px.bar(df,
                     x=mycursor.column_names[0],
                     y=mycursor.column_names[1],
                     orientation='v',
                     color=mycursor.column_names[0]
                     )
        st.plotly_chart(fig, use_container_width=True)

    elif questions == '8. What are the names of all the channels that have published videos in the year 2022?':
        mycursor.execute("""SELECT channel_name AS Channel_Name
                            FROM videos
                            WHERE published_date LIKE '2022%'
                            GROUP BY channel_name
                            ORDER BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':

         mycursor.execute("""select channel_name as channelname,AVG(Duration) as averageduration from videos group by channel_name""")
         df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
         st.write(df)
         st.write("### :green[Avg video duration for channels :]")
         fig = px.bar(df,
               x=mycursor.column_names[0],
               y=mycursor.column_names[1],
               orientation='v',
               color=mycursor.column_names[0]
               )
         st.plotly_chart(fig, use_container_width=True)


    elif questions == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name,video_id AS Video_ID,comments AS Comments
                            FROM videos
                            ORDER BY comments DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Videos with most comments :]")
        fig = px.bar(df,
                     x=mycursor.column_names[1],
                     y=mycursor.column_names[2],
                     orientation='v',
                     color=mycursor.column_names[0]
                     )
        st.plotly_chart(fig, use_container_width=True)












