'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { School, Fingerprint, Bell, BarChart3, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  fadeInUp,
  staggerContainer,
  staggerItem,
  slideInLeft,
  slideInRight,
} from '@/lib/animations';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Animated background shapes */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-400/20 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-indigo-400/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10">
        {/* Header */}
        <motion.header
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          className="container mx-auto px-4 sm:px-6 lg:px-8 py-6"
        >
          <div className="flex items-center justify-between">
            <motion.div
              initial="hidden"
              animate="visible"
              variants={slideInLeft}
              className="flex items-center gap-3"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <School className="h-6 w-6 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                School Biometric
              </span>
            </motion.div>
            <motion.nav
              initial="hidden"
              animate="visible"
              variants={slideInRight}
              className="flex items-center gap-4"
            >
              <Link
                href="/register"
                className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary transition-colors"
              >
                Register
              </Link>
              <Link href="/login">
                <Button variant="outline" size="sm">
                  Login
                </Button>
              </Link>
            </motion.nav>
          </div>
        </motion.header>

        {/* Hero Section */}
        <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            transition={{ delay: 0.2 }}
            className="max-w-4xl mx-auto text-center"
          >
            <motion.h1
              initial="hidden"
              animate="visible"
              variants={fadeInUp}
              transition={{ delay: 0.3 }}
              className="text-5xl sm:text-6xl font-bold text-gray-900 dark:text-white mb-6 leading-tight"
            >
              Automated School
              <motion.span
                initial="hidden"
                animate="visible"
                variants={fadeInUp}
                transition={{ delay: 0.4 }}
                className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600"
              >
                Attendance Management
              </motion.span>
            </motion.h1>
            <motion.p
              initial="hidden"
              animate="visible"
              variants={fadeInUp}
              transition={{ delay: 0.5 }}
              className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto"
            >
              Streamline student attendance tracking with biometric fingerprint technology.
              Real-time notifications and comprehensive reporting for modern schools.
            </motion.p>
            <motion.div
              initial="hidden"
              animate="visible"
              variants={fadeInUp}
              transition={{ delay: 0.6 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Link href="/register">
                <Button size="lg" className="w-full sm:w-auto">
                  Get Started
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/login">
                <Button size="lg" variant="outline" className="w-full sm:w-auto">
                  Sign In
                </Button>
              </Link>
            </motion.div>
          </motion.div>

          {/* Features Grid */}
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-100px' }}
            variants={staggerContainer}
            className="mt-32 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto"
          >
            <motion.div
              variants={staggerItem}
              whileHover={{ scale: 1.02, y: -4 }}
              className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-gray-200/50 dark:border-gray-700/50 transition-shadow hover:shadow-xl"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/30 mb-4">
                <Fingerprint className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Biometric Enrollment
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                Remote fingerprint enrollment from the web interface. No need to manually operate devices.
              </p>
            </motion.div>

            <motion.div
              variants={staggerItem}
              whileHover={{ scale: 1.02, y: -4 }}
              className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-gray-200/50 dark:border-gray-700/50 transition-shadow hover:shadow-xl"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-900/30 mb-4">
                <Bell className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Real-time Notifications
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                Parents receive instant SMS notifications when their children check in or out.
              </p>
            </motion.div>

            <motion.div
              variants={staggerItem}
              whileHover={{ scale: 1.02, y: -4 }}
              className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-gray-200/50 dark:border-gray-700/50 transition-shadow hover:shadow-xl"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-900/30 mb-4">
                <BarChart3 className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Comprehensive Reports
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                Track attendance patterns, generate reports, and analyze student attendance data.
              </p>
            </motion.div>
          </motion.div>
        </main>

        {/* Footer */}
        <motion.footer
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          transition={{ delay: 0.3 }}
          className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 mt-20 border-t border-gray-200/50 dark:border-gray-700/50"
        >
          <div className="text-center text-sm text-gray-600 dark:text-gray-400">
            © 2024 School Biometric System. Built for modern schools in Kenya.
          </div>
        </motion.footer>
      </div>
    </div>
  );
}
