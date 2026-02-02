document.addEventListener("DOMContentLoaded", function () {

    const cardFields = document.getElementById("card-fields");
    const invoiceFields = document.getElementById("invoice-fields");
    const methods = document.querySelectorAll("input[name='method']");
    const payBtn = document.getElementById("pay-btn");

    function updateForm() {
        const selected = document.querySelector("input[name='method']:checked");

        // скрываем всё по умолчанию
        cardFields.style.display = "none";
        invoiceFields.style.display = "none";

        if (!selected) {
            payBtn.textContent = "Оплатить";
            return;
        }

        if (selected.value === "card") {
            cardFields.style.display = "block";
            payBtn.textContent = "Оплатить картой";
        }

        if (selected.value === "invoice") {
            invoiceFields.style.display = "block";
            payBtn.textContent = "Сформировать счёт";
        }

        if (selected.value === "cash") {
            payBtn.textContent = "Подтвердить заказ";
        }
    }

    methods.forEach(method => {
        method.addEventListener("change", updateForm);
    });
});
