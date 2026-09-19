from fastapi import FastAPI, HTTPException, Query, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


app = FastAPI(
	title="Maison Price API & Extended Items API",
	description="API upgrade for Week 7.",
	version="2.0.0",
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


class HousePriceRequest(BaseModel):
	area_sqm: float = Field(..., gt=0)
	bedrooms: int = Field(..., ge=0)
	distance_to_center_km: float


class HousePricePrediction(BaseModel):
	predicted_price: float
	currency: str = "VND"


class ItemCreate(BaseModel):
	name: str = Field(..., min_length=1)
	price: float = Field(..., gt=0)


class ItemUpdate(BaseModel):
	name: str | None = None
	price: float | None = None


class ItemPublic(BaseModel):
	id: int
	name: str
	price: float


class ItemListResponse(BaseModel):
	items: list[ItemPublic]
	total: int
	skip: int
	limit: int


_items_db: list[ItemPublic] = [
	ItemPublic(id=1, name="Laptop Dell XPS", price=25_000_000),
	ItemPublic(id=2, name="Màn hình Dell 27 inch", price=7_500_000),
	ItemPublic(id=3, name="Bàn phím cơ Keychron", price=2_200_000),
	ItemPublic(id=4, name="Chuột Logitech MX Master 3S", price=2_500_000),
	ItemPublic(id=5, name="Tai nghe Sony WH-1000XM5", price=8_000_000),
	ItemPublic(id=6, name="Sạc Anker 65W", price=900_000),
]
_next_item_id = 7


def find_item(item_id: int) -> ItemPublic | None:
	for item in _items_db:
		if item.id == item_id:
			return item
	return None


def has_duplicate_name(name: str, item_id: int | None = None) -> bool:
	return any(
		item.id != item_id and item.name.casefold() == name.casefold()
		for item in _items_db
	)


@app.get("/items", response_model=ItemListResponse)
def list_items(
	min_price: float | None = None,
	max_price: float | None = None,
	q: str | None = Query(None, min_length=2),
	sort_by: str = Query("id", pattern="^(id|name|price)$"),
	order: str = Query("asc", pattern="^(asc|desc)$"),
	skip: int = Query(0, ge=0),
	limit: int = Query(10, ge=1, le=100),
) -> ItemListResponse:
	filtered_items = _items_db
	if min_price is not None:
		filtered_items = [item for item in filtered_items if item.price >= min_price]
	if max_price is not None:
		filtered_items = [item for item in filtered_items if item.price <= max_price]
	if q is not None:
		filtered_items = [item for item in filtered_items if q.casefold() in item.name.casefold()]

	total = len(filtered_items)
	filtered_items = sorted(
		filtered_items,
		key=lambda item: getattr(item, sort_by),
		reverse=order == "desc",
	)

	return ItemListResponse(
		items=filtered_items[skip : skip + limit],
		total=total,
		skip=skip,
		limit=limit,
	)


@app.get("/items/{item_id}", response_model=ItemPublic)
def get_item(item_id: int) -> ItemPublic:
	item = find_item(item_id)
	if item is None:
		raise HTTPException(status_code=404, detail="Item not found")
	return item


@app.post("/items", response_model=ItemPublic, status_code=status.HTTP_201_CREATED)
def create_item(data: ItemCreate) -> ItemPublic:
	global _next_item_id
	if has_duplicate_name(data.name):
		raise HTTPException(status_code=409, detail="Item with this name already exists")

	item = ItemPublic(id=_next_item_id, name=data.name, price=data.price)
	_items_db.append(item)
	_next_item_id += 1
	return item


@app.put("/items/{item_id}", response_model=ItemPublic)
def replace_item(item_id: int, data: ItemCreate) -> ItemPublic:
	item = find_item(item_id)
	if item is None:
		raise HTTPException(status_code=404, detail="Item not found")
	if has_duplicate_name(data.name, item_id):
		raise HTTPException(status_code=409, detail="Item with this name already exists")

	item.name = data.name
	item.price = data.price
	return item


@app.patch("/items/{item_id}", response_model=ItemPublic)
def update_item(item_id: int, data: ItemUpdate) -> ItemPublic:
	item = find_item(item_id)
	if item is None:
		raise HTTPException(status_code=404, detail="Item not found")

	updates = data.model_dump(exclude_unset=True)
	if "name" in updates and has_duplicate_name(updates["name"], item_id):
		raise HTTPException(status_code=409, detail="Item with this name already exists")

	for field, value in updates.items():
		setattr(item, field, value)
	return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
	item = find_item(item_id)
	if item is None:
		raise HTTPException(status_code=404, detail="Item not found")
	_items_db.remove(item)


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


@app.post("/predict/house-price", response_model=HousePricePrediction)
def predict_house_price(request: HousePriceRequest) -> HousePricePrediction:
	price = (
		request.area_sqm * 15_000_000
		- request.distance_to_center_km * 5_000_000
		+ request.bedrooms * 20_000_000
	)
	return HousePricePrediction(predicted_price=price)


@app.get("/", include_in_schema=False)
def home() -> dict[str, str]:
	return {"message": "Open /static/house_form.html to use Maison."}


app.mount("/static", StaticFiles(directory="../frontend", html=True), name="static")