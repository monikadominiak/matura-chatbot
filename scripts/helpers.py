import os
import re

def find_best_matching_task(detected_text: str) -> str:
    """
    Przeszukuje wszystkie pliki .txt w poszukiwaniu zadania, które zawiera 
    słowa kluczowe lub równania wykryte przez OCR na zdjęciu.
    """
    folder_path = os.path.join("data", "official")
    best_context = ""
    max_matches = 0
    

    search_terms = [term.strip() for term in re.split(r'[ ,.\n]+', detected_text) if len(term.strip()) > 3]

    if not os.path.exists(folder_path):
        return ""

    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".txt"):
            continue
            
        with open(os.path.join(folder_path, file_name), "r", encoding="utf-8") as f:
            content = f.read()
            
        tasks = re.split(r'(?=Zadanie \d+\.)', content)
        
        for task_chunk in tasks:
            matches = sum(1 for term in search_terms if term.lower() in task_chunk.lower())
            
            if matches > max_matches and matches > 2:  # minimum 3 pasujące słowa/symbole
                max_matches = matches
                best_context = task_chunk

    if best_context:
        return f"\n--- DOPASOWANE ZADANIE I KLUCZ Z BAZY CKE ---\n{best_context.strip()}\n"
    return ""