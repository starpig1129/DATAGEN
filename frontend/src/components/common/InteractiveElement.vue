<template>
  <component
    :is="tag"
    :class="elementClasses"
    :style="elementStyle"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
    @mousedown="handleMouseDown"
    @mouseup="handleMouseUp"
    @click="handleClick"
    @focus="handleFocus"
    @blur="handleBlur"
    @touchstart="handleTouchStart"
    @touchend="handleTouchEnd"
    v-bind="$attrs"
  >
    <!-- 漣漪效果 -->
    <div
      v-if="enableRipple && ripples.length > 0"
      class="ripple-container"
    >
      <div
        v-for="ripple in ripples"
        :key="ripple.id"
        class="ripple"
        :style="ripple.style"
        @animationend="removeRipple(ripple.id)"
      ></div>
    </div>

    <!-- 粒子效果 -->
    <div
      v-if="enableParticles && showParticles"
      class="particles-container"
    >
      <div
        v-for="particle in particles"
        :key="particle.id"
        class="particle"
        :style="particle.style"
      ></div>
    </div>

    <!-- 發光效果 -->
    <div
      v-if="enableGlow && isGlowing"
      class="glow-overlay"
      :style="glowStyle"
    ></div>

    <!-- 內容插槽 -->
    <slot
      :is-hovered="isHovered"
      :is-pressed="isPressed"
      :is-focused="isFocused"
      :is-active="isActive"
    ></slot>

    <!-- 懸停提示 -->
    <transition name="tooltip-fade">
      <div
        v-if="showTooltip && isHovered && tooltip"
        class="hover-tooltip"
        :class="tooltipPosition"
      >
        {{ tooltip }}
      </div>
    </transition>

    <!-- 狀態指示器 -->
    <div
      v-if="showStatusIndicator"
      class="status-indicator"
      :class="statusClass"
    >
      <div class="status-dot"></div>
    </div>
  </component>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'

interface Ripple {
  id: number
  style: Record<string, string>
}

interface Particle {
  id: number
  style: Record<string, string>
}

interface Props {
  tag?: string
  effect?: 'ripple' | 'glow' | 'particles' | 'bounce' | 'scale' | 'rotate' | 'slide' | 'float'
  intensity?: 'subtle' | 'normal' | 'strong'
  color?: string
  duration?: number
  delay?: number
  enableRipple?: boolean
  enableGlow?: boolean
  enableParticles?: boolean
  enableBounce?: boolean
  enableScale?: boolean
  enableRotate?: boolean
  enableSlide?: boolean
  enableFloat?: boolean
  disabled?: boolean
  loading?: boolean
  active?: boolean
  tooltip?: string
  tooltipPosition?: 'top' | 'bottom' | 'left' | 'right'
  showTooltip?: boolean
  showStatusIndicator?: boolean
  status?: 'success' | 'warning' | 'error' | 'info' | 'default'
  rippleColor?: string
  glowColor?: string
  particleColor?: string
  animateOnMount?: boolean
  animateOnChange?: boolean
  hoverDelay?: number
}

const props = withDefaults(defineProps<Props>(), {
  tag: 'div',
  effect: 'scale',
  intensity: 'normal',
  duration: 300,
  delay: 0,
  enableRipple: false,
  enableGlow: false,
  enableParticles: false,
  enableBounce: false,
  enableScale: true,
  enableRotate: false,
  enableSlide: false,
  enableFloat: false,
  disabled: false,
  loading: false,
  active: false,
  tooltipPosition: 'top',
  showTooltip: true,
  showStatusIndicator: false,
  status: 'default',
  hoverDelay: 100
})

const emit = defineEmits<{
  click: [event: MouseEvent]
  hover: [state: boolean]
  focus: [state: boolean]
  press: [state: boolean]
}>()

// 狀態
const isHovered = ref(false)
const isPressed = ref(false)
const isFocused = ref(false)
const isGlowing = ref(false)
const showParticles = ref(false)
const ripples = ref<Ripple[]>([])
const particles = ref<Particle[]>([])
const nextRippleId = ref(0)
const nextParticleId = ref(0)
const hoverTimer = ref<ReturnType<typeof setTimeout>>()
const animationElement = ref<HTMLElement>()

// 計算屬性
const isActive = computed(() => props.active || isPressed.value)

const elementClasses = computed(() => ({
  'interactive-element': true,
  'is-hovered': isHovered.value && !props.disabled,
  'is-pressed': isPressed.value && !props.disabled,
  'is-focused': isFocused.value && !props.disabled,
  'is-active': isActive.value && !props.disabled,
  'is-disabled': props.disabled,
  'is-loading': props.loading,
  'has-ripple': props.enableRipple,
  'has-glow': props.enableGlow,
  'has-particles': props.enableParticles,
  'enable-bounce': props.enableBounce,
  'enable-scale': props.enableScale,
  'enable-rotate': props.enableRotate,
  'enable-slide': props.enableSlide,
  'enable-float': props.enableFloat,
  [`effect-${props.effect}`]: true,
  [`intensity-${props.intensity}`]: true
}))

const elementStyle = computed(() => ({
  '--effect-duration': `${props.duration}ms`,
  '--effect-delay': `${props.delay}ms`,
  '--effect-color': props.color || 'var(--el-color-primary)',
  '--ripple-color': props.rippleColor || 'rgba(255, 255, 255, 0.6)',
  '--glow-color': props.glowColor || props.color || 'var(--el-color-primary)',
  '--particle-color': props.particleColor || props.color || 'var(--el-color-primary)'
}))

const statusClass = computed(() => `status-${props.status}`)

const glowStyle = computed(() => ({
  boxShadow: `0 0 20px ${props.glowColor || props.color || 'var(--el-color-primary)'}`,
  opacity: isGlowing.value ? '0.6' : '0'
}))

// Methods
const handleMouseEnter = (_event: MouseEvent) => {
  if (props.disabled) return
  
  clearTimeout(hoverTimer.value)
  hoverTimer.value = setTimeout(() => {
    isHovered.value = true
    emit('hover', true)
    
    if (props.enableGlow) {
      isGlowing.value = true
    }
    
    if (props.enableFloat) {
      animateFloat()
    }
  }, props.hoverDelay)
}

const handleMouseLeave = () => {
  if (props.disabled) return
  
  clearTimeout(hoverTimer.value)
  isHovered.value = false
  isGlowing.value = false
  showParticles.value = false
  emit('hover', false)
}

const handleMouseDown = (event: MouseEvent) => {
  if (props.disabled) return
  
  isPressed.value = true
  emit('press', true)
  
  if (props.enableRipple) {
    createRipple(event)
  }
  
  if (props.enableParticles) {
    createParticles(event)
  }
}

const handleMouseUp = () => {
  if (props.disabled) return
  
  isPressed.value = false
  emit('press', false)
}

const handleClick = (event: MouseEvent) => {
  if (props.disabled) return
  
  emit('click', event)
  
  if (props.enableBounce) {
    animateBounce()
  }
  
  if (props.enableRotate) {
    animateRotate()
  }
}

const handleFocus = () => {
  if (props.disabled) return
  
  isFocused.value = true
  emit('focus', true)
}

const handleBlur = () => {
  if (props.disabled) return
  
  isFocused.value = false
  emit('focus', false)
}

const handleTouchStart = (event: TouchEvent) => {
  if (props.disabled) return
  
  const touch = event.touches[0]
  const mouseEvent = new MouseEvent('mousedown', {
    clientX: touch.clientX,
    clientY: touch.clientY
  })
  handleMouseDown(mouseEvent)
}

const handleTouchEnd = () => {
  if (props.disabled) return
  handleMouseUp()
}

// 漣漪效果
const createRipple = (event: MouseEvent) => {
  const element = event.currentTarget as HTMLElement
  const rect = element.getBoundingClientRect()
  const size = Math.max(rect.width, rect.height)
  const x = event.clientX - rect.left - size / 2
  const y = event.clientY - rect.top - size / 2
  
  const ripple: Ripple = {
    id: nextRippleId.value++,
    style: {
      left: `${x}px`,
      top: `${y}px`,
      width: `${size}px`,
      height: `${size}px`,
      animationDuration: `${props.duration}ms`
    }
  }
  
  ripples.value.push(ripple)
}

const removeRipple = (id: number) => {
  const index = ripples.value.findIndex(ripple => ripple.id === id)
  if (index > -1) {
    ripples.value.splice(index, 1)
  }
}

// 粒子效果
const createParticles = (event: MouseEvent) => {
  const element = event.currentTarget as HTMLElement
  const rect = element.getBoundingClientRect()
  const centerX = event.clientX - rect.left
  const centerY = event.clientY - rect.top
  
  showParticles.value = true
  
  for (let i = 0; i < 8; i++) {
    const angle = (i / 8) * 2 * Math.PI
    const distance = 30 + Math.random() * 20
    const x = centerX + Math.cos(angle) * distance
    const y = centerY + Math.sin(angle) * distance
    
    const particle: Particle = {
      id: nextParticleId.value++,
      style: {
        left: `${centerX}px`,
        top: `${centerY}px`,
        '--end-x': `${x}px`,
        '--end-y': `${y}px`,
        animationDelay: `${i * 50}ms`,
        animationDuration: `${props.duration}ms`
      }
    }
    
    particles.value.push(particle)
  }
  
  setTimeout(() => {
    particles.value = []
    showParticles.value = false
  }, props.duration + 400)
}

// 動畫效果
const animateBounce = () => {
  const element = animationElement.value
  if (!element) return
  
  element.style.animation = 'none'
  void element.offsetHeight // 強制重繪
  element.style.animation = `bounce ${props.duration}ms ease-out`
}

const animateRotate = () => {
  const element = animationElement.value
  if (!element) return
  
  element.style.animation = 'none'
  void element.offsetHeight
  element.style.animation = `rotate ${props.duration}ms ease-out`
}

const animateFloat = () => {
  const element = animationElement.value
  if (!element) return
  
  element.style.animation = `float ${props.duration * 2}ms ease-in-out infinite`
}

// 監聽屬性變化
watch(() => props.active, (newVal) => {
  if (props.animateOnChange && newVal) {
    nextTick(() => {
      if (props.effect === 'bounce') animateBounce()
      if (props.effect === 'rotate') animateRotate()
      if (props.effect === 'glow') isGlowing.value = true
    })
  }
})

// 生命週期
onMounted(() => {
  animationElement.value = document.querySelector('.interactive-element') as HTMLElement
  
  if (props.animateOnMount) {
    nextTick(() => {
      if (props.effect === 'bounce') animateBounce()
      if (props.effect === 'rotate') animateRotate()
      if (props.effect === 'float') animateFloat()
    })
  }
})

onUnmounted(() => {
  clearTimeout(hoverTimer.value)
})
</script>

<style scoped>
.interactive-element {
  position: relative;
  overflow: hidden;
  transition: all var(--effect-duration, 300ms) ease;
  cursor: pointer;
  user-select: none;
  outline: none;
}

.interactive-element.is-disabled {
  cursor: not-allowed;
  opacity: 0.5;
  pointer-events: none;
}

.interactive-element.is-loading {
  pointer-events: none;
}

/* 懸停效果 */
.interactive-element.enable-scale.is-hovered {
  transform: scale(1.05);
}

.interactive-element.enable-scale.intensity-subtle.is-hovered {
  transform: scale(1.02);
}

.interactive-element.enable-scale.intensity-strong.is-hovered {
  transform: scale(1.1);
}

/* 按下效果 */
.interactive-element.enable-scale.is-pressed {
  transform: scale(0.95);
}

.interactive-element.enable-scale.intensity-subtle.is-pressed {
  transform: scale(0.98);
}

.interactive-element.enable-scale.intensity-strong.is-pressed {
  transform: scale(0.9);
}

/* 焦點效果 */
.interactive-element.is-focused {
  box-shadow: 0 0 0 2px var(--el-color-primary-light-8);
}

/* 滑動效果 */
.interactive-element.enable-slide.is-hovered {
  transform: translateY(-2px);
}

.interactive-element.enable-slide.intensity-strong.is-hovered {
  transform: translateY(-5px);
}

/* 漣漪容器 */
.ripple-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
  border-radius: inherit;
}

.ripple {
  position: absolute;
  border-radius: 50%;
  background: var(--ripple-color, rgba(255, 255, 255, 0.6));
  transform: scale(0);
  animation: ripple-animation 600ms ease-out;
}

@keyframes ripple-animation {
  to {
    transform: scale(2);
    opacity: 0;
  }
}

/* 粒子容器 */
.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: visible;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: var(--particle-color, var(--el-color-primary));
  border-radius: 50%;
  animation: particle-animation 400ms ease-out forwards;
}

@keyframes particle-animation {
  0% {
    transform: translate(0, 0) scale(1);
    opacity: 1;
  }
  100% {
    transform: translate(var(--end-x, 0), var(--end-y, 0)) scale(0);
    opacity: 0;
  }
}

/* 發光覆蓋層 */
.glow-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  border-radius: inherit;
  transition: opacity var(--effect-duration, 300ms) ease;
}

/* 懸停提示 */
.hover-tooltip {
  position: absolute;
  background: var(--el-bg-color-overlay);
  color: var(--el-text-color-primary);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 1000;
  box-shadow: var(--el-box-shadow-light);
  border: 1px solid var(--el-border-color-light);
}

.hover-tooltip.top {
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 8px;
}

.hover-tooltip.bottom {
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 8px;
}

.hover-tooltip.left {
  right: 100%;
  top: 50%;
  transform: translateY(-50%);
  margin-right: 8px;
}

.hover-tooltip.right {
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  margin-left: 8px;
}

/* 狀態指示器 */
.status-indicator {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid var(--el-bg-color);
}

.status-dot {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--el-color-info);
}

.status-success .status-dot {
  background: var(--el-color-success);
}

.status-warning .status-dot {
  background: var(--el-color-warning);
}

.status-error .status-dot {
  background: var(--el-color-danger);
}

.status-info .status-dot {
  background: var(--el-color-info);
}

/* 動畫關鍵幀 */
@keyframes bounce {
  0%, 20%, 53%, 80%, 100% {
    transform: translate3d(0, 0, 0);
  }
  40%, 43% {
    transform: translate3d(0, -8px, 0);
  }
  70% {
    transform: translate3d(0, -4px, 0);
  }
  90% {
    transform: translate3d(0, -2px, 0);
  }
}

@keyframes rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}

/* 過渡效果 */
.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 200ms ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .interactive-element.enable-scale.is-hovered {
    transform: scale(1.02);
  }
  
  .interactive-element.enable-slide.is-hovered {
    transform: translateY(-1px);
  }
  
  .hover-tooltip {
    font-size: 11px;
    padding: 6px 10px;
  }
}

/* 無障礙支援 */
@media (prefers-reduced-motion: reduce) {
  .interactive-element,
  .ripple,
  .particle,
  .glow-overlay {
    transition: none !important;
    animation: none !important;
  }
}

/* 觸控設備優化 */
@media (hover: none) {
  .interactive-element.is-hovered {
    transform: none;
  }
  
  .hover-tooltip {
    display: none;
  }
}
</style>