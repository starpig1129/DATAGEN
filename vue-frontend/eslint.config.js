import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import * as parserVue from 'vue-eslint-parser'
import configTypescript from '@typescript-eslint/eslint-plugin'
import parserTypescript from '@typescript-eslint/parser'

export default [
  // JavaScript 推薦配置
  js.configs.recommended,
  
  // Vue 推薦配置
  ...pluginVue.configs['flat/recommended'],
  
  // 全局忽略文件
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      'public/**',
      '*.d.ts',
      'auto-imports.d.ts',
      'components.d.ts'
    ]
  },
  
  // TypeScript 和 Vue 文件配置
  {
    files: ['**/*.vue', '**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: parserVue,
      parserOptions: {
        parser: parserTypescript,
        extraFileExtensions: ['.vue'],
        sourceType: 'module',
        ecmaVersion: 'latest'
      },
      globals: {
        // 瀏覽器全局變量
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        process: 'readonly',
        // Node.js 全局變量
        __dirname: 'readonly',
        __filename: 'readonly',
        // Vite 全局變量
        import: 'readonly'
      }
    },
    plugins: {
      '@typescript-eslint': configTypescript,
      vue: pluginVue
    },
    rules: {
      // Vue 規則
      'vue/multi-word-component-names': 'off',
      'vue/component-definition-name-casing': ['error', 'PascalCase'],
      'vue/component-name-in-template-casing': ['error', 'PascalCase'],
      'vue/define-props-declaration': ['error', 'type-based'],
      'vue/define-emits-declaration': ['error', 'type-based'],
      'vue/no-unused-vars': 'error',
      'vue/no-unused-components': 'warn',
      'vue/no-unused-refs': 'warn',
      'vue/prefer-import-from-vue': 'error',
      'vue/no-root-v-if': 'warn',
      'vue/padding-line-between-blocks': 'warn',
      'vue/block-order': ['error', {
        order: ['template', 'script', 'style']
      }],
      
      // TypeScript 規則
      '@typescript-eslint/no-unused-vars': ['error', { 
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_'
      }],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/prefer-const': 'error',
      '@typescript-eslint/no-var-requires': 'error',
      
      // JavaScript 通用規則
      'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      'no-unused-vars': 'off', // 由 TypeScript 規則處理
      'prefer-const': 'error',
      'no-var': 'error',
      'object-shorthand': 'error',
      'prefer-template': 'error',
      'template-curly-spacing': 'error',
      'arrow-spacing': 'error',
      'comma-dangle': ['error', 'never'],
      'quotes': ['error', 'single', { avoidEscape: true }],
      'semi': ['error', 'never'],
      'indent': ['error', 2, { SwitchCase: 1 }],
      'space-before-function-paren': ['error', {
        anonymous: 'always',
        named: 'never',
        asyncArrow: 'always'
      }],
      'keyword-spacing': 'error',
      'space-infix-ops': 'error',
      'eol-last': 'error',
      'no-trailing-spaces': 'error',
      'no-multiple-empty-lines': ['error', { max: 1 }],
      'padded-blocks': ['error', 'never'],
      'space-in-parens': ['error', 'never'],
      'array-bracket-spacing': ['error', 'never'],
      'object-curly-spacing': ['error', 'always'],
      'max-len': ['warn', { 
        code: 100, 
        ignoreUrls: true,
        ignoreStrings: true,
        ignoreTemplateLiterals: true
      }],
      
      // 導入規則
      'sort-imports': ['error', {
        ignoreCase: false,
        ignoreDeclarationSort: true,
        ignoreMemberSort: false,
        memberSyntaxSortOrder: ['none', 'all', 'multiple', 'single'],
        allowSeparatedGroups: true
      }]
    }
  },
  
  // JavaScript 文件特殊配置
  {
    files: ['**/*.js'],
    languageOptions: {
      sourceType: 'module',
      ecmaVersion: 'latest'
    },
    rules: {
      '@typescript-eslint/no-var-requires': 'off'
    }
  },
  
  // 配置文件特殊設置
  {
    files: ['vite.config.*', 'vitest.config.*', 'cypress.config.*', 'playwright.config.*'],
    languageOptions: {
      globals: {
        process: 'readonly'
      }
    },
    rules: {
      'no-console': 'off'
    }
  }
]