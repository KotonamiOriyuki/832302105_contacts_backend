# Backend of Contacts System

---

832302105_contacts_backend

This is the first assignment of Software Engineering of Maynooth International Engineering College, Fuzhou University.

## Basic Features

---
* Provides standard RESTful API style.
* Support Create, Edit, Delete, Get features of contacts
* Extend functions provided (User login, Add Friends)

## Technical Stack

---
* Database: MongoDB (pymongo lib)
* Engine: FastAPI
* Server Launcher: Uvicorn
* Middleware: CORS

## Other Requirements

---
* Git or Github Desktop
* MongoDB Community Edition
* Python 3.9

## Deploy to Local Machine

---
### 1. Clone the code
> git clone xxx\
> cd xxx

Alternatively, you can download the .zip file of this git repo.
### 2. Create a new environment (suggested)
Anaconda/Miniconda/Conda
> conda env create -name {customEnvName}

Virtual Environment (venv)
> python -m venv venv

### 3. Install dependencies
Anaconda/Miniconda/Conda
> conda install -r requirements.txt

venv
> pip install -r requirements.txt

### 4. Launch
Anaconda/Miniconda/Conda
> conda src/main.py

venv
> python src/main.py

## Access the Backend Locally

---
The default backend address is 
> http://0.0.0.0:8000/

You can modify `src/main.py`, Line 21 to 22:
> host='0.0.0.0'\
> port=8000

To change the default settings.

# Appendix

---
## File Structure

---
> Controller\
> ├ \_\_init__.py   // default python package file\
> └ controller.py   // handle API calls from the frontend\
> models\
> ├ \_\_init__.py   // default python package file\
> └ model.py   // contains all templates type supported, which is sent by the frontend\
> src\
> └ main.py // middleware settings and uvicorn launcher
