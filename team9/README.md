# Team 9 - Tick-8 Vocabulary Microservice

Vocabulary learning microservice using the **Tick-8** method

## 📝 Description

This microservice is a vocabulary learning system based on Spaced Repetition with the Tick-8 algorithm that helps users effectively learn English vocabulary and store it in long-term memory.

## 🎯 Key Features

- ✅ Create and manage vocabulary lessons
- ✅ Add words to lessons
- ✅ Word review system with Tick-8 algorithm
- ✅ Progress tracking and learning statistics
- ✅ Personalized user dashboard

## 🔧 Technologies

### Backend
- Django 5.2+
- Django REST Framework
- SQLite Database
- JWT Authentication

### Frontend
- React 18+
- React Router
- Vite
- CSS3

## 🚀 Quick Start

### With Docker (Recommended)

```powershell
# In project root
.\win_scripts\up-team.ps1
# Then enter Team Number: 9
```

The service will be available at:
- Frontend: http://localhost:9141/team9/
- API: http://localhost:8000/team9/api/

### Without Docker

1. **Backend:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate --database=team9

# Seed sample data
python team9/quick_seed.py

# Run server
python manage.py runserver
```

2. **Frontend:**
```bash
cd team9/frontend
npm install
npm run dev
```

## 📚 API Documentation

### Main Endpoints

#### Lessons
- `GET /team9/api/lessons/` - List all lessons
- `POST /team9/api/lessons/` - Create new lesson
- `GET /team9/api/lessons/{id}/` - Retrieve lesson details
- `PUT /team9/api/lessons/{id}/` - Update lesson
- `DELETE /team9/api/lessons/{id}/` - Delete lesson

#### Words
- `GET /team9/api/words/` - List all words
- `POST /team9/api/words/` - Add new word
- `GET /team9/api/words/{id}/` - Retrieve word details
- `PUT /team9/api/words/{id}/` - Update word
- `DELETE /team9/api/words/{id}/` - Delete word
- `POST /team9/api/words/{id}/review/` - Review word

#### Dashboard
- `GET /team9/api/dashboard/` - User dashboard stats and information

### Query Parameters

#### Filtering
```
# Filter words by lesson
GET /team9/api/words/?lesson=1

# Filter learned words
GET /team9/api/words/?is_learned=true

# Words due for review today
GET /team9/api/words/?today_review=true
```

#### Searching
```
# Search in lesson title and description
GET /team9/api/lessons/?search=business

# Search in words (English and Persian)
GET /team9/api/words/?search=accomplish
```

#### Ordering
```
# Sort lessons
GET /team9/api/lessons/?ordering=-created_at

# Sort words
GET /team9/api/words/?ordering=next_review_date
```

## 🎮 How to Use

### For Users

1. **Create Lesson:** From the main page, click "Add New Lesson"
2. **Add Words:** Enter a lesson and add new words
3. **Daily Review:** In the dashboard, see words that need to be reviewed today
4. **Evaluate:** After reviewing each word, mark its learning status

### Tick-8 Algorithm

Words are reviewed in 8 stages:
- Day 0: Initial learning
- Day 1: Review next day
- Day 2: Two days later
- Day 4: Four days later
- Day 8: Eight days later
- And so on until day 128

## 📊 Database Structure

### Models

#### Lesson
```python
- id: Integer (Primary Key)
- title: String (lesson title)
- description: Text (description)
- user_id: Integer (user ID)
- created_at: DateTime
```

#### Word
```python
- id: Integer (Primary Key)
- term: String (English word)
- definition: String (Persian meaning)
- lesson: ForeignKey (lesson relation)
- current_day: Integer (current learning stage 0-8)
- is_learned: Boolean
- next_review_date: Date (next review date)
- created_at: DateTime
```

## 🛠️ Utility Tools

### Reset Database
```bash
# Windows
.\team9\reset_database.bat

# Linux/Mac
./team9/reset_database.sh
```

### Quick Seed
```bash
python team9/quick_seed.py
```

This script creates 5 sample lessons and 12 words.

## 📁 File Structure

```
team9/
├── frontend/               # React Application
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Main pages
│   │   ├── services/      # API services
│   │   └── config.js      # API configuration
│   └── public/
├── templates/             # Django Templates
├── static/                # Static files
├── migrations/            # Database migrations
├── models.py              # Database models
├── views.py               # API Views
├── serializers.py         # DRF Serializers
├── filters.py             # Custom filters
├── urls.py                # URL routing
├── docker-compose.yml     # Docker configuration
├── Dockerfile             # Docker build
└── quick_seed.py          # Seed script

```

## 🔐 Authentication

This microservice uses the project's central JWT Authentication system. Tokens are automatically stored and sent in cookies.

## 🐛 Troubleshooting

### Common Issues

1. **Database tables don't exist:**
```bash
python manage.py migrate --database=team9
python team9/quick_seed.py
```

2. **CORS error:**
- Make sure `CORS_ALLOWED_ORIGINS` is properly configured in settings

3. **404 error in API:**
- Check the URL: `/team9/api/...`
- Make sure the core container is running

## 👥 Development Team

- Group 9
- Course: Software Engineering
- Semester: 1404-01

## 📝 Changelog

### Current Version
- ✅ Full REST API implementation
- ✅ React Frontend with Vite
- ✅ Docker support
- ✅ Dashboard and statistics
- ✅ Tick-8 algorithm

## 📞 Support

To report bugs or request new features, use the Issues section on GitHub.

---

**Note:** For more detailed information about setup and database synchronization, please refer to `SETUP_GUIDE.md` and `DATABASE_SYNC_GUIDE.md` files.
