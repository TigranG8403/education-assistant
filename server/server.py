from fastapi import FastAPI, HTTPException, Body, File, UploadFile, Request, Form
from fastapi.responses import FileResponse, JSONResponse
import json
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pytubefix import YouTube
from pydub import AudioSegment
import speech_recognition as sr
import html
import asyncio
from transformers import pipeline
from bert_punctuation import Bert_punctuation
import re

translator_ru_en = pipeline("translation", model="Helsinki-NLP/opus-mt-ru-en")
translator_en_ru = pipeline("translation", model="Helsinki-NLP/opus-mt-en-ru")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
Bert_punctuation = Bert_punctuation()

app = FastAPI()
DATA_FILE = "C:\\data.json"

def load_users():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}

def save_users(users):
    """Сохраняет пользователей в JSON-файл."""
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

users = load_users()

@app.post("/download")
async def download_file(request: Request):
    data = await request.json()
    print(data)
    user = data.get("user")
    file_name = data.get("file_name")
    print(user)
    print(file_name)
    with open(f"C:\\API\\{user}\\{file_name}.json", 'r', encoding='utf-8') as f:
        js = json.load(f)
        theme = js.get("theme")
        sum_text = js.get("sum_text")
        plan = js.get("plan")
        return JSONResponse({"theme": theme, "sum_text": sum_text, "plan": plan})


@app.post("/download_video")
async def download_video(request: Request):
    data = await request.json()
    url = data.get("url")
    user = data.get("user")
    print(url)

    yt = YouTube(url)
    chars_to_remove = ['<','>',':','«','/','\\','|','?','*']
    delete_table = str.maketrans('', '', ''.join(chars_to_remove))
    yttitle = yt.title.translate(delete_table)


    ys = yt.streams.get_audio_only()

    ys.download(f"C:\\API\\{user}")
    sound = AudioSegment.from_file(f"C:\\API\\{user}\\{yttitle}.m4a")
    sound.export(f"C:\\API\\{user}\\{yttitle}.wav", format="wav")
    audio_file = f"C:\\API\\{user}\\{yttitle}.wav"

    max_duration = 61
    audio = AudioSegment.from_file(audio_file)
    text = ""
    r = sr.Recognizer()
    result = ""
    fragments = []
    start_time = 0
    end_time = 0

    while end_time < len(audio):
        end_time = min(start_time + max_duration * 1000, len(audio))
        audio_fragment = audio[start_time:end_time]

        # Используем распознавание речи для определения конца слова
        with sr.AudioFile(audio_fragment.export(f"C:\\API\\{user}\\temp.wav", format="wav")) as source:
            audio_data = r.record(source)
            try:
                text = r.recognize_google(audio_data, language="ru-RU")
                # Находим индекс последнего пробела в тексте, чтобы определить конец слова
                last_space_index = text.rfind("  ")
                # Если пробел найден, сдвигаем время окончания фрагмента
                if last_space_index != -1:
                    # Исправленный расчет времени окончания:
                    end_time = start_time + (last_space_index + 1) * 1000 / len(text) * len(audio_fragment)

                    # Проверка, чтобы не выйти за пределы аудиофайла
                    end_time = min(end_time, len(audio))

            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"Ошибка распознавания речи: {e}")


        result = result + text + " "
        # Сохраняем фрагмент
        fragment_name = f"{audio_file[:-4]}_{start_time // 1000}_{end_time // 1000}.wav"
        audio_fragment.export(fragment_name, format="wav")
        fragments.append(fragment_name)

        # Переходим к следующему фрагменту, **только если end_time не достиг конца аудиофайла**
        if end_time < len(audio):
            start_time = end_time

    print(result)
    for filename in os.listdir(f"C:\\API\\{user}"):
        if filename.startswith(yttitle):
            file_path = os.path.join(f"C:\\API\\{user}", filename)
            if os.path.isfile(file_path):
                    os.remove(file_path)

    return {"text": result}

@app.post("/register")
async def register(email: str = Body(..., embed=True),
                       password: str = Body(..., embed=True)):

    if email in users:
        raise HTTPException(status_code=401, detail ="Пользователь с таким логином уже существует")

    users[email] = {"password": password}
    save_users(users)
    os.mkdir(f"C:\\API\\{email}")
    return {"message": "Пользователь успешно зарегистрирован"}

@app.post("/auth")
async def auth(email: str = Body(..., embed=True),
                       password: str = Body(..., embed=True)):

    if email not in users:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    if password != users[email]["password"]:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")


@app.get("/files/{user_folder}/{filename}")
async def get_file(user_folder:str, filename: str):
    file_path = os.path.join(user_folder, filename)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        return {"message": "Файл не найден"}

@app.get("/files/{user_folder}")
async def list_files(user_folder: str):
    files = []
    for filename in os.listdir(f"C:\\API\\{user_folder}"):
        files.append(filename)

    files_no_ext = [os.path.splitext(f)[0] for f in files]
    print(files_no_ext)
    return {"files": files_no_ext}

@app.post("/upload_text")
async def upload_text(user: str = Form(...), file: UploadFile = File(...)):
    if os.path.exists(f"C:\\API\\{user}\\temp.wav"):
        # Удаление файла
        os.remove(f"C:\\API\\{user}\\temp.wav")
    else:
        pass

    pr_text = file.file.read().decode("utf-8")
    print(pr_text)
    if not re.search(r"[.,]", pr_text):

        max_length = 120
        parts = []
        current_part = ""
        current_length = 0

    # Разбиваем текст на предложения
        sentences = pr_text.split(".")

        for sentence in sentences:
            words = sentence.split()

            for word in words:
                if current_length + len(word) + 1 > max_length:  # + 1 для пробела
                    parts.append(current_part.strip())
                    current_part = ""
                    current_length = 0
                current_part += word + " "
                current_length += len(word) + 1

        # Добавляем точку в конце предложения
            if current_part:
                current_part += "."
                parts.append(current_part.strip())
                current_part = ""
                current_length = 0


        if current_part:
            parts.append(current_part.strip())

        parts_punctuation = Bert_punctuation.predict(parts)
        print(parts_punctuation)
        ptext = ""
        for i, element in enumerate(parts_punctuation):
            ptext += element
            if i < len(parts_punctuation) - 1:
                ptext += ". "

        print(ptext)
        text = html.unescape(ptext)
    else:
        text = html.unescape(pr_text)

    text_chunks = chunk_text_by_sentence(text, max_chunk_size=500)

    # Шаг 1: Перевод текста с русского на английский
    translated_text = await translate_to_english(text_chunks)

    # Шаг 2: Суммаризация переведенного текста
    summary_chunks = chunk_text_by_sentence(translated_text, max_chunk_size=1024)
    summary_en = await summarize_text(summary_chunks)

    # Шаг 3: Обратный перевод суммаризации на русский
    final_summary_chunks = chunk_text_by_sentence(summary_en, max_chunk_size=500)
    final_summary = await translate_to_russian(final_summary_chunks)
    final_summary = html.unescape(final_summary)  # Декодируем HTML-сущности

    print("Финальная суммаризация:")
    print(final_summary)
    try:
        # Шаг 4: Генерация темы текста
        topic_summary = await generate_topic(translated_text)
        translated_topic = await translate_to_russian([topic_summary])
        translated_topic = html.unescape(translated_topic)  # Декодируем HTML-сущности

        print("\nТема текста:")
        print(translated_topic)

        # Шаг 5: Генерация плана текста
        plan_points = await generate_plan(translated_text)
        translated_plan_points = await translate_to_russian(plan_points)
        translated_plan_chunks = html.unescape(translated_plan_points).split(". ")


        joined_text = ""
        for i, element in enumerate(translated_plan_chunks):
            joined_text += f"{i + 1}. {element}\n\n"
        joined_text.strip()
        short_string = translated_topic[:30] if len(translated_topic) > 20 else translated_topic
        data = {"theme": translated_topic, "sum_text": final_summary, "plan": joined_text}
        with open(f"C:\\API\\{user}\\{short_string}.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return JSONResponse ({"theme": translated_topic, "sum_text": final_summary, "plan": joined_text})

    except:
        short_string = final_summary[:30] if len(final_summary) > 20 else final_summary
        data = {"theme": short_string, "sum_text": final_summary, "plan": 'Ошибка_объём'}
        with open(f"C:\\API\\{user}\\{short_string}.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return JSONResponse({"theme": short_string, "sum_text": final_summary, "plan": 'Ошибка_объём'})


# Функция для разбиения текста на части, сохраняя предложения
def chunk_text_by_sentence(text, max_chunk_size=500):
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_size
        if end >= len(text):
            chunks.append(text[start:])
            break
        end = text.rfind('.', start, end) + 1
        if end == 0:
            end = start + max_chunk_size
        chunks.append(text[start:end].strip())
        start = end
    return chunks

# Асинхронная функция для перевода текста с русского на английский
async def translate_to_english(text_chunks):
    tasks = [asyncio.to_thread(translator_ru_en, chunk, max_length=512) for chunk in text_chunks]
    translations = await asyncio.gather(*tasks)
    return " ".join([t[0]['translation_text'] for t in translations])

# Асинхронная функция для суммаризации текста
async def summarize_text(summary_chunks):
    summarized_chunks = []
    for chunk in summary_chunks:
        input_length = len(chunk.split())  # Определяем количество слов в фрагменте
        max_summary_length = max(30, int(input_length * 0.5))  # Устанавливаем max_length как 50% от длины фрагмента
        summary = await asyncio.to_thread(summarizer, chunk, max_length=max_summary_length, min_length=15, do_sample=False)
        summarized_chunks.append(summary[0]['summary_text'])
    return " ".join(summarized_chunks)

# Асинхронная функция для обратного перевода текста на русский
async def translate_to_russian(text_chunks):
    tasks = [asyncio.to_thread(translator_en_ru, chunk, max_length=512) for chunk in text_chunks]
    translations = await asyncio.gather(*tasks)
    return " ".join([t[0]['translation_text'] for t in translations])

# Асинхронная функция для генерации темы текста
async def generate_topic(translated_text):
    topic_summary = await asyncio.to_thread(summarizer, translated_text, max_length=30, min_length=5, do_sample=False)
    return topic_summary[0]['summary_text']

# Асинхронная функция для генерации плана текста
async def generate_plan(translated_text):
    plan_chunks = chunk_text_by_sentence(translated_text, max_chunk_size=1024)
    plan_points = []
    for chunk in plan_chunks:
        plan_point = await asyncio.to_thread(summarizer, chunk, max_length=30, min_length=5, do_sample=False)
        plan_points.append(plan_point[0]['summary_text'])
    return plan_points

if __name__ == "__main__":
    uvicorn.run("server:app", reload=True, host = "192.168.3.10", port=1234)
