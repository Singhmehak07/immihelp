import { 
  Plus, 
  Search, 
  TrendingUp, 
  Package, 
  Pill, 
  Activity, 
  AlertCircle, 
  CheckCircle2, 
  XCircle, 
  MoreVertical,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { cn } from '@/src/lib/utils';

const medicines = [
  {
    name: 'Amoxicillin 500mg',
    generic: 'Penicillin-type',
    category: 'Antibiotic',
    classification: 'Non-OTC',
    usage: 'Bacterial infections, pneumonia',
    doctorReq: 'Yes, Mandatory',
    icon: Pill,
    iconColor: 'text-teal-600',
    iconBg: 'bg-teal-50'
  },
  {
    name: 'Paracetamol',
    generic: 'Acetaminophen',
    category: 'Analgesic',
    classification: 'OTC',
    usage: 'Fever, mild to moderate pain',
    doctorReq: 'Optional',
    icon: Activity,
    iconColor: 'text-blue-600',
    iconBg: 'bg-blue-50'
  },
  {
    name: 'Loratadine',
    generic: 'Claritin',
    category: 'Antihistamine',
    classification: 'OTC',
    usage: 'Allergies, hay fever, hives',
    doctorReq: 'Optional',
    icon: Pill,
    iconColor: 'text-amber-600',
    iconBg: 'bg-amber-50'
  },
  {
    name: 'Metformin',
    generic: 'Glucophage',
    category: 'Antidiabetic',
    classification: 'Non-OTC',
    usage: 'Type 2 Diabetes management',
    doctorReq: 'Yes, Mandatory',
    icon: AlertCircle,
    iconColor: 'text-red-600',
    iconBg: 'bg-red-50'
  }
];

export default function Medicines() {
  return (
    <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <span className="text-[10px] font-bold text-primary uppercase tracking-widest">Inventory Management</span>
          <h2 className="text-3xl font-extrabold text-on-surface font-headline mt-1">Medicines Repository</h2>
          <p className="text-on-surface-variant mt-2 max-w-xl">Manage essential pharmaceutical stock for rural distribution. AI-assisted categorization helps maintain supply chain integrity.</p>
        </div>
        <button className="bg-primary text-on-primary px-6 py-3 rounded-xl font-bold shadow-lg shadow-primary/20 flex items-center gap-2 hover:scale-[1.02] active:scale-95 transition-all w-fit uppercase tracking-wider text-xs">
          <Plus className="w-4 h-4" />
          Register New Medicine
        </button>
      </div>

      {/* Filters Bento */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-surface-container-lowest p-5 rounded-xl shadow-sm border border-surface-container">
          <p className="text-[10px] font-bold text-on-surface-variant mb-3 uppercase tracking-wider">Filter by Category</p>
          <select className="w-full bg-surface-container-low border-none rounded-lg text-sm font-bold py-2.5 focus:ring-primary-container outline-none">
            <option>All Categories</option>
            <option>Antibiotics</option>
            <option>Analgesics</option>
          </select>
        </div>
        <div className="bg-surface-container-lowest p-5 rounded-xl shadow-sm border border-surface-container">
          <p className="text-[10px] font-bold text-on-surface-variant mb-3 uppercase tracking-wider">OTC Status</p>
          <div className="flex gap-2">
            <button className="flex-1 bg-primary text-on-primary py-2 px-3 rounded-lg text-[10px] font-black uppercase tracking-widest">All</button>
            <button className="flex-1 bg-surface-container-low text-on-surface-variant py-2 px-3 rounded-lg text-[10px] font-black uppercase tracking-widest hover:bg-surface-container transition-colors">OTC</button>
            <button className="flex-1 bg-surface-container-low text-on-surface-variant py-2 px-3 rounded-lg text-[10px] font-black uppercase tracking-widest hover:bg-surface-container transition-colors">Presc.</button>
          </div>
        </div>
        <div className="md:col-span-2 bg-surface-container-lowest p-5 rounded-xl shadow-sm border border-surface-container flex items-center justify-between">
          <div>
            <p className="text-[10px] font-bold text-on-surface-variant mb-1 uppercase tracking-wider">Total Inventory</p>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black text-on-surface font-headline">1,284</span>
              <span className="text-primary text-xs font-bold flex items-center gap-1">
                <TrendingUp className="w-3 h-3" /> +12%
              </span>
            </div>
          </div>
          <div className="h-12 w-12 rounded-full bg-secondary-container flex items-center justify-center">
            <Package className="w-6 h-6 text-on-secondary-container" />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-surface-container-lowest rounded-xl overflow-hidden shadow-sm border border-surface-container">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-surface-container-low/50">
                <th className="text-left px-6 py-4 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Medicine Details</th>
                <th className="text-left px-6 py-4 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Category</th>
                <th className="text-left px-6 py-4 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Classification</th>
                <th className="text-left px-6 py-4 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Usage</th>
                <th className="text-left px-6 py-4 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Doctor Req.</th>
                <th className="text-right px-6 py-4 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-container-low">
              {medicines.map((med, idx) => (
                <tr key={med.name} className={cn(
                  "group hover:bg-surface-container-low transition-colors",
                  idx % 2 !== 0 && "bg-surface-container-low/30"
                )}>
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-4">
                      <div className={cn("h-10 w-10 rounded-lg flex items-center justify-center shrink-0", med.iconBg)}>
                        <med.icon className={cn("w-5 h-5", med.iconColor)} />
                      </div>
                      <div>
                        <p className="text-sm font-bold text-on-surface">{med.name}</p>
                        <p className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Generic: {med.generic}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-secondary-container text-on-secondary-container uppercase tracking-wider">
                      {med.category}
                    </span>
                  </td>
                  <td className="px-6 py-5">
                    <div className={cn(
                      "flex items-center gap-1.5 px-2 py-1 rounded w-fit text-[10px] font-black uppercase tracking-widest",
                      med.classification === 'OTC' ? "bg-primary/10 text-primary" : "bg-error/10 text-error"
                    )}>
                      {med.classification === 'OTC' ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                      {med.classification}
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <p className="text-xs text-on-surface-variant max-w-[150px] truncate font-medium">{med.usage}</p>
                  </td>
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-2 text-on-surface font-bold text-[10px] uppercase tracking-wider">
                      <span className={cn("h-2 w-2 rounded-full", med.doctorReq.includes('Yes') ? "bg-error animate-pulse" : "bg-on-surface-variant/30")}></span>
                      {med.doctorReq}
                    </div>
                  </td>
                  <td className="px-6 py-5 text-right">
                    <button className="text-on-surface-variant hover:text-primary transition-colors">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-surface-container-low/50 flex items-center justify-between border-t border-surface-container">
          <p className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Showing 4 of 1,284 entries</p>
          <div className="flex gap-2">
            <button className="h-8 w-8 flex items-center justify-center rounded bg-surface-container-lowest text-on-surface-variant cursor-not-allowed opacity-50">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button className="h-8 px-3 flex items-center justify-center rounded bg-primary text-on-primary text-[10px] font-black shadow-sm">1</button>
            <button className="h-8 px-3 flex items-center justify-center rounded bg-surface-container-lowest text-on-surface-variant text-[10px] font-black hover:bg-surface-container transition-colors">2</button>
            <button className="h-8 px-3 flex items-center justify-center rounded bg-surface-container-lowest text-on-surface-variant text-[10px] font-black hover:bg-surface-container transition-colors">3</button>
            <button className="h-8 w-8 flex items-center justify-center rounded bg-surface-container-lowest text-on-surface-variant hover:bg-surface-container transition-colors">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
