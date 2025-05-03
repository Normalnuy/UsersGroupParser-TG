import os, datetime, asyncio
from utils import *

from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors import FloodWaitError

async def main():
    create_config()
    client: TelegramClient = await create_client()
    if not client: 
        print("Не удалось создать клиент.")
        program_over()
    
    link = get_link()
    days = get_days()
    group_name = link.split("https://t.me/")[-1]
    
    messages = await fetch_messages(client, group_name, days)
    print(f"Найдено {len(messages)} сообщений за последние {days} дней.")
    
    usernames = await get_usernames(client, messages)
    print(f"Найдено {len(usernames)} юзернеймов.")
    
    save_usernames_to_file(usernames, group_name)
    program_over()
    
    
async def fetch_messages(client: TelegramClient, group_name: str, days: int):
    try:
        if group_name.startswith("+"):
            group_name = f"https://t.me/joinchat/{group_name[1:]}"
        entity = await client.get_entity(group_name)

        date_limit = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
        
        all_messages = []
        offset_id = 0
        limit = 100
        
        print(f"Получение сообщений из группы {group_name} за последние {days} дней.")
        print("За 1 запрос обрабатывается 100 сообщений, будет несколько запросов.")
        print("Это может занять некоторое время.")
        print("Пожалуйста, подождите...")
        while True:
            history = await client(GetHistoryRequest(
                peer=entity,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))

            messages = history.messages
            if not messages:
                break
            
            messages_bar = ProgressBar(len(messages))
            for message in messages:
                messages_bar.next("Получение сообщений.")
                if message.date < date_limit:
                    messages_bar.end("Получение сообщений. | Завершено.")
                    return all_messages
                all_messages.append(message.to_dict())
            offset_id = messages[-1].id
    except Exception as e:
        print(f"\nОшибка при получении сообщений: {e}")
        return []

async def get_usernames(client: TelegramClient, all_messages: list):
    unique_usernames = set()

    print("Получение юзернеймов из сообщений.")
    users_bar = ProgressBar(len(all_messages))
    for message_dict in all_messages:
        users_bar.next("Получение юзернеймов.")
        
        try:
            sender = await get_sender_from_dict(client, message_dict)
            if sender is None: continue
        except FloodWaitError as e:
            print(f"\nСлишком много запросов. Подождите {e.seconds} секунд.")
            await asyncio.sleep(e.seconds)
            sender = await get_sender_from_dict(client, message_dict)
        
        if sender and sender.username and not sender.bot:
            unique_usernames.add(sender.username)
            
    return unique_usernames


async def get_sender_from_dict(client: TelegramClient, message_dict: dict):
    while True:
        try:
            if message_dict is None:
                print("Сообщение отсутствует. Пропуск.")
                return None

            if 'from_id' in message_dict and message_dict['from_id'] is not None:
                if '_' in message_dict['from_id'] and message_dict['from_id']['_'] == 'PeerUser':
                    user_id = message_dict['from_id']['user_id']
                    sender = await client.get_entity(user_id)
                    return sender
                else:
                    return None
            else:
                return None
        except FloodWaitError as e:
            for remaining in range(e.seconds, 0, -1):
                sys.stdout.write(f"\rСлишком много запросов. Подождите {remaining} секунд.")
                sys.stdout.flush()
                await asyncio.sleep(1)
            sys.stdout.write("\r" + " " * 50 + "\r")  # Очистка строки после ожидания
        except Exception as e:
            print(f"Ошибка при получении отправителя: {e}. Повтор попытки...")

def get_days():
    while True:
        days = input("Введите количество дней: ")
        if days.isdigit() and int(days) > 0:
            return int(days)
        print("Некорректное количество дней. Попробуйте снова.")


def get_link():
    while True:
        link = input("Введите ссылку на группу: ")
        if link.startswith("https://t.me/"):
            return link
        print("Некорректная ссылка. Попробуйте снова.")


def create_config():
    if not os.path.exists(session_file):
        print("https://my.telegram.org/")
        api_id = input("Введите api_id аккаунта: ")
        api_hash = input("Введите api_hash аккаунта: ")
        save_config({"api_id": api_id, "api_hash": api_hash})
    return
    

async def create_client():      
    config = read_config()
    api_id = config['api_id']
    api_hash = config['api_hash']
      
    client = TelegramClient(session_file, int(api_id), api_hash, 
                            system_version="4.16.30-vxCUSTOM",
                            device_model='Windows 11 Pro',
                            app_version='9.1.2')
    await client.start()
    if not await client.is_user_authorized():
        await client.disconnect()
        print("Что-то пошло не так...\nПроверьте [ .session | api_id | api_hash ].")
        return False
    else:
        print("Сессия авторизована.")
        return client
    
    
    
    
    
if __name__ == "__main__":
    asyncio.run(main())