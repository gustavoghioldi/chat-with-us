import requests

url = f"https://api.telegram.org/bot8194455142:AAFF3mcqlZO7PkqqQ-jCuoDqMFh7xjTe08M/getUpdates"
response = requests.get(url)
print(response.json())


# import requests

# TOKEN = '8194455142:AAFF3mcqlZO7PkqqQ-jCuoDqMFh7xjTe08M'
# CHAT_ID = '1328800058'
# MENSAJE = 'Me chuoa la pija tu opinion'

# url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
# payload = {
#     'chat_id': CHAT_ID,
#     'text': MENSAJE
# }

# response = requests.post(url, data=payload)
# print(response.json())

##  ejemplo cuando envian un archivo
# {'ok': True, 'result': [{'update_id': 287740888, 'message': {'message_id': 4, 'from': {'id': 1328800058, 'is_bot': False, 'first_name': 'El Barba', 'last_name': 'Katana Voladora', 'language_code': 'es'}, 'chat': {'id': 1328800058, 'first_name': 'El Barba', 'last_name': 'Katana Voladora', 'type': 'private'}, 'date': 1751918397, 'text': 'HOLA'}}, {'update_id': 287740889, 'message': {'message_id': 5, 'from': {'id': 1328800058, 'is_bot': False, 'first_name': 'El Barba', 'last_name': 'Katana Voladora', 'language_code': 'es'}, 'chat': {'id': 1328800058, 'first_name': 'El Barba', 'last_name': 'Katana Voladora', 'type': 'private'}, 'date': 1751918438, 'text': 'CHAU'}}, {'update_id': 287740890, 'message': {'message_id': 6, 'from': {'id': 1328800058, 'is_bot': False, 'first_name': 'El Barba', 'last_name': 'Katana Voladora', 'language_code': 'es'}, 'chat': {'id': 1328800058, 'first_name': 'El Barba', 'last_name': 'Katana Voladora', 'type': 'private'}, 'date': 1751918746, 'document': {'file_name': 'dolarapp.pdf', 'mime_type': 'application/pdf', 'file_id': 'BQACAgEAAxkBAAMGaGwomkDYp2jFbiEJCSrliyU1YxYAArQFAAJhbmBH3f79S4nzupM2BA', 'file_unique_id': 'AgADtAUAAmFuYEc', 'file_size': 16346}}}]}

# {"ok":true,"result":{"file_id":"BQACAgEAAxkBAAMGaGwomkDYp2jFbiEJCSrliyU1YxYAArQFAAJhbmBH3f79S4nzupM2BA","file_unique_id":"AgADtAUAAmFuYEc","file_size":16346,"file_path":"documents/file_0.pdf"}}

# https://api.telegram.org/file/bot8194455142:AAFF3mcqlZO7PkqqQ-jCuoDqMFh7xjTe08M/documents/file_0.pdf

# https://api.telegram.org/file/bot8194455142:AAFF3mcqlZO7PkqqQ-jCuoDqMFh7xjTe08M/voice/file_1.oga
