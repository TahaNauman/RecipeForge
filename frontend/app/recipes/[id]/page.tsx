import { Suspense } from "react";
import RecipeDetail from "./recipe-detail";

export default function RecipeDetailPage() {
  return (
    <Suspense fallback={<p className="text-sm text-zinc-500">Loading recipe…</p>}>
      <RecipeDetail />
    </Suspense>
  );
}