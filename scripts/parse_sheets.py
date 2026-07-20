import os
import re

def parse_sheet_2023(year_sheet: str):
    raw_file_path = os.path.join("data", "official", f"{year_sheet}.txt")
    output_dir = os.path.join("data", "parsed", year_sheet)
    
    if not os.path.exists(raw_file_path):
        print(f"Nie znaleziono pliku: {raw_file_path}")
        return

    os.makedirs(output_dir, exist_ok=True)

    with open(raw_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    main_parts = re.split(r"ZASADY OCENIANIA ROZWIĄZAŃ", content, flags=re.IGNORECASE)
    sheet_text = main_parts[0]
    
    remaining_text = main_parts[1] if len(main_parts) > 1 else ""
    sub_parts = re.split(r"Ocena prac osób ze stwierdzoną dyskalkulią", remaining_text, flags=re.IGNORECASE)
    
    standard_criteria = sub_parts[0]
    dyskalkulia_criteria = sub_parts[1] if len(sub_parts) > 1 else ""

    pattern = r"(Zadanie \d+(?:\.\d+)?\..*?)(?=Zadanie \d+(?:\.\d+)?\.|$)"
    
    sheet_tasks = re.findall(pattern, sheet_text, re.DOTALL | re.IGNORECASE)
    standard_tasks = re.findall(pattern, standard_criteria, re.DOTALL | re.IGNORECASE)
    dyskalkulia_tasks = re.findall(pattern, dyskalkulia_criteria, re.DOTALL | re.IGNORECASE)

    def get_task_id(text):
        match = re.search(r"Zadanie (\d+(?:\.\d+)?)", text, re.IGNORECASE)
        return match.group(1) if match else None

    std_dict = {get_task_id(t): t.strip() for t in standard_tasks if get_task_id(t)}
    dys_dict = {get_task_id(t): t.strip() for t in dyskalkulia_tasks if get_task_id(t)}

    print(f"Rozpoczynam zaawansowane parsowanie arkusza {year_sheet}...")
    
    parsed_count = 0
    for task_text in sheet_tasks:
        task_id = get_task_id(task_text)
        if not task_id:
            continue
            
        task_content = task_text.strip()
        task_criteria = std_dict.get(task_id, "Brak standardowych zasad oceniania.")
        
        main_num = task_id.split('.')[0]
        task_dys = dys_dict.get(task_id, dys_dict.get(main_num, "Stosuje się standardowe zasady oceniania."))

        file_safe_id = task_id.replace('.', '_')

        combined_text = (
            f"=== ARKUSZ: {year_sheet} | ZADANIE {task_id} ===\n\n"
            f"[TREŚĆ ZADANIA]\n{task_content}\n\n"
            f"=========================================\n"
            f"[OFICJALNE ZASADY OCENIANIA CKE]\n{task_criteria}\n\n"
            f"=========================================\n"
            f"[KRYTERIA DLA OSÓB Z DYSKALKULIĄ]\n{task_dys}\n"
        )

        output_file_path = os.path.join(output_dir, f"zadanie_{file_safe_id}.txt")
        with open(output_file_path, "w", encoding="utf-8") as out_f:
            out_f.write(combined_text)
            
        parsed_count += 1

    print(f"Sukces! Podzielono arkusz {year_sheet} na {parsed_count} precyzyjnych plików w: {output_dir}")

if __name__ == "__main__":
    parse_sheet_2023("p2014-grudzien-p")

    