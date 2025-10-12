import React, { useState, useRef, useEffect } from "react";
import "./App.css";

const UploadIcon = () => (
  <svg
    className="upload-icon"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    strokeWidth={1.5}
    stroke="currentColor"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M12 16.5V9.75m0 0l-3.75 3.75M12 9.75l3.75 3.75M3 17.25V19.5a2.25 2.25 0 002.25 2.25h13.5A2.25 2.25 0 0021 19.5v-2.25"
    />
  </svg>
);

const TypingLoader = () => (
  <div className="loader-container">
    <div className="typing-indicator">
      <span></span>
      <span></span>
      <span></span>
    </div>
  </div>
);

function App() {
  const [message, setMessage] = useState("");
  const [file, setFile] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef(null);
  const chatHistoryRef = useRef(null);

  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [chatHistory, isLoading]);

  const handleSendMessage = async () => {
    if (!file) {
      alert("Please upload a file first.");
      return;
    }
    if (!message.trim()) {
      alert("Please enter a message to continue.");
      return;
    }

    const userMessage = message;
    setChatHistory((prev) => [...prev, { type: "user", text: userMessage }]);
    setMessage("");
    setIsLoading(true);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("message", userMessage);
    formData.append("user_id", "react-user");
    formData.append("session_id", "react-session");

    try {
      const response = await fetch("http://localhost:8001/chat", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setChatHistory((prev) => [
          ...prev,
          { type: "bot", text: data.responses[0] },
        ]);
      } else {
        const errorText = await response.text();
        console.error("Error sending message:", response.statusText, errorText);
        setChatHistory((prev) => [
          ...prev,
          { type: "bot", text: `Error: ${response.statusText}` },
        ]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setChatHistory((prev) => [
        ...prev,
        { type: "bot", text: "Error: Could not connect to the server." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current.click();
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
    }
  };

  return (
    <div className="App">
      <div className="sidebar">
        <div className="file-upload-container">
          <h2 className="file-upload-title">FILE UPLOAD</h2>
          <div
            className={`file-drop-area ${isDragging ? "drag-over" : ""}`}
            onClick={handleBrowseClick}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <UploadIcon />
            <button type="button" className="browse-button">
              Browse Files
            </button>
            <p className="file-info">
              {file
                ? `Selected: ${file.name}`
                : "Accepted Formats: .csv, .json, .xlsx"}
            </p>
          </div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: "none" }}
            accept=".csv,.json,.xlsx"
          />
        </div>
      </div>
      <div className="chat-main">
        <div className="chat-history" ref={chatHistoryRef}>
          {chatHistory.length === 0 && !isLoading && (
            <div className="bot-message">
              Hello! Please upload a CSV, JSON, or XLSX file and ask a question
              to begin.
            </div>
          )}
          {chatHistory.map((msg, index) => (
            <div
              key={index}
              className={msg.type === "user" ? "user-message" : "bot-message"}
            >
              {msg.text}
            </div>
          ))}
          {isLoading && <TypingLoader />}
        </div>
        <div className="chat-input-area">
          <div className="message-input-container">
            <input
              type="text"
              className="message-input"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Type your message..."
              disabled={!file || isLoading}
            />
            <button
              className="send-button"
              onClick={handleSendMessage}
              disabled={!file || isLoading}
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
