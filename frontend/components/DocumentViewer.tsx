'use client';

import { useState } from 'react';
import { Document, Comment } from '@/lib/api';

interface Props {
  document: Document;
  content: string;
  comments: Comment[];
  onVersionSelect?: (version: string) => void;
}

export function DocumentViewer({ document, content, comments, onVersionSelect }: Props) {
  const [selectedVersion, setSelectedVersion] = useState<string | null>(null);
  
  const lines = content.split('\n');
  
  // Group comments by line
  const commentsByLine: Record<number, Comment[]> = {};
  comments.forEach(comment => {
    const line = comment.anchor.start_line;
    if (!commentsByLine[line]) commentsByLine[line] = [];
    commentsByLine[line].push(comment);
  });
  
  const handleVersionChange = (version: string) => {
    setSelectedVersion(version);
    onVersionSelect?.(version);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-white">
        <div>
          <h1 className="text-xl font-semibold">{document.title}</h1>
          {document.description && (
            <p className="text-sm text-slate-500">{document.description}</p>
          )}
        </div>
        
        {/* Version selector */}
        <select
          className="px-3 py-1.5 border rounded-lg text-sm bg-white"
          value={selectedVersion || document.versions[0]?.commit_hash || ''}
          onChange={(e) => handleVersionChange(e.target.value)}
        >
          {document.versions.map((v) => (
            <option key={v.commit_hash} value={v.commit_hash}>
              {v.commit_hash.slice(0, 7)} - {v.message.slice(0, 30)}
            </option>
          ))}
        </select>
      </div>
      
      {/* Content area */}
      <div className="flex-1 overflow-auto p-4 bg-slate-50">
        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow">
          <pre className="p-6 text-sm font-mono overflow-x-auto">
            {lines.map((line, idx) => {
              const lineNum = idx + 1;
              const lineComments = commentsByLine[lineNum] || [];
              const hasComments = lineComments.length > 0;
              
              return (
                <div key={idx} className="group relative">
                  <div className={`flex ${hasComments ? 'bg-yellow-50' : ''}`}>
                    <span className="w-10 text-right pr-4 text-slate-400 select-none">
                      {lineNum}
                    </span>
                    <span className="flex-1 whitespace-pre-wrap">{line || ' '}</span>
                    {hasComments && (
                      <span className="ml-2 text-xs text-slate-400">
                        💬 {lineComments.length}
                      </span>
                    )}
                  </div>
                  
                  {/* Inline comments */}
                  {hasComments && (
                    <div className="ml-10 py-2 space-y-2">
                      {lineComments.map((comment) => (
                        <div
                          key={comment.id}
                          className="p-3 rounded-lg text-sm"
                          style={{ 
                            backgroundColor: `${comment.persona_color}15`,
                            borderLeft: `3px solid ${comment.persona_color}`
                          }}
                        >
                          <div className="flex items-center gap-2 mb-1">
                            <span 
                              className="w-2 h-2 rounded-full"
                              style={{ backgroundColor: comment.persona_color }}
                            />
                            <span className="font-medium text-slate-700">
                              {comment.persona_name}
                            </span>
                          </div>
                          <p className="text-slate-600">{comment.content}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </pre>
        </div>
      </div>
    </div>
  );
}
