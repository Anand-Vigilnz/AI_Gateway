# AI Gateway – Secure Chat Application

**Purpose:**  
Standalone chat application (Python + Streamlit) that scans user queries through the **Prompt Security Gateway (Rproxy)** and sends safe requests directly to **OpenAI LLM**. All messages are scanned for security threats before reaching the LLM.

---

## Features

- **💬 Simple Chat Interface** - Clean, conversational UI for chatting with AI
- **🛡️ Security Scanning** - All messages go through Rproxy for threat detection
- **🤖 Direct OpenAI Integration** - Safe messages sent directly to OpenAI (no database dependency)
- **📊 Security Status** - Visual indicators for allowed/blocked messages
- **⚠️ Threat Details** - Expandable threat information for blocked messages
- **⚙️ .env Configuration** - Easy configuration via environment variables
- **🔄 Chat History** - Persistent conversation history during session
- **📈 Performance Metrics** - Latency and status code display for each message

---

## Architecture

### Flow Diagram

```
User Input → Rproxy (Security Scan) → If Safe → OpenAI LLM → Response to UI
                              ↓
                         If Blocked → Show Threats
```

### How It Works

1. **User sends message** → Added to chat history
2. **Security Scan** (if Rproxy configured) → Message sent to Rproxy for threat detection
   - **If Blocked** → Display blocked message with threat details
   - **If Allowed** → Proceed to OpenAI
   - **If Rproxy not configured** → Skip scan, proceed directly to OpenAI
3. **Send to OpenAI LLM** → Message sent to OpenAI API
4. **LLM Response** → Display response in chat interface

---

## Project Structure

- `main.py` – Main Streamlit chat application
- `config.py` – Configuration loader for .env file
- `.env.example` – Template for environment variables
- `requirements.txt` – Python dependencies
- `legacy/` – Previous version files (database-dependent)

---

## Installation

1. Create and activate a virtual environment (recommended):

```bash
cd "AI Gateway"
python -m venv .venv
.\.venv\Scripts\activate  # Windows PowerShell
# or
source .venv/bin/activate  # Linux/Mac
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values
# - RPROXY_URL: Your Rproxy gateway URL
# - RPROXY_AUTH_HEADER: Your Rproxy API key
# - OPENAI_API_KEY: Your OpenAI API key
# - DEFAULT_MODEL: Default OpenAI model (optional)
```

4. Run the application:

```bash
streamlit run main.py
```

---

## Configuration

### Environment Variables (.env file)

#### Required Variables

1. **OPENAI_API_KEY** (required)
   - Your OpenAI API key for LLM requests
   - Get your API key from: https://platform.openai.com/api-keys
   - Format: `sk-...`

#### Optional Variables

2. **RPROXY_URL** (optional)
   - The URL of your Prompt Security Gateway (Rproxy)
   - Example: `https://devaigw.vigilnz.com/`
   - Default: `https://devaigw.vigilnz.com/`
   - If not set, security scanning will be skipped and messages sent directly to OpenAI

3. **RPROXY_AUTH_HEADER** (optional)
   - API key for Rproxy authentication
   - Format: `vpsk_live_{entityId}{random}` or `Bearer vpsk_live_...`
   - Entity ID will be automatically extracted from the API key
   - If not set, security scanning will be skipped

4. **DEFAULT_MODEL** (optional)
   - Default OpenAI model to use if not specified in UI
   - Examples: `gpt-4o-mini`, `gpt-4`, `gpt-3.5-turbo`
   - Default: `gpt-4o-mini`

### Rproxy Configuration

**Note:** Rproxy configuration is optional. If `RPROXY_URL` or `RPROXY_AUTH_HEADER` is not set:
- The chatbot will work without security scanning
- Messages will be sent directly to OpenAI
- A warning will be displayed indicating that Rproxy is not configured
- This is useful for development or when security scanning is not needed

---

## Usage

### Starting the Application

1. Ensure your `.env` file is configured with all required variables
2. Run: `streamlit run main.py`
3. Open your browser to the URL shown in the terminal (usually `http://localhost:8501`)

### Using the Chat Interface

1. **Configure Settings** (Sidebar):
   - Set Rproxy URL (for security scanning)
   - Set Rproxy API Key
   - Set OpenAI Model Name

2. **Send Messages**:
   - Type your message in the chat input
   - Message is automatically scanned by Rproxy
   - If safe, sent to OpenAI and response displayed
   - If blocked, threat details are shown

3. **View Details**:
   - Click "Raw Request/Response Payload" to see full API requests/responses
   - View threat details for blocked messages
   - Check latency and status for each message

---

## Security Features

- **Automatic Threat Detection**: All messages scanned before reaching LLM
- **Threat Details**: Detailed information about detected threats
- **Blocked Messages**: Malicious messages are blocked and never sent to LLM
- **Secure API Keys**: API keys stored in `.env` file (not in code)

---

## Troubleshooting

### "Authorization header is required"
- Ensure `RPROXY_AUTH_HEADER` is set in your `.env` file
- Check that your API key format is correct: `vpsk_live_...`

### "OpenAI API key is required"
- Ensure `OPENAI_API_KEY` is set in your `.env` file
- Verify your API key is valid at https://platform.openai.com/api-keys

### "Entity ID could not be extracted"
- Check that your Rproxy API key follows the format: `vpsk_live_{entityId}{random}`
- The entity ID should be 24 hex characters after `vpsk_live_`

### Connection Errors
- Verify your Rproxy URL is correct and accessible
- Check your network connection
- Ensure Rproxy service is running

---

## Differences from Legacy Version

This version differs from the legacy version in the following ways:

1. **No Database Dependency**: LLM configuration is in the app, not in a database
2. **Direct OpenAI Integration**: Messages sent directly to OpenAI after scanning
3. **Two-Step Flow**: Scan first, then LLM (instead of Rproxy forwarding)
4. **Simplified Architecture**: Removed entity/target lookup logic

---

## Requirements

- Python 3.8+
- Streamlit 1.40.0+
- requests 2.32.3+
- python-dotenv 1.0.0+

---

## License

This is a standalone application for secure AI chat interactions.

---

## Author

Anand S

Date: 2025-12-16

