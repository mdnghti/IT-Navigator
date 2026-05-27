'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { useEffect, useState } from 'react'

export default function HomePage() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20 md:py-32">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Знайдіть свій шлях<br />в IT-індустрії
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
              Професійне тестування для визначення вашої ідеальної IT-спеціальності
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4"
          >
            <Link href="/register">
              <button className="px-8 py-4 bg-accent-primary text-white font-semibold text-lg rounded-2xl hover:bg-accent-secondary transition-colors duration-200 shadow-sm hover:shadow-md min-w-[200px]">
                Почати тестування
              </button>
            </Link>

            <Link href="/login">
              <button className="px-8 py-4 bg-white text-gray-900 font-semibold text-lg rounded-2xl border-2 border-gray-200 hover:border-accent-primary transition-colors duration-200 min-w-[200px]">
                Увійти
              </button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-6 py-16">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-8"
          >
            {[
              {
                icon: '🎯',
                title: 'Точна діагностика',
                desc: 'Науково обґрунтований алгоритм аналізу ваших здібностей та інтересів'
              },
              {
                icon: '📊',
                title: 'Детальні результати',
                desc: 'Повний аналіз відповідності за всіма IT-спеціальностями з відсотками'
              },
              {
                icon: '🚀',
                title: 'Персональні рекомендації',
                desc: 'Індивідуальний план розвитку та рекомендації щодо навчання'
              },
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.5 + i * 0.1 }}
                className="bg-white p-8 rounded-3xl border border-gray-200 hover:border-accent-primary/30 transition-colors duration-200"
              >
                <div className="text-5xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-3 text-gray-900">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-6 py-16">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.8 }}
            className="bg-gradient-to-br from-accent-primary to-accent-secondary p-12 rounded-3xl text-white text-center"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Готові почати?
            </h2>
            <p className="text-xl opacity-90 mb-8">
              Пройдіть тест за 10-15 хвилин і отримайте персональні рекомендації
            </p>
            <Link href="/register">
              <button className="px-10 py-4 bg-white text-accent-primary font-bold text-lg rounded-2xl hover:shadow-xl transition-shadow duration-200">
                Почати зараз
              </button>
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  )
}
