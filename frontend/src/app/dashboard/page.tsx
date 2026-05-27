'use client'

import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { testApi } from '@/lib/api'
import { useEffect, useState } from 'react'

export default function DashboardPage() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    // Check if user is authenticated
    if (typeof window !== 'undefined' && !localStorage.getItem('access_token')) {
      router.push('/login')
    }
  }, [router])

  const { data: results, isLoading } = useQuery({
    queryKey: ['my-results'],
    queryFn: async () => {
      const response = await testApi.getMyResults()
      return response.data
    },
    enabled: mounted,
  })

  // Get top specialty from general test if available
  const generalTestResult = results?.find(r => r.test_id === 1)
  const topSpecialty = generalTestResult?.scores
    ? Object.entries(generalTestResult.scores)
        .sort(([, a], [, b]) => (b as number) - (a as number))[0]
    : null

  if (!mounted || isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="w-12 h-12 border-4 border-accent-primary border-t-transparent rounded-full"
        />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-6xl mx-auto space-y-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <h1 className="text-5xl font-bold text-gray-900">Панель керування</h1>
          <p className="text-xl text-gray-600">
            Керуйте своїми тестами та результатами
          </p>
        </motion.div>

        {/* Quick actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
        >
          <Link href="/test/general" className="h-full">
            <motion.div
              whileHover={{ scale: 1.03, y: -5 }}
              whileTap={{ scale: 0.98 }}
              className="bg-white p-8 rounded-2xl border border-gray-200 hover:border-accent-primary/50 transition-all duration-300 cursor-pointer shadow-sm h-full flex flex-col"
            >
              <motion.div
                className="text-5xl mb-4"
                whileHover={{ scale: 1.1, rotate: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                🎯
              </motion.div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Загальний тест
              </h3>
              <p className="text-gray-600 flex-grow">
                Пройдіть тестування для визначення підходящої IT-спеціальності
              </p>
            </motion.div>
          </Link>

          <Link href="/specialties" className="h-full">
            <motion.div
              whileHover={{ scale: 1.03, y: -5 }}
              whileTap={{ scale: 0.98 }}
              className="bg-white p-8 rounded-2xl border border-gray-200 hover:border-accent-secondary/50 transition-all duration-300 cursor-pointer shadow-sm h-full flex flex-col"
            >
              <motion.div
                className="text-5xl mb-4"
                whileHover={{ scale: 1.1, rotate: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                🚀
              </motion.div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Спеціалізований тест
              </h3>
              <p className="text-gray-600 flex-grow">
                {topSpecialty ? (
                  <>
                    Поглиблене тестування за спеціальністю{' '}
                    <a
                      href={`/test/specialized/${topSpecialty[0]}`}
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        router.push(`/test/specialized/${topSpecialty[0]}`)
                      }}
                      className="font-semibold text-accent-secondary hover:underline"
                    >
                      {generalTestResult?.specialty_names?.[topSpecialty[0]] ?? topSpecialty[0]}
                    </a>
                  </>
                ) : (
                  'Оберіть спеціальність для поглибленого тестування'
                )}
              </p>
            </motion.div>
          </Link>
        </motion.div>

        {/* Results history */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="space-y-6"
        >
          <h2 className="text-3xl font-bold text-gray-900">
            Історія результатів
          </h2>

          {results && results.length > 0 ? (
            <div className="space-y-4">
              {results.map((result, index) => {
                const topSpecialty = Object.entries(result.scores)
                  .sort(([, a], [, b]) => (b as number) - (a as number))[0]

                // Check if all specialties have 100%
                const allPerfect = Object.values(result.scores).every(score => score === 100)

                return (
                  <motion.div
                    key={result.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ x: 10 }}
                    className="bg-white p-6 rounded-2xl border border-gray-200 hover:border-accent-primary/50 transition-all duration-300 shadow-sm"
                  >
                    <div className="flex items-center justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center gap-3">
                          <span className="text-3xl">📊</span>
                          <div>
                            <p className="text-sm text-gray-600">
                              {new Date(result.completed_at).toLocaleDateString('ru-RU', {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </p>
                            <p className="text-lg font-bold text-gray-900">
                              {allPerfect ? (
                                <>🎯 <span className="text-accent-primary">Ідеальний результат — підходите до всіх спеціальностей!</span></>
                              ) : (
                                <>Лідер: <span className="text-accent-primary">{result.specialty_names?.[topSpecialty[0]] ?? topSpecialty[0]}</span> — {(topSpecialty[1] as number).toFixed(1)}%</>
                              )}
                            </p>
                          </div>
                        </div>
                      </div>

                      <Link href={`/results/${result.id}`}>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          className="px-6 py-3 bg-gradient-to-r from-accent-primary to-accent-secondary text-white font-semibold rounded-xl shadow-sm hover:shadow-md transition-all duration-300"
                        >
                          Детальніше →
                        </motion.button>
                      </Link>
                    </div>
                  </motion.div>
                )
              })}
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white p-12 rounded-2xl border border-gray-200 text-center space-y-4 shadow-sm"
            >
              <div className="text-6xl">📝</div>
              <h3 className="text-2xl font-bold text-gray-900">
                Немає результатів
              </h3>
              <p className="text-gray-600 max-w-md mx-auto">
                Ви ще не проходили тести. Почніть із загального тесту, щоб визначити свою спеціальність.
              </p>
              <Link href="/test/general">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="mt-4 px-8 py-4 bg-gradient-to-r from-accent-primary to-accent-secondary text-white font-bold rounded-xl shadow-sm hover:shadow-md transition-all duration-300"
                >
                  Почати тестування
                </motion.button>
              </Link>
            </motion.div>
          )}
        </motion.div>

        {/* Logout */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="text-center"
        >
          <button
            onClick={() => {
              localStorage.removeItem('access_token')
              router.push('/')
            }}
            className="text-gray-600 hover:text-red-600 transition-colors"
          >
            Вийти з акаунта
          </button>
        </motion.div>
      </div>
    </div>
  )
}
