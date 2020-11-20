## Running the Application

### Setting up Virtual Environment
```bash
python -m venv venv     # Create Virtual Environment
source venv/bin/activate    # Activate the Virtual Environment
```

### Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### Export Environment Variables
```bash
export $(grep -v '^#' .env | xargs)
```

### Running the application
```bash
flask run
```
