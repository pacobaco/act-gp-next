# Act-GP Next

Act-GP Next is a Python-based serverless API project built for Vercel.  
It provides multiple endpoints to experiment with AI-powered tasks and predictions, easily deployable on Vercel’s serverless platform.

---

## Features

- Python Serverless Functions using Vercel
- Multiple API endpoints:
  - `/api/hello` — Test endpoint
  - `/api/generate` — Sample generate endpoint
  - `/api/predict` — Sample prediction endpoint
- Ready-to-deploy `vercel.json` and `requirements.txt`
- Compatible with Python 3.11 runtime

---

## Project Structure

```
act-gp-next/
├─ api/
│  ├─ hello.py        # Test endpoint
│  ├─ generate.py     # Sample generate endpoint
│  └─ predict.py      # Sample prediction endpoint
├─ requirements.txt   # Python dependencies
└─ vercel.json        # Vercel deployment config
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/pacobaco/act-gp-next.git
cd act-gp-next
```

Install dependencies locally (optional, for testing):

```bash
pip install -r requirements.txt
```

---

## Deployment on Vercel

1. Make sure you have [Vercel CLI](https://vercel.com/download) installed.
2. Login to Vercel:

```bash
vercel login
```

3. Deploy the project:

```bash
vercel deploy
```

4. Vercel will provide a URL for your deployed API, e.g.:

```
https://act-gp-next.vercel.app/api/hello
```

---

## Usage

All API endpoints return JSON responses. Example:

```bash
curl https://<YOUR_VERCEL_URL>/api/hello
```

Response:

```json
{
  "statusCode": 200,
  "body": "Hello from Act-GP Next API!"
}
```

Similarly:

```bash
curl https://<YOUR_VERCEL_URL>/api/predict
```

Response:

```json
{
  "prediction": "AI predicts success!"
}
```

---

## Adding New Endpoints

1. Create a new Python file in the `api/` folder, e.g., `new_endpoint.py`.
2. Define a `handler(request)` function that returns a JSON-compatible dictionary:

```python
def handler(request):
    return {"statusCode": 200, "body": "Hello from new endpoint!"}
```

3. Deploy to Vercel using `vercel deploy`.

---

## Requirements

- Python 3.11
- Vercel account
- Python dependencies listed in `requirements.txt`

---

## License

This project is open-source under the MIT License.  

---

## Acknowledgements

- Built with Vercel Serverless Functions  
- Inspired by AI experimentation and rapid prototyping workflows
