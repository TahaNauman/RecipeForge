"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { recipesApi, type Recipe, type RecipeVersionHeader } from "@/lib/api";

export default function RecipeHistory() {
  const { id } = useParams<{ id: string }>();
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [versions, setVersions] = useState<RecipeVersionHeader[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([recipesApi.get(id), recipesApi.versions(id)])
      .then(([recipe, versions]) => {
        setRecipe(recipe);
        setVersions(versions);
      })
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Could not load history")
      );
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
    return <p className="text-sm text-zinc-500">Loading history…</p>;
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <div>
        <Link
          href={`/recipes/${recipe.id}`}
          className="text-sm text-emerald-400 hover:underline"
        >
          ← Back to recipe
        </Link>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">
          Version history
        </h1>
        <p className="mt-1 text-sm text-zinc-400">
          {recipe.title} · {versions.length}{" "}
          {versions.length === 1 ? "version" : "versions"}
        </p>
      </div>
      <ol className="flex flex-col gap-3">
        {versions.map((v) => {
          const isCurrent = v.id === recipe.version.id;
          return (
            <li key={v.id}>
              <Link
                href={`/recipes/${recipe.id}?v=${v.id}`}
                className="block rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 hover:border-emerald-500"
              >
                <div className="flex items-center justify-between gap-4">
                  <span className="font-mono text-emerald-400">
                    v{v.version_number}
                  </span>
                  {isCurrent && (
                    <span className="rounded-full border border-emerald-500/40 px-2 py-0.5 text-xs text-emerald-400">
                      current
                    </span>
                  )}
                </div>
                <p className="mt-1 text-sm text-zinc-400">
                  by @{v.author_username} ·{" "}
                  {new Date(v.created_at).toLocaleDateString()} ·{" "}
                  {v.ingredient_count} ingredients
                </p>
                {v.change_description && (
                  <p className="mt-1 text-sm text-zinc-300">
                    {v.change_description}
                  </p>
                )}
              </Link>
            </li>
          );
        })}
      </ol>
    </div>
  );
}