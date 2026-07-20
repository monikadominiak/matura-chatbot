import { useState, useEffect } from "react";
import { analyze } from "./api";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import "./App.css";

function App() {

  const [image, setImage] = useState(null);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);


  const [messages, setMessages] = useState(() => {

    const saved = localStorage.getItem(
      "matura-chat-history"
    );

    return saved
      ? JSON.parse(saved)
      : [];

  });


  useEffect(() => {

    localStorage.setItem(
      "matura-chat-history",
      JSON.stringify(messages)
    );

  }, [messages]);



  async function handleSubmit(e) {

    e.preventDefault();



    if (!question.trim()) {
      alert("Wpisz pytanie.");
      return;
    }


    const imageUrl = image
      ? URL.createObjectURL(image)
      : null;


    const userMessage = {
      sender: "user",
      image: imageUrl,
      question: question
    };


    setMessages(prev => [
      ...prev,
      userMessage
    ]);


    setLoading(true);



    try {

      const result = await analyze(
        image,
        question
      );


      const botMessage = {
        sender: "bot",
        answer: result.answer
      };


      setMessages(prev => [
        ...prev,
        botMessage
      ]);


      setQuestion("");
      setImage(null);


    } catch(err) {

      console.error(err);


      setMessages(prev => [
        ...prev,
        {
          sender:"bot",
          answer:
          "Wystąpił błąd podczas komunikacji z serwerem."
        }
      ]);

    }


    setLoading(false);

  }



  function clearHistory(){

    localStorage.removeItem(
      "matura-chat-history"
    );

    setMessages([]);

  }



return (

<div className="app">


<header className="header">

    <h1>
      📚 Matura Chatbot
    </h1>


    {messages.length > 0 && (

      <button
        className="clear-button"
        onClick={clearHistory}
      >
        Wyczyść historię
      </button>

    )}

</header>



<div className="chat">


{
messages.length === 0 &&

<div className="bot-message welcome">

Cześć!

<br/><br/>

Prześlij zdjęcie rozwiązania zadania maturalnego.
Sprawdzę je według kryteriów CKE.

</div>

}



{
messages.map((msg,index)=>(


<div
key={index}
className={
msg.sender==="user"
?
"user-message"
:
"bot-message"
}
>


{
msg.sender==="user" && msg.image &&

<img
className="solution-image"
src={msg.image}
alt="solution"
/>

}



{
msg.sender==="user" &&

<p>
{msg.question}
</p>

}



{
msg.sender==="bot" &&

<div className="markdown-body">
  <ReactMarkdown
    remarkPlugins={[remarkMath]}
    rehypePlugins={[rehypeKatex]}
  >
    {msg.answer}
  </ReactMarkdown>
</div>

}



</div>


))

}



{
loading &&

<div className="bot-message">

Analizuję rozwiązanie...

</div>

}


</div>




<form onSubmit={handleSubmit}>


<input
type="file"
accept="image/*"
onChange={
e=>setImage(e.target.files[0])
}
/>



<textarea

placeholder=
"Np. Dlaczego ten krok jest błędny?"

value={question}

onChange={
e=>setQuestion(e.target.value)
}

/>


<button>
Wyślij
</button>


</form>



</div>


);


}


export default App;