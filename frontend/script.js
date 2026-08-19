// =========================================================
// NAVIGATION
// =========================================================

function showSection(sectionId, button) {

  const sections =
    document.querySelectorAll(
      ".page-section"
    );

  sections.forEach(function (section) {

    section.classList.remove(
      "active"
    );

  });


  const selected =
    document.getElementById(
      sectionId
    );


  if (selected) {

    selected.classList.add(
      "active"
    );

  }


  const buttons =
    document.querySelectorAll(
      ".nav-btn"
    );


  buttons.forEach(function (btn) {

    btn.classList.remove(
      "active"
    );

  });


  if (button) {

    button.classList.add(
      "active"
    );

  }

}


// =========================================================
// SEND PREDICTION TO STREAMLIT
// =========================================================

function submitPrediction(event) {

  event.preventDefault();


  const location =
    document.getElementById(
      "location"
    ).value;


  const totalSqft =
    document.getElementById(
      "total_sqft"
    ).value;


  const bhk =
    document.getElementById(
      "bhk"
    ).value;


  const bath =
    document.getElementById(
      "bath"
    ).value;


  const askingPrice =
    document.getElementById(
      "asking_price"
    ).value;


  if (!location) {

    alert(
      "Please select a location."
    );

    return;

  }


  if (
    !totalSqft ||
    !bhk ||
    !bath ||
    !askingPrice
  ) {

    alert(
      "Please fill all fields."
    );

    return;

  }


  const params =
    new URLSearchParams();


  params.set(
    "predict",
    "1"
  );


  params.set(
    "location",
    location
  );


  params.set(
    "total_sqft",
    totalSqft
  );


  params.set(
    "bhk",
    bhk
  );


  params.set(
    "bath",
    bath
  );


  params.set(
    "asking_price",
    askingPrice
  );


  /*
      Send the form values to the
      Streamlit Python application.
  */

  window.top.location.href =
    window.top.location.pathname
    +
    "?"
    +
    params.toString();

}


// =========================================================
// DISPLAY RESULT
// =========================================================

function displayPrediction(result) {

  if (!result) {

    return;

  }


  const placeholder =
    document.getElementById(
      "resultPlaceholder"
    );


  const resultBox =
    document.getElementById(
      "predictionResult"
    );


  if (placeholder) {

    placeholder.classList.add(
      "hidden"
    );

  }


  if (resultBox) {

    resultBox.classList.remove(
      "hidden"
    );

  }


  const predicted =
    document.getElementById(
      "predictedPrice"
    );


  if (predicted) {

    predicted.textContent =
      "₹ "
      +
      Number(
        result.predicted_price
      ).toFixed(2)
      +
      " L";

  }


  const asking =
    document.getElementById(
      "resultAskingPrice"
    );


  if (asking) {

    asking.textContent =
      "₹ "
      +
      Number(
        result.asking_price
      ).toFixed(2)
      +
      " L";

  }


  const variance =
    document.getElementById(
      "priceVariance"
    );


  if (variance) {

    const sign =
      result.variance >= 0
        ? "+"
        : "";

    variance.textContent =
      sign
      +
      Number(
        result.variance
      ).toFixed(2)
      +
      "%";

  }


  const rating =
    document.getElementById(
      "ratingBadge"
    );


  if (rating) {

    rating.textContent =
      result.rating;


    rating.classList.remove(
      "undervalued",
      "overpriced"
    );


    if (
      result.rating
        .toLowerCase()
        .includes(
          "undervalued"
        )
    ) {

      rating.classList.add(
        "undervalued"
      );

    }


    if (
      result.rating
        .toLowerCase()
        .includes(
          "overpriced"
        )
    ) {

      rating.classList.add(
        "overpriced"
      );

    }

  }


  const recommendation =
    document.getElementById(
      "recommendationText"
    );


  if (recommendation) {

    recommendation.textContent =
      result.recommendation;

  }

}


// =========================================================
// PAGE LOAD
// =========================================================

document.addEventListener(
  "DOMContentLoaded",
  function () {

    console.log(
      "Bengaluru Real Estate AI loaded."
    );


    if (
      window.predictionResult
    ) {

      displayPrediction(
        window.predictionResult
      );

    }

  }
);