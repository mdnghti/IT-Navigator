import { create } from 'zustand'

interface TestState {
  answers: Record<number, number>
  currentIndex: number
  setAnswer: (questionId: number, answerId: number) => void
  nextQuestion: () => void
  prevQuestion: () => void
  reset: () => void
  goToQuestion: (index: number) => void
}

export const useTestStore = create<TestState>((set) => ({
  answers: {},
  currentIndex: 0,

  setAnswer: (questionId, answerId) =>
    set((state) => ({
      answers: { ...state.answers, [questionId]: answerId },
    })),

  nextQuestion: () =>
    set((state) => ({ currentIndex: state.currentIndex + 1 })),

  prevQuestion: () =>
    set((state) => ({ currentIndex: Math.max(0, state.currentIndex - 1) })),

  goToQuestion: (index) =>
    set({ currentIndex: index }),

  reset: () =>
    set({ answers: {}, currentIndex: 0 }),
}))
