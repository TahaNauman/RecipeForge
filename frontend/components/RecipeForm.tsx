"use client";

import { useState } from "react";
import type { IngredientInput, InstructionInput, Recipe, RecipeInput } from "@/lib/api";

const inputClass =
  "w-full rounded-md border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-500 focus:border-emerald-500 focus:outline-none";

type RowTypes = {
  ingredients: IngredientInput[];
  instructions: InstructionInput[];
};

function initialRows(recipe?: Recipe): RowTypes {
  if (!recipe) {
    return {
      ingredients: [{ name: "", quantity: null, unit: "" }],
      instructions: [{ text: "" }],
    };
  }
  return {
    ingredients: recipe.version.ingredients.map((i) => ({
      name: i.name,
      quantity: i.quantity,
      unit: i.unit ?? "",
    })),
    instructions: recipe.version.instructions.map((i) => ({ text: i.text })),
  };
}

type FormState = {
  title: string;
  description: string;
  cuisine: string;
  difficulty: string;
  prep_time: string;
  cook_time: string;
  servings: string;
  ingredients: IngredientInput[];
  instructions: InstructionInput[];
};

export default function RecipeForm({
  recipe,
  onSubmit,
  submitLabel,
}: {
  recipe?: Recipe;
  onSubmit: (payload: RecipeInput) => Promise<void>;
  submitLabel: string;
}) {
  const [form, setForm] = useState<FormState>(() => ({
    title: recipe?.title ?? "",
    description: recipe?.description ?? "",
    cuisine: recipe?.cuisine ?? "",
    difficulty: recipe?.difficulty ?? "",
    prep_time: recipe?.prep_time?.toString() ?? "",
    cook_time: recipe?.cook_time?.toString() ?? "",
    servings: recipe?.servings?.toString() ?? "",
    ingredients: initialRows(recipe).ingredients,
    instructions: initialRows(recipe).instructions,
  }));
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const set = <K extends keyof FormState>(key: K, value: FormState[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  const setIngredient = (i: number, patch: Partial<IngredientInput>) =>
    set(
      "ingredients",
      form.ingredients.map((r, idx) => (idx === i ? { ...r, ...patch } : r)),
    );

  const setInstruction = (i: number, text: string) =>
    set(
      "instructions",
      form.instructions.map((r, idx) => (idx === i ? { ...r, text } : r)),
    );

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const ingredients = form.ingredients
      .map((r) => ({
        name: r.name.trim(),
        quantity: r.quantity !== null && r.quantity !== undefined ? Number(r.quantity) : null,
        unit: r.unit?.trim() || null,
      }))
      .filter((r) => r.name);
    const instructions = form.instructions.map((r) => r.text.trim()).filter(Boolean);

    if (form.title.trim().length < 3) {
      setError("Title must be at least 3 characters.");
      return;
    }
    if (ingredients.length === 0) {
      setError("Add at least one ingredient.");
      return;
    }
    if (instructions.length === 0) {
      setError("Add at least one instruction.");
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit({
        title: form.title.trim(),
        description: form.description.trim() || null,
        cuisine: form.cuisine.trim() || null,
        difficulty: form.difficulty.trim() || null,
        prep_time: form.prep_time ? Number(form.prep_time) : null,
        cook_time: form.cook_time ? Number(form.cook_time) : null,
        servings: form.servings ? Number(form.servings) : null,
        ingredients,
        instructions: instructions.map((text) => ({ text })),
      });
    } catch (err) {
      setSubmitting(false);
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      {error && (
        <p className="rounded-md border border-red-900 bg-red-950/50 px-3 py-2 text-sm text-red-400">
          {error}
        </p>
      )}

      <div className="flex flex-col gap-4">
        <div>
          <label className="mb-1 block text-sm text-zinc-400">Title</label>
          <input
            className={inputClass}
            value={form.title}
            onChange={(e) => set("title", e.target.value)}
            placeholder="Chicken Karahi"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-zinc-400">Description</label>
          <textarea
            className={inputClass}
            rows={3}
            value={form.description}
            onChange={(e) => set("description", e.target.value)}
            placeholder="Spicy tomato-based chicken curry..."
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm text-zinc-400">Cuisine</label>
            <input
              className={inputClass}
              value={form.cuisine}
              onChange={(e) => set("cuisine", e.target.value)}
              placeholder="Pakistani"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm text-zinc-400">Difficulty</label>
            <select
              className={inputClass}
              value={form.difficulty}
              onChange={(e) => set("difficulty", e.target.value)}
            >
              <option value="">Any</option>
              {["easy", "medium", "hard"].map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm text-zinc-400">Prep time (min)</label>
            <input
              className={inputClass}
              type="number"
              min={0}
              value={form.prep_time}
              onChange={(e) => set("prep_time", e.target.value)}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm text-zinc-400">Cook time (min)</label>
            <input
              className={inputClass}
              type="number"
              min={0}
              value={form.cook_time}
              onChange={(e) => set("cook_time", e.target.value)}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm text-zinc-400">Servings</label>
            <input
              className={inputClass}
              type="number"
              min={1}
              value={form.servings}
              onChange={(e) => set("servings", e.target.value)}
            />
          </div>
        </div>
      </div>

      <fieldset className="flex flex-col gap-3">
        <legend className="mb-2 font-mono text-sm text-emerald-400">/ingredients.txt</legend>
        {form.ingredients.map((ing, i) => (
          <div key={i} className="grid grid-cols-[1fr_5rem_6rem_auto] gap-2">
            <input
              className={inputClass}
              value={ing.name}
              onChange={(e) => setIngredient(i, { name: e.target.value })}
              placeholder="ingredient"
            />
            <input
              className={inputClass}
              type="number"
              min={0}
              step="any"
              value={ing.quantity ?? ""}
              onChange={(e) =>
                setIngredient(
                  i,
                  e.target.value === "" ? { quantity: null } : { quantity: Number(e.target.value) },
                )
              }
              placeholder="qty"
            />
            <input
              className={inputClass}
              value={ing.unit ?? ""}
              onChange={(e) => setIngredient(i, { unit: e.target.value })}
              placeholder="unit"
            />
            <button
              type="button"
              onClick={() => set("ingredients", form.ingredients.filter((_, idx) => idx !== i))}
              className="rounded-md border border-zinc-700 px-2 text-sm text-zinc-400 hover:text-red-400"
              aria-label="Remove ingredient"
            >
              ×
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => set("ingredients", [...form.ingredients, { name: "", quantity: null, unit: "" }])}
          className="self-start rounded-md border border-zinc-700 px-3 py-1.5 text-sm text-zinc-400 hover:border-emerald-500 hover:text-emerald-400"
        >
          + ingredient
        </button>
      </fieldset>

      <fieldset className="flex flex-col gap-3">
        <legend className="mb-2 font-mono text-sm text-emerald-400">/steps.sh</legend>
        {form.instructions.map((step, i) => (
          <div key={i} className="flex items-start gap-2">
            <span className="mt-2 font-mono text-sm text-zinc-500">{i + 1}.</span>
            <textarea
              className={inputClass}
              rows={2}
              value={step.text}
              onChange={(e) => setInstruction(i, e.target.value)}
              placeholder="What do you do?"
            />
            <button
              type="button"
              onClick={() => set("instructions", form.instructions.filter((_, idx) => idx !== i))}
              className="mt-1 rounded-md border border-zinc-700 px-2 text-sm text-zinc-400 hover:text-red-400"
              aria-label="Remove step"
            >
              ×
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => set("instructions", [...form.instructions, { text: "" }])}
          className="self-start rounded-md border border-zinc-700 px-3 py-1.5 text-sm text-zinc-400 hover:border-emerald-500 hover:text-emerald-400"
        >
          + step
        </button>
      </fieldset>

      <button
        type="submit"
        disabled={submitting}
        className="rounded-md bg-emerald-500 px-4 py-2 font-medium text-zinc-950 hover:bg-emerald-400 disabled:opacity-50"
      >
        {submitting ? "Saving…" : submitLabel}
      </button>
    </form>
  );
}