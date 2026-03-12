# import pandas as pd
# from telethon import TelegramClient
# from telethon.tl.types import MessageMediaWebPage, MessageMediaDocument
# import re
# import sqlite3
# import sqlalchemy
# import psycopg2
# from emoji import deEmojify
# import demoji



# # Replace 'api_id', 'api_hash', and 'session_name' with your values
# api_id = 
# api_hash = 
# session_name =
# limit = None

# excel_filepath = r'G:\Django_Project\MassajidMaghribiya\telegram-downloader-main\all_kotob_Download.xlsx'

# list_pdf= []
# list_pdf2= []

# # Postgres Connection
# con_postgres=psycopg2.connect("dbname='Telegram_Kotob' user='postgres' password='7321' host='localhost' port='5432' ")
# cursor_postgres=con_postgres.cursor()

# client = TelegramClient(session_name, api_id, api_hash)

# def get_last_message_from_db(maktaba_id):
#     # cursor = con_postgres.cursor()
#     print("Connected to PostGres")
#     sql_postgres = f'''SELECT DISTINCT max(kitab_id) FROM all_telegram_kotob_fr WHERE Maktaba={maktaba_id}'''
    
#     try:
#         with  psycopg2.connect("dbname='Telegram_Kotob' user='postgres' password='7321' host='localhost' port='5432' ") as conn_postgres:
#             with  conn_postgres.cursor() as cur:
#                 cur.execute(sql_postgres)
#                 conn_postgres.commit()
#                 # Fetch the results
#                 results = cur.fetchone()
#                 for row in results:
#                     ra = row
#                     # print(row)
#                     # print(row['column_name'])
#         cur.close()
#         conn_postgres.close()
#         print(ra)
#         return ra

#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
    
    
# async def get_last_message_from_chat(channel):
#     await client.start()
#     # chat = channel  # Specify the chat or group name
    
#     # total_size = 0  # Initialize total size counter

#     async for message in client.iter_messages(channel):

#         # async for message in client.iter_messages(chat , offset_date = datetime.now(tz=timezone.utc) - timedelta(hours=125),reverse=True):
#         # print(message.sender_id, ':', message.text)

#         last_message_from_chat = message.id
#         return last_message_from_chat

# async def main(channel, maktaba):
#     await client.start()
#     chat = channel  # Specify the chat or group name
#     total_size = 0  # Initialize total size counter

#     async for message in client.iter_messages(chat):
#         if message.media and hasattr(message.media, 'size'):
#             media_size = message.media.size if message.media.size else 0
#             total_size += media_size
#         else:
#             print("No media size available for this message type.")

#     # Convert size to MB
#     total_size_mb = total_size / (1024 * 1024)
#     print(f'Total media size: {total_size_mb:.2f} MB')

# async def get_messages(channel, maktaba,linke,limitat):
    
#     i=1
#     j= 1
    
#     async for message in client.iter_messages(channel, limit=limitat):

#         # print(message.id)
#         # exit()

#         if (hasattr(message, 'media') and hasattr(message.media, 'document')):
#             mime_type = message.media.document.mime_type
#             if mime_type != 'image/webp':
                
#                 #if mime_type in ['application/pdf', 'application/msword', 'application/epub+zip','video/mp4']:
#                 #print(f"Document Autre type detected: {mime_type}")
#                 if message.reply_to_msg_id is None:
#                     link = str(message.id)
#                 else:
#                     link = str(message.reply_to_msg_id)+'/'+str(message.id)
                    
#                 #print(message.id,message.message,message.date)

#                 message1 = demoji.replace(message.message, "")

#                 list_pdf.append((maktaba, message.id, message.file.name, message1.replace("\n", " ** "), str(message.date), message.file.size,link))
#                 #list_pdf.append((maktaba, message.id, message.file.name, message.message.replace("\n", "--"), str(message.date), message.file.size,link))
#                 print(f'-{i}', end='')
#                 i+=1
#                 #break
            
#     kotob_modmaja = pd.DataFrame(list_pdf, columns=["Maktaba", "Kitab_Id", "Kitab_Title", "Kitab_Message","Kitab_Date","Kitab_Size", "Kitab_Link"])
#     # #kotob_modmaja['Kitab_Title'] = kotob_modmaja['Kitab_Title'].str.replace('.pdf', '')
#     # #kotob_maktaba=['channel'] = channel
#     kotob_modmaja['Kitab_Group'] = ''
#     kotob_modmaja = kotob_modmaja.sort_values(by=['Kitab_Id'], ascending=True)
#     # #kotob_modmaja.to_excel('all_kotob_Download.xlsx', index=False) 
    
#     # #kotob_modmaja2 = pd.DataFrame(list_pdf2, columns=["Maktaba", "Kitab_Id", "Kitab_Title", "Kitab_Size", "Kitab_Link","Link"])
#     # #kotob_modmaja2['Kitab_Group'] = ''
#     # #kotob_modmaja2.to_excel('all_kotob_Download2.xlsx', index=False)

#     #print(kotob_modmaja)
    
#     #return
    
#     print('\n')
#     print("----------------------------------------------------------------")
#     print("Fin Recherche dans maktaba ", maktaba, " - Channel : ", channel, ' - Link : ', linke)

#     # #-------------------------------------------------------------------------
#     print("----------------------------------------------------------------")
#     print("Debut Save Maktaba dans DataBase !!! : ", maktaba, " - Channel : ", channel, ' - Link : ', linke)


#     # PREPARED STATEMENT
#     sql = '''Insert into massajid_app_all_telegram_kotob_fr (Maktaba, Kitab_Id,Kitab_Title,Kitab_Message,Kitab_Date,Kitab_Size,Kitab_Link,Kitab_Group) 
#                              values (?,?,?,?,?,?,?,?)'''
#     #sql_postgres = '''insert into all_telegram_kotob 
#     sql_postgres = '''insert into all_telegram_kotob_fr 
#                              (Maktaba, Kitab_Id,Kitab_Title,Kitab_Message,Kitab_Date,Kitab_Size,Kitab_Link,Kitab_Group)
#                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (Maktaba,Kitab_Id) DO NOTHING'''
    
#     try:
#         with  psycopg2.connect("dbname='Telegram_Kotob' user='postgres' password='7321' host='localhost' port='5432' ") as conn:
#             with  conn.cursor() as cur:
#                 # execute the INSERT statement
#                 cur.executemany(sql_postgres, kotob_modmaja.to_numpy().tolist())
#             # commit the changes to the database
#             conn.commit()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)

#     finally:
#         # Closing database connection.
#         if conn:
#             conn.close()
#             print("The SQLite connection is closed")
#         # Postgres connection  
#         if con_postgres:
#             con_postgres.close()
#             print("The PostGres connection is closed")
                  

#     print("----------------------------------------------------------------")
#     print("Fin Save Maktaba_FR dans DataBase !!! : ", maktaba, " - Channel : ", channel, ' - Link : ', linke)

#     print("----------------------------------------------------------------")
# #    print('Fin du travail :-------!!!!!!!!!!!!!!')




# # cnx = sqlite3.connect(database)
# # cursor = cnx.cursor()
# #print("Connected to SQLite")

# # Reverse Order Avec Limit
# #sql_sqlite = "SELECT maktaba_id, maktaba_link, maktaba_at FROM massajid_app_all_telegram_maktaba_fr ORDER BY maktaba_id desc LIMIT 1"

# # Normal Order Avec Limit
# #sql_sqlite = "SELECT maktaba_id, maktaba_link, maktaba_at from massajid_app_all_telegram_maktaba_fr limit 1"

# # Normal Order Sans Lmit
# PostGres_sql = "SELECT maktaba_id, maktaba_link, maktaba_at from all_telegram_maktaba_fr"

# cursor_postgres.execute(PostGres_sql)

# for row in cursor_postgres.fetchall():
#     maktaba = row[0] #row['maktaba_id']
#     linke = row[1] #row['maktaba_link']

#     try:
#         channel = int(row[2])  # Attempt to convert to integer
#     except ValueError:
#           # Keep original if not a number
#         channel = row[2] #row['maktaba_at']

#     print("----------------------------------------------------------------")
#     print('Debut Recherche dans maktaba_FR : ', maktaba, ' - Channel : ', channel, ' - Link : ', linke)

#     with client:
#         #print("----------------------------------------------------------------")
#         #print("Debut du maktaba : ", maktaba, " - Channel : ", channel)
#         #client.loop.run_until_complete(main(channel, maktaba))
#         last_message_from_chat = client.loop.run_until_complete(get_last_message_from_chat(channel))
#         last_message_db = get_last_message_from_db(maktaba)
#         print(last_message_db, '\n')
#         print(last_message_from_chat, '\n')
#         if last_message_db is None:
#             limita = None
#         else:
#             limita = last_message_from_chat - last_message_db
        
#         print('Limite : ', limita)
#         client.loop.run_until_complete(get_messages(channel, maktaba,linke, limita))
#         #exit()
        



# print('Fin du travail :-------!!!!!!!!!!!!!!')





import os
from telethon import TelegramClient
from helpers.config import get_settings, Settings

api_id = Settings.api_id
api_hash = Settings.api_hash
session_name = Settings.session_name

channel = "https://t.me/Joutiya_Library"

folder = "/media/barribar/NewDisc/PDF/python/python_django"

client = TelegramClient(session_name, api_id, api_hash)

async def main():

    await client.start()

    for filename in os.listdir(folder):

        path = os.path.join(folder, filename)

        if os.path.isfile(path):

            # titre = nom du fichier sans extension
            title = os.path.splitext(filename)[0]

            await client.send_file(
                channel,
                path,
                caption=title
            )

            print("Uploaded:", filename)

with client:
    client.loop.run_until_complete(main())