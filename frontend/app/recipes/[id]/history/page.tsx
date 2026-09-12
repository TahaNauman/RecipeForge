import { Suspense } from "react";
import RecipeHistory from "./recipe-history";

export default function RecipeHistoryPage() {
  return (
    <Suspense fallback={<p className="text-sm text-zinc-500">Loading history…</p>}>
      <RecipeHistory />
    </Suspense>
  );
}