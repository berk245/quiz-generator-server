# Qgen Server

## Project Description

Qgen Server is the backend component of the Qgen application, developed to streamline the process of question generation for educators using artificial intelligence. The server provides RESTful APIs for handling user authentication, quiz management, question generation, and more.

The server is live on https://api.qgen.live

## Demo

https://qgen-llm.web.app

## Project Flow

The Qgen Server is built with FastAPI, a modern web framework for building APIs with Python. It utilizes various middleware for tasks such as JWT validation and request logging. The server interacts with a MySQL database to store user data, quizzes, and generated questions. Additionally, Qgen Server integrates with external services such as OpenAI for embeddings and Pinecone for storing vectors.

![Qgen Server Architecture Diagram](link_to_diagram)

## Run Locally

To run the Qgen Server locally, follow these steps:

1. Clone the project: `git clone https://github.com/berk245/quiz-generator-server.git`
2. Navigate to the project directory: `cd quiz-generator-server`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up environment variables: Create a `.env` file with required environment variables (refer to `.env.example` for reference).
5. Start the server: `uvicorn main:app --reload`

## API Documentation

API documentation is available at [https://api.qgen.live/docs](https://api.qgen.live/docs). This interactive documentation provides details about available endpoints, request parameters, and response schemas.

## License

This project is licensed under the [MIT License](LICENSE).

## Additional Information

For more details about the Qgen Frontend and its integration with Qgen Server, refer to the [Qgen Frontend repository](https://github.com/berk245/quiz-generator-client).
