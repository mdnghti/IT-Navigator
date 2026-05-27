'use client'

import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

const SPECIALTIES = [
  {
    code: 'F1',
    name: 'Прикладна математика',
    description: 'Аналіз та розв\'язання складних задач за допомогою математичних методів, моделювання та алгоритмів.',
    icon: '🔢',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    code: 'F2',
    name: 'Інженерія програмного забезпечення',
    description: 'Проектування, розробка, тестування та підтримка складних програмних систем і додатків.',
    icon: '💻',
    color: 'from-purple-500 to-pink-500',
  },
  {
    code: 'F3',
    name: 'Комп\'ютерні науки',
    description: 'Теоретичні основи обчислень, розробка алгоритмів, штучний інтелект та вирішення наукоємних ІТ-задач.',
    icon: '🧠',
    color: 'from-indigo-500 to-blue-500',
  },
  {
    code: 'F4',
    name: 'Системний аналіз та Data Science',
    description: 'Збір, обробка та аналіз великих масивів даних (Big Data), побудова прогностичних моделей та аналітика.',
    icon: '📊',
    color: 'from-green-500 to-emerald-500',
  },
  {
    code: 'F5',
    name: 'Кібербезпека',
    description: 'Захист інформаційних систем, комп\'ютерних мереж, програмного забезпечення та даних від кібератак і загроз.',
    icon: '🔒',
    color: 'from-red-500 to-orange-500',
  },
  {
    code: 'F6',
    name: 'Інформаційні системи та технології',
    description: 'Впровадження, інтеграція та адміністрування ІТ-інфраструктур, баз даних, хмарних сервісів та бізнес-систем.',
    icon: '⚙️',
    color: 'from-yellow-500 to-orange-500',
  },
  {
    code: 'F7',
    name: 'Комп\'ютерна інженерія',
    description: 'Розробка та проектування апаратного забезпечення комп\'ютерів, мікроконтролерів, робототехніки та вбудованих систем.',
    icon: '🔧',
    color: 'from-gray-600 to-gray-800',
  },
]

export default function SpecialtiesPage() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-6xl mx-auto space-y-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-4"
        >
          <h1 className="text-5xl font-bold text-gray-900">Оберіть спеціальність</h1>
          <p className="text-xl text-gray-600">
            Пройдіть спеціалізований тест для поглибленої оцінки ваших знань
          </p>
        </motion.div>

        {/* Back button */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <button
            onClick={() => router.push('/dashboard')}
            className="text-gray-600 hover:text-accent-primary transition-colors flex items-center gap-2"
          >
            ← Повернутися до панелі
          </button>
        </motion.div>

        {/* Specialties grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {SPECIALTIES.map((specialty, index) => (
            <Link key={specialty.code} href={`/test/specialized/${specialty.code}`}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
                whileTap={{ scale: 0.98 }}
                className="bg-white p-6 rounded-2xl border border-gray-200 hover:border-accent-primary/50 transition-all duration-300 cursor-pointer shadow-sm h-full flex flex-col"
              >
                <motion.div
                  className="text-5xl mb-4"
                  whileHover={{ scale: 1.2, rotate: 10 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  {specialty.icon}
                </motion.div>

                <div className={`inline-block px-3 py-1 bg-gradient-to-r ${specialty.color} text-white text-xs font-bold rounded-full mb-3 self-start`}>
                  {specialty.code}
                </div>

                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  {specialty.name}
                </h3>

                <p className="text-gray-600 text-sm flex-grow">
                  {specialty.description}
                </p>

                <motion.div
                  className="mt-4 text-accent-primary font-semibold flex items-center gap-2"
                  whileHover={{ x: 5 }}
                >
                  Почати тест →
                </motion.div>
              </motion.div>
            </Link>
          ))}
        </motion.div>

        {/* Info box */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="bg-blue-50 border border-blue-200 rounded-2xl p-6 text-center"
        >
          <p className="text-blue-800">
            💡 <strong>Порада:</strong> Спочатку пройдіть загальний тест, щоб визначити найбільш підходящу спеціальність
          </p>
        </motion.div>
      </div>
    </div>
  )
}
