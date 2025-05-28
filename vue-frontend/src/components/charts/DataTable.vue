<template>
  <div class="data-table-container">
    <!-- 表格工具欄 -->
    <div class="table-toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchText"
          placeholder="搜索數據..."
          :prefix-icon="Search"
          style="width: 300px"
          clearable
        />
        <el-select
          v-model="selectedColumns"
          multiple
          placeholder="選擇顯示欄位"
          style="width: 200px; margin-left: 12px"
          collapse-tags
          collapse-tags-tooltip
        >
          <el-option
            v-for="field in schema?.fields"
            :key="field.name"
            :label="field.description || field.name"
            :value="field.name"
          />
        </el-select>
      </div>
      
      <div class="toolbar-right">
        <el-button :icon="Download" @click="exportData">
          導出
        </el-button>
        <el-button :icon="Refresh" :loading="loading" @click="$emit('refresh')">
          刷新
        </el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-table
      ref="tableRef"
      :data="filteredData"
      :loading="loading"
      stripe
      border
      height="400"
      @selection-change="handleSelectionChange"
      @filter-change="handleFilterChange"
      @sort-change="handleSortChange"
    >
      <!-- 選擇欄 -->
      <el-table-column type="selection" width="55" />
      
      <!-- 索引欄 -->
      <el-table-column type="index" label="#" width="60" />
      
      <!-- 數據欄 -->
      <el-table-column
        v-for="field in visibleFields"
        :key="field.name"
        :prop="field.name"
        :label="field.description || field.name"
        :sortable="field.type === 'number' || field.type === 'date'"
        :filter-multiple="field.type === 'string'"
        :filters="getFilterOptions(field)"
        show-overflow-tooltip
      >
        <template #default="{ row }">
          <span v-if="field.type === 'date'">
            {{ formatDate(row[field.name]) }}
          </span>
          <span v-else-if="field.type === 'number'">
            {{ formatNumber(row[field.name]) }}
          </span>
          <el-tag
            v-else-if="field.name === 'status'"
            :type="getStatusType(row[field.name])"
            size="small"
          >
            {{ row[field.name] }}
          </el-tag>
          <span v-else>
            {{ row[field.name] }}
          </span>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分頁 -->
    <div class="table-pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="totalItems"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 統計信息 -->
    <div class="table-stats">
      <el-descriptions :column="4" size="small" border>
        <el-descriptions-item label="總計">
          {{ totalItems }} 條記錄
        </el-descriptions-item>
        <el-descriptions-item label="已選擇">
          {{ selectedRows.length }} 條
        </el-descriptions-item>
        <el-descriptions-item label="已篩選">
          {{ filteredData.length }} 條
        </el-descriptions-item>
        <el-descriptions-item label="數值欄位">
          {{ numericFields.length }} 個
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Search, Download, Refresh } from '@element-plus/icons-vue'
import { format } from 'date-fns'
import { zhTW } from 'date-fns/locale'
import type { DataSchema } from '@/types/visualization'

interface Props {
  data: Record<string, any>[]
  schema?: DataSchema
  loading?: boolean
}

interface Emits {
  (e: 'row-select', rows: Record<string, any>[]): void
  (e: 'filter-change', filters: Record<string, any>): void
  (e: 'sort-change', sort: { prop: string; order: string }): void
  (e: 'refresh'): void
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  loading: false
})

const emit = defineEmits<Emits>()

// 響應式狀態
const tableRef = ref()
const searchText = ref('')
const selectedColumns = ref<string[]>([])
const selectedRows = ref<Record<string, any>[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const tableFilters = ref<Record<string, any>>({})
const tableSort = ref<{ prop: string; order: string }>({ prop: '', order: '' })

// 計算屬性
const visibleFields = computed(() => {
  if (!props.schema?.fields) return []
  
  if (selectedColumns.value.length === 0) {
    return props.schema.fields
  }
  
  return props.schema.fields.filter(field => 
    selectedColumns.value.includes(field.name)
  )
})

const numericFields = computed(() => {
  return props.schema?.fields.filter(field => field.type === 'number') || []
})

const filteredData = computed(() => {
  let filtered = props.data

  // 搜索過濾
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(row => 
      Object.values(row).some(value => 
        String(value).toLowerCase().includes(search)
      )
    )
  }

  // 表格過濾
  Object.keys(tableFilters.value).forEach(key => {
    const filterValues = tableFilters.value[key]
    if (filterValues && filterValues.length > 0) {
      filtered = filtered.filter(row => 
        filterValues.includes(row[key])
      )
    }
  })

  return filtered
})

const totalItems = computed(() => props.data.length)

// const paginatedData = computed(() => {
//   const start = (currentPage.value - 1) * pageSize.value
//   const end = start + pageSize.value
//   return filteredData.value.slice(start, end)
// })

// 初始化選擇的欄位
watch(() => props.schema, (newSchema) => {
  if (newSchema?.fields && selectedColumns.value.length === 0) {
    selectedColumns.value = newSchema.fields.slice(0, 6).map(f => f.name)
  }
}, { immediate: true })

// 方法
const getFilterOptions = (field: any) => {
  if (field.type !== 'string') return []
  
  const uniqueValues = [...new Set(props.data.map(row => row[field.name]))]
    .filter(value => value != null)
    .slice(0, 20) // 限制選項數量
    
  return uniqueValues.map(value => ({
    text: String(value),
    value: value
  }))
}

const getStatusType = (status: string): 'primary' | 'success' | 'warning' | 'info' | 'danger' => {
  const statusMap: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    'success': 'success',
    'active': 'success',
    'normal': 'success',
    'warning': 'warning',
    'pending': 'warning',
    'idle': 'info',
    'error': 'danger',
    'failed': 'danger',
    'busy': 'primary'
  }
  
  return statusMap[status?.toLowerCase()] || 'info'
}

const formatDate = (date: any) => {
  if (!date) return '-'
  
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date
    return format(dateObj, 'yyyy-MM-dd HH:mm:ss', { locale: zhTW })
  } catch {
    return String(date)
  }
}

const formatNumber = (value: any) => {
  if (value == null) return '-'
  
  const num = Number(value)
  if (isNaN(num)) return String(value)
  
  // 如果是整數，直接顯示
  if (Number.isInteger(num)) {
    return num.toLocaleString()
  }
  
  // 如果是小數，保留適當精度
  return num.toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 3
  })
}

const exportData = () => {
  // 準備導出數據
  const exportData = selectedRows.value.length > 0 
    ? selectedRows.value 
    : filteredData.value

  // 創建 CSV 內容
  const headers = visibleFields.value.map(field => 
    field.description || field.name
  )
  
  const csvContent = [
    headers.join(','),
    ...exportData.map(row => 
      visibleFields.value.map(field => {
        const value = row[field.name]
        return typeof value === 'string' ? `"${value}"` : value
      }).join(',')
    )
  ].join('\n')

  // 下載檔案
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  
  link.setAttribute('href', url)
  link.setAttribute('download', `data_export_${Date.now()}.csv`)
  link.style.visibility = 'hidden'
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const handleSelectionChange = (selection: Record<string, any>[]) => {
  selectedRows.value = selection
  emit('row-select', selection)
}

const handleFilterChange = (filters: Record<string, any>) => {
  tableFilters.value = filters
  emit('filter-change', filters)
}

const handleSortChange = (sort: { prop: string; order: string }) => {
  tableSort.value = sort
  emit('sort-change', sort)
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

// 公開方法
defineExpose({
  clearSelection: () => tableRef.value?.clearSelection(),
  toggleRowSelection: (row: any, selected?: boolean) => 
    tableRef.value?.toggleRowSelection(row, selected),
  clearFilter: () => tableRef.value?.clearFilter(),
  clearSort: () => tableRef.value?.clearSort()
})
</script>

<style scoped>
.data-table-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.table-pagination {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

.table-stats {
  padding: 16px;
  background: var(--el-bg-color-page);
  border-radius: 8px;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .table-toolbar {
    flex-direction: column;
    gap: 12px;
  }
  
  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: center;
  }
  
  .toolbar-left :deep(.el-input),
  .toolbar-left :deep(.el-select) {
    width: 100% !important;
    max-width: 300px;
  }
}
</style>