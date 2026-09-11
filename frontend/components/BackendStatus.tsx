"use client";

import { useEffect, useState } from "react";
import { healthApi } from "@/lib/api";

type State = { status: "loading" } | { status: "ok"; db: string } | { status: "error" };

export default function BackendStatus() {
  const [state, setState] = useState<State>({ status: "loading" });

  useEffect(() => {
    healthApi
      .get()
      .then((h) => setState({ status: "ok", db: h.db }))
      .catch(() => setState({ status: "error" }));
  }, []);

  if (state.status === "loading") {
    return (
      <div className="flex items-center gap-2 text-sm text-zinc-400">
        <span className="h-2 w-2 animate-pulse rounded-full bg-zinc-500" />
        Checking backend…
      </div>
    );
  }

  if (state.status === "error") {
    return (
      <div className="flex items-center gap-2 text-sm text-red-400">
        <span className="h-2 w-2 rounded-full bg-red-500" />
        Backend unreachable
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 text-sm text-emerald-400">
      <span className="h-2 w-2 rounded-full bg-emerald-500" />
      Backend connected · db: {state.db}
    </div>
  );
}