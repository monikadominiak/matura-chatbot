const API_URL = "http://127.0.0.1:8000";

export async function analyze(image, question) {

    const formData = new FormData();

    formData.append(
        "question",
        question
    );


    if(image){
        formData.append(
            "image",
            image
        );
    }


    const response = await fetch(
        `${API_URL}/analyze`,
        {
            method:"POST",
            body:formData
        }
    );


    if(!response.ok){
        throw new Error(
            "Błąd serwera"
        );
    }


    return await response.json();
}