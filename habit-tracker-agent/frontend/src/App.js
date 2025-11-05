import React, { useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  const sendMessage = async () => {
    if (!message) return;

    const newChatHistory = [...chatHistory, { role: "user", text: message }];
    setChatHistory(newChatHistory);
    setMessage("");

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });
      const data = await response.json();
      setChatHistory([
        ...newChatHistory,
        { role: "agent", text: data.response },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      setChatHistory([
        ...newChatHistory,
        { role: "agent", text: "Sorry, something went wrong." },
      ]);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Habit Tracker Agent</h1>
      </header>
      <div className="chat-container">
        <div className="chat-history">
          {chatHistory.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              {msg.text}
            </div>
          ))}
        </div>
        <div className="chat-input">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Type your message..."
          />
          <button onClick={sendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;
