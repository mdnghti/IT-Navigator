'use client'

import { motion } from 'framer-motion'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useRouter, useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { testApi } from '@/lib/api'
import { useTestStore } from '@/store/testStore'
import { QuestionCard } from '@/components/test/QuestionCard'
import { TestNavigation } from '@/components/test/TestNavigation'
import type { AnswerSubmit } from '@/types'

const SPECIALTY_NAMES: Record<string, string> = {
  F1: 'Прикладна математика',
  F2: 'Інженерія програмного забезпечення',
  F3: 'Комп’ютерні науки',
  F4: 'Системний аналіз та Data Science',
  F5: 'Кібербезпека',
  F6: 'Інформаційні системи та технології',
  F7: 'Комп’ютерна інженерія',
}

export default function SpecializedTestPage() {
  const router = useRouter()
  const params = useParams()
  const specialtyCode = params.code as string
  const { answers, currentIndex, reset } = useTestStore()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    reset()
  }, [reset])

  const { data: questions, isLoading, error } = useQuery({
    queryKey: ['specialized-questions', specialtyCode],
    queryFn: async () => {
      const response = await testApi.getSpecializedQuestions(specialtyCode)
      return response.data
    },
    enabled: mounted && !!specialtyCode,
  })

  const submitMutation = useMutation({
    mutationFn: async () => {
      const submissions: AnswerSubmit[] = Object.entries(answers).map(([qId, aId]) => ({
        question_id: parseInt(qId),
        answer_id: aId,
      }))
      const response = await testApi.submitSpecialized(specialtyCode, submissions)
      return response.data
    },
    onSuccess: (data) => {
      router.push(`/results/${data.result_id}`)
    },
  })

  if (!mounted) return null

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center space-y-4"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="w-16 h-16 border-4 border-accent-primary border-t-transparent rounded-full mx-auto"
          />
          <p className="text-gray-600 text-lg">Завантаження спеціалізованого тесту...</p>
        </motion.div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white p-8 rounded-2xl border border-gray-200 text-center max-w-md shadow-sm"
        >
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-red-600 mb-2">Помилка завантаження</h2>
          <p className="text-gray-600 mb-6">Не вдалося завантажити питання спеціалізованого тесту</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-6 py-3 bg-gradient-to-r from-accent-primary to-accent-secondary text-white font-semibold rounded-xl"
          >
            Повернутися до панелі
          </button>
        </motion.div>
      </div>
    )
  }

  if (!questions || questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white p-8 rounded-2xl border border-gray-200 text-center max-w-md shadow-sm"
        >
          <div className="text-6xl mb-4">📝</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Тест не знайдено</h2>
          <p className="text-gray-600 mb-6">
            Спеціалізований тест для {SPECIALTY_NAMES[specialtyCode] ?? specialtyCode} поки недоступний
          </p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-6 py-3 bg-gradient-to-r from-accent-primary to-accent-secondary text-white font-semibold rounded-xl"
          >
            Повернутися до панелі
          </button>
        </motion.div>
      </div>
    )
  }

  const currentQuestion = questions[currentIndex]

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-2"
        >
          <div className="inline-block px-4 py-2 bg-orange-100 rounded-full mb-2">
            <span className="text-accent-secondary font-bold text-sm">
              СПЕЦІАЛІЗОВАНИЙ ТЕСТ
            </span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900">{SPECIALTY_NAMES[specialtyCode] ?? specialtyCode}</h1>
          <p className="text-gray-600">Поглиблене тестування за спеціальністю</p>
        </motion.div>

        {/* Question card */}
        <QuestionCard
          question={currentQuestion}
          totalCount={questions.length}
          currentIndex={currentIndex}
        />

        {/* Navigation */}
        <TestNavigation
          totalQuestions={questions.length}
          onSubmit={() => submitMutation.mutate()}
          isSubmitting={submitMutation.isPending}
        />

        {/* Question dots indicator */}
        <div className="flex justify-center gap-2 flex-wrap">
          {questions.map((q, idx) => (
            <motion.div
              key={q.id}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: idx * 0.02 }}
              className={`
                w-3 h-3 rounded-full transition-all duration-300
                ${idx === currentIndex
                  ? 'bg-accent-secondary w-8'
                  : answers[q.id]
                    ? 'bg-green-500'
                    : 'bg-gray-300'
                }
              `}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
