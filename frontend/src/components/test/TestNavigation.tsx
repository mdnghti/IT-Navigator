'use client'

import { useTestStore } from '@/store/testStore'

interface TestNavigationProps {
  totalQuestions: number
  onSubmit: () => void
  isSubmitting: boolean
}

export function TestNavigation({ totalQuestions, onSubmit, isSubmitting }: TestNavigationProps) {
  const { currentIndex, nextQuestion, prevQuestion, answers } = useTestStore()
  const isFirstQuestion = currentIndex === 0
  const isLastQuestion = currentIndex === totalQuestions - 1
  const answeredCount = Object.keys(answers).length
  const canSubmit = answeredCount === totalQuestions

  return (
    <div className="flex items-center justify-between gap-4">
      <button
        onClick={prevQuestion}
        disabled={isFirstQuestion}
        className={`
          px-6 py-3 rounded-xl font-medium transition-all duration-200
          ${isFirstQuestion
            ? 'opacity-40 cursor-not-allowed bg-white border border-gray-200'
            : 'bg-white border border-gray-200 hover:border-accent-primary'
          }
        `}
      >
        ← Назад
      </button>

      <div className="text-center">
        <p className="text-sm text-gray-600">
          Відповіли: <span className="text-accent-primary font-semibold">{answeredCount}</span> / {totalQuestions}
        </p>
      </div>

      {!isLastQuestion ? (
        <button
          onClick={nextQuestion}
          className="px-6 py-3 bg-accent-primary text-white font-medium rounded-xl hover:bg-accent-secondary transition-all duration-200"
        >
          Далі →
        </button>
      ) : (
        <button
          onClick={onSubmit}
          disabled={!canSubmit || isSubmitting}
          className={`
            px-8 py-3 rounded-xl font-semibold transition-all duration-200
            ${canSubmit && !isSubmitting
              ? 'bg-green-500 text-white hover:bg-green-600'
              : 'opacity-40 cursor-not-allowed bg-white border border-gray-200'
            }
          `}
        >
          {isSubmitting ? 'Відправка...' : canSubmit ? 'Завершити ✓' : 'Дайте відповідь на всі'}
        </button>
      )}
    </div>
  )
}
