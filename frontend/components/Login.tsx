"use client";

import { useState } from "react";

interface LoginProps {
  onLogin: () => void;
}

export default function Login({
  onLogin,
}: LoginProps) {
  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  async function login() {
    if (!password) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/auth/login`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            password,
          }),
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Não foi possível entrar."
        );
      }

      onLogin();
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Erro ao fazer login."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-slate-100">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white">
            YouTube Extractor
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Digite a senha para acessar.
          </p>
        </div>

        <div className="space-y-4">
          <input
            type="password"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                login();
              }
            }}
            placeholder="Senha"
            className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm outline-none focus:border-red-500"
          />

          {error && (
            <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
              {error}
            </div>
          )}

          <button
            onClick={login}
            disabled={
              loading || !password
            }
            className="w-full rounded-xl bg-red-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading
              ? "Entrando..."
              : "Entrar"}
          </button>
        </div>
      </div>
    </main>
  );
}