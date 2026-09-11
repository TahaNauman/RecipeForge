import Link from "next/link";
import RecipeCard from "@/components/RecipeCard";
import { recipesApi, type RecipeListItem } from "@/lib/api";

export default async function RecipesPage() {
  let recipes: RecipeListItem[] = [];
  let error: string | null = null;
  try {
    recipes = await recipesApi.list();
  } catch {
    error = "Could not load recipes. Is the backend running?";
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Recipes</h1>
          <p className="mt-1 text-sm text-zinc-400">
            Every recipe is versioned from day one.
          </p>
        </div>
        <Link
          href="/recipes/create"
          className="rounded-md bg-emerald-500 px-4 py-2 text-sm font-medium text-zinc-950 hover:bg-emerald-400"
        >
          New recipe
        </Link>
      </div>

      {error ? (
        <p className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 text-sm text-zinc-400">
          {error}
        </p>
      ) : recipes.length === 0 ? (
        <p className="rounded-lg border border-dashed border-zinc-800 p-10 text-center text-sm text-zinc-500">
          No recipes yet. Be the first to{" "}
          <Link href="/recipes/create" className="text-emerald-400 hover:underline">
            create one
          </Link>
          .
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {recipes.map((r) => (
            <RecipeCard key={r.id} recipe={r} />
          ))}
        </div>
      )}
    </div>
  );
}