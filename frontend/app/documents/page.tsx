'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api, Document } from '@/lib/api';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newDoc, setNewDoc] = useState({ title: '', content: '', description: '' });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await api.listDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDoc.title || !newDoc.content) return;
    
    setCreating(true);
    try {
      await api.createDocument(newDoc);
      setShowCreate(false);
      setNewDoc({ title: '', content: '', description: '' });
      loadDocuments();
    } catch (error) {
      console.error('Failed to create document:', error);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-slate-800">
            VOS
          </Link>
          <button
            onClick={() => setShowCreate(true)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            + New Document
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold text-slate-800 mb-6">Documents</h1>

        {loading ? (
          <div className="text-center py-12 text-slate-500">Loading...</div>
        ) : documents.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-500 mb-4">No documents yet</p>
            <button
              onClick={() => setShowCreate(true)}
              className="text-indigo-600 hover:underline"
            >
              Create your first document
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {documents.map((doc) => (
              <Link
                key={doc.id}
                href={`/documents/${doc.id}`}
                className="block p-6 bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-800">
                      {doc.title}
                    </h2>
                    {doc.description && (
                      <p className="text-sm text-slate-500 mt-1">
                        {doc.description}
                      </p>
                    )}
                  </div>
                  <span className="text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded">
                    {doc.versions.length} version{doc.versions.length !== 1 ? 's' : ''}
                  </span>
                </div>
                <div className="mt-4 flex items-center gap-4 text-xs text-slate-400">
                  <span>Branch: {doc.current_branch}</span>
                  <span>•</span>
                  <span>Updated: {new Date(doc.updated_at).toLocaleDateString()}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl">
            <form onSubmit={handleCreate}>
              <div className="p-6 border-b">
                <h2 className="text-xl font-semibold">Create Document</h2>
              </div>
              
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Title
                  </label>
                  <input
                    type="text"
                    value={newDoc.title}
                    onChange={(e) => setNewDoc({ ...newDoc, title: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Document title"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Description (optional)
                  </label>
                  <input
                    type="text"
                    value={newDoc.description}
                    onChange={(e) => setNewDoc({ ...newDoc, description: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Brief description"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Content (Markdown)
                  </label>
                  <textarea
                    value={newDoc.content}
                    onChange={(e) => setNewDoc({ ...newDoc, content: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
                    rows={12}
                    placeholder="# Your document content here..."
                    required
                  />
                </div>
              </div>
              
              <div className="p-6 border-t bg-slate-50 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowCreate(false)}
                  className="px-4 py-2 text-slate-600 hover:text-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                >
                  {creating ? 'Creating...' : 'Create Document'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
