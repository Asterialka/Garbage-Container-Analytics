import sqlite3
import pandas as pd

#Загрузка данных из CSV
file_path = "stats.csv"
data = pd.read_csv(file_path)

#Подключение к базе SQLite
conn = sqlite3.connect("trash_bins.db")
cursor = conn.cursor()

#Сохранение данных в таблице
data.to_sql("trash_data", conn, if_exists="replace", index=False)
conn.commit()
conn.close()
