
# Roomio 
Affan Khamse (ak10529) & Abijith Pradeep (ap8246) 
 

# Work history

- Affan
  - Worked on HomePage
  - session handling
  - searching for unit based on company name and  building name 
  - Favorite feature
  - feature to apply min and max rent
  - View Detail of unit along with pet policy of that apartment building
  - View Interest and create Interest
    
- Abijith
  - Did the User Login & SignUp
  - User Profile
  - Pet Add/Edit functionality
  - Searching apartment based on interest
  - Getting Average value based on zip code
  - feature to apply min and max rent filter on search


## Project Setup Instructions

This guide will walk you through setting up a Python virtual environment and installing the necessary dependencies for your project.

### Step 1: Install virtualenv

Before creating a virtual environment, you need to ensure that `virtualenv` is installed on your system. You can install it using pip, the Python package installer. Open a terminal or command prompt and execute the following command:

```bash
pip install virtualenv
```

### Create virtual env
```bash
virtualenv projectenv
```

### Activate the Virtual Environment

On Windows:
```bash
source projectenv/Scripts/activate
```

On Mac:
```bash
source projectenv/bin/activate
```

### Install required packages
```terminal
pip install -r requirements.txt
```

### Using dotenv to manage environment variables

To manage your application's environment variables more securely and conveniently, you can use the `python-dotenv` package. This allows you to load environment variables from a `.env` file into your project. Here’s how you can set it up:

1. Install `python-dotenv` using pip:
   ```bash
   pip install python-dotenv
   

2. Create a `.env` file in the root of your project directory. Add your environment variables to this file. For example:
   ```plaintext
   DB_NAME=dmname
   DB_USER=usrname
   DB_PASSWORD=pwd
   DB_HOST=host
   DB_PORT=8000 #can be any

3. Load the environment variables from the `.env` file in your project. Make sure to do this early in your application's startup. For a Django project, you can do this in the `settings.py` file:
   ```python
   from dotenv import load_dotenv
   import os

   load_dotenv()  # This loads the environment variables from the .env file.

   # Now you can use os.getenv to access your environment variables.
   DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    },
   }

By following these steps, you ensure that your sensitive information and configuration are not hardcoded into your application's source code, providing an additional layer of security.

The insert statements are provided in Important_notes.pdf

# DB screenshot:
![image](https://github.com/abijith-pradeep/Roomio/assets/60337745/97e7adb8-6f3f-47d1-bb3e-1216f7f5b98d)

![image](https://github.com/abijith-pradeep/Roomio/assets/60337745/f5aa4caa-241f-4e3e-968a-f074b77264b9)

![image](https://github.com/abijith-pradeep/Roomio/assets/60337745/640810f9-df53-4824-a780-d9714ec4b41b)

## List of tables:
![image](https://github.com/abijith-pradeep/Roomio/assets/60337745/a4e80716-bff7-48a0-8e67-7fd336981365)

## Homescreen only listing User interest from Interest Table, 
![image](https://github.com/abijith-pradeep/Roomio/assets/60337745/7b23615e-0489-496e-88df-07633ede7c7c)

## Login and Signup
![image](https://github.com/abijith-pradeep/Roomio/assets/60337745/9278d2e5-fc14-4dd3-81dc-735b0e38d489)

![image](https://github.com/abijith-pradeep/Roomio/assets/60337745/708fecdb-1bf7-4cb2-89a0-caebc261991b)

