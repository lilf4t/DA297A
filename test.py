import psycopg

hostname = 'pgserver.mau.se'  
database = 'health_center_group21'   #Namn på ditt databas
username = 'an4952'  #Ditt databas username, laila:an4952, fatima:an4263
pwd  = '2ecfcvkm' #Password, laila:50owi0jd, fatima:2ecfcvkm
port_id = 5432

conn = None
curr = None 
try:
    conn = psycopg.connect(
        host = hostname,
        dbname = database,
        user = username,
        password = pwd,
        port = port_id)
    
    curr = conn.cursor() #cursor för att hjälpa med SQL operationer, lagrar dessa values som man får av operationerna
    
   
except Exception as error:
    print(error)
#finally behövs för att stänga connection och cursor oavsett om det blir error eller inte.
finally: 
    if curr is not None:
        curr.close()
    if conn is not None:
        conn.close()