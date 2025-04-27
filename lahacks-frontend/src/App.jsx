import { useEffect, useState } from 'react';
import './App.css';
import PlaidLinker from './PlaidLinker.jsx';
import ExpenseChart from './ExpenseChart.jsx';
import InvestmentChart from './InvestmentChart.jsx';

function App() {
  const [userData, setUserData] = useState([]);
  const [invest, setInvest] = useState([]);
  const [aiSummary, setAiSummary] = useState('');
  const [loadingSummary, setLoadingSummary] = useState(false); // For loading animation
  const [savingsAmount, setSavingsAmount] = useState(0);




  useEffect(() => {
    fetch('http://localhost:5001/api/get_transactions')
      .then(res => res.json())
      .then(response => {
        console.log(response);
        setUserData(response.transactions || []);


        if (response.transactions && response.transactions.length > 0) {
          setLoadingSummary(true);
          fetch('http://localhost:5001/api/get_ai_summary/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ transaction_history: response.transactions })
          })
            .then(res => res.json())
            .then(summaryResponse => {
              console.log('AI Summary:', summaryResponse);
            
              const text = summaryResponse.summary;
            
              if (text) {
                // Match the tuple like ('summary', number)
                const tupleMatch = text.match(/\('(.*?)',\s*([\d.]+)\)/);
            
                if (tupleMatch) {
                  const parsedSummary = tupleMatch[1].replace(/\\n/g, '\n');  // First capture group = summary text
                  const parsedAmount = parseFloat(tupleMatch[2]);  // Second capture group = savings number
            
                  console.log('Parsed Summary:', parsedSummary);
                  console.log('Parsed Savings Amount:', parsedAmount);
            
                  setAiSummary(parsedSummary);
                  setSavingsAmount(parsedAmount);
            
                  // ✅ THEN call get_predictions dynamically
                  fetch('http://localhost:5001/api/get_predictions/' + parsedAmount)
                    .then(res => res.json())
                    .then(response => {
                      console.log('Investment Prediction:', response);
                      setInvest(response || []);
                    });
                } else {
                  console.error('Failed to parse AI Summary tuple');
                }
              }
            
              setLoadingSummary(false);
            })
            
        }
      });

    // fetch('http://localhost:5001/api/get_predictions/' + '200')
    //   .then(res => res.json())
    //   .then(response => {
    //     setInvest(response || []);
    //   });

  }, []);

  const startDate = new Date('2025-02-01');
  const endDate = new Date('2025-03-01');

  const expenses = {
    FoodAndDrink: 0,
    Shopping: 0,
    Travel: 0,
    Recreation: 0,
    Other: 0,
  };

  userData.forEach(transaction => {
    const transDate = new Date(transaction.date);
    if (transDate >= startDate && transDate <= endDate && transaction.amount > 0) {
      const category = transaction.category[0];
      console.log(category)
      // console.log(transaction)
      
      if (category === 'Food and Drink') {
        console.log(category === 'Food and Drink')
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

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-8 bg-gradient-to-br from-green-100 via-white to-yellow-100 p-6">
      <h1> FISCORA </h1>

      <div className="card">
        <PlaidLinker />
      </div>

      <div className="w-full flex flex-row gap-6 justify-center">
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
        <InvestmentChart predictions={invest} />

        <div className="bg-gray-50 rounded-2xl shadow-lg p-6 w-full max-w-md flex flex-col items-center relative">
  <div className="w-full flex justify-between items-center mb-6">
    <h2 className="text-xl font-bold">Financial Insights</h2>
  </div>

  <div className="w-full text-left">
    {loadingSummary ? (
      <p className="text-gray-500 animate-pulse">Loading AI analysis...</p>
    ) : (
      <p className="text-gray-700 whitespace-pre-line">{aiSummary}</p>
    )}
  </div>
  </div>

      </div>
    </div>
  );
}

export default App;