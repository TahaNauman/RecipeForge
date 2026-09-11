import BackendStatus from "@/components/BackendStatus";

const features = [
  {
    icon: "⑂",
    title: "Versioned recipes",
    desc: "Every publish creates an immutable version. History is never rewritten.",
  },
  {
    icon: "⑃",
    title: "Fork anything",
    desc: "Fork a recipe at any version and build your own lineage.",
  },
  {
    icon: "≠",
    title: "Git-style diffs",
    desc: "Diff two versions — added, removed, and modified ingredients & steps.",
  },
  {
    icon: "☆",
    title: "Star & review",
    desc: "Stars, ratings, and an activity feed across the whole plate.",
  },
  {
    icon: "◎",
    title: "Lineage graphs",
    desc: "Visualize branches with an interactive fork tree.",
  },
  {
    icon: "△",
    title: "Analytics & similarity",
    desc: "Trends, ingredient vectors, and 'you might also like'.",
  },
];

export default function Home() {
  return (
    <div className="flex flex-col gap-12">
      <section className="flex flex-col items-start gap-6">
        <span className="rounded-full border border-zinc-800 px-3 py-1 font-mono text-xs text-zinc-400">
          GitHub, but for cooking
        </span>
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
          Recipes have commits, branches,
          <br />
          <span className="text-emerald-400">forks, diffs, and history.</span>
        </h1>
        <p className="max-w-xl text-lg text-zinc-400">
          RecipeForge is a developer platform for cooking: a recipe is a small
          software project, and every modification is a release.
        </p>
        <div className="flex flex-wrap items-center gap-4">
          <a
            href="/explore"
            className="rounded-md bg-emerald-500 px-4 py-2 font-medium text-zinc-950 hover:bg-emerald-400"
          >
            Explore recipes
          </a>
          <BackendStatus />
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((f) => (
          <div
            key={f.title}
            className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5"
          >
            <div className="mb-2 font-mono text-lg text-emerald-400">{f.icon}</div>
            <h2 className="mb-1 font-medium">{f.title}</h2>
            <p className="text-sm text-zinc-400">{f.desc}</p>
          </div>
        ))}
      </section>
    </div>
  );
}