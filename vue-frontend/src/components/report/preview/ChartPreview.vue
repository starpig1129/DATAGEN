<template>
  <figure class="chart-preview">
    <div v-if="block.title" class="chart-title">
      <h4>{{ block.title }}</h4>
    </div>
    
    <div class="chart-container">
      <div v-if="isLoading" class="chart-placeholder">
        <el-icon class="loading-icon">
          <Loading />
        </el-icon>
        <span>載入圖表中...</span>
      </div>
      
      <div v-else-if="hasError" class="chart-error">
        <el-icon class="error-icon">
          <Warning />
        </el-icon>
        <span>圖表載入失敗</span>
        <p class="error-details">圖表 ID: {{ block.chartId }}</p>
      </div>
      
      <div v-else class="chart-content">
        <!-- 這裡應該整合實際的圖表組件 -->
        <PlotlyChart
          v-if="chartData"
          :chart-data="chartData"
          :controls="chartControls"
          :height="300"
          class="preview-chart"
        />
        <div v-else class="chart-placeholder-content">
          <el-icon class="chart-icon">
            <TrendCharts />
          </el-icon>
          <span>圖表預覽</span>
          <p class="chart-info">類型: {{ block.chartType }}</p>
          <p class="chart-info">ID: {{ block.chartId }}</p>
        </div>
      </div>
    </div>
    
    <figcaption v-if="block.caption" class="chart-caption">
      {{ block.caption }}
    </figcaption>
  </figure>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Loading, Warning, TrendCharts } from '@element-plus/icons-vue';
import PlotlyChart from '@/components/charts/PlotlyChart.vue';
import type { ChartBlock } from '@/types/report';

interface Props {
  block: ChartBlock;
  index?: number;
}

const props = defineProps<Props>();

const isLoading = ref(true);
const hasError = ref(false);
const chartData = ref<any>(null);

const chartControls = computed(() => ({
  showLegend: true,
  showGrid: true,
  showToolbar: false, // 預覽模式不顯示工具欄
  theme: 'light' as const,
  animation: false, // 預覽模式關閉動畫提升性能
}));

const loadChartData = async () => {
  try {
    isLoading.value = true;
    hasError.value = false;
    
    // TODO: 實際從後端或 store 獲取圖表數據
    // 這裡模擬圖表數據載入
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 模擬圖表數據
    chartData.value = {
      data: [
        {
          x: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
          y: [20, 14, 23, 25, 22],
          type: 'scatter',
          mode: 'lines+markers',
          name: '數據系列',
        },
      ],
      layout: {
        title: props.block.title || '圖表',
        xaxis: { title: 'X軸' },
        yaxis: { title: 'Y軸' },
        margin: { t: 40, r: 20, b: 40, l: 40 },
      },
    };
    
    isLoading.value = false;
  } catch (error) {
    console.error('載入圖表失敗:', error);
    hasError.value = true;
    isLoading.value = false;
  }
};

onMounted(() => {
  loadChartData();
});
</script>

<style scoped>
.chart-preview {
  margin: 2rem 0;
  text-align: center;
}

.chart-title h4 {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.chart-container {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 1rem;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder,
.chart-error,
.chart-placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-regular);
  gap: 0.5rem;
}

.loading-icon {
  font-size: 2rem;
  animation: rotate 1s linear infinite;
}

.error-icon,
.chart-icon {
  font-size: 2rem;
  color: var(--el-color-warning);
}

.chart-icon {
  color: var(--el-color-primary);
}

.error-details,
.chart-info {
  font-size: 0.875rem;
  margin: 0.25rem 0;
  color: var(--el-text-color-secondary);
}

.chart-content {
  width: 100%;
  height: 100%;
}

.preview-chart {
  width: 100%;
  min-height: 300px;
}

.chart-caption {
  margin-top: 0.75rem;
  font-size: 0.875rem;
  color: var(--el-text-color-regular);
  font-style: italic;
  line-height: 1.4;
}

/* 深色主題適配 */
.dark .chart-container {
  background: var(--el-bg-color-page);
  border-color: var(--el-border-color);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .chart-preview {
    margin: 1.5rem 0;
  }
  
  .chart-container {
    padding: 0.75rem;
    min-height: 250px;
  }
  
  .preview-chart {
    min-height: 250px;
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>