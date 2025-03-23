document.addEventListener("DOMContentLoaded", function () {
    // Local storage for products
    const orderProducts = [];
    const productList = document.getElementById("product-list");
    const orderCountElement = document.getElementById("order-count");
    const placeOrderBtn = document.getElementById("place-order-btn");
    const cancelOrderBtn = document.getElementById("cancel-order-btn");
    const supermarketSelect = document.getElementById("supermarket-id");
    const customerEmailElement = document.getElementById("customer-email");
    const orderForm = document.getElementById("order-form");
    const productDataContainer = document.getElementById(
        "product-data-container"
    );
    const supermarketIdHidden = document.getElementById("supermarket-id-hidden");


    // Add product to the list (from modal)
    document.getElementById("add-product-form")
        ?.addEventListener("submit", function (e) {
            e.preventDefault();

            const productSelect = document.getElementById("product");
            const productId = productSelect.value;
            const productName =
                productSelect.options[productSelect.selectedIndex].text;
            const quantity = document.getElementById("quantity").value;

            if (!productId || !quantity || quantity < 1) {
                alert("Please select a product and enter a valid quantity");
                return;
            }

            // Check if product already exists in the list
            const existingItemIndex = orderProducts.findIndex(
                (item) => item.productId === productId
            );

            if (existingItemIndex !== -1) {
                // Update existing product quantity
                orderProducts[existingItemIndex].quantity += parseInt(quantity);
            } else {
                // Add new product
                orderProducts.push({
                    productId: productId,
                    productName: productName,
                    quantity: parseInt(quantity),
                });
            }

            // Update the display
            updateProductList();

            // Close the modal
            const modal = bootstrap.Modal.getInstance(
                document.getElementById("addProductRecordModal")
            );
            if (modal) modal.hide();
            e.target.reset();
        });

    // Update the product list display
    function updateProductList() {
        if (!productList) return;

        if (orderProducts.length === 0) {
            productList.innerHTML = `
            <div class="text-center p-4">
                <p>No products added. Click "Add Product" to begin.</p>
            </div>
        `;
            orderCountElement.textContent = "0";
        } else {
            productList.innerHTML = "";
            orderCountElement.textContent = orderProducts.length.toString();

            orderProducts.forEach((item, index) => {
                const row = document.createElement("div");
                row.className = "row align-items-center border-bottom py-2";
                row.innerHTML = `
                <div class="d-none d-md-block col-3">${item.productId}</div>
                <div class="col-6 col-md-4">${item.productName}</div>
                <div class="col-4 col-md-3">${item.quantity}</div>
                <div class="col-2 text-end">
                    <div class="dropdown">
                        <button class="btn border rounded-3 p-1 px-2 btn-light btn-sm no-arrow"
                                type="button" data-bs-toggle="dropdown"
                                aria-expanded="false">
                            <i class="fa-solid fa-ellipsis fa-lg"></i>
                        </button>
                        <ul class="dropdown-menu rounded-3 px-2 dropdown-menu-end">
                            <li><a class="dropdown-item rounded-2 edit-product" href="#" data-index="${index}">Edit</a></li>
                            <li><a class="dropdown-item rounded-2 delete-product" href="#" data-index="${index}">Delete</a></li>
                        </ul>
                    </div>
                </div>
            `;
                productList.appendChild(row);
            });

            // Add click handlers for dropdown actions
            document.querySelectorAll(".delete-product").forEach((link) => {
                link.addEventListener("click", function (e) {
                    e.preventDefault();
                    const index = parseInt(this.getAttribute("data-index"), 10);
                    orderProducts.splice(index, 1);
                    updateProductList();
                });
            });

            document.querySelectorAll(".edit-product").forEach((link) => {
                link.addEventListener("click", function (e) {
                    e.preventDefault();
                    const index = parseInt(this.getAttribute("data-index"), 10);
                    const item = orderProducts[index];

                    // Populate the modal with product data
                    const productSelect = document.getElementById("product");
                    const quantityInput = document.getElementById("quantity");

                    productSelect.value = item.productId;
                    quantityInput.value = item.quantity;

                    // Remove the item from array (will be re-added when form submits)
                    orderProducts.splice(index, 1);

                    // Open the modal
                    const modal = new bootstrap.Modal(document.getElementById("addProductRecordModal"));
                    modal.show();
                });
            });

            // Remove dropdown toggle arrow
            document.querySelectorAll('.no-arrow.dropdown-toggle').forEach(toggle => {
                toggle.classList.remove('dropdown-toggle');
            });
        }
    }

    // Place Order button click
    placeOrderBtn?.addEventListener("click", function () {
        if (!supermarketSelect.value) {
            alert("Please select a supermarket");
            supermarketSelect.focus();
            return;
        }

        if (orderProducts.length === 0) {
            alert("Please add at least one product to the order");
            return;
        }

        // Clear previous product data
        productDataContainer.innerHTML = "";

        // Add hidden inputs for each product
        orderProducts.forEach((item, index) => {
            const productIdInput = document.createElement("input");
            productIdInput.type = "hidden";
            productIdInput.name = "product_ids";
            productIdInput.value = item.productId;
            productDataContainer.appendChild(productIdInput);

            const quantityInput = document.createElement("input");
            quantityInput.type = "hidden";
            quantityInput.name = "quantities";
            quantityInput.value = item.quantity;
            productDataContainer.appendChild(quantityInput);
        });

        // Set the supermarket ID
        supermarketIdHidden.value = supermarketSelect.value;

        // Submit the form
        orderForm.submit();
    });

    // Cancel button click
    cancelOrderBtn?.addEventListener("click", function () {
        if (orderProducts.length > 0) {
            if (
                !confirm(
                    "Are you sure you want to cancel? All added products will be lost."
                )
            ) {
                return;
            }
        }

        window.location.href = "/orders/";
    });


// Handle place order button
    document.querySelector('.button-primary')?.addEventListener('click', function () {
        // Make sure we have products
        if (orderProducts.length === 0) {
            alert('Please add at least one product to the order');
            return;
        }

        // Get supermarket ID from the page
        const supermarketId = document.querySelector('.order-info').dataset.supermarketId ||
            "{{ supermarket.id }}";  // Fallback to template value

        // Create a form to submit
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = window.location.pathname;
        form.style.display = 'none';

        // Add CSRF token
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);

        // Add supermarket ID
        const supermarketInput = document.createElement('input');
        supermarketInput.type = 'hidden';
        supermarketInput.name = 'supermarket_id';
        supermarketInput.value = supermarketId;
        form.appendChild(supermarketInput);

        // Add products data
        const productsInput = document.createElement('input');
        productsInput.type = 'hidden';
        productsInput.name = 'products_json';
        productsInput.value = JSON.stringify(orderProducts);
        form.appendChild(productsInput);

        // Flag this as an order submission
        const submitFlagInput = document.createElement('input');
        submitFlagInput.type = 'hidden';
        submitFlagInput.name = 'submit_order';
        submitFlagInput.value = 'true';
        form.appendChild(submitFlagInput);

        // Submit the form
        document.body.appendChild(form);
        form.submit();
    });

// Handle cancel button
    document.querySelector('.button-secondary')?.addEventListener('click', function () {
        if (confirm('Are you sure you want to cancel this order?')) {
            window.location.href = '/orders/';
        }
    });

    // Initialize the product list
    updateProductList();
});
