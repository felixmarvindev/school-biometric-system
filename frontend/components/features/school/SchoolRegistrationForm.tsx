/**
 * School Registration Form Component
 * 
 * Requirements:
 * - Use React Hook Form with Zod validation
 * - Use shadcn/ui components (Card, Form, Input, Textarea, Button)
 * - Accept onSubmit, isLoading, and error props
 * - Be fully accessible and responsive
 * - Follow shadcn/ui New York style
 * 
 * Required shadcn/ui components to install:
 * - npx shadcn@latest add card
 * - npx shadcn@latest add form
 * - npx shadcn@latest add input
 * - npx shadcn@latest add textarea
 * - npx shadcn@latest add label
 * - npx shadcn@latest add alert
 * - npx shadcn@latest add separator
 */

'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion } from 'framer-motion';
import { School, Loader2, ArrowRight } from 'lucide-react';
import { fadeInUp, staggerContainer, staggerItem } from '@/lib/animations';
import { schoolRegistrationSchema, type SchoolRegistrationFormData } from '@/lib/validations/school';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';

interface SchoolRegistrationFormProps {
  onSubmit: (data: SchoolRegistrationFormData) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
  onSuccess?: () => void;
}

/**
 * School Registration Form Component
 */
export function SchoolRegistrationForm({
  onSubmit,
  isLoading = false,
  error = null,
  onSuccess,
}: SchoolRegistrationFormProps) {
  const form = useForm<SchoolRegistrationFormData>({
    resolver: zodResolver(schoolRegistrationSchema),
    defaultValues: {
      name: '',
      code: '',
      address: '',
      phone: '',
      email: '',
    },
  });

  const handleSubmit = async (data: SchoolRegistrationFormData) => {
    try {
      await onSubmit(data);
      form.reset();
      onSuccess?.();
    } catch (err) {
      // Error handling is done by parent component
      console.error('Form submission error:', err);
    }
  };

  const handleCodeChange = (value: string) => {
    // Automatically convert to uppercase as user types
    form.setValue('code', value.toUpperCase());
  };

  return (
    <Card className="w-full max-w-2xl shadow-2xl border-0 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm">
      <CardHeader className="space-y-3 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 rounded-t-lg border-b border-blue-100 dark:border-blue-900/50">
        <div className="flex items-center gap-3">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-500/30">
            <School className="h-7 w-7 text-white" />
          </div>
          <div className="space-y-1">
            <CardTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 bg-clip-text text-transparent">
              Register Your School
            </CardTitle>
            <CardDescription className="text-base text-gray-600 dark:text-gray-300">
              Create an account for your school to get started
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6">
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleSubmit)}
            className="space-y-6"
            aria-label="School registration form"
          >
            {/* General form error */}
            {error && (
              <Alert variant="destructive" className="border-red-200 dark:border-red-900/50 bg-red-50 dark:bg-red-950/20">
                <AlertDescription className="text-red-800 dark:text-red-200">{error}</AlertDescription>
              </Alert>
            )}

            {/* Required Fields Section */}
            <motion.div
              initial="hidden"
              animate="visible"
              variants={staggerContainer}
              className="space-y-4"
            >
              <motion.div
                variants={fadeInUp}
                className="flex items-center gap-2 pb-2"
              >
                <div className="h-1 w-1 rounded-full bg-blue-500" />
                <h3 className="text-sm font-semibold uppercase tracking-wide text-blue-600 dark:text-blue-400">
                  Required Information
                </h3>
              </motion.div>

              {/* School Name */}
              <motion.div variants={staggerItem}>
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-gray-700 dark:text-gray-200 font-medium">
                        School Name <span className="text-red-500">*</span>
                      </FormLabel>
                      <FormControl>
                        <Input
                          placeholder="e.g., Greenfield Academy"
                          aria-required="true"
                          disabled={isLoading}
                          className="border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-500/20 transition-colors"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </motion.div>

              {/* School Code */}
              <motion.div variants={staggerItem}>
                <FormField
                  control={form.control}
                  name="code"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-gray-700 dark:text-gray-200 font-medium">
                        School Code <span className="text-red-500">*</span>
                      </FormLabel>
                      <FormControl>
                        <Input
                          placeholder="e.g., GFA-001"
                          aria-required="true"
                          disabled={isLoading}
                          className="border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-500/20 transition-colors font-mono"
                          {...field}
                          onChange={(e) => handleCodeChange(e.target.value)}
                        />
                      </FormControl>
                      <FormDescription className="text-gray-600 dark:text-gray-400">
                        Code will be automatically converted to uppercase. Only letters, numbers, and hyphens allowed.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </motion.div>
            </motion.div>

            <Separator className="my-6 bg-gradient-to-r from-transparent via-gray-300 to-transparent dark:via-gray-700" />

            {/* Optional Fields Section */}
            <motion.div
              initial="hidden"
              animate="visible"
              variants={staggerContainer}
              transition={{ delay: 0.2 }}
              className="space-y-4"
            >
              <motion.div
                variants={fadeInUp}
                className="flex items-center gap-2 pb-2"
              >
                <div className="h-1 w-1 rounded-full bg-purple-500" />
                <h3 className="text-sm font-semibold uppercase tracking-wide text-purple-600 dark:text-purple-400">
                  Optional Information
                </h3>
              </motion.div>

              {/* Address */}
              <motion.div variants={staggerItem}>
                <FormField
                  control={form.control}
                  name="address"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-gray-700 dark:text-gray-200 font-medium">
                        Address{' '}
                        <span className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          (Optional)
                        </span>
                      </FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Enter school address"
                          disabled={isLoading}
                          className="min-h-20 resize-none border-gray-300 dark:border-gray-600 focus:border-purple-500 focus:ring-purple-500/20 transition-colors"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </motion.div>

              {/* Phone */}
              <motion.div variants={staggerItem}>
                <FormField
                  control={form.control}
                  name="phone"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-gray-700 dark:text-gray-200 font-medium">
                        Phone Number{' '}
                        <span className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          (Optional)
                        </span>
                      </FormLabel>
                      <FormControl>
                        <Input
                          type="tel"
                          placeholder="e.g., +254712345678"
                          disabled={isLoading}
                          className="border-gray-300 dark:border-gray-600 focus:border-purple-500 focus:ring-purple-500/20 transition-colors"
                          {...field}
                        />
                      </FormControl>
                      <FormDescription className="text-gray-600 dark:text-gray-400">
                        10-15 digits, optional country code prefix
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </motion.div>

              {/* Email */}
              <motion.div variants={staggerItem}>
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-gray-700 dark:text-gray-200 font-medium">
                        Email Address{' '}
                        <span className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          (Optional)
                        </span>
                      </FormLabel>
                      <FormControl>
                        <Input
                          type="email"
                          placeholder="e.g., admin@school.ac.ke"
                          disabled={isLoading}
                          className="border-gray-300 dark:border-gray-600 focus:border-purple-500 focus:ring-purple-500/20 transition-colors"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </motion.div>
            </motion.div>

            {/* Submit Button */}
            <div className="pt-4">
              <Button
                type="submit"
                className="w-full md:w-auto md:min-w-[200px] bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg shadow-blue-500/30 hover:shadow-blue-500/40 transition-all duration-200"
                disabled={isLoading}
                aria-label={isLoading ? 'Registering school...' : 'Register school'}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Registering...
                  </>
                ) : (
                  <>
                    Register School
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}

