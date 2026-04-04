import { 
  Download, 
  Plus, 
  Search, 
  Calendar, 
  Pill, 
  FileText, 
  Globe, 
  Clock, 
  MoreVertical,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { cn } from '@/src/lib/utils';

const logs = [
  {
    id: '#IM-2940',
    time: '2 mins ago',
    patient: 'Rajesh Kumar',
    phone: '+91 98765 43210',
    initials: 'RK',
    symptoms: 'Mild fever (101.2°F), headache, and body aches. No respiratory distress reported.',
    medicine: 'Paracetamol 500mg',
    category: 'OTC',
    status: 'Resolved by AI',
    lang: 'Hindi',
    duration: '4m 12s',
    statusColor: 'bg-emerald-50 text-emerald-700',
    dotColor: 'bg-emerald-500'
  },
  {
    id: '#IM-2939',
    time: '15 mins ago',
    patient: 'Sunita Patil',
    phone: '+91 87654 32109',
    initials: 'SP',
    symptoms: 'Persistent dry cough for 2 weeks with sharp chest pain upon deep inhalation. Fatigue present.',
    medicine: 'Amoxicillin (Pending)',
    category: 'Non-OTC',
    status: 'Escalated',
    lang: 'Marathi',
    duration: '7m 45s',
    statusColor: 'bg-red-50 text-error',
    dotColor: 'bg-error'
  },
  {
    id: '#IM-2938',
    time: '1 hour ago',
    patient: 'Amit Singh',
    phone: '+91 76543 21098',
    initials: 'AS',
    symptoms: 'Watery eyes and frequent sneezing. Seasonal allergy triggers suspected.',
    medicine: 'Cetirizine 10mg',
    category: 'OTC',
    status: 'Resolved by AI',
    lang: 'English',
    duration: '3m 22s',
    statusColor: 'bg-emerald-50 text-emerald-700',
    dotColor: 'bg-emerald-500'
  }
];

export default function CallLogs({ onSelectCall }: { onSelectCall: (id: string) => void }) {
  return (
    <div className="p-6 md:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-on-surface">Call Logs</h2>
          <p className="text-on-surface-variant mt-1">Reviewing AI-assisted patient interactions and medication logs.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-surface-container-lowest border border-surface-container-high rounded-xl text-sm font-medium text-on-surface-variant hover:bg-surface-container-low transition-colors shadow-sm">
            <Download className="w-4 h-4" />
            Export PDF
          </button>
          <button className="flex items-center gap-2 px-5 py-2.5 bg-primary text-on-primary rounded-full text-sm font-semibold shadow-md hover:opacity-90 transition-opacity">
            <Plus className="w-4 h-4" />
            Manual Entry
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 bg-surface-container-low p-4 rounded-2xl">
        <FilterSelect label="Medicine Name" options={['All Medicines', 'Paracetamol', 'Amoxicillin', 'Cetirizine']} />
        <div className="space-y-1.5">
          <label className="text-[10px] font-bold text-on-surface-variant uppercase ml-1 tracking-wider">Category</label>
          <div className="flex gap-2">
            <button className="flex-1 py-2 px-3 bg-white text-primary text-sm font-semibold rounded-xl border-2 border-primary-container shadow-sm">All</button>
            <button className="flex-1 py-2 px-3 bg-surface-container-lowest text-on-surface-variant text-sm font-medium rounded-xl hover:bg-white transition-colors">OTC</button>
            <button className="flex-1 py-2 px-3 bg-surface-container-lowest text-on-surface-variant text-sm font-medium rounded-xl hover:bg-white transition-colors">Non-OTC</button>
          </div>
        </div>
        <FilterSelect label="AI Status" options={['All Statuses', 'Resolved by AI', 'Escalated']} />
        <div className="space-y-1.5">
          <label className="text-[10px] font-bold text-on-surface-variant uppercase ml-1 tracking-wider">Date Range</label>
          <div className="relative">
            <input 
              type="text" 
              readOnly 
              value="Oct 20 - Oct 27, 2023"
              className="w-full bg-surface-container-lowest border-none rounded-xl py-2 pl-3 pr-10 text-sm focus:ring-2 focus:ring-primary-container outline-none cursor-pointer"
            />
            <Calendar className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-on-surface-variant pointer-events-none" />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-surface-container-lowest rounded-2xl shadow-sm overflow-hidden border border-surface-container">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-surface-container-low/50">
                <th className="px-6 py-4 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Call ID</th>
                <th className="px-6 py-4 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Patient</th>
                <th className="px-6 py-4 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Symptoms Summary</th>
                <th className="px-6 py-4 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Medicine / Category</th>
                <th className="px-6 py-4 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Info</th>
                <th className="px-6 py-4 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-container-low">
              {logs.map((log) => (
                <tr 
                  key={log.id} 
                  className="hover:bg-surface-container-low/30 transition-colors group cursor-pointer"
                  onClick={() => onSelectCall(log.id)}
                >
                  <td className="px-6 py-5 align-top">
                    <span className="text-sm font-bold text-primary">{log.id}</span>
                    <p className="text-[10px] text-on-surface-variant mt-0.5 font-bold">{log.time}</p>
                  </td>
                  <td className="px-6 py-5 align-top">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container font-bold text-xs">
                        {log.initials}
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-on-surface">{log.patient}</p>
                        <p className="text-[10px] text-on-surface-variant font-medium">{log.phone}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-5 align-top max-w-xs">
                    <p className="text-sm text-on-surface-variant line-clamp-2 leading-relaxed">{log.symptoms}</p>
                  </td>
                  <td className="px-6 py-5 align-top">
                    <div className="space-y-2">
                      <div className="flex items-center gap-1.5 text-sm font-medium text-on-surface">
                        {log.category === 'OTC' ? <Pill className="w-4 h-4 text-primary" /> : <FileText className="w-4 h-4 text-error" />}
                        {log.medicine}
                      </div>
                      <span className={cn(
                        "inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider",
                        log.category === 'OTC' ? "bg-secondary-container text-on-secondary-container" : "bg-tertiary-container text-on-tertiary-container"
                      )}>
                        {log.category}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-5 align-top">
                    <span className={cn(
                      "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold",
                      log.statusColor
                    )}>
                      <span className={cn("w-1.5 h-1.5 rounded-full", log.dotColor, log.status === 'Resolved by AI' && "animate-pulse")}></span>
                      {log.status}
                    </span>
                  </td>
                  <td className="px-6 py-5 align-top">
                    <div className="flex flex-col gap-1 text-[10px] text-on-surface-variant font-bold uppercase tracking-wider">
                      <span className="flex items-center gap-1"><Globe className="w-3 h-3" /> {log.lang}</span>
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {log.duration}</span>
                    </div>
                  </td>
                  <td className="px-6 py-5 align-top text-right">
                    <button className="p-2 text-on-surface-variant hover:text-primary transition-colors hover:bg-primary-container/20 rounded-lg">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="px-6 py-4 flex items-center justify-between bg-surface-container-low/30 border-t border-surface-container">
          <p className="text-xs text-on-surface-variant font-medium">Showing <span className="text-on-surface font-bold">1-10</span> of 1,248 results</p>
          <div className="flex gap-1">
            <button className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white text-on-surface-variant transition-colors">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button className="w-8 h-8 flex items-center justify-center rounded-lg bg-primary text-on-primary text-xs font-bold shadow-sm">1</button>
            <button className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white text-on-surface-variant text-xs font-medium transition-colors">2</button>
            <button className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white text-on-surface-variant text-xs font-medium transition-colors">3</button>
            <span className="px-1 text-on-surface-variant self-center text-xs">...</span>
            <button className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white text-on-surface-variant text-xs font-medium transition-colors">125</button>
            <button className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white text-on-surface-variant transition-colors">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

const FilterSelect = ({ label, options }: { label: string, options: string[] }) => (
  <div className="space-y-1.5">
    <label className="text-[10px] font-bold text-on-surface-variant uppercase ml-1 tracking-wider">{label}</label>
    <select className="w-full bg-surface-container-lowest border-none rounded-xl py-2.5 px-3 text-sm focus:ring-2 focus:ring-primary-container outline-none appearance-none font-medium">
      {options.map(opt => <option key={opt}>{opt}</option>)}
    </select>
  </div>
);
