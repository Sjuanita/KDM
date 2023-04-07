from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId, json_util

# Создание экземпляра FastAPI
app = FastAPI()

# Подключение к базе данных MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['messenger']
messages_collection = db['messages']
users_collection = db['users']


# Модель для входящего сообщения
class Message(BaseModel):
    sender_id: str
    recipient_id: str
    text: str


# Модель для пользователя
class User(BaseModel):
    username: str
    password: str


# Создание пользователя
@app.post('/users')
def create_user(user: User):
    user_dict = user.dict()
    # Хэширование пароля и сохранение в базе данных
    # Здесь можно использовать библиотеку passlib для хэширования пароля
    # и сохранения в MongoDB
    user_id = users_collection.insert_one(user_dict)
    return "OK"


# Отправка сообщения
@app.post('/messages')
def send_message(message: Message):
    # Проверка существования отправителя и получателя в базе данных
    sender = users_collection.find_one({'username': message.sender_id})
    recipient = users_collection.find_one({'username': message.recipient_id})
    if not sender or not recipient:
        raise HTTPException(status_code=400, detail='Отправитель или получатель не существует')
    message_dict = message.dict()
    print(message_dict)
    messages_collection.insert_one(message_dict)
    return "OK"


# Получение всех сообщений
@app.get('/messages', response_model=list[Message])
def get_all_messages():
    messages = messages_collection.find()
    return list(messages)


# Получение всех сообщений конкретного получателя
@app.get('/messages/{recipient_id}')
def get_messages_for_recipient(recipient_id: str):
    messages = messages_collection.find({'recipient_id': recipient_id}, {'_id': 0, 'text': 1})  # Указываем, что хотим только поле text
    text_list = [message['text'] for message in messages]
    return text_list
