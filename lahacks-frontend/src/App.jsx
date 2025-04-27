import { useEffect, useState } from 'react';
import './App.css';
import PlaidLinker from './PlaidLinker.jsx';
import ExpenseChart from './ExpenseChart.jsx';
import InvestmentChart from './InvestmentChart.jsx';

function App() {
  const [userData, setUserData] = useState([]);
  const [invest, setInvest] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5001/api/get_transactions')
      .then(res => res.json())
      .then(response => {
        console.log(response);
        setUserData(response.transactions || []);
      });

    fetch('http://localhost:5001/api/get_predictions/' + '200')
      .then(res => res.json())
      .then(response => {
        console.log(response, 'sdfsd');
        setInvest(response || []);
      });

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
      </div>
    </div>
  );
}

export default App;