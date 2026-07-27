import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Mail, Send } from 'lucide-react';
import { Button } from '@components/ui/button';
import { Input } from '@components/ui/input';
import { Label } from '@components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@components/ui/card';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSent(true);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="border-border/50 shadow-2xl backdrop-blur-xl">
        <CardHeader className="space-y-1 pb-6 text-center">
          <CardTitle className="text-2xl font-bold">Reset password</CardTitle>
          <CardDescription>
            {sent
              ? 'Check your email for reset instructions'
              : "Enter your email and we'll send you reset instructions"}
          </CardDescription>
        </CardHeader>
        {!sent ? (
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="reset-email">Email address</Label>
                <Input
                  id="reset-email"
                  type="email"
                  placeholder="analyst@sentinelai.dev"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="h-10"
                />
              </div>
              <Button type="submit" className="w-full h-10" variant="accent">
                <Send className="mr-2 h-4 w-4" />
                Send Reset Link
              </Button>
            </CardContent>
          </form>
        ) : (
          <CardContent className="space-y-4 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/10"
            >
              <Mail className="h-8 w-8 text-emerald-400" />
            </motion.div>
            <p className="text-sm text-muted-foreground">
              If an account exists for <span className="font-medium text-foreground">{email}</span>,
              you will receive password reset instructions shortly.
            </p>
          </CardContent>
        )}
        <CardFooter className="justify-center pb-6">
          <Link
            to="/login"
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to sign in
          </Link>
        </CardFooter>
      </Card>
    </motion.div>
  );
}
