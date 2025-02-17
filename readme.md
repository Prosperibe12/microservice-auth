# Auth Service

## Overview
The Auth Service is a microservice responsible for handling authentication and authorization in the microservices architecture. It provides endpoints for user registration, login, token generation, and validation.

## Features
- User Registration
- User Login
- JWT Token Generation
- Token Validation
- Password Encryption

## Technologies Used
- Node.js
- Express.js
- MongoDB
- JSON Web Tokens (JWT)
- bcrypt

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/auth_service.git
    ```
2. Navigate to the project directory:
    ```bash
    cd auth_service
    ```
3. Install dependencies:
    ```bash
    npm install
    ```

## Configuration
Create a `.env` file in the root directory and add the following environment variables:
```
PORT=3000
MONGO_URI=mongodb://localhost:27017/auth_service
JWT_SECRET=your_jwt_secret
```

## Running the Service
Start the service using the following command:
```bash
npm start
```

## API Endpoints

### Register User
- **URL:** `/api/register`
- **Method:** `POST`
- **Body:**
    ```json
    {
        "username": "exampleuser",
        "password": "examplepassword"
    }
    ```
- **Response:**
    ```json
    {
        "message": "User registered successfully"
    }
    ```

### Login User
- **URL:** `/api/login`
- **Method:** `POST`
- **Body:**
    ```json
    {
        "username": "exampleuser",
        "password": "examplepassword"
    }
    ```
- **Response:**
    ```json
    {
        "token": "jwt_token_here"
    }
    ```

### Validate Token
- **URL:** `/api/validate`
- **Method:** `GET`
- **Headers:**
    ```json
    {
        "Authorization": "Bearer jwt_token_here"
    }
    ```
- **Response:**
    ```json
    {
        "valid": true
    }
    ```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any changes.

## Contact
For any questions or support, please contact [yourname@example.com](mailto:yourname@example.com).