Сайт для аналитики мусорных баков <br />
Проект команды "Без суеты".
Состав команды:
- Плотников Даниил
- Яков Борковец
- Шилов Артем <br />
По всем вопросам обращайтесь в тг: @DanilChil | Подсказки были написаны с использование Linux Ubuntu
# Запуск приложения
Для начала вам нужно скачать файл `Download_App.py`. <br />
Для запуска Streamlit приложения используйте следующую команду:

```bash
streamlit run Download_App.py
```
И установить дополнительные пакеты (если потребуется для запуска):
```bash
pip install streamlit
pip install roboflow
```
 где просиходит загрузка фотографии мусорной площадки, и заполнение соответствующих полей формы:
  ![image](https://github.com/user-attachments/assets/d521a884-ba66-4862-aef8-0aa28b79bbb4)
<br /> Затем идет обработка фотографии с помощью нейронной сети, и полученные данные добавляются в базу данных:
<br /> По итогу вы получаете обновленную базу данных с колонками такими как: <br />
`'Trash_Bin_Id': id` - id обращения к БД <br /> 
` 'Date': date ` - дата <br /> 
` 'Time': time` - время <br />
` 'District': district_codes[district]` - район <br />
`'Container Number': container_number` - идентификационный номер контейнера <br />
` 'Status': status_codes[status]` - статус "до" или "после" уборки <br />
` 'Empty Buckets': empty_buckets ` - кол-во пустых контейнеров <br />
` 'Flooded Buckets': flooded_buckets` - кол-во полных контейнеров <br />
`'Partially Filled Buckets': partially_filled_buckets` - кол-во частично заполненных контейнеров <br />
`'Outside Trash': outside_trash ` - наличие мусора вне бака на площадке <br />
`'Regular Containers': regular_containers` - первый вид контейнеров <br />
`'Plastic Containers': plastic_containers ` - второй вид контейнеров <br />
`'Hopper Containers': hopper_containers` - третий вид контенейров <br />
`'Filename': file_name` - имя файла <br />
Добавленная строчка в базу данных:
![image](https://github.com/user-attachments/assets/f6ac5603-d259-4778-8d76-322a5cbd9cc8)
Интерфейс сайта после добавления фотографии:
![image](https://github.com/user-attachments/assets/cbec5613-0970-4fbd-8f35-5c0965293c74)
![image](https://github.com/user-attachments/assets/25e0454a-3260-437d-8255-7c913990f930)
# Преобразование cvs файла в db
Для этого вам понадобится запустить файл `Сonverter.py`, который сохранит базу данных в эту же папку. Уже с ней вы и будете далее работать.
# Запуск приложения для статистики
Для этого вам понадобится скачать и запустить файл `Statystics_App.py` вместе с базой данных `trash_bins.db`:
```bash
streamlit run Statystics_App.py
```
И нас встретит первичное окно:
![image](https://github.com/user-attachments/assets/16d310cd-64df-4194-99cc-d1a77ca7a59d)
Откуда можно будет перейти по различным разделам:
- Статистика по каждой мусорке за определенные даты отдельно
- Статистика по району
- Статистика по городу
- Проверка дат вывоза (в случае если более 3 дней выскакивает предупреждение)
- Создание и показ еженедельного отчета
- Создание и показ ежемесячного отчета <br />
Один из примеров просмотра статистики: 
![image](https://github.com/user-attachments/assets/2da3e6fe-15d9-4fa0-b2fa-6a8f246a95ac)
Также вы можете добавить отображение картинок на сайт если раскоммитите 209-234 и 16 строчку кода, и загрузите изображения в ваш проект. <br />
`Приятного пользования! По всем вопросам тг: @DanilChil`
