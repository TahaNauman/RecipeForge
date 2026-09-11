"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { recipesApi, type Recipe } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function RecipeDetail() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuth();
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

  const isAuthor = user?.username === recipe.author_username;
  const recipeId = recipe.id;
  const total = (recipe.prep_time ?? 0) + (recipe.cook_time ?? 0);

  async function handleDelete() {
    if (!window.confirm("Delete this recipe? This cannot be undone.")) return;
    await recipesApi.del(recipeId);
    router.push("/recipes");
  }

  return (
    <div className="flex max-w-3xl flex-col gap-8">
      <div>
        <div className="mb-3 flex items-center gap-3">
          <span className="rounded border border-zinc-700 px-1.5 py-0.5 font-mono text-xs text-zinc-400">
            v{recipe.version.version_number}
          </span>
          <span className="text-sm text-zinc-500">by @{recipe.author_username}</span>
        </div>
        <h1 className="text-3xl font-semibold tracking-tight">{recipe.title}</h1>
        {recipe.description && (
          <p className="mt-2 max-w-2xl text-zinc-400">{recipe.description}</p>
        )}
        <div className="mt-4 flex flex-wrap gap-2 text-xs text-zinc-400">
          {recipe.cuisine && (
            <span className="rounded-full border border-zinc-800 px-2 py-0.5">{recipe.cuisine}</span>
          )}
          {recipe.difficulty && (
            <span className="rounded-full border border-zinc-800 px-2 py-0.5">
              {recipe.difficulty}
            </span>
          )}
          {recipe.prep_time != null && <span className="px-1">{recipe.prep_time}m prep</span>}
          {recipe.cook_time != null && <span className="px-1">{recipe.cook_time}m cook</span>}
          {recipe.servings != null && <span className="px-1">{recipe.servings} servings</span>}
          {total > 0 && (
            <span className="px-1">
              {total}m total
            </span>
          )}
        </div>
        {isAuthor && (
          <div className="mt-4 flex gap-3 text-sm">
            <Link
              href={`/recipes/${recipe.id}/edit`}
              className="rounded-md border border-zinc-700 px-3 py-1.5 text-zinc-300 hover:border-emerald-500 hover:text-emerald-400"
            >
              Edit
            </Link>
            <button
              onClick={handleDelete}
              className="rounded-md border border-zinc-700 px-3 py-1.5 text-zinc-400 hover:border-red-500 hover:text-red-400"
            >
              Delete
            </button>
          </div>
        )}
      </div>

      <section>
        <h2 className="mb-3 font-mono text-sm text-emerald-400">ingredients</h2>
        <ul className="flex flex-col gap-1.5 rounded-lg border border-zinc-800 bg-zinc-900/50 p-5 text-sm">
          {recipe.version.ingredients.map((ing, i) => (
            <li key={i} className="flex justify-between gap-4">
              <span>{ing.name}</span>
              <span className="text-zinc-400">
                {ing.quantity != null && `${ing.quantity} `}
                {ing.unit}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="mb-3 font-mono text-sm text-emerald-400">instructions</h2>
        <ol className="flex flex-col gap-3 rounded-lg border border-zinc-800 bg-zinc-900/50 p-5 text-sm">
          {recipe.version.instructions.map((step) => (
            <li key={step.step_number} className="flex gap-3">
              <span className="font-mono text-zinc-500">{step.step_number}</span>
              <span>{step.text}</span>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}