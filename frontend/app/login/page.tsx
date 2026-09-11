import Link from "next/link";
import { Suspense } from "react";
import AuthForm from "@/components/AuthForm";

export default function LoginPage() {
  return (
    <div className="mx-auto flex max-w-sm flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Welcome back</h1>
        <p className="mt-1 text-sm text-zinc-400">Log in to fork, publish, and review.</p>
      </div>
      <Suspense fallback={null}>
        <AuthForm mode="login" />
      </Suspense>
      <p className="text-center text-sm text-zinc-500">
        New to RecipeForge?{" "}
        <Link href="/register" className="text-emerald-400 hover:underline">
          Create an account
        </Link>
      </p>
    </div>
  );
}