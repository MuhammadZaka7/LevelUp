![Python](https://img.shields.io/badge/Python-3.14-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED)
![License](https://img.shields.io/badge/License-MIT-yellow)

# LevelUp - Gamified Employee Performance Tracker

A REST API system that gamifies employee performance tracking using XP, levels, and leaderboards. Built with Flask, PostgreSQL, and Docker.

## 🎮 Features

- **XP System**: Employees earn experience points based on task completion, quality scores, and punctuality
- **10-Level Progression**: From Rookie (Level 1) to Grandmaster (Level 10)
- **Automatic Leveling**: Employees automatically level up when reaching XP thresholds
- **Dynamic Leaderboards**: Global and department-specific rankings
- **Performance Metrics**: Quality scores (1-5 stars) and punctuality bonuses
- **Task History**: Track all completed tasks per employee
- **Statistics Dashboard**: System-wide analytics and insights

## 🏗️ Architecture
```
├── Flask REST API (Python)
├── PostgreSQL Database (Dockerized)
│   ├── employees table
│   ├── tasks table
│   └── levels table
└── Docker Container Management
```

## 📊 XP Calculation Formula
```
XP Earned = Base XP × Quality Multiplier × Punctuality Multiplier

- Base XP: 10 points per task
- Quality Multiplier: (score / 2.5) → 1.0x to 2.0x
- Punctuality Multiplier: 1.5x if on-time, 1.0x if late
```

**Examples:**
- Perfect task (5.0 quality, on-time): 10 × 2.0 × 1.5 = **30 XP**
- Good task (4.0 quality, on-time): 10 × 1.6 × 1.5 = **24 XP**
- Average task (3.0 quality, late): 10 × 1.2 × 1.0 = **12 XP**

## 🎯 Level Progression

| Level | XP Required | Rank Title    |
|-------|-------------|---------------|
| 1     | 0           | Rookie        |
| 2     | 100         | Apprentice    |
| 3     | 250         | Contributor   |
| 4     | 500         | Professional  |
| 5     | 1,000       | Expert        |
| 6     | 2,000       | Master        |
| 7     | 4,000       | Elite         |
| 8     | 8,000       | Champion      |
| 9     | 15,000      | Legend        |
| 10    | 30,000      | Grandmaster   |

## 🚀 API Endpoints

### Employees

**GET /employees**
- Get all employees with current levels and XP

**POST /employees**
- Create new employee
- Required: `name`, `email`
- Optional: `department`, `hire_date`

**GET /employees/{id}**
- Get specific employee details

**GET /employees/{id}/tasks**
- Get employee's complete task history

### Tasks

**POST /tasks**
- Log a completed task
- Required: `employee_id`, `task_name`
- Optional: `quality_score` (1.0-5.0), `was_on_time` (boolean)
- Returns: XP earned and whether employee leveled up

### Leaderboards

**GET /leaderboard**
- Global leaderboard ranked by total XP

**GET /leaderboard/{department}**
- Department-specific leaderboard
- Example: `/leaderboard/Engineering`

### Statistics

**GET /stats**
- System overview: total employees, tasks completed, averages, top performer, department breakdown

## 🛠️ Tech Stack

- **Backend**: Flask 3.1.2 (Python)
- **Database**: PostgreSQL 15
- **Containerization**: Docker
- **Database Driver**: psycopg3

## 📦 Setup & Installation

### Prerequisites
- Docker
- Python 3.14+
- Arch Linux (or any Linux distro)

### 1. Start PostgreSQL Container
```bash
docker run --name levelup-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=levelup2026 \
  -e POSTGRES_DB=levelup \
  -p 5432:5432 \
  -v levelup-data:/var/lib/postgresql/data \
  -d postgres:15
```

### 2. Install Dependencies
```bash
pip install Flask python-dotenv "psycopg[binary]"
```

### 3. Configure Database

Edit `config.py` with your database credentials.

### 4. Run the API
```bash
python app.py
```

API will be available at `http://localhost:5000`

## 📝 Example Usage

### Create an Employee
```bash
curl -X POST http://localhost:5000/employees \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@company.com",
    "department": "Engineering"
  }'
```

### Log a Task
```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "task_name": "Deploy new feature",
    "quality_score": 5.0,
    "was_on_time": true
  }'
```

Response:
```json
{
  "task": {
    "id": 1,
    "employee_id": 1,
    "task_name": "Deploy new feature",
    "xp_earned": 30
  },
  "xp_earned": 30,
  "leveled_up": false
}
```

### View Leaderboard
```bash
curl http://localhost:5000/leaderboard
```

## 🎯 Use Cases

- **Businesses**: Track employee performance with engaging gamification
- **Teams**: Foster healthy competition and motivation
- **Managers**: Data-driven insights into team productivity
- **HR**: Objective performance metrics for reviews

## 🔮 Future Enhancements

- [ ] Achievements & Badges system
- [ ] Streak tracking (consecutive days)
- [ ] Team challenges
- [ ] Frontend dashboard (React)
- [ ] Real-time WebSocket updates
- [ ] Email notifications for level-ups
- [ ] Export reports (PDF/CSV)
- [ ] Mobile app integration

## 👨‍💻 Developer

Built by **[Your Name]** as part of a homelab project.

- Location: Elmont, New York
- Certifications: Network+ (in progress), Security+ (planned)
- Other projects: Palo Alto Network Security Fundamentals, Python (Scrimba), TryHackMe Cybersecurity 101

## 📄 License

This project is open source and available for educational purposes.

---

**LevelUp** - Making performance tracking engaging, one XP at a time. 🎮
