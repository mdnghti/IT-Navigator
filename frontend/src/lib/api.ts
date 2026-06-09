import axios from 'axios'
import type {
  Question,
  AnswerSubmit,
  TestResultResponse,
  TestResult,
  LoginPayload,
  RegisterPayload,
  TokenResponse,
  User,
} from '@/types'

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1',
})

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  register: (email: string, password: string, full_name: string) =>
    api.post<User>('/auth/register', { email, password, full_name }),

  login: (email: string, password: string) => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    return api.post<TokenResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },

  getCurrentUser: () =>
    api.get<User>('/auth/me'),
}

export const testApi = {
  getGeneralQuestions: () =>
    api.get<Question[]>('/tests/general/questions'),

  submitGeneralTest: (answers: Record<number, number>) =>
    api.post<TestResultResponse>('/tests/general/submit', { answers }),

  getSpecializedQuestions: (code: string) =>
    api.get<Question[]>(`/tests/specialized/${code}/questions`),

  submitSpecializedTest: (code: string, answers: Record<number, number>) =>
    api.post<TestResultResponse>(`/tests/specialized/${code}/submit`, { answers }),

  getMyResults: () =>
    api.get<TestResult[]>('/tests/results/my'),

  getResult: (id: number) =>
    api.get<TestResult>(`/tests/results/${id}`),
}
