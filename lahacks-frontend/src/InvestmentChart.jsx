import { useState } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend);

export default function InvestmentChart({ predictions = [] }) {
  const [showLongTerm, setShowLongTerm] = useState(false);

  const shortTermData = {
    labels: Array.from({ length: 20 }, (_, i) => (i + 1).toString()),
    datasets: [
      {
        label: 'Investment Growth (20 days)',
        data: predictions,
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        fill: false,
        tension: 0.3,
        pointRadius: 3,
      },
    ],
  };

  const calculateLongTermGrowth = (startAmount) => {
    const growthRate = 0.07; // 7% annual growth
    const years = 10;
    const result = [];

    for (let i = 0; i <= years; i++) {
      const futureValue = startAmount * Math.pow(1 + growthRate, i);
      result.push(futureValue);
    }

    return result;
  };

  const initialInvestment = predictions.length > 0 ? predictions[0] : 0;
  const longTermPredictions = calculateLongTermGrowth(initialInvestment);

  const longTermData = {
    labels: Array.from({ length: 11 }, (_, i) => (i).toString()), // 0 to 10 years
    datasets: [
      {
        label: 'Investment Growth (10 years)',
        data: longTermPredictions,
        borderColor: 'rgba(153, 102, 255, 1)',
        backgroundColor: 'rgba(153, 102, 255, 0.5)',
        fill: false,
        tension: 0.3,
        pointRadius: 3,
      },
    ],
  };

  const chartData = showLongTerm ? longTermData : shortTermData;

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Amount ($)',
        },
      },
      x: {
        title: {
          display: true,
          text: showLongTerm ? 'Time (Years)' : 'Time (Days)',
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        enabled: true,
      },
    },
  };

  const totalInvestment = showLongTerm
    ? longTermPredictions[longTermPredictions.length - 1]
    : predictions.length > 0 ? predictions[predictions.length - 1] : 0;

  return (
    <div className="bg-gray-50 rounded-2xl shadow-lg p-6 w-full max-w-md flex flex-col items-center relative">
      <div className="w-full flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold">Investment Statistic</h2>
      </div>

      <div className="w-full text-left">
        <h1 className="text-4xl font-bold">${totalInvestment.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</h1>
      </div>

      <div className="w-full h-64 my-8">
        <Line data={chartData} options={options} />
      </div>

      <div className="flex flex-col gap-4 w-full">
        <button
          className="bg-green-100 text-green-700 px-4 py-2 rounded-lg font-semibold hover:bg-green-200 transition"
          onClick={() => setShowLongTerm(!showLongTerm)}
        >
          {showLongTerm ? 'View 20-Day Prediction' : 'Invest in Your Future!'}
        </button>
      </div>
    </div>
  );
}