<div class="#readme-top"></div>
<br />
<div align="center">
  <h3 align="center">E - LibDeck</h3>
  <p align="center">
    An E-Library Management System built with django
    <br />
  </p>
</div>



<!-- TABLE OF CONTENTS -->

## Getting Started

To get the project up and running in your local machine, look at the pre-requisites and head on to installation

### Prerequisites

Setup all the requirements:
* `pip install django`
* `pip install google-api-python-client`
* `pip install rapidfuzz`
* `pip install openpyxl`
* `pip install python-dotenv`

### Installation

* Clone the project on your local machine
* Go to <a href="https://console.cloud.google.com/">Google Cloud Console</a> and create your Oauth 2.0 Client
* Change the Client ID in libdeck/mysite/.env with that of your application
* In Cloud console, change your redirect URI to `http://localhost:8000/auth-receiver`
* Change the auth-receiver function in `views.py` to authorize other email domains

## Usage

To get the project running, follow these steps:
* In a terminal, cd into `libdeck` and run `python manage.py runserver`
* go to `http://localhost:8000/` and enjoy!

To create a Librarian account:
* `python manage.py createsuperuser` and enter the credentials that follow
* use the username and password as login on the admin page
  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

