import { Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend);

export default function InvestmentChart({ predictions = [] }) {
  const data = {
    labels: Array.from({ length: 20 }, (_, i) => (i + 1).toString()),
    datasets: [
      {
        label: 'Investment Growth',
        data: predictions,
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        fill: false,
        tension: 0.3,
        pointRadius: 3,
      },
    ],
  };

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
          text: 'Time (Days)',
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

  const totalInvestment = predictions.length > 0 ? predictions[predictions.length - 1] : 0;

  return (
    <div className="bg-gray-50 rounded-2xl shadow-lg p-6 w-full max-w-md flex flex-col items-center relative">
      <div className="w-full flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold">Investment Statistic</h2>
      </div>

      <div className="w-full text-left">
        <h1 className="text-4xl font-bold">${totalInvestment.toLocaleString()}</h1>
      </div>

      <div className="w-full h-64 my-8">
        <Line data={data} options={options} />
      </div>

      <div className="flex flex-col gap-4 w-full">
        <button className="bg-green-100 text-green-700 px-4 py-2 rounded-lg font-semibold">
          Invest in Your Future!
        </button>
      </div>
    </div>
  );
}