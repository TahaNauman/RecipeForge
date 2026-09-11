"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth";

export default function Navbar() {
  const { user, loading, logout } = useAuth();
  const links = [
    { href: "/", label: "Home" },
    { href: "/explore", label: "Explore" },
    { href: "/analytics", label: "Analytics" },
  ];

  return (
    <header className="sticky top-0 z-10 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur">
      <nav className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2 font-mono font-semibold">
            <span className="text-emerald-400">⑂</span>
            <span>RecipeForge</span>
          </Link>
          <div className="hidden items-center gap-4 text-sm text-zinc-400 sm:flex">
            {links.map((l) => (
              <Link key={l.href} href={l.href} className="hover:text-zinc-100">
                {l.label}
              </Link>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-3 text-sm">
          {loading ? (
            <span className="text-zinc-500">…</span>
          ) : user ? (
            <>
              <Link href={`/profile/${user.username}`} className="text-zinc-400 hover:text-zinc-100">
                @{user.username}
              </Link>
              <button
                onClick={() => logout()}
                className="rounded-md border border-zinc-700 px-3 py-1.5 hover:border-zinc-500 hover:text-zinc-100"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-zinc-400 hover:text-zinc-100">
                Log in
              </Link>
              <Link
                href="/register"
                className="rounded-md border border-emerald-500/40 px-3 py-1.5 font-medium text-emerald-400 hover:bg-emerald-500/10"
              >
                Sign up
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}