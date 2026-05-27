'use client'

import { motion } from 'framer-motion'
import { SpecialtyResult } from '@/types'

interface SpecialtyTableProps {
  results: SpecialtyResult[]
}

export function SpecialtyTable({ results }: SpecialtyTableProps) {
  return (
    <div className="space-y-3">
      {results.map((result, index) => {
        const isTop = index === 0

        return (
          <motion.div
            key={result.specialty_code}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`
              bg-white p-6 rounded-2xl border transition-all duration-200
              ${isTop ? 'border-accent-primary shadow-sm' : 'border-gray-200'}
            `}
          >
            <div className="flex items-center gap-4 mb-4">
              <div className={`
                w-10 h-10 rounded-xl flex items-center justify-center font-bold text-lg flex-shrink-0
                ${isTop
                  ? 'bg-accent-primary text-white'
                  : 'bg-gray-100 text-gray-600'
                }
              `}>
                {index + 1}
              </div>

              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`
                    font-semibold text-sm px-2 py-1 rounded
                    ${isTop ? 'bg-orange-50 text-accent-primary' : 'bg-gray-100 text-gray-600'}
                  `}>
                    {result.specialty_code}
                  </span>
                  <h3 className="text-base font-semibold text-gray-900">
                    {result.specialty_name}
                  </h3>
                </div>
              </div>

              <div className="text-right">
                <div className={`text-2xl font-bold ${isTop ? 'text-accent-primary' : 'text-gray-900'}`}>
                  {result.percentage.toFixed(1)}%
                </div>
                {result.score > 0 && (
                  <div className="text-xs text-gray-600">
                    {result.score} / {result.max_score}
                  </div>
                )}
              </div>
            </div>

            {/* Progress bar */}
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${result.percentage}%` }}
                transition={{ delay: index * 0.1 + 0.2, duration: 0.6 }}
                className={`h-full rounded-full ${isTop ? 'bg-accent-primary' : 'bg-gray-400'}`}
              />
            </div>

            {isTop && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center gap-2 text-accent-primary text-sm font-medium">
                  <span>🏆</span>
                  <span>Рекомендована спеціальність</span>
                </div>
              </div>
            )}
          </motion.div>
        )
      })}
    </div>
  )
}
