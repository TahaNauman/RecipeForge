"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import RecipeForm from "@/components/RecipeForm";
import { recipesApi, type Recipe } from "@/lib/api";

function nextVersionNumber(v: string): string {
  const [major, minor = "0"] = v.split(".");
  return `${major}.${Number(minor) + 1}`;
}

export default function RecipeEdit() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    recipesApi
      .get(id)
      .then(setRecipe)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load recipe"));
  }, [id]);

  if (error) {
    return (
      <div className="flex flex-col items-start gap-4">
        <p className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 text-sm text-zinc-400">
          {error}
        </p>
        <Link href="/recipes" className="text-sm text-emerald-400 hover:underline">
          ← Back to recipes
        </Link>
      </div>
    );
  }

  if (!recipe) {
    return <p className="text-sm text-zinc-500">Loading recipe…</p>;
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Edit recipe</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Current version{" "}
          <span className="font-mono text-emerald-400">v{recipe.version.version_number}</span>{" "}
          — saving creates{" "}
          <span className="font-mono text-emerald-400">
            v{nextVersionNumber(recipe.version.version_number)}
          </span>
          .
        </p>
      </div>
      <RecipeForm
        recipe={recipe}
        onSubmit={async (payload) => {
          await recipesApi.update(id, payload);
          router.push(`/recipes/${id}`);
        }}
        submitLabel="Save new version"
        showChangeNote
      />
    </div>
  );
}