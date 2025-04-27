import { useEffect, useState } from 'react';
import './App.css';
import PlaidLinker from './PlaidLinker.jsx';
import ExpenseChart from './ExpenseChart.jsx';
import InvestmentChart from './InvestmentChart.jsx';

function App() {
  const [userData, setUserData] = useState([]);
  const [invest, setInvest] = useState([]);
  const [aiSummary, setAiSummary] = useState('');
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [savingsAmount, setSavingsAmount] = useState(0);

  const [userEmail, setUserEmail] = useState('');
  const [userGoals, setUserGoals] = useState('');
  const [submissionMessage, setSubmissionMessage] = useState('');

  // Fetch transaction data + AI summary
  useEffect(() => {
    fetch('http://localhost:5001/api/get_transactions')
      .then(res => res.json())
      .then(response => {
        setUserData(response.transactions || []);
  
        if (response.transactions && response.transactions.length > 0) {
          setLoadingSummary(true);
          fetch('http://localhost:5001/api/get_ai_summary/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ transaction_history: response.transactions }),
          })
            .then(res => res.json())
            .then(summaryResponse => {
              const { summary, suggested_savings } = summaryResponse;
  
              if (summary && suggested_savings !== undefined) {
                setAiSummary(summary);
                setSavingsAmount(parseFloat(suggested_savings));
  
                fetch('http://localhost:5001/api/get_predictions/' + suggested_savings)
                  .then(res => res.json())
                  .then(predictions => {
                    setInvest(predictions || []);
                  });
              }
  
              setLoadingSummary(false);
            });
        }
      });
  }, []);

  // Prepare expenses chart
  const startDate = new Date('2025-02-01');
  const endDate = new Date('2025-03-01');
  const expenses = { FoodAndDrink: 0, Shopping: 0, Travel: 0, Recreation: 0, Other: 0 };

  userData.forEach(transaction => {
    const transDate = new Date(transaction.date);
    if (transDate >= startDate && transDate <= endDate && transaction.amount > 0) {
      const category = transaction.category[0];
      if (category === 'Food and Drink') {
        expenses.FoodAndDrink += transaction.amount;
      } else if (category === 'Shops') {
        expenses.Shopping += transaction.amount;
      } else if (category === 'Travel') {
        expenses.Travel += transaction.amount;
      } else if (category === 'Recreation') {
        expenses.Recreation += transaction.amount;
      } else {
        expenses.Other += transaction.amount;
      }
    }
  });

  const total = Object.values(expenses).reduce((sum, val) => sum + val, 0);

 const handleFormSubmit = (e) => {
  e.preventDefault();
  fetch('http://localhost:5001/api/send_email/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      user_email: userEmail,
      user_goals: userGoals,
      ai_summary: aiSummary,
    }),
  })
    .then(response => response.text())
    .then(data => {
      console.log(data);
      setSubmissionMessage('✅ Email sent successfully!');
      setUserEmail('');   
      setUserGoals('');
    })
    .catch(error => {
      console.error('Error:', error);
      setSubmissionMessage('❌ Failed to send email.');
    });
};

  

return (
  <div className="min-h-screen flex flex-col items-center justify-center gap-11 bg-gradient-to-br from-green-100 via-white to-yellow-100 p-8">
    <h1 className="text-7xl font-bold tracking-wide bg-gradient-to-r from-green-300 via-green-400 to-green-500 bg-clip-text text-transparent uppercase font-outfit">
  FISCORA
</h1>






    <div className="w-full max-w-md">
      <PlaidLinker />
    </div>

    <div className="w-full flex flex-col lg:flex-row gap-8 justify-center items-start">
      {/* Expense Chart */}
      <ExpenseChart
        totalExpenses={total - expenses.Other}
        expenseData={[
          expenses.FoodAndDrink,
          expenses.Shopping,
          expenses.Travel,
          expenses.Recreation
        ]}
        startDate="February 01"
        endDate="March 01"
      />

      {/* Investment Chart */}
      <InvestmentChart predictions={invest} />

      {/* Financial Insights */}
      <div className="bg-white rounded-2xl shadow-md p-6 w-full max-w-md flex flex-col items-center">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Financial Insights</h2>
        <div className="w-full text-left">
          {loadingSummary ? (
            <p className="text-gray-400 animate-pulse">Analyzing your data...</p>
          ) : (
            <p className="text-gray-700 whitespace-pre-line">{aiSummary}</p>
          )}
        </div>
      </div>
    </div>

    {/* Email + Finance Goals Form */}
    <div className="bg-white rounded-2xl shadow-md p-6 w-full max-w-md flex flex-col items-center mt-10">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">Get Personalized Finance Help</h2>
      <form onSubmit={handleFormSubmit} className="w-full flex flex-col gap-4">
        <input
          type="email"
          placeholder="Enter your email"
          className="border border-gray-300 p-3 rounded-lg w-full"
          value={userEmail}
          onChange={(e) => setUserEmail(e.target.value)}
          required
        />
        <textarea
          placeholder="Describe your finance goals and style"
          className="border border-gray-300 p-3 rounded-lg w-full h-32"
          value={userGoals}
          onChange={(e) => setUserGoals(e.target.value)}
          required
        />
        <button
          type="submit"
          className="bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-lg transition"
        >
          Submit
        </button>
      </form>
      {submissionMessage && (
        <p className="text-sm text-gray-500 mt-4">{submissionMessage}</p>
      )}
    </div>
  </div>
);
 
}

export default App;

