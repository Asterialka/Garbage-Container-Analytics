import os
import streamlit as st
from datetime import datetime
import pandas as pd
import cv2
from roboflow import Roboflow
import numpy as np
from PIL import Image

rf = Roboflow(api_key="Oz8zziOQaQHBctzNZknq")  
project = rf.workspace().project("musorki")
model = project.version(4).model 

UPLOAD_FOLDER = "c:/Tula_Hack/Uploaded_Photos"
PROCESSED_FOLDER = "c:/Tula_Hack/Processed_Photos"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

csv_file_path = "c:/Tula_Hack/stats.csv"

df_columns = [
    'Trash_Bin_Id',
    'Date', 'Time', 'District', 'Container Number', 'Status',  
    'Empty Buckets', 'Flooded Buckets', 'Partially Filled Buckets', 
    'Outside Trash', 'Regular Containers', 'Plastic Containers', 'Hopper Containers','Filename'
]

if os.path.exists(csv_file_path):
    stats_df = pd.read_csv(csv_file_path)
else:
    stats_df = pd.DataFrame(columns=df_columns)

st.set_page_config(page_title="Уборка территорий", layout="centered")
st.title("📷 Загрузка фотографий уборки")

#Словари для перевода
district_codes = {
    "Центральный": "central",
    "Пролетарский": "proletarian",
    "Зареченский": "zarechensky",
    "Привокзальный": "railway",
    "Советский": "soviet"
}

status_codes = {
    "До уборки": "00",
    "После уборки": "01"
}

#Форма для загрузки данных
with st.form("upload_form"):
    st.header("Введите данные")
    
    uploaded_file = st.file_uploader("Загрузите фотографию", type=["jpg", "jpeg", "png", "gif"])
    
    status = st.selectbox("Статус фотографии", ["До уборки", "После уборки"])
    
    district = st.selectbox(
        "Район",
        ["Центральный", "Пролетарский", "Зареченский", "Привокзальный", "Советский"]
    )
    
    date = st.date_input("Дата съемки", datetime.today())
    time = st.time_input("Время съемки", datetime.now())
    
    container_number = st.text_input("Номер контейнера", "")
    
    submitted = st.form_submit_button("Загрузить")

#Обработка формы
if submitted:
    if not uploaded_file:
        st.error("Пожалуйста, загрузите фотографию.")
    elif not container_number.strip():
        st.error("Пожалуйста, укажите номер контейнера.")
    else:
        index = len(stats_df) + 1 
        file_name = f"{date.strftime('%Y%m%d')}_{container_number}_{district_codes[district]}_{status_codes[status]}_{str(index).zfill(6)}_{time.strftime('%H%M')}.jpg"
        
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success("Фотография успешно загружена!")
        st.write("📅 **Дата съемки:**", date)
        st.write("⏰ **Время съемки:**", time)
        st.write("📍 **Район:**", district)
        st.write("📦 **Номер контейнера:**", container_number)
        st.write("🖼 **Файл сохранен как:**", file_name)
        
        st.image(file_path, caption="Загруженное изображение", use_container_width=True)

        img = Image.open(file_path)
        img_array = np.array(img)

        prediction = model.predict(file_path, confidence=40, overlap=30)

        processed_file_name = f"predictions_{file_name}"
        processed_file_path = os.path.join("c:/Tula_Hack/Processed_Photos", processed_file_name)
        prediction.save(processed_file_path)

        st.image(processed_file_path, caption = "Обработанное изображение", use_container_width = True)

        #Добавление данных в датасет
        if prediction:
            boxes = prediction.json().get("predictions", [])
            
            # Инициализация счетчиков для каждого типа контейнера
            empty_buckets = 0
            flooded_buckets = 0
            partially_filled_buckets = 0
            outside_trash = 0
            regular_containers = 0
            plastic_containers = 0
            hopper_containers = 0
            
            #Подсчет количества контейнеров каждого типа
            for item in boxes:
                if item['class'] == 'empty_trasher':
                    empty_buckets += 1
                elif item['class'] == 'flooded_trasher':
                    flooded_buckets += 1
                elif item['class'] == 'partially-filled_trasher':
                    partially_filled_buckets += 1
                elif item['class'] == 'outside_trash':
                    outside_trash += 1
                elif item['class'] == 'regular_container':
                    regular_containers += 1
                elif item['class'] == 'plastic_container':
                    plastic_containers += 1
                elif item['class'] == 'hopper_container':
                    hopper_containers += 1
            
            #Формируем новую строку данных
            new_row = {
                'Trash_Bin_Id':index,
                'Date': date,
                'Time': time,
                'District': district_codes[district],
                'Container Number': container_number,
                'Status': status_codes[status],
                'Empty Buckets': empty_buckets,
                'Flooded Buckets': flooded_buckets,
                'Partially Filled Buckets': partially_filled_buckets,
                'Outside Trash': outside_trash,
                'Regular Containers': regular_containers,
                'Plastic Containers': plastic_containers,
                'Hopper Containers': hopper_containers,
                'Filename': file_name
            }

            new_row_df = pd.DataFrame([new_row])

            stats_df = pd.concat([stats_df, new_row_df], ignore_index=True)

            #Сохраняем обновленный DataFrame в CSV
            stats_df.to_csv(csv_file_path, index=False)

            st.write("Данные обновлены!")