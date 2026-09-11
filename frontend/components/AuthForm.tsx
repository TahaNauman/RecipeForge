"use client";

import { useState, type FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/auth";

const inputClass =
  "w-full rounded-md border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-emerald-500";

export default function AuthForm({ mode }: { mode: "login" | "register" }) {
  const isLogin = mode === "login";
  const { login, register } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    const form = new FormData(e.currentTarget);
    const username = String(form.get("username") ?? "");
    const email = String(form.get("email") ?? "");
    const password = String(form.get("password") ?? "");
    const confirm = String(form.get("confirm") ?? "");

    if (isLogin && !username) return setError("Enter your username or email");
    if (!isLogin) {
      if (username.length < 3) return setError("Username must be at least 3 characters");
      if (!/^[a-zA-Z0-9_]+$/.test(username))
        return setError("Username may only contain letters, numbers, and underscores");
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return setError("Enter a valid email");
      if (password.length < 8) return setError("Password must be at least 8 characters");
      if (password !== confirm) return setError("Passwords do not match");
    }
    if (isLogin && !password) return setError("Enter your password");

    setBusy(true);
    try {
      if (isLogin) await login(username, password);
      else await register({ username, email, password });

      const next = searchParams.get("next");
      router.push(typeof next === "string" && next.startsWith("/") ? next : "/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
      <label className="flex flex-col gap-1 text-sm text-zinc-400">
        {isLogin ? "Username or email" : "Username"}
        <input
          name="username"
          type="text"
          autoComplete={isLogin ? "username" : "username"}
          className={inputClass}
        />
      </label>

      {!isLogin && (
        <label className="flex flex-col gap-1 text-sm text-zinc-400">
          Email
          <input name="email" type="email" autoComplete="email" className={inputClass} />
        </label>
      )}

      <label className="flex flex-col gap-1 text-sm text-zinc-400">
        Password
        <input
          name="password"
          type="password"
          autoComplete={isLogin ? "current-password" : "new-password"}
          className={inputClass}
        />
      </label>

      {!isLogin && (
        <label className="flex flex-col gap-1 text-sm text-zinc-400">
          Confirm password
          <input name="confirm" type="password" autoComplete="new-password" className={inputClass} />
        </label>
      )}

      {error && (
        <p className="rounded-md border border-red-900 bg-red-950/50 px-3 py-2 text-sm text-red-400">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={busy}
        className="rounded-md bg-emerald-500 px-4 py-2 font-medium text-zinc-950 hover:bg-emerald-400 disabled:opacity-50"
      >
        {busy ? "Please wait…" : isLogin ? "Log in" : "Create account"}
      </button>
    </form>
  );
}