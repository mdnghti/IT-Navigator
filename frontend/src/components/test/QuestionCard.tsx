'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { Question } from '@/types'
import { useTestStore } from '@/store/testStore'

interface QuestionCardProps {
  question: Question
  totalCount: number
  currentIndex: number
}

export function QuestionCard({ question, totalCount, currentIndex }: QuestionCardProps) {
  const { answers, setAnswer } = useTestStore()
  const selectedAnswerId = answers[question.id]

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={question.id}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ duration: 0.3 }}
        className="space-y-6"
      >
        {/* Progress */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600 font-medium">
              Питання {currentIndex + 1} з {totalCount}
            </span>
            <span className="text-accent-primary font-semibold">
              {Math.round(((currentIndex + 1) / totalCount) * 100)}%
            </span>
          </div>

          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-accent-primary rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${((currentIndex + 1) / totalCount) * 100}%` }}
              transition={{ duration: 0.4 }}
            />
          </div>
        </div>

        {/* Question */}
        <div className="bg-white p-6 md:p-8 rounded-2xl border border-gray-200 shadow-sm">
          <h2 className="text-xl md:text-2xl font-semibold text-gray-900 leading-relaxed">
            {question.text}
          </h2>
        </div>

        {/* Answers */}
        <div className="space-y-3">
          {question.answers.map((answer) => {
            const isSelected = selectedAnswerId === answer.id

            return (
              <button
                key={answer.id}
                onClick={() => setAnswer(question.id, answer.id)}
                className={`
                  w-full p-4 rounded-xl text-left transition-all duration-200
                  ${isSelected
                    ? 'bg-orange-50 border-2 border-accent-primary shadow-sm'
                    : 'bg-white border border-gray-200 hover:border-accent-primary/50'
                  }
                `}
              >
                <div className="flex items-center gap-3">
                  <div className={`
                    w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0
                    ${isSelected ? 'border-accent-primary' : 'border-gray-300'}
                  `}>
                    {isSelected && (
                      <div className="w-2.5 h-2.5 rounded-full bg-accent-primary" />
                    )}
                  </div>

                  <span className={`
                    font-medium
                    ${isSelected ? 'text-gray-900' : 'text-gray-600'}
                  `}>
                    {answer.text}
                  </span>
                </div>
              </button>
            )
          })}
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
