// Apollo GraphQL 客戶端配置

import { ApolloClient, InMemoryCache, createHttpLink, split } from '@apollo/client/core'
import { GraphQLWsLink } from '@apollo/client/link/subscriptions'
import { getMainDefinition } from '@apollo/client/utilities'
import { createClient } from 'graphql-ws'
import { setContext } from '@apollo/client/link/context'

// 環境配置
const GRAPHQL_HTTP_URL = import.meta.env.VITE_GRAPHQL_HTTP_URL || 'http://localhost:8000/graphql'
const GRAPHQL_WS_URL = import.meta.env.VITE_GRAPHQL_WS_URL || 'ws://localhost:8000/graphql/ws'

// HTTP 連接配置
const httpLink = createHttpLink({
  uri: GRAPHQL_HTTP_URL,
  credentials: 'include'
})

// 認證 Link
const authLink = setContext((_, { headers }) => {
  // 從 localStorage 獲取 token
  const token = localStorage.getItem('auth_token')
  
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json'
    }
  }
})

// WebSocket 連接配置
const wsLink = new GraphQLWsLink(
  createClient({
    url: GRAPHQL_WS_URL,
    connectionParams: () => {
      const token = localStorage.getItem('auth_token')
      return {
        authorization: token ? `Bearer ${token}` : ''
      }
    },
    retryAttempts: 5,
    shouldRetry: () => true
  })
)

// 分離 HTTP 和 WebSocket 請求
const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query)
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    )
  },
  wsLink,
  authLink.concat(httpLink)
)

// Apollo Client 緩存配置
const cache = new InMemoryCache({
  typePolicies: {
    Query: {
      fields: {
        messages: {
          merge(existing = [], incoming) {
            return [...existing, ...incoming]
          }
        },
        agents: {
          merge(existing = [], incoming) {
            return incoming
          }
        },
        files: {
          merge(existing = [], incoming) {
            return incoming
          }
        }
      }
    },
    Agent: {
      fields: {
        status: {
          merge(existing, incoming) {
            return incoming
          }
        }
      }
    },
    Message: {
      keyFields: ['id']
    }
  },
  addTypename: true
})

// Apollo Client 實例
export const apolloClient = new ApolloClient({
  link: splitLink,
  cache,
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all',
      fetchPolicy: 'cache-and-network'
    },
    query: {
      errorPolicy: 'all',
      fetchPolicy: 'cache-first'
    },
    mutate: {
      errorPolicy: 'all'
    }
  },
  connectToDevTools: import.meta.env.DEV
})

// 錯誤處理
apolloClient.onResetStore(() => {
  console.log('Apollo store reset')
})

// 清除緩存函數
export const clearApolloCache = () => {
  return apolloClient.clearStore()
}

// 重置客戶端
export const resetApolloClient = () => {
  return apolloClient.resetStore()
}

// 更新認證 token
export const updateAuthToken = (token: string | null) => {
  if (token) {
    localStorage.setItem('auth_token', token)
  } else {
    localStorage.removeItem('auth_token')
  }
  // 重置客戶端以應用新的認證
  resetApolloClient()
}