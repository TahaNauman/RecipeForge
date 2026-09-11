import Link from "next/link";
import type { RecipeListItem } from "@/lib/api";

export default function RecipeCard({ recipe }: { recipe: RecipeListItem }) {
  const total = (recipe.prep_time ?? 0) + (recipe.cook_time ?? 0);
  return (
    <Link
      href={`/recipes/${recipe.id}`}
      className="group flex flex-col gap-3 rounded-lg border border-zinc-800 bg-zinc-900/50 p-5 transition hover:border-zinc-600"
    >
      <div className="flex items-start justify-between gap-3">
        <h2 className="font-medium group-hover:text-emerald-400">{recipe.title}</h2>
        <span className="shrink-0 rounded border border-zinc-700 px-1.5 py-0.5 font-mono text-xs text-zinc-400">
          v{recipe.version_number}
        </span>
      </div>
      <div className="flex flex-wrap gap-2 text-xs text-zinc-400">
        {recipe.cuisine && (
          <span className="rounded-full border border-zinc-800 px-2 py-0.5">{recipe.cuisine}</span>
        )}
        {recipe.difficulty && (
          <span className="rounded-full border border-zinc-800 px-2 py-0.5">
            {recipe.difficulty}
          </span>
        )}
        <span className="px-1">{recipe.ingredient_count} ingredients</span>
        {total > 0 && <span className="px-1">{total} min</span>}
      </div>
      <p className="text-sm text-zinc-500">by @{recipe.author_username}</p>
    </Link>
  );
}