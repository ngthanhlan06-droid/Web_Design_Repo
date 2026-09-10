from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


app = FastAPI(
	title="Maison Price API",
	description="A small house-price prediction API for Week 6.",
	version="1.0.0",
)


def predict_price(area: float, bedrooms: int, location: str) -> float:
	"""Return the assignment's rounded placeholder house price in VND."""
	price = 500_000_000 + (15_000_000 * area) + (50_000_000 * bedrooms)
	normalized_location = location.strip().lower()

	if normalized_location == "hanoi":
		price *= 1.3
	elif normalized_location == "hcmc":
		price *= 1.25

	return float(round(price / 1_000_000) * 1_000_000)


class HouseInput(BaseModel):
	area: float
	bedrooms: int
	location: str = "other"


# The calculation is synchronous because it does not perform I/O.
@app.get("/predict")
def get_prediction(
	area: float,
	bedrooms: int,
	location: str = "other",
) -> dict[str, float | int | str]:
	return {
		"area": area,
		"bedrooms": bedrooms,
		"location": location,
		"predicted_price": predict_price(area, bedrooms, location),
	}


@app.post("/predict")
def post_prediction(house: HouseInput) -> dict[str, float | int | str]:
	return {
		"area": house.area,
		"bedrooms": house.bedrooms,
		"location": house.location,
		"predicted_price": predict_price(
			house.area,
			house.bedrooms,
			house.location,
		),
	}


@app.get("/", include_in_schema=False)
def home() -> dict[str, str]:
	return {"message": "Open /static/house_form.html to use Maison."}


app.mount("/static", StaticFiles(directory="../frontend", html=True), name="static")