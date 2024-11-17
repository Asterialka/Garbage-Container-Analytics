Сайт для аналитики мусорных баков.
Проект команды "Без суеты".
Состав команды:
- Плотников Даниил
- Яков Борковец
- Шилов Артем <br />
Для начала вам нужно скачать файл `Download_App.py`, где просиходит загрузка фотографии мусорки и заполнение соответствующих полей формы.
Затем идет обработка фотографии с помощью нейронной сети и, полученные данные добавляются в базу данных.
<br /> По итогу вы получаете обновленную базу данных с колонками такими как: <br />
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
  
