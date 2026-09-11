"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import RecipeForm from "@/components/RecipeForm";
import { recipesApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function CreateRecipePage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.replace("/login?next=/recipes/create");
  }, [loading, user, router]);

  if (loading) {
    return <p className="text-sm text-zinc-500">…</p>;
  }

  if (!user) {
    return (
      <p className="rounded-lg border border-dashed border-zinc-800 p-10 text-center text-sm text-zinc-500">
        Please{" "}
        <Link href="/login?next=/recipes/create" className="text-emerald-400 hover:underline">
          log in
        </Link>{" "}
        to create a recipe.
      </p>
    );
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">New recipe</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Created as <span className="font-mono text-emerald-400">v1.0</span>.
        </p>
      </div>
      <RecipeForm
        onSubmit={async (payload) => {
          const created = await recipesApi.create(payload);
          router.push(`/recipes/${created.id}`);
        }}
        submitLabel="Publish recipe"
      />
    </div>
  );
}