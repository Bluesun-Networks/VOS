'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  fetchDocuments, uploadFile, archiveDocument, restoreDocument, deleteDocument,
  type Document,
} from '@/lib/api';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [showArchived, setShowArchived] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [bulkAction, setBulkAction] = useState(false);
  const router = useRouter();

  const loadDocs = () => {
    setLoading(true);
    fetchDocuments(showArchived)
      .then(setDocuments)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDocs();
  }, [showArchived]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !file.name.endsWith('.md')) return;
    try {
      const result = await uploadFile(file);
      router.push(`/documents/${result.document_id}?autoReview=true`);
    } catch (err) {
      console.error('Upload failed:', err);
    }
  };

  const handleArchive = async (docId: string) => {
    await archiveDocument(docId);
    loadDocs();
    setSelectedIds((prev) => { const next = new Set(prev); next.delete(docId); return next; });
  };

  const handleRestore = async (docId: string) => {
    await restoreDocument(docId);
    loadDocs();
    setSelectedIds((prev) => { const next = new Set(prev); next.delete(docId); return next; });
  };

  const handleDelete = async (docId: string) => {
    if (!confirm('Permanently delete this document?')) return;
    await deleteDocument(docId);
    loadDocs();
    setSelectedIds((prev) => { const next = new Set(prev); next.delete(docId); return next; });
  };

  const handleBulkArchive = async () => {
    await Promise.all(Array.from(selectedIds).map(archiveDocument));
    setSelectedIds(new Set());
    loadDocs();
  };

  const handleBulkDelete = async () => {
    if (!confirm(`Permanently delete ${selectedIds.size} document(s)?`)) return;
    await Promise.all(Array.from(selectedIds).map(deleteDocument));
    setSelectedIds(new Set());
    loadDocs();
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === documents.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(documents.map(d => d.id)));
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  };

  return (
    <main className="min-h-screen bg-[#0a0a0f]">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-8 sm:mb-10">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight">Documents</h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowArchived(!showArchived)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                showArchived ? 'bg-indigo-600 text-white' : 'bg-[#1a1a25] text-neutral-400 hover:text-white hover:bg-[#252530]'
              }`}
            >
              {showArchived ? 'Hide Archived' : 'Show Archived'}
            </button>
            <button
              onClick={() => setBulkAction(!bulkAction)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                bulkAction ? 'bg-[#252530] text-white' : 'bg-[#1a1a25] text-neutral-400 hover:text-white hover:bg-[#252530]'
              }`}
            >
              {bulkAction ? 'Done' : 'Select'}
            </button>
            <label className="px-3 sm:px-4 py-2 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 rounded-lg text-sm font-medium transition-colors cursor-pointer touch-manipulation">
              + Upload
              <input type="file" accept=".md" onChange={handleFileUpload} className="hidden" />
            </label>
          </div>
        </div>

        {/* Bulk actions bar */}
        {bulkAction && selectedIds.size > 0 && (
          <div className="flex items-center gap-2 mb-4 p-3 bg-[#12121a] rounded-xl border border-[#2a2a3a]">
            <span className="text-xs text-neutral-400">{selectedIds.size} selected</span>
            <button onClick={toggleSelectAll} className="text-xs text-indigo-400 hover:text-indigo-300 ml-2">
              {selectedIds.size === documents.length ? 'Deselect All' : 'Select All'}
            </button>
            <div className="ml-auto flex items-center gap-2">
              <button
                onClick={handleBulkArchive}
                className="px-3 py-1.5 bg-[#1a1a25] hover:bg-[#252530] rounded-lg text-xs text-neutral-300 transition-colors"
              >
                Archive
              </button>
              <button
                onClick={handleBulkDelete}
                className="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 rounded-lg text-xs text-red-400 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        )}

        {/* Content */}
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-[#12121a] rounded-xl p-5 border border-[#2a2a3a] animate-pulse">
                <div className="h-5 bg-[#1a1a25] rounded w-1/3 mb-3" />
                <div className="h-3 bg-[#1a1a25] rounded w-2/3" />
              </div>
            ))}
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-4xl mb-4 opacity-30">
              <svg className="w-16 h-16 mx-auto text-neutral-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-neutral-500 mb-4">{showArchived ? 'No archived documents' : 'No documents yet'}</p>
            {!showArchived && (
              <Link href="/" className="text-indigo-400 hover:text-indigo-300 text-sm">
                Upload your first document
              </Link>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className={`bg-[#12121a] hover:bg-[#16161f] active:bg-[#1a1a24] rounded-xl p-4 sm:p-5 border transition-all group touch-manipulation ${
                  doc.is_archived ? 'border-neutral-700/50 opacity-70' : 'border-[#2a2a3a] hover:border-[#3a3a4a]'
                } ${selectedIds.has(doc.id) ? 'ring-1 ring-indigo-500/50' : ''}`}
              >
                <div className="flex items-start gap-3">
                  {bulkAction && (
                    <button
                      onClick={() => toggleSelect(doc.id)}
                      className="mt-1 flex-shrink-0"
                    >
                      <div
                        className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-colors ${
                          selectedIds.has(doc.id)
                            ? 'bg-indigo-600 border-indigo-600'
                            : 'border-neutral-600 hover:border-neutral-400'
                        }`}
                      >
                        {selectedIds.has(doc.id) && (
                          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                          </svg>
                        )}
                      </div>
                    </button>
                  )}
                  <Link
                    href={`/documents/${doc.id}`}
                    className="flex-1 min-w-0 block"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 sm:gap-0">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-[#e4e4ec] group-hover:text-white transition-colors truncate">
                          {doc.title}
                          {doc.is_archived && (
                            <span className="ml-2 text-[10px] text-neutral-500 bg-neutral-800 px-1.5 py-0.5 rounded">
                              Archived
                            </span>
                          )}
                        </h3>
                        {doc.description && (
                          <p className="text-neutral-500 text-sm mt-1 truncate">{doc.description}</p>
                        )}
                      </div>
                      <div className="sm:text-right sm:ml-4 flex-shrink-0 flex sm:block items-center gap-3">
                        <div className="text-xs text-neutral-500">{formatDate(doc.created_at)}</div>
                        {doc.review_count > 0 && (
                          <div className="text-xs text-indigo-400 sm:mt-1">
                            {doc.review_count} review{doc.review_count !== 1 ? 's' : ''}
                          </div>
                        )}
                      </div>
                    </div>
                  </Link>
                  {/* Row actions */}
                  {!bulkAction && (
                    <div className="flex items-center gap-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                      {doc.is_archived ? (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleRestore(doc.id); }}
                          className="p-1.5 text-neutral-500 hover:text-indigo-400 transition-colors"
                          title="Restore"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                          </svg>
                        </button>
                      ) : (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleArchive(doc.id); }}
                          className="p-1.5 text-neutral-500 hover:text-yellow-400 transition-colors"
                          title="Archive"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                          </svg>
                        </button>
                      )}
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDelete(doc.id); }}
                        className="p-1.5 text-neutral-500 hover:text-red-400 transition-colors"
                        title="Delete"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
