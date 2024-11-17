import streamlit as st
import sqlite3
import pandas as pd
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from PIL import Image

# Подключение к базе данных SQLite
def get_data_from_db(query, params=()):
    conn = sqlite3.connect("trash_bins.db")
    data = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return data
#photo_folder = os.path.join(os.getcwd(), "Uploaded_Photos")

# Функция для построения ежемесячного отчета с частотой переполнения
def generate_mouth_report():
    current_date = datetime.now()
    week_start_date = current_date - timedelta(days=30)
    
    query = """
        SELECT Date, [Outside Trash]
        FROM trash_data
        WHERE Date >= ? AND Date <= ?
        ORDER BY Date ASC
    """
    params = (week_start_date.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d"))
    weekly_data = get_data_from_db(query, params)
    
    if weekly_data.empty:
        st.warning("Нет данных за последние 30 дней.")
        return

    # Преобразование данных в формат datetime
    weekly_data["Date"] = pd.to_datetime(weekly_data["Date"])
    
    # Подготовка данных для расчета частоты переполнения
    daily_frequency = (
        weekly_data.groupby("Date")["Outside Trash"]
        .apply(lambda x: (x > 0).sum() / len(x) * 100 if len(x) > 0 else 0)
        .reset_index(name="Overflow Frequency (%)")
    )
    
    # Вывод данных
    st.write("### Ежемесячный отчет по частоте переполнения")
    st.write(daily_frequency)
    
    # Построение графика
    plt.figure(figsize=(10, 5))
    plt.plot(
        daily_frequency["Date"],
        daily_frequency["Overflow Frequency (%)"],
        marker="o",
        linestyle="-",
        color="red",
        label="Частота переполнения"
    )
    plt.title("Частота переполнения баков за последние 30 дней")
    plt.xlabel("Дата")
    plt.ylabel("Частота переполнения (%)")
    plt.grid()
    plt.legend()
    
    # Показ графика в Streamlit
    st.pyplot(plt)

# Функция для построения еженедельного отчета с частотой переполнения
def generate_weekly_report():
    current_date = datetime.now()
    week_start_date = current_date - timedelta(days=7)
    
    query = """
        SELECT Date, [Outside Trash]
        FROM trash_data
        WHERE Date >= ? AND Date <= ?
        ORDER BY Date ASC
    """
    params = (week_start_date.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d"))
    weekly_data = get_data_from_db(query, params)
    
    if weekly_data.empty:
        st.warning("Нет данных за последние 7 дней.")
        return

    # Преобразование данных в формат datetime
    weekly_data["Date"] = pd.to_datetime(weekly_data["Date"])
    
    # Подготовка данных для расчета частоты переполнения
    daily_frequency = (
        weekly_data.groupby("Date")["Outside Trash"]
        .apply(lambda x: (x > 0).sum() / len(x) * 100 if len(x) > 0 else 0)
        .reset_index(name="Overflow Frequency (%)")
    )
    
    # Вывод данных
    st.write("### Еженедельный отчет по частоте переполнения")
    st.write(daily_frequency)
    
    # Построение графика
    plt.figure(figsize=(10, 5))
    plt.plot(
        daily_frequency["Date"],
        daily_frequency["Overflow Frequency (%)"],
        marker="o",
        linestyle="-",
        color="red",
        label="Частота переполнения"
    )
    plt.title("Частота переполнения баков за последние 7 дней")
    plt.xlabel("Дата")
    plt.ylabel("Частота переполнения (%)")
    plt.grid()
    plt.legend()
    
    # Показ графика в Streamlit
    st.pyplot(plt)

def check_all_containers():
    # Запрос данных для всех контейнеров с датой последней уборки
    query = """
        SELECT [Container Number], MAX(Date) AS last_cleaning_date
        FROM trash_data
        GROUP BY [Container Number]
    """
    containers_data = get_data_from_db(query)
    
    if containers_data.empty:
        st.warning("Нет данных о контейнерах.")
        return
    
    # Текущая дата
    current_date = datetime.now()  
    st.write(f"Текущая дата: {current_date}") 
    
    # Проходим по всем контейнерам и проверяем дату последней уборки
    for _, row in containers_data.iterrows():
        container_number = row['Container Number']
        last_cleaning_date = pd.to_datetime(row['last_cleaning_date'])
        days_since_last_cleaning = (current_date - last_cleaning_date).days
        
        # Выводим для отладки
        st.write(f"Контейнер {container_number}: Последняя уборка {last_cleaning_date}, прошло дней: {days_since_last_cleaning}")
        
        # Если прошло больше 3 дней с последней уборки, показываем баннер
        if days_since_last_cleaning > 3:
            st.markdown(
                f"""
                <style>
                    .warning-banner-{container_number} {{
                        position: fixed;
                        top: 10px;
                        right: 10px;
                        background-color: red;
                        color: white;
                        padding: 10px;
                        font-size: 16px;
                        border-radius: 5px;
                        z-index: 1000;
                    }}
                </style>
                <div class="warning-banner-{container_number}">
                    Внимание! Контейнер №{container_number} не был вывезен больше 3 дней!
                </div>
                """, 
                unsafe_allow_html=True
            )

def main():
    st.title("Аналитика контейнерных площадок Тулы")

    # Загрузка уникальных номеров контейнеров из базы данных
    container_query = "SELECT DISTINCT [Container Number] FROM trash_data"
    container_numbers = get_data_from_db(container_query)["Container Number"].tolist()
    
    # Фильтры
    st.sidebar.header("Административная панель")
    st.sidebar.header("Информация по площадке")
    selected_container = st.sidebar.selectbox("Выберите номер площадки", container_numbers)
    date_from = st.sidebar.date_input("Дата начала")
    date_to = st.sidebar.date_input("Дата конца")
    
    # Добавляем кнопку для фильтрации
    if st.sidebar.button("Показать статистику для площадки"):
        date_from_str = pd.to_datetime(date_from).strftime("%Y-%m-%d")
        date_to_str = pd.to_datetime(date_to).strftime("%Y-%m-%d")
        
        # Запрос данных из базы
        query = """
            SELECT *
            FROM trash_data
            WHERE [Container Number] = ?
              AND date >= ?
              AND date <= ?
        """
        params = (selected_container, date_from_str, date_to_str)
        filtered_df = get_data_from_db(query, params)
        st.subheader(f"Статистика для площадки {selected_container}")

        query = """
            SELECT MAX(Date) as LastCleaningDate
            FROM trash_data
            WHERE [Container Number] = ?
        """
        last_cleaning_date_row = get_data_from_db(query, (selected_container,))
        last_cleaning_date = pd.to_datetime(last_cleaning_date_row["LastCleaningDate"].iloc[0])

        # # Вывод последних фотографий, если они существуют
        # date_str = last_cleaning_date.strftime("%Y%m%d")  # Преобразуем дату в строку в формате YYYYMMDD

        # # Путь к фотографиям для этой даты
        # photo_files = [f for f in os.listdir(photo_folder) 
        #            if f.startswith(date_str) and str(selected_container) in f]


        # # Проверка, что фотографии найдены, и вывод их
        # if photo_files:
        #     st.subheader(f"Фотографии для площадки {selected_container} на {last_cleaning_date.strftime('%Y-%m-%d')}")
            
        #     # Создаем колонки для размещения фотографий в одной строке
        #     cols = st.columns(2)
            
        #     # Размер изображений (800x800 пикселей)
        #     image_size = (800, 800)
            
        #     # Отображаем максимум 2 фотографии в одной строке
        #     for i, photo_file in enumerate(photo_files[:2]):
        #         photo_path = os.path.join(photo_folder, photo_file)
        #         img = Image.open(photo_path)
        #         img = img.resize(image_size)  # Изменяем размер изображения
        #         cols[i].image(img, caption=photo_file)
        # else:
        #     st.warning("Фотографии для этой даты и площадки не найдены.")



        # Получение последней даты уборки вне зависимости от выбранного периода
        last_cleaning_query = """
            SELECT MAX(Date) as LastCleaningDate
            FROM trash_data
            WHERE [Container Number] = ?
            AND Status = 1
        """
        last_cleaning_date_row = get_data_from_db(last_cleaning_query, (selected_container,))
        last_cleaning_date = (
            pd.to_datetime(last_cleaning_date_row["LastCleaningDate"].iloc[0])
            if not last_cleaning_date_row.empty and pd.notnull(last_cleaning_date_row["LastCleaningDate"].iloc[0])
            else None
        )

        if filtered_df.empty:
            st.warning("Нет данных для выбранного периода.")
        else:
            filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])
            


            bin_counts = filtered_df.loc[filtered_df["Status"] == 1, "Container Number"].value_counts()
    
            # Графики и статистика 
            if not bin_counts.empty:
                total_bin_count = bin_counts.sum() 
                st.markdown(f"### Количество вывозов мусора за выбранный интервал: **{total_bin_count}**")
            else:
                st.info("Нет данных.")
        

        # 4. Типы баков и их количество
        regular_mode = filtered_df["Regular Containers"].mode()[0]
        plastic_mode = filtered_df["Plastic Containers"].mode()[0]
        hopper_mode = filtered_df["Hopper Containers"].mode()[0]

        # Создаём словарь с типами контейнеров и их модой
        container_types = ["Regular Containers", "Plastic Containers", "Hopper Containers"]
        modes = [regular_mode, plastic_mode, hopper_mode]

        # Создаём датафрейм для передачи в st.bar_chart
        mode_df = pd.DataFrame({"Container Type": container_types, "Mode": modes})

        # Округляем моду до целых чисел
        mode_df["Mode"] = mode_df["Mode"].round().astype(int)

        # График с использованием Streamlit
        st.write("Количество контейнеров на площадке")
        st.bar_chart(mode_df.set_index("Container Type")["Mode"].transpose())


        # 1. Дней после последней уборки
        if last_cleaning_date is not None:
            days_since_last_cleaning = (pd.Timestamp.now() - last_cleaning_date).days
            st.metric("Дней после последней уборки", days_since_last_cleaning)
        else:
            st.metric("Дней после последней уборки", "Нет данных")

        # 2. Средний интервал между уборками
        if not filtered_df.empty:
            cleaning_dates = filtered_df.loc[filtered_df["Status"] == 1, "Date"].sort_values()
            if not cleaning_dates.empty:
                cleaning_dates = pd.to_datetime(cleaning_dates)
                intervals = cleaning_dates.diff().dt.days.dropna()
                average_interval = intervals.mean().round(1) if not intervals.empty else "Нет данных"
                median_interval = intervals.median().round(1) if not intervals.empty else "Нет данных"
            else:
                average_interval = median_interval = "Нет данных"
        else:
            average_interval = median_interval = "Нет данных"

        # 2.5 Средний интервал за все время
        all_time_query = """
            SELECT Date 
            FROM trash_data 
            WHERE Status = 1 AND [Container Number] = ?
        """
        all_cleaning_dates = get_data_from_db(all_time_query, (selected_container,))["Date"]

        if not all_cleaning_dates.empty:
            all_cleaning_dates = pd.to_datetime(all_cleaning_dates).sort_values()
            all_intervals = all_cleaning_dates.diff().dt.days.dropna()
            all_average_interval = all_intervals.mean().round(1) if not all_intervals.empty else "Нет данных"
            all_median_interval = all_intervals.median().round(1) if not all_intervals.empty else "Нет данных"
        else:
            all_average_interval = all_median_interval = "Нет данных"

        # Размещение метрик в одну строку
        col1, col2 = st.columns(2)

        with col1:
            if average_interval != "Нет данных":
                st.metric("Средний интервал уборок (выбранный интервал)", f"{average_interval} дней")
                if median_interval != "Нет данных":
                    st.metric("Медианный интервал уборок (выбранный интервал)", f"{median_interval} дней")
            else:
                st.metric("Средний интервал уборок (выбранный интервал)", "Нет данных")
                st.metric("Медианный интервал уборок (выбранный интервал)", "Нет данных")

        with col2:
            if all_average_interval != "Нет данных":
                st.metric(f"Средний интервал уборок за всё время", f"{all_average_interval} дней")
                if all_median_interval != "Нет данных":
                    st.metric(f"Медианный интервал уборок за всё время", f"{all_median_interval} дней")
            else:
                st.metric(f"Средний интервал уборок за всё время", "Нет данных")
                st.metric(f"Медианный интервал уборок за всё время", "Нет данных")


        all_time_query = """
            SELECT *
            FROM trash_data
            WHERE [Container Number] = ?
        """
        params_all_time = (selected_container,)
        all_time_df = get_data_from_db(all_time_query, params_all_time)

        # 3. Частота событий: заполнение и переполнение
        total_containers = regular_mode + plastic_mode + hopper_mode  # Сумма мод для всех типов контейнеров

        # Для выбранного периода
        filtered_selected_period = filtered_df[filtered_df["Status"] == 0]  # Только записи с Status = 0

        # Проверка наличия данных для выбранного периода
        if not filtered_selected_period.empty:
            # 1) Частота заполнения для выбранного периода
            flooded_count_selected = filtered_selected_period[filtered_selected_period["Flooded Buckets"] >= total_containers].shape[0]
            flooded_frequency_selected = (flooded_count_selected / filtered_selected_period.shape[0]) * 100 if filtered_selected_period.shape[0] > 0 else 0

            # 2) Частота переполнения для выбранного периода
            outside_trash_count_selected = filtered_selected_period[filtered_selected_period["Outside Trash"] > 0].shape[0]
            outside_trash_frequency_selected = (outside_trash_count_selected / filtered_selected_period.shape[0]) * 100 if filtered_selected_period.shape[0] > 0 else 0
        else:
            flooded_frequency_selected = outside_trash_frequency_selected = "Нет данных"

        # Для всего времени (по всем данным, включая все записи)
        # Здесь мы используем all_time_df, который содержит все данные по выбранному контейнеру
        filtered_all_time = all_time_df[all_time_df["Status"] == 0]  # Только записи с Status = 0

        # Проверка наличия данных для всего времени
        if not filtered_all_time.empty:
            # 1) Частота заполнения для всего времени
            flooded_count_all_time = filtered_all_time[filtered_all_time["Flooded Buckets"] >= total_containers].shape[0]
            flooded_frequency_all_time = (flooded_count_all_time / filtered_all_time.shape[0]) * 100 if filtered_all_time.shape[0] > 0 else 0

            # 2) Частота переполнения для всего времени
            outside_trash_count_all_time = filtered_all_time[filtered_all_time["Outside Trash"] > 0].shape[0]
            outside_trash_frequency_all_time = (outside_trash_count_all_time / filtered_all_time.shape[0]) * 100 if filtered_all_time.shape[0] > 0 else 0
        else:
            flooded_frequency_all_time = outside_trash_frequency_all_time = "Нет данных"

        # Размещение метрик в одну строку
        col1, col2 = st.columns(2)

        with col1:
            if flooded_frequency_selected != "Нет данных":
                st.metric("Частота заполнения за выбранный интервал", f"{flooded_frequency_selected:.2f}%")
            else:
                st.metric("Частота заполнения за выбранный интервал", "Нет данных")
            
            if outside_trash_frequency_selected != "Нет данных":
                st.metric("Частота переполнения за выбранный интервал", f"{outside_trash_frequency_selected:.2f}%")
            else:
                st.metric("Частота переполнения за выбранный интервал", "Нет данных")

        with col2:
            if flooded_frequency_all_time != "Нет данных":
                st.metric("Частота заполнения за всё время", f"{flooded_frequency_all_time:.2f}%")
            else:
                st.metric("Частота заполнения за всё время", "Нет данных")

            if outside_trash_frequency_all_time != "Нет данных":
                st.metric("Частота переполнения за всё время", f"{outside_trash_frequency_all_time:.2f}%")
            else:
                st.metric("Частота переполнения за всё время", "Нет данных")
            
        # 5. Корреляция между датами и загруженностью
        filtered_df['loading'] = (filtered_df['Flooded Buckets'] + filtered_df['Partially Filled Buckets'] * 0.5) / total_containers * 100



        filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])

        # Добавляем дополнительные дни на начало и конец для улучшения видимости
        extended_dates = pd.date_range(
            start=filtered_df['Date'].min() - pd.Timedelta(days=1), 
            end=filtered_df['Date'].max() + pd.Timedelta(days=1), 
            freq='D'
        )

        # Добавляем пустые значения для этих дней
        extended_df = pd.DataFrame(extended_dates, columns=['Date'])

        # Мержим с оригинальными данными
        extended_df = pd.merge(extended_df, filtered_df[['Date', 'loading']], on='Date', how='left')



        if 'loading' in filtered_df.columns:
            # Преобразуем даты в таймстампы для расчета корреляции
            filtered_df['timestamp'] = filtered_df['Date'].apply(lambda x: x.timestamp())
            
            # Строим график с использованием Streamlit
            st.write("Загруженность площадки по времени (%)")
            st.line_chart(extended_df.set_index("Date")["loading"].fillna(0))  # Заполняем пустые значения нулями
        else:
            st.warning("Нет данных для расчета загруженности.")


        # Вывод общей информации

        st.write(filtered_df[["Date", "Time", "Status", "trash_bin_id"]])

    # Получаем список районов и их меток
    district_names = {
        "Железнодорожный": "railway",
        "Центральный": "central",
        "Советский": "soviet",
        "Пролетарский": "proletarian",
        "Зареченский": "zarechensky"
    }

    district_names_reversed = {
        "railway": "Железнодорожный",
        "central": "Центральный",
        "soviet" : "Советский",
        "proletarian" : "Пролетарский",
        "zarechensky": "Зареченский"
    }

    # Фильтры
    st.sidebar.header("Информация по району")
    selected_district_name = st.sidebar.selectbox("Выберите район", district_names.keys())

    # Получаем метку района по выбранному названию
    selected_district = district_names[selected_district_name]


    # Кнопка для отображения статистики по району
    if st.sidebar.button("Показать статистику по району"):


        # Запрос данных для выбранного района
        district_query = """
            SELECT *
            FROM trash_data
            WHERE District = ?
        """
        district_data = get_data_from_db(district_query, (selected_district,))

        # Проверка на наличие данных
        if district_data.empty:
            st.warning(f"Нет данных для района: {selected_district_name}.")
        else:
            # Преобразование колонки 'Date' в datetime
            district_data["Date"] = pd.to_datetime(district_data["Date"])
            
            # Вывод всех метрик
            st.subheader(f"Статистика по району {selected_district_name}")

            #1 ТОП 3 худших мусорки
            
            # Функция для вычисления среднего интервала
            def calculate_average_interval(container_data):
                cleaning_dates = container_data.loc[container_data["Status"] == 1, "Date"].sort_values()
                if not cleaning_dates.empty:
                    cleaning_dates = pd.to_datetime(cleaning_dates)
                    intervals = cleaning_dates.diff().dt.days.dropna()
                    if not intervals.empty:
                        return intervals.mean().round(1)
                return None

            # Словари для хранения интервалов
            all_time_intervals = {}
            filtered_intervals = {}

            # Заданный промежуток времени (например, последние 30 дней)
            selected_start_date = datetime.combine(date_from, datetime.min.time())
            selected_end_date = datetime.combine(date_to, datetime.min.time())

            # Рассчитываем интервалы для каждого контейнера
            for container in district_data["Container Number"].unique():
                container_data = district_data[district_data["Container Number"] == container]

                # Рассчитываем средний интервал за все время
                all_time_avg_interval = calculate_average_interval(container_data)
                if all_time_avg_interval is not None:
                    all_time_intervals[container] = all_time_avg_interval

                # Фильтруем данные для заданного промежутка времени
                filtered_data = container_data[(container_data["Date"] >= selected_start_date) & 
                                            (container_data["Date"] <= selected_end_date)]
                if not filtered_data.empty:  # Проверяем, что после фильтрации остались данные
                    filtered_avg_interval = calculate_average_interval(filtered_data)
                    if filtered_avg_interval is not None:
                        filtered_intervals[container] = filtered_avg_interval

            # Преобразуем интервалы в DataFrame для удобства сортировки
            if all_time_intervals:
                all_time_df = pd.DataFrame(list(all_time_intervals.items()), columns=["Container Number", "Average Interval"])
                all_time_worst = all_time_df.sort_values(by="Average Interval", ascending=False).head(3)

                # Выводим топ-3 худших за все время
                st.subheader(f"Топ-3 площадки с большим ожиданием за все время в районе {selected_district_name}")
                if not all_time_worst.empty:
                    for _, row in all_time_worst.iterrows():
                        container = row["Container Number"]
                        interval = row["Average Interval"]
                        st.metric(f"Площадка {int(container)}", f"{interval:.1f} дней")
                else:
                    st.write("Нет данных для расчета интервалов за все время.")

            else:
                st.write("Нет данных для расчета интервалов за все время.")

            # Преобразуем интервалы за выбранный промежуток времени в DataFrame
            if filtered_intervals:
                filtered_df = pd.DataFrame(list(filtered_intervals.items()), columns=["Container Number", "Average Interval"])
                filtered_worst = filtered_df.sort_values(by="Average Interval", ascending=False).head(3)

                # Выводим топ-3 худших за выбранный промежуток времени
                st.subheader(f"Топ-3 площадки с большим ожиданием за выбранный промежуток времени в районе {selected_district_name}")
                if not filtered_worst.empty:
                    for _, row in filtered_worst.iterrows():
                        container = row["Container Number"]
                        interval = row["Average Interval"]
                        st.metric(f"Площадка {int(container)}", f"{interval:.1f} дней")
                else:
                    st.write("Нет данных для расчета интервалов за выбранный промежуток времени.")
            else:
                st.write("Нет данных для расчета интервалов за выбранный промежуток времени.")

            #2 среднее и медиана 

            all_cleaning_dates = district_data.loc[district_data["Status"] == 1, "Date"]
            if not all_cleaning_dates.empty:
                all_cleaning_dates_sorted = all_cleaning_dates.sort_values()
                all_intervals = all_cleaning_dates_sorted.diff().dt.days.dropna()
                all_average_interval = all_intervals.mean().round(1) if not all_intervals.empty else "Нет данных"
                all_median_interval = all_intervals.median().round(1) if not all_intervals.empty else "Нет данных"
            else:
                all_average_interval = all_median_interval = "Нет данных"

            # 2. Среднее и медианное время очистки за выбранный промежуток времени
            filtered_data = district_data[(district_data["Date"] >= selected_start_date) & 
                                        (district_data["Date"] <= selected_end_date)]
            cleaning_dates_filtered = filtered_data.loc[filtered_data["Status"] == 1, "Date"]
            if not cleaning_dates_filtered.empty:
                cleaning_dates_filtered_sorted = cleaning_dates_filtered.sort_values()
                intervals_filtered = cleaning_dates_filtered_sorted.diff().dt.days.dropna()
                average_interval_filtered = intervals_filtered.mean().round(1) if not intervals_filtered.empty else "Нет данных"
                median_interval_filtered = intervals_filtered.median().round(1) if not intervals_filtered.empty else "Нет данных"
            else:
                average_interval_filtered = median_interval_filtered = "Нет данных"

            # Вывод статистики
            st.subheader(f"Прочая статистика")

            col1, col2 = st.columns(2)

            with col1:
                # Выводим "Нет данных", если значения нет, а если есть, добавляем единицы измерения
                if average_interval_filtered != "Нет данных":
                    st.metric(f"Средний интервал уборок (выбранный интервал)", f"{average_interval_filtered} дней")
                else:
                    st.metric(f"Средний интервал уборок (выбранный интервал)", "Нет данных")

                if median_interval_filtered != "Нет данных":
                    st.metric(f"Медианный интервал уборок (выбранный интервал)", f"{median_interval_filtered} дней")
                else:
                    st.metric(f"Медианный интервал уборок (выбранный интервал)", "Нет данных")
                            
            with col2:
                # Выводим "Нет данных", если значения нет, а если есть, добавляем единицы измерения
                if all_average_interval != "Нет данных":
                    st.metric("Средний интервал уборок за всё время", f"{all_average_interval} дней")
                else:
                    st.metric("Средний интервал уборок за всё время", "Нет данных")

                if all_median_interval != "Нет данных":
                    st.metric("Медианный интервал уборок за всё время", f"{all_median_interval} дней")
                else:
                    st.metric("Медианный интервал уборок за всё время", "Нет данных")
            #3 среднее медианное заполнение переполнение

            district_data["total_containers"] = (district_data["Regular Containers"] +
                                     district_data["Plastic Containers"] +
                                     district_data["Hopper Containers"])

            # Для каждой мусорки в районе
            modes_for_district = []

            # Итерируем по каждой мусорке (если у нас есть идентификатор мусорки, например, "Bin_ID")
            for bin_id in district_data["Container Number"].unique():
                bin_data = district_data[district_data["Container Number"] == bin_id]  # Данные по конкретной мусорке

                # 1. Моды для каждого контейнера на данной мусорке
                if not bin_data.empty:
                    regular_mode = bin_data["Regular Containers"].mode()[0]
                    plastic_mode = bin_data["Plastic Containers"].mode()[0]
                    hopper_mode = bin_data["Hopper Containers"].mode()[0]
                else:
                    regular_mode = plastic_mode = hopper_mode = "Нет данных"
                
                # Для выбранного периода
                filtered_selected_period = bin_data[(bin_data["Status"] == 0) & 
                                                    (bin_data["Date"] >= selected_start_date) & 
                                                    (bin_data["Date"] <= selected_end_date)]  # Только записи с Status = 0 и в пределах выбранного периода

                # Проверка наличия данных для выбранного периода
                if not filtered_selected_period.empty:
                    # Частота заполнения для выбранного периода
                    flooded_count_selected = filtered_selected_period[filtered_selected_period["Flooded Buckets"] >= bin_data["total_containers"].mode()[0]].shape[0]
                    flooded_frequency_selected = (flooded_count_selected / filtered_selected_period.shape[0]) * 100 if filtered_selected_period.shape[0] > 0 else 0

                    # Частота переполнения для выбранного периода
                    outside_trash_count_selected = filtered_selected_period[filtered_selected_period["Outside Trash"] > 0].shape[0]
                    outside_trash_frequency_selected = (outside_trash_count_selected / filtered_selected_period.shape[0]) * 100 if filtered_selected_period.shape[0] > 0 else 0
                else:
                    flooded_frequency_selected = outside_trash_frequency_selected = "Нет данных"

                # Для всего времени (по всем данным, включая все записи)
                filtered_all_time = bin_data[bin_data["Status"] == 0]  # Только записи с Status = 0 для всех данных

                # Проверка наличия данных для всего времени
                if not filtered_all_time.empty:
                    # Частота заполнения для всего времени
                    flooded_count_all_time = filtered_all_time[filtered_all_time["Flooded Buckets"] >= bin_data["total_containers"].mode()[0]].shape[0]
                    flooded_frequency_all_time = (flooded_count_all_time / filtered_all_time.shape[0]) * 100 if filtered_all_time.shape[0] > 0 else 0

                    # Частота переполнения для всего времени
                    outside_trash_count_all_time = filtered_all_time[filtered_all_time["Outside Trash"] > 0].shape[0]
                    outside_trash_frequency_all_time = (outside_trash_count_all_time / filtered_all_time.shape[0]) * 100 if filtered_all_time.shape[0] > 0 else 0
                else:
                    flooded_frequency_all_time = outside_trash_frequency_all_time = "Нет данных"
                
                # Сохраняем результаты для каждой мусорки
                modes_for_district.append({
                    "Container Number": bin_id,
                    "Regular Mode": regular_mode,
                    "Plastic Mode": plastic_mode,
                    "Hopper Mode": hopper_mode,
                    "Flooded Frequency (Selected)": flooded_frequency_selected,
                    "Outside Trash Frequency (Selected)": outside_trash_frequency_selected,
                    "Flooded Frequency (All Time)": flooded_frequency_all_time,
                    "Outside Trash Frequency (All Time)": outside_trash_frequency_all_time
                })

            # Преобразуем результаты в DataFrame
            modes_for_district_df = pd.DataFrame(modes_for_district)

            modes_for_district_df['Flooded Frequency (Selected)'] = pd.to_numeric(modes_for_district_df['Flooded Frequency (Selected)'], errors='coerce')
            modes_for_district_df['Outside Trash Frequency (Selected)'] = pd.to_numeric(modes_for_district_df['Outside Trash Frequency (Selected)'], errors='coerce')
            modes_for_district_df['Flooded Frequency (All Time)'] = pd.to_numeric(modes_for_district_df['Flooded Frequency (All Time)'], errors='coerce')
            modes_for_district_df['Outside Trash Frequency (All Time)'] = pd.to_numeric(modes_for_district_df['Outside Trash Frequency (All Time)'], errors='coerce')

            # Теперь можно безопасно вычислить среднее и медианное значения
            average_flooded_frequency_selected = modes_for_district_df['Flooded Frequency (Selected)'].mean()
            average_outside_trash_frequency_selected = modes_for_district_df['Outside Trash Frequency (Selected)'].mean()
            average_flooded_frequency_all_time = modes_for_district_df['Flooded Frequency (All Time)'].mean()
            average_outside_trash_frequency_all_time = modes_for_district_df['Outside Trash Frequency (All Time)'].mean()

            # Выводим результаты
            col1, col2 = st.columns(2)

            with col1:
                # Проверяем и выводим среднее значение для частоты заполнения (выбранный интервал)
                if pd.notna(average_flooded_frequency_selected):
                    st.metric("Среднее значение заполнения (выбранный интервал)", f"{average_flooded_frequency_selected:.2f}%")
                else:
                    st.metric("Среднее значение заполнения (выбранный интервал)", "Нет данных")
                
                # Проверяем и выводим среднее значение для частоты переполнения (выбранный интервал)
                if pd.notna(average_outside_trash_frequency_selected):
                    st.metric("Среднее значение переполнения (выбранный интервал)", f"{average_outside_trash_frequency_selected:.2f}%")
                else:
                    st.metric("Среднее значение переполнения (выбранный интервал)", "Нет данных")

            with col2:
                # Проверяем и выводим среднее значение для частоты заполнения (все данные)
                if pd.notna(average_flooded_frequency_all_time):
                    st.metric("Среднее значение заполнения (всё время)", f"{average_flooded_frequency_all_time:.2f}%")
                else:
                    st.metric("Среднее значение заполнения (всё время)", "Нет данных")
                
                # Проверяем и выводим среднее значение для частоты переполнения (все данные)
                if pd.notna(average_outside_trash_frequency_all_time):
                    st.metric("Среднее значение переполнения (всё время)", f"{average_outside_trash_frequency_all_time:.2f}%")
                else:
                    st.metric("Среднее значение переполнения (всё время)", "Нет данных")
        

    st.sidebar.header("Дополнительная статистика")

    # Общая аналитика по городу
    if st.sidebar.button("Аналитика по городу"):


        district_query = """
            SELECT *
            FROM trash_data
            WHERE District = ?
        """

        districts = district_names_reversed.keys()

        # Словарь для хранения результатов
        average_intervals = {}

        # Проходим по каждому району
        for district in districts:
            # Фильтруем данные по району
            district_data = get_data_from_db(district_query, (district,))
            district_data["Date"] = pd.to_datetime(district_data["Date"], errors='coerce')
            district_data_filtered = district_data[district_data["District"] == district]

            # 1. Среднее время очистки за весь период
            all_cleaning_dates = district_data_filtered.loc[district_data_filtered["Status"] == 1, "Date"]
            if all_cleaning_dates.empty:
                all_average_interval = "Нет данных"
            else:
                all_cleaning_dates_sorted = all_cleaning_dates.sort_values()
                all_intervals = all_cleaning_dates_sorted.diff().dt.days.dropna()
                if all_intervals.empty:
                    all_average_interval = "Нет данных"
                else:
                    all_average_interval = all_intervals.mean().round(1)

            # Сохраняем результат в словарь
            average_intervals[district] = {
                "all_average_interval": all_average_interval
            }

            # Выводим результаты для всех районов
        for district in districts:
            st.markdown(f"### {district_names_reversed[district]}")
            # Проверяем, если данные отсутствуют, выводим "Нет данных"
            if average_intervals[district]['all_average_interval'] == "Нет данных":
                st.markdown(f"**Средний интервал:** Нет данных")
            else:
                st.markdown(f"**Средний интервал:** {average_intervals[district]['all_average_interval']} дней")


        
        problematic_regions = {}
        flooded_locations = {}
        outside_trash_locations = {}

        # Проходим по каждому району
        for district in districts:
            # Фильтруем данные по району
            district_data = get_data_from_db(district_query, (district,))
            
            # Расчеты для проблемных районов (переполненные баки)
            flooded_buckets_mean = district_data["Flooded Buckets"].mean() * 100  
            problematic_regions[district] = flooded_buckets_mean

            # Расчеты для локаций с наибольшим количеством переполненных баков
            flooded_buckets_sum = district_data["Flooded Buckets"].sum()
            flooded_locations[district] = flooded_buckets_sum

            # Расчеты для районов с самым высоким количеством мусора вне баков
            outside_trash_sum = district_data["Outside Trash"].sum() 
            outside_trash_locations[district] = outside_trash_sum


        # 1. Самые проблемные районы (переполненные баки)
        problematic_regions_sorted = sorted(problematic_regions.items(), key=lambda x: x[1], reverse=True)
        problematic_regions_df = pd.DataFrame(problematic_regions_sorted, columns=["District", "Flooded Buckets (%)"])
        st.write("### Самые проблемные районы (переполненные баки)")
        st.bar_chart(problematic_regions_df.set_index("District"))

        # 2. Локации с наибольшим количеством переполненных баков
        flooded_locations_sorted = sorted(flooded_locations.items(), key=lambda x: x[1], reverse=True)
        flooded_locations_df = pd.DataFrame(flooded_locations_sorted, columns=["District", "Flooded Buckets"])
        st.write("### Локации с наибольшим количеством переполненных баков")
        st.bar_chart(flooded_locations_df.set_index("District"))

        # 3. Районы с самым высоким количеством мусора вне баков
        outside_trash_locations_sorted = sorted(outside_trash_locations.items(), key=lambda x: x[1], reverse=True)
        outside_trash_locations_df = pd.DataFrame(outside_trash_locations_sorted, columns=["District", "Outside Trash"])
        st.write("### Районы с самым высоким количеством мусора вне баков")
        st.bar_chart(outside_trash_locations_df.set_index("District"))



        # Кнопка для проверки всех контейнеров
    if st.sidebar.button("Проверка дат вывоза"):
        check_all_containers()

        # Кнопка для построения еженедельного отчета
    if st.sidebar.button("Показать еженедельный отчет"):
        generate_weekly_report()

         # Кнопка для построения ежемесячного отчета
    if st.sidebar.button("Показать ежемесячный отчет"):
        generate_mouth_report()

if __name__ == "__main__":
    main()