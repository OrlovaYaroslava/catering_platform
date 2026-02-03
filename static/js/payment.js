document.addEventListener("DOMContentLoaded", function () {

    const cardFields = document.getElementById("card-fields");
    const invoiceFields = document.getElementById("invoice-fields");
    const payBtn = document.getElementById("pay-btn");

    document.addEventListener("click", function (e) {

        if (e.target.name !== "method") return;

        // скрываем всё
        cardFields.style.display = "none";
        invoiceFields.style.display = "none";

        if (e.target.value === "card") {
            cardFields.style.display = "block";
            payBtn.textContent = "Оплатить картой";
        }

        if (e.target.value === "invoice") {
            invoiceFields.style.display = "block";
            payBtn.textContent = "Сформировать счёт";
        }

        if (e.target.value === "cash") {
            payBtn.textContent = "Подтвердить заказ";
        }
    });
});
