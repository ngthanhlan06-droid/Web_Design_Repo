# Mini House-Price Prediction API

## Run

From the `backend/` folder:

```bash
python3 -m pip install -r requirements.txt
uvicorn main:app --reload
```

Open the form at `http://127.0.0.1:8000/static/house_form.html` or test the API at `http://127.0.0.1:8000/docs`.

## Test result

For `GET /predict?area=80&bedrooms=3&location=hanoi`:

```json
{
	"area": 80.0,
	"bedrooms": 3,
	"location": "hanoi",
	"predicted_price": 2405000000.0
}
```

`location` is optional, so omitting it uses the default value `other`. Omitting `area` returns a `422 Unprocessable Entity` error because `area` is required and FastAPI validates the query parameters automatically.

The frontend uses the relative URL `/predict` because it is served by the same FastAPI server and port as the API. This avoids a cross-origin request and does not require CORS configuration.

The bonus `POST /predict` endpoint accepts the same fields as a JSON request body. Query parameters are sent in the URL, while JSON data is sent inside the request body.