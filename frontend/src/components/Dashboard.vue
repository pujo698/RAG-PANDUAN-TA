<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2>Dashboard Evaluasi RAGAS</h2>
      <p>Laporan kualitas sistem berbasis metrik evaluasi offline.</p>
    </div>

    <div class="charts-grid">
      <!-- Bar Chart RAGAS -->
      <div class="chart-card">
        <h3>Rata-rata Skor RAGAS</h3>
        <div class="chart-wrapper">
          <Bar :data="ragasData" :options="ragasOptions" />
        </div>
      </div>

      <!-- Pie Chart Content Type -->
      <div class="chart-card">
        <h3>Distribusi Content Type</h3>
        <div class="chart-wrapper">
          <Pie :data="contentTypeData" :options="pieOptions" />
        </div>
      </div>

      <!-- Heatmap -->
      <div class="chart-card full-width">
        <h3>Skor per Pertanyaan (Heatmap)</h3>
        <div class="heatmap-container">
          <div class="heatmap-grid">
            <!-- Header Row -->
            <div class="heatmap-cell header"></div>
            <div class="heatmap-cell header" v-for="q in 15" :key="'h' + q">Q{{ q }}</div>
            
            <!-- Data Rows -->
            <template v-for="(row, idx) in heatmapData" :key="idx">
              <div class="heatmap-cell row-label">{{ row.label }}</div>
              <div 
                v-for="(val, qIdx) in row.values" 
                :key="qIdx" 
                class="heatmap-cell value-cell"
                :style="{ backgroundColor: getHeatmapColor(val), color: val > 0.4 && val < 0.8 ? '#000' : '#fff' }"
              >
                {{ val.toFixed(2) }}
              </div>
            </template>
          </div>
          <!-- Legend -->
          <div class="heatmap-legend">
            <span>0.0</span>
            <div class="legend-gradient"></div>
            <span>1.0</span>
          </div>
        </div>
      </div>

      <!-- Histogram Chunk Size -->
      <div class="chart-card full-width">
        <h3>Distribusi Panjang Chunk</h3>
        <div class="chart-wrapper histogram-wrapper">
          <Bar :data="chunkSizeData" :options="histogramOptions" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement
} from 'chart.js'
import { Bar, Pie } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement)

// --- Rata-rata Skor RAGAS Data ---
const ragasData = ref({
  labels: ['Faithfulness', 'Answer Relevancy', 'Context Precision', 'Context Recall'],
  datasets: [
    {
      label: 'Skor',
      data: [0.843, 0.594, 0.394, 0.541],
      backgroundColor: ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0'],
    }
  ]
})

const ragasOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      max: 1.0,
      title: { display: true, text: 'Skor' }
    }
  },
  plugins: {
    legend: { display: false }
  }
}

// --- Distribusi Content Type Data ---
const contentTypeData = ref({
  labels: ['aturan', 'lampiran', 'penulisan', 'persyaratan', 'tabel', 'prosedur', 'definisi', 'flowchart', 'visi_misi', 'jadwal'],
  datasets: [
    {
      data: [57, 44, 34, 30, 30, 27, 9, 8, 6, 2],
      backgroundColor: [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
      ]
    }
  ]
})

const pieOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'right' }
  }
}

// --- Distribusi Panjang Chunk Data ---
const chunkSizeData = ref({
  labels: ['0-250', '250-500', '500-750', '750-1000', '1000-1250', '1250-1500', '1500-1750', '1750-2000', '2000-2250', '2250-2500', '2500-2750', '2750-3000'],
  datasets: [
    {
      label: 'Frekuensi',
      data: [95, 48, 30, 18, 12, 8, 5, 4, 3, 2, 1, 1],
      backgroundColor: '#42A5F5',
      barPercentage: 1.0,
      categoryPercentage: 1.0
    }
  ]
})

const histogramOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: { title: { display: true, text: 'Panjang Chunk (karakter)' } },
    y: { title: { display: true, text: 'Frekuensi' } }
  },
  plugins: {
    legend: { display: false }
  }
}

// --- Heatmap Data ---
const heatmapData = ref([
  {
    label: 'Faith.',
    values: [0.83, 1.00, 0.89, 1.00, 1.00, 0.67, 1.00, 1.00, 0.00, 0.25, 1.00, 1.00, 1.00, 1.00, 1.00]
  },
  {
    label: 'Ans.Rel.',
    values: [0.99, 0.86, 0.72, 0.97, 0.87, 0.00, 0.93, 0.00, 0.00, 0.00, 0.00, 0.93, 1.00, 0.72, 0.93]
  },
  {
    label: 'Ctx.Prec.',
    values: [0.00, 0.59, 1.00, 0.20, 1.00, 0.00, 0.00, 0.58, 0.00, 1.00, 0.00, 1.00, 0.20, 0.33, 0.00]
  },
  {
    label: 'Ctx.Rec.',
    values: [0.67, 1.00, 1.00, 0.20, 1.00, 0.25, 0.00, 1.00, 0.00, 0.00, 0.00, 1.00, 1.00, 1.00, 0.00]
  }
])

// Function to calculate color gradient from red (0.0) to green (1.0)
const getHeatmapColor = (value) => {
  // Simple mapping: 0 -> #b71c1c (red), 0.5 -> #fff59d (yellow), 1.0 -> #1b5e20 (dark green)
  // using HSL for smooth transition from 0 (red) to 120 (green)
  const hue = value * 120; // 0 to 120
  return `hsl(${hue}, 75%, 45%)`;
}
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
  overflow-y: auto;
  height: 100%;
  background: var(--bg-chat);
  color: var(--text-primary);
}

.dashboard-header {
  margin-bottom: 24px;
}

.dashboard-header h2 {
  color: var(--primary-navy);
  margin-bottom: 8px;
}

.dashboard-header p {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  padding-bottom: 40px;
}

.chart-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
}

.chart-card h3 {
  font-size: 1.1rem;
  color: var(--primary-navy);
  margin-bottom: 16px;
  text-align: center;
}

.chart-wrapper {
  flex: 1;
  position: relative;
  min-height: 300px;
}

.histogram-wrapper {
  min-height: 250px;
}

.full-width {
  grid-column: 1 / -1;
}

/* Heatmap Styles */
.heatmap-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-x: auto;
}

.heatmap-grid {
  display: grid;
  grid-template-columns: 80px repeat(15, 1fr);
  gap: 2px;
  background: #eee;
  border: 1px solid #ccc;
  padding: 2px;
}

.heatmap-cell {
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  padding: 10px 4px;
  min-width: 35px;
}

.header {
  font-weight: bold;
  background: #f8f9fa;
  color: #333;
}

.row-label {
  font-weight: bold;
  background: #f8f9fa;
  justify-content: flex-end;
  padding-right: 8px;
  color: #333;
}

.value-cell {
  font-weight: 500;
  transition: opacity 0.2s;
}
.value-cell:hover {
  opacity: 0.8;
}

.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.legend-gradient {
  width: 200px;
  height: 12px;
  background: linear-gradient(to right, hsl(0, 75%, 45%), hsl(60, 75%, 45%), hsl(120, 75%, 45%));
  border-radius: 6px;
}

@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  .full-width {
    grid-column: 1;
  }
}
</style>
