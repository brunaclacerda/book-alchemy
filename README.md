# BookAlchemy

## Setup

Install the required packages:

```powershell
pip install -r requirements.txt
```

Create the database tables once:

```powershell
python -c "from app import app; from setup import db; app.app_context().push(); db.create_all()"
```

Start the application:

```powershell
python app.py
```
