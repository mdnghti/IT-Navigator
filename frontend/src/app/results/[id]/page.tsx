'use client'

import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { testApi } from '@/lib/api'
import { SpecialtyTable } from '@/components/results/SpecialtyTable'
import { useEffect, useState } from 'react'

export default function ResultsPage() {
  const router = useRouter()
  const params = useParams()
  const resultId = parseInt(params.id as string)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const { data: result, isLoading, error } = useQuery({
    queryKey: ['test-result', resultId],
    queryFn: async () => {
      const response = await testApi.getResult(resultId)
      return response.data
    },
    enabled: mounted && !isNaN(resultId),
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
          <p className="text-gray-600 text-lg">Обробка результатів...</p>
        </motion.div>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white p-8 rounded-2xl border border-gray-200 text-center max-w-md shadow-sm"
        >
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-red-600 mb-2">Помилка</h2>
          <p className="text-gray-600 mb-6">Не вдалося завантажити результати</p>
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

  // Transform scores to SpecialtyResult format
  const results = Object.entries(result.scores)
    .map(([code, percentage]) => ({
      specialty_code: code,
      specialty_name: result.specialty_names?.[code] ?? code,
      score: 0,
      max_score: 100,
      percentage: percentage as number,
    }))
    .sort((a, b) => b.percentage - a.percentage)


  const topResult = results[0]

  // Check if all specialties have 100%
  const allPerfect = results.every(r => r.percentage === 100)

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-4"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", duration: 0.8 }}
            className="text-8xl mb-4"
          >
            🎉
          </motion.div>
          <h1 className="text-5xl font-bold text-gray-900">Результати тесту</h1>
          <p className="text-xl text-gray-600">
            Ваш профіль професійних уподобань
          </p>
        </motion.div>

        {/* Perfect score message */}
        {allPerfect && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, rotate: -5 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            transition={{ type: "spring", delay: 0.3 }}
            className="bg-gradient-to-r from-yellow-50 to-orange-50 p-8 rounded-3xl border-2 border-yellow-400 shadow-lg"
          >
            <div className="text-center space-y-4">
              <motion.div
                animate={{ rotate: [0, 10, -10, 10, 0] }}
                transition={{ duration: 0.5, delay: 0.5 }}
                className="text-7xl"
              >
                🧠✨
              </motion.div>
              <h2 className="text-3xl font-bold text-gray-900">
                Абсолютний результат!
              </h2>
              <p className="text-xl text-gray-700 max-w-2xl mx-auto">
                Ви відповіли правильно на всі питання! Схоже, вам варто шукати університет де викладачі розумніші за студентів 😏
              </p>
              <p className="text-lg text-gray-600">
                Але серйозно — ви маєте відмінні знання у всіх напрямках IT. Обирайте спеціальність за інтересами!
              </p>
            </div>
          </motion.div>
        )}

        {/* Top recommendation card */}
        {topResult && !allPerfect && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="bg-white p-8 rounded-3xl border-2 border-accent-primary shadow-lg"
          >
            <div className="text-center space-y-4">
              <div className="inline-block px-4 py-2 bg-orange-50 rounded-full">
                <span className="text-accent-primary font-bold text-sm">
                  🏆 РЕКОМЕНДОВАНА СПЕЦІАЛЬНІСТЬ
                </span>
              </div>
              <h2 className="text-4xl font-bold text-gray-900">
                {topResult.specialty_code}
              </h2>
              <div className="flex items-center justify-center gap-4">
                <div className="text-6xl font-bold text-accent-primary">
                  {topResult.percentage.toFixed(1)}%
                </div>
              </div>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Ця спеціальність найбільше відповідає вашим інтересам та здібностям
              </p>
            </div>
          </motion.div>
        )}

        {/* All results table */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="space-y-6"
        >
          <h3 className="text-2xl font-bold text-gray-900">
            Детальні результати за всіма спеціальностями
          </h3>
          <SpecialtyTable results={results} />
        </motion.div>

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <Link href="/dashboard">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 bg-white border border-gray-200 text-gray-900 font-semibold rounded-xl hover:border-accent-primary/50 transition-all duration-300 shadow-sm"
            >
              Повернутися до панелі
            </motion.button>
          </Link>

          {topResult && (
            <Link href={`/test/specialized/${topResult.specialty_code}`}>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-gradient-to-r from-accent-primary to-accent-secondary text-white font-bold rounded-xl shadow-sm hover:shadow-md transition-all duration-300"
              >
                Пройти спеціалізований тест →
              </motion.button>
            </Link>
          )}
        </motion.div>
      </div>
    </div>
  )
}
