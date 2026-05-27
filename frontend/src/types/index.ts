export interface User {
  id: number
  email: string
  full_name: string | null
  is_active: boolean
  is_admin: boolean
}

export interface Answer {
  id: number
  text: string
}

export interface Question {
  id: number
  text: string
  answers: Answer[]
}

export interface AnswerSubmit {
  question_id: number
  answer_id: number
}

export interface SpecialtyResult {
  specialty_code: string
  specialty_name: string
  score: number
  max_score: number
  percentage: number
}

export interface TestResultResponse {
  results: SpecialtyResult[]
  recommended_specialty: SpecialtyResult | null
  result_id: number
}

export interface TestResult {
  id: number
  user_id: number
  test_id: number
  payload: { answers: AnswerSubmit[] }
  scores: Record<string, number>
  completed_at: string
  specialty_names?: Record<string, string>
}


export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  full_name?: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}
