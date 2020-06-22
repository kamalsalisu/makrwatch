# Youtube Search

This project searches and displays the first 200 YouTube videos that match a certain keyword. 

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install [virtuelenv](https://virtualenv.pypa.io/en/latest/installation.html) (if you don't already have it).

```bash
pip install virtualenv
```

Create a new python environment.

```bash
virtualenv venv
```
Activate your environment.
```bash
source venv/bin/activate 
venv\Scripts\activate # For windows users
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the requirements for this project.



```bash
pip install -r requiremenets.txt
```
Add your YouTube API key in settings.py.
```bash
YOUTUBE_API_KEY = ''
```
Ensure you have [redis](https://redis.io/download) running on your system. 

## Usage
Run the development server in one terminal.
```bash
python manage.py runserver 
```
Run the task scheduler in another terminal.
```bash
python manage.py run_huey 
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
