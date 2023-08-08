import asyncio
from excel import write_excel
from telethon import TelegramClient
import json


api_id =
api_hash = ''
client = TelegramClient("", api_id, api_hash,  system_version="4.16.30-vxYOUR_TEXT")

async def test_parse_channel():
    channel_url = "https://t.me/Alena_Vodonaeva"
    filt = ["вирус", "пандемия"]
    messages = await parse_channel(channel_url, filt)
    print(messages)

async def parse_channel(channel, filt):
    async with client:
        await client.connect()
        results = {word: {} for word in filt}
        message_counts = {word: 0 for word in filt}
        filt_copy = filt.copy()
        async for message in client.iter_messages(channel):
            for word in filt_copy:
                if message.text is not None and word.lower() in message.text.lower() and message.text != '':
                    message_data = {
                        'text': message.text.replace('\n', ' '),
                        'url': fr"https://{channel}/{message.id}"
                    }
                    if message.id not in results[word]:
                        results[word][message.id] = message_data
                        message_counts[word] += 1
                        if message_counts[word] == 100:
                            filt_copy.remove(word)
                if len(filt_copy) == 0:
                    return results
        return results

async def main():
    with open("filter.json", "r") as file:
        all_settings = json.load(file)
    filt = all_settings["filters"]
    channels = all_settings["urls"]
    result_dict = {}
    for channel in channels:
        parsed_channel = await parse_channel(channel, filt)
        for word, messages in parsed_channel.items():
            result_dict.setdefault(word, {})
            result_dict[word] |= messages
    with open('result.json', 'w', encoding="utf-8") as f:
        json.dump(result_dict, f, indent=4, ensure_ascii=False)
    write_excel()
    return result_dict  # функция main теперь возвращает результаты

if __name__ == '__main__':
    len_of_messages = 10
    loop = asyncio.get_event_loop()  # создаем event loop
    result_dict = loop.run_until_complete(main())  # вызываем main() внутри event loop
    loop.close()