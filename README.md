# 📊 Financial News Impact Analyzer

A real-time financial news analysis platform that tracks global financial institutions and their impact on Indian markets using AI-powered sentiment analysis.

## 🌟 Features

- **Real-time News Aggregation**: Fetches latest news from RSS feeds and AI-powered search
- **Sentiment Analysis**: Multi-layered sentiment analysis using VADER, TextBlob, and keyword matching
- **Impact Scoring**: Calculates institution impact scores based on multiple factors
- **Interactive Dashboard**: Beautiful, responsive UI with real-time charts
- **AI Chatbot**: Ask questions about institutions, trends, and market sentiment
- **WebSocket Updates**: Live data updates without page refresh

## 🏗️ Tech Stack

**Backend:**
- Python 3.9+
- Flask & Flask-SocketIO
- SQLite
- Anthropic Claude AI
- NLTK, TextBlob, VADER

**Frontend:**
- HTML5, CSS3, JavaScript (ES6+)
- Chart.js
- Socket.IO Client

## 📋 Prerequisites

- Python 3.9 or higher
- Anthropic API Key ([Get one here](https://console.anthropic.com/))
- Windows/Linux/macOS

## 🚀 Installation & Setup

### Step 1: Clone/Extract the Project
```bash
cd financial-news-bot
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Download NLTK Data (Required for sentiment analysis)

Run Python and execute:
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
```

### Step 5: Configure Environment Variables

1. Copy `.env.example` to `.env`:
```bash
   copy .env.example .env    # Windows
   cp .env.example .env      # Linux/macOS
```

2. Edit `.env` and add your Anthropic API key:
```env
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   SECRET_KEY=your-secret-key-change-this
```

3. Generate a secure secret key (optional but recommended):
```python
   python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 6: Create Required Directories

The application will auto-create these, but you can create them manually:
```bash
mkdir data logs
```

## ▶️ Running the Application

### Method 1: Using run.py (Recommended)
```bash
python run.py
```

### Method 2: Using Flask directly
```bash
cd backend
python app.py
```

### Expected Output:
```
============================================================
  FINANCIAL NEWS IMPACT ANALYZER
============================================================

🚀 Server starting...
📍 URL: http://127.0.0.1:5000
🔧 Environment: development
🐛 Debug Mode: True

⏰ Auto-refresh interval: 1800 seconds

💡 Open your browser and navigate to: http://localhost:5000

============================================================

Performing initial news fetch...
==================================================
Starting news analysis at 2024-12-25 10:30:00
==================================================
...
```

## 🌐 Accessing the Application

Open your browser and navigate to:
```
http://localhost:5000
```

Or:
```
http://127.0.0.1:5000
```

## 🎮 How to Use

### 1. **Initial Load**
- The app automatically fetches news on startup
- Wait 30-60 seconds for initial data processing

### 2. **View Dashboard**
- See market summary and key statistics
- View impact score charts
- Check institution rankings table

### 3. **Refresh Data**
- Click "Refresh Data" button for latest news
- Enable "Auto-Refresh" for automatic updates every 5 minutes

### 4. **Ask Questions**
- Use the AI chatbot to ask about:
  - Specific institutions: "Tell me about JPMorgan"
  - Top performers: "Show me the top institutions"
  - Sentiment: "Which institutions are positive?"
  - India focus: "Which institutions focus on India?"
  - Overview: "Give me a summary"

## ⚙️ Configuration

Edit `.env` file to customize:
```env
# API Configuration
ANTHROPIC_API_KEY=your-key-here

# Server Settings
HOST=127.0.0.1              # Use 0.0.0.0 for network access
PORT=5000

# Refresh Intervals
NEWS_REFRESH_INTERVAL=1800  # 30 minutes (in seconds)
QUICK_REFRESH_INTERVAL=300  # 5 minutes

# Logging
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
```

## 📁 Project Structure
```
financial-news-bot/
├── backend/
│   ├── __init__.py
│   ├── app.py                  # Main Flask application
│   ├── config.py               # Configuration
│   ├── database.py             # Database operations
│   ├── news_scraper.py         # News fetching
│   ├── sentiment_analyzer.py   # Sentiment analysis
│   └── impact_calculator.py    # Impact scoring
├── frontend/
│   ├── index.html              # Main HTML
│   ├── css/
│   │   └── style.css          # Styles
│   └── js/
│       ├── main.js            # Main logic
│       ├── chart.js           # Charts
│       └── websocket.js       # WebSocket
├── data/                       # Database storage
├── logs/                       # Log files
├── venv/                       # Virtual environment
├── .env                        # Environment variables
├── .env.example               # Environment template
├── requirements.txt           # Dependencies
├── run.py                     # Entry point
└── README.md                  # This file
```

## 🐛 Troubleshooting

### Issue: "ANTHROPIC_API_KEY is required"
**Solution:** Make sure you've set your API key in the `.env` file

### Issue: "Module not found"
**Solution:** 
```bash
pip install -r requirements.txt
```

### Issue: "Port 5000 already in use"
**Solution:** Change PORT in `.env` file:
```env
PORT=8000
```

### Issue: "Database locked"
**Solution:** 
```bash
# Delete the database and restart
rm data/news_cache.db
python run.py
```

### Issue: NLTK download errors
**Solution:**
```python
import nltk
nltk.download('all')
```

### Issue: Can't access from other devices
**Solution:** Change HOST in `.env`:
```env
HOST=0.0.0.0
```
Then access via: `http://YOUR_IP:5000`

## 📊 API Endpoints

### GET `/api/news`
Get latest news analysis (cached for 5 minutes)

### POST `/api/refresh`
Force refresh news data

### GET `/api/status`
Get system status

### POST `/api/chat`
Send message to AI chatbot

### GET `/api/health`
Health check endpoint

## 🔒 Security Notes

### For Production Deployment:

1. **Change SECRET_KEY** to a secure random value
2. **Restrict CORS** origins in `app.py`
3. **Use HTTPS** with proper SSL certificates
4. **Set DEBUG=False** in production
5. **Use environment variables** for all secrets
6. **Implement rate limiting** on API endpoints
7. **Add authentication** for admin features

## 🚀 Production Deployment

### Using Gunicorn (Recommended):
```bash
pip install gunicorn

gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 backend.app:app
```

### Using Docker:

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

Build and run:
```bash
docker build -t financial-news-bot .
docker run -p 5000:5000 --env-file .env financial-news-bot
```

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Support

For issues and questions:
- Check the troubleshooting section
- Review logs in `logs/app.log`
- Check console output for errors

## 🎯 Roadmap

- [ ] Add more news sources
- [ ] Implement user authentication
- [ ] Add historical data visualization
- [ ] Email alerts for significant changes
- [ ] Mobile app
- [ ] Multi-language support

## ⚠️ Disclaimer

This tool is for informational purposes only. Not financial advice. Always do your own research before making investment decisions.

---

**Made by ❤️ Om Kapale**