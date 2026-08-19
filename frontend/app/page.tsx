"use client";

import { useState } from "react";
import Login from "@/components/Login";

import type {
  Comment,
  SearchOptions,
} from "@/types/comment";

export default function Home() {
  const [url, setUrl] = useState("");

  const [videoId, setVideoId] = useState("");

  const [comments, setComments] =
    useState<Comment[]>([]);

  const [selectedComments, setSelectedComments] =
    useState<Set<string>>(new Set());

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [totalFound, setTotalFound] =
    useState(0);

  const [progress, setProgress] =
    useState(0);

  const [options, setOptions] =
    useState<SearchOptions>({
      max_comments: 100,
      remove_emoji_only: true,
      remove_empty: true,
      remove_links: false,
      remove_duplicates: false,
      order: "relevance",
    });

  const [authenticated, setAuthenticated] =
    useState(false);

  async function loadCommentsPage(
    jobId: string,
    page: number
  ) {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/youtube/comments/page/${jobId}?page=${page}&page_size=100`,
      {
        credentials: "include",
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        typeof data.detail === "string"
          ? data.detail
          : "Erro ao carregar comentários."
      );
    }

    setComments(data.comments || []);

    setTotalFound(data.total || 0);
  }

  async function fetchComments() {
    if (!url.trim()) {
      return;
    }

    setLoading(true);
    setError(null);
    setSelectedComments(new Set());
    setTotalFound(0);
    setProgress(0);
    setComments([]);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/youtube/comments/start`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url,
            ...options,
          }),
          credentials: "include",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Erro ao iniciar busca."
        );
      }

      const jobId = data.job_id;

      let completed = false;

      while (!completed) {
        await new Promise(
          (resolve) =>
            setTimeout(resolve, 1000)
        );

        const statusResponse =
          await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/youtube/comments/status/${jobId}`,
            {
              credentials: "include",
            }
          );

        const statusData =
          await statusResponse.json();

        if (!statusResponse.ok) {
          throw new Error(
            typeof statusData.detail === "string"
              ? statusData.detail
              : "Erro ao consultar progresso."
          );
        }

        const processed =
          statusData.processed || 0;

        setTotalFound(processed);

        setProgress(
          Math.min(
            100,
            Math.round(
              (processed /
                options.max_comments) *
              100
            )
          )
        );

        if (
          statusData.status ===
          "completed"
        ) {
          completed = true;

          setVideoId(
            statusData.video_id
          );

          setProgress(100);

          await loadCommentsPage(
            jobId,
            1
          );
        }

        if (
          statusData.status ===
          "error"
        ) {
          throw new Error(
            statusData.error ||
            "Erro ao buscar comentários."
          );
        }
      }
    } catch (error) {
      console.error(error);

      setError(
        error instanceof Error
          ? error.message
          : "Não foi possível buscar os comentários."
      );
    } finally {
      setLoading(false);
    }
  }

  function toggleComment(id: string) {
    setSelectedComments((current) => {
      const next = new Set(current);

      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }

      return next;
    });
  }

  function toggleAll() {
    if (
      selectedComments.size ===
      comments.length
    ) {
      setSelectedComments(new Set());
      return;
    }

    setSelectedComments(
      new Set(
        comments.map(
          (comment) => comment.id
        )
      )
    );
  }

  function handleKeyDown(
    event: React.KeyboardEvent<HTMLInputElement>
  ) {
    if (event.key === "Enter") {
      fetchComments();
    }
  }

  const selectedCount =
    selectedComments.size;

  const allSelected =
    comments.length > 0 &&
    selectedComments.size ===
      comments.length;

  if (!authenticated) {
    return (
      <Login
        onLogin={() =>
          setAuthenticated(true)
        }
      />
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-slate-100 sm:p-8 md:p-12">
      <div className="mx-auto max-w-5xl space-y-8">

        {/* HEADER */}

        <header className="space-y-2 text-center sm:text-left">
          <div className="inline-flex items-center gap-2 rounded-full border border-red-500/20 bg-red-500/10 px-3 py-1 text-xs font-semibold text-red-400">
            <span className="h-2 w-2 animate-pulse rounded-full bg-red-500" />

            YouTube Extractor
          </div>

          <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            Comentários do YouTube
          </h1>

          <p className="text-sm text-slate-400">
            Cole a URL de qualquer vídeo para
            buscar e selecionar os comentários.
          </p>
        </header>

        {/* BUSCA */}

        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-4 shadow-xl sm:p-6">

          <div className="flex flex-col gap-3 sm:flex-row">

            <input
              type="text"
              value={url}
              onChange={(event) =>
                setUrl(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="https://www.youtube.com/watch?v=..."
              className="w-full flex-1 rounded-xl border border-slate-800 bg-slate-950 px-4 py-3.5 text-sm text-slate-100 outline-none transition-all placeholder:text-slate-500 focus:border-red-500 focus:ring-2 focus:ring-red-500/20"
            />

            <button
              onClick={fetchComments}
              disabled={
                loading || !url.trim()
              }
              className="rounded-xl bg-red-600 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-red-600/25 transition-all hover:bg-red-500 disabled:pointer-events-none disabled:opacity-50"
            >
              {loading
                ? "Buscando comentários..."
                : "Buscar Comentários"}
            </button>

          </div>

          {/* PROGRESSO */}

          {loading && (
            <div className="mt-5 space-y-2">

              <div className="flex justify-between text-xs text-slate-400">

                <span>
                  Buscando comentários...
                </span>

                <span>
                  {totalFound.toLocaleString(
                    "pt-BR"
                  )}{" "}
                  /{" "}
                  {options.max_comments.toLocaleString(
                    "pt-BR"
                  )}
                </span>

              </div>

              <div className="h-2 overflow-hidden rounded-full bg-slate-800">

                <div
                  className="h-full rounded-full bg-red-600 transition-all duration-300"
                  style={{
                    width: `${progress}%`,
                  }}
                />

              </div>

            </div>
          )}

          {/* ERRO */}

          {error && (
            <div className="mt-4 rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-xs text-red-400">
              {error}
            </div>
          )}

          {/* CONFIGURAÇÕES */}

          <div className="mt-6 border-t border-slate-800 pt-6">

            <h2 className="mb-4 text-sm font-semibold text-slate-200">
              Configurações
            </h2>

            <div className="grid gap-4 sm:grid-cols-2">

              {/* QUANTIDADE */}

              <div>

                <label className="mb-2 block text-xs font-medium text-slate-400">
                  Quantidade máxima
                </label>

                <input
                  type="number"
                  min={1}
                  max={90000}
                  value={options.max_comments}
                  onChange={(event) =>
                    setOptions({
                      ...options,
                      max_comments:
                        Number(
                          event.target.value
                        ),
                    })
                  }
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm outline-none focus:border-red-500"
                />

              </div>

              {/* ORDEM */}

              <div>

                <label className="mb-2 block text-xs font-medium text-slate-400">
                  Ordenação
                </label>

                <select
                  value={options.order}
                  onChange={(event) =>
                    setOptions({
                      ...options,
                      order:
                        event.target.value as
                          | "relevance"
                          | "recent",
                    })
                  }
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm outline-none focus:border-red-500"
                >

                  <option value="relevance">
                    Mais relevantes
                  </option>

                  <option value="recent">
                    Mais recentes
                  </option>

                </select>

              </div>

            </div>

            {/* FILTROS */}

            <div className="mt-5 grid gap-3 sm:grid-cols-2">

              <FilterCheckbox
                checked={
                  options.remove_emoji_only
                }
                onChange={(checked) =>
                  setOptions({
                    ...options,
                    remove_emoji_only:
                      checked,
                  })
                }
                label="Remover comentários somente com emojis"
              />

              <FilterCheckbox
                checked={
                  options.remove_empty
                }
                onChange={(checked) =>
                  setOptions({
                    ...options,
                    remove_empty:
                      checked,
                  })
                }
                label="Remover comentários vazios"
              />

              <FilterCheckbox
                checked={
                  options.remove_links
                }
                onChange={(checked) =>
                  setOptions({
                    ...options,
                    remove_links:
                      checked,
                  })
                }
                label="Remover comentários com links"
              />

              <FilterCheckbox
                checked={
                  options.remove_duplicates
                }
                onChange={(checked) =>
                  setOptions({
                    ...options,
                    remove_duplicates:
                      checked,
                  })
                }
                label="Remover comentários duplicados"
              />

            </div>

          </div>

        </section>

        {/* RESULTADOS */}

        {comments.length > 0 && (

          <section className="space-y-4">

            {/* CABEÇALHO */}

            <div className="flex flex-col gap-3 border-b border-slate-800 pb-3 sm:flex-row sm:items-center sm:justify-between">

              <div>

                <h2 className="text-lg font-semibold text-slate-200">
                  Resultados
                </h2>

                <div className="mt-1 flex flex-wrap gap-3 text-xs text-slate-500">

                  <span>
                    Encontrados:{" "}
                    <strong className="text-slate-300">
                      {totalFound}
                    </strong>
                  </span>

                  <span>
                    Página atual:{" "}
                    <strong className="text-slate-300">
                      {comments.length}
                    </strong>
                  </span>

                  <span>
                    Selecionados:{" "}
                    <strong className="text-red-400">
                      {selectedCount}
                    </strong>
                  </span>

                </div>

              </div>

              <button
                onClick={toggleAll}
                className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-xs font-medium text-slate-300 transition hover:bg-slate-800"
              >
                {allSelected
                  ? "Desmarcar todos"
                  : "Selecionar todos"}
              </button>

            </div>

            {/* COMENTÁRIOS */}

            <div className="grid gap-3">

              {comments.map((comment) => {

                const selected =
                  selectedComments.has(
                    comment.id
                  );

                return (
                  <div
                    key={comment.id}
                    className={`rounded-xl border p-4 transition-all ${
                      selected
                        ? "border-red-500/40 bg-red-500/5"
                        : "border-slate-800/80 bg-slate-900/50 hover:border-slate-700"
                    }`}
                  >

                    <div className="flex items-start gap-3">

                      {/* CHECKBOX */}

                      <input
                        type="checkbox"
                        checked={selected}
                        onChange={() =>
                          toggleComment(
                            comment.id
                          )
                        }
                        className="mt-2 h-4 w-4 shrink-0 accent-red-600"
                      />

                      {/* AVATAR */}

                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-slate-700 bg-slate-800 text-xs font-bold text-slate-300">

                        {comment.author
                          ? comment.author
                              .charAt(0)
                              .toUpperCase()
                          : "?"}

                      </div>

                      {/* CONTEÚDO */}

                      <div className="min-w-0 flex-1 space-y-1">

                        <div className="flex items-center justify-between gap-2">

                          <span className="truncate text-sm font-semibold text-slate-200">
                            {comment.author}
                          </span>

                          {/* LIKES */}

                          <div className="shrink-0 rounded-md border border-slate-700/50 bg-slate-800/80 px-2 py-0.5 text-xs text-slate-400">
                            👍 {comment.likes}
                          </div>

                        </div>

                        <p className="break-words whitespace-pre-line text-sm leading-relaxed text-slate-300">
                          {comment.text}
                        </p>

                      </div>

                    </div>

                  </div>
                );
              })}

            </div>

            {/* EXPORTAR */}

            <div className="flex flex-col items-stretch justify-between gap-3 rounded-xl border border-slate-800 bg-slate-900 p-4 sm:flex-row sm:items-center">

              <span className="text-sm text-slate-400">
                {selectedCount} comentário(s)
                selecionado(s)
              </span>

              <button
                onClick={exportExcel}
                disabled={
                  selectedCount === 0
                }
                className="rounded-xl bg-green-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-green-500 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Exportar selecionados
              </button>

            </div>

          </section>

        )}

      </div>
    </main>
  );

  async function exportExcel() {
    if (selectedComments.size === 0) {
      return;
    }

    const selected = comments.filter(
      (comment) =>
        selectedComments.has(
          comment.id
        )
    );

    console.log(
      "EXPORT VIDEO ID:",
      videoId
    );

    console.log(
      "EXPORT COMMENTS:",
      selected
    );

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/export/excel`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            video_id: videoId,
            comments: selected,
          }),
          credentials: "include",
        }
      );

      if (!response.ok) {
        const data =
          await response
            .json()
            .catch(() => null);

        throw new Error(
          data?.detail ||
          "Erro ao exportar comentários"
        );
      }

      const blob =
        await response.blob();

      const downloadUrl =
        window.URL.createObjectURL(
          blob
        );

      const link =
        document.createElement("a");

      link.href = downloadUrl;

      link.download =
        "youtube-comments.xlsx";

      document.body.appendChild(link);

      link.click();

      link.remove();

      window.URL.revokeObjectURL(
        downloadUrl
      );

    } catch (error) {
      console.error(error);

      setError(
        error instanceof Error
          ? error.message
          : "Não foi possível exportar os comentários."
      );
    }
  }
}

/*
 * COMPONENTE DE CHECKBOX
 */

function FilterCheckbox({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: (
    value: boolean
  ) => void;
  label: string;
}) {
  return (
    <label className="flex cursor-pointer items-center gap-3 text-sm text-slate-300">

      <input
        type="checkbox"
        checked={checked}
        onChange={(event) =>
          onChange(
            event.target.checked
          )
        }
        className="h-4 w-4 accent-red-600"
      />

      <span>{label}</span>

    </label>
  );
}