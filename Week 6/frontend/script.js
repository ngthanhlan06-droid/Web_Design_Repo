const form = document.querySelector("#prediction-form");
const submitButton = document.querySelector("#submit-button");
const result = document.querySelector("#result");
const resultPrice = document.querySelector("#result-price");
const resultMeta = document.querySelector("#result-meta");
const errorMessage = document.querySelector("#error");
const currency = new Intl.NumberFormat("vi-VN");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  result.classList.remove("visible");
  errorMessage.classList.remove("visible");
  submitButton.disabled = true;
  submitButton.querySelector("span").textContent = "Calculating...";

  const formData = new FormData(form);
  const params = new URLSearchParams({
    area: formData.get("area"),
    bedrooms: formData.get("bedrooms"),
    location: formData.get("location"),
  });

  try {
    const response = await fetch(`/predict?${params.toString()}`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail?.[0]?.msg || "Unable to calculate this estimate.");
    }

    resultPrice.textContent = `${currency.format(data.predicted_price)} VND`;
    resultMeta.textContent = `${data.area} m² · ${data.bedrooms} bedrooms · ${data.location}`;
    result.classList.add("visible");
  } catch (error) {
    errorMessage.textContent = error.message || "Something went wrong. Please try again.";
    errorMessage.classList.add("visible");
  } finally {
    submitButton.disabled = false;
    submitButton.querySelector("span").textContent = "Predict";
  }
});