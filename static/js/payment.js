// Payment modal functionality
const bookButtons = document.querySelectorAll(".book-btn");
const subscriptionButtons = document.querySelectorAll(".subscription-btn");
const paymentModal = document.getElementById("paymentModal");
const paymentClose = document.querySelector(".payment-close");
const selectedBikeName = document.getElementById("selectedBikeName");
const selectedBikePrice = document.getElementById("selectedBikePrice");

// Open payment modal from book buttons
if (bookButtons) {
  bookButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const bikeName = this.getAttribute("data-bike-name");
      const bikePrice = this.getAttribute("data-bike-price");

      selectedBikeName.textContent = bikeName;
      selectedBikePrice.textContent = `€${bikePrice} per hour`;

      paymentModal.style.display = "block";
    });
  });
}

// Open payment modal from subscription buttons
if (subscriptionButtons) {
  subscriptionButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const plan = this.getAttribute("data-plan");
      const price = this.getAttribute("data-price");
      let planName;

      switch (plan) {
        case "annual":
          planName = "Annual Membership";
          break;
        case "3day":
          planName = "3-Day Pass";
          break;
        case "payg":
          planName = "Pay As You Go";
          break;
        default:
          planName = "Subscription";
      }

      selectedBikeName.textContent = planName;

      if (plan === "annual") {
        selectedBikePrice.textContent = `€${price} per year`;
      } else if (plan === "3day") {
        selectedBikePrice.textContent = `€${price} for 3 days`;
      } else {
        selectedBikePrice.textContent = `€${price} + €0.50 per 30 min`;
      }

      paymentModal.style.display = "block";
    });
  });
}

// Close payment modal
if (paymentClose) {
  paymentClose.addEventListener("click", function () {
    paymentModal.style.display = "none";
    paymentForm.reset();
    paymentTabs.forEach((tab, index) => {
      if (index === 0) {
        tab.classList.add("active");
      } else {
        tab.classList.remove("active");
      }
    });
  });
}

// Close payment modal when clicking outside
window.addEventListener("click", function (event) {
  if (event.target === paymentModal) {
    paymentModal.style.display = "none";
    paymentForm.reset();
    paymentTabs.forEach((tab, index) => {
      if (index === 0) {
        tab.classList.add("active");
      } else {
        tab.classList.remove("active");
      }
    });
  }
});

// Payment tabs
const paymentTabs = document.querySelectorAll(".payment-tab");

if (paymentTabs) {
  paymentTabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      // Remove active class from all tabs
      paymentTabs.forEach((t) => t.classList.remove("active"));

      // Add active class to clicked tab
      this.classList.add("active");

      // Here you would show/hide content based on tab
      // For demo purposes, we're not implementing this fully
    });
  });
}

// validation function
function validatePaymentForm() {
  const cardNumber = document.getElementById("cardNumber").value;
  const cardName = document.getElementById("cardName").value;
  const expiry = document.getElementById("expiryDate").value;
  const cvv = document.getElementById("cvv").value;
  const errorDiv = document.getElementById("paymentError");

  errorDiv.textContent = ""; // default is empty

  const isCardValid = cardNumber.replace(/\s/g, "").length === 16;
  const isNameValid = cardName.trim() !== "";
  const isCvvValid = /^\d{3}$/.test(cvv);

  if (cardNumber && !isCardValid) {
    errorDiv.textContent = "Please enter a valid 16-digit card number.";
    return false;
  }

  if (cardName && !isNameValid) {
    errorDiv.textContent = "Please enter the name on the card.";
    return false;
  }

  if (cvv && !isCvvValid) {
    errorDiv.textContent = "Please enter a valid 3-digit CVV.";
    return false;
  }

  if (expiry && !expiry.includes('/')) {
    errorDiv.textContent = "Card expiry date doesn't include '/'.";
    return false;
  }

  let expValid = false;

  if (expiry) {
    const [expMonth, expYear] = expiry.includes("/")
      ? expiry.split("/")
      : expiry.split("-");
    const now = new Date();
    const expDate = new Date(
      `20${expYear.length === 2 ? expYear : expYear.slice(-2)}`,
      parseInt(expMonth) - 1
    );
    expValid = expDate >= now;
  }

  if (expiry && !expValid) {
    errorDiv.textContent = "Card expiry date cannot be in the past.";
    return false;
  }

  return isCardValid && isNameValid && isCvvValid && expValid;
}

// Payment form submission

const paymentForm = document.getElementById("paymentForm");
const submitBtn = paymentForm.querySelector("button[type='submit']");

paymentForm.addEventListener("input", () => {
  submitBtn.disabled = !validatePaymentForm();
});

if (paymentForm) {
  paymentForm.addEventListener("submit", function (e) {
    e.preventDefault();

    submitBtn.disabled = true;
    // hide payment method
    paymentModal.style.display = "none";

    // show loading window
    const loadingOverlay = document.createElement("div");
    loadingOverlay.className = "popup-overlay";
    loadingOverlay.innerHTML = `
    <div class="custom-popup no-close">
        <div class="popup-content">
        <p>Processing your payment...</p>
        <p style="font-size: 16px; color: #666;">Please wait a moment.</p>
        </div>
    </div>
    `;
    document.body.appendChild(loadingOverlay);

    const generatePickupCode = () => {
      const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
      let code = "";
      for (let i = 0; i < 16; i++) {
        code += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      return code;
    };

    // show successful message.
    setTimeout(() => {
      loadingOverlay.remove();

      const pickupCode = generatePickupCode();

      const finalPopup = document.createElement("div");
      finalPopup.className = "popup-overlay";
      finalPopup.innerHTML = `
        <div class="custom-popup">
        <div class="popup-content">
            <span class="close-btn">&times;</span>
            <h2>Payment Successful!</h2>
            <p>Your bike is ready for pickup.</p>
            <p><strong>Pickup Code:</strong></p>
            <div class="pickup-code">${pickupCode}</div>
        </div>
        </div>
    `;
      document.body.appendChild(finalPopup);

      finalPopup.querySelector(".close-btn").addEventListener("click", () => {
        finalPopup.remove();
      });

      paymentForm.reset();
    }, 5000);
  });
}
