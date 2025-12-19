import { useState } from 'react'

function App() {

  // State to store all messages
  const [messages, setMessages] = useState([
    { text: 'Welcome! How can I help you today?', sender: 'system' }
  ])
  
  // State to store the current input value
  const [inputValue, setInputValue] = useState('')

  // Function to handle sending a message
  const handleSendMessage = (e) => {
    e.preventDefault() // Prevent page refresh on form submit
    
    // Don't send empty messages
    if (inputValue.trim() === '') return
    
    // Add user message to the messages array
    setMessages([...messages, { text: inputValue, sender: 'user' }])
    
    // Clear the input
    setInputValue('')
  }

  return (
    <div className="min-h-screen bg-gray-600 flex flex-col items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full flex flex-col" style={{ height: '600px' }}>
        
        {/* Welcome Header */}
        <div className="bg-black text-white p-4 rounded-t-lg">
          <h1 className="text-2xl font-bold">Welcome to AutoPilot OS</h1>
          <p className="text-white text-sm mt-1">Chat with your email!</p>
        </div>

        {/* Chat Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-red-500 text-white'  // User bubble, text color
                    : 'bg-gray-200 text-gray-800'  // Chat bubble, text color
                }`}
              >
                <p className="text-sm">{message.text}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Input Box */}
        <form onSubmit={handleSendMessage} className="border-t p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              className="bg-black hover:bg-gray-800 text-white font-semibold px-6 py-2 rounded-lg transition"
            >
              Send
            </button>
          </div>
        </form>
      </div>

      {/* Name with other info */}
      <p className="text-white text-sm mt-12">Rikhil Amonkar | CS @ Drexel University</p>

    </div>
  )
}

export default App
