import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function ExpenseChart({ totalExpenses, expenseData, startDate, endDate }) {
  const data = {
    labels: ['Food & Drink', 'Shopping', 'Travel', "Recreation"],
    datasets: [ 
      {
        data: expenseData,
        backgroundColor: [
          '#d9f99d', // pastel green
          '#bfdbfe', // pastel blue
          '#f5d0fe', // pastel pink
          '#fef9c3', // pastel yellow
          '#cbd5e1', // pastel gray-blue
        ],
        borderWidth: 2,
        cutout: '70%',
      },
    ],
  };

  const options = {
    cutout: '70%', // donut hole size (keep 70%)
    layout: {
      padding: 0, // remove internal padding
    },
    plugins: {
      legend: {
        display: false, 
      },
      tooltip: {
        enabled: true,
      },
    },
    responsive: true,
    maintainAspectRatio: false, // SUPER important: allow full container control
  };

  return (
    <div className="bg-gray-50 rounded-2xl shadow-lg p-6 w-full max-w-sm flex flex-col items-center relative">
      
      {/* Top Section */}
      <div className="w-full flex justify-between items-center mb-6">
        <div className="flex items-center gap-2 bg-gray-100 px-4 py-2 rounded-lg text-sm font-medium text-gray-700">
          📅 {startDate} - {endDate}
        </div>
        {/* <button className="bg-black text-white text-sm px-4 py-2 rounded-lg font-semibold">
          Month
        </button> */}
      </div>

      {/* Total Expense Title */}
      <div className="w-full text-left">
        <h2 className="text-sm text-green-700 font-semibold">Total Expense</h2>
        <h1 className="text-4xl font-bold">${totalExpenses.toLocaleString()}</h1>
      </div>

      {/* Chart with center label */}
      <div className="relative w-64 h-64 my-8">
      <Doughnut data={data} options={options} />
        {/* Centered text inside doughnut */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center justify-center text-center">
        <p className="text-2xl font-bold">${totalExpenses.toLocaleString()}</p>
        <p className="text-green-700 text-sm font-semibold">(42%)</p>
        </div>

      </div>
      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-4 text-sm mt-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-lime-300 rounded-full" /> Food & Drink
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-300 rounded-full" /> Shopping
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-pink-300 rounded-full" /> Travel
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-yellow-200 rounded-full" /> Recreation
        </div>
      </div>
    </div>
  );
}
