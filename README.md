## 1. Klonowanie repozytorium

```bash
git clone https://github.com/monikadominiak/matura-chatbot.git
cd matura-chatbot
```

---

## 2. Utworzenie środowiska wirtualnego

Windows:

```bash
python -m venv .venv
```

Aktywacja:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Instalacja bibliotek

```bash
pip install -r requirements.txt
```

---

## 4. Konfiguracja OpenAI

W pliku

```
.env
```

 wpisz

```text
OPENAI_API_KEY=twój_klucz_api
```

---

# Embeddingi

Repozytorium zawiera już wygenerowane embeddingi ChromaDB.

Jeżeli zostaną dodane nowe zadania do bazy wiedzy, embeddingi można przebudować poleceniem:

```bash
python -m scripts.build_embeddings
```

---

# Backend

W katalogu głównym projektu:

```bash
uvicorn backend.app.main:app --reload
```

```
http://127.0.0.1:8000
```

Dokumentacja Swagger:

```
http://127.0.0.1:8000/docs
```

---

# Frontend

```bash
cd frontend
```

```bash
npm install
```


```bash
npm run dev
```


```
http://localhost:5173
```

---

