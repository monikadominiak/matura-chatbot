import streamlit as str
import streamlit as st
import base64
from openai import OpenAI
from helpers import find_best_matching_task
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.read()).decode('utf-8')

st.set_page_config(page_title="Matura Chatbot", layout="centered")
st.title("🎓 Autonomiczny Asystent Maturalny")
st.write("Wgraj zdjęcie zadania lub swojego rozwiązania, a system sam rozpozna zadanie w bazie CKE!")

uploaded_file = st.file_uploader("Wgraj zdjęcie rozwiązania lub treści zadania:", type=["png", "jpg", "jpeg"])
user_question = st.text_input("Twoje pytanie:", placeholder="np. Co zrobiłem źle?")

if st.button("Analizuj Autonomicznie ✨"):
    if not uploaded_file or not user_question:
        st.error("Proszę wgrać zdjęcie i zadać pytanie!")
    else:
        with st.spinner("Krok 1/2: Rozpoznaję treść zadania ze zdjęcia..."):
            base64_image = encode_image(uploaded_file)
            
            # --- ETAP 1: Szybki OCR i ekstrakcja intencji zadania ---
            ocr_prompt = (
                "Przepisz bardzo dokładnie treść zadania matematycznego widoczną na zdjęciu "
                "(równania, polecenia, liczby). Jeśli na zdjęciu jest tylko odręczne rozwiązanie, "
                "wyciągnij z niego główne równanie wyjściowe lub treść u góry strony, "
                "która pozwoli zidentyfikować oryginalne zadanie."
            )
            
            ocr_response = client.chat.completions.create(
                model="gpt-4o-mini", # używamy tańszego/szybszego modelu do samego OCR
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": ocr_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ],
                max_tokens=300
            )
            detected_text = ocr_response.choices[0].message.content
            
        with st.spinner("Krok 2/2: Przeszukuję bazę kluczy CKE i przygotowuję odpowiedź..."):
            # --- ETAP 2: Szukanie w plikach txt ---
            cke_context = find_best_matching_task(detected_text)
            
            if not cke_context:
                st.warning("Nie udało mi się jednoznacznie dopasować tego zadania do oficjalnych arkuszy w bazie danych. Odpowiem na podstawie ogólnej wiedzy matematycznej.")
            
            # --- ETAP 3: Generowanie właściwej odpowiedzi ---
            system_prompt = (
                "Jesteś życzliwym mentorem maturalnym. Analizujesz odręczne pismo użytkownika na zdjęciu. "
                "Jeśli w sekcji KONTEKST CKE znajduje się właściwe zadanie i zasady oceniania, "
                "użyj ich jako absolutnego priorytetu do oceny i dawania wskazówek krok po kroku. "
                "Nie podawaj od razu końcowego wyniku, naprowadzaj ucznia pytaniami i wskazówkami."
            )
            
            user_content = f"PYTANIE UŻYTKOWNIKA: {user_question}\n\nTEKST WYKRYTY NA ZDJĘCIU:\n{detected_text}\n\n"
            if cke_context:
                user_content += f"KONTEKST CKE (ZASADY OCENIANIA):\n{cke_context}"
                
            final_response = client.chat.completions.create(
                model="gpt-4o", # Główny model analityczny
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_content},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ],
                max_tokens=1200
            )
            
            st.subheader("📝 Analiza Egzaminatora:")
            st.write(final_response.choices[0].message.content)