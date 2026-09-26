const expenses = document.querySelector("#expenses");
const template = document.querySelector("#expense-template");

function addExpense(category = "", amount = "") {
  const row = template.content.cloneNode(true);
  row.querySelector(".category").value = category;
  row.querySelector(".amount").value = amount;
  row.querySelector(".remove").addEventListener("click", (event) => {
    if (expenses.children.length > 1) event.target.closest(".expense-row").remove();
  });
  expenses.appendChild(row);
}

[["Rent", 15000], ["Food", 6000], ["Transport", 3000]].forEach(([c, a]) => addExpense(c, a));
document.querySelector("#add-expense").addEventListener("click", () => addExpense());

document.querySelector("#budget-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const error = document.querySelector("#error");
  const button = event.target.querySelector(".primary");
  error.textContent = "";
  button.disabled = true;
  button.textContent = "Analyzing…";

  const rows = [...document.querySelectorAll(".expense-row")];
  const payload = {
    monthly_income: Number(document.querySelector("#income").value),
    savings_goal: Number(document.querySelector("#goal").value || 0),
    currency: document.querySelector("#currency").value,
    provider: document.querySelector("#provider").value,
    expenses: rows.map(row => ({
      category: row.querySelector(".category").value,
      amount: Number(row.querySelector(".amount").value)
    }))
  };

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Analysis failed.");

    const money = new Intl.NumberFormat(undefined, {style: "currency", currency: payload.currency});
    document.querySelector("#total").textContent = money.format(data.summary.total_expenses);
    document.querySelector("#remaining").textContent = money.format(data.summary.remaining);
    document.querySelector("#ratio").textContent = `${data.summary.expense_ratio}%`;
    document.querySelector("#tips").innerHTML = data.recommendations.map(tip => `<li>${tip}</li>`).join("");
    document.querySelector("#ai-advice").textContent = data.ai_advice;
    document.querySelector("#results").classList.remove("hidden");
  } catch (err) {
    error.textContent = err.message;
  } finally {
    button.disabled = false;
    button.textContent = "Analyze my budget";
  }
});
