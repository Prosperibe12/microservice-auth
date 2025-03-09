# Authentication Service

This is an Authentication Service for a Microservice and Distributed System Project. It holds User data and handles User Registration, Login, Token Verification, and Password Reset functionalities. A Gateway Service will consume this service. It is built using the Django Rest Framework and integrates with other microservices in the project. This Service will be built and run as a container service and deployed to a Kubernetes Cluster.

## Table of Contents

- [Technologies](#technologies)
- [Installation & Setup](#setup)
- [Environment Variables](#environment-variables)
- [Running as Service](#running-the-service)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Technologies

- Python
- Django Rest Framework
- PostgreSQL
- Docker
- Kubernetes

## Installation & Setup

### Prerequisites

- Python 3.10
- SQL Database
- RabbitMQ
- Docker
- Kubernetes

### Environment Variables
```bash
SECRET_KEY=your_secret_key
DEBUG=False
ENVIRONMENT=local # options are [local, staging, production]
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:password@localhost:5432/dbname #production is configured to use Postgres, change in project_core/settings/production.py
# staging db configuration.
# if ENVIRONMENT=local, it uses default sqlite. This can be changed in the DATABASE section in the settings folder.
DB_ENGINE=django.db.backends.mysql 
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=3306
CLOUD_AMQP_URL=amqp://guest:guest@localhost:5672/
```

1. Clone Repository
```bash
   https://github.com/Prosperibe12/microservice-auth.git
   cd auth_service
```
#### Run Locally

2. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```
3. Install the dependencies:
```bash
pip install -r requirements.txt
```
4. Make Migrations & Migrate
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```
5. Start Project
```bash
python3 manage.py runserver
```
### Running as Service
2. Build and run the Docker containers:
```bash
docker build .
```

### Running as Service
3. Deploy to Local Kubernetes Cluster:
```bash
kubectl apply -f ./
```

## API Endpoints
To view the list of API endpoints in this service and their payload, go to 
```bash
http://127.0.0.1:8000
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update Environment Variables or contact Prosperibe12@gmail.com.

## License

[MIT](https://choosealicense.com/licenses/mit/)