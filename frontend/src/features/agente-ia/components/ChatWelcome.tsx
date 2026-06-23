import { BrainCircuit } from 'lucide-react'
import { motion } from 'framer-motion'
import { useAuth } from '@/contexts/AuthContext'

export function ChatWelcome() {
  const { user } = useAuth()
  const firstName = user?.nombre?.split(' ')[0] ?? 'Usuario'

  return (
    <div className="flex flex-col items-center justify-center h-full px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="flex flex-col items-center gap-3 w-full max-w-2xl"
      >
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1, duration: 0.35 }}
          className="flex items-center gap-2.5"
        >
          <BrainCircuit className="w-7 h-7 shrink-0 text-violet-500" />
          <span className="text-2xl font-semibold text-foreground">
            Hola, {firstName}
          </span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.4 }}
          className="text-4xl md:text-5xl font-bold tracking-tight text-center leading-tight"
        >
          ¿Por dónde empezamos?
        </motion.h1>
      </motion.div>
    </div>
  )
}
