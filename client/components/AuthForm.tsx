"use client";

import React, { useState } from "react";
import { supabase } from "@/lib/supabase";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, Lock, ArrowRight, Loader2 } from "lucide-react";

const AuthForm = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ email: "", password: "" });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleAuth = async () => {
    if (!form.email || !form.password) {
      toast.error("Email and password are required");
      return;
    }

    setLoading(true);
    try {
      if (isLogin) {
        const { error } = await supabase.auth.signInWithPassword({
          email: form.email,
          password: form.password,
        });
        if (error) throw error;
        toast.success("Welcome back");
      } else {
        const { error } = await supabase.auth.signUp({
          email: form.email,
          password: form.password,
        });
        if (error) throw error;
        toast.success("Account created");
      }
    } catch (err: any) {
      toast.error(err?.message || "Authentication failed");
    } finally {
      setLoading(false);
      const { data } = await supabase.auth.getSession()
      
      console.log(data?.session?.access_token)
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleAuth();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm">

        {/* Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-10 h-10 rounded-2xl bg-foreground mb-5">
            <Lock className="w-4 h-4 text-background" />
          </div>
          <AnimatePresence mode="wait">
            <motion.div
              key={isLogin ? "login" : "signup"}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2 }}
            >
              <h1 className="text-xl font-semibold tracking-tight text-foreground">
                {isLogin ? "Welcome back" : "Create an account"}
              </h1>
              <p className="mt-1.5 text-sm text-muted-foreground">
                {isLogin
                  ? "Sign in to continue"
                  : "Get started for free today"}
              </p>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-border bg-background/60 backdrop-blur-sm p-6 shadow-sm">

          {/* Tab toggle */}
          <div className="relative flex bg-muted rounded-xl p-1 mb-5">
            <motion.div
              layout
              transition={{ type: "spring", stiffness: 500, damping: 35 }}
              className="absolute inset-y-1 w-[calc(50%-2px)] rounded-lg bg-background shadow-sm"
              style={{ left: isLogin ? "4px" : "calc(50% + 2px)" }}
            />
            {["Login", "Sign Up"].map((label, i) => (
              <button
                key={label}
                onClick={() => setIsLogin(i === 0)}
                className={`relative z-10 w-1/2 py-1.5 text-sm font-medium transition-colors duration-150 ${
                  isLogin === (i === 0)
                    ? "text-foreground"
                    : "text-muted-foreground"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Fields */}
          <div className="space-y-3">
            <FieldInput
              icon={<Mail className="w-4 h-4" />}
              name="email"
              type="email"
              placeholder="Email address"
              value={form.email}
              onChange={handleChange}
              onKeyDown={handleKeyDown}
            />
            <FieldInput
              icon={<Lock className="w-4 h-4" />}
              name="password"
              type="password"
              placeholder="Password"
              value={form.password}
              onChange={handleChange}
              onKeyDown={handleKeyDown}
            />
          </div>

          {/* Forgot password */}
          {isLogin && (
            <div className="mt-2.5 text-right">
              <button className="text-xs text-muted-foreground hover:text-foreground transition-colors">
                Forgot password?
              </button>
            </div>
          )}

          {/* Submit */}
          <button
            onClick={handleAuth}
            disabled={loading}
            className="mt-5 w-full flex items-center justify-center gap-2 h-10 px-4 rounded-xl bg-foreground text-background text-sm font-medium hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                {isLogin ? "Sign in" : "Create account"}
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>

        {/* Footer switch */}
        <p className="mt-5 text-center text-xs text-muted-foreground">
          {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="font-medium text-foreground hover:underline underline-offset-4"
          >
            {isLogin ? "Sign up" : "Sign in"}
          </button>
        </p>
      </div>
    </div>
  );
};

/* ── Field input sub-component ── */
type FieldProps = {
  icon: React.ReactNode;
  name: string;
  type?: string;
  placeholder: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
};

const FieldInput = ({
  icon,
  name,
  type = "text",
  placeholder,
  value,
  onChange,
  onKeyDown,
}: FieldProps) => (
  <div className="relative group">
    <span className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-foreground transition-colors">
      {icon}
    </span>
    <input
      name={name}
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      onKeyDown={onKeyDown}
      className="w-full h-10 pl-10 pr-3.5 rounded-xl border border-border bg-muted/40 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-foreground/20 focus:border-foreground/30 transition-all"
    />
  </div>
);

export default AuthForm;