import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      <div className="max-w-4xl mx-auto px-6 py-20">
        {/* Hero */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-indigo-400 to-purple-400 text-transparent bg-clip-text">
            VOS
          </h1>
          <p className="text-xl text-slate-400 mb-2">
            Voxora · Opinari · Scrutara
          </p>
          <p className="text-slate-500 text-sm italic">
            Many voices. Many opinions. One scrutiny.
          </p>
        </div>

        {/* Description */}
        <div className="bg-slate-800/50 rounded-2xl p-8 mb-12 border border-slate-700">
          <h2 className="text-2xl font-semibold mb-4">
            Document Review with AI Personas
          </h2>
          <p className="text-slate-300 mb-6 leading-relaxed">
            Upload any document and have it reviewed by a panel of AI personas — 
            each with their own perspective, expertise, and critical lens. 
            Security reviewers, technical architects, devil&apos;s advocates, 
            and more examine your content simultaneously.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
              <div className="w-3 h-3 rounded-full bg-red-500 mb-2"></div>
              <span className="text-red-300">Security Reviewer</span>
            </div>
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
              <div className="w-3 h-3 rounded-full bg-blue-500 mb-2"></div>
              <span className="text-blue-300">Technical Architect</span>
            </div>
            <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3">
              <div className="w-3 h-3 rounded-full bg-amber-500 mb-2"></div>
              <span className="text-amber-300">Devil&apos;s Advocate</span>
            </div>
            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-3">
              <div className="w-3 h-3 rounded-full bg-emerald-500 mb-2"></div>
              <span className="text-emerald-300">Clarity Editor</span>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
            <div className="text-2xl mb-3">📝</div>
            <h3 className="font-semibold mb-2">Git-Backed Versioning</h3>
            <p className="text-sm text-slate-400">
              Every edit creates a commit. View diffs, branch for alternatives, 
              track who said what and when.
            </p>
          </div>
          <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
            <div className="text-2xl mb-3">🎭</div>
            <h3 className="font-semibold mb-2">Customizable Personas</h3>
            <p className="text-sm text-slate-400">
              Create your own reviewer personas. Define their expertise, tone, 
              and focus areas. Build review teams.
            </p>
          </div>
          <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
            <div className="text-2xl mb-3">⚡</div>
            <h3 className="font-semibold mb-2">Real-Time Streaming</h3>
            <p className="text-sm text-slate-400">
              Watch feedback appear as personas analyze your document. 
              No waiting for batch processing.
            </p>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <Link
            href="/documents"
            className="inline-block px-8 py-4 bg-indigo-600 hover:bg-indigo-700 rounded-xl font-semibold text-lg transition-colors"
          >
            Get Started →
          </Link>
          <p className="mt-4 text-sm text-slate-500">
            Start reviewing documents with AI-powered personas
          </p>
        </div>
      </div>
    </main>
  );
}
