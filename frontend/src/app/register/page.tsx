'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { useState } from 'react'
import { authApi } from '@/lib/api'
import { useRouter } from 'next/navigation'

export default function RegisterPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await authApi.register(formData)

      const loginResponse = await authApi.login({
        username: formData.email,
        password: formData.password,
      })

      localStorage.setItem('access_token', loginResponse.data.access_token)
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Помилка реєстрації')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-gray-50">
      <div className="w-full max-w-md">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Створити акаунт
            </h1>
            <p className="text-gray-600">Почніть свій шлях в IT</p>
          </div>

          {/* Form */}
          <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-sm">
            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-sm">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Повне ім'я
                </label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary transition-colors"
                  placeholder="Іван Іванов"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary transition-colors"
                  placeholder="your@email.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Пароль
                </label>
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary transition-colors"
                  placeholder="Мінімум 6 символів"
                  minLength={6}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-accent-primary text-white font-semibold rounded-xl hover:bg-accent-secondary transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Створення акаунта...' : 'Зареєструватися'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Вже є акаунт?{' '}
                <Link href="/login" className="text-accent-primary hover:text-accent-secondary font-medium transition-colors">
                  Увійти
                </Link>
              </p>
            </div>
          </div>

          {/* Back link */}
          <div className="text-center mt-6">
            <Link href="/" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">
              ← На главную
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
