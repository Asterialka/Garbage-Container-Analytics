Сайт для аналитики мусорных баков <br />
Проект команды "Без суеты".
Состав команды:
- Плотников Даниил
- Яков Борковец
- Шилов Артем <br />
Для начала вам нужно скачать файл `Download_App.py`, где просиходит загрузка фотографии мусорки, и заполнение соответствующих полей формы:
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


