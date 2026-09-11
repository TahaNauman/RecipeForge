import { Suspense } from "react";
import RecipeEdit from "./recipe-edit";

export default function RecipeEditPage() {
  return (
    <Suspense fallback={<p className="text-sm text-zinc-500">Loading recipe…</p>}>
      <RecipeEdit />
    </Suspense>
  );
}