import { Link } from 'react-router-dom';
import {
  Zap, Share2, BarChart4, DollarSign, Network,
  SearchCode, Workflow, Terminal, ShieldAlert, ChevronRight
} from 'lucide-react';
import FadeIn from '../components/ui/FadeIn';
import { useAuth } from '../context/AuthContext';

const Home = () => {
  const { isLoggedIn } = useAuth();

  const competencies = [
    { title: 'Neural Distribution', icon: Share2, cat: 'Core', desc: 'Secure, multi-threaded asset deployment with zero-latency synchronization.' },
    { title: 'Retention Dynamics', icon: BarChart4, cat: 'Analytics', desc: 'Second-by-second drop-off analysis utilizing predictive heatmap visualization.' },
    { title: 'Yield Management', icon: DollarSign, cat: 'FinOps', desc: 'Institutional RPM optimization through dynamic ad-insertion logic.' },
    { title: 'Platform Migration', icon: Network, cat: 'Growth', desc: 'Proprietary audience funneling protocols for ecosystem transitions.' },
    { title: 'Meta-SEO Engine', icon: SearchCode, cat: 'Optimization', desc: 'Algorithmic metadata generation utilizing semantic clustering techniques.' },
    { title: 'Strategy Node', icon: Workflow, cat: 'Lifecycle', desc: 'End-to-end management of asset decay and high-velocity reposting.' },
    { title: 'Predictive CTR', icon: Terminal, cat: 'Data Science', desc: 'Visual saliency mapping using advanced synthetic audience training sets.' },
    { title: 'Rights Enforcement', icon: ShieldAlert, cat: 'Security', desc: 'Institutional Content ID protection and automated strike mitigation.' },
  ];

  return (
    <>
      <style>{`
        .competency-node {
          position: relative;
          background: #ffffff;
          border: 1px solid #f1f5f9;
          transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .competency-node::after {
          content: '';
          position: absolute;
          top: 0; right: 0; bottom: 0; width: 3px;
          background: #0ea5e9;
          transform: scaleY(0);
          transform-origin: top;
          transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .competency-node:hover {
          border-color: #e2e8f0;
          box-shadow: 0 10px 40px -15px rgba(0,0,0,0.05);
          transform: translateY(-4px);
        }
        .competency-node:hover::after { transform: scaleY(1); }
      `}</style>

      <section className="relative pt-36 pb-24 px-6 max-w-6xl mx-auto text-center">
        <FadeIn>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-sky-50 border border-sky-100 text-sky-600 text-[9px] font-bold uppercase tracking-widest mb-8">
            <Zap size={12} className="animate-pulse" />
            Institutional Grade Intelligence Engine
          </div>
        </FadeIn>

        <FadeIn delay={100}>
          <h1 className="text-5xl md:text-7xl font-bold leading-[0.95] tracking-tight text-slate-900 mb-6">
            The Digital Protocol <br />
            <span className="text-sky-500">for Audience Growth.</span>
          </h1>
        </FadeIn>

        <FadeIn delay={200}>
          <p className="text-lg text-slate-500 max-w-xl mx-auto mb-10 leading-relaxed">
            A high-precision operating system for professional content teams. Secure your intellectual property and maximize reach with institutional-grade predictive analytics.
          </p>
        </FadeIn>

        <FadeIn delay={300}>
          <div className="flex flex-col items-center">
            <div className="flex flex-wrap justify-center gap-3">
              <Link
                to="/audit"
                className="px-8 py-4 bg-slate-900 text-white font-bold text-[10px] uppercase tracking-widest rounded-xl hover:bg-sky-600 transition-all shadow-xl shadow-slate-200 active:scale-95"
              >
                Start New Audit
              </Link>
              <Link
                to="/reports"
                className="px-8 py-4 bg-white text-slate-900 border border-slate-200 font-bold text-[10px] uppercase tracking-widest rounded-xl hover:border-sky-500 transition-all active:scale-95"
              >
                View Reports
              </Link>
            </div>
          </div>
        </FadeIn>
      </section>

      {/* CORE COMPETENCIES SECTION */}
      <section className="bg-[#fafafb] border-y border-slate-200 py-24">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid lg:grid-cols-12 gap-10 mb-20 items-start">
            <div className="lg:col-span-5 space-y-4">
              <h2 className="text-[9px] font-bold tracking-[0.25em] text-sky-600 flex items-center gap-3">
                <div className="h-[1px] w-6 bg-sky-600" />
                SYSTEM CAPABILITIES
              </h2>
              <h3 className="text-4xl font-bold text-slate-900 tracking-tight leading-[1.05]">
                Core <br />
                Competencies <br />
                <span className="text-slate-300">& Ecosystem.</span>
              </h3>
            </div>
            <div className="lg:col-span-7 pt-2">
              <p className="text-base text-slate-500 leading-relaxed max-w-xl">
                Our infrastructure is designed for high-stakes environments where content is treated as a critical financial asset. We deploy precision-engineered modules to maximize retention and revenue.
              </p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {competencies.map((item, i) => (
              <div key={i} className="competency-node rounded-xl bg-white p-6 flex flex-col group relative overflow-hidden">
                <div className="flex justify-between items-start mb-6">
                  <div className="w-10 h-10 rounded-lg bg-slate-50 text-slate-400 flex items-center justify-center group-hover:bg-slate-900 group-hover:text-white transition-all duration-300">
                    <item.icon size={18} />
                  </div>
                  <span className="text-[9px] font-mono font-bold text-slate-300">0{i + 1}</span>
                </div>

                <div className="space-y-3">
                  <span className="text-[8px] font-bold uppercase tracking-widest text-sky-600/60">{item.cat}</span>
                  <h4 className="text-base font-bold text-slate-900 tracking-tight">{item.title}</h4>
                  <p className="text-slate-500 text-[11px] leading-relaxed">{item.desc}</p>
                </div>

                <div className="mt-6 opacity-0 group-hover:opacity-100 transition-all translate-y-2 group-hover:translate-y-0 flex items-center gap-1.5 text-[9px] font-bold uppercase tracking-widest text-sky-600">
                  Protocol Details <ChevronRight size={10} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
};

export default Home;
